"""Prepare isolated Git worktrees and bind checks to exact source content."""

from __future__ import annotations

import difflib
import fnmatch
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

from .contracts import ExecutionError, fingerprint, local_path


def git(repository: Path, *args: str) -> str:
    """Run a bounded Git operation and return safe diagnostic categories."""
    try:
        result = subprocess.run(
            ["git", "-C", str(repository), *args], capture_output=True, text=True, timeout=30
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise ExecutionError("workspace_error", "Git operation unavailable or timed out") from error
    if result.returncode:
        raise ExecutionError("workspace_error", f"Git operation failed: {args[0]}")
    return result.stdout


def files(repository: Path) -> list[str]:
    """Inspect tracked/untracked project files, excluding ignored local credentials/caches."""
    names = set(
        git(repository, "ls-files", "-z", "--cached", "--others", "--exclude-standard").split("\0")
    )
    names.discard("")
    return sorted(name for name in names if local_path(repository, name).is_file())


def source_manifest(repository: Path) -> dict[str, dict]:
    """Fingerprint contents and executable bits, rejecting unsafe symlink inputs."""
    result = {}
    for name in files(repository):
        path = local_path(repository, name)
        if path.name == ".env" or (path.name.startswith(".env.") and path.name != ".env.example"):
            raise ExecutionError(
                "unsafe_input", "Secret-bearing environment files cannot enter a source snapshot"
            )
        result[name] = {
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "executable": bool(path.stat().st_mode & 0o111),
        }
    return result


def current_revision(repository: Path, base_revision: str) -> str:
    """Include Git identity in source evidence; commits/branch changes are not authorized."""
    head = git(repository, "rev-parse", "HEAD").strip()
    if head != base_revision:
        raise ExecutionError(
            "scope_violation", "Agent workspace HEAD changed outside the executor delivery stage"
        )
    return fingerprint({"head": head, "files": source_manifest(repository)})


def prepare(task: dict, workspace: Path, run_directory: Path) -> str:
    """Snapshot authorized uncommitted inputs without modifying the source checkout."""
    repository = Path(task["repository"])
    resolved = git(
        repository, "rev-parse", "--verify", f"{task['base_revision']}^{{commit}}"
    ).strip()
    if resolved != task["base_revision"]:
        raise ExecutionError(
            "invalid_task", "Supply the exact base commit, not a mutable branch name"
        )
    if (
        not task["policy"]["include_working_tree"]
        and git(repository, "status", "--porcelain").strip()
    ):
        raise ExecutionError(
            "dirty_repository", "Authorize a working-tree snapshot or provide a clean repository"
        )
    before = source_manifest(repository) if task["policy"]["include_working_tree"] else None
    git(repository, "worktree", "add", "--detach", str(workspace), resolved)
    if before is not None:
        for name in files(workspace):
            if name not in before:
                local_path(workspace, name).unlink()
        for name in before:
            target = local_path(workspace, name)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(local_path(repository, name), target)
        if before != source_manifest(repository):
            raise ExecutionError(
                "input_changed", "Source changed while preparing the isolated snapshot"
            )
    baseline = run_directory / "baseline"
    baseline.mkdir(mode=0o700)
    manifest = source_manifest(workspace)
    for name in manifest:
        target = local_path(baseline, name)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(local_path(workspace, name), target)
    (run_directory / "baseline.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return current_revision(workspace, resolved)


def changes(workspace: Path, run_directory: Path, allowed_paths: list[str]) -> list[str]:
    """Check the complete task diff rather than trusting a model's file list."""
    baseline = json.loads((run_directory / "baseline.json").read_text())
    current = source_manifest(workspace)
    changed = sorted(
        name for name in baseline.keys() | current.keys() if baseline.get(name) != current.get(name)
    )
    if any(
        not any(fnmatch.fnmatchcase(name, pattern) for pattern in allowed_paths) for name in changed
    ):
        raise ExecutionError(
            "scope_violation", "A changed file is outside the task's allowed paths"
        )
    patch = []
    for name in changed:
        old = local_path(run_directory / "baseline", name)
        new = local_path(workspace, name)
        old_bytes = old.read_bytes() if old.exists() else b""
        new_bytes = new.read_bytes() if new.exists() else b""
        try:
            patch.extend(
                difflib.unified_diff(
                    old_bytes.decode().splitlines(keepends=True),
                    new_bytes.decode().splitlines(keepends=True),
                    fromfile=f"a/{name}" if old.exists() else "/dev/null",
                    tofile=f"b/{name}" if new.exists() else "/dev/null",
                )
            )
        except UnicodeDecodeError:
            patch.append(f"Binary file changed: {name}\n")
    (run_directory / "task.patch").write_text("".join(patch))
    return changed
