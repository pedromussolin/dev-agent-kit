"""SQLite monitoring adapter; all user values use bound SQL parameters."""

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Protocol

from .contracts import ExecutionError
from .pipeline import executor_steps, group_steps
from .processes import safe_value
from .storage import Store
from .workspace import current_revision


class ReadModelError(ValueError):
    def __init__(self, status_code, detail):
        self.status_code = status_code
        super().__init__(detail)


class MonitoringRepository(Protocol):
    def list_runs(self) -> list: ...
    def run_detail(self, run_id: str) -> dict: ...
    def public_events(self, run_id: str, after: int = 0) -> list: ...
    def request_cancel(self, run_id: str) -> None: ...


@contextmanager
def connection(state):
    """Read live state without acquiring the executor writer lock."""
    database = Path(state).resolve() / "state.sqlite3"
    if not database.is_file():
        raise ReadModelError(503, "Executor state has not been initialized")
    db = sqlite3.connect(database.as_uri() + "?mode=ro", uri=True)
    db.row_factory = sqlite3.Row
    try:
        yield db
    finally:
        db.close()


def list_runs(state):
    with connection(state) as db:
        rows = db.execute(
            "SELECT id,status,created_at,calls,attempt,task_json,error_json FROM runs ORDER BY created_at DESC LIMIT 100"
        )
        result = []
        for row in rows:
            value = dict(row)
            task = json.loads(value.pop("task_json"))
            value.update(
                task_id=task["task_id"],
                project_id=task["project_id"],
                goal=task["goal"],
                limits=task["limits"],
                error=json.loads(value.pop("error_json")) if value["error_json"] else None,
            )
            result.append(value)
        return safe_value(result)


def run_detail(state, run_id):
    with connection(state) as db:
        row = db.execute("SELECT * FROM runs WHERE id=?", (run_id,)).fetchone()
        if not row:
            raise ReadModelError(404, "Run is not registered")
        run = dict(row)
        task = json.loads(run.pop("task_json"))
        stages = []
        for item in db.execute(
            "SELECT name,attempt,status,started_at,finished_at,revision_hash,result_json FROM stages WHERE run_id=? ORDER BY attempt,started_at",
            (run_id,),
        ):
            value = dict(item)
            result = json.loads(value.pop("result_json") or "{}")
            value.update(
                summary=result.get("result", {}).get("summary"),
                role_id=result.get("result", {}).get("role_id"),
                error=result.get("error"),
                checks=[
                    {
                        key: c.get(key)
                        for key in (
                            "name",
                            "component",
                            "exit_code",
                            "duration_seconds",
                            "stdout",
                            "stderr",
                            "argv",
                        )
                    }
                    for c in result.get("checks", [])
                ],
            )
            stages.append(value)
        invocations = [
            dict(item)
            for item in db.execute(
                "SELECT id,started_at,total_tokens,status,usage_json FROM invocations WHERE run_id=? ORDER BY started_at",
                (run_id,),
            )
        ]
        for value in invocations:
            value["usage"] = json.loads(value.pop("usage_json") or "null")
        effects = [
            dict(item)
            for item in db.execute(
                "SELECT name,status,result_json FROM effects WHERE run_id=?", (run_id,)
            )
        ]
        for effect in effects:
            effect["result"] = json.loads(effect.pop("result_json"))
        delivery_events = [
            (row["timestamp"], row["type"], json.loads(row["payload_json"]))
            for row in db.execute(
                "SELECT timestamp,type,payload_json FROM events WHERE run_id=? AND type LIKE 'delivery.%' ORDER BY id",
                (run_id,),
            )
        ]
        for effect in effects:
            matching = [
                (time, kind)
                for time, kind, payload in delivery_events
                if payload.get("operation") == effect["name"]
            ]
            effect["started_at"] = next(
                (time for time, kind in matching if kind == "delivery.running"), None
            )
            effect["finished_at"] = next(
                (
                    time
                    for time, kind in reversed(matching)
                    if kind in {"delivery.succeeded", "delivery.failed"}
                ),
                None,
            )
        for stage in stages:
            if stage["name"] == "checks" and stage["status"] in {"running", "failed"}:
                event = db.execute(
                    "SELECT payload_json FROM events WHERE run_id=? AND type='agent.check' ORDER BY id DESC LIMIT 1",
                    (run_id,),
                ).fetchone()
                if event:
                    stage["active_check" if stage["status"] == "running" else "failed_check"] = (
                        json.loads(event[0]).get("message", "").removeprefix("Running check: ")
                    )
        evidence_current = None
        if run["verified_hash"] and Path(run["workspace"]).is_dir():
            try:
                evidence_current = (
                    current_revision(Path(run["workspace"]), task["base_revision"])
                    == run["verified_hash"]
                )
            except ExecutionError:
                evidence_current = False
        return safe_value(
            {
                "run_id": run_id,
                "task_id": task["task_id"],
                "project_id": task["project_id"],
                "goal": task["goal"],
                "status": run["status"],
                "agent_calls": run["calls"],
                "attempts": run["attempt"],
                "limits": task["limits"],
                "stages": stages,
                "invocations": invocations,
                "effects": effects,
                "error": json.loads(run["error_json"] or "null"),
                "workflow": task.get("workflow"),
                "delivery_mode": task["policy"]["delivery"],
                "evidence_current": evidence_current,
                "phases": group_steps(executor_steps(task, stages, effects, run["status"])),
            }
        )


def public_events(state, run_id, after=0):
    run_detail(state, run_id)
    with connection(state) as db:
        events = []
        for row in db.execute(
            "SELECT id,timestamp,type,payload_json FROM events WHERE run_id=? AND id>? ORDER BY id LIMIT 200",
            (run_id, after),
        ):
            payload = json.loads(row["payload_json"])
            if row["type"].startswith(("agent.", "run.", "control.", "delivery.")):
                allowed = (
                    "role_id",
                    "stage",
                    "message",
                    "category",
                    "activity",
                    "tool_calls",
                    "usage",
                    "operation",
                    "run_id",
                )
                events.append(
                    {
                        "id": row["id"],
                        "timestamp": row["timestamp"],
                        "type": row["type"],
                        "payload": {key: payload[key] for key in allowed if key in payload},
                    }
                )
            else:
                events.append(
                    {
                        "id": row["id"],
                        "timestamp": row["timestamp"],
                        "type": row["type"],
                        "payload": {
                            key: payload[key] for key in ("stage", "attempt") if key in payload
                        },
                    }
                )
        return safe_value(events)


class SQLiteMonitoringRepository:
    """Implement the monitor port without exposing query text to HTTP or MCP."""

    def __init__(self, state):
        self.state = Path(state)

    def list_runs(self):
        return list_runs(self.state)

    def run_detail(self, run_id):
        return run_detail(self.state, run_id)

    def public_events(self, run_id, after=0):
        return public_events(self.state, run_id, after)

    def request_cancel(self, run_id):
        self.run_detail(run_id)
        store = Store(self.state)
        try:
            store.request_cancel(run_id)
        finally:
            store.close()
