# Planning session

This template defines a bounded decision workflow. It does not schedule a calendar
meeting, invoke agents or create remote issues. Replace placeholders with real
references; preserve existing authorization and the project's effective policies.

## Charter

- Session identifier, initiative/project references and objective.
- Decision to make and the evidence that makes discussion necessary.
- Decision owner and existing authority reference.
- Relevant roles; explain what each perspective contributes.
- Round/call/time limits and separate AI spending configuration.

## Preparation and comparison

- Current outcomes, blockers, incident/evaluation findings or user feedback.
- Options, including reuse of existing tools and keeping the current approach.
- Value, effort, dependencies, infrastructure cost, AI cost and reversibility.
- Assumptions, disagreements and essential missing information.

## Decisions and backlog

- Proposed, adopted or deferred decision, rationale and evidence references.
- Authority for adopted decisions; consensus does not grant new permissions.
- Actions with owner role, acceptance criteria, dependencies and decision links.
- Real issue/task reference before an action becomes ready for execution.
- Unresolved questions and when to revisit the decision.

Store the result using `contracts/planning-session.schema.json`. The executor must
also check reference integrity, dependency cycles, role availability and authority;
JSON Schema validates shape, not these semantic or execution requirements.
