# PXOS Workflows

Workflows are saved prompts that an AI agent can follow on demand. In tools that support slash commands (e.g. Antigravity, Cursor, continue.dev, Claude Code), these can be triggered with `/workflow-name`.

This file contains the recommended workflow set for PXOS v2.0. Each workflow maps to a phase of the [default operating cycle](./README.md#default-workflow) defined in `AI_BASE.md` and supports both Single-Agent and Multi-Agent parallel environments.

---

## `/install` — Install PXOS in a project

**When to use:** When setting up PXOS in a new project. The agent detects the environment, picks the right flags, and runs the installer in one step. Use this instead of manually composing the `curl` command.

```
Install PXOS in this project by following these steps:

1. Detect the environment:
   - Check if a .cursor/ folder exists → IDE is Cursor
   - Check if a .windsurf/ folder exists → IDE is Windsurf
   - Check if a CLAUDE.md file exists, or if you are Claude Code → IDE is claude
   - Check if a GEMINI.md file exists, or if you are Gemini CLI → IDE is gemini
   - Check if .github/copilot-instructions.md exists → IDE is copilot
   - If none of the above → no --ide flag

2. Compose and run the install command:
   - Always include the base install (no extra flags needed for core files)
   - Add --ide if an IDE was identified
   - Add --full only if I explicitly asked for ROADMAP.md and SPRINT.md

   Examples:
   No IDE detected:      curl -sSL https://raw.githubusercontent.com/madebypx/PXOS/main/install.sh | bash
   Cursor detected:      curl -sSL https://raw.githubusercontent.com/madebypx/PXOS/main/install.sh | bash -s -- --ide cursor
   Claude Code detected: curl -sSL https://raw.githubusercontent.com/madebypx/PXOS/main/install.sh | bash -s -- --ide claude
   Full install with Cursor: curl -sSL https://raw.githubusercontent.com/madebypx/PXOS/main/install.sh | bash -s -- --full --ide cursor

3. After the install completes:
   - Open .ai/PROJECT_CONTEXT.md
   - Ask me to describe the project so you can help fill it in

Do not run the command until you have confirmed which IDE was detected and which flags will be used.
```

---

## `/update` — Upgrade PXOS to latest version

**When to use:** When upgrading an existing PXOS project to the latest version (e.g. from v1.x to v2.0). Safely updates universal operating rules (`AI_BASE.md`), modular specs template (`TEMPLATE_SPEC.md`), and IDE rules while strictly preserving custom project facts (`PROJECT_CONTEXT.md`), active specs, and decision logs.

```
Upgrade PXOS in this project by following these steps:

1. Check current PXOS version:
   - Read the version comment in `.ai/AI_BASE.md` (e.g. `<!-- pxos:version ... -->`).
   - If missing, it indicates a pre-v2.0 installation.

2. Run the safe update command:
   curl -sSL https://raw.githubusercontent.com/madebypx/PXOS/main/install.sh | bash -s -- --update

3. Summarize what was updated:
   - Report updated version (e.g. v2.0.0).
   - Confirm that .ai/specs/TEMPLATE_SPEC.md is present.
   - Confirm that PROJECT_CONTEXT.md, DECISION_LOG.md, and all active specs remain untouched.
   - State that the project is now ready for parallel multi-agent work and hybrid auto-resolution.
```

---

## `/start` — Open a work session (Hybrid Single/Multi-Agent)

**When to use:** At the beginning of every meaningful AI session. Loads the core context files, automatically discovers active branch and task spec, and establishes operating rules.

```
Read the core context files before doing anything:
- .ai/AI_BASE.md
- .ai/PROJECT_CONTEXT.md

Auto-resolve active task spec:
1. Run `git branch --show-current` to identify the current branch.
2. Check if a modular spec exists matching this branch in `.ai/specs/` (e.g. `.ai/specs/SPEC-<branch-suffix>.md` or `.ai/specs/SPEC-<branch-name>.md`).
3. If found, load it as the active task spec.
4. If not found, check `.ai/CURRENT_SPEC.md`.
5. If SPRINT.md exists at the project root, read it to verify assigned goals and dependencies.

Report your findings:
- Active branch: `[branch-name]`
- Active spec: `[spec path]`
- Current workflow phase: `[Discover / Plan / Execute / Validate / Review]`

Then ask me one question:
"Is this session for a new feature or complex task — or a quick fix / small change?"

- If new feature or complex task:
  Check the state of the active spec.
  - If it is populated with a clear goal and acceptance criteria:
    Summarize your understanding of the task in 3–5 bullets and confirm
    you are ready to move to the Plan phase. State what decision or
    confirmation you need from me before proceeding.
  - If it is empty or only contains template placeholders:
    Recommend running /spec to define the task together before planning
    or executing anything.

- If quick fix or small change:
  Ask me to describe the change in one or two sentences.
  Confirm scope, identify affected files, and proceed directly to execution
  following the autonomy rules in AI_BASE.md.

Do not implement anything until you have a clear understanding of scope.
```

---

## `/spec` — Draft a task spec (Modular or Central)

**When to use:** After `/start`, when the active spec is empty or when starting a new feature or task. Use this to collaborate on defining scope, constraints, and acceptance criteria.

```
Help me write a task spec using the PXOS standard structure:

1. Determine target file:
   - If on a dedicated branch/worktree (e.g. `feat/auth-oauth`), create/update `.ai/specs/SPEC-<branch-suffix>.md` based on `.ai/specs/TEMPLATE_SPEC.md`.
   - If on `main` or in a single-spec setup, update `.ai/CURRENT_SPEC.md`.

2. Fill the following structure:
   - Goal
   - User value
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
- That the recommended next step is to run /plan
```

---

## `/plan` — Request a plan before execution

**When to use:** When starting a complex or risky task and you want to explicitly force the planning phase before any code is written.

```
Before writing any code, produce a plan based on the active spec that includes:
1. What you understood from the task
2. Which files will be affected (ensuring no unauthorized shared file mutations)
3. What will change and why
4. Main risks and potential cross-task collisions
5. How success will be validated

After presenting the plan, explicitly state:
- What decision or confirmation you need from me before executing
- What will NOT happen until I approve

Wait for my approval before executing.
```

---

## `/review` — Review what was just implemented

**When to use:** After a task or feature has been executed. Use this to run a structured quality check on the branch diff before merging or opening a PR.

```
Review what was just implemented by checking the branch diff (e.g. against main/origin):
- Overengineering or unnecessary complexity
- Duplicate logic or conflicts with existing patterns
- Accidental scope growth (modifying files outside the task scope)
- Unauthorized edits to shared files (e.g. PROJECT_CONTEXT.md or DECISION_LOG.md)
- Weak naming
- Hidden side effects
- Inconsistencies with existing patterns

If a simpler valid solution exists, point it out.
Do not refactor without my approval.

End the review with one of three classifications:
- ✅ Ready to validate — all criteria met, no blockers
- 🔄 Needs revision — describe what must change before validation
- ⏸ Blocked — describe what decision or information is needed

Then state the recommended next step.
```

---

## `/compact` — Close a session and compact context

**When to use:** At the end of a long session, before switching tasks, or before submitting a PR. Produces a structured session summary and atomically updates task tracking.

```
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

Update workflow state:
1. Update the "Workflow state" section inside the active task spec (`.ai/specs/SPEC-*.md` or `CURRENT_SPEC.md`).
2. If SPRINT.md exists at the project root:
   - Locate the row or item corresponding to this task/branch in the Task Matrix.
   - Update its Status column (e.g., "In Plan", "Executing", "Ready for PR", "Done").
   - Leave other tasks and agents untouched.

If SPRINT.md does not exist but this project has a sprint in progress, ask me if I want to create it.
```

---

## Usage notes

- These workflows cover the full PXOS operating cycle: `/install` → `/start` → `/spec` (when needed) → `/plan` → execute → `/review` → `/compact`.
- In multi-agent parallel environments, each agent runs `/start` in its own worktree and automatically targets its own isolated spec.
- Do not create workflows for individual feature types or component patterns — that becomes a prompt library, which contradicts the PXOS principle of keeping the system minimal.
