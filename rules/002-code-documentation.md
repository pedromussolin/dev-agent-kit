# Regras de Documentação de Código, Docstrings e Comentários

## 1. Princípio Fundamental (Código Autoexplicativo)
- O código deve ser escrito de forma clara e legível por si só.
- Nomes de variáveis, funções e classes devem revelar sua intenção sem necessidade de comentários explicativos sobre *o que* estão fazendo.
- **Regra de Ouro:** Use comentários para explicar o **PORQUÊ** (motivação, regra de negócio complexa, limitação técnica) e NUNCA o **O QUE** (sintaxe óbvia).

---

## 2. Docstrings e Documentação de APIs/Funções

### Quando usar
- **Obrigatório:** Em funções públicas, métodos exportados, interfaces de API, serviços, utilitários globais e classes.
- **Opcional:** Em funções utilitárias internas/privadas de escopo muito reduzido e simples.

### Padrão por Linguagem

#### JavaScript / TypeScript (TSDoc / JSDoc)
- Utilize o formato `/** ... */`.
- Descreva sucintamente o objetivo, parâmetros (`@param`), tipo de retorno (`@returns`) e erros lançados (`@throws`), quando aplicável.

```typescript
/**
 * Calcula o valor atualizado do contrato com base na taxa de juros e mora.
 *
 * @param valorInicial - O valor base do contrato em centavos.
 * @param diasAtraso - Quantidade de dias passados do vencimento.
 * @returns O valor total corrigido em centavos.
 * @throws {InvalidArgumentError} Se o valor inicial ou dias de atraso forem negativos.
 */
export function calcularValorCorrigido(valorInicial: number, diasAtraso: number): number { ... }

```

#### Python (Google / Docstring Style)

* Utilize aspas triplas `""" ... """`.
* Indique os argumentos, retorno e exceções.

```python
def calcular_valor_corrigido(valor_inicial: int, dias_atraso: int) -> int:
    """Calcula o valor atualizado do contrato com base na taxa de juros e mora.

    Args:
        valor_inicial: O valor base do contrato em centavos.
        dias_atraso: Quantidade de dias passados do vencimento.

    Returns:
        O valor total corrigido em centavos.

    Raises:
        ValueError: Se o valor inicial ou dias de atraso forem negativos.
    """

```

---

## 3. Comentários Inline (No meio do código)

### O que NUNCA fazer

```typescript
// NUNCA FAÇA ISSO: Comentar o óbvio
const status = "active"; // define o status como ativo
if (user.age >= 18) { // verifica se é maior de idade

```

### O que FAZER

```typescript
// FAÇA ISSO: Explicar contornos técnicos ou regras de negócio específicas
// A API de pagamentos retorna erro 422 caso a transação seja processada
// em menos de 2 segundos após a criação. Adicionamos um delay intencional.
await sleep(2000);

```

---

## 4. Marcações Especiais (`TODO`, `FIXME`, `HACK`)

Todas as marcações pendentes no código **devem ser vinculadas ao ID de uma Issue do GitHub**:

* **`TODO(#ID)`:** Para tarefas ou melhorias pendentes que serão feitas no futuro.
* **`FIXME(#ID)`:** Para trechos de código que contêm bugs conhecidos ou comportamentos instáveis.
* **`HACK(#ID)`:** Para soluções temporárias ou contornos (workarounds) técnicos.

### Exemplos Obrigatórios:

```typescript
// TODO(#3718): Refatorar a chamada para usar o novo endpoint v2 do serviço de e-mail.
// FIXME(#3718): Tratar o estouro de memória em arquivos de log superiores a 50MB.

```

---

## 5. Idioma da Documentação no Código
- **Regra Absoluta:** Todas as docstrings, JSDoc, comentários inline e marcações (`TODO`, `FIXME`) DEVEM ser escritos **100% em Inglês**, sem exceções.
- Para detalhes sobre a documentação externa (arquivos Markdown em `docs/`), consulte a regra `03-language-standards.md`.