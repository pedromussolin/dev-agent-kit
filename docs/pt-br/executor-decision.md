# Decisão do primeiro executor

**Idiomas:** [English](../en/executor-decision.md) | Português (Brasil)

A versão 0.2 acrescenta papéis configuráveis de planejamento/verificação, atividade
pública ao vivo, limites de tokens observados e painel FastAPI/SSE. `CodexAppServer`
se soma ao `CodexCLI`; a entrega via GitHub CLI suporta PR, checks declarados de CI,
merge do HEAD conferido e deploy/smoke/rollback configurados. SQLite continua sendo
o armazenamento concreto para uso pessoal. O app-server instalado é experimental;
fixe e valide sua compatibilidade. Conectar o produto remoto exige configuração
além do aceite local. Veja [operação](local-executor.md) e
[entrega/Actions](delivery-and-actions.md).

A decisão abaixo registra os tradeoffs iniciais da v0.1. Itens escritos como
futuros são históricos; os guias v0.2 definem o escopo executável atual.

Status: a implementação local inicial está disponível em `dev_agent_kit/`.
Ela executa desenvolvedor → checks por componente → QA → revisão técnica e entrega
um diff. Consulte o [guia operacional](local-executor.md). As demais etapas seguem planejadas.

## Recomendação e motivos

Começar com uma **CLI Python modular, estado em SQLite e um adaptador de agente**.
Python facilita integração com ferramentas, dados e avaliações. SQLite evita
operar um servidor de estado para uma pessoa e uma tarefa por vez. O projeto
executado pode continuar usando Go, Python, TypeScript ou outra stack.

O fluxo inicial deve ser uma máquina de estados explícita e persistida. Ela
controla transições, limites e evidências. Agentes recebem tarefas e propõem
resultados; não decidem sozinhos que um teste passou ou que uma entrega foi autorizada.

| Opção | Adequação neste momento | Quando reconsiderar |
| --- | --- | --- |
| Python + SQLite + subprocessos controlados | Recomendado para um fluxo local sequencial com ferramentas já existentes | Extrair componentes conforme surgirem requisitos concretos |
| LangGraph | Útil para grafos de agentes, checkpoints e interação humana; exige integrar políticas e ferramentas do projeto | Quando os fluxos passarem a precisar dessas capacidades de forma recorrente |
| Temporal | Adequado a workflows duráveis com workers; adiciona operação de infraestrutura | Quando houver tarefas distribuídas e requisitos de execução entre serviços |

