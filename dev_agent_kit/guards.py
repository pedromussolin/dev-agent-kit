"""Stop repeated work, excess observed usage and silent or cancelled agents."""

import time
from collections import Counter
from typing import Callable

from .contracts import ExecutionError, fingerprint


class ExecutionGuard:
    """Use public provider events; never publish private reasoning or raw tool output."""

    def __init__(self, limits: dict, emit: Callable, tick: Callable, revision: Callable):
        self.limits, self.emit, self.external_tick, self.revision = limits, emit, tick, revision
        self.last_activity = time.monotonic()
        self.started_tools = set()
        self.completed_tools = set()
        self.repetitions = Counter()
        self.usage = None

    def tick(self):
        self.external_tick()
        if time.monotonic() - self.last_activity > self.limits["idle_timeout_seconds"]:
            raise ExecutionError(
                "idle_timeout", "Agent produced no observable activity within its idle limit"
            )

    def event(self, event: dict):
        self.last_activity = time.monotonic()
        kind = event.get("type", "")
        if kind == "usage":
            self.usage = event["usage"]
            self.emit({"type": "usage", "usage": self.usage})
            total = self.usage.get(
                "total_tokens",
                self.usage.get("input_tokens", 0) + self.usage.get("output_tokens", 0),
            )
            if total >= self.limits["max_tokens_per_agent"]:
                raise ExecutionError(
                    "token_budget_exhausted", "Assignment observed token threshold reached"
                )
        elif kind == "tool.started":
            identifier = event["id"]
            if identifier not in self.started_tools:
                self.started_tools.add(identifier)
                self.emit(
                    {
                        "type": "activity",
                        "activity": event.get("activity", "using_tool"),
                        "tool_calls": len(self.started_tools),
                    }
                )
            if len(self.started_tools) > self.limits["max_tool_calls"]:
                raise ExecutionError("tool_budget_exhausted", "Assignment tool budget exhausted")
        elif kind == "tool.completed" and event["id"] not in self.completed_tools:
            self.completed_tools.add(event["id"])
            signature = fingerprint(
                {
                    "tool": event.get("signature"),
                    "outcome": event.get("outcome"),
                    "revision": self.revision(),
                }
            )
            self.repetitions[signature] += 1
            if self.repetitions[signature] >= self.limits["max_repeated_tool_calls"]:
                raise ExecutionError(
                    "loop_detected", "Same tool/outcome repeated without a source change"
                )
        elif kind == "progress":
            self.emit({"type": "progress", "message": str(event.get("message", ""))[:2000]})
        self.tick()


def public_item(item: dict, completed: bool = False) -> dict | None:
    """Normalize CLI and app-server tool events without exposing command contents."""
    kind = item.get("type")
    if kind in {
        "command_execution",
        "commandExecution",
        "file_change",
        "fileChange",
        "mcp_tool_call",
        "mcpToolCall",
        "dynamicToolCall",
        "webSearch",
    }:
        activity = (
            "editing_files"
            if kind in {"file_change", "fileChange"}
            else "running_command"
            if kind in {"command_execution", "commandExecution"}
            else "using_tool"
        )
        return {
            "type": "tool.completed" if completed else "tool.started",
            "id": item.get("id"),
            "activity": activity,
            "signature": fingerprint(
                {
                    key: item.get(key)
                    for key in (
                        "type",
                        "command",
                        "tool",
                        "name",
                        "arguments",
                        "changes",
                        "action",
                        "query",
                    )
                }
            ),
            "outcome": fingerprint(
                {
                    key: item.get(key)
                    for key in (
                        "exit_code",
                        "exitCode",
                        "aggregated_output",
                        "aggregatedOutput",
                        "result",
                        "status",
                    )
                }
            ),
        }
    if (
        kind in {"agent_message", "agentMessage"}
        and completed
        and item.get("phase") == "commentary"
    ):
        return {"type": "progress", "message": item.get("text", "")}
    return None
