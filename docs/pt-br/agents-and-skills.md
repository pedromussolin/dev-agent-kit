# Agentes, skills e perfis de provedores

**Idiomas:** [English](../en/agents-and-skills.md) | Português (Brasil)

Formatos dos provedores conferidos em 03/10/2026. Perfis, empacotamento e executor
local persistente inicial estão implementados. Os demais fluxos de SDLC seguem planejados.

## Entender as camadas

| Camada | Função | Exemplo |
| --- | --- | --- |
| Instruções do projeto | Estabelecer convenções do projeto de destino | `AGENTS.md`, `CLAUDE.md`, regras aplicáveis |
| Papel do agente | Assumir responsabilidade e produzir um resultado definido | QA é responsável pela avaliação do aceite |
| Skill | Descrever um procedimento focado, com recursos opcionais | Planejar e executar testes de aceite |
| Perfil do provedor | Expressar o papel no formato nativo do cliente | Markdown do Claude ou TOML do Codex |
| Ferramentas/integrações | Fornecer capacidades reais e acesso autenticado | Testes, navegador, API cloud ou servidor MCP |
| Orquestrador | Agendar, persistir estado e validar transições | Devolver achados de QA para uma tentativa de correção |

Uma skill contém instruções carregáveis pelo cliente. Carregá-la não inicia um
worker, instala ferramentas, autentica uma conta cloud ou cria pipeline persistente.
O modelo é o mecanismo de raciocínio; Codex, Claude Code e Copilot são clientes
que interpretam esses arquivos e oferecem seus próprios recursos de execução.

## Catálogo atual

Todos os 29 papéis têm instruções canônicas e ao menos uma skill focada. São 31 skills:

| Papel | Responsabilidade principal | Skill |
| --- | --- | --- |
| PM | Descoberta do problema e resultados de produto | `sdlc-product-discovery` |
| PO | Prioridades do backlog e aceite | `sdlc-backlog-refinement` |
| Planejador | Divisão do trabalho e dependências | `sdlc-delivery-planning` |
| Estrategista de tecnologias | Escolha fundamentada de stack e tecnologias | `sdlc-technology-evaluation` |
| Arquiteto de software | Estrutura e interfaces do sistema | `sdlc-architecture-design` |
| Engenheiro de software | Viabilidade e contratos técnicos implementáveis | `sdlc-engineering-design` |
| Desenvolvedor | Alterações de código e testes de regressão | `sdlc-implementation` |
| QA | Estratégia antecipada e avaliação do aceite | `sdlc-quality-assurance` |
| Engenheiro de segurança cibernética | Modelo de ameaças e achados de segurança | `sdlc-security-assessment` |
| Arquiteto cloud | Hospedagem, identidade, redes, resiliência e premissas de custo | `sdlc-cloud-design` |
| Engenheiro DevOps | CI/CD e automação de infraestrutura | `sdlc-devops-automation` |
| DBA | Schemas, migrations, consultas e recuperação | `sdlc-database-engineering` |
| Designer UX | Jornada do usuário e comportamento das interações | `sdlc-user-experience` |
| Designer UI | Telas, estados e integração com design system | `sdlc-interface-design` |
| Especialista em acessibilidade | Interação acessível e cobertura de testes | `sdlc-accessibility-review` |
| Revisor técnico | Revisão independente do diff atual | `sdlc-code-review` |
| Responsável por release | Prontidão por revisão e entrega autorizada | `sdlc-release-readiness` |
| SRE | Telemetria, incidentes e recuperação do serviço | `sdlc-reliability-operations` |
| Redator técnico | Documentação correta e onboarding | `sdlc-technical-documentation` |
| Coordenador SDLC | Seleção de papéis, passagens de trabalho e registro de evidências | `sdlc-task-coordination` |
| Estrategista de IA | Roadmap de IA, baseline e critérios de investimento | `sdlc-ai-strategy` |
| Engenheiro de IA | Integrações avaliadas de modelos, ferramentas e recuperação | `sdlc-ai-engineering` |
| Engenheiro de contexto | Otimização de contexto/prompts com qualidade e custo medidos | `sdlc-context-engineering` |
| Engenheiro de dados | Fluxos, contratos, qualidade e origem de dados | `sdlc-data-engineering` |
| Engenheiro de avaliações LLM | Critérios reproduzíveis de qualidade, segurança e custo | `sdlc-llm-evaluation` |
| Engenheiro MLOps | Versões, entrega, monitoramento e recuperação de IA | `sdlc-mlops` |

Segurança, QA, acessibilidade e banco de dados podem contribuir antes do código.
Também revisam mudanças relacionadas aos seus domínios. O arquiteto cloud desenha
a topologia; DevOps prepara a automação; SRE avalia o comportamento em operação.
UX define jornada e interação; UI especifica telas e estados visuais.

