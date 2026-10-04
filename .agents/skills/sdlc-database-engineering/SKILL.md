---
name: sdlc-database-engineering
description: "Design, assess or change schemas, migrations, query performance and database recovery when database work is in scope."
---

# Database Administrator workflow

## Inputs and scope

Data model, workload, current schema, migration constraints and authorized database environment.

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

Distinguish SQLite executor state from project databases. Prefer PostgreSQL and DBeaver when appropriate; define migrations, query evidence, retention and tested recovery.

## Procedure

1. Inspect schemas, query paths and database conventions; distinguish model design from live administration.
2. Evaluate integrity, indexes, query plans and pagination using available evidence instead of guessing bottlenecks.
3. Prepare compatible migrations and backfill sequencing with explicit locking and data-volume assumptions.
4. Validate against an authorized test database; record actual checks and remaining production uncertainties.
5. Define backup/restore and recovery verification when relevant; destructive data operations require explicit scope and policy.

## Output and acceptance

Produce: Schema/query/migration diff, performance evidence and data recovery plan.

Completion gate: Changes preserve data invariants and have migration, verification and recovery evidence appropriate to their risk.

Use the [result contract](references/result-contract.json) when returning a
machine-readable result. A `completed` result describes this role's assignment,
not the whole SDLC. Record actual artifact/evidence references and essential open
questions. Missing tools or unexecuted checks cannot be reported as passed.

Hand off to: Software Architect, Developer, DevOps Engineer and QA Engineer.
