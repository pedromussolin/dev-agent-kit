"""Deliver an approved tree through GitHub CLI and explicitly configured deployment."""

import json
from pathlib import Path
import shutil
import time

from .contracts import ExecutionError, local_path
from .processes import execute
from .workspace import current_revision, git, source_manifest


class GitHubDelivery:
    """Respect remote protections, match the approved head and reconcile external effects."""

    def __init__(self, runner=execute, poll_interval=3):
        self.runner, self.poll_interval = runner, poll_interval

    def command(self, argv, cwd, timeout=30, control=None):
        result = self.runner(argv, cwd, timeout, on_tick=control)
        if result.timed_out or result.exit_code:
            raise ExecutionError('delivery_failed', 'Delivery command failed: ' + Path(argv[0]).name + '; ' + result.stderr[-1000:])
        return result.stdout

    def gh(self, task, args, cwd, control=None):
        argv = ['gh', *args, '--repo', task['delivery']['repository']]
        if args[:2] == ['repo', 'view']:
            argv = ['gh', 'repo', 'view', task['delivery']['repository'], *args[2:]]
        if args[:2] == ['pr', 'checks']:
            result = self.runner(argv, cwd, 30, on_tick=control)
            if result.timed_out or result.exit_code not in {0, 1, 8}:
                raise ExecutionError('delivery_failed', 'Cannot inspect remote CI checks')
            return json.loads(result.stdout)
        return json.loads(self.command(argv, cwd, control=control))

    def preflight(self, task):
        if task['policy']['delivery'] == 'diff':
            return
        repository = Path(task['repository'])
        owner = task['delivery']['repository']
        remote = git(repository, 'remote', 'get-url', 'origin').strip().removesuffix('.git')
        if remote not in {'https://github.com/' + owner, 'git@github.com:' + owner}:
            raise ExecutionError('delivery_configuration', 'Configured repository differs from Git origin')
        metadata = self.gh(task, ['repo', 'view', '--json', 'defaultBranchRef'], repository)
        if metadata['defaultBranchRef']['name'] != task['delivery']['base_branch']:
            raise ExecutionError('delivery_configuration', 'Development delivery must originate from the default branch')
        issue = self.gh(task, ['issue', 'view', str(task['delivery']['issue_number']), '--json', 'number,state'], repository)
        if issue['state'] != 'OPEN':
            raise ExecutionError('delivery_configuration', 'Delivery requires a real open issue')
        if self.remote_head(task, task['delivery']['base_branch'], repository) != task['base_revision']:
            raise ExecutionError('stale_base', 'Refresh the committed default-branch input before delivery')

    def remote_head(self, task, branch, cwd, control=None):
        output = self.command(['git', 'ls-remote', 'origin', 'refs/heads/' + branch], cwd, control=control)
        return output.split()[0] if output.strip() else None

    def deliver(self, store, run_id, control):
        run = store.get(run_id)
        task = run['task']
        mode = task['policy']['delivery']
        if mode == 'diff':
            return {'kind': 'isolated_diff'}
        source = Path(run['workspace'])
        if current_revision(source, task['base_revision']) != run['verified_hash']:
            raise ExecutionError('stale_evidence', 'Delivery requires current accepted source evidence')
        directory = store.root / 'runs' / run_id
        workspace = directory / 'delivery-workspace'
        config = task['delivery']
        branch = f"feature/{config['issue_number']}-{config['branch_description']}-{run_id[:8]}"
        effects = store.effects(run_id)
        publish = effects.get('publish')
        if publish is None:
            self.preflight(task)
            control()
            store.effect(run_id, 'publish', 'running', {'branch': branch})
            git(Path(task['repository']), 'worktree', 'add', '--detach', str(workspace), task['base_revision'])
            git(workspace, 'switch', '-c', branch)
            baseline = json.loads((directory / 'baseline.json').read_text())
            manifest = source_manifest(source)
            for name in baseline.keys() | manifest.keys():
                if baseline.get(name) == manifest.get(name):
                    continue
                destination = local_path(workspace, name)
                if name not in manifest:
                    destination.unlink()
                else:
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(local_path(source, name), destination)
            if source_manifest(workspace) != manifest:
                raise ExecutionError('stale_evidence', 'Delivery tree differs from approved source')
            git(workspace, 'add', '--all')
            if not git(workspace, 'diff', '--cached', '--name-only').strip():
                raise ExecutionError('delivery_configuration', 'No change to publish')
            git(workspace, 'commit', '-m', f"feat({config['issue_number']}): Implement authorized task")
            commit = git(workspace, 'rev-parse', 'HEAD').strip()
            store.effect(run_id, 'publish', 'running', {'branch': branch, 'commit': commit})
        else:
            commit = publish['result'].get('commit')
            if not commit or not workspace.is_dir():
                raise ExecutionError('delivery_uncertain', 'Inspect interrupted local publish preparation before proceeding')
        control()
        remote = self.remote_head(task, branch, workspace, control)
        if remote not in {None, commit}:
            raise ExecutionError('stale_evidence', 'Remote delivery branch changed outside this run')
        if remote is None:
            self.command(['git', 'push', 'origin', commit + ':refs/heads/' + branch], workspace, control=control)
        store.effect(run_id, 'publish', 'succeeded', {'branch': branch, 'commit': commit})
        prs = self.gh(task, ['pr', 'list', '--state', 'all', '--head', branch, '--base', config['base_branch'],
                             '--json', 'number,url,state,headRefOid'], workspace, control)
        if len(prs) > 1:
            raise ExecutionError('delivery_uncertain', 'Multiple pull requests reference this owned branch')
        if not prs:
            body = directory / 'pull-request.md'
            body.write_text(f"Implement task {task['task_id']} for #{config['issue_number']}.\n\n"
                            f"{task['goal']}\n\nValidation: local checks, QA and technical review passed for source fingerprint "
                            f"`{run['verified_hash']}`.\n")
            store.effect(run_id, 'pull_request', 'running', {'branch': branch, 'commit': commit})
            self.command(['gh', 'pr', 'create', '--repo', config['repository'], '--base', config['base_branch'], '--head', branch,
                          '--title', f"feat({config['issue_number']}): Implement authorized task", '--body-file', str(body)], workspace, control=control)
            prs = self.gh(task, ['pr', 'list', '--state', 'all', '--head', branch, '--json', 'number,url,state,headRefOid'], workspace, control)
        if len(prs) != 1 or prs[0]['headRefOid'] != commit:
            raise ExecutionError('stale_evidence', 'Pull request head differs from approved commit')
        pr = prs[0]
        if pr['state'] == 'CLOSED':
            raise ExecutionError('delivery_failed', 'Owned pull request was closed without merging')
        store.effect(run_id, 'pull_request', 'succeeded', pr)
        if mode == 'pull_request':
            return {'kind': mode, 'pull_request': pr, 'commit': commit}
        deadline = time.monotonic() + config['ci_timeout_seconds']
        while True:
            control()
            view = self.gh(task, ['pr', 'view', str(pr['number']), '--json', 'state,headRefOid,mergeCommit,baseRefName'], workspace, control)
            if view['headRefOid'] != commit or view['baseRefName'] != config['base_branch']:
                raise ExecutionError('stale_evidence', 'Pull request identity changed')
            if view['state'] == 'MERGED':
                break
            if view['state'] != 'OPEN':
                raise ExecutionError('delivery_failed', 'Pull request closed without merging')
            if time.monotonic() >= deadline:
                raise ExecutionError('ci_timeout', 'Remote CI or merge queue did not finish within the configured deadline')
            checks = self.gh(task, ['pr', 'checks', str(pr['number']), '--json', 'name,bucket,link'], workspace, control)
            by_name = {name: [check['bucket'] for check in checks if check['name'] == name]
                       for name in config['required_checks']}
            required = config['required_checks']
            if any(bucket in {'fail', 'cancel', 'skipping'} for name in required for bucket in by_name[name]):
                raise ExecutionError('ci_failed', 'A declared remote check failed or did not execute')
            if any(check['bucket'] in {'fail', 'cancel'} for check in checks):
                raise ExecutionError('ci_failed', 'A remote check failed')
            if all(by_name[name] and all(bucket == 'pass' for bucket in by_name[name]) for name in required) and all(check['bucket'] in {'pass', 'skipping'} for check in checks):
                if self.remote_head(task, config['base_branch'], workspace, control) != task['base_revision']:
                    raise ExecutionError('stale_base', 'Default branch changed; obtain new checks/reviews before merging')
                effect = store.effects(run_id).get('merge')
                if not effect:
                    store.effect(run_id, 'merge', 'running', {'pr': pr['number'], 'commit': commit})
                    self.command(['gh', 'pr', 'merge', str(pr['number']), '--repo', config['repository'],
                                  '--' + config['merge_method'], '--match-head-commit', commit], workspace, control=control)
                # A queued or ambiguously interrupted merge must be observed, never repeated blindly.
            with store.connection:
                store.event(run_id, 'delivery.waiting', {'operation': 'ci_or_merge', 'checks': checks})
            time.sleep(min(self.poll_interval, max(0, deadline - time.monotonic())))
        merged = view['mergeCommit']['oid']
        store.effect(run_id, 'merge', 'succeeded', {'commit': merged, 'pull_request': pr['number']})
        if mode == 'merge':
            return {'kind': mode, 'pull_request': pr, 'commit': commit, 'merge_commit': merged}
        self.command(['git', 'fetch', 'origin', merged], workspace, control=control)
        if git(workspace, 'rev-parse', merged + '^{tree}').strip() != git(workspace, 'rev-parse', commit + '^{tree}').strip():
            raise ExecutionError('stale_evidence', 'Merged tree differs from the tested and approved tree')
        return self.deploy(store, run_id, task, merged, directory, control)

    def deploy(self, store, run_id, task, merged, directory, control):
        config = task['delivery']['deployment']
        prior = store.effects(run_id).get('deployment')
        if prior:
            if prior['status'] == 'succeeded':
                return prior['result']
            raise ExecutionError('deployment_uncertain', 'Inspect interrupted or failed deployment before retrying its effects')
        workspace = directory / 'deployment-workspace'
        git(Path(task['repository']), 'worktree', 'add', '--detach', str(workspace), merged)
        store.effect(run_id, 'deployment', 'running', {'revision': merged, 'environment': config['environment']})
        try:
            control()
            self.command(config['argv'], workspace, config['timeout_seconds'], control)
            self.command(config['smoke_argv'], workspace, config['timeout_seconds'], control)
        except ExecutionError as error:
            # Rollback is explicitly authorized by the deployment contract, even after cancellation.
            rollback = self.runner(config['rollback_argv'], workspace, config['timeout_seconds'])
            result = {'revision': merged, 'environment': config['environment'], 'rollback_exit_code': rollback.exit_code,
                      'rollback_timed_out': rollback.timed_out, 'error': error.category}
            store.effect(run_id, 'deployment', 'failed', result)
            raise ExecutionError('deployment_failed', 'Deployment/smoke failed; inspect the recorded rollback outcome') from error
        result = {'kind': 'deploy', 'revision': merged, 'environment': config['environment'], 'smoke': 'passed'}
        store.effect(run_id, 'deployment', 'succeeded', result)
        return result
