# Validação do executor local e dos agentes

**Idiomas:** [English](../en/agent-validation.md) | Português (Brasil)

## Aceite da entrega do produto privado

A [avaliação do produto](../../evaluations/finance-management-delivery.json) registra
a tarefa real do finance-management privado: desenvolvedor, sete testes do produto,
TypeScript/build, QA/revisor independentes, PR #4, ambos os checks de CI, merge
vinculado ao HEAD e smoke autenticado no Docker local passaram. Os três papéis
reportaram 232.410 tokens observados para um limite de 250.000, sem retentativa;
cada um ficou abaixo de 100.000. Custo monetário permanece desconhecido. O caso
valida esse caminho de entrega GitHub; não certifica os outros 23 papéis, limites
de cobrança, execução Claude/Copilot ou reuniões e backlog autônomos.

## Código e limites na versão 0.2

A [avaliação de código](../../evaluations/codex-actions-code-task.json) registra
um defeito real no runner do `actions`: argumento/executável inválido em um check
posterior podia falhar depois de um comando anterior produzir efeitos. Desenvolvedor
corrigiu a validação, testes com processos reais passaram e QA/revisor aceitaram
o mesmo fingerprint. Três atribuições informaram **237.190 tokens totais**, incluindo
input em cache, abaixo do limite de 250.000. Por papel: 97.087 / 78.904 / 61.199.
O modelo informou `gpt-6.1-sol`; custo financeiro continua desconhecido. A retomada
manteve três chamadas antes das mudanças posteriores do kit. É um caso pequeno
de código real, não uma comparação equivalente de economia com a tarefa antiga.

A [avaliação do limite ao vivo](../../evaluations/codex-live-token-stop.json) parou
uma atribuição em 123.411 tokens observados para um limite de 100.000. A requisição
em andamento ultrapassou o limiar; o código parcial ficou sem aceite. Outras
tentativas limitadas, incluindo cancelamento e falha de tamanho do contexto antes
da inferência do QA, continuam falhas/canceladas no SQLite. Nenhuma foi reclassificada
como sucesso.

O kit atual passou 68 testes, incluindo Git/deploy reais com I/O GitHub controlada,
interrupção de subprocessos do protocolo e monitoramento HTTP/SSE. Os 12 testes de
descoberta de stacks passam; a tarefa ampla interrompida não é apresentada como
avaliação concluída pelos três papéis. Os outros 23 papéis ao vivo e tetos financeiros do provedor ainda não foram avaliados.

As seções seguintes preservam a avaliação v0.1. A contagem de 31 testes e seus
limites descrevem aquele runtime. Retomar sucessos históricos exige os fingerprints
originais do kit/configuração; mudanças atuais do kit bloqueiam a retomada.

Avaliação realizada em 04/10/2026 com Python 3.12.3 e Codex CLI 0.160.0. O
[registro da avaliação](../../evaluations/codex-real-task.json) preserva resultados
medidos e limites. É um primeiro caso de aceite com escopo definido, sem certificar
o SDLC completo ou todos os 26 papéis.

## O que passou

| Verificação | Resultado |
| --- | --- |
| Testes unitários e de integração | 31 testes passaram; worktrees Git, subprocessos e SQLite reais, com entrada/saída do provedor controlada |
| Perfis e recursos gerados | 306 arquivos consistentes para Codex, Claude Code e Copilot |
| Tarefa real | Desenvolvedor → checks → QA → revisor técnico concluíram com login ChatGPT existente |
| Vínculo da revisão | QA e revisor aceitaram o mesmo fingerprint final do código |
| Retomada do sucesso atual | `resume` retornou sucesso mantendo 3 atribuições de agentes |

