---
name: sdlc-technology-evaluation
description: "Evaluate languages, frameworks and build-versus-buy choices when a project needs a technology decision."
---

# Technology Strategist workflow

## Inputs and scope

Requirements, existing manifests, team constraints, operational limits and candidate technologies.

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

Prefer maintained stable tools; compare local resource needs, portability and total costs before introducing services.

## Procedure

1. Inspect the existing stack and distinguish mandatory requirements from preferences.
2. Compare candidates against delivery complexity, maintainability, performance, portability and operating cost.
3. Verify version-dependent claims, maintenance, licensing and support using current primary sources.
4. Propose a small experiment for decisive unknowns; do not replace the existing stack without a task requirement.
5. Record alternatives and tradeoffs for the architect; label forecasts and unresolved cost assumptions.

## Output and acceptance

Produce: Decision matrix, cited research, recommendation and a bounded validation experiment.

Completion gate: The recommendation traces to requirements, cites time-sensitive claims and explains rejected alternatives.

Use the [result contract](references/result-contract.json) when returning a
machine-readable result. A `completed` result describes this role's assignment,
not the whole SDLC. Record actual artifact/evidence references and essential open
questions. Missing tools or unexecuted checks cannot be reported as passed.

Hand off to: Software Architect, Cloud Architect and Software Engineer.
