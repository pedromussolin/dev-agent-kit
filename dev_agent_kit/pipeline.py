"""Project technical operations into logical phases without depending on a CI vendor."""

import re
from datetime import datetime, timezone

LABELS = {
    "environment": ("Preparing environment", "Preparando ambiente"),
    "shared": ("Loading shared dependencies", "Carregando recursos compartilhados"),
    "dependencies": ("Installing project dependencies", "Instalando dependências"),
    "quality": ("Checking code quality", "Verificando qualidade"),
    "tests": ("Running tests", "Executando testes"),
    "build": ("Building application", "Construindo aplicação"),
    "validation": ("Validating results", "Validando resultados"),
    "cleanup": ("Cleaning up", "Finalizando execução"),
    "implementation": ("Implementing changes", "Implementando alterações"),
    "review": ("Reviewing changes", "Revisando alterações"),
    "publication": ("Publishing changes", "Publicando alterações"),
    "merge": ("Integrating changes", "Integrando alterações"),
    "deployment": ("Deploying application", "Disponibilizando aplicação"),
}


def status(value):
    """Normalize observed statuses while preserving unknown work as pending."""
    return {
        "succeeded": "success",
        "completed": "pending",
        "in_progress": "running",
        "queued": "pending",
        "waiting": "pending",
        "failure": "failed",
        "cancelled": "failed",
        "timed_out": "failed",
        "blocked": "failed",
        "invalidated": "pending",
    }.get(value, value if value in {"success", "failed", "skipped", "running"} else "pending")


def responsibility(step):
    """Honor explicit phase metadata and infer only recognizable responsibilities."""
    if step.get("phase"):
        return step["phase"]
    name = step.get("name", "")
    text = (name + " " + " ".join(step.get("argv", []))).lower()
    rules = [
        ("cleanup", r"\b(post |clean.?up|finaliz|complete job)"),
        ("shared", r"\b(shared|shared-actions|reusable|compartilhad)"),
        (
            "environment",
            r"checkout|setup-|set up job|prepare.*environment|package manager|corepack enable",
        ),
        ("dependencies", r"install|dependenc|dependência|\b(pip|npm|pnpm|uv) (sync|ci)\b"),
        ("quality", r"lint|format|prettier|ruff|\btsc\b|type.?check|\btypes\b"),
        ("tests", r"\b(test|tests|unit|unittest|pytest|integration|e2e)\b"),
        ("build", r"\b(build|compile|bundle)\b"),
        ("validation", r"validat|verify|smoke|health|require immutable"),
    ]
    for phase, pattern in rules:
        if re.search(pattern, text):
            return phase
    # Unknown responsibilities stay distinct. A custom name is not guessed away.
    return "custom:" + str(step.get("id", name))


def seconds(start, end=None, now=None):
    """Return elapsed wall time, including current duration for active operations."""
    if not start:
        return None
    try:
        if start.startswith("0001-"):
            return None
        first = datetime.fromisoformat(start.replace("Z", "+00:00"))
        last = (
            datetime.fromisoformat(end.replace("Z", "+00:00"))
            if end
            else now or datetime.now(timezone.utc)
        )
        return max(0, (last - first).total_seconds())
    except (ValueError, TypeError):
        return None


def group_steps(steps):
    """Group adjacent operations with the same responsibility, preserving chronology."""
    phases = []
    for operation in steps:
        step = dict(operation)
        step["status"] = status(step.get("status"))
        step.setdefault(
            "duration_seconds",
            seconds(step.get("started_at"), step.get("finished_at"))
            if step["status"] != "pending"
            else None,
        )
        phase = responsibility(step)
        if not phases or phases[-1]["phase"] != phase:
            label = step.get("phase_label") or dict(
                zip(("en", "pt"), LABELS.get(phase, (step.get("name", phase),) * 2))
            )
            if isinstance(label, str):
                label = {"en": label, "pt": label}
            phases.append(
                {"id": str(len(phases)) + ":" + phase, "phase": phase, "label": label, "steps": []}
            )
        phases[-1]["steps"].append(step)
    for phase in phases:
        statuses = [step["status"] for step in phase["steps"]]
        phase["status"] = (
            "failed"
            if "failed" in statuses
            else "running"
            if "running" in statuses
            else "pending"
            if "pending" in statuses
            else "skipped"
            if all(x == "skipped" for x in statuses)
            else "success"
        )
        # Sum child execution time; parallel jobs are projected separately.
        durations = [
            step["duration_seconds"]
            for step in phase["steps"]
            if step["duration_seconds"] is not None
        ]
        phase["duration_seconds"] = sum(durations) if durations else None
        phase["errors"] = [
            (
                (step.get("error") or {}).get("message", step["name"])
                if isinstance(step.get("error"), dict)
                else step.get("error") or step.get("name")
            )
            for step in phase["steps"]
            if step["status"] == "failed"
        ]
    return phases


