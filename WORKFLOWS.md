# PXOS Workflows

Workflows are saved prompts that an AI agent can follow on demand. In tools that support slash commands (e.g. Antigravity, Cursor, continue.dev), these can be triggered with `/workflow-name`.

This file contains the recommended workflow set for PXOS. Each workflow maps to a phase of the [default operating cycle](./README.md#default-workflow) defined in `AI_BASE.md`.

---

## `/install` — Install PXOS in a project

**When to use:**
When setting up PXOS in a new project. The agent detects the environment, picks the right flags, and runs the installer in one step. Use this instead of manually composing the `curl` command.

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
   - Add --ide <detected> if an IDE was identified
   - Add --full only if I explicitly asked for ROADMAP.md and SPRINT.md

   Examples:
     No IDE detected:
       curl -sSL https://raw.githubusercontent.com/rodrigospena/PXOS/main/install.sh | bash

     Cursor detected:
       curl -sSL https://raw.githubusercontent.com/rodrigospena/PXOS/main/install.sh | bash -s -- --ide cursor

     Claude Code detected:
       curl -sSL https://raw.githubusercontent.com/rodrigospena/PXOS/main/install.sh | bash -s -- --ide claude

     Full install with Cursor:
       curl -sSL https://raw.githubusercontent.com/rodrigospena/PXOS/main/install.sh | bash -s -- --full --ide cursor

3. After the install completes:
   - Open .ai/PROJECT_CONTEXT.md
   - Ask me to describe the project so you can help fill it in

Do not run the command until you have confirmed which IDE was detected and which flags will be used.
```

---

## `/start` — Open a work session

**When to use:**
At the beginning of every meaningful AI session. Loads the three core context files, establishes operating rules, and prevents the agent from implementing before understanding the task. This is the most important workflow — it sets the contract for the entire session.

```
Read the following files before doing anything:
- .ai/AI_BASE.md
- .ai/PROJECT_CONTEXT.md
- .ai/CURRENT_SPEC.md

If SPRINT.md exists at the project root, read it as well.

Do not implement anything until you have completed the Discover and Plan phases and I have confirmed the plan.
```

---

## `/plan` — Request a plan before execution

**When to use:**
When starting a complex or risky task and you want to explicitly force the planning phase before any code is written. Use this after `/start` if the task warrants a detailed plan, or independently when resuming mid-session and you need alignment before continuing.

```
Before writing any code, produce a plan that includes:
1. What you understood from the task
2. Which files will be affected
3. What will change and why
4. Main risks
5. How success will be validated

Wait for my approval before executing.
```

---

## `/review` — Review what was just implemented

**When to use:**
After a task or feature has been executed. Use this to run a structured quality check before considering the work done. It catches overengineering, unintended scope growth, and inconsistencies that are easy to miss immediately after implementation.

```
Review what was just implemented and check for:
- Overengineering or unnecessary complexity
- Duplicate logic
- Accidental scope growth
- Weak naming
- Hidden side effects
- Inconsistencies with existing patterns

If a simpler valid solution exists, point it out. Do not refactor without my approval.
```

---

## `/compact` — Close a session and compact context

**When to use:**
At the end of a long or productive session, before switching tasks, or when context has grown noisy. Produces a structured session summary and, if the project uses `SPRINT.md`, updates it to reflect current sprint state. This keeps continuity between sessions without reloading full history.

```
Summarize this session in a compact format:

## What changed
## Important decisions
## Open issues
## Next steps
## Relevant files or systems

Keep it short, factual, and reusable as future context.

If the file SPRINT.md exists at the project root, also update it:
- Mark completed goals as done [x]
- Update the "In progress" section to reflect current state
- Add any new blockers
- Update "Next" with the immediate next steps
- Do not change the sprint goal or remove completed items — only append and update status

If SPRINT.md does not exist but this project has a sprint in progress, ask me if I want to create it.
```

---

## `/spec` — Draft a task spec

**When to use:**
When starting a new feature or task and you need to produce a `CURRENT_SPEC.md` before development begins. Use this to collaborate with the agent on defining scope, constraints, and acceptance criteria — rather than writing the spec alone. A good spec prevents misalignment during execution.

```
Help me write a task spec using this structure:

- Goal
- User value
- Scope (in / out)
- Constraints
- Existing patterns relevant to the task
- Proposed change
- User flow
- Edge cases
- Acceptance criteria
- Validation plan
- Risks

Ask me questions if anything is unclear before filling it in.
```

---

## Usage notes

- These workflows cover the full PXOS operating cycle: install → open → plan → execute → review → close.
- Do not create workflows for individual feature types or component patterns — that becomes a prompt library, which contradicts the PXOS principle of keeping the system minimal.
- If a task requires unusual framing, write it inline. Only promote something to a workflow if it is genuinely reused across sessions.
