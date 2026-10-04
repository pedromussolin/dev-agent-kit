# Logical pipelines, quality and data boundaries

**Languages:** English | [Português (Brasil)](../pt-br/current-increment.md)

This increment extends the existing local executor and the accepted private product delivery. See [historical agent evaluations](agent-validation.md) for actual model-run evidence; the new deterministic checks do not certify every role.

## What is implemented

- A logical phase model independent of GitHub. Explicit `phase`/`phase_label` metadata takes precedence. Recognizable adjacent operations are grouped by responsibility; unknown work stays visible with its original name. Order and job boundaries are preserved. There is no mandatory list of UI phases.
- A separate browser renderer, dashboard controller and stylesheet. The summary shows responsibility, status, duration and failure. Collapsed details expose source operations, argument arrays and sanitized logs. Native details controls support keyboard interaction. Untrusted text uses DOM `textContent`.
- Executor progress persists completed checks while the check stage is still running. HTTP and MCP read the same injectable `MonitoringRepository`; SQLite-specific queries remain in the concrete adapter. An executor store factory supplies a persistence extension point, not an already implemented PostgreSQL backend.
- GitHub run snapshots imported by an authorized host CLI. Timed logs are attributed to source steps. Structured check events unfold a single GitHub action into observed quality/test/build responsibilities. Unknown conclusions do not imply success. Last synchronization is shown; snapshots are not continuous GitHub polling.
- Three additional selectable roles: Code Improver (`code-improver`), Code Reader (`code-reader`) and Incident Analyst (`incident-analyst`). The current catalog contains 29 roles, 31 canonical skills and 87 native role profiles; packaging checks 333 managed files. Selecting a role does not start a daemon or grant more permissions.
- Ruff lint/format gates for Python; Prettier for the monitor. The finance product additionally runs ESLint, Prettier, TypeScript checks, unit/security tests and MCP protocol checks in shared CI. Vendored UI sources retain their existing scoped exceptions.
- An official SDK MCP stdio server for the kit and a finance HTTP-to-MCP adapter. The kit exposes public evidence, without shell/SQL/model/deploy tools. Cancellation is registered only with `--allow-control`. Finance is read-only unless launched with `--allow-write`; writes use API validation and expected revision.
- Finance persistence through a typed repository and Drizzle D1 adapter, preserving parameter binding, user isolation and optimistic concurrency. The Worker accepts domain operations, not arbitrary query text. No additional database is provisioned.
- Check subprocesses have time/output limits and POSIX process-group cleanup. Failed checks mark subsequent checks skipped. Public evidence uses heuristic redaction; this is not a guarantee for every secret format.

## Why these boundaries

The domain defines what can be done; adapters define how. SQLite belongs in a SQLite adapter, just as D1 belongs in a D1 adapter. An `import sqlite3` in that concrete layer is an implementation choice. HTTP handlers, MCP tools and domain callers should not construct query text. Injection prevention depends on parameter binding and controlled identifiers even when an ORM is used. Reviewed fixed migrations remain SQL.

Data-first means defining ownership, schema, identity, validation, retention, migrations and recovery before adding storage. The current small finance snapshot fits typed JSON in a relational table. Split frequently queried entities when query/reporting requirements justify it. A document database or object store needs an explicit access pattern and consistency/backup plan; storing an object does not automatically require another database.

The finance frontend (`app/`) talks to the backend (`worker/`) over its HTTP contract; persistence is under `db/`. They currently share a repository and release build. Separate repositories/services when independent ownership or release cycles justify them, retaining contract tests and MCP parity. React is the product's existing stack, not a kit-wide requirement. The small monitor uses modular HTML/CSS/JavaScript without imposing a product framework on Python/Go projects.

Skills are focused instructions, roles assign responsibility, native profiles adapt provider formats, and tools supply real capabilities. Keep canonical sources once and regenerate provider files; avoid copying personal context into these shared instructions. Load only relevant roles/skills so a small task does not pay for the full roster. Incident learning prefers a demonstrated regression test or scoped rule with ownership and false-positive analysis over an automatic new agent for every error.

