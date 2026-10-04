"""Expose task validation, execution, inspection and safe resumption."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import os
import shlex
import time

from .contracts import ExecutionError, read_task
from .executor import Executor
from .storage import Store
from .workspace import git


def progress(event):
    """Render public activity while leaving the final machine-readable output intact."""
    if event['type'] == 'usage':
        return
    prefix = event.get('role_id', 'executor')
    message = event.get('message') or event.get('activity') or event['type']
    print(f"[{prefix}] {message}", file=sys.stderr, flush=True)


def main() -> int:
    """Return failure for blocked/failed execution while preserving its report."""
    parser = argparse.ArgumentParser(description="Run a local, evidence-driven SDLC task")
    parser.add_argument("--kit-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--state-dir", type=Path, default=Path.home() / ".local/state/dev-agent-kit")
    parser.add_argument('--quiet', action='store_true', help='Suppress live terminal activity')
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("validate", "run"):
        command = commands.add_parser(name)
        command.add_argument("task", type=Path)
    for name in ("status", "resume"):
        command = commands.add_parser(name)
        command.add_argument("run_id")
    cancel = commands.add_parser('cancel')
    cancel.add_argument('run_id')
    commands.add_parser('runs')
    inspect = commands.add_parser('inspect')
    inspect.add_argument('repository', type=Path)
    watch = commands.add_parser('watch')
    watch.add_argument('run_id')
    watch.add_argument('--json', action='store_true', help='Emit public events as JSON lines')
    serve = commands.add_parser('serve')
    serve.add_argument('--host', choices=['127.0.0.1', 'localhost', '0.0.0.0'], default='127.0.0.1')
    serve.add_argument('--port', type=int, default=8765)
    init = commands.add_parser('init')
    init.add_argument('task', type=Path)
    init.add_argument('--repository', type=Path, required=True)
    init.add_argument('--task-id', required=True)
    init.add_argument('--goal', required=True)
    init.add_argument('--allow', action='append', required=True)
    init.add_argument('--check', action='append', required=True, help='A command parsed into an argument list, never evaluated as a shell')
    init.add_argument('--context', action='append', default=[])
    init.add_argument('--delivery', choices=['diff', 'pull_request', 'merge', 'deploy'], default='diff')
    init.add_argument('--delivery-config', type=Path)
    init.add_argument('--max-total-tokens', type=int, default=200000)
    args = parser.parse_args()
    executor = None
    try:
        if args.command == 'inspect':
            from .stacks import detect_components
            print(json.dumps({'repository': str(args.repository.resolve()), 'components': detect_components(args.repository),
                              'note': 'Suggestions only; select and authorize checks in a real task.'}, indent=2))
            return 0
        if args.command == 'init':
            repository = args.repository.resolve()
            task = {'schema_version': 1, 'task_id': args.task_id, 'project_id': repository.name,
                    'repository': str(repository), 'base_revision': git(repository, 'rev-parse', 'HEAD').strip(),
                    'goal': args.goal, 'acceptance_criteria': [args.goal], 'context_files': args.context,
                    'components': [{'name': 'project', 'language': 'configured', 'working_directory': '.',
                                    'checks': [{'name': 'check-' + str(index + 1), 'argv': shlex.split(command), 'timeout_seconds': 120}
                                               for index, command in enumerate(args.check)]}],
                    'agent': {'adapter': 'codex-app-server', 'auth_mode': 'chatgpt'},
                    'limits': {'max_attempts': 2, 'max_agent_calls': 6, 'agent_timeout_seconds': 600,
                               'max_run_seconds': 2400, 'max_context_characters': 40000, 'max_total_tokens': args.max_total_tokens},
                    'policy': {'include_working_tree': args.delivery == 'diff', 'delivery': args.delivery,
                               'allowed_paths': args.allow, 'authorization_reference': 'Task prepared by the operator through the CLI; execution requires invoking run.',
                               'ai_spending': 'existing_chatgpt_account', 'infrastructure_monthly_cap_brl': 100}}
            if args.delivery_config:
                task['delivery'] = json.loads(args.delivery_config.read_text())
            from .contracts import normalize_task
            task = normalize_task(task, args.kit_root)
            with args.task.open('x') as output:
                output.write(json.dumps(task, indent=2) + '\n')
            print(json.dumps({'status': 'created', 'task_id': task['task_id'], 'task': str(args.task)}))
            return 0
        if args.command == 'serve':
            token = os.environ.get('DEV_AGENT_KIT_MONITOR_TOKEN')
            if args.host == '0.0.0.0' and not token:
                raise ExecutionError('configuration_error', 'Nonloopback binding requires DEV_AGENT_KIT_MONITOR_TOKEN')
            try:
                import uvicorn
                from .monitor import create_app
            except ImportError as error:
                raise ExecutionError('tool_unavailable', 'Install the monitor extra: pip install -e .[monitor]') from error
            store = Store(args.state_dir)
            store.close()
            uvicorn.run(create_app(args.state_dir, token), host=args.host, port=args.port, access_log=False)
            return 0
        if args.command in {'cancel', 'watch', 'runs'}:
            store = Store(args.state_dir)
            try:
                if args.command == 'cancel':
                    store.request_cancel(args.run_id)
                    print(json.dumps({'status': 'cancellation_requested', 'run_id': args.run_id}))
                elif args.command == 'runs':
                    print(json.dumps([dict(row) for row in store.connection.execute('SELECT id,status,created_at,calls,attempt FROM runs ORDER BY created_at DESC LIMIT 100')], indent=2))
                else:
                    cursor = 0
                    while True:
                        events = store.events(args.run_id, cursor, 1000)
                        for event in events:
                            cursor = event['id']
                            if args.json:
                                print(json.dumps({'id': event['id'], 'timestamp': event['timestamp'], 'type': event['type'],
                                                  'payload': {key: value for key, value in event['payload'].items()
                                                              if key in {'role_id', 'stage', 'message', 'category', 'activity', 'tool_calls', 'usage', 'operation'}}}), flush=True)
                            elif event['type'].startswith('agent.'):
                                progress({'type': event['type'].split('.', 1)[1], **event['payload']})
                        if store.get(args.run_id)['status'] in {'succeeded', 'failed', 'blocked', 'cancelled'} and len(events) < 1000:
                            break
                        time.sleep(0.5)
            finally:
                store.close()
            return 0
        if args.command == "validate":
            task = read_task(args.task, args.kit_root)
            print(json.dumps({"status": "valid", "task_id": task["task_id"], "note": "Format only; runtime checks occur before execution"}))
            return 0
        executor = Executor(args.kit_root, args.state_dir, on_event=None if args.quiet else progress)
        if args.command == "run":
            report = executor.start(read_task(args.task, args.kit_root))
        elif args.command == "resume":
            report = executor.resume(args.run_id)
        else:
            report = executor.report(args.run_id)
        print(json.dumps({"run_id": report["run_id"], "task_id": report["task_id"], "status": report["status"],
                          "agent_calls": report["agent_calls"], "workspace": report["workspace"], "error": report["error"],
                          "report": str(args.state_dir.resolve() / "runs" / report["run_id"] / "report.json")}, indent=2))
        return 0 if report["status"] == "succeeded" or args.command == "status" else 1
    except (ExecutionError, OSError, ValueError, KeyError) as error:
        print(json.dumps({"status": "failed", "category": getattr(error, "category", "configuration_error"), "message": str(error)}), file=sys.stderr)
        return 1
    finally:
        if executor is not None:
            executor.close()
