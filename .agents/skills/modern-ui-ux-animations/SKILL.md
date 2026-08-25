---
name: modern-ui-ux-animations
description: Use this skill when the user asks to build or improve the visual design of UI components, add micro-interactions, or implement Tailwind CSS / Shadcn / Framer Motion styling.
---

# Modern UI/UX and Micro-animations

When building user interfaces, prioritize premium aesthetics, responsive design, and smooth interactions.

## 1. Tailwind CSS Best Practices
- Use Tailwind CSS utility classes for styling. Avoid writing custom CSS unless absolutely necessary.
- Group related classes together logically (e.g., layout, spacing, typography, colors, effects).
- Use `clsx` or `tailwind-merge` when combining dynamic class names, especially when creating reusable components (like Shadcn UI does).

## 2. Micro-Interactions & Hover Effects
- Add subtle, meaningful hover states to all interactive elements (buttons, links, cards). Examples: slight scaling (`hover:scale-[1.02]`), background color shifts, or box-shadow changes.
- Ensure all transitions are smooth by applying `transition-all duration-200 ease-in-out` (or similar appropriate timing functions).

## 3. Framer Motion Integration
- When building complex React animations, use Framer Motion.
- Use `layoutId` for smooth transitions of elements between different states or pages.
- Add staggered entrance animations to lists using the `variants` prop.
- Example for a simple fade-in: `<motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} />`

## 4. Dark Mode Support
- Always consider Dark Mode. Implement colors using Tailwind's `dark:` modifier (e.g., `bg-white dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100`).

## Validation Step
Does the UI feel "alive"? If a user hovers or clicks, is there visual feedback? Is the layout fully responsive on mobile screens (`sm:`, `md:`, `lg:` breakpoints)?
