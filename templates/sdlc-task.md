# SDLC task contract

This is a design template, not a runtime schema. Replace placeholders with real
project information before execution. Never invent an issue ID or base revision.

## Identity and intent

- `task_id`: Existing issue or task identifier.
- `initiative_id`: Product initiative or parent backlog reference when applicable.
- `problem`: Evidence-backed user or business problem, with unknowns identified.
- `expected_outcome`: Desired outcome and observable success measure.
- `priority`: Explicit ordering and rationale from product ownership.
- `goal`: Observable user or system outcome.
- `repository`: Target repository and local checkout.
- `base_branch`: Discovered default branch or explicitly configured integration branch.
- `base_revision`: Confirmed commit used for the isolated workspace.
- `acceptance_criteria`: Numbered behaviors and how each will be verified.
- `scope`: Allowed changes and explicit exclusions.
- `open_questions`: Missing decisions and which stages they block.

## Components

For each component, declare:

- `name`, `working_directory`, `language`, `manifest`, `lockfile`.
- `setup`: Dependency/environment preparation and required authorization.
- `checks`: Named commands as argument arrays, timeout and required outcome.
- `artifacts`: Expected reports or build outputs.

## Agent execution

- `provider`: Selected and authenticated CLI/API adapter.
- `roles`: Selected role IDs from `agents/catalog.json`, including relevant product, design, engineering, security, cloud, DevOps, database and quality specialists.
- `readiness`: Required product, design and QA inputs before implementation.
- `context`: Required rules, files, architecture and prior evidence.
- `output_contract`: Structured result fields and validation requirements.
- `limits`: Maximum attempts, elapsed time and provider usage where measurable.

## Data, AI and budget constraints

- `project_defaults`: Effective version/fingerprint of `policies/project-defaults.json` or bundled policy.
- `data_contracts`: Schemas, ownership, provenance, quality, privacy and retention when applicable.
- `ai_behavior`: Model/tool boundaries, deterministic baseline, evaluation cases and fallback when applicable.
- `hosting`: Local by default; optional cloud needs a complete cost estimate.
- `infrastructure_budget`: BRL 100/month total cap; record prices, region, usage, conversion and fees.
- `ai_budget`: Separate configured amount; unspecified is not unlimited.
- `usage_evidence`: Exposed tokens/cache, calls, retries, latency, cost and explicit unavailable measurements.

## Policy and delivery

- `automatic_actions`: Actions already authorized for unattended execution.
- `approval_actions`: Actions requiring a specific approval under project policy.
- `disabled_actions`: Actions the executor must not perform.
- `delivery_target`: Verified diff, PR, merge, deployment or operational verification.
- `environment`: Target environment if delivery includes deployment.
- `rollback`: Reversal procedure and trigger when deployment is in scope.

## Evidence

- `run_id`, `attempt_id`, `stage`, `status`, timestamps.
- Base revision, resulting revision/diff fingerprint and configuration fingerprint.
- Commands, exit codes, agent metadata and artifact references.
- Acceptance results and blocking review findings.
- Product decisions, priority changes and operational feedback when applicable.
- Remote PR/CI/release identifiers and observed outcomes when applicable.
