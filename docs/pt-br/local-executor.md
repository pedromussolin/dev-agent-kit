# Operação do executor local

**Idiomas:** [English](../en/local-executor.md) | Português (Brasil)

A versão 0.2 executa uma sequência configurada de planejamento → implementação →
checks reais → verificações independentes → entrega. O padrão usa desenvolvedor,
QA e revisor técnico. Os 26 papéis cadastrados podem participar; uma implementação,
QA e revisão continuam obrigatórios. A entrega pode criar PR, aguardar CI remoto,
fazer merge e deploy conforme a tarefa. Consulte [entrega e Actions](delivery-and-actions.md).

## Preparar o ambiente

Use Python 3.11+, Git com worktrees e um host POSIX. Mantenha o checkout do kit:
o pacote contém executor/painel, mas contratos, perfis e skills ficam no repositório.
`--kit-root` escolhe esses recursos; não altera o caminho de importação do Python.
O estado precisa ficar fora do repositório do produto.

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e '.[monitor,test]'
python3 scripts/provider_profiles.py --check
python3 -m unittest discover -s tests -v
codex --version
codex login status
python3 -m dev_agent_kit --help
```

Os adaptadores usam a autenticação ChatGPT existente (`ai_spending:
existing_chatgpt_account`) e rejeitam `OPENAI_API_KEY`/`CODEX_API_KEY` não vazias.
Nenhuma credencial de API é criada. O cliente instalado foi validado na versão
0.160.0. `codex-app-server` fornece atividade e uso cumulativo de tokens durante
a tarefa; a CLI instalada marca esse comando como experimental. O adaptador fica
atrás de `AgentAdapter`; atualizações do cliente exigem nova validação.
`codex-cli` permanece disponível, com tokens informados somente ao concluir uma
atribuição. Nenhum dos adaptadores impõe um teto financeiro no provedor.

Prepare separadamente as dependências reais dos checks do produto. O executor não
instala ferramentas nem recria ambientes ignorados. Checks herdam o ambiente do
host e são subprocessos locais confiáveis, sem shell. Worktree isola alterações,
mas não é sandbox de segurança. O desenvolvedor usa `workspace-write`, planejamento
e verificação usam `read-only`; as ferramentas do app-server ficam sem acesso à
rede. Checks e comandos de deploy usam sua autoridade declarada e precisam de
isolamento próprio para projetos não confiáveis.

## Descrever e iniciar uma tarefa

Substitua caminhos, IDs, objetivos e checks pelos valores reais:

```bash
python3 -m dev_agent_kit inspect /CAMINHO/ABSOLUTO/DO/PROJETO
python3 -m dev_agent_kit init /CAMINHO/ABSOLUTO/task.json   --repository /CAMINHO/ABSOLUTO/DO/PROJETO   --task-id ID-REAL-DA-TAREFA --goal 'Seu objetivo concreto de aceite'   --allow 'src/arquivo-especifico.py' --context README.md   --check 'python3 -m unittest discover -s tests -v'
```

`inspect` lê manifests na raiz e sugere checks; não executa nem instala nada.
Componentes de linguagens diferentes continuam independentes. `init` cria um
arquivo novo de tarefa real, registra o commit completo e preenche limites iniciais.
Revise critérios de aceite, componentes, escopo e autorização antes de `run`.
ID local não é issue GitHub; entrega remota exige uma issue real e aberta.

O [contrato da tarefa](../../contracts/execution-task.schema.json) rejeita chaves
não previstas. Contexto, escopo e diretórios dos checks precisam ficar no projeto,
sem symlinks, `..`, caminhos absolutos ou `.git`. Declare padrões de escopo estreitos.
Comandos são arrays de argumentos; `--check` interpreta aspas, sem executar operadores
de shell. Escolha as ferramentas existentes: Python, Go, JS, Rust ou outras.

`workflow` pode conter etapas `{name, role_id, kind}`. Use `plan` para especialistas
sem escrita antes da implementação, exatamente uma etapa `implement` e `verify`
para especialistas independentes depois dos checks. Inclua `qa-engineer` e
`technical-reviewer`. Aumente o limite explícito de chamadas somente quando os
papéis escolhidos precisarem. Cada papel consome uso; a empresa inteira não precisa
participar de cada correção pequena. Uma rodada de planejamento é uma passagem
limitada pelos papéis, sem discussão infinita ou agendamento em background.

## Validar, executar e acompanhar

Execute no checkout do kit, substituindo tarefa e ID:

```bash
KIT_ROOT="$PWD"
STATE_DIR="$HOME/.local/state/dev-agent-kit"
TASK_FILE="/CAMINHO/ABSOLUTO/task.json"
python3 -m dev_agent_kit --kit-root "$KIT_ROOT" --state-dir "$STATE_DIR" validate "$TASK_FILE"
python3 -m dev_agent_kit --kit-root "$KIT_ROOT" --state-dir "$STATE_DIR" run "$TASK_FILE"
RUN_ID="<ID_RETORNADO_POR_RUN>"
python3 -m dev_agent_kit --kit-root "$KIT_ROOT" --state-dir "$STATE_DIR" status "$RUN_ID"
python3 -m dev_agent_kit --state-dir "$STATE_DIR" runs
python3 -m dev_agent_kit --state-dir "$STATE_DIR" watch "$RUN_ID"
python3 -m dev_agent_kit --state-dir "$STATE_DIR" cancel "$RUN_ID"
```

`validate` comprova formato/caminhos, não prontidão nem aceite. `run` verifica
autenticação, ferramentas e entrega, depois cria o snapshot autorizado. O progresso
vai para stderr; o resultado estruturado final vai para stdout. `--quiet` oculta o
progresso, e `watch --json` publica eventos para outros consumidores.

O painel usa o mesmo estado e mostra atribuições, etapas, comentários públicos,
uso, limites, efeitos da entrega e cancelamento:

```bash
python3 -m dev_agent_kit --state-dir "$STATE_DIR" serve
```

Abra `http://127.0.0.1:8765`. A interface suporta português/inglês. SSE retoma por ID
de evento; SQLite WAL permite acompanhar uma execução com o lock ativo. Comandos
brutos, saídas de ferramentas, prompts e raciocínio privado não são publicados na
linha do tempo pública. Comentários/resultados passam por sanitização heurística;
isso não garante remoção formal de qualquer segredo. Interfaces não locais exigem
`DEV_AGENT_KIT_MONITOR_TOKEN`; o navegador usa autenticação HTTP Basic. O Compose
fornecido publica somente no loopback do host.

