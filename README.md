# PXOS

A reusable AI operating system for software and product development. A compact, framework-agnostic base that defines how an AI agent should behave, reason, and operate — across any project.

---

## What it is

PXOS is a four-document system designed to be adopted as a base layer in any project that uses AI agents for development work. It keeps universal operating rules separate from project-specific context, making it easy to reuse, adapt, and maintain over time.

It is not a prompt library. It is not a collection of tips. It is an operational contract between the human and the AI — defining priorities, workflow, autonomy boundaries, and quality standards that remain stable across projects.

---

## Why it exists

AI agents produce inconsistent results not because they lack capability, but because they lack operational structure. Without clear rules:

- They implement before understanding the problem.
- They over-engineer when simplicity would work.
- They consume context inefficiently.
- They make architectural decisions that should belong to the human.
- They lose coherence across long sessions.

PXOS addresses this with a minimal, durable operating layer.

---

## Structure

```
your-project/
├── .ai/                    # core — required
│   ├── AI_BASE.md
│   ├── PROJECT_CONTEXT.md
│   ├── CURRENT_SPEC.md
│   └── DECISION_LOG.md
├── ROADMAP.md              # optional — product direction (root, high visibility)
├── SPRINT.md               # optional — active sprint (root, high visibility)
└── docs/                   # optional — specialized technical context
    ├── DESIGN.md
    ├── DOMAIN_RULES.md
    ├── DATA_MODEL.md
    └── GLOSSARY.md
```

Each layer has a clear role: `.ai/` is the AI operational core, the root holds files every collaborator should find immediately, and `docs/` holds specialized context loaded on demand.

---

## Documents

### `AI_BASE.md`

The universal layer. Defines:

- Core priorities (correctness, clarity, simplicity, maintainability, consistency, context efficiency)
- Default workflow: Discover → Plan → Execute → Validate → Review → Compact Context
- Autonomy rules by risk level (Low / Medium / High)
- Context management rules
- Quality bar for task completion
- Behavioral constraints

This file should change rarely. When it does, update it intentionally across all projects.

### `PROJECT_CONTEXT.md`

The project-specific layer. Contains:

- Product summary, target user, core value
- Product priorities and anti-priorities
- Technical stack
- Architecture style and existing patterns
- Code, UX, and design conventions
- Known constraints and risks

This file grows slowly and holds only durable facts. It is not a place for session notes or temporary plans.

### `CURRENT_SPEC.md`

The task layer. Contains:

- Goal and user value
- Scope (in / out)
- Constraints
- Existing patterns relevant to the task
- Proposed change
- User flow
- Edge cases
- Acceptance criteria
- Validation plan
- Risks

Replace or update this file per feature or task. Optionally version past specs in a `/specs` archive.

### `DECISION_LOG.md`

The memory layer. Records:

- What was decided
- Why, including options considered
- Tradeoffs accepted
- Impact on the system
- Current status

Only durable decisions belong here — architectural choices, dependency replacements, structural changes, product direction shifts.

---

## How to use

### Setting up a new project

1. Copy the `.ai/` folder into the root of your project.
2. Fill in `PROJECT_CONTEXT.md` with your product and technical facts.
3. Keep `AI_BASE.md` as-is unless you have a strong reason to adjust it.
4. Leave `DECISION_LOG.md` empty until real decisions accumulate.
5. Use `CURRENT_SPEC.md` as the active task spec before each meaningful session.

For a faster setup, use the ready-to-copy templates in the [`/templates`](./templates) folder:

```bash
# Copy core files into your project
cp -r PXOS/templates/.ai ./

# Optionally copy planning files
cp PXOS/templates/ROADMAP.md ./
cp PXOS/templates/SPRINT.md ./
```

### Starting an AI session

Load documents based on what the session requires:

| Session type | Documents to load |
|---|---|
| New feature | `AI_BASE.md` + `PROJECT_CONTEXT.md` + `CURRENT_SPEC.md` |
| Bug fix | `AI_BASE.md` + `PROJECT_CONTEXT.md` |
| Architectural decision | `AI_BASE.md` + `PROJECT_CONTEXT.md` + `DECISION_LOG.md` |
| Isolated task | `AI_BASE.md` only |

### Updating documents

- `AI_BASE.md` — update only when a universal behavioral rule needs to change. Propagate to other projects intentionally.
- `PROJECT_CONTEXT.md` — update when product priorities, stack, or conventions change in a durable way.
- `CURRENT_SPEC.md` — replace per task. No need to preserve history unless you want it.
- `DECISION_LOG.md` — append only. Never delete past entries; mark them as superseded instead.

### Saved prompt workflows

For agents that support saved prompts or slash commands (e.g. Antigravity, Cursor, continue.dev), see [WORKFLOWS.md](./WORKFLOWS.md) for the recommended PXOS workflow set covering the full operating cycle: open → plan → execute → review → close.

---

## Extended context files (optional)

Some projects need additional, stable documents beyond the four core files. PXOS recommends a consistent placement convention based on the nature of each file.

### Placement convention

| Location | What belongs there | Examples |
|---|---|---|
| **Project root** | Files every collaborator should find immediately — product and sprint visibility | `ROADMAP.md`, `SPRINT.md` |
| **`docs/`** | Specialized technical context loaded on demand — not needed in every session | `DESIGN.md`, `DOMAIN_RULES.md`, `DATA_MODEL.md`, `GLOSSARY.md` |
| **`.ai/`** | The four core files only | `AI_BASE.md`, `PROJECT_CONTEXT.md`, `CURRENT_SPEC.md`, `DECISION_LOG.md` |

