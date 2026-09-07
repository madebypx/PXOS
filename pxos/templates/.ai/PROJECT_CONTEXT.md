# Project Context

This file contains durable, project-specific facts.
Update it when product priorities, stack, or conventions change in a lasting way.
This is not a place for session notes, temporary plans, or task details.

---

## Product

**Name:**
[Project name]

**Summary:**
[One or two sentences describing what the product does and for whom.]

**Target user:**
[Who uses this product and in what context.]

**Core value:**
[The single most important thing this product delivers to users.]

---

## Product priorities

In order:

1. [Priority 1]
2. [Priority 2]
3. [Priority 3]

**Anti-priorities — explicitly avoid:**
- [Thing to avoid]
- [Thing to avoid]

---

## Technical stack

**Frontend:** [e.g. Next.js 14, TypeScript, Tailwind CSS]
**Backend:** [e.g. Node.js, Fastify, Prisma]
**Database:** [e.g. PostgreSQL]
**Auth:** [e.g. Clerk]
**Hosting:** [e.g. Vercel, Railway]
**Other:** [Any other relevant tools or services]

---

## Architecture

**Style:** [e.g. modular monolith, feature-based folders, layered architecture]

**Key patterns:**
- [Pattern or convention the AI should follow]
- [Pattern or convention the AI should follow]

**Avoid:**
- [Architectural anti-pattern specific to this project]

---

## Conventions

**Naming:**
- [e.g. Components: PascalCase, files: kebab-case]

**File structure:**
- [e.g. Each feature lives in /features/[name] with its own components, hooks, and types]

**State management:**
- [e.g. Local state with useState, global with Zustand]

**Styling:**
- [e.g. Tailwind utility classes, no inline styles, design tokens in tailwind.config]

**API:**
- [e.g. REST, route handlers in /app/api, always validate with Zod]

---

## Known constraints and risks

- [Constraint or technical debt the AI should be aware of]
- [Constraint or technical debt the AI should be aware of]

---

## Macro Context & Paths (Optional)

**Research directory:** `.ai/research/` (or `docs/research/`)
**Audits directory:** `.ai/audits/` (or `docs/audits/`)
**Design / Tokens:** [e.g. `docs/DESIGN.md` or `.ai/research/DESIGN.md`]

---

## Critical invariants (optional)

Hard constraints that must never be violated by any agent. Use short IDs for traceability.
Leave this section empty or remove it if the project has no critical invariants.

<!-- Example:
- **INV-001:** Quarantine period is always >= 120 days. Never hardcode shorter values.
- **INV-002:** Assignment IDs must be deterministic: `prefix_${source}_${sourceId}`.
- **INV-003:** Every data mutation must propagate to all persistence nodes (DB + Bridge + Cache).
-->
