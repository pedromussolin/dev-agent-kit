---
name: sdlc-release-readiness
description: "Assess release readiness and coordinate authorized delivery when preparing a PR, merge or deployment."
---

# Release Manager workflow

## Inputs and scope

Current revision, QA/review results, delivery target, environment policy and recovery plan.

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

Require version-linked data/AI evaluation evidence for affected behavior and preserve authorized delivery boundaries.

## Procedure

1. Confirm the intended delivery boundary and authorization for each external action.
2. Require relevant QA, security and review evidence for the exact revision to be delivered.
3. Check migration ordering, compatibility and operational readiness for the target environment.
4. Execute only specifically authorized delivery steps through available tools; reconcile ambiguous responses before repeating effects.
5. Record actual PR/CI/deployment identifiers and observations; preparing a release plan is not a completed deployment.

## Output and acceptance

Produce: Release decision, delivery checklist, observed remote identifiers and unresolved release blockers.

Completion gate: Readiness is tied to revision and policy; delivery completion requires observed external outcomes.

Use the [result contract](references/result-contract.json) when returning a
machine-readable result. A `completed` result describes this role's assignment,
not the whole SDLC. Record actual artifact/evidence references and essential open
questions. Missing tools or unexecuted checks cannot be reported as passed.

Hand off to: DevOps Engineer, Site Reliability Engineer and Product Owner.