O catálogo fica disponível, mas cada tarefa usa os papéis pertinentes. Otimizar
uma consulta pode envolver DBA, desenvolvimento, QA e revisão. Um fluxo de produto
novo pode acrescentar PM, PO, UX, UI e arquitetura. Criar todos os papéis não exige
ativar todos, e combinar responsabilidades não elimina as evidências de aceite.

## Organização do repositório

```text
agents/
  catalog.json                     Registro dos papéis
  software-architect.md            Instruções canônicas do papel
policies/
  project-defaults.json             Padrões canônicos de plataforma/dados/IA
contracts/
  agent-result.schema.json         Contrato de saída canônico
.agents/skills/
  sdlc-architecture-design/
    SKILL.md                       Procedimento portável
    references/result-contract.json  Cópia gerada do schema portável
    references/project-defaults.json Cópia portável gerada da política
    agents/openai.yaml             Metadados opcionais da UI de skills do Codex
.codex/agents/*.toml                Perfis gerados para Codex
.claude/agents/*.md                 Perfis gerados para Claude Code
.claude/skills/*/                   Cópias geradas para descoberta no Claude
.github/agents/*.agent.md           Perfis gerados para Copilot
scripts/provider_profiles.py       Validação e empacotamento locais
.dev-agent-kit-profiles.json        Impressões dos arquivos gerados
```

As fontes mantidas são o catálogo, os Markdown dos papéis, as skills canônicas,
o schema e a política da raiz. Perfis nativos e cópias do Claude são resultados
reproduzíveis. As cópias portáveis do schema e da política permitem levar uma skill
sem depender da estrutura deste repositório; `--sync-resources` as atualiza a partir
das fontes canônicas. `--sync-contracts` permanece como alias compatível.

As instruções usam as regras e ferramentas do projeto de destino. Instalar essas
skills não impõe o Git flow, Tailwind, Node.js ou ferramentas de banco deste kit
a outro projeto. Restrições específicas pertencem às instruções daquele projeto.

## O que entra no SKILL.md

