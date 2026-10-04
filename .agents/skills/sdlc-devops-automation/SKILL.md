---
name: sdlc-devops-automation
description: "Create or improve CI/CD, infrastructure-as-code and delivery automation when build or platform work is requested."
---

# DevOps Engineer workflow

## Inputs and scope

Cloud design, repository toolchains, environment policy and delivery requirements.

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

Use Docker Compose for optional local services; use reproducible IaC such as OpenTofu if cloud is justified and budgeted.

## Procedure

1. Inspect existing pipelines, lockfiles and infrastructure definitions before choosing tools.
2. Separate build, test, artifact publication and environment deployment with explicit dependencies.
3. Prepare repeatable CI/IaC changes and validate them using available project tools.
4. Preserve secret handling, scoped identities and declared environment policy; do not broaden permissions to make a check pass.
5. Record plan/check results and recovery steps; live apply, resource deletion or deployment follows task authorization.

## Output and acceptance

Produce: CI/CD or IaC diff, validation evidence and operational runbook.

Completion gate: Configuration is reviewable, applicable validations are recorded and live operations are separately identified.

Use the [result contract](references/result-contract.json) when returning a
machine-readable result. A `completed` result describes this role's assignment,
not the whole SDLC. Record actual artifact/evidence references and essential open
questions. Missing tools or unexecuted checks cannot be reported as passed.

Hand off to: Technical Reviewer, Release Manager and Site Reliability Engineer.
