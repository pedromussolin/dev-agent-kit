# Code quality, data and API contracts

Apply this rule when changing owned code, database boundaries or application APIs.

## Quality gates

Use the project's declared formatter, linter, type checks and meaningful tests. Add missing check commands to the actual CI/task configuration when in scope; instructions alone are not an enforced gate. Verification uses read-only modes (`--check`, not automatic formatting). Report missing tools as unverified. Preserve explicitly vendored/generated sources and their documented ownership. Keep diffs readable and explain behavioral changes separately from bulk formatting.

## Data and query safety

Define ownership, identity, schema/validation, access patterns, versioning, retention and recovery before choosing storage. Keep driver imports and query construction inside concrete persistence adapters. Prefer typed repository operations for domain callers. Bind all external SQL values; allowlist dynamic identifiers. ORM raw-query functions require the same security review. Do not expose arbitrary SQL through HTTP/MCP. Reviewed fixed migrations and parameterized adapter SQL are supported. Verify user/tenant isolation and concurrency for affected paths.

Use relational JSON, documents, object storage or references according to actual queries and consistency needs. A second storage system must justify its operations, cost, backup and consistency model; objects alone do not justify NoSQL.

## HTTP and MCP parity

Application API capabilities need an MCP adapter sharing their domain/service or authenticated API contract. Define transport, capability scope, input/output/error contracts and credentials. Enforce mutation authority in code, not tool annotations or prompt wording. Bound time, result sizes and tool exposure. Do not register financial/personal context tools into unrelated sessions. CI utility repositories without an application API do not need an artificial MCP server.

## Architecture and learning

Keep presentation, API, domain and persistence responsibilities distinct. Separate repositories when ownership or release cadence warrants it; test contracts across boundaries. Choose maintained project-fit technologies from verified requirements instead of imposing a universal stack.

For a demonstrated incident, prefer a focused regression, validation or runbook. Reusable rules need applicability, evidence, owner and a verification method. Use Code Reader for a bounded evidence map, Code Improver for scoped refactors/measured optimization, and Incident Analyst for failure investigation when those responsibilities are useful. Do not add every role to every task.
