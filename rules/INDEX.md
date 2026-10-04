# Mapeador de Regras do Projeto (Rule Index)

Este repositório utiliza um sistema modular de regras. **NÃO leia todas as regras de uma vez.** 
Identifique a tarefa atual na tabela abaixo e consulte **APENAS** os arquivos listados na coluna "Regras Aplicáveis".

> ⚠️ **Regra Global Obrigatória:** A regra `003-language-standards.md` deve ser respeitada em **TODAS** as tarefas que envolvam escrita de código, logs, commits ou documentação.
>
> **Escopo:** Exemplos de Node, React, Tailwind e Zod só se aplicam às stacks correspondentes. A regra `012` orienta decisões para Python, Go e outras linguagens.

---

## Tabela de Roteamento por Tarefa

| Tipo de Tarefa | Regras Aplicáveis | O que verificar |
| :--- | :--- | :--- |
| **Git / Branch / Commit / PR** | `001`, `003` | Nomenclatura de branch, formato do commit, origem da branch. |
| **Documentar Código / Docstrings** | `002`, `003` | Padrão JSDoc/Docstring, TODOs com #ID issue. |
| **Estilização / Layout / CSS** | `003`, `004` | Tailwind CSS, utilitário `cn()`, SCSS, tokens. |
| **Criar/Refatorar Componente Frontend** | `003`, `004`, `005` | Arquitetura feature-based, props, estado local, temas (Light/Dark). |
| **Tratamento de Erros / APIs** | `003`, `006` | Classes de erro (`AppError`), JSON payload, middlewares. |
| **Criar ou Ajustar Testes** | `003`, `007` | Estrutura `tests/` (backend) vs colocalizado (frontend), padrão AAA, mocks. |
| **Adicionar Logs / Telemetria** | `003`, `008` | Logs JSON no Backend vs RUM/Sentry no Frontend, remoção de console.log. |
| **Criar Documentação Externa** | `003` | Estrutura de pastas bilingue (`docs/en/` e `docs/pt-br/`). |
| **Criar/Alterar Banco ou Consultas ORM** | `003`, `009` | Nomenclatura `snake_case` em inglês, migrations seguras (Expand-Contract), índices em FKs, prevenção de N+1 queries. |
| **Criar/Alterar Endpoints e APIs** | `003`, `010`, `012` | Validação de entrada na stack adotada, sanitização de saída, headers e rate-limiting. |
| **Adicionar/Alterar Variáveis de Ambiente** | `003`, `011` | Validação de schema no boot da aplicação, sincronização com `.env.example`, proibição de segredos no código. |
| **Escolher Stack / Ferramentas / Monorepo** | `003`, `012`, `015` | Manifests, lockfiles, convenções da linguagem e perfis por componente. |
| **Automatizar SDLC / Orquestrar Agentes** | `001`, `003`, `007`, `011`, `012`, `013`, `015`, `016` | Contratos de tarefas, etapas, evidências, isolamento e política de execução. |
| **Criar Agentes / Skills / Perfis de Provedores** | `003`, `011`, `013`, `014`, `015`, `016` | Fontes portáveis, formatos nativos, geração, preservação de configurações e validação. |
| **Plataforma Local / Custos Cloud / Dados / Estratégia de IA** | `003`, `008`, `009`, `011`, `012`, `015` | Execução local, custo total em BRL, orçamento de IA separado, contratos de dados e avaliações. |

| **Desenhar Extensões / Planejar Evolução / Revisar Compatibilidade** | `003`, `011`, `012`, `013`, `014`, `015`, `016` | Contratos, capacidades, sessões limitadas, decisões e critérios de ativação. |

---

## Resumo Breve de Cada Regra

- **`001-git-workflow.md`**: Git flow, nomes de branches (`feature/ID-desc`), commits imperativos.
- **`002-code-documentation.md`**: Padrão de docstrings/JSDoc e marcação de dívida técnica (`TODO(#ID)`).
- **`003-language-standards.md`**: **(OBRIGATÓRIA)** Código/logs/commits 100% em Inglês. Docs externas em EN e PT-BR em diretórios separados.
- **`004-css-tailwind-standards.md`**: Tailwind CSS, utilitário `cn()`, uso de SCSS e responsividade.
- **`005-frontend-component-architecture.md`**: Arquitetura Feature-Based, limitação de linhas por componente, tokens semânticos de temas.
- **`006-error-handling-standards.md`**: Exceções customizadas, JSON de erro de API, no silent failures.
- **`007-testing-standards.md`**: Testes automáticos (pasta `tests/` no backend vs colocalizado no frontend), AAA e mocks.
- **`008-logging-observability-standards.md`**: Logs JSON estruturados (backend) vs RUM/Sentry (frontend), sanitização de PII.
- **`009-database-migrations-standards.md`**: Convenções `snake_case`, padrão Expand-Contract para migrations, índices em FKs e prevenção de N+1 queries.
- **`010-api-security-standards.md`**: Validação estrita de entrada via Zod, sanitização de saída com DTOs/Serializers, headers OWASP e rate-limiting.
- **`011-env-secrets-management.md`**: Validação de variáveis de ambiente no startup, contrato `.env.example` e tolerância zero para segredos hardcoded.
- **`012-polyglot-project-standards.md`**: Escolha de stack pelo projeto, adaptadores por componente e convenções idiomáticas.
- **`013-agent-sdlc-workflow.md`**: Contratos, orquestração, critérios de passagem e evidências para automação do SDLC.
- **`014-agent-skills-provider-standards.md`**: Organização de agentes e skills, formatos nativos e validação das exportações.

- **`015-local-data-ai-policy.md`**: Plataforma local, teto de infraestrutura, IA com orçamento separado, dados e avaliações.

- **`016-modularity-planning-governance.md`**: Integrações substituíveis, planejamento por evidências, compatibilidade e crescimento comercial.
