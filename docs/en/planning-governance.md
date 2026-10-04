# Planning and continuous improvement

**Languages:** English | [Português (Brasil)](../pt-br/planning-governance.md)

Connect objectives, decisions and execution. A kit meeting is a bounded decision
workflow producing a traceable artifact. It can be asynchronous and reuse existing
reports instead of simulating a conversation among every agent.

| Organizational responsibility | Existing roles |
| --- | --- |
| Direction and value | User, PM and AI Strategist |
| Priorities and acceptance | PO and Delivery Planner |
| Technical coherence | Architect, Software Engineer and Technology Strategist |
| Experience and quality | UX/UI, accessibility, QA, security and LLM evaluation |
| Platform and data | Cloud, DevOps, SRE, DBA, Data Engineer and MLOps |
| Execution and records | Developer, reviewer, release, writer and coordinator |

These responsibilities do not require permanent processes. The user establishes
objectives/authority; agents analyze and execute within existing scope. Already
authorized decisions do not require repeated approval.

| Suggested session | Trigger | Deliverable |
| --- | --- | --- |
| Product direction | New objective or delivered-value review | Hypotheses, outcomes and priorities |
| Refinement/planning | Work ready for decomposition | Proposed backlog, acceptance and dependencies |
| Technical decision | Tool/provider/architecture change | Alternatives, decision and validation pilot |
| Retrospective | Delivery, incident or evaluation regression | Evidence-based prioritized improvement |

Weekly priority review is a suggestion. Simple decisions can be direct; sessions
serve unresolved tradeoffs or evidence, rather than every small correction.

## Bounded workflow

1. Record the objective, decision, evidence, authority and resource limits.
2. Collect only relevant role perspectives with source references.
3. Compare value, effort, data/AI, cost, dependencies and reversibility.
4. Record proposed/adopted/deferred decisions, disagreements and uncertainty.
5. Define actions with owners, acceptance and dependencies; execution readiness
   requires an actual task ID, an adopted decision and valid effective policy.
6. Measure outcomes and feed results back into the backlog.

The contract requires round/call/time limits. Paid inference needs separately
configured AI limits. Planning does not expand permissions, install tools or publish.

Use the [planning skill](../../.agents/skills/sdlc-planning-session/SKILL.md),
[template](../../templates/planning-session.md) and
[result contract](../../contracts/planning-session.schema.json).
The [example](../../examples/planning/example-session-result.json) is fictional:
proposals, not real approvals/issues. Schema validates shape; the future executor
checks references, dependency cycles, authority and role availability. The executor now supports one bounded pass of selected planning roles before
implementation. Autonomous scheduling and dedicated planning-session artifact
validation remain pending.

## Tool proposals

State the problem, existing alternatives, capability, cost, access and conformance
pilot. Use the [extension skill](../../.agents/skills/sdlc-extension-design/SKILL.md)
and [proposal template](../../templates/extension-proposal.md). PO prioritizes value
and dependencies. Relevant security/platform/data roles contribute; implementation
and activation follow the actual task's scope.

Keep durable decisions with status, alternatives, consequences and revisit criteria.
Short referenced summaries reduce repeated context. Repeating an unsupported claim
does not turn it into evidence or consensus.
