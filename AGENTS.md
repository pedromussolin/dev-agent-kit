# Regras e Instruções para Agentes e Codex

## Documentos de Diretrizes Obrigatórias
Antes de executar qualquer ação, gerar código ou propor operações de Git (criação de branches, PRs ou commits), você DEVE ler e seguir rigorosamente todas as diretrizes contidas no diretório:

- Ler todos os arquivos em: `./docs/regras/*.md`

## Diretrizes Principais
1. **Conformidade com o Git:** Exija sempre a nomenclatura correta de branches (`natureza/ID-tarefa-descricao`) e o formato de commits (`natureza(ID): descricao`) detalhados em `docs/regras/01-git-workflow.md`.
2. **Criação de Branches:** Garanta que qualquer nova branch de desenvolvimento seja criada estritamente a partir da branch `master`.
3. **Zero Contaminação:** Nunca faça merge ou pull das branches `sandbox` ou `staging` para dentro de branches de desenvolvimento.