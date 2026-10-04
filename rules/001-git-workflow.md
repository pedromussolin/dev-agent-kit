# Regras Obrigatórias de Git e GitHub

## Ambientes e Branches
- **sandbox** → Branch `sandbox` (Homologação interna)
- **staging** → Branch `staging` (Pré-release)
- **Produção** → Branch principal definida pelo projeto (`main`, `master` ou outra configuração explícita).

Descubra a branch principal pelo contexto do projeto e pelo HEAD remoto. Neste
repositório, a branch principal é `main`. Não crie uma branch `master` apenas para
adequar o projeto a um exemplo de regra. `sandbox` e `staging` são convenções para
projetos que adotam esses ambientes, não branches obrigatórias em todo repositório.

---

## Padrões de Nomenclatura (100% em Inglês - Alinhado à Regra 03)

### Branches
Toda branch DEVE ser criada a partir de uma Issue do GitHub e ter seu nome em **Inglês**, seguindo a convenção:
- `feature/ID-task-description` (ex: `feature/3718-adjust-linked-entity-enum`)
- `fix/ID-task-description` (ex: `fix/3718-fix-compound-interest-calculation`)
- `hotfix/ID-task-description` (ex: `hotfix/3718-fix-compound-interest-calculation`)
- `refact/ID-task-description` (ex: `refact/3718-refactor-linked-entity-enum`)
- `release/AAAAMMDD` (ex: `release/20260920`)

*Regra:* Para `feature`, `fix`, `hotfix` e `refact`, a descrição em inglês deve conter entre **3 a 6 palavras**.

### Commits
A estrutura e mensagem do commit DEVEM ser escritas em **Inglês no modo imperativo**:
`natureza(IDtask): Description in imperative present tense`

Tipos permitidos:
- `feat` → Novas funcionalidades
- `fix` → Correções de bugs
- `docs` → Documentação (Readme, docstrings, etc.)
- `style` → Alterações de formatação ou estilo
- `refact` → Refatoração sem alteração de funcionalidade
- `test` → Adição ou ajuste de testes
- `build` → Configurações de build/CI (Docker, pacotes)
- `perf` → Melhorias de performance
- `chore` → Tarefas gerais que não alteram código do sistema

Exemplo: `feat(3718): Adjust linked entity enum`

---

## Fluxo de Trabalho e Restrições Críticas

1. **Origem Obrigatória:** Toda nova branch de desenvolvimento DEVE ser criada a partir da branch principal atualizada e confirmada no projeto. Inspecione o estado de trabalho antes de atualizar ou alterar branches; não sobrescreva alterações locais.
2. **Proibição de Merge Inverso:** NUNCA faça `git pull` ou `git merge` das branches `staging` ou `sandbox` para dentro da sua branch de desenvolvimento.
3. **Resolução de Conflitos:** Resolva conflitos apenas via rebase/merge com a branch principal ou através de branches de integração próprias.

4. **Rastreabilidade:** Use um ID real de Issue/tarefa nas branches e commits. Enquanto não existir um ID, prepare alterações locais para revisão sem inventar números.
