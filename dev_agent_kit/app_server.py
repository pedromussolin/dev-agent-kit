"""Drive the installed Codex app-server stable JSON-RPC surface over local stdio."""

import json
import os
import selectors
import signal
import subprocess
import time

from .adapters import AgentResponse, CodexCLI, bounded_client_options
from .contracts import ExecutionError, native_output_schema
from .guards import ExecutionGuard, public_item
from .processes import safe_value, sanitize
from .workspace import current_revision


class RPCProcess:
    """Bound transport buffers and process lifetime independently of the agent."""

    def __init__(self, command, cwd, timeout, control):
        self.process = subprocess.Popen(command, cwd=cwd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE, start_new_session=True)
        self.selector = selectors.DefaultSelector()
        self.selector.register(self.process.stdout, selectors.EVENT_READ, 'stdout')
        self.selector.register(self.process.stderr, selectors.EVENT_READ, 'stderr')
        self.buffer = b''
        self.stderr = b''
        self.received = 0
        self.sequence = 0
        self.notifications = []
        self.deadline = time.monotonic() + timeout
        self.control = control

    def send(self, method, params=None, notification=False):
        self.sequence += 1
        message = {'method': method, 'params': params or {}}
        if not notification:
            message['id'] = self.sequence
        try:
            self.process.stdin.write((json.dumps(message) + '\n').encode())
            self.process.stdin.flush()
        except (BrokenPipeError, OSError) as error:
            raise ExecutionError('provider_failure', 'Codex app-server closed its transport') from error
        return self.sequence

    def receive(self):
        while True:
            self.control()
            if time.monotonic() >= self.deadline:
                raise ExecutionError('timeout', 'Codex assignment exceeded its deadline')
            if b'\n' in self.buffer:
                line, self.buffer = self.buffer.split(b'\n', 1)
                try:
                    return json.loads(line)
                except json.JSONDecodeError as error:
                    raise ExecutionError('invalid_result', 'Invalid app-server protocol message') from error
            for key, _ in self.selector.select(0.1):
                data = os.read(key.fileobj.fileno(), 65536)
                if not data:
                    self.selector.unregister(key.fileobj)
                    continue
                self.received += len(data)
                if self.received > 1_048_576:
                    raise ExecutionError('output_limit', 'Provider stream exceeded capture limit')
                if key.data == 'stdout':
                    self.buffer += data
                else:
                    self.stderr = (self.stderr + data)[-8000:]
            if not self.selector.get_map() or (self.process.poll() is not None and not self.buffer):
                raise ExecutionError('provider_failure', 'Codex app-server exited before completion')

    def request(self, method, params=None):
        identifier = self.send(method, params)
        while True:
            message = self.receive()
            if message.get('id') == identifier:
                if 'error' in message:
                    raise ExecutionError('provider_failure', 'Codex rejected app-server request: ' + method)
                return message.get('result', {})
            if 'id' in message and 'method' in message:
                raise ExecutionError('needs_input', 'Provider requested interaction outside the task contract')
            self.notifications.append(message)

    def close(self):
        if self.process.poll() is None:
            os.killpg(self.process.pid, signal.SIGKILL)
        self.process.wait()
        self.selector.close()
        for stream in (self.process.stdin, self.process.stdout, self.process.stderr):
            stream.close()


