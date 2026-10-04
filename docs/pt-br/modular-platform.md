# Plataforma modular e caminho para um produto

**Idiomas:** [English](../en/modular-platform.md) | Português (Brasil)

A direção recomendada é um **monólito modular com interfaces substituíveis**:
um processo local inicialmente, módulos com contratos explícitos e integrações
selecionadas por configuração. Isso permite mudar tecnologias e crescer mantendo
as responsabilidades claras, dentro da operação pessoal e do teto de infraestrutura.

## Aprender o desacoplamento

O domínio descreve tarefa, decisão, política, tentativa e evidência. Ele não importa
SDK de modelo, cliente de banco ou API do GitHub. Define interfaces que adaptadores
implementam. Esse desenho é conhecido como ports and adapters; aqui, uma porta é
um contrato, e um adaptador conecta uma tecnologia a esse contrato.

Exemplo: o fluxo chama `execute(Assignment)` em um adaptador de agente. O adaptador
Codex ou Claude transforma a entrada para seu cliente e normaliza o resultado.
Trocar o cliente mantém os critérios de passagem do fluxo. Capacidades e resultados
podem diferir, então a troca só é válida após verificar compatibilidade e avaliações.

| Fronteira substituível | Contrato esperado | Implementação inicial proposta |
| --- | --- | --- |
| Agente | Executar atribuição, cancelar, declarar capacidades e uso disponível | Um cliente local validado |
| Stack | Executar checks por componente e retornar comandos/saídas/revisão | Comandos explícitos Python, Go ou outra stack |
| Estado | Persistir/consultar transições e reconciliar tentativas | SQLite com transações |
| Entrega | Criar/consultar PR e CI; operações distintas para merge/deploy | Diff/relatório e entrega GitHub configurável |
| Telemetria | Registrar eventos sanitizados e correlação | JSON local; exportadores opcionais |
| Ferramenta | Receber argumentos tipados e devolver resultado validado | Função local, CLI, MCP ou HTTP conforme o caso |
| Formato de perfil | Transformar papel/skills em arquivos nativos | Geradores Codex, Claude e Copilot já separados |

O runtime local implementa `AgentAdapter` com `CodexCLI`, comandos explícitos por
componente, estado SQLite e entrega de diff. O armazenamento é concreto, sem porta
injetável; entrega remota e exportadores de telemetria seguem planejados.
O empacotador já permite
injetar um gerador de perfis por código, reaproveitando validação, exportação e
preservação de arquivos. A CLI continua oferecendo os três provedores conhecidos;
carregar extensões arbitrárias por manifesto ainda não foi implementado.

## Plug and play com um contrato real

O [manifesto de extensão](../../contracts/plugin-manifest.schema.json) é um contrato
interno proposto do kit. Ele informa ID/versão, tipo, versão do protocolo, capacidades,
implementação, permissões, contratos, configuração e evidência de conformidade.
Não é um formato exigido pelos provedores nem um instalador universal.

Uma integração deverá passar por: registro explícito → compatibilidade → configuração
validada → acesso permitido → verificação funcional → ativação. Se uma capacidade
obrigatória estiver ausente, a tarefa fica bloqueada com motivo. Capacidades opcionais
podem ter fallback documentado. Um manifesto não concede acesso nem prova conformidade.

O [exemplo de adaptador Python](../../examples/plugins/example-python-checks.json)
é deliberadamente inerte: o módulo e contratos com prefixo `kit://proposed/` ainda
não existem. Serve para revisar o desenho; o futuro loader deve rejeitá-lo enquanto
essas referências e evidências não forem resolvidas.

Para ferramentas externas, MCP padroniza a comunicação entre cliente e servidor.
Ele pode conectar uma ferramenta de banco ou infraestrutura a vários clientes.
O adaptador ainda precisa resolver configuração, acesso e significado do resultado;
MCP não implementa o SDLC. [Especificação oficial](https://modelcontextprotocol.io/specification/2026-07-28).

## Escalar em etapas

1. **Uma pessoa:** uma tarefa por vez, módulos locais, estado persistido, contratos e recuperação verificada.
2. **Vários projetos:** IDs de projeto/execução, configuração separada, limites e workspaces próprios; nenhuma credencial global em prompts.
3. **Mais trabalho simultâneo:** concorrência limitada, locks, filas e workers quando carga real justificar; invalidar evidências após mudanças.
4. **Usuários externos:** identidade, isolamento de dados/segredos/cotas, auditoria, exportação e suporte antes de aceitar clientes.
5. **Operação comercial:** medição por cliente, planos, cobrança e objetivos de disponibilidade/recovery com custos próprios.

A primeira implementação deve identificar projeto e execução nos artefatos e manter
storage, entrega e modelos atrás das interfaces. Não precisa implementar uma plataforma
multiusuário já. Migrar SQLite para PostgreSQL ou extrair workers exigirá migrações e
testes de equivalência, mesmo com uma interface estável.

O teto de R$ 100 vale para sua infraestrutura pessoal. Um serviço comercial deve
ter orçamento e custo por cliente explicitamente configurados; não pode herdar uma
promessa de hospedagem nesse teto. A linguagem de um plugin também não determina a
linguagem dos projetos; processos/MCP/HTTP podem conectar implementações diferentes.

## Monetização orientada por evidências

Primeiro medir o resultado pessoal: tarefas aceitas, tempo poupado, custo, taxa de
retrabalho e confiabilidade. Depois identificar um problema repetível para um público:
qual entrega ele compra e como verificar que recebeu valor.

Avaliar kit distribuível, serviço assistido e SaaS gerenciado como modelos distintos.
Antes da distribuição comercial, escolher a licença do kit e verificar direitos das
dependências, termos dos provedores, dados e custos. O repositório não possui uma
licença explícita nesta revisão; nenhuma licença foi escolhida automaticamente.

A diferenciação deve vir de resultados reproduzíveis, integrações úteis e operação
confiável. Um catálogo de muitos agentes por si só não demonstra valor comercial.
A [governança de planejamento](planning-governance.md) organiza as decisões e o
[registro de compatibilidade](provider-readiness.md) mostra o que já foi verificado.
