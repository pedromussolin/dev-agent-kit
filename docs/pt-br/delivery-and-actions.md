# Entrega, repositórios e GitHub Actions

**Idiomas:** [English](../en/delivery-and-actions.md) | Português (Brasil)

O kit é o motor reutilizável; `finance-management` é o produto. Código, checks e
configuração de deploy ficam com o produto. Contratos de agentes, skills e executor
ficam no `dev-agent-kit`. Um repositório chamado `actions` passa a fazer sentido
quando vários projetos compartilham workflows com releases independentes. Usar
GitHub Actions não exige um repositório com esse nome.

Workflows reutilizáveis ficam em `.github/workflows/` e declaram `workflow_call`.
O produto chama o workflow do repo `actions` em um commit publicado e imutável, seguindo o
[modelo oficial do GitHub](https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows).
As revisões do actions e do kit estão publicadas e fixadas no template do caller. O executor reutilizável `actions/.github/workflows/sdlc-executor.yml`
e o [template do produto](../../templates/github-actions/product-sdlc.yml.template)
separam execução e responsabilidade pelo produto.

## Capacidades de entrega ativadas

| Modo da tarefa | Limite da entrega concluída |
| --- | --- |
| `diff` | Patch/relatório isolado e aceite local independente |
| `pull_request` | Branch própria e PR correspondentes ao código aceito |
| `merge` | PR + checks remotos declarados + merge do HEAD conferido |
| `deploy` | Merge + comando de implantação + smoke check, com rollback na falha |

Escolha explicitamente o modo na tarefa real. Complete o
[template de configuração](../../templates/delivery-config.json.template) e use
`init --delivery deploy --delivery-config ARQUIVO`. Templates contêm placeholders
inválidos de propósito e não podem ser executados como tarefas reais. O JSON registra
repositório GitHub, issue real aberta, branch padrão, nomes dos checks obrigatórios,
método de merge, espera limitada de CI e comandos do ambiente.

Entrega remota exige entrada limpa e commitada, igual à branch padrão remota.
O executor cria outro worktree, commita somente a árvore aceita, publica uma branch
própria sem force e confere o HEAD do PR. Usa `gh pr merge --match-head-commit` sem
ignorar proteções. Se a branch padrão avançar, o aceite precisa ser renovado.
Efeitos repetidos são reconciliados com o estado persistido. Merge/deploy ambíguos
permanecem visíveis. O deploy busca o commit efetivamente integrado e compara a
árvore com o aceite local. Comandos são arrays de argumentos. `smoke_argv` e
`rollback_argv` são obrigatórios; o resultado do rollback é registrado, sem presumir
sucesso.

## Execução local primeiro

GitHub Actions agenda; o executor é o kit. Para uso pessoal, um runner Linux dedicado
pode chamar o kit, reter SQLite e acessar o Codex já autenticado localmente. Arquivos
de autenticação ChatGPT não são copiados para repositórios nem artefatos do Actions.
Instalação do runner, login e label são pré-requisitos reais; adicionar YAML não os
configura. Use esse runner pessoal somente com tarefas confiáveis iniciadas
manualmente na branch padrão. Veja [runners próprios](https://docs.github.com/en/actions/concepts/runners/self-hosted-runners).

O workflow limita concorrência por produto com `cancel-in-progress: false`, além
dos locks e orçamentos do executor. O estado fica fora dos checkouts descartáveis.
Publique somente um relatório sanitizado selecionado quando apropriado; artefatos
do provedor e patches brutos não são enviados automaticamente. Cancelar o job não
comprova rollback de deploy; efeitos interrompidos precisam de reconciliação.

O token de entrega precisa das permissões do produto. Tokens de instalação de
GitHub App são a opção escalável; PAT restrito é uma alternativa. O `GITHUB_TOKEN`
padrão muda os gatilhos: a documentação atual exige aprovação nos workflows dos
PRs criados por ele e suprime outros eventos recursivos. App/PAT adequado evita
essa aprovação extra de CI quando o objetivo é automação completa. Consulte
[gatilhos de workflows](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow).
Credenciais ficam fora de skills/prompts e não são configuradas automaticamente.

## Infraestrutura e limites

Runner e painel locais não exigem serviço novo na nuvem; energia/hardware e uso da
conta continuam custos reais. A política mantém infraestrutura até R$ 100/mês e IA
com orçamento separado. Escolha de plano cloud exige verificar custo completo e
requisitos do destino. O [Compose do painel](../../compose.monitor.yaml) executa
somente monitoramento; comandos de deploy do produto continuam específicos.

O destino do finance-management é o Docker nesta máquina; a integração é
rastreada pela issue #1 do produto. Testes locais usam Git e processos de deploy
reais com I/O GitHub controlada; isoladamente, não comprovam publicação. Tarefas já escolhem seu repositório/ID de projeto. Separe
serviços ou um repo Actions quando consumidores, releases ou responsabilidades
independentes justificarem a divisão.

## Ambiente pessoal conectado

Os repositórios actions e finance-management são privados. O produto roda no
Docker local com D1 persistente, gateway autenticado em loopback, backups SQLite
verificados e rollback de imagem. Use `use-local-github-auth: true` apenas no
runner pessoal confiável para aproveitar o login gh existente, sem copiar seu
token para secrets. Para clientes futuros, prefira token de instalação GitHub App.

Dois processos separados evitam que o agente bloqueie o único worker ao aguardar CI:

```bash
python3 scripts/local_runners.py start finance-sdlc finance-ci
python3 scripts/local_runners.py status finance-sdlc finance-ci
python3 scripts/local_runners.py stop finance-sdlc finance-ci
```

Registro e ambiente Python persistente ficam fora dos repositórios, em
`~/.local/share/dev-agent-kit`. O launcher roda como processo do usuário; reinicie
após reboot. Ele exige repositório privado. O arquivo do produto deve fixar os
SHAs publicados do actions e do kit; tarefas reais usam issue e critérios de CI
existentes.

## Pré-requisitos da ativação pessoal

O primeiro consumidor privado usa a revisão actions
`3f4cfeb8a0e363d237dd6d117d7422b941189667` e a revisão kit
`ab4c21894e61e3aca09575cf237e50a154955478`. Os runners registrados usam GitHub
Runner 2.337.0, GitHub CLI 2.102.0 e ambiente Python persistente. A credencial
permanece no armazenamento local existente. Alterações de workflows são
publicadas pela chave SSH configurada; o token OAuth não tem escopo workflow,
mas atende à entrega comum e às operações de API. Um CI anterior falhou pela
reutilização da pasta de utilidades; cada job agora usa uma pasta temporária
exclusiva. Checks de push e PR com o mesmo nome exigido precisam passar.

Execute o launcher no terminal do host: a conferência de PID usa o namespace de
processos Linux dessa máquina. Um resultado parado dentro de outro container
não comprova que o runner do host parou. Confirme a conexão no GitHub. Agentes
só iniciam por solicitação manual explícita; não há consumo recorrente de IA.
Uma tarefa concluída cuja issue foi fechada não pode ser reenviada sem novo
escopo e issue válidos.
