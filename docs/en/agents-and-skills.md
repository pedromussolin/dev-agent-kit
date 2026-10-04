# Agents, skills and provider profiles

**Languages:** English | [Português (Brasil)](../pt-br/agents-and-skills.md)

Provider formats checked on 2026-10-03. Profiles, packaging and the initial local
persistent executor are implemented. Broader SDLC workflows remain planned.

## Understand the layers

| Layer | Purpose | Example |
| --- | --- | --- |
| Project instructions | Establish the target project's conventions | `AGENTS.md`, `CLAUDE.md`, applicable rules |
| Agent role | Own a responsibility and produce a defined result | QA Engineer owns acceptance assessment |
| Skill | Describe a focused procedure, with optional supporting files | Plan and perform acceptance testing |
| Provider profile | Express that role in a particular client's native configuration | Claude subagent Markdown or Codex TOML |
| Tools/integrations | Supply actual capabilities and authenticated access | Test runner, browser, cloud API or MCP server |
| Orchestrator | Schedule work, persist state and validate stage transitions | Retry implementation after a verified QA failure |

A skill is instructions the client can load. Loading it does not start a background
worker, install tools, authenticate a cloud account or create a persistent pipeline.
A model is the reasoning engine; Codex, Claude Code and Copilot are clients that
interpret these files and expose their own execution features.

## Current roster

All 29 roles have canonical instructions and at least one focused skill. There are 31 skills:

| Role | Main responsibility | Skill |
| --- | --- | --- |
| Product Manager | Problem discovery and product outcomes | `sdlc-product-discovery` |
| Product Owner | Backlog priorities and acceptance | `sdlc-backlog-refinement` |
| Delivery Planner | Work breakdown and dependencies | `sdlc-delivery-planning` |
| Technology Strategist | Evidence-based stack and technology choices | `sdlc-technology-evaluation` |
| Software Architect | System structure and interfaces | `sdlc-architecture-design` |
| Software Engineer | Feasibility and implementable technical contracts | `sdlc-engineering-design` |
| Developer | Scoped code changes and regression tests | `sdlc-implementation` |
| QA Engineer | Early test strategy and acceptance assessment | `sdlc-quality-assurance` |
| Cybersecurity Engineer | Threat modeling and security findings | `sdlc-security-assessment` |
| Cloud Architect | Hosting, identity, networks, resilience and cost assumptions | `sdlc-cloud-design` |
| DevOps Engineer | CI/CD and infrastructure automation | `sdlc-devops-automation` |
| Database Administrator | Schemas, migrations, queries and recovery | `sdlc-database-engineering` |
| UX Designer | User journeys and interaction behavior | `sdlc-user-experience` |
| UI Designer | Screens, states and design-system handoff | `sdlc-interface-design` |
| Accessibility Specialist | Accessible interaction and test coverage | `sdlc-accessibility-review` |
| Technical Reviewer | Independent review of the current diff | `sdlc-code-review` |
| Release Manager | Revision-specific readiness and authorized delivery | `sdlc-release-readiness` |
| Site Reliability Engineer | Telemetry, incidents and service recovery | `sdlc-reliability-operations` |
| Technical Writer | Accurate documentation and onboarding | `sdlc-technical-documentation` |
| SDLC Coordinator | Role selection, handoffs and evidence ledger | `sdlc-task-coordination` |
| AI Strategist | AI roadmap, baseline and investment criteria | `sdlc-ai-strategy` |
| AI Engineer | Evaluated model, tool and retrieval integrations | `sdlc-ai-engineering` |
| Context Engineer | Context/prompt optimization with measured quality and cost | `sdlc-context-engineering` |
| Data Engineer | Data flows, contracts, quality and provenance | `sdlc-data-engineering` |
| LLM Evaluation Engineer | Reproducible quality, safety and cost regression gates | `sdlc-llm-evaluation` |
| MLOps Engineer | AI versions, delivery, monitoring and recovery | `sdlc-mlops` |

Security, QA, accessibility and database expertise can contribute before development.
They also review changes relevant to their boundaries. A cloud architect designs
the topology; DevOps prepares automation; SRE examines its operational behavior.
UX specifies the journey and interaction; UI specifies the screens and visual states.

