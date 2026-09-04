---
name: review
description: "PXOS /review workflow: Review what was just implemented by checking the branch diff against base for overengineering, bugs, consistency, and UX heuristics."
---

# /review — Review what was just implemented

Review what was just implemented by checking the branch diff (e.g. against main/origin):
- Overengineering or unnecessary complexity
- Duplicate logic or conflicts with existing patterns
- Accidental scope growth (modifying files outside the task scope)
- Unauthorized edits to shared files (e.g. `PROJECT_CONTEXT.md`)
- Weak naming or missing error boundaries
- Hidden side effects or security risks
- Inconsistencies with existing patterns

**UX & Interaction Heuristics (If the diff modifies UI, styles, or frontend interactions):**
- *Status visibility:* Are loading states, transitions, and system feedback clear and responsive?
- *Error prevention:* Are destructive actions guarded with confirmation? Are validation errors clear?
- *Cognitive friction:* Is the user flow direct and intuitive, minimizing unnecessary clicks or confusion?

If a simpler valid solution exists, point it out.
Do not refactor without my approval.

End the review with one of three classifications:
- **Ready to validate** — all criteria met, no blockers
- **Needs revision** — describe what must change before validation
- **Blocked** — describe what decision or information is needed

Then state the recommended next step.
