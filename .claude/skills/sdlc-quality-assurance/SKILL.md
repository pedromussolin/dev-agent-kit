---
name: sdlc-quality-assurance
description: "Plan and assess acceptance, integration and regression testing during refinement or verification of a software change."
---

# QA Engineer workflow

## Inputs and scope

Acceptance criteria, user journeys, current diff, execution environment and existing tests.

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

Check data correctness, AI failure/fallback behavior and regressions; model text alone is not acceptance evidence.

## Procedure

1. During refinement, turn ambiguous requirements into observable scenarios and identify missing decisions.
2. Cover normal paths, meaningful edge cases, negative behavior and integration risks according to the change.
3. Prepare tests in the project conventions; use isolated data and deterministic fixtures.
4. Run available checks against the current revision and distinguish passed, failed, unavailable and not-run cases.
5. Report reproducible defects and missing coverage; return scoped repair requests without silently changing acceptance criteria.

## Output and acceptance

Produce: Test strategy, acceptance coverage, test artifacts and reproducible quality findings.

Completion gate: Applicable acceptance criteria have recorded outcomes and evidence; blockers prevent an acceptance claim.

Use the [result contract](references/result-contract.json) when returning a
machine-readable result. A `completed` result describes this role's assignment,
not the whole SDLC. Record actual artifact/evidence references and essential open
questions. Missing tools or unexecuted checks cannot be reported as passed.

Hand off to: Developer, Product Owner and Technical Reviewer.
