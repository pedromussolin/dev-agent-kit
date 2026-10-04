# Regras de Automação de SDLC com Agentes

## 1. Contrato da Tarefa

Toda execução deve partir de uma tarefa identificada com objetivo, critérios de
aceite, escopo, repositório, revisão base e política de execução. Use
`templates/sdlc-task.md` como referência. Sem informação essencial, registre a
lacuna e bloqueie a etapa dependente; não invente requisitos ou IDs.

## 2. Controle do Fluxo

O orquestrador controla estados, dependências, ferramentas, limites e persistência.
Os agentes propõem decisões e executam ações permitidas por esse contrato.
Resultados textuais de agentes não devem autorizar transições por si só.
Etapas: descoberta de produto, refinamento de backlog, planejamento, desenho,
implementação, verificação/validação, revisão, entrega e operação. Uma execução
parcial deve ser identificada como parcial. Resultados operacionais alimentam o backlog.

## 3. Evidências e Critérios de Passagem

Registre execução, tarefa, tentativa, revisão de código, configuração, comandos,
códigos de saída e referências aos artefatos. Valide resultados estruturados,
testes e diff. A existência de um documento não prova que seus requisitos foram
atendidos. Verificação e revisão devem corresponder à mesma revisão entregue.

Falhas devem ter categoria explícita: requisito ausente, configuração inválida,
ferramenta ausente, teste falhando, timeout, falha do provedor ou revisão reprovada.
Retentativas devem ter limite e respeitar a possibilidade de efeitos duplicados.

## 4. Execução e Recuperação

Use workspace isolado por tarefa e bloqueio por workspace. Persista transições
antes de iniciar novas etapas. Retomar uma execução exige comparar base, diff,
configuração e evidências; alterações invalidam etapas dependentes.

Defina quais ações são automáticas, exigem aprovação ou estão desativadas conforme
a autorização e as configurações do projeto. Não exija aprovações repetidas para
ações já autorizadas. Não execute entregas com política desconhecida.
Proteja segredos conforme `011`; evite armazenar credenciais em prompts e logs.

## 5. Papéis e Integrações

Defina responsabilidades de PM, PO, planejador, engenheiro de software, arquiteto,
desenvolvedor, QA, revisor e entrega/operações conforme a tarefa. PM orienta problema
e resultado; PO organiza backlog e aceite; planejador organiza execução e dependências.
QA participa também do refinamento e desenho. Engenheiro e desenvolvedor podem ser
um mesmo papel, conforme o projeto. Inclua especialistas de segurança, cloud,
DevOps, banco de dados, UX, UI, acessibilidade, tecnologias, estratégia de IA,
engenharia de IA/contexto/dados, avaliações LLM e MLOps quando o escopo exigir.
O catálogo completo está em `agents/catalog.json`. Não imponha uma equipe completa
para toda correção pequena. Consulte `templates/agent-role.md` para os contratos.

Separe responsabilidade de planejamento, implementação, verificação e revisão.
Separar papéis não exige provedores, modelos ou processos diferentes. Agentes
adicionais são uma escolha do executor, não autorização para criar subagentes em
qualquer sessão. O adaptador de agente deve declarar limites, capacidades,
autenticação externa e formato do resultado. O adaptador de linguagem deve
declarar ferramentas e critérios de verificação.

Consulte `docs/en/architecture.md` ou `docs/pt-br/architecture.md` para a proposta.
