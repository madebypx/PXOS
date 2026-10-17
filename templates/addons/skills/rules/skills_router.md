# PXOS Cognitive Skills Router — Just-in-Time Rules
<!-- pxos:version 2.8.0 -->

This rule governs intelligent agentic skill discovery and execution across the workspace.
It enforces Just-in-Time (JIT) skill activation to prevent context pollution, token exhaustion, and cognitive drift.

---

## 1. Decision Matrix: When to Trigger Skills

| Scenario / Task Intent | Recommended Skill | Reference Path | Skill Scope & Objective |
|---|---|---|---|
| **New Landing Page / Web Hero (from scratch)** | `design-taste-frontend` | `skills/design-taste-frontend/SKILL.md` | Editorial art direction, anti-slop visual hierarchy, balanced tracking. |
| **Brand-Inspired Design Tokens (Linear, Stripe, etc.)** | `awesome-design-md` | `skills/awesome-design-md/SKILL.md` | 84 real design systems, color tokens, dark surfaces, and borders. |
| **Improve / Elevate Existing UI without Breaking Logic** | `redesign-existing-projects` | `skills/redesign-existing-projects/SKILL.md` | Diagnose generic AI patterns and elevate visual fidelity cleanly. |
| **Accessibility, Contrast, and Web Guidelines Audit** | `web-design-guidelines` | `skills/web-design-guidelines/SKILL.md` | Vercel Web Interface Guidelines, WCAG, contrast, touch targets. |
| **Mobile App Development (Expo / React Native)** | `expo-overview`, `expo-router` | `skills/expo-*/SKILL.md` | Apple HIG / Material 3, design tokens, canonical navigation. |
| **Browser Automation, E2E Testing, Snapshots** | `playwright-cli` | `skills/playwright-cli/SKILL.md` | Token-efficient CLI navigation, network inspection, accessibility refs. |
| **Google Stitch Specifications (`DESIGN.md`)** | `stitch-design-taste` | `skills/stitch-design-taste/SKILL.md` | Semantic specifications in Markdown understood by Google Stitch. |
| **Brand Kit, Visual Identity, Asset Boards** | `brandkit` | `skills/brandkit/SKILL.md` | Premium brand guidelines, conceptual mockups, and logo concepts. |
| **Multi-Agent Spatial Swarm Orchestration** | `maestri*` | `skills/maestri*/SKILL.md` | Terminal communication, floor isolation, and canvas note syncing. |
| **PXOS Lifecycle Governance** | `start`, `spec`, `plan`, `review`, `compact` | `skills/<cmd>/SKILL.md` | Deterministic 6-phase engineering lifecycle workflows. |

---

## 2. Golden Rules of Execution (Token Economics & Safe Execution)

1. **Just-in-Time (JIT) Activation:** Read `SKILL.md` ONLY when the current task directly enters the corresponding domain. Never eagerly load skill definitions into context during generic tasks.
2. **Zero Overhead for Trivial Work:** For localized bug fixes, variable renames, small styling tweaks, or unit test runs, implement directly without reading skills.
3. **No Conflicting Philosophies:** When implementing a design style, adhere strictly to its tokens without mixing contradictory aesthetics in the same view.
4. **Precedence of Local Repository Context:** If the workspace contains a local `.ai/DESIGN.md`, `.ai/PROJECT_CONTEXT.md`, or `.ai/DOMAIN_RULES.md`, local definitions ALWAYS override any external skill guidance.
