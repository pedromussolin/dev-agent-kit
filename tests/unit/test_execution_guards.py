"""Verify termination decisions and privacy against observable provider events."""

import unittest
from unittest.mock import patch

from dev_agent_kit.contracts import ExecutionError
from dev_agent_kit.guards import ExecutionGuard, public_item


class GuardTests(unittest.TestCase):
    def setUp(self):
        self.events = []
        self.revision = 'unchanged'
        self.limits = {'idle_timeout_seconds': 10, 'max_tokens_per_agent': 100, 'max_tool_calls': 2, 'max_repeated_tool_calls': 2}
        self.guard = ExecutionGuard(self.limits, self.events.append, lambda: None, lambda: self.revision)

    def test_repeated_outcome_stops_and_changed_source_allows_new_work(self):
        event = {'type': 'tool.completed', 'id': 'a', 'signature': 'read', 'outcome': 'same'}
        self.guard.event(event)
        self.revision = 'changed'
        self.guard.event({**event, 'id': 'b'})
        with self.assertRaises(ExecutionError) as caught:
            self.guard.event({**event, 'id': 'c'})
        self.assertEqual(caught.exception.category, 'loop_detected')

    def test_duplicate_notifications_do_not_consume_extra_tool_budget(self):
        self.guard.event({'type': 'tool.started', 'id': 'a'})
        self.guard.event({'type': 'tool.started', 'id': 'a'})
        self.guard.event({'type': 'tool.started', 'id': 'b'})
        with self.assertRaises(ExecutionError) as caught:
            self.guard.event({'type': 'tool.started', 'id': 'c'})
        self.assertEqual(caught.exception.category, 'tool_budget_exhausted')

    def test_usage_is_emitted_before_threshold_interrupt(self):
        with self.assertRaises(ExecutionError) as caught:
            self.guard.event({'type': 'usage', 'usage': {'input_tokens': 90, 'output_tokens': 10}})
        self.assertEqual(caught.exception.category, 'token_budget_exhausted')
        self.assertEqual(self.events[-1]['usage']['output_tokens'], 10)

    def test_idle_and_operator_cancellation_stop_work(self):
        with patch('dev_agent_kit.guards.time.monotonic', return_value=self.guard.last_activity + 11):
            with self.assertRaises(ExecutionError) as caught:
                self.guard.tick()
        self.assertEqual(caught.exception.category, 'idle_timeout')
        self.guard.external_tick = lambda: (_ for _ in ()).throw(ExecutionError('cancelled', 'Operator stop'))
        with self.assertRaises(ExecutionError) as caught:
            self.guard.tick()
        self.assertEqual(caught.exception.category, 'cancelled')

    def test_reasoning_and_raw_commands_are_not_public_events(self):
        self.assertIsNone(public_item({'type': 'reasoning', 'text': 'private'}, True))
        self.assertIsNone(public_item({'type': 'agentMessage', 'phase': 'final_answer', 'text': 'result'}, True))
        event = public_item({'type': 'commandExecution', 'id': 'tool', 'command': 'private-command', 'aggregatedOutput': 'private-output'}, True)
        self.assertNotIn('private', str(event))
        self.assertEqual(public_item({'type': 'agentMessage', 'phase': 'commentary', 'text': 'Reading files'}, True)['message'], 'Reading files')
