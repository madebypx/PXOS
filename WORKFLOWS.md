# PXOS Workflows

Workflows are saved prompts that an AI agent can follow on demand. In tools that support slash commands (e.g. Antigravity, Cursor, continue.dev, Claude Code), these can be triggered with `/workflow-name`.

This file contains the recommended workflow set for PXOS v2.1. Each workflow maps to a phase of the default operating cycle defined in `AI_BASE.md` and supports both Single-Agent and Multi-Agent parallel environments.

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

**When to use:** When upgrading an existing PXOS project to the latest version (v2.2.0). Safely updates universal operating rules (`AI_BASE.md`), modular specs template (`TEMPLATE_SPEC.md`), research/audit scaffolding, and IDE rules while strictly preserving custom project facts (`PROJECT_CONTEXT.md`), active specs, and decision logs.

```
Upgrade PXOS in this project by following these steps:

1. Check current PXOS version:
   - Read the version comment in `.ai/AI_BASE.md` (e.g. `<!-- pxos:version ... -->`).
   - If missing, it indicates a pre-v2.0 installation.

2. Run the safe update command:
   curl -sSL https://raw.githubusercontent.com/madebypx/PXOS/main/install.sh | bash -s -- --update

3. Summarize what was updated:
   - Report updated version (v2.2.0).
   - Confirm that .ai/specs/TEMPLATE_SPEC.md includes Strategic & Audit Alignment.
   - Confirm that .ai/research/ and .ai/audits/ directories and starter guides are present.
   - Confirm that PROJECT_CONTEXT.md, DECISION_LOG.md, and all active specs remain untouched.
   - State that the project is now ready for v2.2.0 workflows (/decision, /audit, /benchmark, UX reviews).
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
5. If SPRINT.md exists at the project root (or inside `.internal/SPRINT.md` / `.ai/SPRINT.md`), read it to verify assigned goals and dependencies.

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

2. Autonomous Grounding (Macro Context):
   - Autonomously inspect `.ai/audits/` (or `docs/audits/`) for open findings touching the affected files.
   - Autonomously check `.ai/research/INDEX.md` (or `docs/research/`) for active benchmarks or architectural invariants.
   - Auto-populate the Strategic & Audit Alignment block with explicit IDs or "Clean — No active audit blockers touching this scope".

3. Fill the following structure:
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
- That the recommended next step is to run /plan
```

---

## `/plan` — Request a plan before execution

**When to use:** When starting a complex or risky task and you want to explicitly force the planning phase before any code is written.

```
Before writing any code, produce a plan based on the active spec that includes:

1. Task Scope & Decomposition:
   - Determine if this is a Single-Task (monolithic implementation) or if it can be decoupled into 2+ independent parallel tasks.
   - If parallelizable: Outline the sub-tasks (e.g. T-01 on `feat/auth`, T-02 on `feat/billing`) and propose creating dedicated worktrees automatically.

2. Technical Implementation Plan:
   - What you understood from the task
   - Which files will be affected (ensuring no unauthorized shared file mutations)
   - What will change and why
   - Audit & Invariant Cross-Check: Verify that proposed file edits directly account for known audit risks, cite audit IDs being resolved (e.g. SEC-01, MEM-03), and prevent reintroducing previously audited defects.
   - Main risks and cross-task dependencies
   - How success will be validated

3. Mutation Lifecycle Check (conditional — only if this task creates, modifies, or deletes persisted data across multiple sources):
   - List every persistence node affected (e.g., database, local storage, file system, external API, cache layer).
   - For each relevant mutation (Create / Update / Delete), state how it propagates to each node.
   - If a node is intentionally NOT updated, state why and confirm no background process (watcher, sync, cron) will contradict that decision.
   - Cross-reference critical invariants from `PROJECT_CONTEXT.md` if present.

After presenting the plan, explicitly state:
- What decision or confirmation you need from me before executing
- What will NOT happen until I approve
- (If parallel tasks were proposed): Confirm that upon approval, you will automatically execute the worktree provisioning script (`./scripts/pxos-task.sh` or `.\scripts\pxos-task.ps1`), initialize specs, and register them in SPRINT.md.

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
- Unauthorized edits to shared files (e.g. PROJECT_CONTEXT.md)
- Weak naming or missing error boundaries
- Hidden side effects or security risks
- Inconsistencies with existing patterns

UX & Interaction Heuristics (If the diff modifies UI, styles, or frontend interactions):
- Status visibility: Are loading states, transitions, and system feedback clear and responsive?
- Error prevention: Are destructive actions guarded with confirmation? Are validation errors clear?
- Cognitive friction: Is the user flow direct and intuitive, minimizing unnecessary clicks or confusion?

Spec Satisfaction Check:
- Re-read the active spec's acceptance criteria.
- For each criterion, classify: ✅ Verified (state how) | ⚠️ Not directly verified (state why) | ❌ Not met (state what's missing).
- Flag any implementation that relies on assumed values not sourced from the codebase or domain rules.

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

**When to use:** At the end of a long session, before switching tasks, or before submitting a PR. Produces a structured session summary, automatically records architectural decisions (ADRs), and atomically updates task tracking.

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

Update workflow state & durable memory:
1. Update the "Workflow state" section inside the active task spec (`.ai/specs/SPEC-*.md` or `CURRENT_SPEC.md`).
2. If SPRINT.md exists at the project root (or inside `.internal/SPRINT.md` / `.ai/SPRINT.md`):
   - Locate the row or item corresponding to this task/branch in the Task Matrix.
   - Update its Status column (e.g., "In Plan", "Executing", "Ready for PR", "Done").
   - Leave other tasks and agents untouched.
3. Architectural & Product Decision Check (Autonomous ADR):
   - Did this session make or cement any durable architectural, structural, or product decisions (e.g. library choices, API/IPC protocols, rejected alternatives)?
   - If yes: Autonomously format an ADR entry and append it directly to the end of `.ai/DECISION_LOG.md`. Note the added ADR in the summary.

If SPRINT.md does not exist but this project has a sprint in progress, ask me if I want to create it.
```

