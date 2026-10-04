---
name: sdlc-backlog-refinement
description: "Refine and prioritize backlog items with testable acceptance criteria when product goals or candidate tasks are available."
---

# Product Owner workflow

## Inputs and scope

Product brief, candidate backlog, existing priorities and stakeholder authority.

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

Include data quality, AI fallback and cost-sensitive acceptance criteria when the feature depends on them.

## Procedure

1. Trace each candidate item to the product outcome and supplied priority constraints.
2. Split work into independently reviewable outcomes with explicit exclusions.
3. Write observable acceptance criteria and involve QA in ambiguous scenarios.
4. Surface competing priorities or business decisions that exceed the supplied authority.
5. Mark items ready only when required product and technical questions are resolved.

## Output and acceptance

Produce: Ordered backlog, bounded scope, acceptance criteria and readiness assessment.

Completion gate: Each ready item has a real task reference, bounded scope, acceptance criteria and priority rationale.

Use the [result contract](references/result-contract.json) when returning a
machine-readable result. A `completed` result describes this role's assignment,
not the whole SDLC. Record actual artifact/evidence references and essential open
questions. Missing tools or unexecuted checks cannot be reported as passed.

Hand off to: Delivery Planner, Software Engineer and QA Engineer.
