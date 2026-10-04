---
name: sdlc-task-coordination
description: "Coordinate requested SDLC roles and evidence handoffs when a user asks to run a multi-role development workflow."
---

# SDLC Coordinator workflow

## Inputs and scope

Initiative/task contract, selected roles, execution policy, artifacts and resource limits.

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

Select the smallest sufficient set of roles and context; track data dependencies, attempt limits and separate infrastructure/AI accounting.

## Procedure

1. Classify the task and select relevant roles from the catalog; do not activate the whole roster for every change.
2. Check required inputs, action authority and workspace ownership before assigning work.
3. Delegate only when requested or authorized by applicable project/workflow instructions and supported by the runtime.
4. Collect structured outputs, compare revision-specific evidence and route bounded repair requests.
5. Report partial, blocked and completed stages accurately; this skill does not supply a persistent scheduler or crash recovery.

## Output and acceptance

Produce: Role assignments, stage/evidence ledger, blockers and accurate workflow status.

Completion gate: Reported stage status matches received evidence and outstanding blockers remain explicit.

Use the [result contract](references/result-contract.json) when returning a
machine-readable result. A `completed` result describes this role's assignment,
not the whole SDLC. Record actual artifact/evidence references and essential open
questions. Missing tools or unexecuted checks cannot be reported as passed.

Hand off to: Selected specialists and the user.
