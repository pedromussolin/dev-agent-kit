---
name: sdlc-extension-design
description: "Design a replaceable kit adapter or tool extension when a new provider, stack, database, delivery or telemetry integration needs a stable capability contract."
---

# Extension Design

Read target-project instructions, the caller's objective and existing evidence.
Read [project defaults](references/project-defaults.json) for local hosting,
the BRL 100/month infrastructure cap and separate AI budget; explicit user/project
settings take precedence. Unspecified AI spending is not unlimited.

## Procedure

1. State the unmet requirement and compare reuse of an existing adapter, a small composition, and a new extension.
2. Define the stable request/result contract and required/optional capabilities. Keep provider SDK types outside the domain; unsupported capabilities remain unavailable rather than silently degrading.
3. Specify a versioned manifest, configuration schema and explicit implementation binding. Use MCP for interoperable external tools when appropriate; it does not replace workflow or provider adapters.
4. Declare filesystem/network/credential scope, cancellation, deadlines, retry/idempotency behavior, sanitization and data retention. In-process code is trusted code; a manifest is not a sandbox.
5. Define a conformance suite for success/failure, malformed results, cancellation and compatibility. A tool proposal enters planning/backlog; installation, spending and live mutations follow existing task authority.

## Deliverable and acceptance

The proposed manifest validates against the bundled contract; capability/permission boundaries and conformance scenarios are explicit. A schema or manifest alone does not implement installation or an executable plugin loader.

Use the [specialized artifact contract](references/plugin-manifest.schema.json) for the planning
or extension artifact. Return the role's [result contract](references/result-contract.json)
with references to that artifact, observed evidence and outstanding questions.
No background scheduler, model calls or deployments are supplied by this skill.
