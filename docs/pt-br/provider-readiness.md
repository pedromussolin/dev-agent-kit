# Compatibilidade e otimização dos provedores

**Idiomas:** [English](../en/provider-readiness.md) | Português (Brasil)

Formatos conferidos em 03/10/2026; execução não interativa verificada em 04/10/2026
com Codex CLI 0.160.0. O [registro legível por máquina](../../providers/compatibility.json)
separa evidências de formato, descoberta e comportamento com escopo definido.
Claude Code e Copilot CLI não estavam no PATH. O adaptador local carrega perfil/skill
explicitamente; descoberta automática ainda não foi testada.
Consulte a [avaliação real com escopo definido](agent-validation.md) da tarefa dos guias.

## Estrutura adotada

| Cliente | Instruções do projeto | Skills | Perfis de agente |
| --- | --- | --- | --- |
| Codex | `AGENTS.md` | `.agents/skills/*/SKILL.md` | `.codex/agents/*.toml` |
| Claude Code | `CLAUDE.md` encaminha à fonte do projeto | `.claude/skills/*/SKILL.md` | `.claude/agents/*.md` |
| Copilot | `.github/copilot-instructions.md` encaminha à fonte | `.agents/skills/*/SKILL.md` conforme cliente | `.github/agents/*.agent.md` |

O núcleo de skills usa `name`, `description` e instruções Markdown com recursos
sob demanda. É o padrão aberto Agent Skills. Perfis, ferramentas e permissões ficam
no formato nativo. [Especificação](https://agentskills.io/specification),
[Codex skills](https://learn.chatgpt.com/docs/build-skills),
[Codex agentes](https://learn.chatgpt.com/docs/agent-configuration/subagents).

Claude pode pré-carregar skills declaradas no perfil; isso deve entrar na medição
de contexto. Delegação aninhada depende de versão e configuração. O kit não altera
autenticação, profundidade de agentes ou permissões globais para forçar compatibilidade.
[Skills Claude](https://code.claude.com/docs/en/skills),
[Subagentes Claude](https://code.claude.com/docs/en/sub-agents).

No Copilot, nomes desconhecidos de ferramentas podem ser ignorados e o alias `web`
não está disponível atualmente no cloud agent. O adapter deve confirmar capacidades
obrigatórias. Um arquivo aceito não garante ferramentas disponíveis em toda interface.
[Configuração](https://docs.github.com/en/copilot/reference/custom-agents-configuration),
[Skills](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills),
[Instruções](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/add-custom-instructions/add-repository-instructions).

Os routers CLAUDE/Copilot são instruções deste repositório, não arquivos impostos
aos projetos de destino pelo empacotador. Configurações existentes são preservadas.

## O que significa otimizar

Descrições de skills ficaram focadas no gatilho da tarefa. Restrições de orçamento,
dados e IA continuam no corpo e nas referências portáveis, carregadas com o workflow.
O catálogo mantém todos os 29 papéis; sessões e tarefas escolhem quais usar. Hoje
há 31 skills porque planejamento e desenho de extensões complementam papéis existentes.

Uma troca de modelo/cliente precisa de avaliação por tarefa. O contrato de resultado
é o domínio normalizado do kit: cada provedor poderá exigir adaptação para seu formato
de saída estruturada. Validar schema não substitui critérios de aceite ou consulta ao
registro de papéis. Novos IDs de papel não exigem alterar o schema compartilhado.

| Nível | Evidência exigida |
| --- | --- |
| Arquivo | Frontmatter/TOML válidos, referências consistentes e geração reproduzível |
| Descoberta | Cliente/versão inicia e encontra as skills/perfis esperados |
| Capacidade | Ferramentas, isolamento, cancelamento e formato de saída funcionam |
| Comportamento | Tarefas representativas passam no aceite e reportam falhas corretamente |
| Otimização | Qualidade preservada com comparação de custo, latência e contexto |
| Operação | Reinício/recuperação, efeitos duplicados e limites verificados |

Os arquivos foram verificados nos provedores gerados. O executor local acrescenta
testes de integração com Git/checks/SQLite reais e avaliação de tarefa no Codex;
isso não valida todos os papéis, provedores ou workflows. “100% otimizado” não é uma
certificação fornecida por uma estrutura de diretórios. É uma meta contínua, com
métricas e regressões: custo por tarefa aceita, retrabalho, duração, consumo de
contexto e falhas de recuperação. Registre uso indisponível como desconhecido.
