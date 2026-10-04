---
name: sdlc-engineering-design
description: "Translate refined requirements into implementable contracts and technical feasibility before or during complex development."
---

# Software Engineer workflow

## Inputs and scope

Acceptance criteria, architecture decisions, repository code and integration constraints.

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

Design typed data and tool contracts with observable failures and explicit resource/inference limits.

## Procedure

1. Trace requirements through the actual code paths and dependent systems.
2. Identify invariants, edge cases and compatibility constraints that implementation must preserve.
3. Define data and interface contracts using the target language conventions.
4. Resolve implementation-level alternatives and surface architecture or product changes to their owners.
5. Map acceptance criteria to unit, integration or end-to-end evidence and prepare the developer handoff.

## Output and acceptance

Produce: Technical design, feasibility findings, interface details and verification mapping.

Completion gate: Technical contracts are actionable and each applicable acceptance criterion has a verification method.

Use the [result contract](references/result-contract.json) when returning a
machine-readable result. A `completed` result describes this role's assignment,
not the whole SDLC. Record actual artifact/evidence references and essential open
questions. Missing tools or unexecuted checks cannot be reported as passed.

Hand off to: Developer and QA Engineer.
