"""Package project-scoped agent profiles without invoking models or changing credentials."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import tomllib
from collections.abc import Callable, Mapping
from pathlib import Path

PROVIDERS = ("codex", "claude", "copilot")
MANIFEST = ".dev-agent-kit-profiles.json"
NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")


class ProfileError(ValueError):
    """Report invalid sources, profile drift or unsafe target paths."""


def confined_path(root: Path, relative: str) -> Path:
    """Resolve a relative path and reject traversal or symlinks below its root."""
    value = Path(relative)
    if value.is_absolute() or ".." in value.parts or not value.parts:
        raise ProfileError(f"Invalid relative path: {relative}")
    candidate = root / value
    cursor = root
    for part in value.parts:
        cursor = cursor / part
        if cursor.is_symlink():
            raise ProfileError(f"Symlink paths are not supported: {relative}")
    if not candidate.resolve().is_relative_to(root.resolve()):
        raise ProfileError(f"Path escapes root: {relative}")
    return candidate


def skill_metadata(path: Path) -> dict[str, str]:
    """Read the kit's minimal two-field YAML frontmatter without a YAML dependency."""
    content = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\n(.*?)\n---\n", content, re.S)
    if not match:
        raise ProfileError(f"Invalid skill frontmatter: {path}")
    result = {}
    for line in match.group(1).splitlines():
        key, separator, value = line.partition(":")
        if not separator or key not in {"name", "description"} or key in result:
            raise ProfileError(f"Expected minimal name/description frontmatter: {path}")
        value = value.strip()
        result[key] = json.loads(value) if value.startswith('"') else value
    if set(result) != {"name", "description"} or not all(
        isinstance(value, str) and value.strip() for value in result.values()
    ):
        raise ProfileError(f"Missing skill name/description: {path}")
    if not NAME.fullmatch(result["name"]) or len(result["name"]) > 64:
        raise ProfileError(f"Invalid skill name: {path}")
    if result["name"] != path.parent.name or len(result["description"]) > 1024:
        raise ProfileError(f"Skill metadata violates naming/length constraints: {path}")
    return result


def load_catalog(source: Path) -> list[dict]:
    """Validate role identities and portable schema/policy resource consistency."""
    catalog = json.loads(confined_path(source, "agents/catalog.json").read_text())
    if catalog.get("schema_version") != 1 or not isinstance(catalog.get("roles"), list):
        raise ProfileError("Invalid catalog version or roles")
    if not catalog["roles"]:
        raise ProfileError("The role catalog is empty")
    schema_path = confined_path(source, "contracts/agent-result.schema.json")
    contract = schema_path.read_bytes()
    schema = json.loads(contract)
    defaults = confined_path(source, "policies/project-defaults.json").read_bytes()
    json.loads(defaults)
    seen = set()
    for role in catalog["roles"]:
        role_id = role.get("id", "")
        if not isinstance(role_id, str) or not NAME.fullmatch(role_id) or role_id in seen:
            raise ProfileError(f"Invalid or duplicate role ID: {role_id}")
        seen.add(role_id)
        for key in ("title", "group", "description", "instructions"):
            if not isinstance(role.get(key), str) or not role[key].strip():
                raise ProfileError(f"Missing {key} for {role_id}")
        if role.get("access") not in {"analysis", "workspace"}:
            raise ProfileError(f"Invalid access mode for {role_id}")
        instructions = confined_path(source, role["instructions"])
        if not instructions.is_file() or not instructions.read_text().strip():
            raise ProfileError(f"Missing instructions for {role_id}")
        if not isinstance(role.get("skills"), list) or not role["skills"]:
            raise ProfileError(f"Missing skills for {role_id}")
        for name in role["skills"]:
            if not isinstance(name, str) or not NAME.fullmatch(name):
                raise ProfileError(f"Invalid skill reference for {role_id}")
            skill = confined_path(source, f".agents/skills/{name}/SKILL.md")
            skill_metadata(skill)
            reference = confined_path(
                source, f".agents/skills/{name}/references/result-contract.json"
            )
            if reference.read_bytes() != contract:
                raise ProfileError(f"Stale bundled result contract: {name}")
            policy = confined_path(
                source, f".agents/skills/{name}/references/project-defaults.json"
            )
            if policy.read_bytes() != defaults:
                raise ProfileError(f"Stale bundled project defaults: {name}")
            for resource in skill.parent.glob("references/*.schema.json"):
                bundled = confined_path(source, resource.relative_to(source).as_posix())
                canonical = confined_path(source, f"contracts/{resource.name}")
                if bundled.read_bytes() != canonical.read_bytes():
                    raise ProfileError(f"Stale bundled {resource.name}: {name}")
    if any(
        not re.fullmatch(schema["properties"]["role_id"]["pattern"], role_id) for role_id in seen
    ):
        raise ProfileError("Result contract role ID pattern does not cover the catalog")
    return catalog["roles"]


