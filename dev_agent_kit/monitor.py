"""Expose a local monitoring view and public SSE timeline using FastAPI."""

import asyncio
import json
import secrets
from pathlib import Path
import sqlite3
from contextlib import contextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.sse import EventSourceResponse, ServerSentEvent
from starlette.middleware.trustedhost import TrustedHostMiddleware

from .contracts import ExecutionError
from .processes import safe_value
from .storage import Store
from .workspace import current_revision


@contextmanager
def connection(state):
    """Read live state without acquiring the executor writer lock."""
    database = Path(state).resolve() / 'state.sqlite3'
    if not database.is_file():
        raise HTTPException(503, 'Executor state has not been initialized')
    db = sqlite3.connect(database.as_uri() + '?mode=ro', uri=True)
    db.row_factory = sqlite3.Row
    try:
        yield db
    finally:
        db.close()


def list_runs(state):
    with connection(state) as db:
        rows = db.execute('SELECT id,status,created_at,calls,attempt,task_json,error_json FROM runs ORDER BY created_at DESC LIMIT 100')
        result = []
        for row in rows:
            value = dict(row)
            task = json.loads(value.pop('task_json'))
            value.update(task_id=task['task_id'], project_id=task['project_id'], goal=task['goal'],
                         limits=task['limits'], error=json.loads(value.pop('error_json')) if value['error_json'] else None)
            result.append(value)
        return safe_value(result)


def run_detail(state, run_id):
    with connection(state) as db:
        row = db.execute('SELECT * FROM runs WHERE id=?', (run_id,)).fetchone()
        if not row:
            raise HTTPException(404, 'Run is not registered')
        run = dict(row)
        task = json.loads(run.pop('task_json'))
        stages = []
        for item in db.execute('SELECT name,attempt,status,started_at,finished_at,revision_hash,result_json FROM stages WHERE run_id=? ORDER BY attempt,started_at', (run_id,)):
            value = dict(item)
            result = json.loads(value.pop('result_json') or '{}')
            value.update(summary=result.get('result', {}).get('summary'), role_id=result.get('result', {}).get('role_id'),
                         error=result.get('error'), checks=[{'name': c['name'], 'exit_code': c['exit_code']} for c in result.get('checks', [])])
            stages.append(value)
        invocations = [dict(item) for item in db.execute('SELECT id,started_at,total_tokens,status,usage_json FROM invocations WHERE run_id=? ORDER BY started_at', (run_id,))]
        for value in invocations:
            value['usage'] = json.loads(value.pop('usage_json') or 'null')
        effects = [dict(item) for item in db.execute('SELECT name,status,result_json FROM effects WHERE run_id=?', (run_id,))]
        for effect in effects:
            effect['result'] = json.loads(effect.pop('result_json'))
        evidence_current = None
        if run['verified_hash'] and Path(run['workspace']).is_dir():
            try:
                evidence_current = current_revision(Path(run['workspace']), task['base_revision']) == run['verified_hash']
            except ExecutionError:
                evidence_current = False
        return safe_value({'run_id': run_id, 'task_id': task['task_id'], 'project_id': task['project_id'], 'goal': task['goal'],
                           'status': run['status'], 'agent_calls': run['calls'], 'attempts': run['attempt'],
                           'limits': task['limits'], 'stages': stages, 'invocations': invocations, 'effects': effects,
                           'error': json.loads(run['error_json'] or 'null'), 'workflow': task.get('workflow'),
                           'delivery_mode': task['policy']['delivery'], 'evidence_current': evidence_current})


def public_events(state, run_id, after=0):
    run_detail(state, run_id)
    with connection(state) as db:
        events = []
        for row in db.execute('SELECT id,timestamp,type,payload_json FROM events WHERE run_id=? AND id>? ORDER BY id LIMIT 200', (run_id, after)):
            payload = json.loads(row['payload_json'])
            if row['type'].startswith(('agent.', 'run.', 'control.', 'delivery.')):
                allowed = ('role_id', 'stage', 'message', 'category', 'activity', 'tool_calls', 'usage', 'operation', 'run_id')
                events.append({'id': row['id'], 'timestamp': row['timestamp'], 'type': row['type'],
                               'payload': {key: payload[key] for key in allowed if key in payload}})
            else:
                events.append({'id': row['id'], 'timestamp': row['timestamp'], 'type': row['type'],
                               'payload': {key: payload[key] for key in ('stage', 'attempt') if key in payload}})
        return safe_value(events)


def create_app(state: Path, access_token: str | None = None):
    """Default to loopback; nonlocal hosts additionally require an access token."""
    app = FastAPI(title='Dev Agent Kit Monitor')
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=['127.0.0.1', 'localhost', '[::1]'])

    @app.middleware('http')
    async def authenticate(request: Request, call_next):
        if access_token:
            import base64
            from fastapi.responses import Response
            authorization = request.headers.get('authorization', '')
            supplied = ''
            if authorization.startswith('Basic '):
                try:
                    supplied = base64.b64decode(authorization[6:], validate=True).decode().split(':', 1)[1]
                except (ValueError, IndexError, UnicodeDecodeError):
                    pass
            if not secrets.compare_digest(supplied.encode(), access_token.encode()):
                return Response(status_code=401, headers={'WWW-Authenticate': 'Basic realm="Dev Agent Kit"'})
        response = await call_next(request)
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Referrer-Policy'] = 'no-referrer'
        response.headers['Cache-Control'] = 'no-store'
        return response

    @app.get('/', response_class=HTMLResponse)
    def home():
        return (Path(__file__).parent / 'assets/monitor.html').read_text()

    @app.get('/health')
    def health():
        return {'status': 'ok'}

    @app.get('/api/runs')
    def runs():
        return list_runs(state)

    @app.get('/api/runs/{run_id}')
    def detail(run_id: str):
        return run_detail(state, run_id)

    @app.post('/api/runs/{run_id}/cancel')
    def cancel(run_id: str, request: Request):
        if request.headers.get('x-dev-agent-kit-control') != '1':
            raise HTTPException(403, 'Same-origin control header required')
        origin = request.headers.get('origin')
        if origin and origin.rstrip('/') != str(request.base_url).rstrip('/'):
            raise HTTPException(403, 'Cross-origin control denied')
        run_detail(state, run_id)
        store = Store(state)
        try:
            store.request_cancel(run_id)
        finally:
            store.close()
        return {'status': 'cancellation_requested', 'run_id': run_id}

    @app.get('/api/runs/{run_id}/events', response_class=EventSourceResponse)
    async def timeline(run_id: str, request: Request, after: int = 0):
        run_detail(state, run_id)
        try:
            cursor = max(0, after, int(request.headers.get('last-event-id', '0')))
        except ValueError:
            raise HTTPException(400, 'Invalid event cursor')
        while not await request.is_disconnected():
            events = await asyncio.to_thread(public_events, state, run_id, cursor)
            for event in events:
                cursor = event['id']
                yield ServerSentEvent(data=event, id=str(cursor))
            status = (await asyncio.to_thread(run_detail, state, run_id))['status']
            if status in {'succeeded', 'failed', 'blocked', 'cancelled'} and len(events) < 200:
                break
            await asyncio.sleep(0.5)

    return app
