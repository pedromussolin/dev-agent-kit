# Agent instructions

Read `rules/INDEX.md` first, then load the rules applicable to the task.
`rules/003-language-standards.md` applies to code, logs, commits and documentation.
The canonical rule directory is `rules/`.

## Project context

- Inspect manifests, lockfiles, existing tooling and project instructions before choosing tools.
- Follow `rules/012-polyglot-project-standards.md` when selecting or changing a stack.
- Node.js, React, Tailwind and Zod apply to matching stacks; they are not universal requirements.
- Preserve language conventions, including Go package tests beside their source.
- The local executor implements bounded task execution with configurable PR, merge and deploy stages; advanced orchestration in `docs/en/architecture.md` remains a proposal.
- Follow `rules/013-agent-sdlc-workflow.md` when designing or implementing automation.
- Follow `rules/014-agent-skills-provider-standards.md` when editing agents, skills or provider profiles.
- Follow `rules/015-local-data-ai-policy.md` for local hosting, infrastructure budget, data and AI decisions.
- Follow `rules/017-quality-data-api-contracts.md` for code quality gates, data/query boundaries and application MCP parity.
- Follow `rules/016-modularity-planning-governance.md` for extension boundaries, planning and provider readiness.
- Agent and skill sources are in `agents/` and `.agents/skills/`; native provider profiles are generated.
- After shared schema/policy changes, run `python3 scripts/provider_profiles.py --sync-resources --target .`.
- After source changes, run `python3 scripts/provider_profiles.py --target .`, then `--check` and `python3 -m unittest discover -s tests -v`.

## Delivery

- Follow `rules/001-git-workflow.md`. Discover the default branch instead of assuming `master`.
- Development branches and commits require an actual task/issue ID; never invent one.
- Never merge `sandbox` or `staging` into a development branch.
- Missing commands, evidence, tools or failed checks must block completion.
- Report completed stages and outstanding integrations accurately.
- Provide public documentation in English and Portuguese as specified in rule `003`.