def render_codex(role: dict, prompt: str) -> dict[str, bytes]:
    """Render a native Codex configuration layer without pinning a model."""
    sandbox = "workspace-write" if role["access"] == "workspace" else "read-only"
    native = (
        f"name = {json.dumps(role['id'])}\n"
        f"description = {json.dumps(role['description'])}\n"
        f"sandbox_mode = {json.dumps(sandbox)}\n"
        f"developer_instructions = {json.dumps(prompt, ensure_ascii=False)}\n"
    )
    tomllib.loads(native)
    return {f".codex/agents/{role['id']}.toml": native.encode()}


def render_claude(role: dict, prompt: str) -> dict[str, bytes]:
    """Render Claude Code frontmatter with its documented skill preloading."""
    tools = ["Read", "Grep", "Glob", "WebSearch", "WebFetch", "Skill"]
    if role["access"] == "workspace":
        tools += ["Edit", "Write", "Bash"]
    if role["id"] == "sdlc-coordinator":
        tools = ["Read", "Grep", "Glob", "Skill", "Agent"]
    native = (
        "---\n"
        f"name: {role['id']}\n"
        f"description: {json.dumps(role['description'])}\n"
        f"tools: {json.dumps(tools)}\n"
        f"skills: {json.dumps(role['skills'])}\n"
        "---\n\n" + prompt.replace(".agents/skills/", ".claude/skills/")
    )
    return {f".claude/agents/{role['id']}.md": native.encode()}


def render_copilot(role: dict, prompt: str) -> dict[str, bytes]:
    """Render Copilot's documented tool aliases and custom-agent format."""
    tools = ["read", "search", "web"]
    if role["access"] == "workspace":
        tools += ["edit", "execute"]
    if role["id"] == "sdlc-coordinator":
        tools = ["read", "search", "agent"]
    native = (
        "---\n"
        f"name: {role['id']}\n"
        f"description: {json.dumps(role['description'])}\n"
        f"tools: {json.dumps(tools)}\n"
        "---\n\n" + prompt
    )
    return {f".github/agents/{role['id']}.agent.md": native.encode()}


Renderer = Callable[[dict, str], dict[str, bytes]]
PROFILE_RENDERERS: dict[str, Renderer] = {
    "codex": render_codex,
    "claude": render_claude,
    "copilot": render_copilot,
}


def render_profiles(
    source: Path,
    providers: tuple[str, ...] = PROVIDERS,
    *,
    renderers: Mapping[str, Renderer] | None = None,
) -> dict[str, bytes]:
    """Render native profiles and portable skill bundles from canonical sources."""
    selected_renderers = PROFILE_RENDERERS if renderers is None else renderers
    if (
        not providers
        or len(set(providers)) != len(providers)
        or any(provider not in selected_renderers for provider in providers)
    ):
        raise ProfileError("Unknown or empty provider selection")
    roles = load_catalog(source)
    files = {}
    for role in roles:
        instructions = confined_path(source, role["instructions"]).read_text(encoding="utf-8")
        paths = ", ".join(f".agents/skills/{skill}/SKILL.md" for skill in role["skills"])
        prompt = (
            "Generated from dev-agent-kit canonical role and skill sources.\n"
            "Read the target project's AGENTS.md and applicable instructions.\n"
            f"Choose the relevant skill(s) for the assignment from: {paths}.\n"
            "Return a result matching the skill's references/result-contract.json.\n"
            "Use the real task ID supplied by the caller; missing essential context is needs_input.\n\n"
            + instructions
        )
        for provider in providers:
            for relative, content in selected_renderers[provider](role, prompt).items():
                if relative in files:
                    raise ProfileError(f"Provider renderer path collision: {relative}")
                if not isinstance(content, bytes):
                    raise ProfileError(f"Provider renderer must return bytes: {relative}")
                files[relative] = content
        for name in role["skills"]:
            directory = confined_path(source, f".agents/skills/{name}")
            for path in sorted(directory.rglob("*")):
                if path.is_symlink():
                    raise ProfileError(f"Symlink in source skill: {path}")
                if not path.is_file():
                    continue
                relative = path.relative_to(directory).as_posix()
                output = f".agents/skills/{name}/{relative}"
                if output in files and files[output] != path.read_bytes():
                    raise ProfileError(f"Provider renderer path collision: {output}")
                files[f".agents/skills/{name}/{relative}"] = path.read_bytes()
                if "claude" in providers:
                    output = f".claude/skills/{name}/{relative}"
                    if output in files and files[output] != path.read_bytes():
                        raise ProfileError(f"Provider renderer path collision: {output}")
                    files[output] = path.read_bytes()
    return files


