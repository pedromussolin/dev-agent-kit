---
name: sdlc-reliability-operations
description: "Plan or assess observability, reliability, incident response and recovery when operational behavior is in scope."
---

# Site Reliability Engineer workflow

## Inputs and scope

Service topology, reliability objectives, authorized telemetry and incident or release context.

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

Correlate run/task/role/attempt identifiers in sanitized JSON telemetry; stage OpenTelemetry, Grafana/Loki/Alloy and Prometheus according to operational need.

## Procedure

1. Identify service outcomes, supplied reliability objectives and critical dependencies.
2. Inspect relevant telemetry and separate observed symptoms from causal hypotheses.
3. Prepare observability or runbook changes with actionable signals and data minimization.
4. Rehearse recovery in an authorized environment; live remediation follows the supplied incident authority.
5. Record verified outcomes and follow-up items; health checks alone do not prove product outcomes.

## Output and acceptance

Produce: Reliability plan, telemetry findings, incident timeline and recovery evidence.

Completion gate: Reliability claims use observed evidence and recovery actions have scope, outcome and remaining risks.

Use the [result contract](references/result-contract.json) when returning a
machine-readable result. A `completed` result describes this role's assignment,
not the whole SDLC. Record actual artifact/evidence references and essential open
questions. Missing tools or unexecuted checks cannot be reported as passed.

Hand off to: DevOps Engineer, Database Administrator, Security Engineer and Product Manager.
