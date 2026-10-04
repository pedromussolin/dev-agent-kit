# Extension proposal

This is a design record, not an installed plugin. Use the internal
`contracts/plugin-manifest.schema.json` for a proposed manifest; native provider
plugin formats remain separate packaging targets.

- Problem and measurable expected improvement.
- Existing alternatives and why a new integration is justified.
- Extension kind, stable ID/version and host protocol major version.
- Required/optional capabilities and caller-owned configuration.
- Input/output/configuration schemas with resolvable versioned references.
- Implementation binding: trusted in-process adapter, command, MCP or HTTP.
- Filesystem/network/credential scope; keep secret values out of the manifest.
- Deadlines, cancellation, retry/idempotency, errors and unavailable usage.
- Conformance evidence for success, malformed results, timeouts and incompatible versions.
- Dependency/resource requirements, license review and total infrastructure/AI costs.
- Enable/disable/update procedure, migrations and rollback compatibility.
- Planning decision and real backlog reference before implementation/activation.