class CodexAppServer(CodexCLI):
    """Expose public activity and cumulative token updates during an assignment."""

    def preflight(self):
        metadata = super().preflight()
        metadata.update(adapter='codex-app-server', live_token_updates=True,
                        token_enforcement='interrupt_on_observed_usage; in-flight request may overshoot')
        return metadata

    def execute(self, assignment):
        directory = assignment.artifact_directory
        directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        schema = native_output_schema(assignment.output_schema)
        (directory / 'native-schema.json').write_text(json.dumps(schema))
        prompt = ('Complete only this role assignment. Do not delegate, commit, publish, merge or deploy. '
                  'Keep tool calls focused; executor runs all declared checks after implementation. '
                  'Do not duplicate its complete regression suite. Use supplied check evidence for verification. '
                  'The selected skill, effective kit policy and result schema are already supplied: '
                  'do not re-read identical kit copies. Batch required project-instruction reads in one command. '
                  'Return the structured result with the supplied revision.\n' +
                  json.dumps({'role_id': assignment.role_id, 'task': assignment.task,
                              'evidence': assignment.context, 'remaining_assignment_seconds': assignment.timeout_seconds}))
        if len(prompt) + len(assignment.instructions) > assignment.task['limits']['max_context_characters']:
            raise ExecutionError('limit_exceeded', 'Full role/task context exceeds configured size')
        guard = ExecutionGuard(assignment.task['limits'], assignment.event_sink or (lambda event: None),
                               assignment.check_control or (lambda: None),
                               lambda: current_revision(assignment.workspace, assignment.task['base_revision']))
        command = [self.executable, '--no-daemon', 'app-server', '--listen', 'stdio://',
                   *bounded_client_options()]
        rpc = RPCProcess(command, assignment.workspace, assignment.timeout_seconds, guard.tick)
        started = time.monotonic()
        thread_id = turn_id = None
        final = None
        model = None
        try:
            rpc.request('initialize', {'clientInfo': {'name': 'dev_agent_kit', 'title': 'Dev Agent Kit', 'version': '0.2.0'}})
            rpc.send('initialized', notification=True)
            account = rpc.request('account/read', {'refreshToken': False}).get('account')
            if not account or account.get('type') not in {'chatgpt', 'chatgptAuthTokens'}:
                raise ExecutionError('auth_unsupported', 'App-server must use existing ChatGPT account authentication')
            thread = rpc.request('thread/start', {'cwd': str(assignment.workspace), 'ephemeral': True,
                                                 'approvalPolicy': 'never',
                                                 'sandbox': 'workspace-write' if assignment.writable else 'read-only',
                                                 'developerInstructions': assignment.instructions})
            thread_id = thread['thread']['id']
            model = thread.get('model')
            policy = {'type': 'workspaceWrite', 'writableRoots': [str(assignment.workspace)],
                      'networkAccess': False} if assignment.writable else {'type': 'readOnly', 'networkAccess': False}
            reply = rpc.request('turn/start', {'threadId': thread_id, 'input': [{'type': 'text', 'text': prompt}],
                                               'approvalPolicy': 'never', 'sandboxPolicy': policy, 'outputSchema': schema})
            turn_id = reply['turn']['id']
            while True:
                event = rpc.notifications.pop(0) if rpc.notifications else rpc.receive()
                guard.last_activity = time.monotonic()
                if 'id' in event and 'method' in event:
                    raise ExecutionError('needs_input', 'Provider requested approval/input outside the task contract')
                method, params = event.get('method'), event.get('params', {})
                if params.get('threadId', thread_id) != thread_id:
                    continue
                if method == 'thread/tokenUsage/updated':
                    total = params['tokenUsage']['total']
                    usage = {'input_tokens': total.get('inputTokens', 0), 'cached_input_tokens': total.get('cachedInputTokens', 0),
                             'output_tokens': total.get('outputTokens', 0), 'reasoning_output_tokens': total.get('reasoningOutputTokens', 0),
                             'total_tokens': total.get('totalTokens', total.get('inputTokens', 0) + total.get('outputTokens', 0))}
                    guard.event({'type': 'usage', 'usage': usage})
                elif method in {'item/started', 'item/completed'}:
                    item = params.get('item', {})
                    public = public_item(item, method == 'item/completed')
                    if public:
                        if public['type'] == 'tool.completed':
                            guard.event({**public, 'type': 'tool.started'})
                        guard.event(public)
                    if method == 'item/completed' and item.get('type') == 'agentMessage' and item.get('phase') != 'commentary':
                        final = item.get('text')
                elif method == 'turn/completed':
                    if params['turn']['status'] != 'completed':
                        raise ExecutionError('provider_failure', 'Provider turn failed or was interrupted')
                    break
            if not guard.usage:
                raise ExecutionError('usage_unavailable', 'Live token accounting required but not reported by client')
            try:
                result = json.loads(final or '')
            except json.JSONDecodeError as error:
                raise ExecutionError('invalid_result', 'App-server final result is not valid structured JSON') from error
            (directory / 'provider-result.json').write_text(json.dumps(safe_value(result), indent=2) + '\n')
            return AgentResponse(result, guard.usage, {'adapter': 'codex-app-server', 'model': model,
                                 'sandbox': policy['type'], 'duration_seconds': time.monotonic() - started,
                                 'prompt_characters': len(prompt), 'exit_code': 0})
        except BaseException as error:
            if thread_id and turn_id and rpc.process.poll() is None:
                try:
                    rpc.send('turn/interrupt', {'threadId': thread_id, 'turnId': turn_id})
                except ExecutionError:
                    pass
            (directory / 'failure.json').write_text(json.dumps(safe_value({'category': getattr(error, 'category', 'interrupted'),
                                               'usage': guard.usage, 'stderr': sanitize(rpc.stderr.decode(errors='replace'))}), indent=2))
            raise
        finally:
            rpc.close()
