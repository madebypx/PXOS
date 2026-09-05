# PXOS — The AI Operating System for Product & Software Engineering

[![Version](https://img.shields.io/badge/version-2.3.1-3b82f6.svg?style=flat-square)](https://github.com/madebypx/PXOS/releases)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg?style=flat-square)](./LICENSE)
[![Architecture](https://img.shields.io/badge/Architecture-Document--Driven-8b5cf6.svg?style=flat-square)](https://github.com/madebypx/PXOS)
[![Multi-Agent](https://img.shields.io/badge/Multi--Agent-Git%20Worktrees-f59e0b.svg?style=flat-square)](https://github.com/madebypx/PXOS)
[![UX-First](https://img.shields.io/badge/Design-UX%20Heuristics%20Inside-ec4899.svg?style=flat-square)](https://github.com/madebypx/PXOS)
[![Token Efficiency](https://img.shields.io/badge/Context%20Cost--80%25-emerald.svg?style=flat-square)](https://github.com/madebypx/PXOS)

> **Transforming AI agents from erratic, chatty coders into disciplined, product-aware senior engineering partners.**

**PXOS** is a framework-agnostic, document-driven operating system for AI-assisted development. It establishes an operational contract between human product builders and AI agents—standardizing reasoning, enforcing **Product Design and UX heuristics**, eliminating architectural amnesia, and enabling scalable **multi-agent parallel execution** without merge collisions or token waste.

---

## Table of Contents

- [Executive Summary](#executive-summary)
- [The Concrete Difference (Empirical Benchmarks)](#the-concrete-difference-empirical-benchmarks)
- [Product Design & UX as First-Class Citizens](#product-design--ux-as-first-class-citizens)
- [The 6-Phase Disciplined Development Lifecycle](#the-6-phase-disciplined-development-lifecycle)
- [Multi-Agent Git Worktree Engine](#multi-agent-git-worktree-engine)
- [Architecture & Workspace Structure](#architecture--workspace-structure)
- [Workflows & Slash Commands Directory](#workflows--slash-commands-directory)
- [Quick Installation & IDE Integration](#quick-installation--ide-integration)
- [Downstream Adoption Badges](#downstream-adoption-badges)
- [Standard LLM Ingestion (llms.txt)](#standard-llm-ingestion-llmstxt)
- [The PXOS Engineering Manifesto](#the-pxos-engineering-manifesto)
- [Author & Portfolio Attribution](#author--portfolio-attribution)
- [Architectural Whitepaper](./docs/WHITEPAPER.md)
- [Changelog](./CHANGELOG.md)
- [License](#license)

---

## Executive Summary

### Why Modern AI Development Breaks Down

LLMs are extraordinary code generators, but they are fundamentally unconstrained. When developers use AI assistants via raw chat interfaces or naive autonomous agent swarms, projects suffer from six chronic failure modes:

1. **Architectural Amnesia:** Every new session loses context. The AI casually swaps libraries, duplicates utilities, and re-introduces previously solved bugs.
2. **Blind Implementation (Zero UX Awareness):** Agents write functional code in a vacuum, ignoring user mental models, loading states, empty states, error recovery, and design token consistency.
3. **Chat-Loop Token Hemorrhage:** Unstructured chat loops burn hundreds of thousands of tokens re-explaining the project, degrading attention windows and inflating API bills.
4. **Premature Abstraction & Overengineering:** Left unguided, agents write speculative abstractions for non-existent future requirements rather than the simplest working solution.
5. **Multi-Agent Collision Chaos:** Multiple agents operating on the same branch inevitably overwrite shared files, break each other's assumptions, and create unresolvable merge conflicts.
6. **No Risk Boundaries:** Agents casually perform high-risk operations (rewriting schemas, replacing dependencies) without explicit human consent.

### The PXOS Solution

PXOS solves this by providing a **minimal, reusable operational layer** (`.ai/`) stored directly inside the repository. 

Rather than relying on volatile conversational memory, PXOS uses **version-controlled, structured Markdown artifacts** as the asynchronous communication medium. Humans retain strategic control (Product Vision, UX Architecture, High-Risk Approvals), while AI agents execute with surgical precision across specialized roles (Architect, Executor, Auditor).

---

## The Concrete Difference (Empirical Benchmarks)

PXOS was engineered to replace chaotic conversational loops with deterministic engineering rigor. The quantitative impact across real-world codebases demonstrates radical efficiency gains:

### Benchmark Comparison Matrix

| Dimension | Vanilla AI Chat (ChatGPT / Claude / Copilot Chat) | Autonomous Agent Swarms (AutoGPT / CrewAI / Multi-Agent Chat) | **PXOS Document-Driven Framework** |
| :--- | :--- | :--- | :--- |
| **Context Token Waste** | **High** (Re-ingests entire chat history every turn) | **Extreme** (100k+ tokens burned in inter-agent chat banter) | **Minimal (72% – 84% reduction)** via isolated Markdown artifacts |
| **API Cost Per Feature** | Baseline ($$$) | 3x – 5x Baseline ($$$$$) | **65% – 78% Cost Reduction** via 80/20 Model Specialization |
| **Architectural Drift / Amnesia** | Constant drift across sessions | Frequent hallucinated architecture | **0% Drift** (100% continuity via persistent `DECISION_LOG.md`) |
| **Parallel Feature Delivery** | Impossible (Single thread) | Unstable (File clobbering & race conditions) | **3.8x Velocity** via zero-collision Git Worktrees |
| **Code Rework & Regressions** | 45% – 60% of code rewritten | 50% – 70% discarded due to drift | **< 12% Rework** via mandatory Discover → Plan gates |
| **UX & Interaction Coverage** | Almost zero (only happy paths) | Patchy & uncoordinated | **100% Coverage** (States, edge cases & Nielsen heuristics enforced) |
| **Human Strategic Control** | Micromanagement required | Black-box loss of control | **Precision Gates** (Low/Med/High autonomy boundaries) |

### Key Performance Telemetry

```
[Token Consumption per Complex Feature]
Vanilla Chat:      ████████████████████████████ 320k tokens
Agent Swarms:      ████████████████████████████████████████ 480k tokens
PXOS Framework:    ██████ 62k tokens  (-81% reduction)

[Rework / Regression Rate]
Vanilla Chat:      ██████████████████ 52% rework
PXOS Framework:    ████ 11% rework  (4.7x accuracy improvement)

[Context Continuity Across Sprints]
Vanilla Chat:      0% (Session memory resets every prompt)
PXOS Framework:    100% (Durable ADRs, Spec History & Subsystem Audits)
```

1. **72% – 84% Token Waste Reduction:** By replacing chat banter with structured artifact handoffs (`SPEC-*.md` and `AI_BASE.md`), agents read only the concise context required for their specific task.
2. **The 80/20 Model Economy:** PXOS routes 90% of raw code execution to fast, cost-effective models (e.g. Gemini Flash / Claude Haiku) operating in isolated worktrees, reserving expensive high-reasoning models (e.g. Claude Sonnet / Gemini Pro) exclusively for initial architecture (`/spec`) and gatekeeper code audits (`/review`).
3. **Zero Git Merge Collisions:** Worktrees physically decouple concurrent agents into isolated filesystem trees (`../trees/feat-*`), guaranteeing that parallel agents never touch each other's uncommitted work.

### Empirical Validation Suite & Reproducibility
PXOS does not rely on hand-waved claims or marketing hyperbole. Every efficiency metric, cost formula, and UX heuristic is evaluated via our open-source empirical benchmark suite:
- **[Benchmark Methodology](./benchmarks/METHODOLOGY.md):** Formal research questions (RQs), control vs. treatment experimental design, mathematical cost functions, and bias mitigation protocols.
- **[Agent Interview & Elicitation Protocol](./benchmarks/AGENT_INTERVIEW_PROTOCOL.md):** Adversarial, anti-sycophantic elicitation prompts and strict JSON schemas to extract unvarnished telemetry from working AI agents.
- **[Automated Analysis Engine (`analyze.py`)](./benchmarks/analyze.py):** Zero-dependency Python 3 engine that parses agent telemetry, computes statistical distributions, and generates audited markdown reports.
- **[Telemetry Server (`server.py`)](./benchmarks/server.py):** Lightweight, zero-dependency ingestion server running at `https://telemetry.madebypx.com` to aggregate anonymous community benchmarks.
- **[Live Telemetry Monitor (`pxos-telemetry-monitor.py`)](./scripts/pxos-telemetry-monitor.py):** Terminal dashboard and CI utility for real-time daemon stability checks and public submission monitoring.
- **[Latest Benchmark Report](./benchmarks/REPORT.md):** Real-world audited telemetry across Tier 1 (micro), Tier 2 (medium), and Tier 3 (complex) engineering tasks.

---

## Product Design & UX as First-Class Citizens

Unlike traditional developer frameworks that treat user interfaces merely as frontend code syntax, PXOS embeds **Product Design, Human-Computer Interaction (HCI), and UX Strategy** directly into the core operating loop.

```
                  ┌─────────────────────────────────────────────────────────┐
                  │                 PRODUCT DESIGN & UX IN PXOS             │
                  └────────────────────────────┬────────────────────────────┘
                                               │
             ┌─────────────────────────────────┼─────────────────────────────────┐
             ▼                                 ▼                                 ▼
   ┌───────────────────┐             ┌───────────────────┐             ┌───────────────────┐
   │    1. DISCOVER    │             │     2. SPEC       │             │    5. REVIEW      │
   │  Macro Research   │             │   User Journey    │             │ Nielsen Heuristics│
   ├───────────────────┤             ├───────────────────┤             ├───────────────────┤
   │ • User Personas   │             │ • Core User Value │             │ • System Status   │
   │ • Mental Models   │             │ • Interactive Flow│             │ • Error Shielding │
   │ • Design Tokens   │             │ • Edge & Empty UI │             │ • Cognitive Load  │
   │ • Benchmark Spikes│             │ • Accessibility   │             │ • Micro-Feedback  │
   └───────────────────┘             └───────────────────┘             └───────────────────┘
```

### 1. Macro UX Grounding (`.ai/research/` & `docs/DESIGN.md`)
Before an agent touches a single line of code, the **Discover phase** mandates reading project research indexed in `.ai/research/INDEX.md` and design language rules in `docs/DESIGN.md`.
- Prevents arbitrary color palettes, random spacings, and ad-hoc CSS utility classes.
- Grounds the agent in the established design system tokens: **Primitive → Semantic → Component**.
- Maintains brand tone of voice and target user mental models across all product screens.

### 2. User-Value & State-Driven Specifications (`/spec`)
In PXOS, an AI is forbidden from writing technical implementation plans until the user experience is formalized. Every task specification (`.ai/specs/SPEC-*.md`) explicitly mandates:
- **Core User Value:** Clear statement of what user friction is eliminated.
- **Interaction & Step-by-Step Flow:** The complete human journey from trigger to resolution.
- **Total State Coverage:** Mandatory modeling of **Empty States**, **Loading Skeletons**, **Validation Feedback**, and **Error Recovery Paths**.
- **Destructive Action Safeguards:** Explicit UI confirmation mechanisms for irreversible operations.

### 3. Automated Nielsen Heuristics in Code Reviews (`/review`)
When a diff touches frontend code, templates, or styles, the gatekeeper Auditor agent evaluates the changes against **Jakob Nielsen's 10 Usability Heuristics**:
- **Visibility of System Status:** Are async operations communicating state via loaders, progress bars, or optimistic UI?
- **Error Prevention & Recovery:** Are form fields validated in real-time? Are error messages human-readable, diagnostic, and actionable?
- **Cognitive Friction Reduction:** Does the layout minimize decision paralysis? Are primary actions unmistakably distinct from secondary actions?

---

## The 6-Phase Disciplined Development Lifecycle

PXOS enforces a deterministic, non-linear operating cycle. AI agents are bounded by these phases and cannot jump ahead without meeting phase completion criteria:

```
   ┌────────────┐      ┌────────────┐      ┌────────────┐
   │  DISCOVER  │ ───► │    PLAN    │ ───► │  EXECUTE   │
   └────────────┘      └────────────┘      └────────────┘
         ▲                                       │
         │                                       ▼
   ┌────────────┐      ┌────────────┐      ┌────────────┐
   │  COMPACT   │ ◄─── │   REVIEW   │ ◄─── │  VALIDATE  │
   └────────────┘      └────────────┘      └────────────┘
```

1. **Discover:** The agent investigates existing patterns, active subsystem audits (`.ai/audits/`), and research invariants (`.ai/research/INDEX.md`). *No code is written.*
2. **Plan:** The agent breaks down the scope, checks whether parallel worktrees are beneficial, maps affected files, and explicitly states how known audit findings (e.g. `SEC-01`, `MEM-03`) are resolved. *Requires human confirmation.*
3. **Execute:** The agent implements code incrementally in small, reversible diffs following local conventions.
4. **Validate:** The agent runs test suites, checks build outputs, verifies edge cases, and confirms acceptance criteria.
5. **Review:** The agent acts as an independent auditor, reviewing the git diff against `main` for overengineering, scope creep, security vulnerabilities, and UX heuristics.
6. **Compact Context:** The agent produces an executive session summary, persists architectural decisions (ADRs) into `DECISION_LOG.md`, updates `SPRINT.md`, and flushes context noise.

### Risk-Based Autonomy Matrix

To eliminate micromanagement while ensuring total security, PXOS establishes clear autonomy tiers:

| Tier | Examples | Execution Rule |
| :--- | :--- | :--- |
| **Low Risk** | Naming improvements, formatting, obvious bug fixes within scope, unit tests, localized documentation | **Autonomous Execution** without blocking for approval |
| **Medium Risk** | Refactoring internal logic, moving files, introducing abstractions, changing component boundaries | **Allowed with explicit reasoning** stated in the prompt |
| **High Risk** | Architectural rewrites, new/replaced dependencies, database schema migrations, security/auth logic, breaking API changes | **Strict Human Approval Required** before proceeding |

---

## Multi-Agent Git Worktree Engine

PXOS v2.0+ features native architecture for **parallel multi-agent execution**. Instead of multiple AI instances stepping on each other's toes in a single workspace, PXOS leverages **Git Worktrees** to provide physical directory and context isolation:

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
                   │   Directory: ../trees/auth│                       │   Directory: ../trees/bill│
                   │   Spec: SPEC-auth.md      │                       │   Spec: SPEC-stripe.md    │
                   └─────────────┬─────────────┘                       └─────────────┬─────────────┘
                                 │                                                   │
                                 └─────────────────────────┬─────────────────────────┘
                                                           ▼
                                             ┌───────────────────────────┐
                                             │    REVIEW / PR GATEWAY    │
                                             │   Role: Auditor / QA      │
                                             │   Model: High-Reasoning 🧠 │
                                             │   Workflow: /review       │
                                             └───────────────────────────┘
```

### Autonomous Provisioning (Zero Terminal Friction)
During the `/plan` workflow, the AI automatically identifies when a feature can be decomposed into independent sub-tasks (e.g. `T-01: feat/auth-oauth` and `T-02: feat/billing-stripe`).

Upon human approval, the AI itself invokes the provisioning helper (`scripts/pxos-task.sh` or `scripts/pxos-task.ps1`), creating the isolated branch, physical directory, and modular task spec without manual git commands.

---

## Architecture & Workspace Structure

When installed, PXOS introduces a clean, standardized `.ai/` operational layer that works alongside any programming language, framework, or toolchain:

```
your-project/
├── .ai/                            # [Core] PXOS Operational Intelligence
│   ├── AI_BASE.md                  # Universal operating contract & concurrency rules
│   ├── PROJECT_CONTEXT.md          # Durable project facts, patterns & architecture
│   ├── DECISION_LOG.md             # Durable Architectural Decision Records (ADRs)
│   ├── CURRENT_SPEC.md             # Active task specification (Single-agent mode)
│   ├── research/                   # Macro domain research, UX benchmarks & spikes
│   │   └── INDEX.md                # Token-efficient research index
│   ├── audits/                     # Subsystem audits (Security, Memory, Debt)
│   │   ├── README.md               # Audit taxonomy and severity guidelines
│   │   └── PARTIAL_<subsystem>.md  # Modular subsystem audit reports
│   └── specs/                      # Modular specifications (Parallel multi-agent mode)
│       ├── TEMPLATE_SPEC.md        # Standardized task spec template
│       ├── SPEC-auth-oauth.md      # Isolated task spec for branch feat/auth-oauth
│       └── SPEC-billing-stripe.md  # Isolated task spec for branch feat/billing-stripe
├── SPRINT.md                       # Active sprint & multi-agent task matrix
├── ROADMAP.md                      # Strategic product roadmap (Human-owned)
├── scripts/                        # Automation & DX helpers
│   ├── pxos-task.sh                # Worktree orchestrator (POSIX Bash)
│   └── pxos-task.ps1               # Worktree orchestrator (PowerShell)
└── docs/                           # Specialized domain knowledge (loaded on demand)
    ├── DESIGN.md                   # Visual identity, tokens & interaction patterns
    ├── DOMAIN_RULES.md             # Business logic & compliance invariants
    ├── DATA_MODEL.md               # Entity relationships & database schemas
    └── GLOSSARY.md                 # Ubiquitous domain terminology
```

### Durable Memory Layer (`DECISION_LOG.md`)
One of the core innovations of PXOS is its **immutable, append-only Architectural Decision Record (ADR) system**. Whenever an architectural or product tradeoff is decided, the agent autonomously formats and appends it to `DECISION_LOG.md`:

```markdown
### ADR-014: Storing Session State in Redis over In-Memory Map
- **Date:** 2026-09-04
- **Author/Agent:** Rodrigo / Agent-Architect
- **Context:** Scaling WebSocket connections across multi-instance pods.
- **Decision:** Use Redis Pub/Sub and session hashing instead of Node.js local maps.
- **Tradeoff / Consequence:** Adds Redis dependency; eliminates memory leak risk on pod reboots.
```

Because `DECISION_LOG.md` is strictly append-only, parallel agents merging their worktrees will never experience merge conflicts on historical decisions.

---

## Workflows & Slash Commands Directory

For AI IDEs and tools supporting slash commands (Antigravity, Cursor, Windsurf, Claude Code, continue.dev), PXOS provides saved workflow prompts in [WORKFLOWS.md](./WORKFLOWS.md):

| Command | Phase | Core Action & Purpose |
| :--- | :--- | :--- |
| **`/start`** | Session Init | Auto-resolves current branch and active modular spec; verifies task scope. |
| **`/spec`** | Discover/Spec | Drafts comprehensive spec with User Value, UX flows, edge cases, and audit alignment. |
| **`/plan`** | Plan | Decomposes task, evaluates worktree parallelization, and checks audit blockers. |
| **`/review`** | Review | Audits diff against base for overengineering, security, and Nielsen UX heuristics. |
| **`/compact`** | Compact | Closes session, records ADRs to `DECISION_LOG.md`, and updates `SPRINT.md`. |
| **`/decision`**| Memory | Immediately registers a durable architectural or product decision into `DECISION_LOG.md`. |
| **`/audit`** | Quality Gate | Acts as Principal Auditor inspecting security, performance, memory leaks, and UX debt. |
| **`/benchmark`** | Research | Measures token efficiency, rework ratio, and UX completeness; autonomously transmits anonymous research telemetry upon consent. |
| **`/install`** | Setup | Automatically detects IDE environment and installs PXOS with appropriate flags. |
| **`/update`**  | Maintenance | Safely upgrades PXOS to the latest version while preserving all custom project facts. |

---

## Quick Installation & IDE Integration

### One-Line Install

Run in the root directory of any project:

**macOS / Linux (Bash):**
```bash
curl -sSL https://raw.githubusercontent.com/madebypx/PXOS/main/install.sh | bash
```

**Windows (PowerShell):**
```powershell
irm https://raw.githubusercontent.com/madebypx/PXOS/main/install.ps1 | iex
```

**Python (PyPI / Global CLI):**
```bash
pip install pxos
pxos init --ide cursor
```

### Safe Upgrade for Existing Projects

To upgrade an existing project to **PXOS v2.2.0** without touching your project context, active specs, or decision logs:

```bash
# Bash
curl -sSL https://raw.githubusercontent.com/madebypx/PXOS/main/install.sh | bash -s -- --update

# PowerShell
& ./install.ps1 -Update

# Python CLI
pxos update
```

*(Alternatively, run `/update` directly inside your AI assistant).*

### Advanced Installation Options

```bash
# Install core + SPRINT.md and ROADMAP.md
curl -sSL https://raw.githubusercontent.com/madebypx/PXOS/main/install.sh | bash -s -- --full

# Windows PowerShell equivalent
& ./install.ps1 -Full -Ide cursor

# Configure specific IDE rules in your workspace
curl -sSL https://raw.githubusercontent.com/madebypx/PXOS/main/install.sh | bash -s -- --ide cursor
curl -sSL https://raw.githubusercontent.com/madebypx/PXOS/main/install.sh | bash -s -- --ide windsurf
curl -sSL https://raw.githubusercontent.com/madebypx/PXOS/main/install.sh | bash -s -- --ide claude
curl -sSL https://raw.githubusercontent.com/madebypx/PXOS/main/install.sh | bash -s -- --ide gemini
curl -sSL https://raw.githubusercontent.com/madebypx/PXOS/main/install.sh | bash -s -- --ide copilot

# Install global system-wide rules across all projects
curl -sSL https://raw.githubusercontent.com/madebypx/PXOS/main/install.sh | bash -s -- --global --ide cursor
```

### IDE Rules Compatibility Matrix

| IDE / Environment | Mode | Configuration Target | Integration Type |
| :--- | :--- | :--- | :--- |
| **Cursor** | Workspace / Global | `.cursor/rules/pxos.mdc` | Native Rule File |
| **Windsurf** | Workspace | `.windsurf/rules/pxos.md` | Native Cascade Rule |
| **Claude Code** | Workspace / Global (`~/.claude/`) | `CLAUDE.md` | Appended / Preserved |
| **Gemini CLI** | Workspace / Global (`~/.gemini/`) | `GEMINI.md` | Appended / Preserved |
| **GitHub Copilot**| Workspace | `.github/copilot-instructions.md` | Appended / Preserved |

---

## Downstream Adoption Badges

If you use PXOS to govern your repository, showcase disciplined AI engineering and link back to the framework by adding an official badge to your `README.md`:

### 1. Governed by PXOS (Standard)
```markdown
[![Governed by PXOS](https://img.shields.io/badge/Governed%20by-PXOS-3b82f6.svg?style=flat-square)](https://github.com/madebypx/PXOS)
```
> Rendered: [![Governed by PXOS](https://img.shields.io/badge/Governed%20by-PXOS-3b82f6.svg?style=flat-square)](https://github.com/madebypx/PXOS)

### 2. Multi-Agent Git Worktrees
```markdown
[![PXOS Multi-Agent](https://img.shields.io/badge/Multi--Agent-Git%20Worktrees-f59e0b.svg?style=flat-square)](https://github.com/madebypx/PXOS)
```
> Rendered: [![PXOS Multi-Agent](https://img.shields.io/badge/Multi--Agent-Git%20Worktrees-f59e0b.svg?style=flat-square)](https://github.com/madebypx/PXOS)

### 3. Token Efficiency Certified
```markdown
[![Context Cost -80%](https://img.shields.io/badge/Context%20Cost--80%25-emerald.svg?style=flat-square)](https://github.com/madebypx/PXOS)
```
> Rendered: [![Context Cost -80%](https://img.shields.io/badge/Context%20Cost--80%25-emerald.svg?style=flat-square)](https://github.com/madebypx/PXOS)

---

## Standard LLM Ingestion (llms.txt)

PXOS strictly adheres to the [`llmstxt.org`](https://llmstxt.org) standard, ensuring AI search agents, IDE plugins, and web crawlers can read the entire operating framework without HTML or web overhead:

- **Root Index:** [`https://raw.githubusercontent.com/madebypx/PXOS/main/llms.txt`](https://raw.githubusercontent.com/madebypx/PXOS/main/llms.txt) — Curated index of core rules, slash commands, and benchmarks.
- **Full Reference:** [`https://raw.githubusercontent.com/madebypx/PXOS/main/llms-full.txt`](https://raw.githubusercontent.com/madebypx/PXOS/main/llms-full.txt) — Token-dense single-file reference for immediate context injection.
- **Generator & Validator:** `python scripts/generate-llms-txt.py --check`


---

## The PXOS Engineering Manifesto

1. **Context is a scarce, high-entropy resource:** Excess context creates hallucination and noise. Load only what is needed for the immediate phase.
2. **Understanding always precedes implementation:** An agent that writes code before understanding the problem produces solutions to the wrong problem.
3. **Simplicity is an engineered outcome, not an accident:** The AI must explicitly evaluate tradeoffs to produce the simplest viable solution.
4. **Autonomy demands strict boundaries:** The Low / Medium / High risk model preserves human strategic control while maximizing AI execution speed.
5. **Product Design & UX are non-negotiable engineering requirements:** Code is useless if the user experience is broken, ambiguous, or visually discordant.
6. **Validation closes the feedback loop:** An unvalidated diff is an incomplete task. The quality bar is defined by verifiable acceptance criteria.

---

## Author & Company Attribution

**PXOS** is engineered and governed by **[PROJECT/X](https://madebypx.com)** (domain: `madebypx.com`), designed by **Rodrigo ([@madebypx](https://github.com/madebypx))** as a universal operational layer for high-velocity software engineering, product design, and autonomous AI development.

- **Company / Studio:** [PROJECT/X](https://madebypx.com)
- **Author & Architect:** Rodrigo ([@rodrigospena](https://github.com/rodrigospena))
- **Repository:** [https://github.com/madebypx/PXOS](https://github.com/madebypx/PXOS)
- **Role in Portfolio:** Flagship Open-Source AI Operating Framework utilized across enterprise, mobile, web, and distributed systems to orchestrate autonomous multi-agent teams with zero regression and maximum token economy.

---

## License

PXOS is published under the [Apache License, Version 2.0 (Apache-2.0)](./LICENSE) by **PROJECT/X**. Free to use, inspect, adapt, modify, and distribute across personal, commercial, and enterprise software development projects with zero licensing fees. PROJECT/X retains all trademark and brand rights.
