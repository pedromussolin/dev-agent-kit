# Regras de Gerenciamento de Variáveis de Ambiente e Segredos

## 1. Validação de Schema de Ambiente na Inicialização (Type-Safe Env)
- **Boot Validation:** A aplicação deve validar todas as variáveis de ambiente necessárias durante a fase de inicialização (*startup*).
- **Interrupção Imediata (Fail Fast):** Se uma variável obrigatória estiver ausente ou com tipo inválido, a aplicação deve falhar a inicialização imediatamente e exibir uma mensagem clara no terminal.

```typescript
// ✅ CORRETO: Validação de variáveis de ambiente com Zod no boot da aplicação
import { z } from "zod";

const envSchema = z.object({
  NODE_ENV: z.enum(["development", "production", "test"]),
  PORT: z.string().transform(Number).default("3000"),
  DATABASE_URL: z.string().url(),
});

export const env = envSchema.parse(process.env);
```

---

## 2. O Contrato `.env.example`

* **Sincronização Obrigatória:** Todo repositório deve manter um arquivo `.env.example` na raiz.
* **Valores Fictícios:** O arquivo `.env.example` deve conter todas as chaves exigidas pela aplicação preenchidas com valores de exemplo ou descrições explicativas. NUNCA coloque credenciais reais neste arquivo.

---

## 3. Tolerância Zero para Segredos Hardcoded

* **Proibição Absoluta:** É estritamente proibido incluir chaves de API, tokens JWT, senhas de banco de dados ou segredos de criptografia em arquivos de código.
* **Prevenção no Git:** O arquivo `.env` (com valores reais) deve estar presente no `.gitignore`. Commits contendo segredos reais serão sumariamente rejeitados.