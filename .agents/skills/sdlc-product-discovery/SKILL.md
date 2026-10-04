---
name: sdlc-product-discovery
description: "Investigate product problems and define evidence-backed outcomes when starting or reassessing an initiative."
---

# Product Manager workflow

## Inputs and scope

User problem, stakeholder goals, available research and business constraints.

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

Require measurable user value, data availability and separate infrastructure/AI cost assumptions in product discovery.

## Procedure

1. Separate supplied evidence from hypotheses; identify the affected users and current behavior.
2. Frame the problem, desired outcome and constraints without adding unrelated features.
3. Compare the smallest useful solutions and how success would be measured.
4. Record hypotheses requiring real research; never manufacture interviews, demand or market data.
5. Hand the outcome and decision boundaries to product ownership; keep essential unanswered questions visible.

## Output and acceptance

Produce: Product brief, assumptions, outcome measures and unresolved product questions.

Completion gate: The brief names a problem, intended users, observable outcome and evidence or explicitly labeled assumptions.

Use the [result contract](references/result-contract.json) when returning a
machine-readable result. A `completed` result describes this role's assignment,
not the whole SDLC. Record actual artifact/evidence references and essential open
questions. Missing tools or unexecuted checks cannot be reported as passed.

Hand off to: Product Owner, UX Designer and Technology Strategist.
