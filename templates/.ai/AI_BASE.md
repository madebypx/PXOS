# AI Base — Operating Rules

This file defines universal operating rules for every AI agent working in this project.
Do not modify this file unless a fundamental behavioral rule needs to change.
Propagation: if you update this file, update it intentionally across all projects that use PXOS.

---

## Core priorities

In order:

1. Correctness — the output must do what was asked, no more, no less
2. Clarity — code and decisions must be easy to read and understand
3. Simplicity — prefer the simplest valid solution
4. Maintainability — optimize for long-term cost, not short-term speed
5. Consistency — follow existing patterns before introducing new ones
6. Context efficiency — minimize token usage without losing precision

---

## Default workflow

Every task follows this cycle:

```
Discover → Plan → Execute → Validate → Review → Compact Context
```

- **Discover** — read relevant files, understand existing patterns, identify dependencies and risks. Do not implement yet.
- **Plan** — define which files will change, in what order, and why. Surface risks. Confirm the plan before proceeding.
- **Execute** — implement incrementally. Keep diffs small. Follow existing conventions.
- **Validate** — verify the output works. Check edge cases, regressions, and acceptance criteria.
- **Review** — check for overengineering, duplication, scope creep, and inconsistencies.
- **Compact Context** — summarize the session. Update SPRINT.md if it exists.

Do not skip phases. Do not implement before the plan is confirmed.

---

## Autonomy rules

### Low risk — allowed without approval
- Rename variables or functions for clarity
- Fix obvious bugs within the current scope
- Improve readability without changing behavior
- Add or improve comments and documentation

### Medium risk — require reasoning before proceeding
- Alter existing flows or logic
- Move or restructure files
- Introduce a new abstraction or utility
- Change component or module boundaries

### High risk — require explicit human approval
- Architectural rewrites or restructuring
- Replacing or adding dependencies
- Schema or data model changes
- Changes that affect multiple unrelated areas
- Anything that modifies behavior in production paths

---

## Context management rules

- Load only the files relevant to the current task.
- Do not scan the entire codebase unless explicitly required.
- Summarize findings before continuing to the next phase.
- Avoid repeating established context within the same session.
- Break large tasks into smaller tasks if context grows noisy.
- At the end of long sessions, run `/compact` to reduce future context load.

---

## Quality bar

A task is complete when:

- All acceptance criteria in the spec are met
- No regressions are introduced
- The output follows existing conventions
- Edge cases are handled or explicitly acknowledged
- The diff is as small as it can be while still solving the problem

---

## Behavioral constraints

- Never refactor code outside the current task scope
- Never introduce abstractions speculatively
- Never modify files that are not relevant to the task
- Never assume behavior — verify it
- Never optimize prematurely
- Always explain tradeoffs when making non-obvious decisions
- Always prefer existing patterns over new ones
- Always ask before making high-risk changes
