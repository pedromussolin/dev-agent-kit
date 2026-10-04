"""Exercise arbitrary workflow projection and responsibility boundaries."""

import unittest
from datetime import datetime, timezone

from dev_agent_kit.pipeline import executor_steps, group_steps, seconds, status
from dev_agent_kit.workflows import project_job


class PipelineTests(unittest.TestCase):
    def test_operations_group_by_responsibility_without_reordering(self):
        steps = [
            {"id": str(i), "name": name, "status": "success", "duration_seconds": 2}
            for i, name in enumerate(
                [
                    "Run actions/checkout@sha",
                    "Run actions/setup-python@sha",
                    "Load shared utilities",
                    "Enable declared package manager",
                    "Run pytest",
                    "Run unit tests",
                    "Publish invoice report",
                    "Update search index",
                ]
            )
        ]
        phases = group_steps(steps)
        self.assertEqual(
            [p["phase"] for p in phases],
            ["environment", "shared", "environment", "tests", "custom:6", "custom:7"],
        )
        self.assertEqual([len(p["steps"]) for p in phases], [2, 1, 1, 2, 1, 1])
        self.assertEqual(phases[3]["duration_seconds"], 4)

    def test_explicit_custom_phase_and_failure_location(self):
        phases = group_steps(
            [
                {
                    "name": "Read file",
                    "phase": "risk",
                    "phase_label": "Assess portfolio",
                    "status": "success",
                },
                {
                    "name": "Compute risk",
                    "phase": "risk",
                    "status": "failed",
                    "error": {"message": "Missing prices"},
                },
                {"name": "Deliver result", "status": "skipped"},
            ]
        )
        self.assertEqual(phases[0]["label"]["en"], "Assess portfolio")
        self.assertEqual(phases[0]["status"], "failed")
        self.assertEqual(phases[0]["errors"], ["Missing prices"])
        self.assertEqual(phases[1]["status"], "skipped")
        self.assertIsNone(phases[1]["duration_seconds"])

    def test_statuses_and_observed_duration(self):
        self.assertEqual(status("completed"), "pending")
        self.assertEqual(status("cancelled"), "failed")
        phase = group_steps(
            [
                {"name": "Run pytest", "status": "success"},
                {"name": "Run tests", "status": "running"},
            ]
        )[0]
        self.assertEqual(phase["status"], "running")
        self.assertEqual(
            seconds(
                "2026-10-04T10:00:00Z", now=datetime(2026, 10, 4, 10, 0, 8, tzinfo=timezone.utc)
            ),
            8,
        )
        self.assertIsNone(seconds("0001-01-01T00:00:00Z"))

    def test_duplicate_check_names_in_separate_components_use_distinct_evidence(self):
        task = {
            "workflow": [{"name": "develop", "role_id": "developer", "kind": "implement"}],
            "components": [
                {"name": component, "checks": [{"name": "unit", "argv": ["pytest"]}]}
                for component in ["api", "ui"]
            ],
        }
        steps = executor_steps(
            task,
            [
                {
                    "name": "checks",
                    "checks": [{"component": "api", "name": "unit", "exit_code": 0}],
                    "active_check": "ui:unit",
                }
            ],
            [],
        )
        self.assertEqual([s["status"] for s in steps[1:]], ["success", "running"])
        self.assertEqual(executor_steps(task, [], [], "failed")[1]["status"], "skipped")

    def test_single_github_action_unfolds_into_observed_quality_tests_and_build(self):
        import json

        source = {
            "id": 1,
            "name": "checks",
            "status": "completed",
            "conclusion": "failure",
            "steps": [
                {
                    "number": 1,
                    "name": "Run actual product checks",
                    "status": "completed",
                    "conclusion": "failure",
                    "started_at": "2026-10-04T10:00:00Z",
                    "completed_at": "2026-10-04T10:01:00Z",
                }
            ],
        }
        events = [
            {
                "id": "1",
                "name": "style",
                "phase": "quality",
                "argv": ["ruff", "check"],
                "status": "success",
                "stdout": "passed",
            },
            {
                "id": "2",
                "name": "unit",
                "phase": "tests",
                "argv": ["pytest"],
                "status": "failed",
                "stderr": "assertion failed",
                "error": "unit failed",
            },
            {"id": "3", "name": "bundle", "phase": "build", "argv": ["build"], "status": "skipped"},
        ]
        lines = [
            "2026-10-04T10:00:00.100Z DEV_AGENT_KIT_CHECK_EVENT " + json.dumps(event)
            for event in events
        ]
        job = project_job(source, lines)
        phases = group_steps(job["steps"])
        self.assertEqual([p["phase"] for p in phases], ["quality", "tests", "build"])
        self.assertEqual([p["status"] for p in phases], ["success", "failed", "skipped"])
        self.assertEqual(phases[1]["errors"], ["unit failed"])
        self.assertEqual(phases[1]["steps"][0]["logs"], "assertion failed")
        self.assertEqual(phases[1]["steps"][0]["source_step"], "Run actual product checks")
