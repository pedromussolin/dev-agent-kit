# Planejamento e melhoria contínua

**Idiomas:** [English](../en/planning-governance.md) | Português (Brasil)

Uma organização precisa ligar objetivos, decisões e execução. No kit, a reunião é
um workflow limitado para resolver uma decisão e produzir um artefato rastreável.
Ela pode ser assíncrona e começar com relatórios existentes; não precisa simular
uma conversa entre todos os agentes.

## Papéis na organização

| Responsabilidade | Papéis existentes |
| --- | --- |
| Direção e valor | Usuário, PM e estrategista de IA |
| Priorização e aceite | PO e planejador |
| Coerência técnica | Arquiteto, engenheiro e estrategista de tecnologias |
| Experiência e qualidade | UX/UI, acessibilidade, QA, segurança e avaliações LLM |
| Plataforma e dados | Cloud, DevOps, SRE, DBA, engenharia de dados e MLOps |
| Execução e registro | Desenvolvedor, revisor, release, redator e coordenador |

Essas são responsabilidades, não cargos que precisam de um processo permanente.
O usuário define objetivos e autoridade; agentes fornecem análises e executam tarefas
no escopo existente. Uma decisão pode ser adotada dentro de autorização já concedida,
sem pedir a mesma aprovação novamente.

## Sessões sugeridas

| Sessão | Gatilho | Saída |
| --- | --- | --- |
| Direção de produto | Novo objetivo ou revisão do valor entregue | Hipóteses, resultado esperado e prioridades |
| Refinamento/planejamento | Trabalho pronto para divisão | Backlog proposto, critérios de aceite e dependências |
| Decisão técnica | Nova ferramenta, fornecedor ou mudança de arquitetura | Alternativas, decisão e ensaio de validação |
| Retrospectiva | Entrega, incidente ou regressão de avaliações | Melhoria priorizada com evidências |

Cadência semanal para revisar prioridades é uma sugestão inicial. Uma decisão simples
pode ser tomada diretamente. A sessão existe quando perspectivas ou evidências precisam
ser conciliadas; não deve adicionar custo a toda correção pequena.

## Fluxo e critérios de passagem

1. Registrar objetivo, decisão a tomar, evidências, autoridade e limites de recursos.
2. Pedir contribuições somente aos papéis pertinentes, preservando referências.
3. Comparar opções por valor, esforço, dados/IA, custo, dependências e reversibilidade.
4. Registrar decisão proposta, adotada ou adiada; manter discordâncias e incertezas.
5. Transformar ações em tarefas com responsável, aceite e dependências. Uma ação só
   fica pronta para o executor com ID real, decisão adotada e política efetiva válida.
6. Medir o resultado e atualizar o backlog com feedback.

Limites de rodadas, chamadas e tempo são obrigatórios no contrato da sessão. Limite
financeiro de IA continua separado e deve ser configurado para inferência paga.
Uma reunião não amplia permissões, instala ferramentas nem publica automaticamente.

Use a [skill de planejamento](../../.agents/skills/sdlc-planning-session/SKILL.md),
o [template](../../templates/planning-session.md) e o
[contrato de resultado](../../contracts/planning-session.schema.json).
O [exemplo](../../examples/planning/example-session-result.json) é fictício e
contém propostas, não aprovações ou issues reais. O schema valida o formato;
o executor ainda deverá verificar referências, ciclos, autoridade e disponibilidade
dos papéis. Agendamento e execução automática de sessões ainda não existem.

## Como novas ferramentas entram

Uma proposta identifica problema, alternativa existente, capacidade, custo,
limites de acesso e ensaio de conformidade. O arquiteto usa a
[skill de extensões](../../.agents/skills/sdlc-extension-design/SKILL.md) e o
[template de proposta](../../templates/extension-proposal.md). O PO prioriza a
implementação conforme valor e dependências. DevOps/segurança/dados contribuem
quando a integração envolve seus domínios; configuração e ativação seguem a tarefa.

Registre decisões duradouras com status, alternativas, consequências e critério
para revisitar. Resumos curtos e referências reduzem contexto repetido. Evidências
antigas ou alegações sem fonte não viram consenso por repetição.
