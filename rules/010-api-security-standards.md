# Regras de Segurança de API, Validação e Sanitização

## 1. Validação Estrita de Entrada (Input Schemas)
- **Validação Antecipada:** Nenhuma rota HTTP (REST ou GraphQL) pode processar payloads (`req.body`), parâmetros (`req.params`) ou query strings (`req.query`) sem validação prévia por schema (ex: Zod, Valibot, Yup).
- **Falhe Rápido (Fail Fast):** Se o payload violar o schema, a API deve rejeitar a requisição imediatamente com código de erro `422 Unprocessable Entity` ou `400 Bad Request`.

```typescript
// ✅ CORRETO: Validação de schema isolada antes de executar o controller
import { z } from "zod";

export const createUserSchema = z.object({
  body: z.object({
    email: z.string().email(),
    age: z.number().min(18),
  }),
});
```

---

## 2. Sanitização de Saída (Response DTOs & Serialization)

* **Proibido Retornar Entidades do Banco de Dados Brutas:** NUNCA retorne a resposta do ORM/banco diretamente para o cliente.
* **Uso Obrigatório de DTOs / Serializers:** Mapeie os dados explicitamente apenas para os campos que a UI precisa receber. Isso previne o vazamento de hashes de senhas, flags internas de administrador ou metadados sensíveis.

```typescript
// ❌ INCORRETO: Retorna o objeto do banco bruto (vazando hash de senha)
const user = await userRepository.findById(id);
return res.json(user);

// ✅ CORRETO: Mapeia apenas os dados públicos necessários
const user = await userRepository.findById(id);
return res.json({
  id: user.id,
  email: user.email,
  name: user.name,
});
```

---

## 3. Segurança Baseada em OWASP

* **Headers de Segurança:** Todas as aplicações devem configurar os headers HTTP recomendados pela OWASP (ex: Helmet.js para projetos Node).
* **CORS Estrito:** Ambientes de homologação e produção devem ter configurações de CORS com origens explicitamente declaradas. O uso de `Access-Control-Allow-Origin: *` em rotas privadas é proibido.
* **Proteção contra Rate-Limiting:** Rotas públicas de autenticação (`/login`, `/reset-password`) devem implementar limites de requisições por IP/Conta para prevenir ataques de força bruta.