"""Execute explicit argument arrays with bounded duration and sanitized output."""

from __future__ import annotations

import os
import re
import signal
import subprocess
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

from .contracts import ExecutionError


@dataclass(frozen=True)
class ProcessResult:
    """Retain actual command outcomes instead of inferring success from prose."""

    exit_code: int
    stdout: str
    stderr: str
    duration_seconds: float
    timed_out: bool = False


def sanitize(text: str) -> str:
    """Redact known secret formats and secret-bearing environment values."""
    text = re.sub(r"\x1b\[[0-?]*[ -/]*[@-~]", "", text)
    text = re.sub(r"[\x00-\x08\x0b-\x1f\x7f]", "", text)
    for key, value in os.environ.items():
        if len(value) >= 8 and re.search(r"TOKEN|SECRET|PASSWORD|API_KEY", key, re.I):
            text = text.replace(value, "[REDACTED]")
    text = re.sub(r"\b(?:sk-[A-Za-z0-9_-]{12,}|gh[pousr]_[A-Za-z0-9]{12,})", "[REDACTED]", text)
    text = re.sub(r"(?i)(bearer\s+)[A-Za-z0-9._-]+", r"\1[REDACTED]", text)
    text = re.sub(
        r"(?i)((?:api[_-]?key|password|secret|access[_-]?token)\s*[=:]\s*)[^\s,;]+",
        r"\1[REDACTED]",
        text,
    )
    return text


def safe_value(value):
    """Sanitize structured artifacts without storing raw provider transcripts."""
    if isinstance(value, str):
        return sanitize(value)
    if isinstance(value, list):
        return [safe_value(item) for item in value]
    if isinstance(value, dict):
        return {key: safe_value(item) for key, item in value.items()}
    return value


def execute(
    argv: list[str],
    cwd: Path,
    timeout: float,
    stdin: str | None = None,
    max_output_bytes: int = 1_048_576,
    on_line=None,
    on_tick=None,
) -> ProcessResult:
    """Terminate the whole process group on timeout; never invoke a shell wrapper."""
    if timeout <= 0:
        raise ExecutionError("limit_exceeded", "Execution deadline exhausted")
    started = time.monotonic()
    with tempfile.TemporaryFile() as output, tempfile.TemporaryFile() as errors:
        try:
            process = subprocess.Popen(
                argv,
                cwd=cwd,
                stdin=subprocess.PIPE if stdin is not None else subprocess.DEVNULL,
                stdout=output,
                stderr=errors,
                start_new_session=True,
            )
        except FileNotFoundError as error:
            raise ExecutionError("tool_unavailable", "Required command is not installed") from error
        timed_out = False
        supplied_input = None if stdin is None else stdin.encode()
        read_offset, pending = 0, b""

        def drain():
            nonlocal read_offset, pending
            if on_line is None:
                return
            data = os.pread(output.fileno(), max_output_bytes + 1, read_offset)
            read_offset += len(data)
            pending += data
            while b"\n" in pending:
                line, pending = pending.split(b"\n", 1)
                on_line(sanitize(line.decode(errors="replace")))
            if len(pending) > max_output_bytes:
                raise ExecutionError("output_limit", "Provider event exceeded capture limit")

        try:
            while True:
                if on_tick:
                    on_tick()
                drain()
                remaining = timeout - (time.monotonic() - started)
                if remaining <= 0:
                    timed_out = True
                    os.killpg(process.pid, signal.SIGKILL)
                    process.communicate()
                    break
                if (
                    os.fstat(output.fileno()).st_size + os.fstat(errors.fileno()).st_size
                    > max_output_bytes
                ):
                    os.killpg(process.pid, signal.SIGKILL)
                    process.communicate()
                    raise ExecutionError(
                        "output_limit", "Command output exceeded its configured capture limit"
                    )
                try:
                    process.communicate(supplied_input, timeout=min(0.1, remaining))
                    drain()
                    break
                except subprocess.TimeoutExpired:
                    supplied_input = None
        except BaseException:
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGKILL)
                process.communicate()
            raise
        output.seek(0)
        errors.seek(0)
        stdout = output.read(max_output_bytes + 1)
        stderr = errors.read(max_output_bytes + 1)
        if len(stdout) + len(stderr) > max_output_bytes:
            raise ExecutionError(
                "output_limit", "Command output exceeded its configured capture limit"
            )
        return ProcessResult(
            process.returncode,
            sanitize(stdout.decode(errors="replace")),
            sanitize(stderr.decode(errors="replace")),
            time.monotonic() - started,
            timed_out,
        )
