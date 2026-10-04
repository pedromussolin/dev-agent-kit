# Local executor and agent validation

**Languages:** English | [Português (Brasil)](../pt-br/agent-validation.md)

## Private product delivery acceptance

The [product evaluation](../../evaluations/finance-management-delivery.json) records
the real private finance-management task: developer, seven product tests,
TypeScript/build, independent QA/review, PR #4, both required CI checks, matched-head
merge and authenticated local Docker smoke all passed. The three roles reported
232,410 observed tokens against a 250,000 run threshold, with no retry. Each stayed
below its 100,000 role threshold. Monetary cost remains unknown. This verifies
the scoped GitHub delivery path; it does not certify the other 23 roles, provider
billing limits, Claude/Copilot runtime or autonomous meeting/backlog scheduling.

## Version 0.2 code task and limits

The [code evaluation](../../evaluations/codex-actions-code-task.json) records the
actual `actions` runner defect: an invalid later executable/argument could fail
after an earlier command had side effects. Developer fixed validation, actual
process tests passed, and independent QA/review accepted the same fingerprint.
Three assignments reported **237,190 total tokens** including cached input, under
the configured 250,000 run threshold. Per-role totals were 97,087 / 78,904 / 61,199.
The model reported `gpt-6.1-sol`; monetary cost remains unknown. Resume preserved
three calls before later kit changes. This is an actual small code case, not a
like-for-like savings comparison with the older documentation task.

A [live guard evaluation](../../evaluations/codex-live-token-stop.json) also stopped
an assignment at 123,411 observed tokens against a 100,000 threshold. An in-flight
request overshot; partial code remained unaccepted. Further bounded attempts,
including an operator cancellation and a context-size failure before QA inference,
remain failed/cancelled in SQLite. No failure was relabeled as a successful task.

The current kit suite has 68 passing tests, including actual Git/deploy processes
with controlled GitHub I/O, real protocol subprocess interruption and HTTP/SSE
monitoring. Stack discovery's 12 tests pass; the interrupted broad stack task is
not presented as a completed three-role evaluation. The other 23 live roles and provider billing hard caps remain unevaluated.

The following sections preserve the v0.1 evaluation. Their 31-test count and
limitations describe that original runtime. Historical success resumes require
the original kit/configuration fingerprint; current kit changes block resume.

Evaluated on 2026-10-04 with Python 3.12.3 and Codex CLI 0.160.0. The
[evaluation record](../../evaluations/codex-real-task.json) preserves measured
results and limits. This is a scoped first acceptance case, not certification of
the complete SDLC or all 26 roles.

## What passed

| Check | Result |
| --- | --- |
| Unit/integration suite | 31 tests passed; actual Git worktrees, subprocesses and SQLite, with controlled provider I/O |
| Generated profiles/resources | 306 files consistent across Codex, Claude Code and Copilot |
| Live task | Developer → checks → QA → technical reviewer succeeded with existing ChatGPT login |
| Revision binding | QA and review accepted the same final source fingerprint |
| Recovery of current success | `resume` returned success with agent assignments still at 3 |

The real local task is
[`executor-runbook-handoff`](../../examples/execution/executor-runbook-handoff.json).
It refined existing bilingual operating-guide drafts, added the first-run
checklists and checked their factual behavior against the implementation.
Implementation used `workspace-write`; QA/review used `read-only` and inspected
the actual check evidence. All three assignments produced valid structured
results without blocking findings.

The deterministic checks executed CLI help, guide acceptance and all 31 regression
tests. The integration suite separately covers failing checks, bounded repair,
invalid identity/results, stale reviews, unauthorized writes, unavailable tools,
timeouts, output limits, persistent call limits and ambiguous interrupted work.
This case validates documentation work; code-change behavior needs its own cases.
Actual Go execution was not tested because the toolchain was unavailable.

## Failures remain part of the evidence

Earlier executions of
[`executor-runbook-validation`](../../examples/execution/executor-runbook-validation.json)
failed. The managed parent sandbox prevented Codex configuration initialization;
an authorized host retry retained the child sandboxes. The provider then rejected
untyped `const`/`enum` nodes in the native output schema. Translation was corrected
and a regression test added, while the canonical contract stayed intact.

240-second assignments also timed out before their final structured result. Their
drafts were preserved and inspected. The new focused handoff task allowed 600
seconds per assignment, 2400 seconds overall and six assignments at most. Earlier
runs retained their original limits and failed status; they were not relabeled as
accepted. Stage history is retained in SQLite events; retry artifacts at the same
attempt/stage path may overwrite earlier files.

## Measured usage and next evaluations

The successful run reported **1,075,351 input tokens**, of which **889,088 were
cached**, and **11,590 output tokens**. These are the client's cumulative counts
across internal turns, not the size of one prompt. Reasoning output is reported
separately by the client; it is not added again to output totals. Usage from
interrupted invocations is unavailable, so these figures exclude earlier failures.
Monetary cost and the exact model ID were not exposed by the captured events.
They remain unknown; existing account access does not imply zero cost.

`max_agent_calls` counts **adapter invocations / Codex assignments**, not individual
model requests or tool calls inside an assignment. Time and input-character limits
bound execution; this increment has no token-level or monetary provider hard stop.
The measured context consumption warrants a narrower-context comparison while
holding acceptance quality constant. No token-savings claim is established yet.

The adapter explicitly loaded generated TOML instructions and the selected skills.
Automatic discovery, the other 23 roles, Claude/Copilot behavior, multiple models,
product planning, automated meetings, plugin loading and PR/CI/merge/deploy remain
outside this evaluation.

## Inspect the preserved run

From the source checkout with its dependencies available:

```bash
python3 -m dev_agent_kit status 08ac7c001f7646af95c099968c80946b
```

The default local state contains `runs/<run_id>/report.json`, `task.patch`, the
worktree, baseline and provider artifacts. The JSON evaluation also stores hashes
of the approved guide files. The run ID requires that retained local state; it is
not portable execution state. A different machine needs its own real task record.
See the [operating guide](local-executor.md) for setup and recovery boundaries.

After successful executor delivery, an operator rehearsal restored the previous
image, passed authenticated smoke, redeployed the accepted source and passed
smoke again. The named database volume remained attached; database migrations
were not reversed. Private online backup integrity passed before redeployment.
