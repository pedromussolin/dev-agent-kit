"""Drive a bounded implementation/check/QA/review workflow with persisted evidence."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import uuid

from .adapters import AgentAdapter, Assignment, CodexCLI, role_profile
from .contracts import ExecutionError, fingerprint, local_path, normalize_task, validate
from .processes import execute, safe_value
from .storage import Store
from .workspace import changes, current_revision, git, prepare
from .delivery import GitHubDelivery

ROLES = {"implementation": "developer", "qa": "qa-engineer", "review": "technical-reviewer"}


class Executor:
    """Keep workflow decisions independent of the selected provider implementation."""

    def __init__(self, kit_root: Path, state_directory: Path, adapter: AgentAdapter | None = None, delivery=None, on_event=None):
        self.kit_root = kit_root.resolve()
        self.store = Store(state_directory)
        self.adapter = adapter
        self.adapter_is_injected = adapter is not None
        self.delivery = delivery or GitHubDelivery()
        self.on_event = on_event
        self.result_schema = json.loads((self.kit_root / "contracts/agent-result.schema.json").read_text())
        roles = json.loads((self.kit_root / 'agents/catalog.json').read_text())['roles']
        self.profiles = {role['id']: role_profile(self.kit_root, role['id']) for role in roles}

    def close(self):
        """Close persisted state after a CLI command finishes."""
        self.store.close()

    def kit_fingerprint(self) -> str:
        """Invalidate resumption when executor code or loaded role resources change."""
        paths = list((self.kit_root / "dev_agent_kit").glob("*.py"))
        paths += [self.kit_root / "contracts/agent-result.schema.json", self.kit_root / "contracts/execution-task.schema.json",
                  self.kit_root / "policies/project-defaults.json"]
        catalog = json.loads((self.kit_root / "agents/catalog.json").read_text())
        for role in catalog["roles"]:
            if role["id"] in self.profiles:
                paths.append(self.kit_root / ".codex/agents" / f"{role['id']}.toml")
                for skill in role["skills"]:
                    paths.extend(path for path in (self.kit_root / ".agents/skills" / skill).rglob("*") if path.is_file())
        return fingerprint({path.relative_to(self.kit_root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths})

    def start(self, task: dict) -> dict:
        """Create a run with a real task record and an isolated, preserved worktree."""
        with self.store.locked():
            task = normalize_task(task, self.kit_root)
            repository = Path(task["repository"])
            if self.store.root.is_relative_to(repository):
                raise ExecutionError("invalid_state_directory", "Store run artifacts outside the project checkout")
            run_id = uuid.uuid4().hex
            directory = self.store.root / "runs" / run_id
            directory.mkdir(parents=True, mode=0o700)
            workspace = directory / "workspace"
            self.store.create(run_id, task, fingerprint(task), self.kit_fingerprint(), workspace)
            try:
                self._select_adapter(task)
                metadata = self.adapter.preflight()
                self._preflight_checks(task)
                self.delivery.preflight(task)
                revision = prepare(task, workspace, directory)
                with self.store.connection:
                    self.store.event(run_id, "workspace.prepared", {"input_fingerprint": revision, "adapter": metadata})
                self.store.status(run_id, "running")
                self._emit(run_id, {'type': 'started', 'message': 'Task workspace prepared', 'run_id': run_id})
                self._drive(run_id)
            except ExecutionError as error:
                self._fail(run_id, error)
            except (KeyboardInterrupt, SystemExit):
                self._fail(run_id, ExecutionError("interrupted", "Execution was interrupted; reconcile before resuming"))
                raise
            except Exception as error:
                self._fail(run_id, ExecutionError("executor_error", f"Unexpected executor failure: {type(error).__name__}"))
            return self.report(run_id)

    def resume(self, run_id: str) -> dict:
        """Reuse only current evidence and refuse ambiguous interrupted implementation."""
        with self.store.locked():
            run = self.store.get(run_id)
            try:
                if run["config_hash"] != fingerprint(run["task"]) or run["kit_hash"] != self.kit_fingerprint():
                    raise ExecutionError("configuration_changed", "Configuration or loaded kit resources changed; create a new run")
                workspace = Path(run["workspace"])
                if not (self.store.root / "runs" / run_id / "baseline.json").is_file():
                    raise ExecutionError("workspace_incomplete", "Workspace preparation did not finish; create a new run")
                stages = self.store.stages(run_id)
                implementation_names = {step['name'] for step in run['task']['workflow'] if step['kind'] == 'implement'}
                if any(stage['name'] in implementation_names and stage['status'] == 'running' for stage in stages):
                    raise ExecutionError("interrupted_implementation", "Implementation may have partial effects; inspect it before creating a new run")
                revision = current_revision(workspace, run["task"]["base_revision"])
                changes(workspace, self.store.root / "runs" / run_id, run["task"]["policy"]["allowed_paths"])
                if run["status"] == "succeeded" and run["verified_hash"] == revision:
                    return self.report(run_id)
                if run['status'] == 'cancelled' or (run.get('error_json') and json.loads(run['error_json']).get('category') in
                    {'loop_detected', 'tool_budget_exhausted', 'token_budget_exhausted', 'project_budget_exhausted', 'no_progress'}):
                    raise ExecutionError('reconciliation_required', 'Inspect stopped work and create an explicitly revised task; resume preserves budgets')
                self._select_adapter(run['task'])
                self.adapter.preflight()
                self._preflight_checks(run["task"])
                if any(stage['name'] in {'checks'} | {step['name'] for step in run['task']['workflow'] if step['kind'] == 'verify'}
                       and stage['status'] == 'succeeded' and stage['revision_hash'] != revision for stage in stages):
                    self.store.invalidate(run_id)
                self.store.status(run_id, "running")
                self._drive(run_id)
            except ExecutionError as error:
                self._fail(run_id, error)
            except Exception as error:
                self._fail(run_id, ExecutionError("executor_error", f"Unexpected resumption failure: {type(error).__name__}"))
            return self.report(run_id)

    def _remaining(self, run: dict) -> float:
        started = datetime.fromisoformat(run["created_at"])
        remaining = run["task"]["limits"]["max_run_seconds"] - (datetime.now(timezone.utc) - started).total_seconds()
        if remaining <= 0:
            raise ExecutionError("limit_exceeded", "Run deadline exhausted")
        return remaining

    def _select_adapter(self, task):
        if not self.adapter_is_injected:
            if task['agent']['adapter'] == 'codex-app-server':
                from .app_server import CodexAppServer
                self.adapter = CodexAppServer()
            else:
                self.adapter = CodexCLI()

    def _control(self, run_id):
        if self.store.cancelled(run_id):
            raise ExecutionError('cancelled', 'Execution cancelled by the operator')
        self._remaining(self.store.get(run_id))

    def _emit(self, run_id, event):
        event = safe_value(event)
        with self.store.connection:
            self.store.event(run_id, 'agent.' + event['type'], event)
        if self.on_event:
            self.on_event(event)

    def _preflight_checks(self, task: dict):
        for component in task["components"]:
            names = [check["name"] for check in component["checks"]]
            if len(set(names)) != len(names):
                raise ExecutionError("invalid_task", "Check names must be unique within a component")
            for check in component["checks"]:
                command = check["argv"][0]
                if "/" not in command and shutil.which(command) is None:
                    raise ExecutionError("tool_unavailable", f"Required check tool is unavailable for {component['name']}")
                if '/' in command:
                    executable = Path(command)
                    if not executable.is_absolute():
                        executable = Path(task['repository']) / component['working_directory'] / executable
                    if not executable.is_file() or not os.access(executable, os.X_OK):
                        raise ExecutionError('tool_unavailable', f"Required check executable is unavailable for {component['name']}")

    def _context(self, run: dict, revision: str, feedback: dict | None) -> dict:
        task = run["task"]
        workspace = Path(run["workspace"])
        directory = self.store.root / "runs" / run["id"]
        context = {"current_revision": revision, "base_commit": task["base_revision"], "feedback": feedback,
                   "checks": [], "context_files": {}, "task_patch": (directory / "task.patch").read_text() if (directory / "task.patch").exists() else ""}
        context['handoffs'] = []
        for relative in task["context_files"]:
            path = local_path(workspace, relative)
            if path.is_file():
                context["context_files"][relative] = path.read_text()
            else:
                raise ExecutionError("context_unavailable", "Required context file is missing")
        for stage in self.store.stages(run["id"]):
            if stage['attempt'] == run['attempt'] and stage['status'] == 'succeeded' and stage['name'] != 'checks' and stage['result_json']:
                result = json.loads(stage['result_json']).get('result', {})
                context['handoffs'].append({'role_id': result.get('role_id'), 'summary': result.get('summary', '')[:1500],
                                            'decisions': result.get('decisions', [])[:8]})
            if stage["attempt"] == run["attempt"] and stage["name"] == "checks" and stage["status"] == "succeeded":
                context["checks"] = json.loads(stage["result_json"])["checks"]
        # Large command logs remain inspectable in artifacts; model context stays bounded.
        for check in context["checks"]:
            check["stdout"] = check["stdout"][-6000:]
            check["stderr"] = check["stderr"][-2000:]
        if len(json.dumps(context)) > task["limits"]["max_context_characters"]:
            raise ExecutionError("limit_exceeded", "Assignment context exceeds its configured size")
        return safe_value(context)

    def _instructions(self, role_id: str) -> str:
        catalog = json.loads((self.kit_root / "agents/catalog.json").read_text())
        role = next(role for role in catalog["roles"] if role["id"] == role_id)
        text = self.profiles[role_id]
        text += "\n\nThe selected skill instructions and effective policy are included below. Use these supplied copies directly; do not read identical kit copies again. Project-specific instructions still apply.\n"
        for skill in role["skills"]:
            text += (self.kit_root / ".agents/skills" / skill / "SKILL.md").read_text() + "\n"
        text += "\nEffective kit defaults:\n" + (self.kit_root / "policies/project-defaults.json").read_text()
        return text

    def _agent_stage(self, run: dict, name: str, feedback: dict | None = None):
        task = run["task"]
        workspace = Path(run["workspace"])
        directory = self.store.root / "runs" / run["id"]
        revision = current_revision(workspace, task["base_revision"])
        step = next(step for step in task['workflow'] if step['name'] == name)
        role_id, kind = step['role_id'], step['kind']
        invocation_id = None

        def observed(event):
            if event['type'] == 'usage':
                self.store.observe_usage(invocation_id, event['usage'])
            self._emit(run['id'], {**event, 'role_id': role_id, 'stage': name})
            budget = self.store.budget(run['id'])
            if budget['run_tokens'] >= task['limits']['max_total_tokens'] or budget['project_tokens_today'] >= task['limits']['max_project_tokens_per_day']:
                raise ExecutionError('token_budget_exhausted', 'Run/project observed token threshold reached')
        assignment = Assignment(role_id, task, workspace, self._instructions(role_id), self._context(run, revision, feedback),
                                self.result_schema, min(task["limits"]["agent_timeout_seconds"], self._remaining(run)),
                                directory / f"attempt-{run['attempt']}" / name / f"call-{run['calls'] + 1}", kind == 'implement',
                                observed, lambda: self._control(run['id']))
        self.store.start_stage(run["id"], run["attempt"], name, revision)
        try:
            self._control(run['id'])
            invocation_id = self.store.reserve_call(run['id'], task['limits']['max_agent_calls'], task['limits'])
            self._emit(run['id'], {'type': 'assigned', 'role_id': role_id, 'stage': name, 'message': 'Agent assignment started'})
            response = self.adapter.execute(assignment)
            if response.usage:
                observed({'type': 'usage', 'usage': response.usage})
            validate(response.result, self.result_schema)
            if response.result["task_id"] != task["task_id"] or response.result["role_id"] != role_id:
                raise ExecutionError("invalid_result", "Agent result task or role identity differs from its assignment")
            after = current_revision(workspace, task["base_revision"])
            changed = changes(workspace, directory, task["policy"]["allowed_paths"])
            if kind != 'implement' and revision != after:
                raise ExecutionError("scope_violation", "Verification/review modified source files")
            if kind == 'verify' and response.result.get('revision') != revision:
                raise ExecutionError("stale_evidence", "Agent review is not bound to the current source fingerprint")
            if kind == 'verify' and not response.result['evidence']:
                raise ExecutionError("invalid_result", "Verification/review requires evidence references")
            if response.result['status'] in {'blocked', 'needs_input'}:
                raise ExecutionError('needs_input', 'Role requires missing information or unresolved prerequisites')
            if response.result["status"] != "completed" or response.result["blocking_findings"]:
                raise ExecutionError(f"{name}_rejected", "Agent reported incomplete work or blocking findings")
            record = {"result": response.result, "usage": response.usage, "usage_status": "observed" if response.usage else "unknown",
                      "cost_brl": None, "cost_status": "unknown", "metadata": response.metadata, "changed_files": changed}
            self.store.finish_stage(run["id"], run["attempt"], name, "succeeded", record, after)
            self.store.finish_invocation(invocation_id, 'succeeded')
            self._emit(run['id'], {'type': 'completed', 'role_id': role_id, 'stage': name, 'message': response.result['summary']})
        except ExecutionError as error:
            record = {"error": {"category": error.category, "message": str(error)}}
            if "response" in locals():
                record.update(result=response.result, usage=response.usage, metadata=response.metadata)
            self.store.finish_stage(run["id"], run["attempt"], name, "failed", record, revision)
            if invocation_id:
                self.store.finish_invocation(invocation_id, 'failed')
            raise

    def _checks(self, run: dict):
        task = run["task"]
        workspace = Path(run["workspace"])
        revision = current_revision(workspace, task["base_revision"])
        self.store.start_stage(run["id"], run["attempt"], "checks", revision)
        records = []
        try:
            for component in task["components"]:
                cwd = local_path(workspace, component["working_directory"])
                for check in component["checks"]:
                    self._emit(run['id'], {'type': 'check', 'message': 'Running check: ' + check['name']})
                    outcome = execute(check["argv"], cwd, min(check["timeout_seconds"], self._remaining(run)),
                                      on_tick=lambda: self._control(run['id']))
                    records.append({"component": component["name"], "language": component["language"], "name": check["name"],
                                    "argv": check["argv"], "working_directory": component["working_directory"],
                                    "exit_code": outcome.exit_code, "stdout": outcome.stdout, "stderr": outcome.stderr,
                                    "duration_seconds": outcome.duration_seconds, "timed_out": outcome.timed_out})
                    if current_revision(workspace, task["base_revision"]) != revision:
                        raise ExecutionError("checks_mutated_workspace", "Verification command changed source files")
                    if outcome.timed_out:
                        raise ExecutionError("timeout", "Required check timed out")
                    if outcome.exit_code:
                        raise ExecutionError("checks_failed", "A required check returned a nonzero exit code")
            self.store.finish_stage(run["id"], run["attempt"], "checks", "succeeded", {"checks": records}, revision)
        except ExecutionError as error:
            self.store.finish_stage(run["id"], run["attempt"], "checks", "failed", {"checks": records, "error": {"category": error.category, "message": str(error)}}, revision)
            raise

    def _drive(self, run_id: str):
        feedback = None
        while True:
            run = self.store.get(run_id)
            self._remaining(run)
            current_revision(Path(run["workspace"]), run["task"]["base_revision"])
            history = {stage["name"]: stage for stage in self.store.stages(run_id) if stage["attempt"] == run["attempt"]}
            try:
                implementation = next(step for step in run['task']['workflow'] if step['kind'] == 'implement')
                for step in run['task']['workflow']:
                    if step['kind'] == 'verify':
                        continue
                    stage = history.get(step['name'])
                    if stage is None or stage['status'] != 'succeeded':
                        if stage and stage['result_json'] and feedback is None:
                            feedback = {'previous_invocation': json.loads(stage['result_json']), 'instruction': 'Inspect retained work and continue within remaining limits'}
                        self._agent_stage(run, step['name'], feedback)
                revision = current_revision(Path(run['workspace']), run['task']['base_revision'])
                checked = history.get('checks')
                if not checked or checked['status'] != 'succeeded' or checked['revision_hash'] != revision:
                    self._checks(run)
                for step in run['task']['workflow']:
                    if step['kind'] == 'verify':
                        previous = history.get(step['name'])
                        if not previous or previous['status'] != 'succeeded' or previous['revision_hash'] != revision:
                            self._agent_stage(run, step['name'])
                revision = current_revision(Path(run["workspace"]), run["task"]["base_revision"])
                with self.store.connection:
                    self.store.connection.execute('UPDATE runs SET verified_hash=? WHERE id=?', (revision, run_id))
                self.delivery.deliver(self.store, run_id, lambda: self._control(run_id))
                self.store.status(run_id, "succeeded", verified_hash=revision)
                return
            except ExecutionError as error:
                repairable = {'checks_failed'} | {step['name'] + '_rejected' for step in run['task']['workflow'] if step['kind'] == 'verify'}
                if error.category not in repairable:
                    raise
                stages = self.store.stages(run_id)
                feedback = {"category": error.category, "message": str(error),
                            "last_stage_result": json.loads(stages[-1]["result_json"]) if stages and stages[-1]["result_json"] else None}
                result = feedback['last_stage_result'] or {}
                signature = fingerprint({'revision': current_revision(Path(run['workspace']), run['task']['base_revision']),
                                         'category': error.category, 'findings': result.get('result', {}).get('blocking_findings'),
                                         'checks': [(check['name'], check['exit_code'], check['stdout'], check['stderr']) for check in result.get('checks', [])]})
                previous = self.store.events(run_id, limit=1000)
                repeated = sum(event['type'] == 'repair.observed' and event['payload'].get('signature') == signature for event in previous)
                with self.store.connection:
                    self.store.event(run_id, 'repair.observed', {'signature': signature})
                if repeated + 1 >= run['task']['limits']['max_no_progress_attempts']:
                    raise ExecutionError('no_progress', 'Repeated rejection with unchanged source and findings')
                self.store.next_attempt(run_id, run["task"]["limits"]["max_attempts"])
                self.store.invalidate(run_id)

    def _fail(self, run_id: str, error: ExecutionError):
        status = "blocked" if error.category in {"tool_unavailable", "auth_unavailable", "auth_unsupported", "configuration_changed", "interrupted_implementation", "context_unavailable"} else "failed"
        if error.category in {'needs_input', 'loop_detected', 'no_progress', 'reconciliation_required', 'usage_unavailable',
                              'delivery_uncertain', 'deployment_uncertain', 'stale_base', 'project_budget_exhausted'}:
            status = 'blocked'
        if error.category == 'cancelled':
            status = 'cancelled'
        self.store.status(run_id, status, {"category": error.category, "message": str(error)})
        self._emit(run_id, {'type': 'stopped', 'message': str(error), 'category': error.category})

    def report(self, run_id: str) -> dict:
        """Produce a standalone report that never equates agent prose with delivery."""
        run = self.store.get(run_id)
        stages = self.store.stages(run_id)
        directory = self.store.root / "runs" / run_id
        evidence_current = False
        if run["verified_hash"]:
            try:
                evidence_current = current_revision(Path(run["workspace"]), run["task"]["base_revision"]) == run["verified_hash"]
            except ExecutionError:
                evidence_current = False
        report = {"schema_version": 1, "run_id": run_id, "task_id": run["task"]["task_id"], "project_id": run["task"]["project_id"],
                  "status": "stale" if run["status"] == "succeeded" and not evidence_current else run["status"],
                  "evidence_current": evidence_current, "workspace": run["workspace"], "base_revision": run["task"]["base_revision"],
                  "configuration_fingerprint": run["config_hash"], "verified_fingerprint": run["verified_hash"],
                  "agent_calls": run["calls"], "attempts": run["attempt"],
                  'budget': self.store.budget(run_id), 'limits': run['task']['limits'],
                  'workflow': run['task'].get('workflow'), 'external_effects': self.store.effects(run_id),
                  "error": json.loads(run["error_json"]) if run["error_json"] else None,
                  "stages": [{**stage, "result": json.loads(stage["result_json"]) if stage["result_json"] else None} for stage in stages],
                  "delivery": {"kind": run['task']['policy']['delivery'], "patch": str(directory / "task.patch"), "source_checkout_modified": False,
                               'remote_pr': self.store.effects(run_id).get('pull_request', 'pending' if run['task']['policy']['delivery'] != 'diff' else 'not_requested'),
                               'deployment': self.store.effects(run_id).get('deployment', 'pending' if run['task']['policy']['delivery'] == 'deploy' else 'not_requested')}}
        for stage in report["stages"]:
            stage.pop("result_json", None)
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "report.json").write_text(json.dumps(safe_value(report), indent=2) + "\n")
        return safe_value(report)
