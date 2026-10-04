---
name: sdlc-accessibility-review
description: "Assess accessible interaction and interface requirements when accessibility review is requested or an affected flow requires it."
---

# Accessibility Specialist workflow

## Inputs and scope

User flows, UI specification, implemented interface and the project accessibility target.

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

Check keyboard and assistive-technology behavior for streamed AI results, status changes and recovery controls when present.

## Procedure

1. Identify the affected journeys and supplied accessibility target; verify applicable standard details from primary sources.
2. Inspect semantics, labels, keyboard paths, focus management, contrast and assistive-technology expectations.
3. Run available automated and manual checks in the authorized environment; state when browser or assistive tools are unavailable.
4. Distinguish automated results from manual evidence; an automated pass does not establish full conformance.
5. Report reproduction steps and practical changes to UI, development and QA.

## Output and acceptance

Produce: Accessibility findings, test evidence and remediation requirements.

Completion gate: The assessment identifies target, checked scenarios, observed evidence and unverified coverage.

Use the [result contract](references/result-contract.json) when returning a
machine-readable result. A `completed` result describes this role's assignment,
not the whole SDLC. Record actual artifact/evidence references and essential open
questions. Missing tools or unexecuted checks cannot be reported as passed.

Hand off to: UX Designer, UI Designer, Developer and QA Engineer.