`.ai/` is reserved exclusively for the PXOS core. Do not add project-specific extended files there — it blurs the boundary between the universal operating layer and project content.

### Extended file examples

- `docs/DESIGN.md` — design language, components, tokens, interaction patterns
- `docs/DOMAIN_RULES.md` — domain-specific constraints (legal, financial, medical, etc.)
- `docs/DATA_MODEL.md` — stable description of entities, relationships, and invariants
- `docs/GLOSSARY.md` — domain language, naming decisions, and definitions

### How to load them in AI sessions

Treat extended files as on-demand context:

- Only load them when the task actually depends on them.
- Avoid loading all extended files by default to prevent context noise and token waste.
- Refer to them explicitly in the prompt when they matter, for example:

  > You also have access to `docs/DESIGN.md`. Use it as the source of truth for visual language and interaction patterns. Do not contradict it.

---

## Planning and progress files (optional)

For projects with active development cycles, two additional files help maintain shared awareness between human and AI across sessions. Both live at the **project root** for immediate visibility.

### `ROADMAP.md`

The product direction layer.

**Ownership: human.** The AI reads it for product direction context but does not update it autonomously. When a session decision affects the roadmap, the AI flags it and asks the human to update the file.

Contains:
- Planned features and improvements
- Priority order
- Status per item (planned / in progress / done / dropped)
- High-level dependencies between items

Template: [`templates/ROADMAP.md`](./templates/ROADMAP.md)

### `SPRINT.md`

The active sprint layer.

**Ownership: shared.** The human defines sprint goals. The AI updates task status and blockers via the `/compact` workflow at the end of each session.

Contains:
- Sprint name or date range
- Goals with completion status
- What is currently in progress
- Blockers
- What was completed this sprint
- Immediate next steps

This file is short-lived — replace it when a new sprint begins. Optionally archive past sprints in a `/sprints` folder.

Template: [`templates/SPRINT.md`](./templates/SPRINT.md)

### Ownership rules at a glance

| File | Who defines | Who updates | Life span |
|---|---|---|---|
| `ROADMAP.md` | Human | Human (AI flags changes) | Weeks / months |
| `SPRINT.md` | Human | Human + AI via `/compact` | Days / sprint |

---

## Templates

The [`/templates`](./templates) folder contains ready-to-copy versions of all PXOS files — core and optional.

```
templates/
├── .ai/
│   ├── AI_BASE.md
│   ├── PROJECT_CONTEXT.md
│   ├── CURRENT_SPEC.md
│   └── DECISION_LOG.md
├── SPRINT.md              # optional
└── ROADMAP.md             # optional
```

All files include placeholder instructions and comments to guide setup.

---

## Prompt templates

PXOS does not prescribe a prompt library. The `CURRENT_SPEC.md` file already serves as the task prompt — a well-filled spec eliminates the need for verbose task descriptions in the prompt itself.

What is worth standardizing is the **session opener**: the short message that initializes any AI session under PXOS, establishes which files are in context, and enforces the workflow before any implementation begins.

### Standard session opener

Use this for most sessions — new features, bug fixes, refactors, and general development tasks.

```
You have access to the following context files. Read all of them before doing anything.

- .ai/AI_BASE.md — your operating rules
- .ai/PROJECT_CONTEXT.md — project context
- .ai/CURRENT_SPEC.md — current task spec

Do not implement anything until you have completed the Discover and Plan phases and I have confirmed the plan.
```

### Extended session opener

Use this when the task touches areas covered by extended context files.

```
You have access to the following context files. Read all of them before doing anything.

- .ai/AI_BASE.md — your operating rules
- .ai/PROJECT_CONTEXT.md — project context
- .ai/CURRENT_SPEC.md — current task spec
- docs/[EXTENDED_FILE].md — [describe what it covers, e.g. "design system and visual language"]

Do not implement anything until you have completed the Discover and Plan phases and I have confirmed the plan.
```

Replace `[EXTENDED_FILE]` and the description with the actual file and what it governs. Only include extended files that are directly relevant to the current task.

### Why only two templates

Adding more prompt templates creates a prompt system that must be maintained separately from the documents it references. That adds overhead without proportional benefit. If a task requires unusual framing, write it inline — do not create a new template for it.

---

## Principles

The system is built on five operational beliefs:

**1. Context is a limited resource.**
More context does not produce better results. Excess context increases noise, reduces precision, and raises cost. Load only what the current task requires.

**2. Understanding before implementation.**
An agent that skips discovery produces solutions to the wrong problem. The Discover and Plan phases are not optional steps — they are how quality is preserved.

**3. Simplicity is the output, not the method.**
The goal is not to keep the codebase simple by restricting what the AI can do. The goal is for the AI to produce the simplest valid solution by reasoning about tradeoffs explicitly.

**4. Autonomy requires boundaries.**
An agent with no constraints makes strategic decisions it should not make. An agent with too many constraints becomes slow and brittle. The Low / Medium / High risk model defines where human judgment is required without over-restricting execution.

**5. Validation closes the loop.**
A task that has not been validated has not been completed. The quality bar is not subjective — it is defined in advance by the spec's acceptance criteria.

---

## License

MIT
