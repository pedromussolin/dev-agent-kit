# dev-agent-kit

**Languages:** English | [Português (Brasil)](docs/pt-br/README.md)

Development rules and architecture for a project-aware, agent-driven SDLC.
Projects may use Python, Go, JavaScript/TypeScript or other languages according
to their requirements and existing tooling.

## Current capabilities

- Modular [rules](rules/INDEX.md) routed through [AGENTS.md](AGENTS.md).
- Stack selection and idiomatic conventions in [rule 012](rules/012-polyglot-project-standards.md).
- Agent workflow contracts and quality gates in [rule 013](rules/013-agent-sdlc-workflow.md).
- Templates for [tasks](templates/sdlc-task.md), [agent roles](templates/agent-role.md), [reviews](templates/pr-review.md) and [new rules](templates/new-rule.md).
- Twenty-six canonical agent roles and twenty-eight portable skills covering product, engineering, design, security, cloud, DevOps, databases, quality, operations, AI strategy/engineering/evaluations and data engineering.
- Generated native profiles for Codex, Claude Code and GitHub Copilot, plus a Python standard-library packager and local/CI validation.
- A local Python executor with SQLite state, isolated Git worktrees, bounded Codex calls, component checks, QA and technical review before configurable diff/PR/merge/deploy delivery, with live monitoring and persistent token/tool/loop controls.

## Agents and skills

Read the [agents and skills guide](docs/en/agents-and-skills.md) for the full roster,
provider formats, examples and the reasons behind the organization.

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e .
python3 scripts/provider_profiles.py --check
python3 -m unittest discover -s tests -v
```

## Run a task

The [executor guide](docs/en/local-executor.md) covers task configuration and
`validate`, `run`, `status` and `resume`. The first adapter uses your existing Codex
ChatGPT authentication. It does not provision API keys. AI usage has a separate
budget; call, time and context limits do not constitute a monetary billing cap.

```bash
python3 -m dev_agent_kit validate examples/execution/executor-runbook-validation.json
```

That task record is specific to this checkout and revision. Prepare a real task
for your repository before running it; the executor delivers an isolated diff/report.
The [first real evaluation](docs/en/agent-validation.md) records the accepted
three-role task, earlier failures and measured usage. Context optimization and
code-change scenarios still need their own comparisons.

## Local platform, data and AI

The [platform guide](docs/en/local-platform-and-ai.md) describes staged local tools,
a BRL 100/month infrastructure cap and separate AI budgeting. All roles/skills carry
these defaults. See the [executor decision](docs/en/executor-decision.md) for the
Python CLI, SQLite state and boundaries of the first working increment.

## Modular planning and growth

Read [modular architecture](docs/en/modular-platform.md), [planning governance](docs/en/planning-governance.md)
and [provider readiness](docs/en/provider-readiness.md) for replaceable integrations,
bounded decision sessions and the path from personal use to a commercial product.
Planning/extension skills and schemas are available; autonomous sessions and a
manifest-based plugin loader remain pending.

## Architecture proposal

Read the [architecture](docs/en/architecture.md) for the separation between the
orchestrator, agents, language adapters and delivery adapters. The document
includes contracts, failure recovery, an implementation roadmap and open decisions.

The role profiles, skills, packager, kit-validation workflow and initial local
executor are implemented. All 26 roles can be selected in bounded sequential task workflows. Native client
discovery, autonomous product scheduling and plugin loading require further
increments. Delivery adapters and shared Actions workflows are implemented and
activated for the private finance-management product on two local runners. The
real developer → checks → QA → review → PR → CI → merge → Docker delivery passed.
See the measured [product evaluation](evaluations/finance-management-delivery.json) and
[delivery and Actions](docs/en/delivery-and-actions.md).
Provider format validation alone does not establish agent quality.
