"""Verify delivery using actual Git repositories/deployment processes and controlled GitHub I/O."""

import json
from pathlib import Path
import sys
import unittest

from dev_agent_kit.delivery import GitHubDelivery
from dev_agent_kit.processes import ProcessResult, execute
from dev_agent_kit.workspace import git
from tests.integration.test_executor import ControlledAgent, ExecutorFixture, ROOT
from dev_agent_kit.executor import Executor


class GitHubFixture:
    """Replace remote HTTP/network operations while keeping local Git effects real."""
    def __init__(self, remote, base):
        self.remote, self.base = remote, base
        self.pr = None
        self.calls = []
        self.fail_ci = False
        self.stale_head = False
        self.merge_calls = 0

    def __call__(self, argv, cwd, timeout, **kwargs):
        self.calls.append(argv)
        if argv[0] == 'git':
            command = argv.copy()
            command[command.index('origin')] = str(self.remote)
            return execute(command, cwd, timeout, **kwargs)
        if argv[0] != 'gh':
            return execute(argv, cwd, timeout, **kwargs)
        operation = argv[1:3]
        value = None
        status = 0
        if operation == ['repo', 'view']:
            value = {'defaultBranchRef': {'name': 'main'}}
        elif operation == ['issue', 'view']:
            value = {'number': 123, 'state': 'OPEN'}
        elif operation == ['pr', 'list']:
            value = [self.pr] if self.pr else []
        elif operation == ['pr', 'create']:
            self.pr = {'number': 42, 'url': 'https://github.com/fixture/project/pull/42', 'state': 'OPEN',
                       'headRefOid': git(cwd, 'rev-parse', 'HEAD').strip()}
            return ProcessResult(0, self.pr['url'], '', 0)
        elif operation == ['pr', 'view']:
            value = {**self.pr, 'headRefOid': '0' * 40 if self.stale_head else self.pr['headRefOid'],
                     'mergeCommit': {'oid': self.pr['headRefOid']} if self.pr['state'] == 'MERGED' else None,
                     'baseRefName': 'main'}
        elif operation == ['pr', 'checks']:
            value = [{'name': 'required-test', 'bucket': 'fail' if self.fail_ci else 'pass', 'link': 'https://example.invalid/check'}]
            status = 1 if self.fail_ci else 0
        elif operation == ['pr', 'merge']:
            self.merge_calls += 1
            git(self.remote, 'update-ref', 'refs/heads/main', self.pr['headRefOid'])
            self.pr['state'] = 'MERGED'
            return ProcessResult(0, '', '', 0)
        else:
            raise AssertionError(argv)
        return ProcessResult(status, json.dumps(value), '', 0)


class DeliveryTests(ExecutorFixture, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.remote = self.root / 'remote.git'
        git(self.root, 'init', '--bare', str(self.remote))
        git(self.repository, 'push', str(self.remote), 'HEAD:refs/heads/main')
        git(self.repository, 'remote', 'add', 'origin', 'https://github.com/fixture/project.git')
        self.io = GitHubFixture(self.remote, self.task['base_revision'])
        self.task['policy'].update(include_working_tree=False, delivery='merge')
        self.task['delivery'] = {'repository': 'fixture/project', 'issue_number': 123, 'base_branch': 'main',
                                 'branch_description': 'implement-checked-feature', 'required_checks': ['required-test'],
                                 'merge_method': 'rebase', 'ci_timeout_seconds': 5}

    def configured(self):
        executor = Executor(ROOT, self.root / 'state', ControlledAgent(), GitHubDelivery(self.io, poll_interval=0))
        self.executors.append(executor)
        return executor

    def test_merge_matches_approved_head_and_preserves_source_checkout(self):
        result = self.configured().start(self.task)
        self.assertEqual(result['status'], 'succeeded', result['error'])
        self.assertEqual(self.io.merge_calls, 1)
        merge = next(call for call in self.io.calls if call[:3] == ['gh', 'pr', 'merge'])
        self.assertIn('--match-head-commit', merge)
        self.assertNotIn('--admin', merge)
        self.assertEqual(git(self.repository, 'rev-parse', 'HEAD').strip(), self.task['base_revision'])
        self.assertFalse((self.repository / 'feature.py').exists())
        self.assertEqual(result['external_effects']['merge']['status'], 'succeeded')

    def test_failed_remote_checks_prevent_merge_and_resume_reuses_reviews(self):
        executor = self.configured()
        self.io.fail_ci = True
        failed = executor.start(self.task)
        self.assertEqual(failed['error']['category'], 'ci_failed')
        self.assertEqual(self.io.merge_calls, 0)
        self.io.fail_ci = False
        resumed = executor.resume(failed['run_id'])
        self.assertEqual(resumed['status'], 'succeeded', resumed['error'])
        self.assertEqual(resumed['agent_calls'], 3)
        self.assertEqual(sum(call[:3] == ['gh', 'pr', 'create'] for call in self.io.calls), 1)

    def test_changed_remote_head_prevents_merge(self):
        self.io.stale_head = True
        result = self.configured().start(self.task)
        self.assertEqual(result['error']['category'], 'stale_evidence')
        self.assertEqual(self.io.merge_calls, 0)

    def deployment_task(self, smoke_fails=False):
        self.task['policy']['delivery'] = 'deploy'
        marker = self.root / 'deployment.marker'
        self.task['delivery']['deployment'] = {'environment': 'local-test',
            'argv': [sys.executable, '-c', 'from pathlib import Path; Path('+repr(str(marker))+').write_text("deployed")'],
            'smoke_argv': [sys.executable, '-c', 'raise SystemExit('+('7' if smoke_fails else '0')+')'],
            'rollback_argv': [sys.executable, '-c', 'from pathlib import Path; Path('+repr(str(marker))+').write_text("rolled back")'],
            'timeout_seconds': 5}
        return marker

    def test_real_deploy_and_smoke_run_from_merged_tree(self):
        marker = self.deployment_task()
        result = self.configured().start(self.task)
        self.assertEqual(result['status'], 'succeeded', result['error'])
        self.assertEqual(marker.read_text(), 'deployed')
        self.assertEqual(result['external_effects']['deployment']['result']['smoke'], 'passed')

    def test_failed_smoke_rolls_back_and_uncertain_deploy_is_not_repeated(self):
        marker = self.deployment_task(True)
        executor = self.configured()
        failed = executor.start(self.task)
        self.assertEqual(failed['error']['category'], 'deployment_failed')
        self.assertEqual(marker.read_text(), 'rolled back')
        resumed = executor.resume(failed['run_id'])
        self.assertEqual(resumed['error']['category'], 'deployment_uncertain')
        self.assertEqual(resumed['agent_calls'], 3)
        self.assertEqual(self.io.merge_calls, 1)
