# Regras de Logs e Observabilidade

## 1. Padrões para Backend (Server-Side Logging)

- **Formato JSON Estruturado:** Todos os logs devem ser emitidos em formato JSON via `stdout`/`stderr` usando bibliotecas dedicadas (ex: Pino, Winston).
- **Injeção de Contexto (Correlation ID):** Toda requisição HTTP deve carregar um `traceId` ou `requestId` injetado via middleware para rastreabilidade de ponta a ponta.
- **Coletores Globais:** Os logs gerados no `stdout` são consumidos automaticamente por agregadores (Datadog, Grafana Loki, ELK, CloudWatch).

```json
{
  "level": "error",
  "timestamp": "2026-09-20T22:30:00.000Z",
  "traceId": "req-98234-abc",
  "service": "billing-service",
  "path": "/api/v1/invoices",
  "message": "Payment gateway timeout",
  "error": {
    "code": "GATEWAY_TIMEOUT",
    "details": "Timeout after 5000ms"
  }
}
```

---

## 2. Padrões para Frontend (Client-Side & Telemetria)

* **Proibido `console.log` em Produção:** Chamadas de `console.log`, `console.warn` ou `console.error` devem ser desativadas/removidas na build de produção (via bundler/Linter).
* **Monitoramento de Exceções (RUM/Error Tracking):** Erros não capturados e falhas de UI devem ser transmitidos para serviços de monitoramento de cliente (ex: Sentry, Datadog RUM, LogRocket).
* **Contexto de Cliente:** Erros de frontend devem incluir meta-informações do ambiente do usuário:
  * `sessionId` e `userId` ou análogos (se autenticado).
  * Rota/URL atual.
  * Informações de ambiente (navegador, sistema operacional, versão da aplicação).



```typescript
// Exemplo de captura no Frontend com Sentry/RUM
Sentry.captureException(error, {
  tags: {
    section: "checkout-flow",
    route: "/checkout/payment",
  },
  extra: {
    cartTotal: 15000,
  },
});
```

---

## 3. Níveis de Log e Quando Usar

* **`FATAL` / `CRITICAL`:** Falhas catastróficas que derrubam a aplicação ou o serviço (ex: falha de conexão no boot do banco de dados).
* **`ERROR`:** Exceções não tratadas, erros 5xx de API ou falhas em Error Boundaries do frontend.
* **`WARN`:** Anomalias ou falhas operacionais esperadas (ex: tentativas de login inválidas, rate-limit atingido, retentativas de rede).
* **`INFO`:** Eventos significativos do ciclo de vida (ex: inicialização do servidor, execução de cron job, troca de status relevante).
* **`DEBUG`:** Informações detalhadas de execução (queries SQL completas, payloads de eventos). **Desativado em produção.**

---

## 4. Proteção de Dados Sensíveis (PII & Security)

Independente da camada (Backend ou Frontend), NUNCA registre nos logs ou envie para serviços de telemetria:

* Credenciais, senhas, tokens JWT, chaves de API e segredos.
* Números de cartão de crédito, CVVs e dados bancários.
* Dados Pessoais Identificáveis (PII) sem anonimização prévia.