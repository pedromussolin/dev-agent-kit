---
name: sdlc-context-engineering
description: "Optimize prompts, context selection and model routing when agent token consumption or response reliability needs improvement."
---

# Context Engineer workflow

## Inputs and scope

Representative tasks, baseline results, context sources, provider capabilities and actual or explicitly unavailable usage measurements.

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

Measure savings per accepted task; preserve source references and quality gates when reducing context or routing to cheaper models.

## Procedure

1. Measure the baseline by accepted task outcome, including retries, context size, latency and usage when available.
2. Select relevant files and evidence per role instead of loading the whole repository or full conversation history.
3. Version reusable instructions and structured handoff summaries; include source references and invalidate stale summaries.
4. Evaluate provider-specific caching and cheaper-model routing using current documentation; treat cache hits and prices as measured or unknown.
5. Compare changes on the same regression cases; keep optimizations only if acceptance and safety criteria remain satisfied.

## Output and acceptance

Produce: Versioned context/prompt assets and before/after quality, usage and latency comparison.

Completion gate: The optimization has reproducible task cases, no unacceptable quality regression, and explicit measured versus estimated costs.

Use the [result contract](references/result-contract.json) when returning a
machine-readable result. A `completed` result describes this role's assignment,
not the whole SDLC. Record actual artifact/evidence references and essential open
questions. Missing tools or unexecuted checks cannot be reported as passed.

Hand off to: AI Engineer, LLM Evaluation Engineer and SDLC Coordinator.
