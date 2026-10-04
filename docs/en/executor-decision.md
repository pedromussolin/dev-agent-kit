# First-executor decision

**Languages:** English | [Português (Brasil)](../pt-br/executor-decision.md)

Version 0.2 adds configurable planning/verification roles, live public activity,
observed-token guards and a FastAPI/SSE monitor. `CodexAppServer` joins `CodexCLI`;
GitHub CLI delivery supports PR, declared CI checks, matched-head merge and
configured deployment/smoke/rollback. SQLite remains a concrete single-user store.
The installed app-server command is experimental; pin and test its compatibility.
Remote product wiring is separate from local acceptance. See
[operations](local-executor.md) and [delivery/Actions](delivery-and-actions.md).

The decision below records the initial v0.1 tradeoffs; its future-tense items are
historical and the v0.2 guides define the current executable scope.

Status: the initial local implementation is available in `dev_agent_kit/`.
It runs developer → component checks → QA → technical review and delivers a diff.
See the [operating guide](local-executor.md). Broader SDLC stages remain planned.

## Recommendation and rationale

Start with a **modular Python CLI, SQLite state and one agent adapter**. Python
supports tooling/data/evaluation integration. SQLite avoids a state server for a
single user and sequential tasks. Target projects remain free to use their own
languages, including Go, Python and TypeScript.

Use an explicit persisted state machine to control transitions, limits and evidence.
Agents receive assignments and propose results; the executor establishes actual
check outcomes and authorized delivery boundaries.

| Option | Current fit | Reconsider when |
| --- | --- | --- |
| Python + SQLite + controlled subprocesses | Recommended for a local sequential workflow with existing tools | Concrete requirements justify extracting components |
| LangGraph | Agent graphs, checkpoints and human interaction; project policies/tools still need integration | Those graph capabilities recur across real workflows |
| Temporal | Durable workflows with workers, plus infrastructure to operate | Distributed tasks and cross-service execution become necessary |

LangGraph offers orchestration/persistence capabilities; Temporal has self-hosted
deployment. Both are valid alternatives. The initial proposal minimizes service
operation for personal use. [LangGraph](https://docs.langchain.com/oss/python/langgraph/overview),
[Temporal](https://docs.temporal.io/self-hosted-guide).

A custom flow also has a cost: recovery, transitions and duplicate effects need
meaningful tests. Specify a small number of states/paths instead of recreating a
generic workflow framework.

## Modules and contracts

| Module | Responsibility |
| --- | --- |
| `domain` | Task, acceptance, states, attempts, results and policies |
| `orchestration` | Role selection, dependencies and passage gates |
| `storage` | SQLite transactions, events, artifacts and state migrations |
| `agent_adapters` | Selected client, I/O, cancellation, capabilities and exposed usage |
| `stack_adapters` | Component commands, environment, timeouts and execution evidence |
| `workspace` | Isolated worktree, lock and revision/diff fingerprint |
| `observability` | Sanitized logs and run/task/role/attempt identifiers |
| `delivery` | Separate PR, CI, merge and deploy operations under project policy |
| `cli` | Validate configuration/tasks, run, inspect and resume |

The initial code uses small modules: `contracts.py`, `executor.py`, `adapters.py`,
`processes.py`, `workspace.py`, `storage.py` and `cli.py`. `AgentAdapter` accepts
provider-neutral `Assignment`/`AgentResponse` values; only `CodexCLI` is wired into
the CLI today. Checks are configured argument lists rather than language SDKs.
SQLite is the concrete store; a replaceable storage interface and migrations are
future work. Remote delivery, telemetry exporters and plugin discovery are pending.

Commands use argument lists and explicit working directories. A subprocess alone
is not a sandbox; declare the actual isolation controls. Model settings and
credentials live outside prompts and skills.

## First end-to-end workflow

1. Validate a real task: repository, objective, acceptance, base revision, components and authorized actions.
2. Create an isolated workspace and persist execution/configuration before invoking agents.
3. Invoke the developer with its native profile, skill and bounded task context.
4. Validate structured results and execute the affected components' real checks.
5. Obtain QA and review evidence for the same revision/diff fingerprint.
6. Repair failures within configured limits, invalidating evidence after changes.
7. Deliver a verifiable diff/report; add PR creation and remote CI in the delivery increment.

This flow begins with a refined task. Executable PM/PO and product-discovery stages
follow; the roster alone does not automate the full SDLC. Deployment and operation
also need adapters and acceptance scenarios.

Persist each attempt's start/end, command/model, revision, output and evidence
references. A `running` step after a crash requires reconciliation, never automatic
success. Bounded retries check earlier external effects before repeating them.

## AI, data and costs from the start

Separate operational events from sensitive content. Preserve structured payloads,
contract versions, provenance and retention; do not log secrets or full prompts by
default. JSON logs can gain OpenTelemetry export later.

Effective configuration distinguishes infrastructure and AI. An unspecified AI
budget is not unlimited and does not authorize new kit spending. Support per-task
and per-attempt limits; where reliable prices/usage exist, reserve estimates before
calls and reconcile observed consumption. Clients without measurements need
call/time limits and `unknown` reporting, which is not a provider billing hard stop.

## Executor acceptance

- A real authorized task passes implementation, checks, QA and review.
- Invalid results, unavailable tools, failed tests and timeouts prevent completion.
- Restart reconciles state; changed diffs invalidate stale evidence.
- Limits terminate repair loops and keep failures visible.
- Python and Go components use their own commands without a Node requirement.
- Reports distinguish completed work, pending stages and unavailable usage.

Choose and verify the first adapter against the installed client version. An
existing CLI may avoid a new API integration, but still requires authentication,
noninteractive execution, structured results, cancellation and limits. Validate
those capabilities before relying on autonomous execution.

The implemented adapter uses Codex CLI 0.160.0 with existing ChatGPT login,
ephemeral noninteractive execution and structured results. This CLI has no agent
selector for `exec`; the adapter explicitly loads the generated TOML profile and
skill instructions. Automatic discovery remains a separate check. The normalized
JSON Schema is translated to the stricter native output format.
Implementation uses the client's `workspace-write` sandbox; QA/review use
`read-only`. Project check commands run as ordinary local subprocesses and must be
trusted. A worktree isolates changes but is not a security boundary.

## Extension and planning boundaries

Keep provider/client types behind adapters as described in [modular architecture](modular-platform.md).
The normalized result contract accepts extensible role IDs; the executor must resolve
them against its active registry. Planning artifacts do not authorize transitions.
Validate their authority, references and ready-task IDs before execution.
