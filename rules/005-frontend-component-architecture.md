# Regras de Arquitetura e Organização de Componentes Frontend

## 1. Arquitetura Modular Baseada em Funcionalidades (Feature-Based)
Evite agrupar todos os componentes do sistema em uma única pasta global. Organize o projeto por **domínios de negócio/funcionalidades (features)**.

### Estrutura de Diretórios Recomendada:
```text
src/
├── assets/                 <-- Imagens, fontes, ícones globais
├── components/             <-- Componentes genéricos e reutilizáveis (UI Primitives)
│   └── ui/                 <-- Buttons, Inputs, Modals, Badges
├── features/               <-- Módulos isolados por regra de negócio
│   ├── auth/
│   │   ├── components/     <-- Componentes exclusivos de Auth (ex: LoginForm)
│   │   ├── hooks/          <-- Hooks / Composables / Serviços de Auth
│   │   ├── types/          <-- Tipos TypeScript exclusivos de Auth
│   │   └── index.ts        <-- Exportações públicas do módulo
│   └── billing/
├── services/               <-- Clientes de API, SDKs e utilitários globais
└── utils/                  <-- Funções puras utilitárias (ex: formatters, cn)
```

---

## 2. Princípio da Responsabilidade Única (SRP) e Limite de Tamanho

* **Tamanho Máximo do Componente:** Um arquivo de componente **não deve ultrapassar ~200 a 400 linhas de código**. Se for maior, quebre-o em subcomponentes internos ou extraia a lógica de estado.
* **Separação entre Apresentação e Lógica:**
    * O componente deve focar apenas na renderização da interface e eventos de usuário.
    * Lógicas complexas (chamadas de API, transformações de dados pesadas, formulários) devem ser abstraídas em **Custom Hooks** (React/Next.js), **Composables** (Vue/Svelte) ou **Services** (Angular).



```tsx
// ❌ INCORRETO: Lógica de busca, estado e UI misturados em 300 linhas
export function UserProfile() {
  const [data, setData] = useState(null);
  useEffect(() => { fetch('/api/user').then(...) }, []);
  // ... 200 linhas de manipulação ...
  return <div>...</div>;
}

// ✅ CORRETO: Lógica encapsulada em um hook, componente focado em UI
export function UserProfile({ userId }: UserProfileProps) {
  const { user, isLoading, error } = useUserProfile(userId);

  if (isLoading) return <UserProfileSkeleton/>;
  if (error) return <ErrorMessage message="{error.message}"/>;

  return (
    <div className="flex flex-col gap-4">
      <Avatar alt="{user.name}" src="{user.avatarUrl}"/>
      <UserInfo email="{user.email}" name="{user.name}"/>
    </div>
  );
}
```

---

## 3. Nomenclatura e Convenções

### Nomes de Componentes e Arquivos

* **Nome do Componente:** Sempre em **PascalCase** (ex: `PaymentCard`, `InvoiceTable`).
* **Nomes de Arquivos:**
    * **React / Vue:** PascalCase alinhado ao nome do componente (ex: `PaymentCard.tsx`, `PaymentCard.vue`).
    * **Angular / Svelte:** Siga a convenção idiomática do framework (ex: `payment-card.component.ts`, `PaymentCard.svelte`).



### Convenção de Props e Eventos

* **Props de Dados:** Use nomes no formato `camelCase` claros e descritivos (ex: `isSubmitting`, `totalAmount`).
* **Handled Events:** Prefix os manipuladores de eventos internos com `handle` e as props de callback com `on`.

```tsx
// ✅ CORRETO: Prop de callback 'onSuccess' e handler interno 'handleSubmit'
export function LoginForm({ onSuccess }: LoginFormProps) {
  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    await login();
    onSuccess();
  };

  return <form onSubmit={handleSubmit}>...</form>;
}
```

---

## 4. Tipagem Estrita de Props e Eventos (TypeScript)

Todo componente deve definir explicitamente a interface/tipo das suas propriedades.

* O nome da interface deve seguir o padrão `<ComponentName>Props`.
* Torne propriedades opcionais explícitas (`?`) e forneça valores padrão (*default props*).

