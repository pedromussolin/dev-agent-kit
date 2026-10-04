# Local platform, data, AI and budgets

**Languages:** English | [Português (Brasil)](../pt-br/local-platform-and-ai.md)

Requirements: initially local execution; optional personal cloud hosting capped
at **BRL 100/month total infrastructure cost**; a separate AI budget whose amount
is still unspecified. The [canonical policy](../../policies/project-defaults.json)
is bundled with every skill. Official sources were consulted on 2026-10-03.
This change does not install or provision any service.

## Recommended tools and adoption order

Choose maintained stable tools that match the requirements. Verify compatibility,
licensing and release stability before pinning project versions, lockfiles or
container image digests. Activate services only when useful.

| Need | Recommendation | Adoption rationale |
| --- | --- | --- |
| Executor state | SQLite, persisted events and JSON logs | First increment: low service overhead, inspectable local recovery |
| Local services | Docker Compose | Reproducible optional database and telemetry profiles |
| Application database | PostgreSQL | Shared relational workloads when appropriate; existing project stacks still apply |
| Database administration | DBeaver Community | Schema inspection and queries with minimum required access |
| Searchable logs | Grafana + Loki + Alloy | When local log files no longer support investigation; bound volume and retention |
| Metrics and instrumentation | Prometheus + OpenTelemetry | Measure failures, duration and resources; avoid high-cardinality prompt-text labels |
| Traces | Tempo, optional | When cross-operation correlation is useful |
| AI observability | Langfuse, optional | When prompt/version comparisons and traces justify extra dependencies |
| AI evaluations | Project tests; promptfoo when useful | Reproducible comparisons of model, prompt and tool quality/cost |
| Local models | Ollama, optional | After measuring hardware needs, quality and latency |
| Vector search | pgvector, optional | Only for a demonstrated semantic retrieval requirement |
| Cloud infrastructure | OpenTofu | When needed: versioned, reviewable infrastructure declarations |

Compose manages multi-service applications; OpenTelemetry instruments logs,
metrics and traces; DBeaver Community is an open database administration tool.
See [Compose](https://docs.docker.com/compose/),
[OpenTelemetry](https://opentelemetry.io/docs/), [DBeaver](https://dbeaver.io/),
[Loki](https://grafana.com/docs/loki/latest/setup/install/docker/),
[Alloy](https://grafana.com/docs/alloy/latest/),
[Prometheus](https://prometheus.io/docs/introduction/overview/),
[Tempo](https://grafana.com/docs/tempo/latest/),
[PostgreSQL](https://www.postgresql.org/docs/current/pgstatstatements.html),
[pgvector](https://github.com/pgvector/pgvector),
[promptfoo](https://www.promptfoo.dev/docs/intro/),
[Ollama](https://docs.ollama.com/) and [OpenTofu](https://opentofu.org/docs/).

SQLite stores kit execution state; it does not dictate application storage.
A DBA can examine PostgreSQL query statistics before recommending indexes.
Schema changes and live database access follow the task scope and project policy.

Langfuse's deployment includes PostgreSQL, ClickHouse, Redis/Valkey and object
storage. It is consequently excluded from the minimal profile. Intelligent
operations still require evidence and authorization for any automated repair.
[Langfuse architecture](https://langfuse.com/self-hosting#architecture).

## Local and cloud within the cap

Local hosting runs the executor and services on your machine. Model inference may
remain remote, depending on the client/provider, and is accounted for separately.
Local open software still consumes hardware, electricity and maintenance time.

Evaluate a hybrid option first: local executor/database with sanitized telemetry
in Grafana Cloud's free plan. Current allowances include 50 GB of ingested logs
per month, 14-day retention and 10,000 active metric series. Pro starts at
USD 19/month plus usage; compatibility with the BRL cap must not be assumed.
Recheck the terms before adoption. [Grafana pricing](https://grafana.com/pricing/).

A small VPS is another conditional option. Hetzner's price adjustment effective
2026-06-15 lists CX23 at EUR 5.49/month in Germany/Finland excluding IPv4 and VAT. That is
one price line, not a total-cost guarantee or a provider selection.
[Official adjustment](https://docs.hetzner.com/general/infrastructure-and-availability/price-adjustment/).

| Cost item | Required evidence |
| --- | --- |
| Compute, database, observability | Plan, region, quantity, official price and date |
| Disk, backup, traffic, billable IP | Expected volume, retention and applicable charges |
| Currency and fees | BRL conversion, taxes and payment fees |
| Free allowances | Quota, behavior at the limit and no automatic paid upgrade |
| Monthly total | Expected/growth scenarios within BRL 100 |

A suggested BRL 20 planning reserve leaves a BRL 80 target estimate. This is a
recommendation, not an additional user-imposed cap. Missing usage/prices make a
proposal incomplete; financial alerts alone do not guarantee a billing hard stop.

## Data-first and AI-first practices

Data-first starts with schemas, ownership, quality, provenance, privacy, retention
and recovery. Record which data was used and which checks passed. Retrieval,
vector stores and distributed pipelines require a demonstrated use case.

AI-first evaluates AI in product and tool design through structured results,
bounded tool use, evaluations and fallback. Deterministic operations remain the
baseline when they deliver the outcome reliably and cheaply. For example, a model
plans a change while actual tests and schema validation establish acceptance.

| New role | Expected deliverable |
| --- | --- |
| AI Strategist | Opportunities, baseline, roadmap and investment criteria |
| AI Engineer | Evaluated model/tool/retrieval integrations |
| Context Engineer | Role-specific context and versioned quality/cost comparisons |
| Data Engineer | Ingestion, contracts, quality, provenance and recovery |
| LLM Evaluation Engineer | Quality, safety, latency and cost regression cases |
| MLOps Engineer | AI versions, delivery, monitoring and rollback |

DBA owns storage/query behavior while data engineering owns flows/contracts. QA
checks product acceptance while LLM evaluation checks probabilistic behavior.
MLOps adds AI-specific versions and gates to DevOps delivery. Select the relevant
responsibilities rather than activating all 26 agents for every task.

## Evidence-based token savings

1. Select relevant source excerpts and pass referenced role-specific summaries.
2. Use deterministic discovery/check tools and send only useful outcomes to models.
3. Bound attempts, tool calls, context size and elapsed time.
4. Evaluate cheaper models by task category, with justified escalation.
5. Use provider/model-specific caching and invalidate stale code/data artifacts.
6. Measure cost per accepted task, including retries and evaluator-model calls.

Cache and usage capabilities vary across clients/models; unavailable usage is
`unknown`, not zero. Consult [prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching)
and [evaluation best practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices).

Do not promise a savings percentage. Distinguish observed, estimated and unavailable
measurements; record model, prompt/data versions, exposed input/output/cache tokens,
latency, attempts and quality. Policy consistency is checked during packaging;
the local executor enforces call/time/context limits and records exposed token
usage with unknown monetary cost. Provider billing caps, model selection and
comparative optimization evaluations remain future work.

See the [executor decision](executor-decision.md) and [operating guide](local-executor.md).
