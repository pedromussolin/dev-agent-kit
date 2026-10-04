"""Exercise persistent budgets, role workflows and no-progress recovery with real state."""

import unittest

from tests.integration.test_executor import ControlledAgent, ExecutorFixture


class ExecutionControlTests(ExecutorFixture, unittest.TestCase):
    # Reuse fixture creation without rediscovering the parent's complete test suite.
    def test_project_budget_survives_new_runs(self):
        self.task["limits"]["max_project_calls_per_day"] = 2
        adapter = ControlledAgent()
        executor = self.executor(adapter)
        first = executor.start(self.task)
        self.assertEqual(first["error"]["category"], "project_budget_exhausted")
        self.assertEqual(first["agent_calls"], 2)
        second = executor.start(self.task)
        self.assertEqual(second["error"]["category"], "project_budget_exhausted")
        self.assertEqual(second["agent_calls"], 0)
        self.assertEqual(len(adapter.calls), 2)

    def test_observed_tokens_stop_subsequent_stages_and_survive_resume(self):
        self.task["limits"]["max_total_tokens"] = 20
        executor = self.executor()
        result = executor.start(self.task)
        self.assertEqual(result["error"]["category"], "token_budget_exhausted")
        self.assertEqual(result["budget"]["run_tokens"], 30)
        self.assertEqual(result["agent_calls"], 2)
        self.assertEqual(executor.resume(result["run_id"])["agent_calls"], 2)

    def test_identical_failed_repairs_stop_before_all_attempts(self):
        self.task["limits"]["max_attempts"] = 5
        self.task["limits"]["max_agent_calls"] = 15
        self.task["components"][0]["checks"][0]["argv"] = ["python3", "-c", "raise SystemExit(7)"]
        result = self.executor().start(self.task)
        self.assertEqual(result["error"]["category"], "no_progress")
        self.assertEqual(result["agent_calls"], 2)
        self.assertEqual(result["attempts"], 2)

    def test_planning_specialists_feed_handoffs_without_writes(self):
        self.task["workflow"] = [
            {"name": "architecture", "role_id": "software-architect", "kind": "plan"},
            {"name": "implementation", "role_id": "developer", "kind": "implement"},
            {"name": "security", "role_id": "security-engineer", "kind": "verify"},
            {"name": "qa", "role_id": "qa-engineer", "kind": "verify"},
            {"name": "review", "role_id": "technical-reviewer", "kind": "verify"},
        ]
        adapter = ControlledAgent()
        result = self.executor(adapter).start(self.task)
        self.assertEqual(result["status"], "succeeded", result["error"])
        self.assertEqual(
            adapter.calls,
            [
                "software-architect",
                "developer",
                "security-engineer",
                "qa-engineer",
                "technical-reviewer",
            ],
        )

    def test_cancel_is_persisted_and_stops_before_new_stage(self):
        adapter = ControlledAgent()
        executor = self.executor(adapter)
        original = adapter.execute

        def execute(assignment):
            response = original(assignment)
            run_id = executor.store.connection.execute(
                "SELECT id FROM runs ORDER BY created_at DESC LIMIT 1"
            ).fetchone()[0]
            executor.store.request_cancel(run_id)
            return response

        adapter.execute = execute
        result = executor.start(self.task)
        self.assertEqual(result["status"], "cancelled")
        self.assertEqual(result["agent_calls"], 1)
        self.assertEqual(executor.resume(result["run_id"])["agent_calls"], 1)

    def test_needs_input_is_not_repaired_as_a_code_defect(self):
        adapter = ControlledAgent()
        original = adapter.execute

        def execute(assignment):
            response = original(assignment)
            response.result["status"] = "needs_input"
            response.result["open_questions"] = ["Missing product decision"]
            return response

        adapter.execute = execute
        result = self.executor(adapter).start(self.task)
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["error"]["category"], "needs_input")
        self.assertEqual(result["agent_calls"], 1)