The roster is available, but a task uses its relevant roles. A query optimization
can use DBA, developer, QA and reviewer; a new product flow can also involve PM,
PO, UX, UI and architecture. Creating all roles does not require activating them
all, and combining responsibilities does not remove acceptance evidence.

## Repository organization

```text
agents/
  catalog.json                     Role registry
  software-architect.md            Canonical role instructions
policies/
  project-defaults.json             Canonical local/data/AI defaults
contracts/
  agent-result.schema.json         Canonical output contract
.agents/skills/
  sdlc-architecture-design/
    SKILL.md                       Portable procedure
    references/result-contract.json  Generated portable schema copy
    references/project-defaults.json Generated portable policy copy
    agents/openai.yaml             Optional Codex skill UI metadata
.codex/agents/*.toml                Generated Codex profiles
.claude/agents/*.md                 Generated Claude Code profiles
.claude/skills/*/                   Generated copies for Claude discovery
.github/agents/*.agent.md           Generated Copilot profiles
scripts/provider_profiles.py       Local validation and packaging
.dev-agent-kit-profiles.json        Generated-file ownership fingerprints
```

Only the registry, role Markdown, canonical skills, root schema and project-default policy are maintained
as sources. Provider profiles and Claude skill copies are reproducible outputs.
Portable schema copies let a skill travel without depending on this repository's
directory layout; `--sync-resources` refreshes them from their canonical sources. The older `--sync-contracts` spelling remains an alias.

Instructions use the target project's rules and toolchain. Installing these skills
does not impose the kit's Git flow, Tailwind, Node.js or database tooling on another
project. Project-specific constraints belong in that project's instructions.

## What goes inside SKILL.md

