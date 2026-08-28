# PXOS

[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](https://github.com/madebypx/PXOS/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

A reusable AI operating system for software and product development.

A compact, framework-agnostic base that defines how an AI agent should behave, reason, and operate — across any project, in single-agent or parallel multi-agent setups.

---

## Quick Install

Run this in the root of any project:

```bash
curl -sSL https://raw.githubusercontent.com/madebypx/PXOS/main/install.sh | bash
```

This creates the `.ai/` folder with the core files and modular spec templates. No dependencies beyond `curl`.

### Upgrading an Existing Project

To safely upgrade an existing project to **PXOS v2.0** without touching your project context or existing specs:

```bash
curl -sSL https://raw.githubusercontent.com/madebypx/PXOS/main/install.sh | bash -s -- --update
```
*(Or invoke the `/update` workflow directly from your AI agent).*

### Installation Options

```bash
# Also install ROADMAP.md and SPRINT.md
curl -sSL https://raw.githubusercontent.com/madebypx/PXOS/main/install.sh | bash -s -- --full

# Also configure your IDE (workspace only)
curl -sSL https://raw.githubusercontent.com/madebypx/PXOS/main/install.sh | bash -s -- --ide cursor
curl -sSL https://raw.githubusercontent.com/madebypx/PXOS/main/install.sh | bash -s -- --ide windsurf
curl -sSL https://raw.githubusercontent.com/madebypx/PXOS/main/install.sh | bash -s -- --ide claude
curl -sSL https://raw.githubusercontent.com/madebypx/PXOS/main/install.sh | bash -s -- --ide gemini
curl -sSL https://raw.githubusercontent.com/madebypx/PXOS/main/install.sh | bash -s -- --ide copilot

# Install IDE rules globally (all projects in that IDE)
curl -sSL https://raw.githubusercontent.com/madebypx/PXOS/main/install.sh | bash -s -- --global --ide cursor

# Everything at once
curl -sSL https://raw.githubusercontent.com/madebypx/PXOS/main/install.sh | bash -s -- --full --ide cursor
```

### IDE rules behavior

| IDE | Scope | File created |
|---|---|---|
| Cursor | workspace | `.cursor/rules/pxos.mdc` |
| Windsurf | workspace | `.windsurf/rules/pxos.md` |
| Claude Code | workspace or `~/.claude/` | `CLAUDE.md` |
| Gemini CLI | workspace or `~/.gemini/` | `GEMINI.md` |
| GitHub Copilot | workspace only | `.github/copilot-instructions.md` |

For `claude`, `gemini`, and `copilot`: if the file already exists, PXOS **appends** its rules instead of replacing your content. Safe to run multiple times.

After installing, fill in `.ai/PROJECT_CONTEXT.md` with your project facts and you're ready to start a session.

---

## What it is

PXOS is a structured, document-driven operating system designed to be adopted as a base layer in any project that uses AI agents for development work. It keeps universal operating rules separate from project-specific context, making it easy to reuse, adapt, and maintain over time.

It is not a prompt library or an autonomous framework with infinite, expensive chat loops. It is an **operational contract** between the human developer and AI agents — defining priorities, workflow phases, concurrency isolation, and quality standards that remain stable across projects and toolchains.

---

## Why it exists

AI agents produce inconsistent results and waste tokens not because they lack capability, but because they lack operational structure. Without clear rules:

- They implement before understanding the problem.
- They over-engineer when simplicity would work.
- They consume context inefficiently through noisy chat loops.
- In multi-agent scenarios, they collide on working files and overwrite specs.
- They make architectural decisions that should belong to the human.
- They lose coherence across long sessions.

PXOS addresses this with a minimal, durable operating layer.

---

## Structure

```
your-project/
├── .ai/                            # core — required
│   ├── AI_BASE.md                  # universal operating & concurrency rules
│   ├── PROJECT_CONTEXT.md          # durable project facts & patterns
│   ├── DECISION_LOG.md             # durable architectural decisions
│   ├── CURRENT_SPEC.md             # active spec for single-agent mode
│   └── specs/                      # [v2.0] modular specs for parallel multi-agent mode
│       ├── TEMPLATE_SPEC.md        # standardized task spec template
│       ├── SPEC-auth-oauth.md      # isolated task spec for branch feat/auth-oauth
│       └── SPEC-billing-stripe.md  # isolated task spec for branch feat/billing-stripe
├── SPRINT.md                       # optional — active sprint & multi-agent task matrix
├── ROADMAP.md                      # optional — product direction (human-owned)
├── scripts/                        # optional — lightweight DX helpers
│   ├── pxos-task.sh                # POSIX bash worktree helper
│   └── pxos-task.ps1               # PowerShell worktree helper
└── docs/                           # optional — specialized technical context
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
- **Multi-Agent & Concurrency Rules** (worktree isolation, spec auto-resolution, shared file mutation rules)
- **Agent Roles** (Architect, Executor, Auditor)
- Context management rules
- Quality bar and behavioral constraints

### `PROJECT_CONTEXT.md`

The project-specific layer. Contains:

- Product summary, target user, core value
- Technical stack, conventions, and existing architectural patterns
- Known constraints and risks

### `CURRENT_SPEC.md` & `.ai/specs/SPEC-<task>.md`

The task specification layer:
- **`CURRENT_SPEC.md`**: Used in traditional Single-Agent mode.
- **`.ai/specs/SPEC-<task>.md`**: Used in Multi-Agent parallel mode, isolating requirements and state per branch/worktree.

### `DECISION_LOG.md`

The durable memory layer:
- Records significant architectural decisions, alternatives evaluated, tradeoffs, and system impacts.
- In multi-agent parallel branches, decisions are drafted in the local spec and promoted to `DECISION_LOG.md` upon merge to `main`.

---

## Multi-Agent Development with Git Worktrees

PXOS v2.0 introduces native support for **parallel multi-agent development** with zero context collision and zero merge noise:

```
                  ┌────────────────────────────────────────────────────────┐
                  │                 HUMAN ORCHESTRATOR                     │
                  │             Coordinates: SPRINT.md                     │
                  └───────────────────────────┬────────────────────────────┘
                                              │
                    ┌─────────────────────────┴─────────────────────────┐
                    ▼                                                   ▼
      ┌───────────────────────────┐                       ┌───────────────────────────┐
      │   WORKTREE 1: feat/auth   │                       │  WORKTREE 2: feat/stripe  │
      │   Role: Coding Executor   │                       │  Role: Coding Executor   │
      │   Model: Fast / Flash ⚡  │                       │   Model: Fast / Flash ⚡  │
      │   Spec: SPEC-auth.md      │                       │   Spec: SPEC-stripe.md    │
      └─────────────┬─────────────┘                       └─────────────┬─────────────┘
                    │                                                   │
                    └─────────────────────────┬─────────────────────────┘
                                              ▼
                                ┌───────────────────────────┐
                                │    REVIEW / PR GATEWAY    │
                                │   Role: Auditor / QA      │
                                │   Model: High-Reasoning 🧠 │
                                │   Command: /review        │
                                └───────────────────────────┘
```

### 1. Worktree & Spec Isolation
Each agent operates in an independent physical directory using `git worktree` and reads only its assigned modular spec (`.ai/specs/SPEC-<task>.md`). This guarantees:
- **Zero local file collisions** between concurrent agents.
- **Minimal context window usage** (agents do not process unrelated tasks).
- **Clean Git history** with atomic pull requests.

### 2. Autonomous Provisioning (Zero Manual Plumbing)
You don't need to create branches or worktrees manually. During the **`/plan`** workflow, the AI agent:
1. Automatically identifies if your request should be split into parallel sub-tasks.
2. Proposes the sub-tasks (e.g. `T-01` on `feat/auth-oauth` and `T-02` on `feat/billing-stripe`).
3. Upon your approval of the plan, **the agent itself executes the provisioning script** via terminal, scaffolds the modular specs, and updates `SPRINT.md`.

*Manual override is also supported via `scripts/pxos-task.sh` (Bash) or `scripts/pxos-task.ps1` (PowerShell).*

This creates the branch, sets up `../trees/feat-auth-oauth`, copies `TEMPLATE_SPEC.md` to `.ai/specs/SPEC-auth-oauth.md`, and prepares the agent workspace.

---

## Token & Cost Efficiency Guide (The 80/20 Rule)

Multi-agent chatrooms (e.g. unconstrained conversational frameworks) waste tens of thousands of tokens per minute in conversational loops. PXOS is **document-driven**, meaning agents communicate asynchronously through structured Markdown artifacts:

1. **The 80/20 Model Strategy:**
   - **Use Fast/Cost-Efficient Models (e.g. Gemini 1.5/2.0 Flash) for 90% of execution:** Code writing, diff generation, and unit testing in worktrees.
   - **Reserve High-Reasoning Models (e.g. Gemini 1.5/2.5 Pro, Claude Sonnet) for 10% of strategic tasks:** Writing the architectural spec (`/spec`) and auditing the diff (`/review`).
2. **Artifact Passing vs. Chat History:**
   - Instead of passing whole conversation transcripts between agents, agents produce clean specs and diffs. This reduces token consumption by **70% to 85%**.

---

## Saved Prompt Workflows

For agents that support slash commands (e.g. Antigravity, Cursor, Claude Code, continue.dev), see [WORKFLOWS.md](./WORKFLOWS.md) for the complete workflow set:

- **`/install`** — Detects environment and installs PXOS.
- **`/start`** — Auto-resolves current branch, loads relevant spec, and establishes scope.
- **`/spec`** — Collaboratively drafts modular or central task specifications.
- **`/plan`** — Formulates a structured technical plan before writing code.
- **`/review`** — Audits implemented diffs for overengineering, scope creep, and quality.
- **`/compact`** — Compacts context, updates workflow status, and updates `SPRINT.md`.

---

## Prompt Templates

### Standard Session Opener (Single-Agent)

```
You have access to the following context files. Read all of them before doing anything.

- .ai/AI_BASE.md — your operating rules
- .ai/PROJECT_CONTEXT.md — project context
- .ai/CURRENT_SPEC.md — current task spec

Do not implement anything until you have completed the Discover and Plan phases and I have confirmed the plan.
```

### Multi-Agent Worktree Session Opener

```
You have access to the following context files. Read all of them before doing anything.

- .ai/AI_BASE.md — your operating rules
- .ai/PROJECT_CONTEXT.md — project context
- SPRINT.md — sprint coordination and task matrix

Run `git branch --show-current` to identify your active branch and load the corresponding spec in `.ai/specs/`.

Do not implement anything until you have completed the Discover and Plan phases and I have confirmed the plan.
```

---

## Principles

**1. Context is a limited resource.**  
Excess context increases noise, reduces precision, and raises cost. Load only what the current task requires.

**2. Understanding before implementation.**  
An agent that skips discovery produces solutions to the wrong problem. Discover and Plan preserve quality.

**3. Simplicity is the output, not the method.**  
The goal is for the AI to produce the simplest valid solution by reasoning about tradeoffs explicitly.

**4. Autonomy requires boundaries.**  
The Low / Medium / High risk model defines where human judgment is required without over-restricting execution.

**5. Validation closes the loop.**  
A task that has not been validated has not been completed. The quality bar is defined by the spec's acceptance criteria.

---

## License

MIT
