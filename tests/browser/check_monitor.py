"""Check real browser rendering, expansion, status labels and untrusted logs."""

import json
import os
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from urllib.request import urlopen

from playwright.sync_api import sync_playwright

from dev_agent_kit.storage import Store


def main():
    with tempfile.TemporaryDirectory() as directory:
        state = Path(directory)
        Store(state).close()
        (state / "workflows").mkdir()
        steps = [
            {
                "id": "1",
                "name": "Run formatter",
                "phase": "quality",
                "status": "success",
                "duration_seconds": 3,
            },
            {
                "id": "2",
                "name": "Run linter",
                "phase": "quality",
                "status": "failed",
                "duration_seconds": 2,
                "error": "Unused import",
                "argv": ["ruff", "check"],
                "logs": '<img src=x onerror="window.injected=true">',
            },
        ] + [
            {
                "id": str(i),
                "name": "Operation " + str(i),
                "phase": "custom:" + str(i),
                "phase_label": "Custom responsibility " + str(i),
                "status": status,
            }
            for i, status in enumerate(["pending", "running", "success", "skipped"], start=3)
        ]
        snapshot = {
            "id": "fixture",
            "name": "Arbitrary pipeline",
            "repository": "example/product",
            "status": "failed",
            "updated_at": "2026-10-04T10:00:00Z",
            "url": "https://example.invalid/run",
            "jobs": [
                {
                    "id": "1",
                    "name": "Product checks",
                    "status": "failed",
                    "steps": steps,
                    "logs": "",
                }
            ],
        }
        (state / "workflows/fixture.json").write_text(json.dumps(snapshot))
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            port = sock.getsockname()[1]
        process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "dev_agent_kit",
                "--state-dir",
                directory,
                "serve",
                "--port",
                str(port),
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            env={**os.environ, "DEV_AGENT_KIT_MONITOR_TOKEN": "browser-test-password"},
        )
        try:
            for _ in range(100):
                if process.poll() is not None:
                    raise RuntimeError(process.stderr.read().decode())
                try:
                    urlopen(f"http://127.0.0.1:{port}/health", timeout=0.2)
                except Exception as error:
                    if getattr(error, "code", None) == 401:
                        break
                    time.sleep(0.05)
            else:
                raise RuntimeError("Monitor did not start")
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch()
                context = browser.new_context(
                    http_credentials={"username": "local", "password": "browser-test-password"}
                )
                page = context.new_page()
                errors = []
                page.on("pageerror", lambda error: errors.append(str(error)))
                page.goto(f"http://127.0.0.1:{port}/")
                page.get_by_role("button", name="Arbitrary pipeline", exact=False).click()
                page.wait_for_selector(".phase-card")
                assert page.locator(".phase-card").count() == 5
                assert page.locator(".phase-card.failed").count() == 1
                assert page.get_by_text("Unused import", exact=False).first.is_visible()
                assert page.get_by_text("Duração: 5s", exact=True).is_visible()
                assert page.locator("details[open]").count() == 0
                page.locator(".phase-card.failed summary").click()
                assert page.locator(".phase-card.failed pre").last.inner_text().startswith("<img")
                assert page.locator("img").count() == 0
                assert not page.evaluate("Boolean(window.injected)")
                page.locator("#language").select_option("en")
                page.wait_for_selector(".phase-card.failed details[open]")
                assert page.get_by_text("Checking code quality", exact=True).is_visible()
                page.set_viewport_size({"width": 390, "height": 844})
                assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
                assert not errors, errors
                page.screenshot(path="/tmp/dev-agent-kit-pipeline.png", full_page=True)
                browser.close()
        finally:
            process.terminate()
            process.communicate(timeout=10)
    print(
        "Browser checks passed: dynamic grouping, all statuses, error, duration, expansion, language, mobile, XSS."
    )


if __name__ == "__main__":
    main()