O núcleo portável usa frontmatter YAML com `name` e `description`, seguido de
Markdown. O nome da pasta corresponde ao da skill. Recursos adicionais são
opcionais. Essas convenções seguem a
[especificação Agent Skills](https://agentskills.io/specification).

Um exemplo abreviado:

```markdown
---
name: sdlc-architecture-design
description: Design boundaries and interfaces when a change affects system structure.
---

# Architecture design

Read the target project's requirements and existing architecture.
Compare coherent alternatives and record interfaces, tradeoffs and failure behavior.
Return a design decision with evidence and unresolved questions.
```

A [skill real de arquitetura](../../.agents/skills/sdlc-architecture-design/SKILL.md)
inclui entradas, procedimento, contrato de saída, critério de conclusão e próximo
responsável. A descrição explica quando usar a capacidade; ela não é uma biografia
genérica. Os procedimentos completos são carregados quando necessários, reduzindo
contexto irrelevante.

`agents/openai.yaml` dentro da skill descreve sua interface no Codex. É um arquivo
distinto de `.codex/agents/*.toml`, que define agentes personalizados. Um papel
pode usar várias skills e uma skill pode servir a vários papéis; o catálogo já
aceita uma lista de skills por papel.

## Formatos nativos dos provedores

| Cliente | Skills do projeto | Arquivos de agentes personalizados |
| --- | --- | --- |
| Codex | `.agents/skills/NAME/SKILL.md` | `.codex/agents/NAME.toml` |
| Claude Code | `.claude/skills/NAME/SKILL.md` | `.claude/agents/NAME.md` |
| GitHub Copilot | Aceita `.agents/skills/NAME/SKILL.md`; existem outras pastas documentadas | `.github/agents/NAME.agent.md` |

Perfis independentes do Codex usam `name`, `description` e `developer_instructions`;
os gerados também definem o sandbox pretendido. Modelo e configuração de raciocínio
são herdados, sem fixar versões. Consulte a documentação oficial da OpenAI para
[skills](https://learn.chatgpt.com/docs/build-skills) e
[agentes personalizados](https://learn.chatgpt.com/docs/agent-configuration/subagents).

Os perfis do Claude usam frontmatter YAML e instruções Markdown. A lista `skills`
pré-carrega as capacidades selecionadas; `tools` limita as ferramentas disponíveis.
Consulte a documentação da Anthropic para
[skills](https://code.claude.com/docs/en/skills) e
[subagentes](https://code.claude.com/docs/en/sub-agents).

Os perfis do Copilot usam frontmatter YAML e Markdown, com aliases de ferramentas
documentados. O prompt manda carregar as skills canônicas e instruções do projeto.
Ferramentas e recursos de personalização variam conforme a interface; confirme
cliente e ambiente instalados. Consulte a documentação do GitHub para
[skills](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills) e
[configuração de agentes](https://docs.github.com/en/copilot/reference/custom-agents-configuration).

Procedimentos portáveis são compartilhados; permissões, interface e comportamento
de execução permanecem próprios de cada cliente. O exportador não altera configurações
globais, credenciais, modelos ou conexões MCP. Acesso a shell permite mais que testes;
a política de execução precisa limitar as ações da tarefa. Instruções textuais não
substituem sandbox ou credenciais com escopo adequado.

## Usar e manter o kit

Na pasta do kit, valide os arquivos gerados e execute os testes locais:

```bash
python3 scripts/provider_profiles.py --check
python3 -m unittest discover -s tests -v
```

Depois de editar papéis ou skills canônicos:

```bash
python3 scripts/provider_profiles.py --target .
```

Depois de alterar o schema de saída compartilhado ou a política de padrões:

```bash
python3 scripts/provider_profiles.py --sync-resources --target .
```

Para empacotar em outro projeto existente, informe seu caminho real. O exemplo
usa um caminho ilustrativo; substitua antes de executar:

```bash
python3 scripts/provider_profiles.py --provider codex --target /path/to/project
```

Use `--provider claude`, `--provider copilot` ou `--provider all` para outros destinos.
O exportador verifica conflitos antes de escrever, preserva arquivos não relacionados
e recusa sobrescrever conteúdo gerado alterado localmente. Reconcilie a mudança
desejada nas fontes. Ele não apaga automaticamente arquivos obsoletos quando um
papel é removido; inspecione antes da limpeza. Empacotar vários arquivos não é uma
transação resistente a crashes ou escritores simultâneos.

Em uma nova sessão do Codex no projeto de destino, uma solicitação de skill pode ser:

```text
Use $sdlc-architecture-design to assess the module boundaries for this task.
```

Para solicitar explicitamente o papel nativo:

```text
Delegate this architecture assessment to the software-architect agent.
```

No Claude Code ou Copilot, selecione o agente gerado pela interface do cliente e
forneça o contexto da tarefa. Pastas de perfis novas podem exigir nova sessão.
Criar arquivos não altera o catálogo de skills já carregado nesta conversa nem
comprova que todos os clientes instalados descobriram os perfis.

## Por que essa estrutura

1. **Uma intenção mantida:** Variantes de provedores são geradas dos mesmos papéis e skills.
2. **Descoberta precisa:** Cada skill descreve um trabalho reconhecível, evitando carregar todos os procedimentos.
3. **Passagens explícitas:** Papéis entregam artefatos, evidências, bloqueios e dúvidas pelo mesmo contrato.
4. **Execução conforme projeto:** Linguagens e ferramentas seguem o projeto; o procedimento do especialista continua reutilizável.
5. **Autonomia incremental:** O executor local controla estado, tentativas e revisões para desenvolvedor/QA/revisor; orquestração de especialistas e política de release vêm depois.

## O que foi validado e o que falta

O kit inclui verificação local de fontes/perfis, testes de empacotamento e workflow
do GitHub Actions para essas verificações. Esse CI valida arquivos do kit;
ele não executa o ciclo de desenvolvimento de um produto nem chama provedores de modelos.

Validação de arquivos não mede qualidade das decisões, seleção automática de skills
ou execução ponta a ponta. Avalie isso com tarefas reais autorizadas por cliente.
Casos úteis: QA sem critérios de aceite, revisão de segurança com achados sem prova,
escolha de tecnologia com fontes antigas, migration sem recuperação e release com
verificações de uma revisão anterior.

O executor local fornece entrada de tarefa, workspace isolado, validação de saída,
checks reais por componente, QA/revisão e tentativas limitadas. A entrega é um
diff/relatório. Consulte o [guia operacional](local-executor.md). A skill Coordenador
SDLC fornece instruções; as transições do workflow são implementadas em código.

## Padrões compartilhados de plataforma, dados e IA

Todos os papéis e skills incluem execução local, teto de R$ 100/mês para
infraestrutura e orçamento de IA separado ainda indefinido. Cada skill carrega a
política para instalação independente; o empacotador compara a cópia com a fonte.
Configurações explícitas do usuário/projeto prevalecem; registre as restrições
efetivas. As instruções não implementam bloqueio financeiro em runtime.

Consulte o [guia de plataforma e IA](local-platform-and-ai.md) para ferramentas,
custos e responsabilidades, e a [decisão do executor](executor-decision.md) para
os limites atuais. Os perfis, por si só, não configuram serviços autenticados.

## Workflows de planejamento e extensões

O coordenador também usa `sdlc-planning-session`; o arquiteto também usa
`sdlc-extension-design`. Essas skills focadas incluem contratos especializados de
artefatos. Consulte [planejamento](planning-governance.md), [arquitetura modular](modular-platform.md)
e [compatibilidade dos provedores](provider-readiness.md).

Novos papéis: melhoria de código (`sdlc-code-improvement`), leitura eficiente (`sdlc-code-reading`) e análise de incidentes (`sdlc-incident-learning`). Veja o [incremento atual](current-increment.md) para comportamento testado e limites.
