# Regras de Agentes, Skills e Perfis de Provedores

## Fontes de verdade

- `agents/catalog.json` registra os papéis, permissões locais pretendidas e skills.
- `agents/*.md` define responsabilidades e contratos independentes do provedor.
- `.agents/skills/*/SKILL.md` contém procedimentos portáveis e focados em tarefas.
- `contracts/agent-result.schema.json` é o contrato de saída compartilhado.
- `policies/project-defaults.json` define padrões locais, orçamento, dados e IA.
- Cada skill inclui cópias portáveis do contrato e da política em `references/`.
- Perfis em `.codex/agents/`, `.claude/agents/` e `.github/agents/` são gerados.
- Skills em `.claude/skills/` são cópias geradas para descoberta pelo Claude Code.

Edite as fontes, depois execute `python3 scripts/provider_profiles.py --target .`.
Ao alterar o schema ou a política, use `--sync-resources` para atualizar as
referências portáveis; `--sync-contracts` permanece como alias compatível.
Não mantenha variantes de prompts manualmente nos diretórios gerados. O exportador
recusa sobrescrever perfis alterados localmente; reconcilie a mudança com a fonte.

## Escopo e formato

Uma skill descreve como executar uma capacidade. Um perfil de agente descreve o
papel e sua configuração no cliente. O padrão comum de skill usa `name` e
`description` no frontmatter YAML, mais instruções Markdown e recursos opcionais.
O kit mantém frontmatter mínimo para reduzir diferenças entre clientes.

`agents/openai.yaml` dentro de uma skill é metadado de interface do Codex;
ele não cria um agente independente e não é requisito geral dos outros clientes.
Modelos e credenciais são escolhidos na configuração de execução, não embutidos
nas skills. Preserve a descoberta automática das skills, salvo pedido explícito.

## Validação e comportamento

Execute o verificador de perfis e os testes do kit. A validação de arquivos não
comprova qualidade de decisões ou compatibilidade de todas as versões dos clientes.
Teste os papéis com tarefas reais autorizadas antes de depender deles em execução
autônoma. Registre versão do cliente e resultado observado.

Ferramentas declaradas e sandbox não substituem a autorização da tarefa. Evite
desativar controles de execução para contornar integrações ausentes. A presença
de perfis e skills não implementa persistência, agendamento ou recuperação do SDLC.

Consulte `docs/pt-br/agents-and-skills.md` para formatos, exemplos e fontes oficiais.

Registre evidências por cliente e superfície em `providers/compatibility.json`.
Schemas especializados em `contracts/*.schema.json` podem acompanhar skills em
`references/`; `--sync-resources` também atualiza essas cópias existentes.
