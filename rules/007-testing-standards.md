# Regras de Testes Automáticos e Qualidade de Código

## 1. Padrão de Organização para Backend

No backend, **todos os testes devem ser mantidos em uma pasta dedicada `tests/` na raiz do projeto**, separando por tipo de teste para não poluir o diretório `src/`:

```text
backend-project/
├── src/                          <-- Apenas código de produção
│   ├── controllers/
│   │   └── user.controller.ts
│   └── services/
│       └── user.service.ts
└── tests/                        <-- Pasta dedicada de testes
    ├── unit/                     <-- Testes de regras de negócio isoladas
    │   └── services/
    │       └── user.service.test.ts
    ├── integration/              <-- Testes de rotas HTTP e banco de dados
    │   └── controllers/
    │       └── user.controller.test.ts
    └── e2e/                      <-- Testes de fluxos completos de API
        └── health-check.spec.ts
```

---

## 2. Padrão de Organização para Frontend

No frontend, adota-se a **colocalização para testes unitários/componentes** e uma pasta dedicada apenas para fluxos **E2E**:

```text
frontend-project/
├── src/                          <-- Código de produção com testes unitários
│   └── features/
│       └── auth/
│           ├── components/
│           │   ├── LoginForm.tsx
│           │   └── LoginForm.test.tsx   <-- Teste colocalizado ao lado do componente
│           └── utils/
│               ├── validateEmail.ts
│               └── validateEmail.test.ts
└── tests/                        <-- Pasta dedicada apenas para E2E
    └── e2e/
        └── checkout-flow.spec.ts <-- Playwright / Cypress
```

---

## 3. Diretrizes de Execução (Padrão AAA)

Tanto no Backend quanto no Frontend, a estrutura de cada bloco de teste deve seguir o padrão **AAA (Arrange, Act, Assert)**:

```typescript
it("should calculate discount correctly for VIP users", () => {
  // Arrange
  const user = { type: "VIP" };
  const cartTotal = 100;

  // Act
  const finalPrice = calculateDiscount(cartTotal, user);

  // Assert
  expect(finalPrice).toBe(80);
});
```

---

## 4. Filosofia de Mocks e Determinismo

* **Mocks Restritos:** Faça mock apenas de dependências de I/O externo (banco de dados em testes unitários, chamadas HTTP para APIs de terceiros, envio de e-mails, gateways de pagamento).
* **Backend:** Em testes de integração, prefira utilizar bancos de dados de teste (ex: PostgreSQL em Docker/Testcontainers) em vez de mockar o ORM.
* **Frontend:** Em testes de componentes, teste o comportamento visível e interações do usuário (`userEvent.click`), evitando inspecionar estados internos.
* **Testes Determinísticos:** Proibido utilizar `setTimeout` ou geradores de dados aleatórios sem *seed* fixa (`Math.random()`).