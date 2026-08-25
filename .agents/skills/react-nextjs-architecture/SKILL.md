---
name: react-nextjs-architecture
description: Use this skill when generating, reviewing, or refactoring React and Next.js (App Router) components, ensuring adherence to modern architecture and Server Components best practices.
---

# React & Next.js Architecture Runbook

When writing or reviewing React/Next.js code, strictly follow these architectural standards:

## 1. Server vs. Client Components
- Default to React Server Components (RSC) by omitting `"use client"`.
- Use `"use client"` only at the leaf nodes of the component tree, specifically where state (`useState`), effects (`useEffect`), or browser APIs (like `window`) are strictly required.
- Do not pass non-serializable data (like functions) from Server to Client components as props.

## 2. Next.js App Router Conventions
- Place data fetching logic directly inside Server Components (using async/await) instead of using `useEffect`.
- Utilize Next.js specific files correctly: `layout.tsx`, `page.tsx`, `loading.tsx`, `error.tsx`, and `not-found.tsx`.
- Use the `next/image` component for images and `next/link` for internal routing.

## 3. Clean Code & Component Structure
- Keep components small and focused on a single responsibility.
- Extract complex business logic into custom hooks.
- For type safety, always define TypeScript interfaces or types for component props. Do not use `any`.

## 4. Server Actions
- Use Server Actions (functions marked with `"use server"`) for form submissions and data mutations directly from the UI without needing API routes.

## Validation Step
Before outputting code, check: "Is there an unnecessary `use client` directive here?" and "Can this data be fetched on the server instead?"


# Next.js (Tailwind, TypeScript)

# Next.js with Tailwind CSS and TypeScript

## Overview
This document outlines the best practices and rules for developing Next.js applications using Tailwind CSS and TypeScript. The goal is to ensure that the codebase is maintainable, scalable, and adheres to modern web development standards.

## Key Features
- **Next.js**: Utilized for server-side rendering and static site generation.
- **Tailwind CSS**: Used for utility-first CSS styling, ensuring responsive and customizable designs.
- **TypeScript**: Enhances code quality and developer productivity through static typing.

## Coding Standards
- **Functional Components**: Prefer functional components over class components.
- **TypeScript**: Use TypeScript for all components and utilities to ensure type safety.
- **Tailwind CSS**: Apply Tailwind CSS classes directly within JSX for styling.

## Preferred Libraries
- **Next.js**: For routing and server-side rendering.
- **Tailwind CSS**: For styling components.
- **TypeScript**: For type checking and enhancing developer experience.

## File Structure
- **components/**: Reusable UI components.
- **pages/**: Next.js pages.
- **styles/**: Tailwind CSS configuration and global styles.
- **types/**: TypeScript type definitions.

## Performance Optimization
- **React.memo**: Use for optimizing functional components.
- **Lazy Loading**: Implement for components and routes to improve load times.
- **useEffect Optimization**: Ensure dependencies are correctly managed to prevent unnecessary re-renders.

## Testing Requirements
- **Jest and React Testing Library**: For unit and integration testing.
- **Test Coverage**: Aim for at least 80% test coverage.
- **Snapshot Testing**: Use for UI components to detect unintended changes.

## Documentation
- **JSDoc**: Use for documenting functions and components.
- **README.md**: Include in each main directory with both English and Chinese versions.

## Error Handling
- **try/catch**: Use for handling asynchronous operations.
- **Error Boundaries**: Implement global error boundaries to catch runtime errors.

## Conclusion
By following these guidelines, developers can ensure that their Next.js applications are robust, maintainable, and scalable. Tailwind CSS and TypeScript further enhance the development experience by providing powerful styling and type safety features.
