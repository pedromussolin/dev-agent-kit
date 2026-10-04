# Regras de Projetos com Múltiplas Linguagens

## 1. Seleção por Contexto

Inspecione manifests, lockfiles, arquitetura, CI e instruções locais antes de
selecionar ferramentas. Em projetos existentes, preserve a stack e as versões
declaradas. Em novos projetos, registre a decisão com requisitos, alternativas
e consequências. A linguagem do executor do kit não impõe a linguagem do projeto.

## 2. Perfis por Componente

Cada componente deve declarar diretório de trabalho, linguagem, preparação do
ambiente e comandos de formatação, análise estática, testes e build aplicáveis.
Um monorepo pode combinar perfis diferentes. Detecção de manifest sugere um
perfil, mas não autoriza executar comandos automaticamente.

Exemplos de sinais, sem obrigação de instalar todas as ferramentas:

| Linguagem | Sinais | Convenções a preservar |
| --- | --- | --- |
| Python | `pyproject.toml`, `requirements.txt`, lockfile | Ambiente virtual, type hints e ferramentas declaradas pelo projeto |
| JavaScript/TypeScript | `package.json`, lockfile | Gerenciador correspondente ao lockfile e scripts existentes |
| Go | `go.mod`, `go.work` | Ferramentas Go e testes `*_test.go` junto ao pacote |
| Rust | `Cargo.toml`, `Cargo.lock` | Cargo e organização idiomática de testes |
| Java | `pom.xml`, `build.gradle` | Wrapper e estrutura do build existente |
| Outras | Manifests do ecossistema ou configuração explícita | Adaptador explícito, sem fingir suporte automático |

## 3. Princípios Comuns, Implementações Idiomáticas

As regras de idioma (`003`), testes (`007`), segurança (`010`) e segredos (`011`)
permanecem aplicáveis. Bibliotecas de exemplo não são obrigatórias em outra stack.
Go pode usar erros retornados e Python exceções; não imponha classes TypeScript
às duas linguagens. Validação, serialização e observabilidade devem usar os
mecanismos da aplicação e do ecossistema escolhido.

## 4. Verificação Reproduzível

Declare comandos de verificação sem alterações silenciosas no código. Comandos
de autofix devem ser ações de implementação e gerar alterações revisáveis.
Não aceite ferramenta ausente ou comando de teste inexistente como sucesso.
Use dependências e lockfiles do projeto; não instale versões globais por padrão.
