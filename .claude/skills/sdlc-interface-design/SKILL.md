---
name: sdlc-interface-design
description: "Specify screens, interaction states and design-system usage when interface planning or visual design is requested."
---

# UI Designer workflow

## Inputs and scope

UX flows, existing design system, screen requirements and supported devices.

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

Specify accessible loading, empty, error and AI-result states using existing design tokens and component conventions.

## Procedure

1. Inspect existing components, tokens and design references before creating new patterns.
2. Translate user flows into screen structure, hierarchy and responsive behavior.
3. Specify interaction states, content and accessibility requirements for each important component.
4. Use available design tools only when requested or relevant; do not claim a mockup exists without an artifact.
5. Provide implementable specifications and identify design-system gaps without forcing a particular frontend stack.

## Output and acceptance

Produce: Screen/state specification, component mapping, tokens and implementation handoff.

Completion gate: The handoff covers screen structure, responsive behavior, states and components with artifact references.

Use the [result contract](references/result-contract.json) when returning a
machine-readable result. A `completed` result describes this role's assignment,
not the whole SDLC. Record actual artifact/evidence references and essential open
questions. Missing tools or unexecuted checks cannot be reported as passed.

Hand off to: Developer, Accessibility Specialist and QA Engineer.
