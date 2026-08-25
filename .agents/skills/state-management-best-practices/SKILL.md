---
name: state-management-best-practices
description: Use this skill when managing complex global or local state in React applications, particularly when working with Zustand, Redux Toolkit, or React Context.
---

# State Management Best Practices

Follow these rules to prevent prop-drilling, avoid unnecessary re-renders, and maintain clean state architecture.

## 1. Choose the Right Tool
- **Local State (`useState`, `useReducer`)**: For state confined to a single component (e.g., form inputs, toggle switches, local loading states).
- **Server State (TanStack Query / SWR)**: For fetching, caching, synchronizing, and updating server data. Do NOT put server data into global state stores like Redux or Zustand unless necessary.
- **Global UI State (Zustand / Redux Toolkit)**: For cross-component state (e.g., themes, user authentication status, complex multi-step wizards, shopping carts).

## 2. Zustand Architecture
- Keep stores small and modular. Create separate stores for different domains (e.g., `useAuthStore`, `useCartStore`) rather than one massive store.
- Only export custom hooks that select exactly the state needed to minimize re-renders.
  ```typescript
  // Good:
  const userName = useUserStore((state) => state.name);
  ```

## 3. Avoid Prop Drilling
- If you are passing a prop down through more than 3 levels of components that don't need it, refactor to use a global store or the Context API.

## 4. Immutability
- Never mutate state directly. Always return a new object/array.
- If using Redux Toolkit or Zustand with Immer, you can write "mutating" logic safely, but be aware of the underlying immutability requirement.

## Validation Step
Check for re-renders. If a component is subscribed to a store, will it re-render when an *unrelated* piece of state in that store changes? If yes, fix the selector.
