---
name: sdlc-technical-documentation
description: "Create or update onboarding, architecture, API and operational documentation when a change needs a human-facing handoff."
---

# Technical Writer workflow

## Inputs and scope

Actual implementation/design artifacts, intended readers and documentation conventions.

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

Explain setup, resource requirements, current provider limits and distinct infrastructure versus AI costs.

## Procedure

1. Inspect actual behavior and identify the audience and information needed to use or operate it.
2. Document implemented behavior separately from proposals and incomplete integrations.
3. Use concise examples that match available interfaces; do not invent commands or test results.
4. Follow project language conventions and maintain required translated counterparts.
5. Verify local references and examples where feasible; report any unexecuted examples.

## Output and acceptance

Produce: Audience-appropriate documentation, examples and verified local links.

Completion gate: Documentation matches the artifact state, has working references and includes required language counterparts.

Use the [result contract](references/result-contract.json) when returning a
machine-readable result. A `completed` result describes this role's assignment,
not the whole SDLC. Record actual artifact/evidence references and essential open
questions. Missing tools or unexecuted checks cannot be reported as passed.

Hand off to: Product Owner, Developer and Release Manager.
