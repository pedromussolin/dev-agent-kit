---
name: sdlc-ai-strategy
description: "Evaluate AI opportunities and define an AI roadmap when model use, value, risk or model-versus-deterministic tradeoffs are in scope."
---

# AI Strategist workflow

## Inputs and scope

Product outcomes, workload, representative data, privacy constraints and a separately defined AI spending limit.

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

Treat AI as a measurable product capability with a deterministic baseline, privacy boundaries and a separately defined inference budget.

## Procedure

1. Identify the measurable user outcome and compare an AI approach with a deterministic baseline.
2. Map data availability, ownership, quality, privacy and failure consequences before selecting a model.
3. Compare candidate providers or local models using current capabilities, project constraints and total cost per accepted outcome.
4. Define evaluation cases, rollout limits, fallback behavior and a bounded pilot; do not treat an unspecified AI budget as unlimited.
5. Deliver a prioritized roadmap with hypotheses and measurable go/no-go criteria to engineering and product.

## Output and acceptance

Produce: AI decision record, prioritized roadmap, evaluation plan and separate AI cost assumptions.

Completion gate: Each recommendation has a baseline, data requirements, evaluation metric, fallback and explicit cost assumptions.

Use the [result contract](references/result-contract.json) when returning a
machine-readable result. A `completed` result describes this role's assignment,
not the whole SDLC. Record actual artifact/evidence references and essential open
questions. Missing tools or unexecuted checks cannot be reported as passed.

Hand off to: Product Manager, AI Engineer, Data Engineer and LLM Evaluation Engineer.
