---
name: sdlc-delivery-planning
description: "Break refined work into dependencies and executable handoffs when planning delivery or replanning a blocked task."
---

# Delivery Planner workflow

## Inputs and scope

Refined backlog, technical constraints, available roles and execution limits.

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

Choose only relevant roles, bound attempts and context, and include evaluation/data preparation dependencies.

## Procedure

1. Identify prerequisite artifacts and shared resources for the selected work.
2. Split work by observable outcomes; assign ownership and inputs rather than vague role names.
3. Sequence dependencies and identify independent work without assuming unlimited workers.
4. Record uncertainty in estimates and blockers instead of inventing delivery dates.
5. Define verification points, bounded repair loops and when a product decision is needed.

## Output and acceptance

Produce: Task graph, work sequence, ownership, dependencies and verification milestones.

Completion gate: Every planned item has inputs, an owner, a completion gate and dependencies without cycles.

Use the [result contract](references/result-contract.json) when returning a
machine-readable result. A `completed` result describes this role's assignment,
not the whole SDLC. Record actual artifact/evidence references and essential open
questions. Missing tools or unexecuted checks cannot be reported as passed.

Hand off to: SDLC Coordinator and the selected specialists.
