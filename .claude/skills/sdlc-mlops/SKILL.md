---
name: sdlc-mlops
description: "Prepare reproducible AI delivery and monitoring when model, prompt or retrieval versions need controlled rollout and recovery."
---

# MLOps Engineer workflow

## Inputs and scope

AI artifacts, evaluation gates, deployment environment, retention policy and separate infrastructure/AI budgets.

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

Keep AI delivery and tracing optional and reproducible; evaluate the resource overhead of Langfuse before enabling it locally or in cloud.

## Procedure

1. Inventory model/provider, prompt, retrieval and dataset versions; preserve a reproducible configuration for each release.
2. Integrate evaluation gates and authorized delivery with existing CI/CD rather than creating a separate untracked release flow.
3. Trace task and model operations with sanitized metadata; use Langfuse only when its capabilities justify its dependencies.
4. Configure quality/cost monitoring, bounded retries and fallback or rollback behavior without exposing sensitive prompts.
5. Rehearse recovery in the authorized environment and report resources, failure cases and actual or unavailable provider usage.

## Output and acceptance

Produce: AI delivery configuration, version registry, sanitized monitoring and recovery evidence.

Completion gate: A release can be traced to evaluated artifacts and recovered; monitoring respects retention and both budget scopes.

Use the [result contract](references/result-contract.json) when returning a
machine-readable result. A `completed` result describes this role's assignment,
not the whole SDLC. Record actual artifact/evidence references and essential open
questions. Missing tools or unexecuted checks cannot be reported as passed.

Hand off to: DevOps Engineer, Site Reliability Engineer, LLM Evaluation Engineer and Release Manager.
