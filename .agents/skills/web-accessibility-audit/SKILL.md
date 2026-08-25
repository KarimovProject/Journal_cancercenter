---
name: web-accessibility-audit
description: Use this skill when the user asks to review UI code, check for accessibility (a11y), improve SEO, or audit the frontend against best practices.
---

# Web Accessibility (A11y) & SEO Audit

When asked to audit frontend UI or HTML/templates, evaluate the code against these strict criteria:

## 1. Semantic HTML
- Ensure the page uses a logical heading structure (only one `<h1>`, followed sequentially by `<h2>`, `<h3>`).
- Replace generic `<div>` tags with semantic landmarks: `<nav>`, `<main>`, `<article>`, `<section>`, `<footer>`, `<aside>`.

## 2. ARIA & Screen Readers
- Interactive elements that aren't native (e.g., custom dropdowns, modals) must have appropriate `role`, `aria-expanded`, `aria-hidden`, and `aria-labelledby` attributes.
- All images `<img>` must have meaningful `alt` text. Decorative images should have `alt=""`.

## 3. Keyboard Navigation
- Every interactive element (buttons, links, inputs) MUST be reachable via the `Tab` key.
- Provide clear `:focus` or `:focus-visible` styles. Do not use `outline: none;` without a fallback visual indicator.

## 4. Color Contrast
- Check that text has sufficient contrast against its background (WCAG AA standard: at least 4.5:1 for normal text).

## 5. SEO Basics
- Ensure important meta tags (title, description, open graph) are present or can be dynamically injected.
- Links `<a>` must have descriptive text. Avoid "Click here" or "Read more".

## Validation Action
When providing the audit results to the user, present them as a checklist with severity levels (Critical, Warning, Optimization) and provide the exact code snippets to fix the issues.
