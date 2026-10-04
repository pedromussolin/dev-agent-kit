"""Describe root components and check suggestions without executing project code."""

from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path

_MAX_MANIFEST_BYTES = 1024 * 1024
_LOCKFILES = {
    "npm": ("package-lock.json", "npm-shrinkwrap.json"),
    "pnpm": ("pnpm-lock.yaml",),
    "yarn": ("yarn.lock",),
    "bun": ("bun.lock", "bun.lockb"),
}


def _present(path: Path) -> bool:
    if path.is_symlink():
        raise ValueError(f"{path.name}: symlinked metadata is not supported")
    if not path.exists():
        return False
    if not path.is_file():
        raise ValueError(f"{path.name}: expected a regular metadata file")
    return True


def _read(path: Path) -> str:
    try:
        with path.open("rb") as source:
            content = source.read(_MAX_MANIFEST_BYTES + 1)
        if len(content) > _MAX_MANIFEST_BYTES:
            raise ValueError("manifest exceeds the 1 MiB inspection limit")
        return content.decode("utf-8")
    except (OSError, ValueError) as error:
        raise ValueError(f"{path.name}: cannot read manifest ({error})") from error


def _metadata(path: Path) -> dict:
    try:
        content = _read(path)
        value = json.loads(content) if path.suffix == ".json" else tomllib.loads(content)
    except (json.JSONDecodeError, tomllib.TOMLDecodeError) as error:
        raise ValueError(f"{path.name}: invalid manifest ({error})") from error
    if not isinstance(value, dict):
        raise ValueError(f"{path.name}: manifest must contain an object")
    return value


def _table(metadata: dict, key: str, filename: str) -> dict:
    value = metadata.get(key, {})
    if not isinstance(value, dict):
        raise ValueError(f"{filename}: {key} must be a table/object")
    return value


def _name(metadata: dict, fallback: str, filename: str) -> str:
    value = metadata.get("name", fallback)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{filename}: name must be a nonempty string")
    return value


def _check(name: str, argv: list[str]) -> dict:
    return {"name": name, "argv": argv, "timeout_seconds": 120}


def _component(name: str, language: str, manifests: list[str], checks: list[dict]) -> dict:
    return {
        "name": name,
        "language": language,
        "working_directory": ".",
        "manifests": manifests,
        "suggested_checks": checks,
    }


def detect_components(repository: Path) -> list[dict]:
    """Read root manifests and return independent language components.

    Args:
        repository: Existing repository directory; no Git metadata is required.

    Returns:
        Components with argument-array check suggestions, or an empty list when
        no supported manifests exist. No suggested command is executed.

    Raises:
        ValueError: The root is missing, metadata is unreadable or malformed, or
            conflicting JavaScript lockfiles prevent selecting a package manager.
    """
    if not repository.is_dir():
        raise ValueError(f"Repository directory is unavailable: {repository}")
    components = []

    python_manifests = [
        filename
        for filename in ("pyproject.toml", "requirements.txt")
        if _present(repository / filename)
    ]
    if python_manifests:
        metadata = (
            _metadata(repository / "pyproject.toml") if "pyproject.toml" in python_manifests else {}
        )
        if "requirements.txt" in python_manifests:
            # Requirements are opaque here; dependency resolution is outside inspection.
            _read(repository / "requirements.txt")
        project = _table(metadata, "project", "pyproject.toml")
        tools = _table(metadata, "tool", "pyproject.toml")
        checks = []
        if "pytest" in tools:
            _table(tools, "pytest", "pyproject.toml")
            checks.append(_check("test", ["python", "-m", "pytest"]))
        elif (repository / "tests").is_dir() and not (repository / "tests").is_symlink():
            checks.append(
                _check("test", ["python", "-m", "unittest", "discover", "-s", "tests", "-v"])
            )
        if (
            "ruff" in tools
            or _present(repository / "ruff.toml")
            or _present(repository / ".ruff.toml")
        ):
            checks.extend(
                [
                    _check("lint", ["python", "-m", "ruff", "check", "."]),
                    _check("format", ["python", "-m", "ruff", "format", "--check", "."]),
                ]
            )
        components.append(
            _component(
                _name(project, "python", "pyproject.toml"), "python", python_manifests, checks
            )
        )

    if _present(repository / "go.mod"):
        content = _read(repository / "go.mod")
        modules = re.findall(
            r'^\s*module\s+("[^"\r\n]+"|[^\s"]+)\s*(?://[^\n]*)?$', content, re.MULTILINE
        )
        if len(modules) != 1:
            raise ValueError("go.mod: expected exactly one module declaration")
        components.append(
            _component(
                modules[0].strip('"'), "go", ["go.mod"], [_check("test", ["go", "test", "./..."])]
            )
        )

    if _present(repository / "package.json"):
        metadata = _metadata(repository / "package.json")
        scripts = _table(metadata, "scripts", "package.json")
        if any(not isinstance(command, str) for command in scripts.values()):
            raise ValueError("package.json: script commands must be strings")
        managers = [
            manager
            for manager, filenames in _LOCKFILES.items()
            if any([_present(repository / filename) for filename in filenames])
        ]
        if len(managers) > 1:
            raise ValueError(
                "package.json: conflicting package-manager lockfiles: " + ", ".join(managers)
            )
        manager = managers[0] if managers else "npm"
        checks = [
            _check(name, [manager, "run", name])
            for name in ("test", "lint", "format:check", "build", "typecheck")
            if scripts.get(name, "").strip()
        ]
        components.append(
            _component(
                _name(metadata, "javascript", "package.json"),
                "javascript",
                ["package.json"],
                checks,
            )
        )

    if _present(repository / "Cargo.toml"):
        metadata = _metadata(repository / "Cargo.toml")
        package = _table(metadata, "package", "Cargo.toml")
        _table(metadata, "workspace", "Cargo.toml")
        if "package" not in metadata and "workspace" not in metadata:
            raise ValueError("Cargo.toml: expected a package or workspace table")
        components.append(
            _component(
                _name(package, "rust", "Cargo.toml"),
                "rust",
                ["Cargo.toml"],
                [_check("test", ["cargo", "test"])],
            )
        )

    return components
