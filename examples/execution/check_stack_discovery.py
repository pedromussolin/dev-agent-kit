"""Verify the real stack-inspection feature with harmless local fixture manifests."""

from pathlib import Path
import tempfile

from dev_agent_kit.stacks import detect_components

with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    assert detect_components(root) == []
    (root / 'pyproject.toml').write_text('[project]\nname = "fixture"\nversion = "0.1.0"\n')
    python = detect_components(root)
    assert any(component['language'] == 'python' for component in python)
    (root / 'go.mod').write_text('module example.invalid/fixture\n\ngo 1.22\n')
    (root / 'package.json').write_text('{"name":"fixture","scripts":{"test":"echo test","build":"echo build"}}')
    (root / 'package-lock.json').write_text('{}')
    (root / 'Cargo.toml').write_text('[package]\nname="fixture"\nversion="0.1.0"\n')
    components = detect_components(root)
    languages = {component['language'] for component in components}
    assert {'python', 'go', 'javascript', 'rust'}.issubset(languages), components
    for component in components:
        assert {'name', 'language', 'working_directory', 'manifests', 'suggested_checks'}.issubset(component), component
        assert component['working_directory'] == '.'
        assert all(isinstance(check['argv'], list) and check['argv'] for check in component['suggested_checks'])
    js = next(component for component in components if component['language'] == 'javascript')
    assert {'test', 'build'}.issubset({check['name'] for check in js['suggested_checks']})
    assert not (root / 'node_modules').exists()
    assert not (root / '.venv').exists()
print('Python/Go/JavaScript/Rust manifest discovery and explicit command suggestions passed without execution or installation.')
