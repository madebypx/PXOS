# Cognitive Skills Router & Just-in-Time Matrix
<!-- pxos:skills-version 1.0.0 -->

This document establishes the project-level cognitive router for AI agents working in this workspace.
It maps project tasks and developer intentions to specialized agentic skills (`skills/*/SKILL.md`), enforcing Just-in-Time (JIT) activation and eliminating token waste.

---

## 1. Just-in-Time (JIT) Activation Protocol

1. **JIT Loading Only:** Agents must NOT read heavy `SKILL.md` instruction files proactively during initial prompt load. Read them only when the task explicitly enters the designated domain.
2. **Zero Overhead for Trivial Edits:** For localized bug fixes, variable renames, single-line CSS adjustments, or small tests, execute directly using native editing tools without loading skills.
3. **Local Precedence:** If the repository contains a local `.ai/DESIGN.md` or `.ai/DOMAIN_RULES.md`, local project rules ALWAYS take strict precedence over any external or global skill guidelines.
4. **Coherence & Non-Contradiction:** Never combine opposing architectural or aesthetic philosophies in the same component or screen.

---

## 2. Core Intent & Decision Matrix

| Task Scenario / Intent | Recommended Skill | Path / Location | Deliverables & Scope |
|---|---|---|---|
| **Zero-to-One UI / Web Landing Pages** | `design-taste-frontend` | `skills/design-taste-frontend/SKILL.md` | Editorial art direction, asymmetric layouts, balanced typography, visual inspection loops. |
| **Brand-Inspired Design Systems** | `awesome-design-md` | `skills/awesome-design-md/SKILL.md` | Production-ready design tokens, dark surfaces, curated color palettes, component specifications. |
| **UI Polish & AI Slop Elimination** | `redesign-existing-projects` | `skills/redesign-existing-projects/SKILL.md` | Elevate generic AI aesthetics while preserving 100% of existing business logic and code structure. |
| **Accessibility & Web Guidelines Audit** | `web-design-guidelines` | `skills/web-design-guidelines/SKILL.md` | WCAG compliance, contrast checks, keyboard navigation, touch targets, and semantics. |
| **Mobile Architecture (React Native / Expo)** | `expo-overview`, `expo-router` | `skills/expo-*/SKILL.md` | Apple HIG / Material 3 compliance, native routing, native modules, and mobile performance. |
| **E2E Browser Automation & Testing** | `playwright-cli` | `skills/playwright-cli/SKILL.md` | Token-efficient CLI browser automation, accessibility snapshots, and deterministic testing. |
| **Brand Identity & Design Kits** | `brandkit` | `skills/brandkit/SKILL.md` | Brand guidelines, high-fidelity mockups, logo concepts, and identity boards. |
| **Google Stitch UI Specifications** | `stitch-design-taste` | `skills/stitch-design-taste/SKILL.md` | Semantic UI specifications and markdown artifacts optimized for Google Stitch. |
| **Spatial Canvas & Swarm Orchestration** | `maestri*` | `skills/maestri*/SKILL.md` | Multi-agent collaboration, canvas notes synchronization, floor and terminal management. |
| **PXOS Governance Lifecycle** | `start`, `spec`, `plan`, `review`, `compact` | `skills/<cmd>/SKILL.md` | Session opening, specification drafting, structured planning, code review, and compact context. |

---

## 3. Project-Specific Extensions

Teams can register project-specific skills below (stored in `.agents/skills/` or `.ai/skills/`):

| Local Task / Subsystem | Local Skill Path | Description & Trigger Criteria |
|---|---|---|
| *None yet* | `.agents/skills/<name>/SKILL.md` | *Register repository-specific workflows here* |
