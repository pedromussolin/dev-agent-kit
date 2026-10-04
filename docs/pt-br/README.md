# dev-agent-kit

**Idiomas:** [English](../../README.md) | Português (Brasil)

Regras de desenvolvimento e arquitetura para um SDLC conduzido por agentes,
adaptado às necessidades e ferramentas de cada projeto. Os projetos podem usar
Python, Go, JavaScript/TypeScript ou outras linguagens.

## Capacidades atuais

- [Regras modulares](../../rules/INDEX.md) direcionadas por [AGENTS.md](../../AGENTS.md).
- Escolha de stack e convenções idiomáticas na [regra 012](../../rules/012-polyglot-project-standards.md).
- Contratos e critérios de passagem do fluxo de agentes na [regra 013](../../rules/013-agent-sdlc-workflow.md).
- Templates de [tarefas](../../templates/sdlc-task.md), [papéis de agentes](../../templates/agent-role.md), [revisão](../../templates/pr-review.md) e [novas regras](../../templates/new-rule.md).
- Vinte e seis papéis canônicos e vinte e oito skills portáveis para produto, engenharia, design, segurança, cloud, DevOps, bancos, qualidade, operação, estratégia/engenharia/avaliações de IA e engenharia de dados.
- Perfis nativos gerados para Codex, Claude Code e GitHub Copilot, com empacotador em Python sem dependências externas e validação local/CI.
- Executor local em Python com estado SQLite, worktrees Git isolados, chamadas Codex limitadas, checks por componente, QA e revisão técnica antes da entrega configurável por diff/PR/merge/deploy, com painel e limites persistidos de tokens, ferramentas e loops.

## Agentes e skills

Leia o [guia de agentes e skills](agents-and-skills.md) para consultar catálogo,
formatos dos provedores, exemplos e as razões da organização.

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e .
python3 scripts/provider_profiles.py --check
python3 -m unittest discover -s tests -v
```

## Executar uma tarefa

O [guia do executor](local-executor.md) explica a configuração e os comandos
`validate`, `run`, `status` e `resume`. O primeiro adaptador usa a autenticação
ChatGPT existente no Codex, sem criar chaves de API. IA tem orçamento separado;
limites de chamadas, tempo e contexto não constituem um teto financeiro de cobrança.

```bash
python3 -m dev_agent_kit validate examples/execution/executor-runbook-validation.json
```

Esse registro de tarefa é específico deste checkout e revisão. Prepare uma tarefa
real para seu repositório antes de executá-la; a entrega é um diff/relatório isolado.
A [primeira avaliação real](agent-validation.md) registra a tarefa aceita pelos três
papéis, falhas anteriores e uso medido. Otimização de contexto e cenários de alteração
de código ainda precisam de comparações próprias.

## Plataforma local, dados e IA

O [guia de plataforma](local-platform-and-ai.md) apresenta ferramentas locais por
etapa, teto de R$ 100/mês para infraestrutura e orçamento de IA separado. Todos
os papéis/skills carregam esses padrões. A [decisão do executor](executor-decision.md)
explica a CLI Python, SQLite e os limites do primeiro incremento funcional.

## Planejamento modular e crescimento

Leia [arquitetura modular](modular-platform.md), [planejamento](planning-governance.md)
e [compatibilidade](provider-readiness.md) para integrações substituíveis, sessões
de decisão limitadas e o caminho do uso pessoal a um produto comercial.
Skills/contratos de planejamento e extensões estão disponíveis; sessões autônomas
e carregamento de plugins por manifesto ainda estão pendentes.

## Proposta de arquitetura

Leia a [arquitetura](architecture.md) para entender a separação entre orquestrador,
agentes, adaptadores de linguagem e adaptadores de entrega. O documento apresenta
contratos, recuperação de falhas, roadmap e decisões em aberto.

Perfis, skills, empacotador, workflow de validação e executor local inicial estão
implementados. Os 26 papéis podem ser escolhidos em tarefas sequenciais limitadas. Descoberta
nativa nos clientes, agendamento autônomo de produto e plugins ainda exigem
integração. Adaptadores de entrega e workflows Actions compartilhados estão
implementados; ativação remota exige revisão publicada, runner e configuração
do produto. Veja [entrega e Actions](delivery-and-actions.md). Validar formatos dos
provedores não comprova a qualidade dos agentes.
