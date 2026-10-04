# Local executor operations

**Languages:** English | [Português (Brasil)](../pt-br/local-executor.md)

Version 0.2 runs a configured sequence of planning roles → implementation → actual
checks → verification roles → delivery. Developer, QA and technical reviewer form
the default flow. All 29 registered roles can be selected; one implementation stage
and both QA and review remain mandatory. Delivery can create a PR, wait for remote
CI, merge and deploy according to the task. See [delivery and Actions](delivery-and-actions.md).

## Prepare the environment

Use Python 3.11+, Git worktrees and a POSIX host. Retain a kit source checkout: the
wheel contains the runtime/dashboard, while contracts, profiles and skills remain
repository resources. `--kit-root` selects those resources; it does not change
Python's import path. State must reside outside the target repository.

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e '.[monitor,test]'
python3 scripts/provider_profiles.py --check
python3 -m unittest discover -s tests -v
codex --version
codex login status
python3 -m dev_agent_kit --help
```

The adapters use existing ChatGPT authentication (`ai_spending:
existing_chatgpt_account`) and reject nonempty `OPENAI_API_KEY`/`CODEX_API_KEY`.
No API credentials are provisioned. The installed client was tested at 0.160.0.
`codex-app-server` supplies live activity and cumulative token updates; the installed
CLI labels its app-server command experimental. Its adapter is isolated behind
`AgentAdapter`; compatibility must be revalidated after client updates.
`codex-cli` remains available, with token usage observed only after a completed
assignment. Neither adapter is a monetary provider billing cap.

Prepare the target project's actual check dependencies separately. The executor
never installs them or recreates ignored environments. Check commands inherit the
host environment and run as trusted local subprocesses, without a shell. A Git
worktree is change isolation, not a security sandbox. The model's developer uses
`workspace-write`, planning/verification use `read-only`; network access is disabled
in the app-server tool sandbox. Host check/deployment commands have their declared
authority and need their own isolation when handling untrusted projects.

## Describe and initialize a task

Replace project paths, IDs, goals and checks with actual values:

```bash
python3 -m dev_agent_kit inspect /ABSOLUTE/PATH/TO/PROJECT
python3 -m dev_agent_kit init /ABSOLUTE/PATH/TO/task.json   --repository /ABSOLUTE/PATH/TO/PROJECT   --task-id ACTUAL-LOCAL-TASK-ID --goal 'Your concrete acceptance goal'   --allow 'src/specific-file.py' --context README.md   --check 'python3 -m unittest discover -s tests -v'
```

`inspect` reads root manifests and suggests checks; it does not execute or install
anything. Multi-language components remain independent. `init` creates a new real
task file exclusively, records the full current commit and fills bounded defaults.
Review acceptance criteria, component checks, scope and authorization before `run`.
A local task ID is not a GitHub issue; remote delivery requires a real open issue.

The authoritative [task schema](../../contracts/execution-task.schema.json) rejects
unknown keys. Context/scope/check directories must stay within the project, without
symlinks, `..`, absolute paths or `.git`. Narrow allowed path patterns are required.
Commands are argument arrays; `--check` splits quoting but does not interpret shell
operators. Select existing project toolchains: Python, Go, JS, Rust or others.

`workflow` optionally contains named `{name, role_id, kind}` steps. Use `plan` for
read-only specialists before implementation, exactly one `implement` step and
`verify` for independent specialists after checks. Include `qa-engineer` and
`technical-reviewer`. Increase the explicit call budget only when the chosen roles
require it. Every extra role consumes account usage; the full company roster should
not run for every small bug. A planning round is a bounded pass through selected
roles, not an infinite discussion or background scheduling service.

## Validate, execute and inspect

Run these from the kit checkout, replacing the task/run placeholders:

```bash
KIT_ROOT="$PWD"
STATE_DIR="$HOME/.local/state/dev-agent-kit"
TASK_FILE="/ABSOLUTE/PATH/TO/task.json"
python3 -m dev_agent_kit --kit-root "$KIT_ROOT" --state-dir "$STATE_DIR" validate "$TASK_FILE"
python3 -m dev_agent_kit --kit-root "$KIT_ROOT" --state-dir "$STATE_DIR" run "$TASK_FILE"
RUN_ID="<RUN_ID_FROM_RUN_OUTPUT>"
python3 -m dev_agent_kit --kit-root "$KIT_ROOT" --state-dir "$STATE_DIR" status "$RUN_ID"
python3 -m dev_agent_kit --state-dir "$STATE_DIR" runs
python3 -m dev_agent_kit --state-dir "$STATE_DIR" watch "$RUN_ID"
python3 -m dev_agent_kit --state-dir "$STATE_DIR" cancel "$RUN_ID"
```

`validate` proves format/path validity, not runtime readiness or acceptance. `run`
performs auth/tool/delivery preflight and snapshots authorized inputs. Terminal
progress goes to stderr; final structured output goes to stdout. `--quiet` suppresses
progress, while `watch --json` streams public events for other consumers.

The monitor uses the same state and shows assignments, stages, public commentary,
usage, limits, delivery effects and cancellation:

```bash
python3 -m dev_agent_kit --state-dir "$STATE_DIR" serve
```

Open `http://127.0.0.1:8765`. The UI supports English/Portuguese. SSE resumes by event
ID and SQLite WAL permits monitoring while a run holds its execution lock. Raw
commands, tool output, prompts and private reasoning are not published in the
public timeline. Public comments/results are sanitized heuristically; do not treat
redaction as a formal guarantee for arbitrary secrets. Bind nonlocal interfaces
only with `DEV_AGENT_KIT_MONITOR_TOKEN`; the browser uses HTTP Basic authentication.
The shipped Compose option publishes only on host loopback.

