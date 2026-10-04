"""Read workflow snapshots; keep GitHub credentials outside the monitor."""

import json
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from .contracts import ExecutionError
from .pipeline import group_steps, status
from .processes import execute, safe_value, sanitize

MARKER = "DEV_AGENT_KIT_CHECK_EVENT "


def snapshot_path(state, identity):
    if not re.fullmatch(r"[a-zA-Z0-9_.-]+", identity) or identity in {".", ".."}:
        raise ValueError("Invalid workflow identity")
    directory = Path(state).resolve() / "workflows"
    path = directory / (identity + ".json")
    if directory.is_symlink() or path.is_symlink():
        raise ValueError("Workflow snapshot symlinks are not allowed")
    return path


def read_snapshot(path):
    if path.is_symlink() or path.stat().st_size > 2_000_000:
        raise ValueError("Invalid workflow snapshot")
    value = json.loads(path.read_text())
    if not isinstance(value.get("jobs"), list):
        raise ValueError("Workflow snapshot has no jobs")
    return value


def list_workflows(state):
    result = []
    directory = Path(state) / "workflows"
    if directory.is_symlink():
        raise ValueError("Workflow snapshot symlinks are not allowed")
    paths = sorted(directory.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    for path in paths[:100]:
        item = read_snapshot(path)
        result.append(
            {key: item[key] for key in ("id", "name", "repository", "status", "updated_at", "url")}
        )
    return safe_value(result)


def workflow_detail(state, identity):
    item = read_snapshot(snapshot_path(state, identity))
    for job in item["jobs"]:
        job["phases"] = group_steps(job["steps"])
    return safe_value(item)


def project_job(job, lines):
    """Attribute timed logs to their source operation and unfold structured checks."""
    parsed_lines = []
    for line in lines:
        timestamp, separator, content = line.partition(" ")
        if separator and re.match(r"^\d{4}-\d{2}-\d{2}T", timestamp):
            try:
                parsed_lines.append(
                    (datetime.fromisoformat(timestamp.replace("Z", "+00:00")), sanitize(content))
                )
            except ValueError:
                continue
    # GitHub step times have second precision. Bind a complete runner invocation
    # through its first event so a terminal event in the rounded final second
    # does not leak into the following cleanup operation.
    invocations = {}
    for time, line in parsed_lines:
        if not line.startswith(MARKER):
            continue
        try:
            event = json.loads(line[len(MARKER) :])
            if not isinstance(event, dict) or not all(
                isinstance(event.get(k), str) for k in ("id", "name", "status")
            ):
                continue
            if not isinstance(event.get("argv"), list) or not all(
                isinstance(a, str) for a in event["argv"]
            ):
                continue
            if any(
                event.get(key) is not None and not isinstance(event[key], str)
                for key in (
                    "phase",
                    "phase_label",
                    "started_at",
                    "finished_at",
                    "stdout",
                    "stderr",
                    "error",
                )
            ):
                continue
            identity = event.get("invocation_id", "legacy")
            if not isinstance(identity, str) or len(identity) > 80:
                continue
            invocation = invocations.setdefault(identity, {"first": time, "events": {}})
            if len(invocation["events"]) < 20 or event["id"] in invocation["events"]:
                invocation["events"][event["id"]] = event
        except (ValueError, TypeError):
            continue
    assigned = {}
    sources = job.get("steps", [])
    for invocation in invocations.values():
        eligible = [
            source
            for source in sources
            if source.get("started_at")
            and not source["started_at"].startswith("0001-")
            and datetime.fromisoformat(source["started_at"].replace("Z", "+00:00"))
            <= invocation["first"]
        ]
        if eligible:
            source = max(eligible, key=lambda value: (value["started_at"], value["number"]))
            assigned.setdefault(source["number"], {}).update(invocation["events"])
    steps = []
    for source in sources:
        start, end = source.get("started_at"), source.get("completed_at")
        logs = [
            content
            for time, content in parsed_lines
            if start
            and not start.startswith("0001-")
            and time >= datetime.fromisoformat(start.replace("Z", "+00:00"))
            and (not end or time < datetime.fromisoformat(end.replace("Z", "+00:00")))
        ]
        events = assigned.get(source["number"], {})
        if events:
            for event in events.values():
                steps.append(
                    {
                        "id": str(source["number"]) + ":" + event["id"],
                        "name": event["name"],
                        "source_step": source["name"],
                        "phase": event.get("phase"),
                        "phase_label": event.get("phase_label"),
                        "argv": event["argv"],
                        "status": status(event["status"]),
                        "started_at": event.get("started_at"),
                        "finished_at": event.get("finished_at"),
                        "logs": (event.get("stdout", "") + event.get("stderr", ""))[-50000:],
                        "error": event.get("error"),
                    }
                )
        else:
            steps.append(
                {
                    "id": str(source["number"]),
                    "name": source["name"],
                    "status": status(source.get("conclusion") or source["status"]),
                    "started_at": start,
                    "finished_at": end,
                    "logs": "\n".join(logs)[-12000:],
                    "error": "This operation failed; inspect technical logs."
                    if status(source.get("conclusion") or source["status"]) == "failed"
                    else None,
                }
            )
    return {
        "id": str(job["id"]),
        "name": job["name"],
        "status": status(job.get("conclusion") or job["status"]),
        "steps": steps,
        "logs": "\n".join(sanitize(line) for line in lines)[-50000:],
    }


def sync_github(state, repository, run_id, include_logs=False):
    """Fetch one authorized run with bounded API calls, output and time."""
    if (
        not re.fullmatch(r"[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+", repository)
        or not str(run_id).isdigit()
    ):
        raise ValueError("Use owner/repository and a numeric run ID")

    def fetch(endpoint, raw=False):
        outcome = execute(
            ["gh", "api", endpoint, *(["--allow-escape-sequences"] if raw else [])],
            Path(state).parent,
            30,
            max_output_bytes=2_000_000,
        )
        if outcome.exit_code or outcome.timed_out:
            raise ExecutionError(
                "workflow_sync_failed", "GitHub evidence unavailable: " + outcome.stderr[-2000:]
            )
        return outcome.stdout if raw else json.loads(outcome.stdout)

    run = fetch(f"repos/{repository}/actions/runs/{run_id}")
    response = fetch(f"repos/{repository}/actions/runs/{run_id}/jobs?per_page=100")
    jobs = response["jobs"]
    if response.get("total_count", len(jobs)) > 20:
        raise ValueError("At most 20 jobs per snapshot; run was not imported partially")
    value = {
        "id": repository.replace("/", "--") + "--" + str(run_id),
        "name": run.get("display_title") or run["name"],
        "repository": repository,
        "status": status(run.get("conclusion") or run["status"]),
        "url": run["html_url"],
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "jobs": [],
    }
    for job in jobs:
        lines = (
            fetch(f"repos/{repository}/actions/jobs/{job['id']}/logs", raw=True).splitlines()
            if include_logs and job["status"] == "completed"
            else []
        )
        value["jobs"].append(project_job(job, lines))
    directory = Path(state) / "workflows"
    path = snapshot_path(state, value["id"])
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    with tempfile.NamedTemporaryFile(mode="w", dir=directory, delete=False) as output:
        temporary = Path(output.name)
        try:
            output.write(json.dumps(safe_value(value), indent=2) + "\n")
            output.flush()
            temporary.replace(path)
        finally:
            temporary.unlink(missing_ok=True)
    return value["id"]
