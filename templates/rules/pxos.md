# PXOS — Operating Rules
<!-- pxos:version 2.4.0 -->

This project adheres to the PXOS framework (v2.4).

1. **Read Core Files & Grounding**:
   - Always check `.ai/AI_BASE.md` and `.ai/PROJECT_CONTEXT.md` before executing tasks.
   - In Discover, inspect `.ai/audits/` and `.ai/research/INDEX.md` if present for active constraints and invariants.
   - If `PROJECT_CONTEXT.md` contains a `Critical invariants` section, cross-reference it during Plan for any task that modifies listed entities.
   - Identify active branch (`git branch --show-current`). If `.ai/specs/SPEC-<branch>.md` exists, load it as the active spec; otherwise fall back to `.ai/CURRENT_SPEC.md`.

2. **Follow Default Workflow**:
   - Discover → Plan → Execute → Validate → Review → Compact Context.
   - During `/plan`, cite resolved audit blockers and evaluate Single-Task vs. parallel Multi-Agent Worktrees.
   - During `/review`, check code correctness, security, and (if touching UI) Nielsen UX heuristics.
   - During `/compact`, append durable decisions to `.ai/DECISION_LOG.md` and update `SPRINT.md`.

3. **Multi-Agent & Environment Isolation**:
   - In parallel worktrees, never edit files outside your assigned directory or modify specs belonging to other agents.
   - `PROJECT_CONTEXT.md` is strictly read-only on feature branches.
   - `DECISION_LOG.md` is append-only (concatenate on merge conflict).

4. **Respect Autonomy Levels**:
   - Low risk: execute directly (naming, small bug fixes, readability).
   - Medium risk: provide reasoning before changing internal flows or abstractions.
   - High risk: require explicit human approval (architecture, dependencies, schemas).

5. **Context Hygiene & Git Standards**:
   - Load only relevant files, preserve conciseness, and run `/compact` at the end of sessions.
   - Stage changed files, commit using English Conventional Commits (e.g. `feat: ...`, `fix: ...`), and push cleanly.
