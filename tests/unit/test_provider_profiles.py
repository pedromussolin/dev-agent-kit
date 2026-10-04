"""Verify portable exports, project preservation and target confinement."""

import importlib.util
import json
import shutil
import tempfile
import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "provider_profiles", ROOT / "scripts/provider_profiles.py"
)
profiles = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(profiles)


class ProviderProfileTests(unittest.TestCase):
    """Exercise exports in isolated directories without calling an AI provider."""

    def _copy_sources(self, target):
        for name in ("agents", "contracts", "policies", ".agents"):
            shutil.copytree(ROOT / name, target / name)

    def test_owned_profiles_can_follow_canonical_changes(self):
        """Regenerate owned files while preserving unrelated project instructions."""
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source"
            target = Path(directory) / "target"
            self._copy_sources(source)
            profiles.export_profiles(source, target)
            instructions = target / "AGENTS.md"
            instructions.write_text("Existing project instructions")
            role = source / "agents/developer.md"
            role.write_text(role.read_text() + "\nAdditional canonical requirement.\n")
            profiles.export_profiles(source, target)
            native = tomllib.loads((target / ".codex/agents/developer.toml").read_text())
            self.assertIn("Additional canonical requirement.", native["developer_instructions"])
            self.assertEqual(instructions.read_text(), "Existing project instructions")
            profiles.export_profiles(source, target, check=True)

    def test_contract_updates_are_bundled_from_one_source(self):
        """Detect stale schemas and refresh every portable copy before export."""
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source"
            self._copy_sources(source)
            canonical = source / "contracts/agent-result.schema.json"
            schema = json.loads(canonical.read_text())
            schema["description"] = "Updated shared contract"
            canonical.write_text(json.dumps(schema, indent=2) + "\n")
            with self.assertRaises(profiles.ProfileError):
                profiles.load_catalog(source)
            count = profiles.sync_result_contracts(source)
            roles = profiles.load_catalog(source)
            self.assertEqual(count, len({name for role in roles for name in role["skills"]}))
            for path in (source / ".agents/skills").glob("*/references/result-contract.json"):
                self.assertEqual(path.read_bytes(), canonical.read_bytes())

    def test_export_is_portable_and_idempotent(self):
        """Package all roles and support an independent checkout of generated files."""
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            count = profiles.export_profiles(ROOT, target)
            self.assertGreater(count, 0)
            for role in profiles.load_catalog(ROOT):
                data = tomllib.loads((target / f".codex/agents/{role['id']}.toml").read_text())
                self.assertEqual(data["name"], role["id"])
                self.assertNotIn("model", data)
                self.assertNotIn("model_reasoning_effort", data)
                for skill in role["skills"]:
                    canonical = target / f".agents/skills/{skill}"
                    claude = target / f".claude/skills/{skill}"
                    self.assertEqual(
                        (canonical / "SKILL.md").read_bytes(), (claude / "SKILL.md").read_bytes()
                    )
                    self.assertTrue((canonical / "references/result-contract.json").is_file())
                    for directory in (canonical, claude):
                        self.assertEqual(
                            (directory / "references/project-defaults.json").read_bytes(),
                            (ROOT / "policies/project-defaults.json").read_bytes(),
                        )
                self.assertTrue((target / f".github/agents/{role['id']}.agent.md").is_file())
            first = {
                path.relative_to(target): path.read_bytes()
                for path in target.rglob("*")
                if path.is_file()
            }
            profiles.export_profiles(ROOT, target)
            second = {
                path.relative_to(target): path.read_bytes()
                for path in target.rglob("*")
                if path.is_file()
            }
            self.assertEqual(first, second)
            self.assertEqual(profiles.export_profiles(ROOT, target, check=True), count)

    def test_conflict_preflight_preserves_existing_project(self):
        """Reject a conflicting profile before writing any other generated file."""
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            existing = target / ".github/agents/developer.agent.md"
            existing.parent.mkdir(parents=True)
            existing.write_text("Existing project customization")
            with self.assertRaises(profiles.ProfileError):
                profiles.export_profiles(ROOT, target)
            self.assertEqual(existing.read_text(), "Existing project customization")
            self.assertFalse((target / ".codex").exists())
            self.assertFalse((target / profiles.MANIFEST).exists())

    def test_local_generated_edits_are_preserved(self):
        """Ownership of a file must not permit clobbering subsequent local edits."""
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            profiles.export_profiles(ROOT, target)
            edited = target / ".claude/agents/qa-engineer.md"
            edited.write_text(edited.read_text() + "\nProject-specific local change\n")
            content = edited.read_bytes()
            with self.assertRaises(profiles.ProfileError):
                profiles.export_profiles(ROOT, target)
            self.assertEqual(edited.read_bytes(), content)

    def test_symlinked_target_directory_cannot_escape_workspace(self):
        """Reject provider paths redirected into another directory."""
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "target"
            outside = Path(directory) / "outside"
            target.mkdir()
            outside.mkdir()
            (target / ".codex").symlink_to(outside, target_is_directory=True)
            with self.assertRaises(profiles.ProfileError):
                profiles.export_profiles(ROOT, target)
            self.assertEqual(list(outside.iterdir()), [])

    def test_check_does_not_create_missing_files(self):
        """Report incomplete exports without modifying the target."""
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "missing"
            with self.assertRaises(profiles.ProfileError):
                profiles.export_profiles(ROOT, target, check=True)
            self.assertFalse(target.exists())

    def test_provider_selection_has_no_unrelated_profile_directories(self):
        """A Codex-only export leaves other providers unconfigured."""
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            profiles.export_profiles(ROOT, target, ("codex",))
            self.assertTrue((target / ".codex/agents").is_dir())
            self.assertFalse((target / ".claude").exists())
            self.assertFalse((target / ".github").exists())

    def test_invalid_catalog_reference_is_rejected(self):
        """Prevent a role instruction path from reading outside canonical sources."""
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory)
            self._copy_sources(source)
            catalog = json.loads((ROOT / "agents/catalog.json").read_text())
            catalog["roles"][0]["instructions"] = "../outside.md"
            (source / "agents/catalog.json").write_text(json.dumps(catalog))
            (source / "contracts/agent-result.schema.json").write_bytes(
                (ROOT / "contracts/agent-result.schema.json").read_bytes()
            )
            with self.assertRaises(profiles.ProfileError):
                profiles.load_catalog(source)

    def test_policy_drift_is_detected_and_updates_owned_exports(self):
        """Keep independent skill bundles consistent with a changed project policy."""
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source"
            target = Path(directory) / "target"
            self._copy_sources(source)
            profiles.export_profiles(source, target)
            canonical = source / "policies/project-defaults.json"
            policy = json.loads(canonical.read_text())
            policy["recommended_profiles"]["optional_traces"] = []
            canonical.write_text(json.dumps(policy, indent=2) + "\n")
            with self.assertRaisesRegex(profiles.ProfileError, "Stale bundled project defaults"):
                profiles.load_catalog(source)
            profiles.sync_result_contracts(source)
            profiles.export_profiles(source, target)
            profiles.export_profiles(source, target, check=True)
            for path in target.glob(".*/skills/*/references/project-defaults.json"):
                self.assertEqual(path.read_bytes(), canonical.read_bytes())

    def test_new_role_does_not_require_changing_the_result_contract(self):
        """Extend the registry without changing the provider-neutral output schema."""
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source"
            target = Path(directory) / "target"
            self._copy_sources(source)
            contract = (source / "contracts/agent-result.schema.json").read_bytes()
            path = source / "agents/catalog.json"
            catalog = json.loads(path.read_text())
            role = dict(next(role for role in catalog["roles"] if role["id"] == "developer"))
            role.update(id="project-specialist", title="Project Specialist")
            catalog["roles"].append(role)
            path.write_text(json.dumps(catalog))
            profiles.export_profiles(source, target)
            self.assertTrue((target / ".codex/agents/project-specialist.toml").is_file())
            self.assertEqual((source / "contracts/agent-result.schema.json").read_bytes(), contract)

    def test_injected_renderer_uses_existing_packaging_and_conflict_checks(self):
        """Use an additional renderer without editing traversal or export control."""

        def example_renderer(role, prompt):
            return {f".example/agents/{role['id']}.json": json.dumps({"prompt": prompt}).encode()}

        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            renderers = {"example": example_renderer}
            profiles.export_profiles(ROOT, target, ("example",), renderers=renderers)
            profiles.export_profiles(ROOT, target, ("example",), check=True, renderers=renderers)
            self.assertFalse((target / ".codex").exists())
            edited = target / ".example/agents/developer.json"
            edited.write_text("Existing customization")
            with self.assertRaises(profiles.ProfileError):
                profiles.export_profiles(ROOT, target, ("example",), renderers=renderers)
            self.assertEqual(edited.read_text(), "Existing customization")

    def test_renderer_path_collisions_are_rejected_before_writes(self):
        """A renderer cannot replace a canonical skill through output collisions."""

        def conflicting_renderer(role, prompt):
            return {f".agents/skills/{role['skills'][0]}/SKILL.md": b"Conflicting instructions"}

        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            with self.assertRaisesRegex(profiles.ProfileError, "path collision"):
                profiles.export_profiles(
                    ROOT, target, ("example",), renderers={"example": conflicting_renderer}
                )
            self.assertEqual(list(target.iterdir()), [])

    def test_specialized_contracts_are_synchronized_and_exported(self):
        """Preserve standalone planning skills after their artifact contract changes."""
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source"
            target = Path(directory) / "target"
            self._copy_sources(source)
            path = source / "contracts/planning-session.schema.json"
            schema = json.loads(path.read_text())
            schema["description"] = "Updated planning result contract"
            path.write_text(json.dumps(schema, indent=2) + "\n")
            with self.assertRaisesRegex(profiles.ProfileError, "Stale bundled planning-session"):
                profiles.load_catalog(source)
            profiles.sync_result_contracts(source)
            profiles.export_profiles(source, target)
            for base in (".agents", ".claude"):
                copy = (
                    target
                    / base
                    / "skills/sdlc-planning-session/references/planning-session.schema.json"
                )
                self.assertEqual(copy.read_bytes(), path.read_bytes())


if __name__ == "__main__":
    unittest.main()
