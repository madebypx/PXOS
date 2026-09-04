---
name: spec
description: "PXOS /spec workflow: Draft or refine a task specification in .ai/specs/SPEC-<branch>.md or .ai/CURRENT_SPEC.md with autonomous audit & research grounding."
---

# /spec — Draft a task spec (Modular or Central)

Help me write a task spec using the PXOS standard structure:

1. **Determine target file:**
   - If on a dedicated branch/worktree (e.g. `feat/auth-oauth`), create or update `.ai/specs/SPEC-<branch-suffix>.md` based on `.ai/specs/TEMPLATE_SPEC.md`.
   - If on `main` or in a single-spec setup, update `.ai/CURRENT_SPEC.md`.

2. **Autonomous Grounding (Macro Context):**
   - Autonomously inspect `.ai/audits/` (or `docs/audits/`) for open findings touching the affected files.
   - Autonomously check `.ai/research/INDEX.md` (or `docs/research/`) for active benchmarks or architectural invariants.
   - Auto-populate the `Strategic & Audit Alignment` block with explicit IDs or "Clean — No active audit blockers touching this scope".

3. **Fill the following structure:**
   - Goal
   - User value
   - Strategic & Audit Alignment (auto-filled by agent)
   - Scope (in / out)
   - Constraints
   - Existing patterns relevant to the task
   - Proposed change
   - User flow / Technical flow
   - Edge cases
   - Acceptance criteria
   - Validation plan
   - Risks & Cross-Task Dependencies

Ask me questions if anything is unclear before filling it in.

After the spec is complete, explicitly state:
- That the spec file is ready
- That the recommended next step is to run `/plan`
