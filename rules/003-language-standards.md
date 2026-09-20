# Regras de Idioma, Internacionalização e Documentação

## 1. Código-Fonte e Artefatos Internos (100% Inglês)
Todo o código-fonte deve ser escrito estritamente em **Inglês**. Não é permitido misturar Português com Inglês no código (*Portunglês*).

### O que deve estar OBRIGATORIAMENTE em Inglês:
- **Identificadores:** Nomes de variáveis, funções, métodos, classes, interfaces, tipos e constantes.
- **Banco de Dados:** Nomes de tabelas, colunas, schemas e migrations.
- **Comentários de Código:** Todos os comentários inline, marcadores (`TODO`, `FIXME`) e explicações técnicas.
- **Docstrings e JSDoc:** Todas as descrições de parâmetros, retornos e exceções das funções.
- **Mensagens de Exceção e Logs:** Logs do sistema, mensagens de erro lançadas por classes/funções e códigos de erro internos.
- **Arquivos de Configuração:** Chaves em JSON, YAML, variáveis de ambiente (ex: `.env.example`).

---

## 2. Documentação Externa e Pública (Estrutura por Diretórios)
Toda documentação voltada para consumo humano externo, onboarding ou manuais do sistema deve ser disponibilizada em pastas separadas por idioma.

### Estrutura de Diretórios Padrão:
```text
meu-projeto/
├── README.md                 <-- Inglês (Padrão para GitHub/comunidade)
└── docs/
    ├── en/                   <-- Documentação completa em Inglês
    │   ├── architecture.md
    │   ├── setup.md
    │   └── api-reference.md
    └── pt-br/                <-- Documentação completa em Português
        ├── README.md         <-- Tradução do README principal
        ├── architecture.md
        ├── setup.md
        └── api-reference.md
```

### Regras de Cabeçalho e Navegação:

1. **O `README.md` da raiz** deve ser em Inglês (padrão do GitHub) e conter um link de atalho no topo para a versão em Português:
```markdown
**Languages:** English | [Português (Brasil)](docs/pt-br/README.md)
```


2. **O `docs/pt-br/README.md**` deve conter um link de atalho no topo retornando para a versão em Inglês:
```markdown
**Idiomas:** [English](../../README.md) | Português (Brasil)
```


3. Qualquer novo documento adicionado em `docs/en/` deve ter seu correspondente criado em `docs/pt-br/`.