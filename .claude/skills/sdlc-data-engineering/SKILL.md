---
name: sdlc-data-engineering
description: "Design or implement data ingestion, transformations and quality contracts when reliable analytical or AI inputs are required."
---

# Data Engineer workflow

## Inputs and scope

Source systems, consumers, schemas, ownership, access policy, data volume and freshness requirements.

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

Make data contracts, provenance, idempotence and quality checks explicit before adding retrieval or AI consumers.

## Procedure

1. Identify data owners, source provenance, schema contracts, consumers and quality/freshness requirements.
2. Implement repeatable ingestion and transformations with idempotence, checkpoints and failure visibility.
3. Validate schema, completeness, duplicates and sensitive-data handling using representative fixtures.
4. Define lineage, versioning, deletion, retention and recovery; avoid sending unrestricted datasets to model providers.
5. Verify output contracts and recovery behavior; hand storage/query responsibilities to DBA and datasets to AI/evaluation roles.

## Output and acceptance

Produce: Data contracts, pipeline changes, quality checks, lineage and recovery evidence.

Completion gate: Consumers receive validated, traceable data; repeat runs and recovery do not silently duplicate or corrupt records.

Use the [result contract](references/result-contract.json) when returning a
machine-readable result. A `completed` result describes this role's assignment,
not the whole SDLC. Record actual artifact/evidence references and essential open
questions. Missing tools or unexecuted checks cannot be reported as passed.

Hand off to: Database Administrator, AI Engineer, Security Engineer and LLM Evaluation Engineer.