def digest(content: bytes) -> str:
    """Return the content fingerprint used to preserve target edits."""
    return hashlib.sha256(content).hexdigest()


def sync_result_contracts(source: Path) -> int:
    """Refresh portable schema and policy copies from their canonical sources."""
    source = source.resolve()
    catalog = json.loads(confined_path(source, "agents/catalog.json").read_text())
    contract = confined_path(source, "contracts/agent-result.schema.json").read_bytes()
    schema = json.loads(contract)
    defaults = confined_path(source, "policies/project-defaults.json").read_bytes()
    json.loads(defaults)
    roles = catalog["roles"]
    if any(
        not re.fullmatch(schema["properties"]["role_id"]["pattern"], role["id"]) for role in roles
    ):
        raise ProfileError("Result contract role ID pattern does not cover the catalog")
    targets = {}
    skills = set()
    for role in roles:
        for name in role["skills"]:
            if not isinstance(name, str) or not NAME.fullmatch(name):
                raise ProfileError("Invalid skill reference")
            skill_metadata(confined_path(source, f".agents/skills/{name}/SKILL.md"))
            skills.add(name)
            targets[
                confined_path(source, f".agents/skills/{name}/references/result-contract.json")
            ] = contract
            targets[
                confined_path(source, f".agents/skills/{name}/references/project-defaults.json")
            ] = defaults
            directory = confined_path(source, f".agents/skills/{name}/references")
            for resource in directory.glob("*.schema.json"):
                bundled = confined_path(source, resource.relative_to(source).as_posix())
                targets[bundled] = confined_path(source, f"contracts/{resource.name}").read_bytes()
    for path, content in targets.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    return len(skills)


def export_profiles(
    source: Path,
    target: Path,
    providers: tuple[str, ...] = PROVIDERS,
    check: bool = False,
    *,
    renderers: Mapping[str, Renderer] | None = None,
) -> int:
    """Write or check profiles, refusing to overwrite unrelated or locally edited files."""
    source, target = source.resolve(), target.resolve()
    files = render_profiles(source, providers, renderers=renderers)
    manifest_path = confined_path(target, MANIFEST)
    owned = {}
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())
        if manifest.get("schema_version") != 1 or not isinstance(manifest.get("files"), dict):
            raise ProfileError("Invalid generated-file ownership manifest")
        owned = manifest["files"]
    changes = []
    conflicts = []
    for relative, content in files.items():
        path = confined_path(target, relative)
        if path.exists() and not path.is_file():
            conflicts.append(relative)
        elif path.exists():
            current = path.read_bytes()
            if current != content:
                if owned.get(relative) != digest(current):
                    conflicts.append(relative)
                changes.append(relative)
        else:
            changes.append(relative)
    if conflicts:
        raise ProfileError(
            "Refusing to overwrite unrelated or edited files: " + ", ".join(conflicts)
        )
    if check:
        if changes:
            raise ProfileError("Missing or outdated generated profiles: " + ", ".join(changes))
        return len(files)
    target.mkdir(parents=True, exist_ok=True)
    for relative in changes:
        path = confined_path(target, relative)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(files[relative])
    owned.update({relative: digest(content) for relative, content in files.items()})
    manifest_path.write_text(
        json.dumps({"schema_version": 1, "files": owned}, indent=2, sort_keys=True) + "\n"
    )
    return len(files)


def main() -> int:
    """Run the local profile packager without contacting providers."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--target", type=Path, default=Path.cwd())
    parser.add_argument("--provider", choices=(*PROVIDERS, "all"), default="all")
    parser.add_argument("--check", action="store_true", help="Validate without writing files")
    parser.add_argument(
        "--sync-resources",
        "--sync-contracts",
        dest="sync_resources",
        action="store_true",
        help="Refresh bundled result schemas and project defaults before export",
    )
    args = parser.parse_args()
    selected = PROVIDERS if args.provider == "all" else (args.provider,)
    try:
        if args.sync_resources and args.check:
            raise ProfileError("--check cannot be combined with --sync-resources")
        if args.sync_resources:
            sync_result_contracts(args.source)
        count = export_profiles(args.source, args.target, selected, args.check)
    except (ProfileError, OSError, ValueError, KeyError, TypeError) as error:
        print(f"Profile packaging failed: {error}", file=sys.stderr)
        return 1
    print(f"{'Checked' if args.check else 'Packaged'} {count} files for {', '.join(selected)}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
