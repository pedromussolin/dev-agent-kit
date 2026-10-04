# Plataforma local, dados, IA e orçamento

**Idiomas:** [English](../en/local-platform-and-ai.md) | Português (Brasil)

Requisitos: execução inicialmente local; nuvem opcional para uso pessoal com teto
**total de R$ 100/mês em infraestrutura**; IA com orçamento separado ainda não
quantificado. A [política canônica](../../policies/project-defaults.json) acompanha
cada skill. As recomendações abaixo foram pesquisadas em fontes oficiais em
03/10/2026. Nenhum serviço foi instalado ou provisionado por esta alteração.

## Ferramentas recomendadas e ordem de adoção

A proposta usa ferramentas conhecidas, mantidas e adequadas ao problema. Uma versão
recente só entra depois de verificar compatibilidade, licença e estabilidade,
fixando a versão e o lockfile ou digest de imagem pertinente ao projeto.

| Necessidade | Recomendação | Quando ativar e por quê |
| --- | --- | --- |
| Estado do executor | SQLite, eventos persistidos e logs JSON | Primeiro incremento: reduz serviços e facilita inspeção, backup e retomada local |
| Serviços locais | Docker Compose | Quando houver banco ou telemetria: configura serviços reproduzíveis com perfis opcionais |
| Banco da aplicação | PostgreSQL | Quando a aplicação precisa de banco relacional compartilhado; a stack existente continua orientando a escolha |
| Administração de banco | DBeaver Community | Consultas, inspeção de schemas e análise manual; acesso mínimo e leitura quando suficiente |
| Logs consultáveis | Grafana + Loki + Alloy | Quando arquivos locais deixarem de atender a investigação; limitar retenção e volume |
| Métricas e instrumentação | Prometheus + OpenTelemetry | Medir duração, falhas e recursos; evitar labels de alta cardinalidade como texto de prompts |
| Traces | Tempo, opcional | Quando correlação de chamadas ajudar a diagnosticar operações; não exige ativação inicial |
| Observabilidade de IA | Langfuse, opcional | Quando comparação de prompts, versões e traces justificar a infraestrutura adicional |
| Avaliações de IA | Testes do projeto; promptfoo quando útil | Comparar modelos, prompts e ferramentas por casos reproduzíveis, qualidade e custo |
| Modelos locais | Ollama, opcional | Após medir qualidade, memória, latência e capacidade do hardware disponível |
| Busca vetorial | pgvector, opcional | Somente quando recuperação semântica resolver um requisito demonstrado |
| Infraestrutura cloud | OpenTofu | Quando a nuvem for necessária: infraestrutura declarada, versionada e revisável |

