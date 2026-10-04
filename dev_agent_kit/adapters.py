"""Implement Codex CLI behind a provider-neutral assignment interface."""

from __future__ import annotations

import hashlib
import json
import os
import time
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from .contracts import ExecutionError, native_output_schema
from .guards import ExecutionGuard, public_item
from .processes import execute, safe_value
from .workspace import current_revision


@dataclass(frozen=True)
class Assignment:
    """Supply the task, role, bounded context and evidence without provider SDK types."""

    role_id: str
    task: dict
    workspace: Path
    instructions: str
    context: dict
    output_schema: dict
    timeout_seconds: float
    artifact_directory: Path
    writable: bool
    event_sink: object = None
    check_control: object = None


@dataclass(frozen=True)
class AgentResponse:
    """Normalize actual provider output and exposed usage for the orchestrator."""

    result: dict
    usage: dict | None
    metadata: dict


class AgentAdapter(Protocol):
    """Keep provider setup and invocation out of workflow transitions."""

    def preflight(self) -> dict: ...

    def execute(self, assignment: Assignment) -> AgentResponse: ...


def bounded_client_options() -> list[str]:
    """Limit unrelated discovery/output without changing account credentials or project rules."""
    return [
        "--disable",
        "multi_agent",
        "--disable",
        "apps",
        "--disable",
        "plugins",
        "--disable",
        "remote_plugin",
        "-c",
        "skills.max_context_tokens=1000",
        "-c",
        "tool_output_token_limit=2000",
        "-c",
        "shell_environment_policy.ignore_default_excludes=false",
    ]


class CodexCLI:
    """Use existing ChatGPT account access with an explicit sandbox and no API-key setup."""

    def __init__(self, executable: str = "codex"):
        self.executable = executable

    def preflight(self) -> dict:
        """Reject API-key mode rather than silently creating separately billed calls."""
        if os.environ.get("OPENAI_API_KEY") or os.environ.get("CODEX_API_KEY"):
            raise ExecutionError(
                "auth_unsupported", "This adapter requires existing ChatGPT account access"
            )
        status = execute([self.executable, "login", "status"], Path.cwd(), 20)
        if status.exit_code or "chatgpt" not in (status.stdout + status.stderr).lower():
            raise ExecutionError(
                "auth_unavailable", "Existing Codex ChatGPT authentication is required"
            )
        version = execute([self.executable, "--version"], Path.cwd(), 20)
        help_result = execute([self.executable, "exec", "--help"], Path.cwd(), 20)
        for flag in (
            "--ephemeral",
            "--json",
            "--output-schema",
            "--output-last-message",
            "--sandbox",
        ):
            if flag not in help_result.stdout:
                raise ExecutionError(
                    "capability_unavailable",
                    "Installed Codex lacks a required execution capability",
                )
        if version.exit_code or help_result.exit_code:
            raise ExecutionError("capability_unavailable", "Codex capability inspection failed")
        return {
            "adapter": "codex-cli",
            "version": version.stdout.strip(),
            "auth_mode": "chatgpt",
            "isolation": "codex_sandbox",
            "native_discovery": "not_tested",
            "profile_loading": "explicit_developer_instructions_override",
        }

    def execute(self, assignment: Assignment) -> AgentResponse:
        """Capture only final structured output and usage, omitting raw tool/prompt traces."""
        directory = assignment.artifact_directory
        directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        schema_path = directory / "native-schema.json"
        result_path = directory / "provider-result.json"
        schema_path.write_text(json.dumps(native_output_schema(assignment.output_schema)))
        prompt = (
            "Complete only the assignment below. Use the provided role and its referenced skill.\n"
            "Do not spawn other agents, commit, switch branches, publish, merge or deploy.\n"
            "For QA/review inspect the supplied actual check evidence and source without changing files.\n"
            "Return only the requested structured result; revision is the supplied source fingerprint.\n"
            + json.dumps(
                {
                    "role_id": assignment.role_id,
                    "task": assignment.task,
                    "evidence": assignment.context,
                }
            )
        )
        if (
            len(prompt) + len(assignment.instructions)
            > assignment.task["limits"]["max_context_characters"]
        ):
            raise ExecutionError(
                "limit_exceeded", "Full role/task context exceeds its configured size"
            )
        sandbox = "workspace-write" if assignment.writable else "read-only"
        command = [
            self.executable,
            "--no-daemon",
            "exec",
            "--ephemeral",
            "--json",
            "--color",
            "never",
            "--sandbox",
            sandbox,
            *bounded_client_options(),
            "--output-schema",
            str(schema_path),
            "--output-last-message",
            str(result_path),
            "--cd",
            str(assignment.workspace),
            "-c",
            'approval_policy="never"',
            "-c",
            "developer_instructions=" + json.dumps(assignment.instructions),
            "-",
        ]
        guard = ExecutionGuard(
            assignment.task["limits"],
            assignment.event_sink or (lambda event: None),
            assignment.check_control or (lambda: None),
            lambda: current_revision(assignment.workspace, assignment.task["base_revision"]),
        )

        def stream(line):
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                return
            guard.last_activity = time.monotonic()
            item = public_item(event.get("item", {}), event.get("type") == "item.completed")
            if item:
                if item["type"] == "tool.completed":
                    guard.event({**item, "type": "tool.started"})
                guard.event(item)
            if event.get("type") == "turn.completed" and isinstance(event.get("usage"), dict):
                guard.event({"type": "usage", "usage": event["usage"]})

        process = execute(
            command,
            assignment.workspace,
            assignment.timeout_seconds,
            prompt,
            on_line=stream,
            on_tick=guard.tick,
        )
        usage = None
        for line in process.stdout.splitlines():
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if event.get("type") == "turn.completed" and isinstance(event.get("usage"), dict):
                usage = event["usage"]
        if process.timed_out or process.exit_code:
            (directory / "failure.txt").write_text(
                process.stderr[-8000:] + "\n" + process.stdout[-8000:]
            )
        if process.timed_out:
            raise ExecutionError("timeout", "Codex assignment exceeded its deadline")
        if process.exit_code:
            # Provider/tool errors remain sanitized, bounded and inspectable locally.
            raise ExecutionError(
                "provider_failure",
                "Codex returned a nonzero exit; inspect the sanitized failure artifact",
            )
        if not result_path.is_file():
            raise ExecutionError("invalid_result", "Codex did not produce its structured result")
        try:
            result = json.loads(result_path.read_text())
        except json.JSONDecodeError as error:
            result_path.write_text("[Invalid provider result omitted]\n")
            raise ExecutionError("invalid_result", "Codex result is not valid JSON") from error
        result_path.write_text(json.dumps(safe_value(result), indent=2) + "\n")
        return AgentResponse(
            result,
            usage,
            {
                "sandbox": sandbox,
                "duration_seconds": process.duration_seconds,
                "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
                "prompt_characters": len(prompt),
                "exit_code": process.exit_code,
            },
        )


def role_profile(kit_root: Path, role_id: str) -> str:
    """Load the generated native profile explicitly because exec has no agent selector."""
    catalog = json.loads((kit_root / "agents/catalog.json").read_text())
    role = next((role for role in catalog["roles"] if role["id"] == role_id), None)
    if role is None:
        raise ExecutionError("unknown_role", "Requested role is not registered")
    path = kit_root / ".codex/agents" / f"{role_id}.toml"
    profile = tomllib.loads(path.read_text())
    if profile["name"] != role_id:
        raise ExecutionError(
            "invalid_profile", "Native profile identity differs from the registered role"
        )
    return profile["developer_instructions"]
