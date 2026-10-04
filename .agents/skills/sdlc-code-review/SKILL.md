---
name: sdlc-code-review
description: "Review a current diff for correctness, regressions and design compatibility when independent technical review is requested."
---

# Technical Reviewer workflow

## Inputs and scope

Task, acceptance criteria, architecture decisions, current diff and verification evidence.

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

Review data contracts, bounded tool/model use and evidence freshness without requiring unnecessary new infrastructure.

## Procedure

1. Read task intent and inspect the actual diff and affected execution paths.
2. Check invariants, edge cases, error handling and compatibility using the project conventions.
3. Verify that supplied test and QA evidence applies to the reviewed revision.
4. Report concrete actionable findings with file references, impact and reproduction where possible.
5. Separate blocking defects from optional improvements and unverified assumptions; review does not approve its own fixes.

## Output and acceptance

Produce: Prioritized review findings and evidence gaps tied to the current revision.

Completion gate: Findings and the review conclusion reference the actual diff and current verification evidence.

Use the [result contract](references/result-contract.json) when returning a
machine-readable result. A `completed` result describes this role's assignment,
not the whole SDLC. Record actual artifact/evidence references and essential open
questions. Missing tools or unexecuted checks cannot be reported as passed.

Hand off to: Developer, QA Engineer and Release Manager.
