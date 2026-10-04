"""Test JSON-RPC transport and live limits with real subprocesses and controlled provider I/O."""

import json
from pathlib import Path
import sys
import unittest

from dev_agent_kit.adapters import Assignment
from dev_agent_kit.app_server import CodexAppServer
from dev_agent_kit.contracts import ExecutionError, normalize_task
from dev_agent_kit.workspace import current_revision
from tests.integration.test_executor import ExecutorFixture, ROOT

FAKE_SERVER = '''#!/usr/bin/env python3
import json,sys,time
from pathlib import Path
settings=json.loads(Path(sys.argv[0]+'.json').read_text())
def emit(value):
 print(json.dumps(value),flush=True)
for line in sys.stdin:
 request=json.loads(line);method=request['method'];params=request.get('params',{})
 if 'id' not in request: continue
 result={}
 if method=='account/read': result={'account':{'type':'chatgpt'}}
 if method=='thread/start': result={'thread':{'id':'thread-fixture'},'model':'fixture-model'}
 if method=='turn/start': result={'turn':{'id':'turn-fixture','status':'inProgress'}}
 emit({'id':request['id'],'result':result})
 if method=='turn/start':
  task=json.loads(params['input'][0]['text'].split('\\n',1)[1])
  emit({'method':'item/completed','params':{'threadId':'thread-fixture','item':{'id':'private','type':'reasoning','text':'private reasoning'}}})
  total=500 if settings['exceed'] else 25
  emit({'method':'thread/tokenUsage/updated','params':{'threadId':'thread-fixture','tokenUsage':{'total':{'inputTokens':total-5,'cachedInputTokens':10,'outputTokens':5,'totalTokens':total}}}})
  if settings['exceed']:
   time.sleep(3);Path(settings['marker']).write_text('should not execute');continue
  result={'schema_version':1,'task_id':task['task']['task_id'],'role_id':task['role_id'],'status':'completed','summary':'Controlled protocol response','artifacts':[],'evidence':[],'blocking_findings':[],'open_questions':[],'revision':task['evidence']['current_revision'],'decisions':[]}
  emit({'method':'item/completed','params':{'threadId':'thread-fixture','item':{'id':'final','type':'agentMessage','phase':'final_answer','text':json.dumps(result)}}})
  emit({'method':'turn/completed','params':{'threadId':'thread-fixture','turn':{'id':'turn-fixture','status':'completed'}}})
'''


class AppServerTests(ExecutorFixture, unittest.TestCase):
    def assignment(self, exceed=False):
        executable = self.root / 'controlled-codex'
        executable.write_text(FAKE_SERVER)
        executable.chmod(0o755)
        self.marker = self.root / 'unexpected-effect'
        Path(str(executable) + '.json').write_text(json.dumps({'exceed': exceed, 'marker': str(self.marker)}))
        task = normalize_task(self.task, ROOT)
        task['limits']['max_tokens_per_agent'] = 100
        events = []
        assignment = Assignment('developer', task, self.repository, 'Controlled test instructions',
                                {'current_revision': current_revision(self.repository, task['base_revision'])},
                                json.loads((ROOT / 'contracts/agent-result.schema.json').read_text()), 5,
                                self.root / 'artifacts', True, events.append, lambda: None)
        return CodexAppServer(str(executable)), assignment, events

    def test_stable_protocol_returns_usage_model_and_structured_result(self):
        adapter, assignment, events = self.assignment()
        response = adapter.execute(assignment)
        self.assertEqual(response.result['task_id'], self.task['task_id'])
        self.assertEqual(response.usage['total_tokens'], 25)
        self.assertEqual(response.metadata['model'], 'fixture-model')
        self.assertNotIn('private reasoning', str(events))
        self.assertTrue((assignment.artifact_directory / 'provider-result.json').is_file())

    def test_live_usage_exhaustion_interrupts_real_process_before_later_effect(self):
        adapter, assignment, events = self.assignment(True)
        with self.assertRaises(ExecutionError) as caught:
            adapter.execute(assignment)
        self.assertEqual(caught.exception.category, 'token_budget_exhausted')
        self.assertFalse(self.marker.exists())
        failure = json.loads((assignment.artifact_directory / 'failure.json').read_text())
        self.assertEqual(failure['usage']['total_tokens'], 500)
