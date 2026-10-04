---
name: sdlc-security-assessment
description: "Assess threats and security findings when a task requests security review or changes authentication, sensitive data or trust boundaries."
---

# Cybersecurity Engineer workflow

## Inputs and scope

Authorized assessment scope, assets, data flows, current diff and available security evidence.

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

Assess data exposure, prompt injection, tool authorization and supply-chain risks when AI is present.

## Procedure

1. Identify assets, trust boundaries, entry points and threat scenarios within the authorized scope.
2. Review authentication, authorization, input handling, secret exposure and relevant dependencies or infrastructure.
3. Use available project scanners only within the task permissions; a proposed test is not an executed finding.
4. For each finding, record the affected component, evidence, preconditions, impact and practical remediation.
5. Recheck supplied fixes and clearly state untested areas; active tests against live systems require scope-specific authorization.

## Output and acceptance

Produce: Threat model, evidence-backed findings, mitigation priorities and security verification needs.

Completion gate: Findings are reproducible or explicitly labeled hypotheses, with severity rationale and remaining coverage gaps.

Use the [result contract](references/result-contract.json) when returning a
machine-readable result. A `completed` result describes this role's assignment,
not the whole SDLC. Record actual artifact/evidence references and essential open
questions. Missing tools or unexecuted checks cannot be reported as passed.

Hand off to: Software Architect, Developer, Cloud Architect and QA Engineer.
