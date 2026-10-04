"""HTTP presentation over an injectable monitoring repository."""

import asyncio
import secrets
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.sse import EventSourceResponse, ServerSentEvent
from starlette.middleware.trustedhost import TrustedHostMiddleware

from .monitor_repository import MonitoringRepository, ReadModelError, SQLiteMonitoringRepository
from .workflows import list_workflows, workflow_detail


def create_app(
    state: Path, access_token: str | None = None, repository: MonitoringRepository | None = None
):
    """Default to loopback; nonlocal hosts additionally require an access token."""
    reader = repository or SQLiteMonitoringRepository(state)
    app = FastAPI(title="Dev Agent Kit Monitor")

    @app.exception_handler(ReadModelError)
    async def repository_error(request, error):
        return JSONResponse(status_code=error.status_code, content={"detail": str(error)})

    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost", "[::1]"])

    @app.middleware("http")
    async def authenticate(request: Request, call_next):
        if access_token:
            import base64

            from fastapi.responses import Response

            authorization = request.headers.get("authorization", "")
            supplied = ""
            if authorization.startswith("Basic "):
                try:
                    supplied = (
                        base64.b64decode(authorization[6:], validate=True).decode().split(":", 1)[1]
                    )
                except (ValueError, IndexError, UnicodeDecodeError):
                    pass
            if not secrets.compare_digest(supplied.encode(), access_token.encode()):
                return Response(
                    status_code=401, headers={"WWW-Authenticate": 'Basic realm="Dev Agent Kit"'}
                )
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Cache-Control"] = "no-store"
        return response

    @app.get("/", response_class=HTMLResponse)
    def home():
        return (Path(__file__).parent / "assets/monitor.html").read_text()

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.get("/assets/{name}")
    def frontend_asset(name: str):
        media = {
            "pipeline.js": "text/javascript",
            "dashboard.js": "text/javascript",
            "monitor.css": "text/css",
        }
        if name not in media:
            raise HTTPException(404, "Asset unavailable")
        return Response(
            (Path(__file__).parent / "assets" / name).read_text(), media_type=media[name]
        )

    @app.get("/api/workflows")
    def workflows():
        return list_workflows(state)

    @app.get("/api/workflows/{identity}")
    def workflow(identity: str):
        try:
            return workflow_detail(state, identity)
        except FileNotFoundError:
            raise HTTPException(404, "Workflow snapshot unavailable")
        except ValueError:
            raise HTTPException(400, "Invalid workflow identity")

    @app.get("/api/runs")
    def runs():
        return reader.list_runs()

    @app.get("/api/runs/{run_id}")
    def detail(run_id: str):
        return reader.run_detail(run_id)

    @app.post("/api/runs/{run_id}/cancel")
    def cancel(run_id: str, request: Request):
        if request.headers.get("x-dev-agent-kit-control") != "1":
            raise HTTPException(403, "Same-origin control header required")
        origin = request.headers.get("origin")
        if origin and origin.rstrip("/") != str(request.base_url).rstrip("/"):
            raise HTTPException(403, "Cross-origin control denied")
        reader.run_detail(run_id)
        reader.request_cancel(run_id)
        return {"status": "cancellation_requested", "run_id": run_id}

    @app.get("/api/runs/{run_id}/events", response_class=EventSourceResponse)
    async def timeline(run_id: str, request: Request, after: int = 0):
        reader.run_detail(run_id)
        try:
            cursor = max(0, after, int(request.headers.get("last-event-id", "0")))
        except ValueError:
            raise HTTPException(400, "Invalid event cursor")
        while not await request.is_disconnected():
            events = await asyncio.to_thread(reader.public_events, run_id, cursor)
            for event in events:
                cursor = event["id"]
                yield ServerSentEvent(data=event, id=str(cursor))
            status = (await asyncio.to_thread(reader.run_detail, run_id))["status"]
            if status in {"succeeded", "failed", "blocked", "cancelled"} and len(events) < 200:
                break
            await asyncio.sleep(0.5)

    return app