## Limites e recuperação

Limites persistidos cobrem atribuições, tentativas, tempo total, contexto,
ferramentas, resultados idênticos sem mudança de código, inatividade, tokens
observados por agente/execução, tokens/chamadas por projeto no dia UTC e reparos
sem progresso. Chamadas são reservadas antes da invocação. Uso é registrado antes
da interrupção. Retomadas e novas execuções no mesmo projeto/estado não reiniciam
o saldo diário. IDs de projeto devem ser estáveis; estados separados contabilizam
separadamente. Chamadas históricas da v0.1 não são importadas para esse saldo. Uso
não informado continua desconhecido e limitado por chamadas/tempo/ferramentas.

O app-server é interrompido quando o uso cumulativo informado alcança o limite.
Trabalho em andamento pode ultrapassá-lo; isso não é reserva exata nem quota do
provedor. A CLI informa uso ao concluir, então impede atribuições posteriores sem
garantir interrupção por tokens durante a chamada. Input em cache entra na contagem.
`cost_brl` continua desconhecido sem evidência real de custo. O teto de R$ 100/mês
para infraestrutura exclui IA e não compra serviços nem impõe limites na nuvem.

Leia `$STATE_DIR/runs/$RUN_ID/report.json`, `task.patch`, checks e erros antes de
retomar. QA/revisão precisam do mesmo fingerprint dos checks. Mudanças de conteúdo
ou HEAD invalidam evidência; mudanças no kit/configuração bloqueiam a retomada.
Artefatos de retry têm diretórios distintos por tentativa/etapa/chamada.

```bash
python3 -m dev_agent_kit --kit-root "$KIT_ROOT" --state-dir "$STATE_DIR" resume "$RUN_ID"
```

Sucesso ainda atual retorna sem novas atribuições. Falhas de CI podem reutilizar
aceite local quando o código é idêntico. Implementação ou efeitos externos ambíguos
exigem inspeção. Cancelamento, loops e orçamento esgotado exigem tarefa explicitamente
revisada; retomar não reinicia limites. Falhas de deploy executam rollback configurado
e guardam seu resultado real; deploy falho/ambíguo não se repete cegamente.

`run`/`resume` retornam zero somente no sucesso. `status` retorna zero quando a
inspeção funciona, mesmo que a tarefa tenha falhado; leia status/erro. Arquivos
retidos ou alegações do agente não comprovam entrega. Descoberta automática de
skills pelos clientes, workers distribuídos, agendamento autônomo de backlog e
carregamento de plugins por manifesto continuam integrações distintas. Veja a
[validação](agent-validation.md).
