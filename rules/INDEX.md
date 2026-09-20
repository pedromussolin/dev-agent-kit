# Mapeador de Regras do Projeto (Rule Index)

Este repositório utiliza um sistema modular de regras. **NÃO leia todas as regras de uma vez.** 
Identifique a tarefa atual na tabela abaixo e consulte **APENAS** os arquivos listados na coluna "Regras Aplicáveis".

> ⚠️ **Regra Global Obrigatória:** A regra `003-language-standards.md` deve ser respeitada em **TODAS** as tarefas que envolvam escrita de código, logs, commits ou documentação.

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
| **Criar/Alterar Endpoints e APIs** | `003`, `010` | Validação estrita de entrada (Zod), sanitização de saída via DTOs, headers OWASP e rate-limiting. |
| **Adicionar/Alterar Variáveis de Ambiente** | `003`, `011` | Validação de schema no boot da aplicação, sincronização com `.env.example`, proibição de segredos no código. |

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