The portable core uses YAML frontmatter with `name` and `description`, followed by
Markdown. A directory name matches the skill name. Supporting files are optional.
These conventions follow the [Agent Skills specification](https://agentskills.io/specification).

An abbreviated example:

```markdown
---
name: sdlc-architecture-design
description: Design boundaries and interfaces when a change affects system structure.
---

# Architecture design

Read the target project's requirements and existing architecture.
Compare coherent alternatives and record interfaces, tradeoffs and failure behavior.
Return a design decision with evidence and unresolved questions.
```

The actual [architecture skill](../../.agents/skills/sdlc-architecture-design/SKILL.md)
adds inputs, workflow, output contract, completion gate and handoff. Descriptions
explain when a capability applies; they are not generic biographies. Detailed
instructions load only when needed, reducing irrelevant context.

`agents/openai.yaml` inside a skill describes that skill's Codex UI. It is separate
from `.codex/agents/*.toml`, which defines custom agents. One role can eventually
use several skills, and a skill can serve several roles; the registry already
supports a list of skills per role.

## Native provider formats

| Client | Project skills | Custom agent files |
| --- | --- | --- |
| Codex | `.agents/skills/NAME/SKILL.md` | `.codex/agents/NAME.toml` |
| Claude Code | `.claude/skills/NAME/SKILL.md` | `.claude/agents/NAME.md` |
| GitHub Copilot | `.agents/skills/NAME/SKILL.md` supported; other documented locations also exist | `.github/agents/NAME.agent.md` |

Codex standalone profiles use `name`, `description` and `developer_instructions`;
the generated profiles additionally set the intended sandbox. Models and reasoning
settings inherit rather than being pinned. See official OpenAI documentation for
[skills](https://learn.chatgpt.com/docs/build-skills) and
[custom agents](https://learn.chatgpt.com/docs/agent-configuration/subagents).

Claude profiles have YAML frontmatter and Markdown instructions. Their `skills`
list preloads the selected capabilities; `tools` limits the available tool set.
See Anthropic's documentation for [skills](https://code.claude.com/docs/en/skills)
and [subagents](https://code.claude.com/docs/en/sub-agents).

Copilot profiles use YAML frontmatter and Markdown with documented tool aliases.
The prompt explicitly loads the canonical skills and project instructions. Tool
availability and customization support vary by surface; verify the installed
client and environment. See GitHub's documentation for
[skills](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills)
and [agent configuration](https://docs.github.com/en/copilot/reference/custom-agents-configuration).

Portable workflow instructions are shared; provider-specific permissions, UI and
runtime behavior remain native. The exporter does not modify global settings,
credentials, model choices or MCP connections. Shell access can execute more than
tests; runtime policy must enforce the task's permitted actions. Textual boundaries
are not a replacement for a sandbox or scoped credentials.

## Use and maintain the kit

From the kit checkout, validate the generated files and run local tests:

```bash
python3 scripts/provider_profiles.py --check
python3 -m unittest discover -s tests -v
```

After editing canonical roles or skills:

```bash
python3 scripts/provider_profiles.py --target .
```

After editing the shared output schema or project-default policy:

```bash
python3 scripts/provider_profiles.py --sync-resources --target .
```

To package into another existing project, specify its actual path. This example
uses a sample path; replace it before running:

```bash
python3 scripts/provider_profiles.py --provider codex --target /path/to/project
```

Use `--provider claude`, `--provider copilot` or `--provider all` for other exports.
The exporter preflights conflicts before writing, preserves unrelated files and
refuses to overwrite locally edited generated content. Reconcile the intended
change in the canonical sources. It does not automatically delete obsolete files
when roles are removed; inspect those files before cleanup. Packaging multiple files
is not transactional against process crashes or simultaneous writers.

In a fresh Codex session rooted in the target project, a skill request can be:

```text
Use $sdlc-architecture-design to assess the module boundaries for this task.
```

To request the native agent role explicitly:

```text
Delegate this architecture assessment to the software-architect agent.
```

In Claude Code or Copilot, select the generated custom agent through the client's
agent interface and give it the task context. New profile directories may require
a fresh session. Creating files does not change this conversation's already loaded
skill catalog or prove they have been discovered by each installed client.

## Why this structure

1. **One maintained intent:** Provider variants are generated from the same role and skills.
2. **Precise discovery:** Each skill describes a recognizable job and avoids loading the entire roster's procedures.
3. **Explicit handoffs:** Roles return artifacts, evidence, blockers and questions through the same output contract.
4. **Project-aware execution:** Languages and tools follow the target project, while the specialist workflow stays reusable.
5. **Incremental autonomy:** The local executor enforces state, attempts and revision checks for developer/QA/review; specialist orchestration and release policy follow separately.

## What is validated and what remains

The kit includes local profile/source checks, packaging tests and a GitHub Actions
workflow for those checks. That CI validates the kit's files; it does not run a
product-development pipeline or call model providers.

File validation does not measure decision quality, automatic skill selection or
end-to-end execution. Evaluate those with authorized real tasks per installed
client. Useful cases include QA with absent acceptance criteria, a security review
with unverified findings, a technology decision with outdated evidence, a database
migration with recovery gaps and a release with stale check results.

The local executor supplies task input, isolated workspaces, structured output
validation, actual component checks, QA/review and bounded retries. Its delivery
is a diff/report. See the [operating guide](local-executor.md). The SDLC Coordinator
skill supplies coordination instructions; workflow transitions are implemented in code.

## Shared local, data and AI defaults

Every role and skill includes local-first guidance, the BRL 100/month infrastructure
cap and a separate, unspecified AI budget. Each skill bundles that policy for
independent installation; packaging checks it against the canonical file. Explicit
target-project/user settings take precedence and effective constraints must be
recorded. Policy instructions are not runtime spending enforcement.

See the [platform and AI guide](local-platform-and-ai.md) for tools, costs and
specialist boundaries, and the [executor decision](executor-decision.md) for current
execution boundaries. Profile files alone do not configure authenticated services.

## Planning and extension workflows

The coordinator also uses `sdlc-planning-session`; the architect also uses
`sdlc-extension-design`. These task-specific skills include specialized artifact
schemas. See [planning governance](planning-governance.md), [modular architecture](modular-platform.md)
and [provider readiness](provider-readiness.md).

New roles: Code Improver (`sdlc-code-improvement`), Code Reader (`sdlc-code-reading`) and Incident Analyst (`sdlc-incident-learning`). See [current increment](current-increment.md) for tested behavior and boundaries.
