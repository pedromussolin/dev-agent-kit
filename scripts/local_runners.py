"""Operate already registered personal Linux runners without copying credentials."""

import argparse
import json
import os
import signal
import subprocess
import time
from pathlib import Path

ROOT = Path.home() / ".local/share/dev-agent-kit"
STATE = Path.home() / ".local/state/dev-agent-kit"


def identity(pid):
    """Bind a control record to its actual Linux process start time."""
    try:
        return (Path("/proc") / str(pid) / "stat").read_text().rsplit(")", 1)[1].split()[19]
    except FileNotFoundError:
        return None


def operate(name, action):
    """Start or stop one configured runner under a private process record."""
    if not name or any(
        character not in "abcdefghijklmnopqrstuvwxyz0123456789-" for character in name
    ):
        raise ValueError("Runner name must contain lowercase letters, digits or hyphens")
    directory = ROOT / name
    configuration = directory / ".runner"
    if not configuration.is_file():
        raise ValueError("Register the runner before starting it")
    record = directory / "local-process.json"
    value = json.loads(record.read_text()) if record.exists() else {}
    active = bool(value.get("pid") and identity(value["pid"]) == value.get("identity"))
    if action == "status":
        print(name + ": " + ("running" if active else "stopped"))
        return
    if action == "stop":
        if active:
            os.killpg(value["pid"], signal.SIGTERM)
        print(name + ": stop requested" if active else name + ": already stopped")
        return
    if active:
        print(name + ": already running")
        return
    repository = json.loads(configuration.read_text(encoding="utf-8-sig"))["gitHubUrl"]
    slug = repository.removeprefix("https://github.com/").rstrip("/")
    private = subprocess.check_output(
        ["gh", "api", "repos/" + slug, "--jq", ".private"], text=True
    ).strip()
    if private != "true":
        raise ValueError("This personal runner launcher requires a private repository")
    python = ROOT / "executor-venv/bin/python"
    if not python.is_file():
        raise ValueError("Prepare the persistent executor virtual environment first")
    STATE.mkdir(parents=True, exist_ok=True, mode=0o700)
    env = {**os.environ, "DEV_AGENT_KIT_PYTHON": str(python), "DEV_AGENT_KIT_STATE_DIR": str(STATE)}
    log_path = directory / "local-runner.log"
    with log_path.open("a") as log:
        log_path.chmod(0o600)
        process = subprocess.Popen(
            ["bash", "./run.sh"],
            cwd=directory,
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=log,
            stderr=log,
            start_new_session=True,
        )
    time.sleep(0.2)
    if process.poll() is not None:
        raise ValueError("Runner exited; inspect its private local log")
    record.write_text(json.dumps({"pid": process.pid, "identity": identity(process.pid)}) + "\n")
    record.chmod(0o600)
    print(name + ": started; confirm online status with GitHub")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["start", "status", "stop"])
    parser.add_argument("names", nargs="+")
    arguments = parser.parse_args()
    for name in arguments.names:
        operate(name, arguments.action)


if __name__ == "__main__":
    main()