A tarefa local real é
[`executor-runbook-handoff`](../../examples/execution/executor-runbook-handoff.json).
Ela refinou os rascunhos bilíngues do guia operacional, acrescentou checklists de
primeiro uso e conferiu as informações contra a implementação. O desenvolvedor
usou `workspace-write`; QA/revisor usaram `read-only` e inspecionaram as evidências
dos checks reais. As três atribuições produziram resultados estruturados válidos,
sem achados bloqueantes.

Os checks determinísticos executaram ajuda da CLI, aceite dos guias e os 31 testes
de regressão. A integração cobre também checks reprovados, reparo limitado,
identidade/resultado inválidos, revisão antiga, escrita indevida, ferramenta ausente,
timeout, excesso de saída, limites persistentes e implementação interrompida com
efeitos incertos. Este caso valida documentação; alterações de código exigem seus
próprios casos. Go não foi executado porque a ferramenta não estava disponível.

## As falhas fazem parte da evidência

Execuções anteriores de
[`executor-runbook-validation`](../../examples/execution/executor-runbook-validation.json)
falharam. O sandbox gerenciado do processo principal impediu a inicialização da
configuração do Codex; uma retomada autorizada no host manteve os sandboxes dos
agentes. Depois, o provedor rejeitou nós `const`/`enum` sem tipo no schema nativo.
A tradução foi corrigida e ganhou teste de regressão, preservando o contrato canônico.

Atribuições com limite de 240 segundos também expiraram antes do resultado
estruturado final. Seus rascunhos foram preservados e inspecionados. A nova tarefa
de handoff permitiu 600 segundos por atribuição, 2400 segundos no total e até seis
atribuições. As execuções anteriores mantiveram os limites originais e o estado
de falha; não foram convertidas em aceitas. Eventos SQLite preservam o histórico;
retentativas no mesmo caminho de tentativa/etapa podem sobrescrever artefatos antigos.

## Uso medido e próximas avaliações

A execução bem-sucedida reportou **1.075.351 tokens de entrada**, dos quais
**889.088 em cache**, e **11.590 de saída**. São contagens cumulativas do cliente
entre seus turnos internos, não o tamanho de um único prompt. A saída de raciocínio
é informada separadamente pelo cliente e não é somada novamente à saída total.
O uso das invocações interrompidas não está disponível; esses valores excluem as
falhas anteriores. Custo monetário e ID exato do modelo não foram expostos pelos
eventos capturados. Permanecem desconhecidos; acesso pela conta não implica custo zero.

`max_agent_calls` conta **invocações do adaptador / atribuições Codex**, não cada
requisição ao modelo ou chamada de ferramenta dentro de uma atribuição. Tempo e
caracteres de entrada limitam a execução; este incremento não impõe teto de tokens
ou cobrança do provedor. O consumo medido justifica comparar contextos menores,
mantendo a qualidade do aceite. Ainda não foi demonstrada economia de tokens.

O adaptador carregou explicitamente as instruções TOML geradas e as skills
selecionadas. Descoberta automática, os outros 23 papéis, comportamento Claude/Copilot,
múltiplos modelos, planejamento de produto, reuniões automáticas, plugins e
PR/CI/merge/deploy estão fora desta avaliação.

## Consultar a execução preservada

No checkout fonte com as dependências disponíveis:

```bash
python3 -m dev_agent_kit status 08ac7c001f7646af95c099968c80946b
```

O estado local padrão contém `runs/<run_id>/report.json`, `task.patch`, worktree,
baseline e artefatos do provedor. O JSON da avaliação também guarda hashes dos
guias aprovados. Esse ID exige o estado local preservado, sem transportar execução
para outra máquina; lá será necessário um registro real próprio.
Consulte o [guia operacional](local-executor.md) para instalação e limites da recuperação.

Depois da entrega do executor, um ensaio operacional restaurou a imagem anterior,
passou no smoke autenticado, refez o deploy do código aceito e passou novamente
no smoke. O volume nomeado do banco foi preservado; migrations não foram
revertidas. A integridade do backup privado foi verificada antes do redeploy.
