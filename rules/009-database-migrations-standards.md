# Regras de Banco de Dados, Migrations e Consulta ORM

## 1. Nomenclatura de Esquemas e Tabelas
- **Tabelas e Colunas:** DEVEM ser nomeadas estritamente em `snake_case` (ex: `user_profiles`, `created_at`, `order_items`).
- **Chaves Estrangeiras (Foreign Keys):** Devem seguir a convenção `<tabela_singular>_id` (ex: `user_id`, `product_id`).

---

## 2. Migrations Seguras e Ciclo de Vida (Expand-Contract Pattern)
- **Zero Breaking Changes em Produção:** NUNCA remova ou renomeie uma coluna diretamente no banco de dados em um único deploy.
- **Padrão Expand-Contract para alteração de colunas:**
  1. *Passo 1 (Expand):* Adicione a nova coluna sem deletar a antiga. Atualize a aplicação para escrever em ambas.
  2. *Passo 2 (Backfill):* Migre os dados existentes da coluna antiga para a nova.
  3. *Passo 3 (Contract):* Atualize a aplicação para ler apenas da nova coluna e, na migration seguinte, remova a antiga.
- **Tabelas de Produção:** Toda alteração de schema deve ser executada através de arquivos de migration versionados. Proibido executar scripts DDL manuais no ambiente de produção.

---

## 3. Desempenho e Indexação
- **Indexação Obrigatória:**
  - Todas as colunas de chave estrangeira (`foreign_keys`) DEVEM possuir índices criados explicita ou implicitamente.
  - Colunas utilizadas frequentemente em ordenação ou filtros de pesquisa (`WHERE`, `ORDER BY`, `GROUP BY`) devem ser indexadas.
- **Consultas Paginadas:** Todas as consultas que retornam listas públicas DEVEM obrigatoriamente impor paginação via limit/offset ou baseada em cursor (cursor-based).

---

## 4. Prevenção de Problemas de Performance em ORMs (N+1 Queries)
- **Proibido Consultas em Loops (N+1):** É proibido disparar queries dentro de laços de repetição.
- **Eager Loading / Joins Explicitos:** Utilize abordagens de carregamento ansioso (`include`, `join`, `select`) para trazer relacionamentos necessários em uma única requisição ao banco.

```typescript
// ❌ INCORRETO: Dispara N queries dentro do loop (N+1)
const users = await prisma.user.findMany();
for (const user of users) {
  const posts = await prisma.post.findMany({ where: { userId: user.id } });
}

// ✅ CORRETO: Traz os relacionamentos em uma única query otimizada
const usersWithPosts = await prisma.user.findMany({
  include: { posts: true },
});
```