```typescript
// ✅ CORRETO: Interface clara e tipada
export interface ButtonProps {
  variant?: "primary" | "secondary" | "danger";
  size?: "sm" | "md" | "lg";
  disabled?: boolean;
  onClick: () => void;
  children: React.ReactNode;
}
```

---

## 5. Colocalização e Gerenciamento de Estado

* **Colocalização de Estado (Local-First):** Mantenha o estado o mais próximo possível de onde ele é utilizado. Não jogue estados puramente visuais (ex: modal aberto/fechado, tab ativa) em gerenciadores globais (Redux, Zustand, Pinia, NGRX).
* **Evite Prop Drilling:** Se uma propriedade precisa ser passada por mais de 2 ou 3 níveis de componentes intermediários, utilize **Context API**, **Inject/Provide** ou refatore a composição dos componentes.

---

## 6. Exportações e Barrels (`index.ts`)

Para manter as importações limpas, cada diretório de funcionalidade/componente deve usar um arquivo `index.ts` como porta de entrada:

```typescript
// features/auth/index.ts
export { LoginForm } from "./components/LoginForm";
export { useAuth } from "./hooks/useAuth";
export type { User } from "./types/user.types";
```

Permite importar de forma limpa:

```typescript
import { LoginForm, useAuth } from "@/features/auth";
```

---

## 7. Arquitetura de Temas e Tokens Semânticos (Multi-Theme)

### Princípio do Uso de Tokens Semânticos
NUNCA utilize cores absolutas ou hardcoded diretamente nos componentes (ex: `bg-white`, `bg-black`, `text-slate-800`). Todo componente deve consumir **tokens semânticos** definidos nas variáveis globais do CSS/Tailwind.

```tsx
// ❌ INCORRETO: Engessa o componente e quebra a troca de temas
<div className="bg-white text-black dark:bg-slate-900 dark:text-white">

// ✅ CORRETO: O componente reage automaticamente a qualquer tema ativo
<div className="bg-background text-foreground border-border">
```

### Estrutura de Variáveis CSS Padrão (`globals.css` / `theme.css`)

O sistema de temas deve ser estruturado utilizando variáveis CSS (prefira o espaço de cor **OKLCH** ou **HSL** para transição suave de cores):

```css
@layer base {
  /* Tema Claro (Default) */
  :root, [data-theme="light"] {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;
    --card: 0 0% 100%;
    --primary: 222.2 47.4% 11.2%;
    --primary-foreground: 210 40% 98%;
    --muted: 210 40% 96.1%;
    --muted-foreground: 215.4 16.3% 46.9%;
    --border: 214.3 31.8% 91.4%;
  }

  /* Tema Escuro */
  .dark, [data-theme="dark"] {
    --background: 222.2 84% 4.9%;
    --foreground: 210 40% 98%;
    --card: 222.2 84% 4.9%;
    --primary: 210 40% 98%;
    --primary-foreground: 222.2 47.4% 11.2%;
    --muted: 217.2 32.6% 17.5%;
    --muted-foreground: 215 20.2% 65.1%;
    --border: 217.2 32.6% 17.5%;
  }

  /* Exemplo de Tema Customizado (ex: Brand/Nord/Catppuccin) */
  [data-theme="nord"] {
    --background: 220 16% 22%;
    --foreground: 218 27% 92%;
    --primary: 193 43% 67%;
    /* ... demais tokens ... */
  }
}

```

### Provedor de Tema e Preferência do Usuário

* **Suporte a `system`:** O gerenciador de temas da aplicação deve respeitar por padrão a preferência do sistema operacional do usuário (`prefers-color-scheme`).
* **Persistência:** A escolha do tema pelo usuário deve ser salva em `localStorage` ou `cookies` (no caso de renderização SSR com Next.js/Nuxt para evitar efeito de *flash* na página).
* **Abstração:** Utilize bibliotecas consagradas para gerenciamento do estado do tema (ex: `next-themes` para Next.js/React, ou provedores nativos equivalente no Vue/Svelte).