"""Verify bounded metadata discovery and explicit, nonexecuting suggestions."""

import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from dev_agent_kit.cli import main
from dev_agent_kit.stacks import detect_components


class StackDiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)

    def write(self, filename, content):
        (self.root / filename).write_text(content, encoding='utf-8')

    def test_empty_root_and_nested_manifests_are_ignored(self):
        self.assertEqual(detect_components(self.root), [])
        nested = self.root / 'nested'
        nested.mkdir()
        (nested / 'package.json').write_text('invalid', encoding='utf-8')
        self.assertEqual(detect_components(self.root), [])

    def test_mixed_languages_are_independent_and_discovery_has_no_side_effects(self):
        self.write('pyproject.toml', '[project]\nname="fixture"\n')
        self.write('requirements.txt', '# Dependencies are not resolved\n')
        self.write('go.mod', 'module example.invalid/fixture\n\ngo 1.22\n')
        self.write('package.json', json.dumps({'name': 'fixture', 'scripts': {
            'test': 'touch should-not-exist', 'build': 'build', 'start': 'start'}}))
        self.write('package-lock.json', '{}')
        self.write('Cargo.toml', '[package]\nname="fixture"\nversion="0.1.0"\n')
        before = {path.name: path.read_bytes() for path in self.root.iterdir()}

        components = detect_components(self.root)

        by_language = {component['language']: component for component in components}
        self.assertEqual(set(by_language), {'python', 'go', 'javascript', 'rust'})
        self.assertEqual(by_language['python']['manifests'], ['pyproject.toml', 'requirements.txt'])
        self.assertEqual(by_language['python']['suggested_checks'], [])
        self.assertEqual(by_language['go']['suggested_checks'][0]['argv'], ['go', 'test', './...'])
        self.assertEqual(by_language['rust']['suggested_checks'][0]['argv'], ['cargo', 'test'])
        self.assertEqual([check['name'] for check in by_language['javascript']['suggested_checks']], ['test', 'build'])
        for component in components:
            self.assertEqual(component['working_directory'], '.')
            self.assertTrue(component['name'])
            for check in component['suggested_checks']:
                self.assertIsInstance(check['argv'], list)
                self.assertTrue(check['argv'])
                self.assertGreater(check['timeout_seconds'], 0)
        self.assertEqual({path.name: path.read_bytes() for path in self.root.iterdir()}, before)

    def test_package_manager_selection_and_script_filtering(self):
        self.write('package.json', json.dumps({'scripts': {
            'test': 'test', 'lint': 'lint', 'build': 'build', 'typecheck': 'types',
            'start': 'start', 'test:unit': 'unit'}}))
        cases = [(None, 'npm'), ('package-lock.json', 'npm'), ('npm-shrinkwrap.json', 'npm'),
                 ('pnpm-lock.yaml', 'pnpm'), ('yarn.lock', 'yarn'),
                 ('bun.lock', 'bun'), ('bun.lockb', 'bun')]
        for filename, manager in cases:
            with self.subTest(lockfile=filename):
                if filename:
                    self.write(filename, '')
                checks = detect_components(self.root)[0]['suggested_checks']
                self.assertEqual([check['name'] for check in checks], ['test', 'lint', 'build', 'typecheck'])
                self.assertEqual([check['argv'] for check in checks],
                                 [[manager, 'run', name] for name in ('test', 'lint', 'build', 'typecheck')])
                if filename:
                    (self.root / filename).unlink()

    def test_missing_or_empty_scripts_do_not_invent_checks(self):
        for metadata in ({}, {'scripts': {}}, {'scripts': {'test': ' ', 'start': 'serve'}}):
            with self.subTest(metadata=metadata):
                self.write('package.json', json.dumps(metadata))
                self.assertEqual(detect_components(self.root)[0]['suggested_checks'], [])

    def test_conflicting_managers_have_visible_diagnostic(self):
        self.write('package.json', '{}')
        self.write('yarn.lock', '')
        self.write('pnpm-lock.yaml', '')
        with self.assertRaisesRegex(ValueError, 'package.json: conflicting'):
            detect_components(self.root)

    def test_python_uses_existing_test_signals(self):
        self.write('requirements.txt', '')
        self.assertEqual(detect_components(self.root)[0]['suggested_checks'], [])
        (self.root / 'tests').mkdir()
        self.assertEqual(detect_components(self.root)[0]['suggested_checks'][0]['argv'],
                         ['python', '-m', 'unittest', 'discover', '-s', 'tests', '-v'])
        self.write('pyproject.toml', '[tool.pytest.ini_options]\naddopts="-q"\n')
        self.assertEqual(detect_components(self.root)[0]['suggested_checks'][0]['argv'], ['python', '-m', 'pytest'])

    def test_rust_workspace_and_quoted_go_module(self):
        self.write('Cargo.toml', '[workspace]\nmembers=[]\n')
        self.write('go.mod', '// comment\nmodule "example.invalid/fixture" // comment\n')
        components = detect_components(self.root)
        self.assertEqual(components[0]['name'], 'example.invalid/fixture')
        self.assertEqual(components[1]['language'], 'rust')

    def test_invalid_manifests_are_not_silently_ignored(self):
        cases = [('package.json', '{'), ('package.json', '[]'),
                 ('package.json', '{"scripts": []}'), ('package.json', '{"scripts":{"test":42}}'),
                 ('package.json', '{"name":null}'), ('pyproject.toml', '[project'),
                 ('pyproject.toml', 'project = []'), ('pyproject.toml', '[tool]\npytest=[]'),
                 ('Cargo.toml', '[package'), ('Cargo.toml', ''), ('Cargo.toml', 'package=[]'),
                 ('go.mod', ''), ('go.mod', 'go 1.22\n'),
                 ('go.mod', 'module first\nmodule second\n')]
        for filename, content in cases:
            with self.subTest(filename=filename, content=content):
                self.write(filename, content)
                with self.assertRaises(ValueError) as caught:
                    detect_components(self.root)
                self.assertIn(filename, str(caught.exception))
                (self.root / filename).unlink()

    def test_invalid_root_and_unreadable_metadata_are_visible(self):
        with self.assertRaisesRegex(ValueError, 'Repository directory'):
            detect_components(self.root / 'missing')
        self.write('file', '')
        with self.assertRaisesRegex(ValueError, 'Repository directory'):
            detect_components(self.root / 'file')
        (self.root / 'package.json').mkdir()
        with self.assertRaisesRegex(ValueError, 'package.json: expected a regular'):
            detect_components(self.root)
        (self.root / 'package.json').rmdir()
        (self.root / 'requirements.txt').write_bytes(b'\xff')
        with self.assertRaisesRegex(ValueError, 'requirements.txt: cannot read'):
            detect_components(self.root)

    def test_symlinked_manifests_and_lockfiles_are_rejected(self):
        (self.root / 'pyproject.toml').symlink_to(self.root / 'missing')
        with self.assertRaisesRegex(ValueError, 'pyproject.toml: symlinked'):
            detect_components(self.root)
        (self.root / 'pyproject.toml').unlink()
        self.write('package.json', '{}')
        (self.root / 'yarn.lock').symlink_to(self.root / 'missing')
        with self.assertRaisesRegex(ValueError, 'yarn.lock: symlinked'):
            detect_components(self.root)

    def test_oversized_manifest_is_bounded(self):
        self.write('requirements.txt', '#' * (1024 * 1024 + 1))
        with self.assertRaisesRegex(ValueError, 'requirements.txt:.*limit'):
            detect_components(self.root)

    def test_inspect_cli_reports_invalid_manifest_as_failure(self):
        self.write('package.json', '{')
        output = io.StringIO()
        with patch('sys.argv', ['dev-agent-kit', 'inspect', str(self.root)]), contextlib.redirect_stderr(output):
            result = main()
        self.assertEqual(result, 1)
        diagnostic = json.loads(output.getvalue())
        self.assertEqual(diagnostic['status'], 'failed')
        self.assertIn('package.json', diagnostic['message'])
