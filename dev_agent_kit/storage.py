"""Persist run transitions and attempts in SQLite under a single-writer lock."""

from __future__ import annotations

import fcntl
import json
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from .contracts import ExecutionError
from .processes import safe_value


def now() -> str:
    """Return an unambiguous event timestamp."""
    return datetime.now(timezone.utc).isoformat()


class Store:
    """Keep authority/configuration and observable stage outcomes in transactions."""

    def __init__(self, root: Path):
        self.root = root.resolve()
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.connection = sqlite3.connect(self.root / "state.sqlite3")
        self.connection.row_factory = sqlite3.Row
        self.connection.executescript("""
            PRAGMA journal_mode=WAL;
            PRAGMA busy_timeout=5000;
            PRAGMA foreign_keys=ON;
            CREATE TABLE IF NOT EXISTS runs (
                id TEXT PRIMARY KEY, task_json TEXT NOT NULL, config_hash TEXT NOT NULL,
                kit_hash TEXT NOT NULL, workspace TEXT NOT NULL, status TEXT NOT NULL,
                created_at TEXT NOT NULL, calls INTEGER NOT NULL DEFAULT 0,
                attempt INTEGER NOT NULL DEFAULT 1, verified_hash TEXT, error_json TEXT
            );
            CREATE TABLE IF NOT EXISTS stages (
                run_id TEXT NOT NULL REFERENCES runs(id), attempt INTEGER NOT NULL,
                name TEXT NOT NULL, status TEXT NOT NULL, revision_hash TEXT,
                started_at TEXT NOT NULL, finished_at TEXT, result_json TEXT,
                PRIMARY KEY (run_id, attempt, name)
            );
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY, run_id TEXT NOT NULL REFERENCES runs(id),
                timestamp TEXT NOT NULL, type TEXT NOT NULL, payload_json TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS events_run_id ON events(run_id,id);
            CREATE TABLE IF NOT EXISTS invocations (
                id TEXT PRIMARY KEY, run_id TEXT NOT NULL REFERENCES runs(id),
                project_id TEXT NOT NULL, started_at TEXT NOT NULL,
                total_tokens INTEGER NOT NULL DEFAULT 0, usage_json TEXT, status TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS invocations_project ON invocations(project_id,started_at);
            CREATE TABLE IF NOT EXISTS controls (
                run_id TEXT PRIMARY KEY REFERENCES runs(id), cancel_requested INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS effects (
                run_id TEXT NOT NULL REFERENCES runs(id), name TEXT NOT NULL,
                status TEXT NOT NULL, result_json TEXT NOT NULL,
                PRIMARY KEY(run_id,name)
            );
            PRAGMA user_version=2;
        """)

    def close(self):
        """Release the SQLite connection."""
        self.connection.close()

    @contextmanager
    def locked(self):
        """Fail clearly if another executor already owns this state directory."""
        with (self.root / "executor.lock").open("a") as lock:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as error:
                raise ExecutionError(
                    "workspace_busy", "Another executor owns this state directory"
                ) from error
            try:
                yield
            finally:
                fcntl.flock(lock, fcntl.LOCK_UN)

    def event(self, run_id: str, kind: str, payload: dict):
        """Append a sanitized event within the caller's transaction."""
        self.connection.execute(
            "INSERT INTO events(run_id,timestamp,type,payload_json) VALUES(?,?,?,?)",
            (run_id, now(), kind, json.dumps(safe_value(payload))),
        )

    def create(self, run_id: str, task: dict, config_hash: str, kit_hash: str, workspace: Path):
        """Persist identity before workspace preparation or model calls."""
        with self.connection:
            self.connection.execute(
                "INSERT INTO runs(id,task_json,config_hash,kit_hash,workspace,status,created_at) VALUES(?,?,?,?,?,?,?)",
                (run_id, json.dumps(task), config_hash, kit_hash, str(workspace), "pending", now()),
            )
            self.event(
                run_id,
                "run.created",
                {"task_id": task["task_id"], "project_id": task["project_id"]},
            )

    def get(self, run_id: str) -> dict:
        """Return the persisted effective task rather than rereading mutable input."""
        row = self.connection.execute("SELECT * FROM runs WHERE id=?", (run_id,)).fetchone()
        if row is None:
            raise ExecutionError("unknown_run", "Run ID is not registered")
        result = dict(row)
        result["task"] = json.loads(result.pop("task_json"))
        return result

    def status(
        self, run_id: str, status: str, error: dict | None = None, verified_hash: str | None = None
    ):
        """Commit final status and its evidence binding together."""
        with self.connection:
            self.connection.execute(
                "UPDATE runs SET status=?, error_json=?, verified_hash=? WHERE id=?",
                (status, json.dumps(safe_value(error)) if error else None, verified_hash, run_id),
            )
            self.event(run_id, f"run.{status}", error or {"revision_hash": verified_hash})

    def reserve_call(self, run_id: str, maximum: int, limits: dict | None = None):
        """Count a call before invoking the provider, including failed/interrupted calls."""
        with self.connection:
            run = self.get(run_id)
            limits = limits or run["task"]["limits"]
            budget = self.budget(run_id)
            if budget["project_calls_today"] >= limits.get("max_project_calls_per_day", 20):
                raise ExecutionError(
                    "project_budget_exhausted", "Daily project assignment budget exhausted"
                )
            if budget["project_tokens_today"] >= limits.get("max_project_tokens_per_day", 500000):
                raise ExecutionError(
                    "project_budget_exhausted", "Daily project observed token budget exhausted"
                )
            if budget["run_tokens"] >= limits.get("max_total_tokens", 200000):
                raise ExecutionError(
                    "token_budget_exhausted", "Run observed token budget exhausted"
                )
            row = self.connection.execute(
                "UPDATE runs SET calls=calls+1 WHERE id=? AND calls<?", (run_id, maximum)
            )
            if row.rowcount != 1:
                raise ExecutionError("limit_exceeded", "Agent call budget exhausted")
            invocation_id = uuid.uuid4().hex
            self.connection.execute(
                "INSERT INTO invocations VALUES(?,?,?,?,?,?,?)",
                (invocation_id, run_id, run["task"]["project_id"], now(), 0, None, "running"),
            )
            self.event(run_id, "agent.call_reserved", {"invocation_id": invocation_id})
            return invocation_id

    def budget(self, run_id: str) -> dict:
        """Account for failed/interrupted invocations across resumed and new project runs."""
        run = self.get(run_id)
        day = now()[:10]
        project = self.connection.execute(
            "SELECT count(*),coalesce(sum(total_tokens),0) FROM invocations WHERE project_id=? AND started_at LIKE ?",
            (run["task"]["project_id"], day + "%"),
        ).fetchone()
        total = self.connection.execute(
            "SELECT coalesce(sum(total_tokens),0),count(*)-count(usage_json) FROM invocations WHERE run_id=?",
            (run_id,),
        ).fetchone()
        return {
            "project_calls_today": project[0],
            "project_tokens_today": project[1],
            "run_tokens": total[0],
            "unknown_usage_invocations": total[1],
            "day_utc": day,
        }

    def observe_usage(self, invocation_id: str, usage: dict):
        """Persist monotonic cumulative counts before enforcing observed thresholds."""
        total = int(
            usage.get("total_tokens", usage.get("input_tokens", 0) + usage.get("output_tokens", 0))
        )
        if total < 0:
            raise ExecutionError("invalid_usage", "Provider usage cannot be negative")
        with self.connection:
            self.connection.execute(
                "UPDATE invocations SET total_tokens=max(total_tokens,?),usage_json=? WHERE id=?",
                (total, json.dumps(safe_value(usage)), invocation_id),
            )

    def finish_invocation(self, invocation_id: str, status: str):
        with self.connection:
            self.connection.execute(
                "UPDATE invocations SET status=? WHERE id=?", (status, invocation_id)
            )

    def request_cancel(self, run_id: str):
        self.get(run_id)
        with self.connection:
            self.connection.execute(
                "INSERT INTO controls VALUES(?,1) ON CONFLICT(run_id) DO UPDATE SET cancel_requested=1",
                (run_id,),
            )
            self.event(run_id, "control.cancel_requested", {})

    def cancelled(self, run_id: str) -> bool:
        row = self.connection.execute(
            "SELECT cancel_requested FROM controls WHERE run_id=?", (run_id,)
        ).fetchone()
        return bool(row and row[0])

    def effects(self, run_id: str) -> dict:
        return {
            row["name"]: {"status": row["status"], "result": json.loads(row["result_json"])}
            for row in self.connection.execute("SELECT * FROM effects WHERE run_id=?", (run_id,))
        }

    def effect(self, run_id: str, name: str, status: str, result: dict):
        with self.connection:
            self.connection.execute(
                "INSERT INTO effects VALUES(?,?,?,?) ON CONFLICT(run_id,name) DO UPDATE SET status=excluded.status,result_json=excluded.result_json",
                (run_id, name, status, json.dumps(safe_value(result))),
            )
            self.event(run_id, "delivery." + status, {"operation": name, "result": result})

    def events(self, run_id: str, after: int = 0, limit: int = 200) -> list[dict]:
        self.get(run_id)
        return [
            {**dict(row), "payload": json.loads(row["payload_json"])}
            for row in self.connection.execute(
                "SELECT id,timestamp,type,payload_json FROM events WHERE run_id=? AND id>? ORDER BY id LIMIT ?",
                (run_id, after, min(limit, 1000)),
            )
        ]

    def start_stage(self, run_id: str, attempt: int, name: str, revision_hash: str):
        """Persist running before a stage can have side effects."""
        with self.connection:
            self.connection.execute(
                "INSERT OR REPLACE INTO stages VALUES(?,?,?,?,?,?,?,?)",
                (run_id, attempt, name, "running", revision_hash, now(), None, None),
            )
            self.event(run_id, "stage.running", {"attempt": attempt, "stage": name})

    def update_stage_result(self, run_id: str, attempt: int, name: str, result: dict):
        """Persist observed progress without promoting the stage to success."""
        with self.connection:
            self.connection.execute(
                "UPDATE stages SET result_json=? WHERE run_id=? AND attempt=? AND name=? AND status='running'",
                (json.dumps(safe_value(result)), run_id, attempt, name),
            )

    def finish_stage(
        self, run_id: str, attempt: int, name: str, status: str, result: dict, revision_hash: str
    ):
        """Bind actual results and stage status to the current source fingerprint."""
        with self.connection:
            self.connection.execute(
                "UPDATE stages SET status=?,result_json=?,revision_hash=?,finished_at=? WHERE run_id=? AND attempt=? AND name=?",
                (
                    status,
                    json.dumps(safe_value(result)),
                    revision_hash,
                    now(),
                    run_id,
                    attempt,
                    name,
                ),
            )
            self.event(
                run_id,
                f"stage.{status}",
                {
                    "attempt": attempt,
                    "stage": name,
                    "revision_hash": revision_hash,
                    "result": result,
                },
            )

    def stages(self, run_id: str) -> list[dict]:
        """Read historical stage evidence, including invalidated attempts."""
        rows = self.connection.execute(
            "SELECT * FROM stages WHERE run_id=? ORDER BY attempt,started_at", (run_id,)
        )
        return [dict(row) for row in rows]

    def next_attempt(self, run_id: str, maximum: int):
        """Keep repair attempts bounded across restarts."""
        with self.connection:
            row = self.connection.execute(
                "UPDATE runs SET attempt=attempt+1 WHERE id=? AND attempt<?", (run_id, maximum)
            )
            if row.rowcount != 1:
                raise ExecutionError("limit_exceeded", "Repair attempt budget exhausted")
            self.event(run_id, "attempt.started", {})

    def invalidate(self, run_id: str):
        """Revoke passed checks/reviews after a workspace revision changes."""
        with self.connection:
            task = self.get(run_id)["task"]
            names = ["checks"] + [
                step["name"] for step in task.get("workflow", []) if step["kind"] == "verify"
            ]
            if len(names) == 1:
                names += ["qa", "review"]
            placeholders = ",".join("?" for _ in names)
            self.connection.execute(
                f"UPDATE stages SET status='invalidated' WHERE run_id=? AND name IN ({placeholders}) AND status='succeeded'",
                (run_id, *names),
            )
            self.connection.execute("UPDATE runs SET verified_hash=NULL WHERE id=?", (run_id,))
            self.event(run_id, "evidence.invalidated", {})
