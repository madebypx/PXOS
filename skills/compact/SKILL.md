---
name: compact
description: "PXOS /compact workflow: Close a session, compact context, record durable decisions (ADRs), and update SPRINT.md and active spec."
---

# /compact — Close a session and compact context

Summarize this session in a compact format:

## What changed
## Important decisions
## Open issues
## Next steps
## Relevant files or systems

Keep it short, factual, and reusable as future context.

In the "Next steps" section, distinguish between:
- Immediate next action (what should happen first in the next session)
- Pending human decision (what I need to decide before work resumes)
- Future follow-up (non-urgent items that can wait)

If the workflow state is incomplete, state which PXOS phase should resume first in the next session.

Update workflow state & durable memory:
1. Update the "Workflow state" section inside the active task spec (`.ai/specs/SPEC-*.md` or `CURRENT_SPEC.md`).
2. If `SPRINT.md` exists at the project root:
   - Locate the row or item corresponding to this task/branch in the Task Matrix.
   - Update its Status column (e.g., "In Plan", "Executing", "Ready for PR", "Done").
   - Leave other tasks and agents untouched.
3. **Architectural & Product Decision Check (Autonomous ADR):**
   - Did this session make or cement any durable architectural, structural, or product decisions (e.g., library choices, IPC/API protocols, rejected technical paths)?
   - If yes: Autonomously format an ADR entry (following the template in `.ai/DECISION_LOG.md`) and append it directly to the end of `.ai/DECISION_LOG.md`. Note the added ADR in the summary.

If `SPRINT.md` does not exist but this project has a sprint in progress, ask me if I want to create it.
