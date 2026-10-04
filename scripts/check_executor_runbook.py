"""Check the real executor onboarding deliverable's minimum command coverage."""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
for language in ("en", "pt-br"):
    path = ROOT / "docs" / language / "local-executor.md"
    text = path.read_text()
    for command in ("validate", "run", "status", "resume"):
        if not re.search(r"python3 -m dev_agent_kit[^\n]*\b" + command + r"\b", text):
            raise SystemExit(f"Missing runnable command coverage: {language}/{command}")
    if "--state-dir" not in text or "--kit-root" not in text:
        raise SystemExit(f"Missing executor directory configuration: {language}")
    if "existing_chatgpt_account" not in text:
        raise SystemExit(f"Missing account-based execution policy: {language}")
print("Executor runbook command/policy coverage passed in English and Portuguese.")
