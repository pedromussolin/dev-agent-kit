---
name: sdlc-cloud-design
description: "Design cloud topology, identity and resilience when cloud hosting or infrastructure choices are in scope."
---

# Cloud Architect workflow

## Inputs and scope

Workload requirements, existing cloud environment, data constraints and cost assumptions.

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

Keep local hosting as the default. A cloud proposal must account for compute, database, logs, storage, backups, network and currency/tax fees within the BRL 100 infrastructure cap.

## Procedure

1. Inspect the workload and existing hosting; respect the chosen cloud and region constraints.
2. Compare topology choices against availability, recovery, latency, data residency and operational complexity.
3. Design least-privilege identity, network exposure and environment separation with security input.
4. Verify current service capabilities and prices from provider sources; record workload assumptions rather than promise fixed cost.
5. Hand an implementable design and recovery objectives to DevOps; design work does not provision live resources.

## Output and acceptance

Produce: Cloud design, identity/network boundaries, resilience decisions and cost model assumptions.

Completion gate: The design names environment, identity/network boundaries, recovery requirements and justified cost assumptions.

Use the [result contract](references/result-contract.json) when returning a
machine-readable result. A `completed` result describes this role's assignment,
not the whole SDLC. Record actual artifact/evidence references and essential open
questions. Missing tools or unexecuted checks cannot be reported as passed.

Hand off to: DevOps Engineer, Security Engineer and Site Reliability Engineer.
