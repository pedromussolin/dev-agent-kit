# Project guidance

This kit contains canonical SDLC role/skill instructions and a Python 3.11+
standard-library profile packager. Read `AGENTS.md` and `rules/INDEX.md`, then only
the applicable rules. Keep code and internal artifacts in English; public docs
have English and Portuguese counterparts.

Edit `agents/`, `.agents/skills/`, `contracts/` and `policies/` as canonical sources.
Provider profiles and Claude skill copies are generated. After shared resource
changes run `python3 scripts/provider_profiles.py --sync-resources --target .`.
Then run `python3 scripts/provider_profiles.py --check` and
`python3 -m unittest discover -s tests -v`.

Preserve the target project's languages and existing tools. Planning, plugins and
the persistent SDLC runtime have the implementation status recorded in the docs;
file validation alone does not establish autonomous execution.
