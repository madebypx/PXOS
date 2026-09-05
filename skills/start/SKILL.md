---
name: start
description: "PXOS /start workflow: Open a work session, auto-resolve active branch and task spec, read core context files (.ai/AI_BASE.md, .ai/PROJECT_CONTEXT.md, SPRINT.md), and establish task scope."
---

# /start — Open a work session (Hybrid Single/Multi-Agent)

Read the core context files before doing anything:
- `.ai/AI_BASE.md`
- `.ai/PROJECT_CONTEXT.md`

Auto-resolve active task spec:
1. Run `git branch --show-current` to identify the current branch.
2. Check if a modular spec exists matching this branch in `.ai/specs/` (e.g. `.ai/specs/SPEC-<branch-suffix>.md` or `.ai/specs/SPEC-<branch-name>.md`).
3. If found, load it as the active task spec.
4. If not found, check `.ai/CURRENT_SPEC.md`.
5. If `SPRINT.md` exists at the project root (or inside `.internal/SPRINT.md` / `.ai/SPRINT.md`), read it to verify assigned goals and dependencies.

Report your findings:
- Active branch: `[branch-name]`
- Active spec: `[spec path]`
- Current workflow phase: `[Discover / Plan / Execute / Validate / Review]`

Then ask me one question:
"Is this session for a new feature or complex task — or a quick fix / small change?"

- **If new feature or complex task:**
  Check the state of the active spec.
  - If it is populated with a clear goal and acceptance criteria:
    Summarize your understanding of the task in 3–5 bullets and confirm you are ready to move to the Plan phase. State what decision or confirmation you need from me before proceeding.
  - If it is empty or only contains template placeholders:
    Recommend running `/spec` to define the task together before planning or executing anything.

- **If quick fix or small change:**
  Ask me to describe the change in one or two sentences.
  Confirm scope, identify affected files, and proceed directly to execution following the autonomy rules in `AI_BASE.md`.

Do not implement anything until you have a clear understanding of scope.
