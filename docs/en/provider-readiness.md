# Provider compatibility and optimization

**Languages:** English | [Português (Brasil)](../pt-br/provider-readiness.md)

Provider formats were checked on 2026-10-03; noninteractive execution was checked
on 2026-10-04 against Codex CLI 0.160.0. The
[machine-readable record](../../providers/compatibility.json) distinguishes format,
discovery and scoped behavior evidence. Claude Code and Copilot CLI were not on PATH.
The local adapter uses explicit profile/skill loading; automatic discovery is untested.
See the [scoped real evaluation](agent-validation.md) for the three-role guide task.

| Client | Project instructions | Skills | Agent profiles |
| --- | --- | --- | --- |
| Codex | `AGENTS.md` | `.agents/skills/*/SKILL.md` | `.codex/agents/*.toml` |
| Claude Code | `CLAUDE.md` routes to project sources | `.claude/skills/*/SKILL.md` | `.claude/agents/*.md` |
| Copilot | `.github/copilot-instructions.md` routes to project sources | `.agents/skills/*/SKILL.md` by client surface | `.github/agents/*.agent.md` |

Skill metadata uses `name`, `description` and Markdown with resources loaded as needed.
Native profiles preserve provider-specific tools and permissions.
[Agent Skills](https://agentskills.io/specification),
[Codex skills](https://learn.chatgpt.com/docs/build-skills),
[Codex agents](https://learn.chatgpt.com/docs/agent-configuration/subagents).

Claude profile `skills` can preload procedures, contributing to context cost.
Nested delegation depends on version/settings; the kit does not alter global
permissions, authentication or nesting to force compatibility.
[Claude skills](https://code.claude.com/docs/en/skills),
[Claude subagents](https://code.claude.com/docs/en/sub-agents).

Copilot may ignore unknown tool names; `web` is currently unavailable for cloud
agent. Required capabilities need verification on the selected surface.
[Agent configuration](https://docs.github.com/en/copilot/reference/custom-agents-configuration),
[Skills](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills),
[Instructions](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/add-custom-instructions/add-repository-instructions).

Claude/Copilot routers belong to this repository; packaging does not impose them
on target projects or replace existing instructions.

## Measured optimization

Skill descriptions now focus on task triggers. Budget/data/AI constraints remain
in loaded instructions and portable references. All 26 roles remain available;
28 skills include planning/extension workflows assigned to existing roles.

Provider/model substitution needs task evaluations. The result schema is the kit's
normalized domain contract; native structured-output formats may need adaptation.
Schema validation does not replace acceptance or checking the role registry. Adding
role IDs no longer requires editing the shared schema.

| Readiness level | Required evidence |
| --- | --- |
| File | Valid frontmatter/TOML, consistent references, reproducible generation |
| Discovery | Installed client/version finds expected skills/profiles |
| Capability | Tools, isolation, cancellation and output actually work |
| Behavior | Representative tasks meet acceptance and report failures |
| Optimization | Preserved quality with compared cost, latency and context |
| Operation | Recovery, duplicate effects and limits are verified |

File readiness is verified across generated providers. The local executor adds
real Git/check/storage integration tests and Codex task evaluation; those results
do not validate all roles, providers or workflows. A directory layout cannot certify
“100% optimized.” Track cost per accepted task, rework, duration, context usage
and recovery failures. Unavailable usage remains unknown.
