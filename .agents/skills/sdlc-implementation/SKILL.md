---
name: sdlc-implementation
description: "Implement or repair a scoped software task when acceptance criteria and relevant project context are available."
---

# Developer workflow

## Inputs and scope

Task scope, acceptance criteria, technical plan, assigned workspace and permitted actions.

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

Preserve project languages; implement data validation and bounded AI behavior only where requirements call for them.

## Procedure

1. Read target project instructions and manifests; preserve its language and dependency conventions.
2. Confirm the assigned workspace and implement the agreed behavior with focused changes.
3. Add meaningful regression coverage for changed behavior; keep unrelated refactors out of scope.
4. Run the project checks applicable to the change and record actual results; unavailable checks remain unresolved.
5. Hand the current diff and evidence to QA and review; do not self-approve delivery.

## Output and acceptance

Produce: Code diff, relevant tests, check results and implementation notes.

Completion gate: The diff addresses the task and carries current check evidence or explicit blockers.

Use the [result contract](references/result-contract.json) when returning a
machine-readable result. A `completed` result describes this role's assignment,
not the whole SDLC. Record actual artifact/evidence references and essential open
questions. Missing tools or unexecuted checks cannot be reported as passed.

Hand off to: QA Engineer and Technical Reviewer.
