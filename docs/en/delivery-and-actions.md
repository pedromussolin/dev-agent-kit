# Delivery, repositories and GitHub Actions

**Languages:** English | [Português (Brasil)](../pt-br/delivery-and-actions.md)

The kit is the reusable execution engine; `finance-management` is the product.
Keep product code, checks and deployment configuration with the product. Keep role
contracts, skills and executor implementations in `dev-agent-kit`. The private
[actions repository](https://github.com/pedromussolin/actions) owns independently
released reusable workflows; the first consumer, finance-management, is also private.

GitHub reusable workflows live in `.github/workflows/` and declare `workflow_call`.
A product caller can reference the shared Actions workflow at an immutable published commit.
This follows [GitHub's reuse model](https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows).
Both workflow and kit revisions are published and pinned in the caller template. `actions/.github/workflows/sdlc-executor.yml`
and [product caller template](../../templates/github-actions/product-sdlc.yml.template)
separate execution from product ownership.

## Activated delivery capabilities

| Task delivery mode | Completed boundary |
| --- | --- |
| `diff` | Isolated patch/report and independent local acceptance |
| `pull_request` | Owned branch and PR matching approved source |
| `merge` | PR + declared remote CI checks + matched-head merge |
| `deploy` | Merge + deployment command + smoke check, rollback on failure |

Select the mode explicitly in the real task. For remote delivery, pass a completed
[delivery configuration template](../../templates/delivery-config.json.template)
to `init --delivery deploy --delivery-config FILE`. Templates deliberately contain
invalid placeholders and cannot be executed as real tasks. The complete JSON task
records the GitHub repository, actual open issue, default branch, required check
names, merge method, bounded CI wait and environment commands.

Remote delivery requires clean committed input matching the actual default branch.
The executor makes a separate delivery worktree, commits only the accepted tree,
publishes its owned branch without force and verifies the PR head. It calls
`gh pr merge --match-head-commit` and does not bypass repository protections.
If the default branch moves, evidence must be renewed. Duplicate external effects
are reconciled against persisted state. Ambiguous merges/deploys remain visible.
Deployment fetches the actual merge commit and verifies its tree matches local
acceptance. Commands are argument arrays, not arbitrary shell text. `smoke_argv`
and `rollback_argv` are required; rollback outcome is recorded rather than assumed.

## Local-first execution

GitHub Actions is scheduling infrastructure, not the agent executor. For personal
use, a dedicated Linux self-hosted runner can invoke the kit, retain SQLite and
access an already authenticated local Codex client. No ChatGPT authentication file
is copied into this repository or Actions artifacts. Runner installation, account
login and its label are real environment prerequisites, not implemented by adding
YAML. Use only trusted manually started/default-branch tasks on this personal
runner. See [self-hosted runners](https://docs.github.com/en/actions/concepts/runners/self-hosted-runners).

The workflow uses per-product concurrency with `cancel-in-progress: false`, plus
executor locks and budgets. Store state outside disposable checkouts. Publish only
a selected sanitized run report when appropriate; provider artifacts and raw source
patches are not automatically uploaded. Job cancellation/process termination is
not proof of deployment rollback; interrupted effects require reconciliation.

A delivery token must have the necessary permissions for the product. GitHub App
installation tokens are the scalable choice; a narrowly scoped PAT is an alternative.
The default `GITHUB_TOKEN` changes workflow-trigger behavior: current documentation
requires approval for PR workflows it creates and suppresses other recursive events.
A suitable App/PAT avoids that extra PR CI approval when full automation is intended.
See [workflow triggering](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow).
On the trusted personal runner, `use-local-github-auth: true` uses the existing
local `gh` account without copying its credential into GitHub secrets. An App
installation token remains the recommended boundary before operating for clients.

## Infrastructure and boundaries

A local runner and monitor require no new cloud service; electricity/hardware and
account usage remain real costs. Cloud infrastructure keeps the BRL 100/month
policy, with a separate AI budget. Do not choose a cloud plan without checking its
complete cost and actual target requirements. The optional
[monitor Compose](../../compose.monitor.yaml) runs only the monitoring service;
product deployment commands remain product-specific.

The personal target is Docker on this host. The product uses a persistent local
D1 volume, an authenticated loopback gateway, verified SQLite backups and image
rollback. Its integration is tracked by actual product issue #1. CI and agent
execution require two separate runner processes to avoid a job waiting for CI
while holding its only worker. Operate the registered private runners with:

```bash
python3 scripts/local_runners.py start finance-sdlc finance-ci
python3 scripts/local_runners.py status finance-sdlc finance-ci
python3 scripts/local_runners.py stop finance-sdlc finance-ci
```

Registration and the persistent Python environment live outside repositories in
`~/.local/share/dev-agent-kit`. This launcher is a user process, not a boot service;
start it again after reboot. It requires a private product repository. Local
integration tests exercise actual Git and deployment processes with controlled
GitHub I/O; they are not proof of production publication. Multi-repository tasks
already select their own repository/project ID. Do not split runtime code merely
for appearance: extract a service or Actions repository when separate releases,
ownership or consumers justify it.

## Personal activation prerequisites

The first private consumer is connected to Actions revision
`3f4cfeb8a0e363d237dd6d117d7422b941189667` and kit revision
`ab4c21894e61e3aca09575cf237e50a154955478`. The registered local runners use
GitHub Runner 2.337.0, GitHub CLI 2.102.0 and the persistent Python environment.
The account credential remains in its existing local store. Publishing workflow
changes uses the already configured SSH identity; its OAuth token lacks workflow
scope and is sufficient for ordinary delivery/API operations. Earlier CI failed
on a reused utility directory; each job now clones into its unique runner temp
directory. Both push and PR checks must pass when they share a required name.

Run the launcher from the actual host terminal: its PID identity check uses that
host Linux process namespace. A stopped status from another container namespace
does not establish that the host runner stopped. Confirm connectivity through
GitHub runner status. Agents start only through an explicit manual task request;
there is no recurring model usage. A completed task with a closed issue cannot
be submitted again without a new valid scope/issue.
