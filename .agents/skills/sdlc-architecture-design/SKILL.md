---
name: sdlc-architecture-design
description: "Design system boundaries, interfaces and architectural tradeoffs when features cross modules or change system structure."
---

# Software Architect workflow

## Inputs and scope

Product scope, quality requirements, existing architecture and technology decisions.

Read the target project's applicable instructions and tooling. Use only the task's
scope and existing authorization. Essential missing inputs block dependent work.
If installed outside dev-agent-kit, use the target project's conventions; this skill
does not require the kit's rule directory or additional skills.

## Local platform, data and AI policy

Read the skill's bundled [project defaults](references/project-defaults.json).
Start locally. Optional cloud infrastructure has a BRL 100/month cap, including
compute, databases, telemetry, storage, backups, network and currency/tax fees.
AI has a separate budget; an unset amount means unspecified, not unlimited.
Use maintained stable tools that fit the project; activate services only as needed.
Apply explicit data contracts, quality/provenance/privacy checks and measured AI
quality/cost with bounded context and attempts where relevant. Preserve explicit
user overrides and target-project instructions; record effective constraints.
The local executor enforces scoped execution/observed-token limits; provider billing and cloud spending are not runtime-enforced by these instructions.

Define schema ownership, AI boundaries and deterministic fallback; keep optional infrastructure modular.

## Procedure

1. Map existing boundaries and the quality attributes affected by the task.
2. Compare the smallest coherent designs before adding services or infrastructure.
3. Specify interfaces, data ownership, failure behavior and compatibility boundaries.
4. Request relevant security, database, cloud and UX input rather than deciding outside the supplied constraints.
5. Record decisions and a testable migration plan with unresolved assumptions.

## Output and acceptance

Produce: Architecture decision records, interface contracts, failure paths and migration approach.

Completion gate: The design connects requirements to interfaces, tradeoffs, failure behavior and verification.

Use the [result contract](references/result-contract.json) when returning a
machine-readable result. A `completed` result describes this role's assignment,
not the whole SDLC. Record actual artifact/evidence references and essential open
questions. Missing tools or unexecuted checks cannot be reported as passed.

Hand off to: Software Engineer, Developer and relevant specialists.