---

## `/decision` — Record an architectural or product decision (ADR)

**When to use:** When you or the agent make a lasting decision during conversation that should be durably recorded immediately without waiting for `/compact`.

```
Record an architectural or product decision into .ai/DECISION_LOG.md:

1. Capture context:
   - What was decided?
   - What alternatives were considered and why were they rejected?
   - What are the key tradeoffs and impacts?

2. Format as a standard ADR (following the schema in .ai/DECISION_LOG.md).
3. Append directly to the end of .ai/DECISION_LOG.md.
4. Confirm to me that the decision has been logged and summarize the core invariant.
```

---

## `/audit` — Autonomous codebase or subsystem audit

**When to use:** Before major releases, after refactors, or to diagnose technical debt, memory leaks, and security posture across subsystems.

```
Act as a Principal Auditor to inspect codebase subsystems against quality, security, and memory standards:

1. Scope & Context Window Protection:
   - Audit modularly by subsystem (e.g. /audit auth, /audit audio, /audit ipc) to prevent context exhaustion.
   - For a full audit, inspect subsystems sequentially and synthesize a consolidated report.

2. Inspect across core dimensions:
   - Security & Auth (secrets, injection, sanitization, exposed APIs)
   - Performance & Memory (leaks, unclosed handles, event listeners, main-thread blocking)
   - Architecture & Invariants (layering, circular imports, adherence to PROJECT_CONTEXT.md)
   - Reliability & Errors (swallowed exceptions, unhandled promises, missing error boundaries)
   - UX & Interaction (if UI: status visibility, destructive actions guarded)

3. Format structured findings with IDs, severity (P0 Blocker, P1 Critical, P2 Major, P3 Minor), location, evidence, and remediation.
4. Output report into .ai/audits/PARTIAL_<subsystem>.md or .ai/audits/AUDIT_YYYY-MM-DD.md.
5. Provide an executive summary with count by severity and immediate blockers.
```

---

## `/benchmark` — Empirical performance & telemetry audit

**When to use:** After completing a feature or session. Measures token efficiency, code rework, and UX state completeness, saves empirical JSON telemetry cleanly within `.ai/audits/` (zero project root pollution), and autonomously contributes anonymous metrics to the research study upon user consent.

```
Audit development performance on recent tasks:

1. Extract Telemetry:
   - Calculate total turns, prompt tokens, completion tokens, and framework overhead.
   - Calculate rework ratio (lines modified or deleted after initial diff).
   - Evaluate UX completeness (Universal 5-State Matrix: idle, loading, empty, error, destructive guard).
   - Check architectural fidelity (ADR retention, duplicate utilities prevented).

2. Clean Storage (Zero Project Root Pollution):
   - In consumer projects, save structured JSON strictly inside:
     .ai/audits/BENCHMARK_<task_id>.json
   - Never create a root benchmarks/ folder in consumer repositories.

3. Interactive Consent & Autonomous Dispatch:
   - Present the sanitized preview of numerical metrics to the human.
   - Ask for explicit consent to transmit anonymous telemetry.
   - If approved, autonomously POST the JSON payload to https://telemetry.madebypx.com/api/v1/telemetry.
   - Report the resulting submission ID back to the user.
```

### Monitoring Telemetry Health & Public Submissions

To verify server stability and monitor community benchmark submissions in real time:

```bash
# Live terminal dashboard (snapshot):
python scripts/pxos-telemetry-monitor.py

# Continuous watch mode (auto-refreshing every 15s):
python scripts/pxos-telemetry-monitor.py --watch

# Machine-readable JSON output for CI / dashboards:
python scripts/pxos-telemetry-monitor.py --json

# Latency threshold check (fails with exit code 1 if ping > 300ms):
python scripts/pxos-telemetry-monitor.py --max-latency-ms 300
```

---

## Usage notes

- These workflows cover the complete PXOS operating cycle: `/install` → `/start` → `/spec` → `/plan` → execute → `/review` → `/compact`, plus on-demand macro tools (`/decision`, `/audit`).
- In multi-agent parallel environments, each agent runs `/start` in its own worktree and automatically targets its own isolated spec.
- `DECISION_LOG.md` entries are strictly append-only; in the rare event of a git merge conflict, concatenate entries without discarding either.
- Do not create workflows for individual feature types or component patterns — that becomes a prompt library, which contradicts the PXOS principle of keeping the system minimal.
