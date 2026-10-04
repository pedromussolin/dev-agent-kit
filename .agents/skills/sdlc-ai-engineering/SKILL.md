---
name: sdlc-ai-engineering
description: "Design or implement model integrations, tool use and retrieval when an application needs evaluated AI behavior."
---

# AI Engineer workflow

## Inputs and scope

Approved behavior, data contracts, provider capabilities, evaluation fixtures and task-specific execution limits.

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

Prefer data contracts, structured results, bounded tool calls and evaluated provider adapters over opaque agent loops.

## Procedure

1. Inspect application boundaries and implement a deterministic baseline or fallback where appropriate.
2. Use typed inputs and structured outputs; validate tool arguments independently and restrict tools to task-authorized capabilities.
3. Implement provider-neutral boundaries with provider-specific adapters, timeouts, cancellation and bounded retries.
4. Use retrieval only for a demonstrated context need; preserve provenance, access rules and invalidation on data changes.
5. Run authorized evaluations against representative cases; report observed quality, usage and failure behavior without inventing token savings.

## Output and acceptance

Produce: AI integration changes, data/tool contracts, regression evidence and cost/quality observations.

Completion gate: Applicable checks and representative evaluation cases pass; limits, failure handling and fallback are demonstrable.

Use the [result contract](references/result-contract.json) when returning a
machine-readable result. A `completed` result describes this role's assignment,
not the whole SDLC. Record actual artifact/evidence references and essential open
questions. Missing tools or unexecuted checks cannot be reported as passed.

Hand off to: Context Engineer, LLM Evaluation Engineer, Security Engineer and MLOps Engineer.
