# Modular platform and product evolution

**Languages:** English | [Português (Brasil)](../pt-br/modular-platform.md)

Recommended direction: a **modular monolith with replaceable interfaces**, initially
one local process. Explicit contracts and configured integrations support technology
changes and growth while keeping personal operation and infrastructure cost manageable.

## Decoupling responsibilities

The domain defines tasks, decisions, policies, attempts and evidence without importing
model SDKs, database clients or GitHub APIs. Ports define contracts; adapters connect
technologies to those contracts. This is the ports-and-adapters architecture pattern.

For example, the workflow calls an agent adapter's `execute(Assignment)`. A Codex or
Claude adapter translates inputs and normalizes outputs. Workflow gates remain stable,
but substitution still requires capability checks and behavioral evaluations.

| Replaceable boundary | Expected contract | Proposed initial implementation |
| --- | --- | --- |
| Agent | Assignment execution, cancellation, capabilities and exposed usage | One validated local client |
| Stack | Component checks with commands, outputs and revision evidence | Explicit Python/Go/other commands |
| State | Persist/query transitions and reconcile attempts | Transactional SQLite |
| Delivery | PR/CI operations, separate merge/deploy operations | Diff/report and configurable GitHub delivery |
| Telemetry | Sanitized correlated events | Local JSON with optional exporters |
| Tool | Typed arguments and validated results | Function, CLI, MCP or HTTP as appropriate |
| Profile format | Canonical roles/skills to native files | Separate Codex/Claude/Copilot renderers, implemented |

The local runtime implements `AgentAdapter` with `CodexCLI`, explicit component
commands, SQLite state and diff delivery. Storage is concrete rather than an
injectable port; remote delivery and telemetry exporters remain planned.
The packager already accepts injected profile
renderers through its Python interface while retaining export/conflict controls. Its
CLI supports the three known providers; arbitrary manifest-based loading is pending.

## Plug and play through explicit contracts

The [extension manifest](../../contracts/plugin-manifest.schema.json) is a proposed
internal kit contract: ID/version, kind, protocol version, capabilities, implementation,
permissions, contracts, configuration and conformance evidence. It is neither a native
provider requirement nor a universal installer.

Proposed lifecycle: explicit registration → compatibility → validated configuration →
permitted access → functional checks → activation. Missing required capabilities block
a task. Optional fallback is documented. A manifest does not grant access or prove
conformance.

The [Python adapter example](../../examples/plugins/example-python-checks.json) is
inert: its module and `kit://proposed/` contracts do not exist. It supports design
review; a future loader must reject it until bindings and evidence are resolved.

MCP standardizes external client/server tool communication. Configuration, access,
normalization and SDLC orchestration remain kit responsibilities.
[Official specification](https://modelcontextprotocol.io/specification/2026-07-28).

## Incremental scaling

1. **Personal use:** one task at a time, local modules, persistent state and verified recovery.
2. **Multiple projects:** project/run IDs, separate configuration, workspaces and limits; no global credentials in prompts.
3. **Concurrency:** bounded workers/queues and resource locks when measured demand justifies them.
4. **External users:** identity, data/secret/quota isolation, audit, export and support before onboarding customers.
5. **Commercial operation:** per-customer metering, plans, billing and availability/recovery objectives with a separate cost model.

Identify projects/runs in initial artifacts and isolate storage/model/delivery interfaces.
Multiuser hosting is not required yet. SQLite-to-PostgreSQL or worker extraction still
requires migrations and equivalence checks despite stable interfaces.

BRL 100 applies to personal infrastructure. A commercial service needs explicit
budgets and per-customer costs. Extension languages do not determine project languages;
processes, MCP and HTTP can connect different implementations.

## Evidence before monetization

Measure accepted tasks, time saved, costs, rework and reliability in personal use.
Then identify a repeatable problem and the outcome a customer would pay for.
Compare a distributable kit, assisted service and managed SaaS separately.

Before commercial distribution, choose a kit license and review dependency rights,
provider terms, data handling and costs. This checkout currently has no explicit
license; this change does not select one automatically.

Reliable results and useful integrations establish product value. A large agent
roster alone does not. See [planning governance](planning-governance.md) and
[provider readiness](provider-readiness.md).