LangGraph oferece capacidades de orquestração e persistência; Temporal possui
implantação self-hosted. São alternativas válidas, mas o desenho inicial procura
reduzir os serviços necessários à operação pessoal.
[LangGraph](https://docs.langchain.com/oss/python/langgraph/overview),
[Temporal](https://docs.temporal.io/self-hosted-guide).

Usar um fluxo próprio também tem custo: precisamos testar recuperação, transições
e efeitos duplicados. O primeiro executor deve ter estados e poucos caminhos bem
especificados; não recriar um framework genérico de workflows.

## Módulos e contratos

| Módulo | Responsabilidade |
| --- | --- |
| `domain` | Tarefa, critérios de aceite, estados, tentativas, resultado e políticas |
| `orchestration` | Seleção de papéis, dependências e critérios de passagem |
| `storage` | SQLite, transações, eventos, artefatos e migrações do estado |
| `agent_adapters` | Cliente escolhido, entrada/saída, cancelamento, capacidades e uso disponível |
| `stack_adapters` | Comandos por componente, ambiente, timeout e evidência de execução |
| `workspace` | Worktree isolado, bloqueio e fingerprint do diff/revisão |
| `observability` | Logs sanitizados e IDs de execução/tarefa/papel/tentativa |
| `delivery` | Operações distintas de PR, CI, merge e deploy, conforme política |
| `cli` | Validar tarefa/configuração, executar, consultar e retomar |

O código inicial usa módulos pequenos: `contracts.py`, `executor.py`, `adapters.py`,
`processes.py`, `workspace.py`, `storage.py` e `cli.py`. `AgentAdapter` recebe
`Assignment`/`AgentResponse` sem tipos de SDK; hoje somente `CodexCLI` está conectado
à CLI. Os checks são listas de argumentos, não SDKs de linguagem. SQLite é a
implementação concreta; interface substituível de armazenamento e migrações ficam
para depois. Entrega remota, exportadores de telemetria e descoberta de plugins
continuam pendentes.

Defina comandos como listas de argumentos e diretório explícito. Um subprocesso
não cria sandbox; o adaptador deve declarar isolamento e controles realmente
disponíveis. Configuração de modelos e credenciais fica fora dos prompts e skills.

## Primeiro fluxo ponta a ponta

1. Validar uma tarefa real: repositório, objetivo, aceite, revisão base, componentes e ações autorizadas.
2. Criar workspace isolado e persistir execução/configuração antes de chamar agentes.
3. Chamar o desenvolvedor com perfil nativo, skill e contexto limitado da tarefa.
4. Validar resultados contra o schema e executar as verificações dos componentes afetados.
5. Obter avaliação de QA e revisão com evidências da mesma revisão/fingerprint do código.
6. Corrigir falhas dentro dos limites e invalidar evidências afetadas por novas mudanças.
7. Produzir diff e relatório verificáveis; acrescentar PR e CI remoto no incremento de entrega.

O primeiro fluxo parte de uma tarefa refinada. PM/PO e descoberta de produto serão
etapas executáveis adicionais; o catálogo completo não equivale a SDLC inteiro já
automatizado. Deploy e operação também precisam de adaptadores e casos de aceite.

Cada tentativa persiste início, término, comando/modelo, revisão, saída e referências
às evidências. Uma etapa `running` após crash exige reconciliação, nunca conversão
automática para sucesso. Retentativas têm limites e precisam conferir efeitos
anteriores antes de repetir uma operação externa.

## IA, dados e custos desde o primeiro incremento

Separar eventos operacionais de conteúdo sensível. Guardar payloads estruturados,
versão do contrato, origem e retenção; não armazenar segredos ou prompts completos
por padrão. Logs JSON podem ganhar exportação OpenTelemetry depois.

A configuração efetiva deve distinguir infraestrutura e IA. Enquanto o limite de
IA estiver indefinido, não assumir uso ilimitado nem iniciar novos gastos pelo kit.
O executor deve suportar limites por tarefa/tentativa e, quando houver preço/uso
confiáveis, reservar estimativas antes da chamada e reconciliar o consumo observado.
Clientes sem medição exigem limites de chamadas/tempo e relatório `unknown`; esses
limites não devem ser apresentados como garantia de bloqueio financeiro do provedor.

## O que define sucesso do executor

- Uma tarefa real autorizada passa por implementação, verificações, QA e revisão.
- Resultado inválido, ferramenta ausente, teste reprovado e timeout impedem conclusão.
- Reinício retoma estado coerente; mudança de diff invalida evidências antigas.
- Limites encerram loops de correção e deixam falhas visíveis.
- Um componente Python e um Go têm comandos próprios, sem imposição de Node.
- O relatório identifica o que ocorreu, o que ficou pendente e o uso não disponível.

O primeiro adaptador precisa ser escolhido e validado contra a versão instalada do
cliente. Uma CLI existente pode evitar uma nova integração de API, mas ainda exige
autenticação, execução sem interface interativa, saída estruturada, cancelamento e
limites. Isso deve ser verificado antes de prometer execução autônoma.

O adaptador implementado usa Codex CLI 0.160.0 com login ChatGPT existente,
execução não interativa efêmera e resultado estruturado. Essa CLI não oferece
seleção de agente em `exec`; o adaptador carrega explicitamente o perfil TOML gerado
e as instruções da skill. Descoberta automática exige validação separada. O JSON
Schema normalizado é traduzido para o formato nativo mais restrito.
Implementação usa sandbox `workspace-write` do cliente; QA/revisão usam `read-only`.
Os checks do projeto são subprocessos locais comuns e precisam ser confiáveis.
Um worktree isola alterações, mas não é uma fronteira de segurança.

## Fronteiras de extensões e planejamento

Mantenha tipos de clientes/provedores atrás de adaptadores conforme a [arquitetura modular](modular-platform.md).
O contrato normalizado aceita IDs extensíveis; o executor deve conferir seu registro
ativo. Artefatos de planejamento não autorizam transições. Valide autoridade,
referências e IDs reais das tarefas prontas antes da execução.
