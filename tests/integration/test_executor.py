"""Exercise transitions, isolation, evidence freshness and limits without paid inference."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

from dev_agent_kit.adapters import AgentResponse
from dev_agent_kit.contracts import ExecutionError
from dev_agent_kit.executor import Executor
from dev_agent_kit.processes import execute
from dev_agent_kit.workspace import current_revision, git

ROOT = Path(__file__).resolve().parents[2]


class ControlledAgent:
    """Stand in only for provider I/O while actual Git/checks/storage remain real."""

    def __init__(self, failure=None):
        self.calls = []
        self.implementations = 0
        self.failure = failure

    def preflight(self):
        return {"adapter": "controlled-test-adapter", "auth_mode": "test"}

    def execute(self, assignment):
        self.calls.append(assignment.role_id)
        if assignment.role_id == "developer":
            self.implementations += 1
            value = 0 if self.failure == "repair" and self.implementations == 1 else 42
            (assignment.workspace / "feature.py").write_text(f"VALUE = {value}\n")
        result = {
            "schema_version": 1,
            "task_id": assignment.task["task_id"],
            "role_id": assignment.role_id,
            "status": "completed",
            "summary": "Controlled test assignment",
            "artifacts": [],
            "evidence": [
                {
                    "claim": "Check evidence inspected",
                    "reference": "executor://checks",
                    "result": "observed",
                }
            ],
            "blocking_findings": [],
            "open_questions": [],
            "revision": assignment.context["current_revision"],
            "decisions": [],
        }
        if self.failure == "invalid":
            del result["status"]
        if self.failure == "wrong_task":
            result["task_id"] = "different-task"
        if self.failure == "stale" and assignment.role_id == "qa-engineer":
            result["revision"] = "old-revision"
        if self.failure == "qa_write" and assignment.role_id == "qa-engineer":
            (assignment.workspace / "feature.py").write_text("VALUE = 0\n")
        if self.failure == "review" and assignment.role_id == "technical-reviewer":
            result["blocking_findings"] = ["Controlled blocking finding"]
        return AgentResponse(
            result,
            {"input_tokens": 10, "output_tokens": 5},
            {"provider": "controlled-test-adapter"},
        )


class ExecutorFixture:
    """Create actual isolated Git and SQLite fixtures shared by runtime tests."""

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.repository = self.root / "repository"
        self.repository.mkdir()
        git(self.repository, "init", "-b", "main")
        git(self.repository, "config", "user.name", "Test Fixture")
        git(self.repository, "config", "user.email", "fixture@example.invalid")
        (self.repository / "README.md").write_text("Fixture project\n")
        (self.repository / ".gitignore").write_text("__pycache__/\n.env\n")
        (self.repository / "verify.py").write_text(
            "from feature import VALUE\nassert VALUE == 42\n"
        )
        git(self.repository, "add", ".")
        git(self.repository, "commit", "-m", "Initialize isolated test fixture")
        self.task = {
            "schema_version": 1,
            "task_id": "local-test-task",
            "project_id": "fixture",
            "repository": str(self.repository),
            "base_revision": git(self.repository, "rev-parse", "HEAD").strip(),
            "goal": "Implement a checked feature",
            "acceptance_criteria": ["Feature exposes the accepted value"],
            "context_files": ["README.md"],
            "components": [
                {
                    "name": "python-component",
                    "language": "python",
                    "working_directory": ".",
                    "checks": [
                        {
                            "name": "acceptance",
                            "argv": [sys.executable, "verify.py"],
                            "timeout_seconds": 5,
                        }
                    ],
                }
            ],
            "agent": {"adapter": "codex-cli", "auth_mode": "chatgpt"},
            "limits": {
                "max_attempts": 1,
                "max_agent_calls": 6,
                "agent_timeout_seconds": 10,
                "max_run_seconds": 60,
                "max_context_characters": 50000,
            },
            "policy": {
                "include_working_tree": True,
                "delivery": "diff",
                "allowed_paths": ["feature.py"],
                "authorization_reference": "Isolated integration-test fixture",
                "ai_spending": "existing_chatgpt_account",
                "infrastructure_monthly_cap_brl": 100,
            },
        }
        self.executors = []

    def tearDown(self):
        for executor in self.executors:
            executor.close()
        self.temporary.cleanup()

    def executor(self, adapter=None):
        executor = Executor(ROOT, self.root / "state", adapter or ControlledAgent())
        self.executors.append(executor)
        return executor


class ExecutorIntegrationTests(ExecutorFixture, unittest.TestCase):
    """Verify observable failures and recovery rather than matching prompt wording."""

    def test_missing_absolute_executable_blocks_before_model_call(self):
        self.task["components"][0]["checks"][0]["argv"] = [str(self.root / "missing-executable")]
        adapter = ControlledAgent()
        result = self.executor(adapter).start(self.task)
        self.assertEqual(result["error"]["category"], "tool_unavailable")
        self.assertEqual(adapter.calls, [])

    def test_success_preserves_source_and_ignored_credentials(self):
        (self.repository / "README.md").write_text("Authorized uncommitted input\n")
        (self.repository / ".env").write_text("Fixture credential excluded from snapshots")
        adapter = ControlledAgent()
        executor = self.executor(adapter)
        report = executor.start(self.task)
        self.assertEqual(report["status"], "succeeded", report["error"])
        self.assertEqual(adapter.calls, ["developer", "qa-engineer", "technical-reviewer"])
        self.assertFalse((self.repository / "feature.py").exists())
        self.assertEqual(
            (Path(report["workspace"]) / "README.md").read_text(), "Authorized uncommitted input\n"
        )
        self.assertFalse((Path(report["workspace"]) / ".env").exists())
        self.assertTrue(report["evidence_current"])
        self.assertIn("VALUE = 42", Path(report["delivery"]["patch"]).read_text())

    def test_failed_real_check_prevents_qa_and_completion(self):
        self.task["components"][0]["checks"][0]["argv"] = [
            sys.executable,
            "-c",
            "raise SystemExit(7)",
        ]
        adapter = ControlledAgent()
        report = self.executor(adapter).start(self.task)
        self.assertEqual(report["status"], "failed")
        self.assertEqual(adapter.calls, ["developer"])
        check = next(stage for stage in report["stages"] if stage["name"] == "checks")
        self.assertEqual(check["result"]["checks"][0]["exit_code"], 7)

    def test_bounded_repair_receives_failed_check_evidence(self):
        self.task["limits"]["max_attempts"] = 2
        adapter = ControlledAgent("repair")
        report = self.executor(adapter).start(self.task)
        self.assertEqual(report["status"], "succeeded", report["error"])
        self.assertEqual(adapter.implementations, 2)
        self.assertEqual(report["attempts"], 2)
        self.assertEqual(report["agent_calls"], 4)

    def test_invalid_result_and_wrong_identity_are_rejected(self):
        for failure in ("invalid", "wrong_task"):
            with self.subTest(failure=failure):
                report = self.executor(ControlledAgent(failure)).start(self.task)
                self.assertEqual(report["status"], "failed")
                self.assertEqual(report["error"]["category"], "invalid_result")

    def test_stale_qa_cannot_authorize_review(self):
        adapter = ControlledAgent("stale")
        report = self.executor(adapter).start(self.task)
        self.assertEqual(report["error"]["category"], "stale_evidence")
        self.assertNotIn("technical-reviewer", adapter.calls)

    def test_qa_source_mutation_is_detected(self):
        report = self.executor(ControlledAgent("qa_write")).start(self.task)
        self.assertEqual(report["status"], "failed")
        self.assertEqual(report["error"]["category"], "scope_violation")

    def test_blocking_review_remains_visible(self):
        report = self.executor(ControlledAgent("review")).start(self.task)
        self.assertEqual(report["status"], "failed")
        review = next(stage for stage in report["stages"] if stage["name"] == "review")
        self.assertEqual(
            review["result"]["result"]["blocking_findings"], ["Controlled blocking finding"]
        )

    def test_missing_component_tool_blocks_before_model_call(self):
        self.task["components"][0].update(name="go-component", language="go")
        self.task["components"][0]["checks"][0]["argv"] = [
            "kit-test-unavailable-go",
            "test",
            "./...",
        ]
        report = self.executor().start(self.task)
        self.assertEqual(report["status"], "blocked")
        self.assertEqual(report["error"]["category"], "tool_unavailable")
        self.assertEqual(report["agent_calls"], 0)

    def test_verification_cannot_mutate_source(self):
        self.task["components"][0]["checks"][0]["argv"] = [
            sys.executable,
            "-c",
            "from pathlib import Path; Path('feature.py').write_text('changed')",
        ]
        report = self.executor().start(self.task)
        self.assertEqual(report["error"]["category"], "checks_mutated_workspace")

    def test_real_command_timeout_prevents_completion(self):
        self.task["components"][0]["checks"][0].update(
            argv=[sys.executable, "-c", "import time; time.sleep(5)"], timeout_seconds=1
        )
        report = self.executor().start(self.task)
        self.assertEqual(report["error"]["category"], "timeout")
        self.assertEqual(report["status"], "failed")

    def test_call_limit_survives_resumption(self):
        self.task["limits"]["max_agent_calls"] = 2
        executor = self.executor()
        report = executor.start(self.task)
        self.assertEqual(report["status"], "failed")
        self.assertEqual(report["agent_calls"], 2)
        resumed = executor.resume(report["run_id"])
        self.assertEqual(resumed["status"], "failed")
        self.assertEqual(resumed["agent_calls"], 2)

    def test_changed_diff_invalidates_success_and_rechecks(self):
        adapter = ControlledAgent()
        executor = self.executor(adapter)
        report = executor.start(self.task)
        (Path(report["workspace"]) / "feature.py").write_text(
            "VALUE = 42\n# Additional inspected change\n"
        )
        self.assertEqual(executor.report(report["run_id"])["status"], "stale")
        resumed = executor.resume(report["run_id"])
        self.assertEqual(resumed["status"], "succeeded", resumed["error"])
        self.assertEqual(adapter.implementations, 1)
        self.assertEqual(resumed["agent_calls"], 5)
        self.assertNotEqual(report["verified_fingerprint"], resumed["verified_fingerprint"])

    def test_restart_reuses_current_success_without_new_calls(self):
        executor = self.executor()
        report = executor.start(self.task)
        next_adapter = ControlledAgent()
        restarted = self.executor(next_adapter)
        resumed = restarted.resume(report["run_id"])
        self.assertEqual(resumed["status"], "succeeded")
        self.assertEqual(next_adapter.calls, [])

    def test_interrupted_implementation_is_not_automatically_repeated(self):
        executor = self.executor()
        report = executor.start(self.task)
        revision = current_revision(Path(report["workspace"]), self.task["base_revision"])
        executor.store.start_stage(report["run_id"], 1, "implementation", revision)
        executor.store.status(report["run_id"], "running")
        resumed = executor.resume(report["run_id"])
        self.assertEqual(resumed["status"], "blocked")
        self.assertEqual(resumed["error"]["category"], "interrupted_implementation")
        self.assertEqual(resumed["agent_calls"], 3)

    def test_traversal_and_invalid_policy_are_rejected_before_execution(self):
        self.task["policy"]["allowed_paths"] = ["../outside.py"]
        with self.assertRaises(ExecutionError):
            self.executor().start(self.task)

    def test_actual_process_output_limit_is_enforced(self):
        with self.assertRaisesRegex(ExecutionError, "output"):
            execute(
                [sys.executable, "-c", "print('x' * 10000)"],
                self.repository,
                5,
                max_output_bytes=500,
            )


if __name__ == "__main__":
    unittest.main()