Compose configura aplicações com vários serviços; OpenTelemetry fornece
instrumentação de logs, métricas e traces. DBeaver Community é uma ferramenta
aberta de administração de bancos. Consulte as documentações de
[Compose](https://docs.docker.com/compose/),
[OpenTelemetry](https://opentelemetry.io/docs/) e [DBeaver](https://dbeaver.io/).
Para os demais componentes, consulte
[Loki](https://grafana.com/docs/loki/latest/setup/install/docker/),
[Alloy](https://grafana.com/docs/alloy/latest/),
[Prometheus](https://prometheus.io/docs/introduction/overview/),
[Tempo](https://grafana.com/docs/tempo/latest/),
[PostgreSQL](https://www.postgresql.org/docs/current/pgstatstatements.html),
[pgvector](https://github.com/pgvector/pgvector),
[promptfoo](https://www.promptfoo.dev/docs/intro/),
[Ollama](https://docs.ollama.com/) e [OpenTofu](https://opentofu.org/docs/).

O SQLite guarda execuções do kit; ele não determina o banco dos projetos. O DBA
pode usar estatísticas de consultas do PostgreSQL para investigar gargalos antes
de recomendar novos índices. Mudanças de schema e acesso ao banco real continuam
sujeitas ao escopo da tarefa e à política do projeto.

Langfuse em Compose utiliza vários componentes, incluindo PostgreSQL, ClickHouse,
Redis/Valkey e armazenamento de objetos. Por isso não entra no perfil mínimo. Ferramentas
inteligentes também precisam de operação: telemetria, avaliações e análise de
consultas devem produzir evidências, com automações de reparo limitadas à autorização
existente. [Arquitetura do Langfuse](https://langfuse.com/self-hosting#architecture).

## Local e nuvem dentro do teto

Local significa hospedar o executor e seus serviços na sua máquina. O processamento
do modelo pode continuar remoto, conforme o cliente/provedor escolhido, e terá
contabilidade de IA separada. Software aberto local não implica custo zero de
energia, hardware ou manutenção.

A primeira alternativa cloud a avaliar é híbrida: executor e banco locais, com
telemetria sanitizada no plano gratuito do Grafana Cloud. Na consulta atual, o
plano gratuito oferece 50 GB de logs ingeridos/mês e retenção de 14 dias; métricas
possuem limite de 10 mil séries ativas. O plano Pro começa em US$ 19/mês mais uso,
portanto não deve ser considerado automaticamente compatível com o seu teto.
As condições devem ser conferidas antes da adoção. [Preços oficiais do Grafana](https://grafana.com/pricing/).

Uma VPS pequena é uma segunda alternativa, condicionada ao hardware exigido e
à estimativa completa. Como referência, o reajuste oficial da Hetzner em
15/06/2026 informa CX23 a € 5,49/mês na Alemanha/Finlândia, sem IPv4 e VAT. Isso é apenas
o preço de uma linha, não uma promessa de custo total nem uma decisão de provedor.
[Reajuste oficial](https://docs.hetzner.com/general/infrastructure-and-availability/price-adjustment/).

Antes de aprovar qualquer desenho cloud, o arquiteto deve registrar:

| Item | Evidência necessária |
| --- | --- |
| Compute, banco e observabilidade | Plano, região, quantidade e preço oficial com data |
| Disco, backup, tráfego e IP quando cobrados | Volume previsto, retenção e cobrança aplicável |
| Câmbio e encargos | Conversão para BRL, impostos e tarifas do meio de pagamento |
| Limites gratuitos | Franquia, comportamento ao atingir o limite e ausência de upgrade pago automático |
| Total mensal | Cenário esperado e cenário de crescimento; total dentro dos R$ 100 |

Sugestão de planejamento: reservar R$ 20 do teto para variação, buscando uma
estimativa de até R$ 80. Essa margem é uma recomendação, não um novo limite imposto
pelo usuário. Faltando preços ou informações de uso, a proposta fica incompleta;
a existência de alertas financeiros não garante um bloqueio absoluto de cobrança.

## Data-first e AI-first na prática

Data-first significa começar por schema, propriedade, qualidade e origem dos
dados, além de privacidade, retenção e recuperação. O agente deve saber quais
dados foram usados, de onde vieram e quais validações passaram. RAG, vetores e
pipelines distribuídos entram quando o requisito pedir.

AI-first significa avaliar IA desde o desenho do produto e das ferramentas:
resultados estruturados, uso limitado de ferramentas, avaliações e fallback.
Operações determinísticas continuam sendo a referência quando entregam o resultado
com menos custo e variabilidade. Um exemplo: o modelo planeja a mudança; comandos
reais de teste e um validador de schema determinam se as evidências de aceite passaram.

| Papel novo | Entrega esperada |
| --- | --- |
| Estrategista de IA | Oportunidades, baseline, roadmap e critérios de investimento |
| Engenheiro de IA | Integrações de modelos, ferramentas e recuperação avaliadas |
| Engenheiro de contexto | Contexto por papel, prompts versionados e comparação de custo/qualidade |
| Engenheiro de dados | Ingestão, contratos, qualidade, origem e recuperação |
| Engenheiro de avaliações LLM | Casos de regressão e critérios de qualidade, segurança, latência e custo |
| Engenheiro MLOps | Versões, entrega, monitoramento e rollback de capacidades de IA |

Eles colaboram com os papéis existentes. DBA cuida de armazenamento e consultas;
engenharia de dados cuida dos fluxos e contratos. QA verifica o aceite do produto;
avaliações LLM verificam comportamento probabilístico. DevOps cuida da entrega;
MLOps acrescenta versões e critérios específicos de IA. A tarefa escolhe quais
responsabilidades precisam atuar, sem iniciar todos os 26 agentes em cada execução.

## Economia de tokens com evidências

1. Selecionar arquivos e trechos relevantes, passando referências e resumos por papel.
2. Executar descoberta, testes e validações determinísticas com ferramentas; enviar apenas resultados úteis ao modelo.
3. Limitar tentativas, chamadas de ferramentas, tamanho de contexto e duração.
4. Testar modelos mais econômicos por classe de tarefa, com escalonamento justificado.
5. Usar cache conforme o provedor/modelo e invalidar artefatos quando código ou dados mudarem.
6. Comparar custo por tarefa aceita, incluindo retentativas e modelos usados como avaliadores.

Cache é específico do provedor e da versão; o executor não deve supor que todos
os clientes expõem uso e cache da mesma maneira. Uso ausente é `unknown`, não zero.
Consulte [prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching)
e [boas práticas de avaliações](https://developers.openai.com/api/docs/guides/evaluation-best-practices).

Não há promessa de percentual de economia. O relatório deve separar observado,
estimado e indisponível, registrando modelo, versão do prompt/dados, tokens de
entrada/saída/cache quando expostos, latência, tentativas e qualidade. A política
está nas instruções e é validada quanto à consistência do empacotamento. Os
limites de chamadas/tempo/contexto já são impostos pelo executor local, que registra
tokens expostos com custo monetário desconhecido. Tetos de cobrança do provedor,
seleção de modelos e avaliações comparativas de economia ficam para novos incrementos.

Leia a [decisão do executor](executor-decision.md) e o [guia operacional](local-executor.md).
