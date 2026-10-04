"""Validate tasks and normalized results before permitting workflow transitions."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


class ExecutionError(RuntimeError):
    """Represent a categorized, visible execution failure."""

    def __init__(self, category: str, message: str):
        super().__init__(message)
        self.category = category


def fingerprint(value: object) -> str:
    """Hash normalized configuration or evidence without depending on key order."""
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def validate(value: object, schema: dict, category: str = "invalid_result") -> None:
    """Use the shared JSON Schema rather than treating model text as a contract."""
    errors = sorted(
        Draft202012Validator(schema).iter_errors(value), key=lambda error: str(error.path)
    )
    if errors:
        raise ExecutionError(
            category, f"Schema validation failed at {list(errors[0].path)}: {errors[0].validator}"
        )


def local_path(root: Path, relative: str) -> Path:
    """Reject absolute paths, traversal and symlinks before accessing task files."""
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts:
        raise ExecutionError("unsafe_path", "Expected a workspace-relative path")
    cursor = root
    for part in path.parts:
        cursor = cursor / part
        if cursor.is_symlink():
            raise ExecutionError("unsafe_path", "Symlinks are not supported in task paths")
    candidate = root / path
    if not candidate.resolve().is_relative_to(root.resolve()):
        raise ExecutionError("unsafe_path", "Path escapes the workspace")
    return candidate


def native_output_schema(schema: dict) -> dict:
    """Make optional fields required/nullable for clients requiring strict objects."""
    result = copy.deepcopy(schema)

    def visit(value):
        if isinstance(value, dict):
            if "const" in value:
                value["enum"] = [value.pop("const")]
            if "enum" in value and "type" not in value:
                first = value["enum"][0]
                value["type"] = (
                    "boolean"
                    if isinstance(first, bool)
                    else "integer"
                    if isinstance(first, int)
                    else "string"
                )
            if value.get("type") == "object" and "properties" in value:
                value["required"] = list(value["properties"])
                value["additionalProperties"] = False
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    visit(result)
    return result


def normalize_task(value: dict, kit_root: Path) -> dict:
    """Validate task authority for both CLI and direct Python callers."""
    task = copy.deepcopy(value)
    schema = json.loads((kit_root / "contracts/execution-task.schema.json").read_text())
    validate(task, schema, "invalid_task")
    for key, definition in schema["properties"]["limits"]["properties"].items():
        if "default" in definition:
            task["limits"].setdefault(key, definition["default"])
    task.setdefault(
        "workflow",
        [
            {"name": "implementation", "role_id": "developer", "kind": "implement"},
            {"name": "qa", "role_id": "qa-engineer", "kind": "verify"},
            {"name": "review", "role_id": "technical-reviewer", "kind": "verify"},
        ],
    )
    registered = {
        role["id"] for role in json.loads((kit_root / "agents/catalog.json").read_text())["roles"]
    }
    steps = task["workflow"]
    names = [step["name"] for step in steps]
    if len(set(names)) != len(names) or any(name in {"checks", "delivery"} for name in names):
        raise ExecutionError("invalid_task", "Workflow stage names must be unique and nonreserved")
    if any(step["role_id"] not in registered for step in steps):
        raise ExecutionError("unknown_role", "Workflow contains an unregistered role")
    kinds = [step["kind"] for step in steps]
    if kinds.count("implement") != 1:
        raise ExecutionError("invalid_task", "Workflow requires exactly one implementation stage")
    position = kinds.index("implement")
    if any(kind != "plan" for kind in kinds[:position]) or any(
        kind != "verify" for kind in kinds[position + 1 :]
    ):
        raise ExecutionError(
            "invalid_task", "Planning precedes implementation; verification follows it"
        )
    if not {"qa-engineer", "technical-reviewer"}.issubset(
        {step["role_id"] for step in steps[position + 1 :]}
    ):
        raise ExecutionError("invalid_task", "QA and technical review are required delivery gates")
    if task["policy"]["delivery"] != "diff":
        if "delivery" not in task or (
            task["policy"]["delivery"] == "deploy" and "deployment" not in task["delivery"]
        ):
            raise ExecutionError(
                "invalid_task",
                "Activated delivery requires repository/issue/checks and deployment configuration",
            )
        if task["policy"]["include_working_tree"]:
            raise ExecutionError("invalid_task", "Remote delivery requires clean committed inputs")
    repository = Path(task["repository"]).expanduser().resolve()
    if not repository.is_dir():
        raise ExecutionError("invalid_task", "Repository directory is unavailable")
    task["repository"] = str(repository)
    for component in task["components"]:
        local_path(repository, component["working_directory"])
    for pattern in task["policy"]["allowed_paths"]:
        local_path(repository, pattern)
        if pattern in {".", "**", "*", ".git"} or pattern.startswith(".git/"):
            raise ExecutionError("invalid_task", "Declare a bounded change scope")
    for relative in task["context_files"]:
        local_path(repository, relative)
    return task


def read_task(path: Path, kit_root: Path) -> dict:
    """Resolve a real local task record and validate explicit execution authority."""
    return normalize_task(json.loads(path.read_text()), kit_root)
