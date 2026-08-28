# PXOS — Operating Rules
<!-- pxos:version 2.0.0 -->

This project adheres to the PXOS framework (v2.0).

1. **Read Core Files & Auto-Resolve Spec First**:
   - Always check `.ai/AI_BASE.md` and `.ai/PROJECT_CONTEXT.md` before executing tasks.
   - Identify active branch (`git branch --show-current`). If `.ai/specs/SPEC-<branch>.md` exists, load it as the active spec; otherwise fall back to `.ai/CURRENT_SPEC.md`.

2. **Follow Default Workflow**:
   - Discover → Plan → Execute → Validate → Review → Compact Context.
   - During `/plan`, evaluate if tasks should run as Single-Task or parallel Multi-Agent Worktrees.

3. **Multi-Agent & Environment Isolation**:
   - In parallel worktrees, never edit files outside your assigned directory or modify specs belonging to other agents.
   - `PROJECT_CONTEXT.md` is strictly read-only on feature branches.

4. **Respect Autonomy Levels**:
   - Low risk: execute directly (naming, small bug fixes, readability).
   - Medium risk: provide reasoning before changing internal flows or abstractions.
   - High risk: require explicit human approval (architecture, dependencies, schemas).

5. **Context Hygiene & Git Standards**:
   - Load only relevant files, preserve conciseness, and run `/compact` at the end of sessions.
   - Stage changed files, commit using English Conventional Commits (e.g. `feat: ...`, `fix: ...`), and push directly to GitHub.
