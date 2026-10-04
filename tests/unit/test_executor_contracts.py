"""Verify native schema translation without changing normalized domain semantics."""

import copy
import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

from dev_agent_kit.contracts import native_output_schema

ROOT = Path(__file__).resolve().parents[2]


class NativeSchemaTests(unittest.TestCase):
    """Keep every native response node explicitly typed and strict."""

    def test_native_schema_preserves_result_validation(self):
        canonical = json.loads((ROOT / "contracts/agent-result.schema.json").read_text())
        before = copy.deepcopy(canonical)
        native = native_output_schema(canonical)
        self.assertEqual(before, canonical)
        Draft202012Validator.check_schema(native)
        result = {
            "schema_version": 1,
            "task_id": "local-fixture",
            "role_id": "developer",
            "status": "completed",
            "summary": "Fixture result",
            "artifacts": [{"kind": "diff", "reference": "fixture://diff", "revision": None}],
            "evidence": [
                {"claim": "Fixture assertion", "reference": "fixture://check", "result": "observed"}
            ],
            "blocking_findings": [],
            "open_questions": [],
            "revision": None,
            "decisions": [],
        }
        Draft202012Validator(native).validate(result)
        result["schema_version"] = 2
        self.assertTrue(list(Draft202012Validator(native).iter_errors(result)))

        def inspect(node):
            if isinstance(node, dict):
                if "enum" in node:
                    self.assertIn("type", node)
                if "properties" in node:
                    self.assertEqual(set(node["properties"]), set(node["required"]))
                for child in node.values():
                    inspect(child)
            elif isinstance(node, list):
                for child in node:
                    inspect(child)

        inspect(native)
