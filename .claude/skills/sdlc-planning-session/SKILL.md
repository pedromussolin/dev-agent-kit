---
name: sdlc-planning-session
description: "Facilitate a bounded planning or retrospective session when next steps, priorities, tool proposals or improvement decisions need documented outcomes."
---

# Planning Session

Read target-project instructions, the caller's objective and existing evidence.
Read [project defaults](references/project-defaults.json) for local hosting,
the BRL 100/month infrastructure cap and separate AI budget; explicit user/project
settings take precedence. Unspecified AI spending is not unlimited.

## Procedure

1. Define the decision to make, existing evidence and the caller's decision authority. Use the session template when useful.
2. Select only participants relevant to the decision. Reuse existing role results; delegate only when authorized and supported, otherwise record missing perspectives.
3. Compare proposals by user value, effort, dependencies, data/AI quality, infrastructure/AI cost and reversibility. Record disagreement and uncertainty, not fabricated consensus.
4. Stop at the configured round/call/time limits. Unresolved decisions become questions or deferred items; additional discussion does not imply progress.
5. Produce a planning artifact with decisions, authority references and actions with owners, acceptance and dependencies. Proposed actions are not executable tasks until linked to actual task IDs and validated by the executor.

## Deliverable and acceptance

A session result validates against the bundled planning contract; referenced decisions/dependencies resolve, ready actions refer to adopted decisions, and missing authority remains explicit. This skill neither schedules meetings nor creates remote issues.

Use the [specialized artifact contract](references/planning-session.schema.json) for the planning
or extension artifact. Return the role's [result contract](references/result-contract.json)
with references to that artifact, observed evidence and outstanding questions.
No background scheduler, model calls or deployments are supplied by this skill.
