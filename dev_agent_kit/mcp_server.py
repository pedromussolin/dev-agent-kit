"""Expose the same monitoring repository over the official local MCP transport."""

from pathlib import Path

from .monitor_repository import SQLiteMonitoringRepository
from .workflows import list_workflows, workflow_detail


def create_server(state: Path, allow_control=False, repository=None):
    from mcp.server import MCPServer
    from mcp.server.mcpserver.exceptions import ToolError
    from mcp.types import ToolAnnotations

    reader = repository or SQLiteMonitoringRepository(state)
    server = MCPServer(
        "Dev Agent Kit",
        instructions="Inspect public execution evidence. No SQL, shell, model execution or deployment tool is exposed.",
    )
    read_only = ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=False)

    def read(operation, *args):
        try:
            return operation(*args)
        except (ValueError, OSError, KeyError) as error:
            raise ToolError("Evidence unavailable: " + str(error)) from None

    @server.tool(annotations=read_only)
    def list_agent_runs() -> list[dict]:
        """List recent agent tasks and their observed outcomes."""
        return read(reader.list_runs)

    @server.tool(annotations=read_only)
    def get_agent_run(run_id: str) -> dict:
        """Read logical phases, public check details and measured token usage."""
        return read(reader.run_detail, run_id)

    @server.tool(annotations=read_only)
    def get_agent_events(run_id: str, after: int = 0) -> list[dict]:
        """Read bounded public progress, excluding private reasoning and prompts."""
        if after < 0:
            raise ToolError("Event cursor must be nonnegative")
        return read(reader.public_events, run_id, after)

    @server.tool(annotations=read_only)
    def list_pipeline_runs() -> list[dict]:
        """List locally synchronized CI/CD snapshots and their freshness timestamps."""
        return read(list_workflows, state)

    @server.tool(annotations=read_only)
    def get_pipeline_run(identity: str) -> dict:
        """Read arbitrary jobs grouped into logical responsibilities."""
        return read(workflow_detail, state, identity)

    if allow_control:

        @server.tool(
            annotations=ToolAnnotations(
                readOnlyHint=False, destructiveHint=True, openWorldHint=False
            )
        )
        def cancel_agent_run(run_id: str) -> dict:
            """Request cancellation; available only when the operator enabled control."""
            read(reader.request_cancel, run_id)
            return {"status": "cancellation_requested", "run_id": run_id}

    return server
