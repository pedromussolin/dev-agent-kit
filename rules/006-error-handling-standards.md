# Regras de Tratamento de Erros, Resiliência e Logging

## 1. Princípios Fundamentais
- **Proibido Engolir Erros (No Silent Failures):** Blocos `catch` vazios ou que apenas imprimem o erro no console sem tratar ou propagar a exceção são estritamente proibidos.
- **Fail Fast (Falhe Rápido):** Valide parâmetros e pré-condições no início da execução de funções e rotas. Lance exceções o mais cedo possível para evitar estados inconsistentes.
- **Erros Previsíveis vs. Inesperados:**
  - *Erros Previsíveis (Operacionais):* Validações de entrada, recurso não encontrado, falta de permissão. Devem ser capturados e retornar respostas amigáveis.
  - *Erros Inesperados (Bugs/Infraestrutura):* Falha de banco de dados, falha de memória, estouro de ponteiro. Devem ser capturados por handlers globais, logados criticamente e mascarados para o cliente final.
---

## 2. Exceções Customizadas e Tipadas
Em vez de lançar `throw new Error("msg")` genérico, crie classes de erro customizadas derivadas de uma classe base (`AppError`).

### Exemplo de Estrutura de Erros (`src/errors/`):

```typescript
// Base class for all operational errors
export class AppError extends Error {
  public readonly statusCode: number;
  public readonly code: string;
  public readonly details?: unknown;

  constructor(message: string, statusCode = 400, code = "INTERNAL_ERROR", details?: unknown) {
    super(message);
    this.name = this.constructor.name;
    this.statusCode = statusCode;
    this.code = code;
    this.details = details;
    Error.captureStackTrace(this, this.constructor);
  }
}

// Specialized errors
export class NotFoundError extends AppError {
  constructor(entity: string, id?: string | number) {
    const message = id ? `${entity} with id '${id}' was not found.` : `${entity} not found.`;
    super(message, 404, "RESOURCE_NOT_FOUND");
  }
}

export class UnauthorizedError extends AppError {
  constructor(message = "Unauthorized access.") {
    super(message, 401, "UNAUTHORIZED");
  }
}

export class ValidationError extends AppError {
  constructor(message: string, details?: unknown) {
    super(message, 422, "VALIDATION_FAILED", details);
  }
}
```

---

## 3. Estrutura Padronizada de Resposta de API (JSON Error Payload)

Toda resposta de erro de API deve seguir estritamente o mesmo schema JSON para facilitar o consumo pelo frontend:

```json
{
  "success": false,
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "User with id '3718' was not found.",
    "details": null
  }
}
```

* **Ambiente de Desenvolvimento:** Pode incluir o campo `"stack"` na resposta.
* **Ambiente de Produção (Master):** O campo `"stack"` NUNCA deve ser enviado ao cliente por questões de segurança.

---

## 4. Captura Global e Handlers (Backend & Frontend)

### Backend (Middleware Centralizado)

Evite colocar blocos `try/catch` genéricos em todos os controllers/rotas. Deixe que exceções não tratadas subam para o middleware global de erro:

```typescript
// Express / Fastify Error Handler Example
export function errorHandler(error: Error, req: Request, res: Response, next: NextFunction) {
  if (error instanceof AppError) {
    return res.status(error.statusCode).json({
      success: false,
      error: {
        code: error.code,
        message: error.message,
        details: error.details,
      },
    });
  }

  // Log unexpected system errors for internal review
  logger.error({ err: error, path: req.path }, "Unhandled System Exception");

  // Mask internal error details from external users
  return res.status(500).json({
    success: false,
    error: {
      code: "INTERNAL_SERVER_ERROR",
      message: "An unexpected error occurred. Please try again later.",
    },
  });
}
```

### Frontend (Error Boundaries & Interceptors)

* **API Interceptors:** Capture respostas de erro HTTP (ex: Axios/Fetch Interceptor) para redirecionar em `401 (Unauthorized)` ou acionar notificações de toast globais.
* **Error Boundaries:** Envolva áreas críticas da UI (gráficos, tabelas complexas, checkout) em *Error Boundaries* para que uma falha isolada em um componente não quebre a tela inteira da aplicação.

---

## 5. Regras de Logging e Privacidade (PII)

* **Níveis de Log:**
    * `logger.error()`: Apenas para falhas do sistema, erros 5xx ou exceções não tratadas.
    * `logger.warn()`: Para erros operacionais 4xx (tentativas inválidas, não autorizado, rate limit).
    * `logger.info()`: Para eventos importantes do ciclo de vida (ex: "User #123 created").


* **Proteção de Dados Sensíveis:** NUNCA grave em arquivos de log ou serviços externos:
    * Senhas, hashes de autenticação e PINs.
    * Tokens JWT, chaves de API e números de cartão de crédito.
    * Dados pessoais sensíveis (CPF, e-mail, telefone) sem prévia anonimização/mascaramento.