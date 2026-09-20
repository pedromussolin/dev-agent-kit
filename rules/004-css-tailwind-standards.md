# Regras de Estilização: Tailwind CSS e SCSS

## 1. Coexistência entre Tailwind CSS e SCSS
O projeto utiliza **Tailwind CSS** para estilização rápida baseada em utilitários e **SCSS** para animações complexas, estruturas de layout avançadas, mixins ou componentes com CSS encapsulado (CSS Modules).

### Guia de Decisão:
- **Use Tailwind Utility Classes:** Para a grande maioria dos layouts, espaçamentos, tipografia, cores e estados simples (`hover`, `focus`, `active`).
- **Use SCSS (`.scss` / `.module.scss`):** Para seletores complexos, animações (`@keyframes`), regras com nesting profundo (`& > div`), ou quando a lista de classes do Tailwind comprometer a legibilidade do HTML/JSX.

---

## 2. Design Responsivo Multi-Dispositivo
Não há restrição ou prioridade exclusiva para dispositivos móveis. O sistema deve ser desenhado para funcionar com excelência em todas as resoluções (Mobile, Tablet, Desktop e Ultra-wide).

### Mecânica de Breakpoints do Tailwind:
Como os breakpoints do Tailwind usam `min-width`, a classe base define o comportamento geral e os modificadores ajustam para ecrãs maiores.

```tsx
// ✅ Estrutura responsiva clara para Desktop e Mobile
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
  {/* 1 coluna em mobile, 2 em tablets (md), 4 em desktop (lg) */}
</div>
```

---

## 3. Uso Correto do SCSS

### Nesting e Seletores (`&`)

Aproveite o encadeamento do SCSS, mas limite o nesting a no máximo **3 níveis de profundidade** para evitar CSS demasiado específico e difícil de sobrescrever.

```scss
/* ✅ CORRETO: Nesting limpo e legível */
.card-container {
  background-color: var(--color-bg-surface);
  padding: 1.5rem;

  &:hover {
    border-color: var(--color-primary);
  }

  .card-title {
    font-size: 1.25rem;
    font-weight: 600;
  }
}

```

### Variáveis e Mixins SCSS

* Mantenha as variáveis globais de cor e tema centralizadas no Tailwind (`tailwind.config.js` ou variáveis CSS nativas em `globals.scss`).
* Use Mixins no SCSS apenas para reutilizar blocos complexos de regras (ex: centralização flexbox, scrollbars personalizadas, animações).

```scss
// styles/abstracts/_mixins.scss
@mixin flex-center {
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-overlay {
  @include flex-center;
  position: fixed;
  inset: 0;
}
```

---

## 4. Integração do SCSS com Tailwind (`@apply`)

Quando utilizar ficheiros SCSS, pode integrar utilitários do Tailwind através da diretiva `@apply`, mantendo o código limpo.

```scss
// styles/components/sidebar.module.scss
.sidebar {
  @apply fixed top-0 left-0 h-full w-64 bg-slate-900 text-white transition-transform;

  // Personalização via SCSS para seletores complexos
  &__item {
    @apply flex items-center gap-3 px-4 py-2 hover:bg-slate-800;

    &--active {
      @apply bg-blue-600 font-bold;
    }
  }
}
```

---

## 5. Manipulação Dinâmica de Classes com `cn()`

Sempre que precisar de alternar classes do Tailwind dinamicamente no código TypeScript/React, utilize o helper `cn()` (`clsx` + `tailwind-merge`).

```tsx
// ❌ INCORRETO: Interpolação direta com risco de conflito de CSS
<button className={`btn-base ${isActive ? 'bg-blue-500' : 'bg-gray-500'} ${className}`}>

// ✅ CORRETO: Fusão segura de classes Tailwind e SCSS
import { cn } from "@/utils/cn";
import styles from "./button.module.scss";

export function Button({ isActive, className, children }: ButtonProps) {
  return (
    <button
      className={cn(
        styles.customButton,
        "px-4 py-2 rounded-lg font-medium transition-all",
        isActive ? "bg-blue-600 text-white" : "bg-gray-200 text-gray-700",
        className
      )}
    >
      {children}
    </button>
  );
}