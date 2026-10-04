# Agent role contract

This template defines a logical responsibility, not a requirement for a dedicated
model, process or provider. Use only the roles relevant to the initiative or task.

## Definition

- `role_id`: Stable role ID from `agents/catalog.json`, such as `product-manager`,
  `software-architect`, `qa-engineer` or `security-engineer`.
- `purpose`: The question this role is responsible for answering.
- `inputs`: Task/product context, required upstream artifacts and applicable rules.
- `decisions`: Choices this role may make within the supplied authority.
- `tools`: Permitted capabilities and workspace scope.
- `outputs`: Structured result contract and required artifacts.
- `gates`: Independent evidence needed to accept the output.
- `handoff`: Consumers of the output and blocking questions to propagate.
- `feedback`: Conditions that return work to a previous role/stage.
- `limits`: Time, attempts and provider usage constraints.

## Shared result fields

The machine-readable source is `contracts/agent-result.schema.json`. Each portable
skill bundles a generated copy under `references/result-contract.json`.

- `status`: Proposed structured outcome validated by the orchestrator.
- `summary`: Concise result with evidence references.
- `decisions`: Choices, rationale and constraints.
- `artifacts`: Paths or persistent identifiers for produced evidence.
- `open_questions`: Unknowns with their impact on downstream stages.
- `blocking_findings`: Findings that prevent the next transition.
- `acceptance_results`: Applicable criteria mapped to outcomes and evidence.

## Typical outputs

| Role | Output |
| --- | --- |
| PM | Product brief, problem evidence and outcome metrics |
| PO | Ordered backlog, scope, acceptance criteria and readiness decision |
| Planner | Task breakdown, dependencies and execution plan |
| Software engineer | Feasibility, technical contracts, implementation and evidence |
| Architect | Architecture decisions, interfaces and tradeoffs |
| Developer | Diff, implementation notes and relevant tests |
| QA | Early test strategy, acceptance scenarios and quality findings |
| Reviewer | Findings linked to the current diff and check evidence |
| Release/operations | PR/CI/release identifiers, health observations and recovery results |

Product claims need supplied evidence; missing information must remain explicit.
Code claims need independent check evidence for the current revision. Delivery
claims need observed external results. Combining roles does not remove these gates.