## Limits and recovery

Persisted limits cover assignments, attempts, total elapsed time, context size,
tool calls, identical tool outcomes without source change, inactivity, per-agent
observed tokens, total run tokens, UTC-day project tokens/calls and repeated failed
repairs with no progress. Calls are reserved before invocation. Usage is recorded
before the guard interrupts. Resume and new runs in the same project/state cannot
reset the daily ledger. Project IDs must remain stable; separate state stores are
separate accounting domains. Historical v0.1 calls are not backfilled into this
ledger. Unknown usage is reported and still bounded by calls/time/tools.

App-server interruption occurs when reported cumulative usage reaches a configured
threshold. In-flight work may overshoot; this is not an exact token reservation or
provider quota. CLI usage arrives at completion and therefore stops subsequent
assignments rather than guaranteeing a live token stop. Cached input counts toward
observed usage. `cost_brl` remains unknown unless actual cost evidence exists. The
BRL 100/month infrastructure policy excludes the separate AI budget and does not
purchase services or enforce cloud billing automatically.

Read `$STATE_DIR/runs/$RUN_ID/report.json`, `task.patch`, check results and error
categories before resuming. QA/review must refer to the same source fingerprint as
checks. Changed content or HEAD invalidates evidence; kit/configuration changes
block resume. Retry artifacts have unique attempt/stage/call directories.

```bash
python3 -m dev_agent_kit --kit-root "$KIT_ROOT" --state-dir "$STATE_DIR" resume "$RUN_ID"
```

A current success returns without new assignments. Remote CI failures can reuse
accepted local evidence when the source remains identical. Ambiguous implementation
or external effects require inspection. Cancelled work, loops and exhausted budgets
require an explicitly revised task; resume does not silently reset limits. Deployment
failures execute the configured rollback and retain its actual outcome; ambiguous
or failed deploys are not blindly repeated.

`run`/`resume` return zero only on success. `status` returns zero for successful
inspection even when the reported run failed; read its status/error. Retained files
or an agent's success claim are not proof of completed delivery. Automatic client
skill discovery, distributed workers, autonomous product backlog scheduling and a
manifest-based plugin loader remain separate integrations. See [validation](agent-validation.md).