## Test without spending model tokens

From the kit checkout with Python 3.11+:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[monitor,test,browser]'
.venv/bin/python scripts/provider_profiles.py --check
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m playwright install --with-deps chromium
PYTHONPATH=. .venv/bin/python tests/browser/check_monitor.py
```

The browser test uses temporary state, fixture data and an ephemeral local monitor. It verifies grouping, all statuses, error placement, duration, details, language, mobile width and log XSS prevention. It does not modify real finance data. CI repeats it on Python 3.12; the core suite runs on 3.11/3.12/3.13.

In finance-management, use the declared Node/pnpm toolchain:

```bash
pnpm install --frozen-lockfile
pnpm quality
pnpm test
pnpm build
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
.venv/bin/python -m unittest discover -s tests -p 'test_*.py' -v
```

In `actions`, install Ruff 0.16.10, then run `ruff check .`, `ruff format --check .` and `python3 -m unittest discover -s tests -v`. These commands validate code/transport behavior; they do not invoke models or deploy.

## View a real GitHub pipeline

Use a real run ID in the host checkout, with `gh` already authenticated to that repository:

```bash
.venv/bin/python -m dev_agent_kit sync-workflow --repository OWNER/REPOSITORY --run-id REAL_RUN_ID --logs
```

The default state is `~/.local/state/dev-agent-kit`, the same directory used by the local monitor. The importer bounds each API command to 30 seconds/2 MB and rejects runs over 20 jobs instead of silently importing a subset. Logs are optional and may contain private application information despite redaction; synchronize only authorized runs. The Docker monitor does not receive GitHub credentials.

A producer may declare any responsibility:

```json
{"name":"risk-report","phase":"risk-analysis","phase_label":"Assess portfolio","argv":["python","scripts/risk_report.py"],"timeout_seconds":120}
```

Existing checks without phase metadata continue working. Matching phases separated by other work remain separate cards, preserving execution order. Phase duration sums observed operation time; unavailable historical timings show a dash, and jobs are kept separate rather than pretending parallel time is sequential.

## MCP startup and client configuration

After installing the `mcp` extra, run the kit server with an absolute interpreter path and checkout working directory:

```bash
.venv/bin/python -m dev_agent_kit --state-dir /ABSOLUTE/PRIVATE/STATE mcp
```

For finance, launch its script using the Python environment with `requirements-dev.txt` installed. The local product must be running and its private Basic password file must exist:

```bash
.venv/bin/python scripts/finance_mcp.py --base-url http://127.0.0.1:8787
```

See [the configuration example](../../examples/mcp/servers.json). Replace absolute paths for your environment and add only the desired entries to your client's existing MCP settings. Configuration formats differ by client; do not overwrite unrelated provider settings. Servers are launched on demand through stdio. MCP has no HTTP password here: access is determined by the local process/user and selected state/credential paths. Tool annotations describe behavior; actual write/control access is enforced by tool registration and the existing API. Personal financial data belongs only in an explicitly authorized private MCP session.

## Personal context and remaining work

Private life Markdown resides outside software repositories. Its contents are not loaded automatically by agents, the monitor or MCP. Keep document extraction private, cite file/page sources, distinguish reported facts from assumptions and review budgets/goals before turning them into tasks.

Still required for a broader autonomous platform: real-task evaluation of the remaining 26 roles, Claude/Copilot execution adapters, a tested alternative persistence adapter, plugin loading/capability negotiation, scheduled planning-to-backlog execution, durable runner startup, provider billing enforcement and database restore drills. PostgreSQL/Grafana/Loki/AI telemetry remain optional profiles, not services started by this increment. Current hosting remains local; the infrastructure cloud cap is BRL 100/month and AI budget is separate. This increment introduces no paid model evaluation or new cloud service.
