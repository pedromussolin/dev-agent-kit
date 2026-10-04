"""Check MCP capability registration and real stdio JSON-RPC transport."""

import sys
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient
from mcp import Client, StdioServerParameters

from dev_agent_kit.mcp_server import create_server
from dev_agent_kit.monitor import create_app
from dev_agent_kit.storage import Store


class MemoryReader:
    def list_runs(self):
        return [{"id": "memory-run", "status": "running"}]

    def run_detail(self, run_id):
        return {"run_id": run_id, "status": "running", "phases": []}

    def public_events(self, run_id, after=0):
        return []

    def request_cancel(self, run_id):
        self.cancelled = run_id


class MCPTests(unittest.IsolatedAsyncioTestCase):
    async def test_http_and_mcp_share_an_injected_repository_without_sqlite(self):
        with tempfile.TemporaryDirectory() as directory:
            reader = MemoryReader()
            http = TestClient(
                create_app(Path(directory), "test-password", repository=reader),
                base_url="http://localhost",
            )
            self.assertEqual(http.get("/api/runs").status_code, 401)
            data = http.get("/api/runs", auth=("local", "test-password")).json()
            async with Client(create_server(Path(directory), repository=reader)) as client:
                tools = await client.list_tools()
                names = {t.name for t in tools.tools}
                self.assertIn("get_agent_run", names)
                self.assertNotIn("cancel_agent_run", names)
                result = await client.call_tool("list_agent_runs")
                self.assertFalse(result.is_error)
                self.assertEqual(result.structured_content["result"], data)
                invalid = await client.call_tool(
                    "get_agent_events", {"run_id": "memory-run", "after": -1}
                )
                self.assertTrue(invalid.is_error)
            async with Client(create_server(Path(directory), True, reader)) as client:
                result = await client.call_tool("cancel_agent_run", {"run_id": "memory-run"})
                self.assertFalse(result.is_error)
                self.assertEqual(reader.cancelled, "memory-run")

    async def test_cli_starts_a_real_stdio_server(self):
        with tempfile.TemporaryDirectory() as directory:
            Store(Path(directory)).close()
            params = StdioServerParameters(
                command=sys.executable,
                args=["-m", "dev_agent_kit", "--state-dir", directory, "mcp"],
            )
            async with Client(params) as client:
                result = await client.call_tool("list_agent_runs")
                self.assertFalse(result.is_error)
                self.assertEqual(result.structured_content["result"], [])
                result = await client.call_tool("get_pipeline_run", {"identity": "../private"})
                self.assertTrue(result.is_error)
