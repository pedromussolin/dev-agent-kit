# Pipelines lógicos, qualidade e contratos de dados

**Idiomas:** [English](../en/current-increment.md) | Português (Brasil)

Este incremento amplia o executor local e a entrega privada já aceita. As [avaliações históricas](agent-validation.md) registram as execuções reais de modelos; testes determinísticos novos não certificam todos os agentes.

## O que foi implementado

- Modelo de etapas lógicas independente do GitHub. Metadados `phase`/`phase_label` têm prioridade. Operações adjacentes reconhecidas são agrupadas por responsabilidade; operações desconhecidas continuam visíveis. Ordem e separação entre jobs são preservadas. Não existe lista obrigatória de etapas na UI.
- Renderizador, controlador do dashboard e CSS separados. O resumo mostra responsabilidade, estado, duração e erro. Detalhes recolhidos mostram operações originais, argumentos e logs sanitizados. Controles nativos de expansão funcionam por teclado. Texto externo usa `textContent`, sem interpretação como HTML.
- Persistência das verificações concluídas enquanto a etapa de checks segue em andamento. HTTP e MCP usam o mesmo contrato injetável `MonitoringRepository`; consultas SQLite ficam no adaptador concreto. A fábrica de store permite substituição futura, mas não representa um backend PostgreSQL já implementado.
- Importação de snapshots GitHub por CLI autenticada no host. Logs com timestamps são atribuídos à operação original. Eventos estruturados desdobram uma única action em qualidade, testes e build observados. Conclusão desconhecida não vira sucesso. A interface mostra a última sincronização; ainda não há polling GitHub contínuo.
- Três papéis novos: melhoria de código (`code-improver`), leitura eficiente (`code-reader`) e análise de incidentes (`incident-analyst`). São 29 papéis, 31 skills canônicas, 87 perfis nativos e 333 arquivos gerenciados verificados pelo empacotador. Selecionar um papel não inicia um serviço permanente nem amplia permissões.
- Gates Ruff para Python e Prettier para o monitor. O produto financeiro também executa ESLint, Prettier, TypeScript, testes unitários/de segurança e protocolo MCP no CI compartilhado. Fontes vendorizadas de UI mantêm as exceções específicas existentes.
- Servidor MCP stdio com SDK oficial para o kit e adaptador HTTP→MCP para finanças. O kit expõe evidência pública, sem shell, SQL, execução de modelos ou deploy. Cancelamento só é registrado com `--allow-control`. Finanças é somente leitura por padrão; `--allow-write` habilita gravação com validação da API e revisão esperada.
- Persistência financeira por repositório tipado e adaptador Drizzle D1, preservando parâmetros, isolamento por usuário e concorrência otimista. O Worker recebe operações do domínio, sem SQL arbitrário. Nenhum banco adicional foi provisionado.
- Checks com limites de tempo/saída e encerramento do grupo de processos em POSIX. Falhas marcam os checks seguintes como ignorados. A sanitização é heurística, sem garantia universal para qualquer segredo.

## Por que organizar assim

O domínio define as operações; os adaptadores implementam a tecnologia. SQLite pertence ao adaptador SQLite, assim como D1 ao adaptador D1. `import sqlite3` nessa camada é uma escolha de implementação. HTTP, MCP e consumidores do domínio não precisam montar consultas. A proteção contra injection depende de parâmetros e identificadores controlados, inclusive com ORM. Migrations fixas e revisadas continuam em SQL.

Data-first significa definir propriedade, schema, identidade, validação, retenção, migrations e recuperação antes de adicionar storage. O snapshot financeiro pequeno cabe em JSON tipado numa tabela relacional. Separe entidades quando consultas e relatórios justificarem. NoSQL ou object storage precisam de padrão de acesso e plano de consistência/backup; um objeto não exige automaticamente outro banco.

O frontend financeiro (`app/`) usa o contrato HTTP do backend (`worker/`), e a persistência fica em `db/`. Hoje compartilham repositório e build de entrega. Separe serviços/repositórios quando houver ciclos de release ou responsabilidades independentes, conservando testes de contrato e paridade MCP. React é a stack atual do produto, não uma obrigação universal do kit. O monitor pequeno usa HTML/CSS/JavaScript modular sem impor frameworks a projetos Python/Go.

Skills descrevem procedimentos; papéis atribuem responsabilidade; perfis adaptam o formato do provedor; ferramentas fornecem capacidades reais. Mantenha uma fonte canônica e regenere os formatos nativos. Contexto pessoal não entra nessas instruções públicas. Selecione apenas papéis e skills relevantes para controlar contexto e tokens. Aprendizado de incidentes começa por regressão demonstrada ou regra delimitada, com responsável e análise de falsos positivos; não cria automaticamente um agente para cada erro.

