---
name: sdlc-user-experience
description: "Plan user journeys, information architecture and interaction flows when defining or improving a product experience."
---

# UX Designer workflow

## Inputs and scope

Product brief, user evidence, acceptance goals and existing interaction patterns.

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

Design understandable AI progress, uncertainty, failure and review interactions where users need to make a decision.

## Procedure

1. Trace the intended user outcome and distinguish research evidence from assumptions.
2. Map the journey and friction points, including empty, error, loading and recovery paths.
3. Specify navigation, task flow and information hierarchy with the smallest useful interaction model.
4. Plan accessibility and usability checks; do not fabricate user interviews or usability results.
5. Hand behavior and content priorities to UI design, product ownership and QA.

## Output and acceptance

Produce: User flows, information structure, interaction requirements and usability questions.

Completion gate: Flows cover the intended outcome and meaningful failure paths with explicit evidence and unresolved research.

Use the [result contract](references/result-contract.json) when returning a
machine-readable result. A `completed` result describes this role's assignment,
not the whole SDLC. Record actual artifact/evidence references and essential open
questions. Missing tools or unexecuted checks cannot be reported as passed.

Hand off to: UI Designer, Accessibility Specialist, Product Owner and QA Engineer.
