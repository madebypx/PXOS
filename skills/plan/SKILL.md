---
name: plan
description: "PXOS /plan workflow: Request a structured technical plan, evaluate single vs multi-agent decomposition, verify audit blockers, and provision worktrees upon approval."
---

# /plan — Request a plan before execution

Before writing any code, produce a plan based on the active spec that includes:

1. **Task Scope & Decomposition:**
   - Determine if this is a Single-Task (monolithic implementation) or if it can be decoupled into 2+ independent parallel tasks.
   - If parallelizable: Outline the sub-tasks (e.g. T-01 on `feat/auth`, T-02 on `feat/billing`) and propose creating dedicated worktrees automatically.

2. **Technical Implementation Plan:**
   - What you understood from the task
   - Which files will be affected (ensuring no unauthorized shared file mutations)
   - What will change and why
   - **Audit & Invariant Cross-Check:** Verify that proposed file edits directly account for known audit risks, cite audit IDs being resolved (e.g. SEC-01, MEM-03), and prevent reintroducing previously audited defects or architectural violations.
   - Main risks and cross-task dependencies
   - How success will be validated

3. **Mutation Lifecycle Check (conditional — only if this task creates, modifies, or deletes persisted data across multiple sources):**
   - List every persistence node affected (e.g., database, local storage, file system, external API, cache layer).
   - For each relevant mutation (Create / Update / Delete), state how it propagates to each node.
   - If a node is intentionally NOT updated, state why and confirm no background process (watcher, sync, cron) will contradict that decision.
   - Cross-reference critical invariants from `PROJECT_CONTEXT.md` if present.

After presenting the plan, explicitly state:
- What decision or confirmation you need from me before executing
- What will NOT happen until I approve
- *(If parallel tasks were proposed)*: Confirm that upon approval, you will automatically execute the worktree provisioning script (`./scripts/pxos-task.sh` or `.\scripts\pxos-task.ps1`), initialize specs, and register them in `SPRINT.md` without requiring manual commands from the user.

Wait for my approval before executing.