def executor_steps(task, stages, effects, terminal_status=None):
    """Derive the configured task path and observed checks instead of a fixed stage list."""
    result = []
    for definition in task.get("workflow", []):
        stage = next((s for s in reversed(stages) if s["name"] == definition["name"]), {})
        result.append(
            {
                "id": definition["name"],
                "name": definition["name"],
                "role_id": definition["role_id"],
                "phase": definition.get("phase")
                or (
                    "implementation"
                    if definition["kind"] == "implement"
                    else "review"
                    if definition["role_id"] == "technical-reviewer"
                    else "validation"
                    if definition["kind"] == "verify"
                    else "custom:" + definition["name"]
                ),
                "phase_label": definition.get("phase_label"),
                "status": stage.get("status", "pending"),
                "started_at": stage.get("started_at"),
                "finished_at": stage.get("finished_at"),
                "summary": stage.get("summary"),
                "error": stage.get("error"),
            }
        )
        if definition["kind"] == "implement":
            check_stage = next((s for s in reversed(stages) if s["name"] == "checks"), {})
            checked = {(c.get("component"), c["name"]): c for c in check_stage.get("checks", [])}
            for component in task["components"]:
                for check in component["checks"]:
                    observed = checked.get((component["name"], check["name"]), {})
                    result.append(
                        {
                            "id": component["name"] + ":" + check["name"],
                            "name": check["name"],
                            "argv": check["argv"],
                            "component": component["name"],
                            "status": "failed"
                            if check_stage.get("failed_check")
                            == component["name"] + ":" + check["name"]
                            and check_stage.get("error")
                            else ("success" if observed.get("exit_code") == 0 else "failed")
                            if observed
                            else "running"
                            if check_stage.get("active_check")
                            == component["name"] + ":" + check["name"]
                            else "failed"
                            if check_stage.get("failed_check")
                            == component["name"] + ":" + check["name"]
                            else "pending",
                            "duration_seconds": observed.get("duration_seconds"),
                            "logs": observed.get("stdout", "") + observed.get("stderr", ""),
                            "error": observed.get("error")
                            or (
                                check_stage.get("error")
                                if check_stage.get("failed_check")
                                == component["name"] + ":" + check["name"]
                                else None
                            ),
                            "phase": check.get("phase"),
                            "phase_label": check.get("phase_label"),
                        }
                    )
    mappings = {
        "publish": "publication",
        "pull_request": "publication",
        "merge": "merge",
        "deployment": "deployment",
    }
    mode = task.get("policy", {}).get("delivery", "diff")
    expected = ["publish", "pull_request"] if mode in {"pull_request", "merge", "deploy"} else []
    if mode in {"merge", "deploy"}:
        expected.append("merge")
    if mode == "deploy":
        expected.append("deployment")
    observed_effects = {effect["name"]: effect for effect in effects}
    ordered = [observed_effects.pop(name, {"name": name, "status": "pending"}) for name in expected]
    ordered.extend(observed_effects.values())
    for effect in ordered:
        value = effect.get("result", {})
        result.append(
            {
                "id": effect["name"],
                "name": effect["name"],
                "phase": mappings.get(effect["name"], effect["name"]),
                "status": effect["status"],
                "started_at": effect.get("started_at"),
                "finished_at": effect.get("finished_at"),
                "summary": value.get("environment"),
                "logs": value.get("stdout", "") + value.get("stderr", ""),
                "error": value.get("error"),
            }
        )
    if terminal_status in {"failed", "cancelled", "blocked"}:
        for step in result:
            if step["status"] == "pending":
                step["status"] = "skipped"
    return result
