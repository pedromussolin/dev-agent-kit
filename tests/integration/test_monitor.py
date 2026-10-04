"""Exercise public monitoring, SSE replay and control isolation using actual SQLite."""

import unittest

from tests.integration.test_executor import ExecutorFixture

try:
    from fastapi.testclient import TestClient
    from dev_agent_kit.monitor import create_app
except ImportError:
    TestClient = None


@unittest.skipUnless(TestClient, 'Install monitor/test extras to run HTTP monitoring checks')
class MonitorTests(ExecutorFixture, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.executor_instance = self.executor()
        self.report = self.executor_instance.start(self.task)
        self.client = TestClient(create_app(self.root / 'state'), base_url='http://127.0.0.1')

    def test_dashboard_and_detail_present_real_stage_results(self):
        self.assertEqual(self.client.get('/').status_code, 200)
        response = self.client.get('/api/runs/' + self.report['run_id'])
        self.assertEqual(response.status_code, 200)
        value = response.json()
        self.assertEqual(value['status'], 'succeeded')
        self.assertEqual(value['agent_calls'], 3)
        self.assertEqual(sum(i['total_tokens'] for i in value['invocations']), 45)
        self.assertEqual(self.client.get('/api/runs').json()[0]['task_id'], self.task['task_id'])
        self.assertTrue(value['evidence_current'])

    def test_modified_source_is_reported_as_stale_evidence(self):
        from pathlib import Path
        (Path(self.report['workspace']) / 'feature.py').write_text('VALUE = 0\n')
        value = self.client.get('/api/runs/' + self.report['run_id']).json()
        self.assertFalse(value['evidence_current'])

    def test_sse_replays_public_events_and_respects_cursor(self):
        with self.executor_instance.store.connection:
            self.executor_instance.store.event(self.report['run_id'], 'stage.succeeded', {'result': {'reasoning': 'must stay private'}, 'stage': 'review'})
        url = '/api/runs/' + self.report['run_id'] + '/events'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('text/event-stream', response.headers['content-type'])
        self.assertNotIn('must stay private', response.text)
        ids = [int(line[4:]) for line in response.text.splitlines() if line.startswith('id: ')]
        self.assertTrue(ids)
        replay = self.client.get(url, headers={'Last-Event-ID': str(max(ids))})
        self.assertNotIn('data: ', replay.text)

    def test_cancel_requires_same_origin_control_and_persists(self):
        url = '/api/runs/' + self.report['run_id'] + '/cancel'
        self.assertEqual(self.client.post(url).status_code, 403)
        self.assertEqual(self.client.post(url, headers={'X-Dev-Agent-Kit-Control': '1', 'Origin': 'https://untrusted.example'}).status_code, 403)
        self.assertEqual(self.client.post(url, headers={'X-Dev-Agent-Kit-Control': '1', 'Origin': 'http://127.0.0.1'}).status_code, 200)
        self.assertTrue(self.executor_instance.store.cancelled(self.report['run_id']))

    def test_unknown_runs_and_host_rebinding_are_rejected(self):
        self.assertEqual(self.client.get('/api/runs/unknown').status_code, 404)
        self.assertEqual(self.client.get('/api/runs', headers={'Host': 'untrusted.example'}).status_code, 400)

    def test_optional_monitor_password_is_required_when_configured(self):
        secured = TestClient(create_app(self.root / 'state', 'fixture-password'), base_url='http://127.0.0.1')
        self.assertEqual(secured.get('/api/runs').status_code, 401)
        self.assertEqual(secured.get('/api/runs', auth=('operator', 'fixture-password')).status_code, 200)
