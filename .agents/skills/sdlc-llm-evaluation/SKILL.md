---
name: sdlc-llm-evaluation
description: "Build and run AI evaluations when prompts, models, tools or retrieval need quality, safety and cost regression evidence."
---

# LLM Evaluation Engineer workflow

## Inputs and scope

Behavior requirements, representative datasets, candidate versions, baseline, evaluation thresholds and authorized inference budget.

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

Compare quality and total usage on reproducible cases; include retries and judge-model calls in AI accounting.

## Procedure

1. Translate acceptance criteria into versioned representative cases, including malformed outputs and failure scenarios.
2. Separate deterministic assertions from model-judged scores; calibrate judgments against human-labeled examples.
3. Measure success, schema conformance, grounding, relevant security cases, latency and cost per accepted task.
4. Use a suitable evaluation runner such as promptfoo or project tests; run paid inference only within explicitly configured limits.
5. Compare candidates on the same cases and report limitations; block rollout on agreed regressions or missing essential evidence.

## Output and acceptance

Produce: Evaluation dataset, runner configuration, comparison report and version-specific release gate.

Completion gate: The report identifies data/model/prompt versions, thresholds, observed results and unexecuted or uncertain measurements.

Use the [result contract](references/result-contract.json) when returning a
machine-readable result. A `completed` result describes this role's assignment,
not the whole SDLC. Record actual artifact/evidence references and essential open
questions. Missing tools or unexecuted checks cannot be reported as passed.

Hand off to: AI Strategist, AI Engineer, QA Engineer and Release Manager.