## Testar sem consumir tokens de modelos

No checkout do kit, com Python 3.11+:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[monitor,test,browser]'
.venv/bin/python scripts/provider_profiles.py --check
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m playwright install --with-deps chromium
PYTHONPATH=. .venv/bin/python tests/browser/check_monitor.py
```

O teste de navegador usa dados fictícios, estado temporário e monitor local numa porta livre. Verifica agrupamento, todos os estados, erro, duração, expansão, idioma, largura mobile e prevenção de XSS nos logs. Não modifica dados financeiros reais. O CI repete em Python 3.12; a suíte principal roda em 3.11/3.12/3.13.

No finance-management, use a versão Node/pnpm declarada:

```bash
pnpm install --frozen-lockfile
pnpm quality
pnpm test
pnpm build
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
.venv/bin/python -m unittest discover -s tests -p 'test_*.py' -v
```

Em `actions`, instale Ruff 0.16.10 e execute `ruff check .`, `ruff format --check .` e `python3 -m unittest discover -s tests -v`. Esses comandos validam código/protocolo; não chamam modelos nem fazem deploy.

## Acompanhar um pipeline GitHub real

Use um ID real no checkout do host, com `gh` autenticado e acesso ao repositório:

```bash
.venv/bin/python -m dev_agent_kit sync-workflow --repository OWNER/REPOSITORY --run-id REAL_RUN_ID --logs
```

O estado padrão é `~/.local/state/dev-agent-kit`, compartilhado com o monitor local. Cada comando de API tem limite de 30 segundos/2 MB; runs acima de 20 jobs são rejeitados, sem importação parcial silenciosa. Logs são opcionais e podem conter informações privadas mesmo sanitizados: sincronize apenas runs autorizados. O monitor Docker não recebe credenciais GitHub.

O produtor pode declarar qualquer responsabilidade:

```json
{"name":"risk-report","phase":"risk-analysis","phase_label":"Assess portfolio","argv":["python","scripts/risk_report.py"],"timeout_seconds":120}
```

Checks sem metadados continuam funcionando. Responsabilidades iguais separadas por outros trabalhos ficam em cartões distintos para preservar a ordem. A duração soma tempos observados das operações; timings históricos ausentes aparecem como traço. Jobs paralelos permanecem separados.

## Iniciar MCP e configurar clientes

Depois de instalar o extra `mcp`, configure o intérprete absoluto e o diretório do checkout:

```bash
.venv/bin/python -m dev_agent_kit --state-dir /ABSOLUTE/PRIVATE/STATE mcp
```

Para finanças, use o ambiente Python com `requirements-dev.txt`. O produto local precisa estar ativo e seu arquivo privado de senha Basic deve existir:

```bash
.venv/bin/python scripts/finance_mcp.py --base-url http://127.0.0.1:8787
```

Veja o [exemplo de configuração](../../examples/mcp/servers.json). Substitua os caminhos e adicione apenas os servidores desejados às configurações MCP existentes do cliente. Os formatos variam por provedor; preserve configurações sem relação com a mudança. O cliente inicia o processo stdio sob demanda. Nesse transporte, acesso depende do usuário/processo local e dos arquivos de estado/credenciais selecionados, não de senha HTTP do MCP. Anotações descrevem comportamento; registro das ferramentas e a API aplicam os controles reais. Dados financeiros só devem entrar numa sessão MCP privada explicitamente autorizada.

## Contexto pessoal e pendências

Markdown pessoal fica fora dos repositórios de software e não é carregado automaticamente por agentes, monitor ou MCP. A extração de documentos deve ficar privada, citar arquivo/página, separar fatos de hipóteses e ter orçamento/metas conferidos antes de virar tarefa.

Para uma plataforma autônoma mais ampla, ainda faltam: avaliação real dos outros 26 papéis, adaptadores de execução Claude/Copilot, persistência alternativa testada, carregamento de plugins/negociação de capacidades, planejamento agendado integrado ao backlog, inicialização durável dos runners, controle financeiro no provedor e simulações de restauração do banco. PostgreSQL/Grafana/Loki/telemetria de IA continuam perfis opcionais; não foram ativados neste incremento. Hosting segue local; teto de nuvem é R$ 100/mês e IA tem orçamento separado. Esta entrega não introduz avaliação paga de modelos ou serviço novo na nuvem.
