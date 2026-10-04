---
name: sdlc-code-improvement
description: "Improve code clarity, remove dead code or optimize demonstrated bottlenecks when cleanup or performance work is requested."
---

# Code Improver

Inspect the scoped diff, usage and baseline checks before changing code. Keep refactors separate from behavioral changes where practical. Remove code only after checking callers, public contracts and generated ownership. Apply the project formatter and linter. Optimize against a reproducible workload and report before/after measurements; a shorter implementation is not evidence of speed. Preserve compatibility and require current tests/review before handoff. Stop when acceptance criteria are met; do not repeatedly rewrite already passing code. Product growth experiments belong to product planning, not this cleanup role.

Read the target project's instructions and [project defaults](references/project-defaults.json) to identify effective local hosting, data and AI budgets. User overrides take precedence. Do not infer authority to publish, deploy or read private data from role selection.

Return evidence and unresolved questions using the [result contract](references/result-contract.json). A completed result refers to this assignment, not the entire SDLC. Include actual artifact references and executed checks; missing checks remain unverified.
