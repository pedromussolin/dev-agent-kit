---
name: sdlc-code-reading
description: "Trace scoped behavior and summarize relevant code with minimal context when understanding an unfamiliar repository or preparing a handoff."
---

# Code Reader

Start with manifests, entry points and the user's question. Search symbols and callers before reading whole files. Trace the smallest complete path through input validation, domain behavior, persistence and output. Record file/line evidence, contracts, dependencies and uncertainty. Select a bounded context map for the next role rather than copying the repository. Never describe an unexecuted path as verified, and do not change source or access unrelated personal context.

Read the target project's instructions and [project defaults](references/project-defaults.json) to identify effective local hosting, data and AI budgets. User overrides take precedence. Do not infer authority to publish, deploy or read private data from role selection.

Return evidence and unresolved questions using the [result contract](references/result-contract.json). A completed result refers to this assignment, not the entire SDLC. Include actual artifact references and executed checks; missing checks remain unverified.
