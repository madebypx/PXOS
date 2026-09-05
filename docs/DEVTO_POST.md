---
title: Why We Built a Document-Driven OS for AI Coding Agents (and Cut Token Waste by 80%)
published: true
description: How we eliminated AI agent amnesia, prevented merge collisions, and slashed token rework with a zero-dependency in-repo contract.
tags: ai, programming, devtools, opensource
canonical_url: https://pxos.madebypx.com
---

If you’ve spent any serious time coding with frontier LLMs—whether through **Claude 3.7 Sonnet**, **Cursor**, **Windsurf**, **Gemini Code Assist**, or **GitHub Copilot**—you’ve almost certainly hit what our team calls **"The 2-Hour Wall"**.

In the first 30 minutes, the AI feels like a superpower. It scaffolds endpoints, writes utility functions, and fixes tricky CSS bugs with astonishing speed.

Then, around hour two, something subtle breaks down:
1. **Architectural Amnesia:** The model silently swaps a library you agreed to use, rewrites a core abstraction, or casually re-introduces a bug you squashed 45 minutes ago.
2. **Context Degradation & Token Burn:** Every prompt burns tens of thousands of tokens re-explaining the architecture, yet the model's attention window feels fuzzier and hallucination-prone.
3. **Multi-Agent Collision Chaos:** If you run two agents in parallel or switch tasks, they stomp on each other's files, mutate shared configs, and leave you with impossible git merges.
4. **Premature Coding:** The AI writes 250 lines of speculative, over-engineered code before even understanding what problem you actually needed solved.

We realized the bottleneck in AI-assisted software engineering is no longer code generation speed—**it's cognitive drift and workflow governance.**

---

## The Trap: Heavyweight Orchestrators

When developers notice these problems, the industry's default reaction is to add *more software*:
- Heavy Python daemon servers
- External vector databases (RAG)
- Complex agent swarm orchestrators running in Docker containers

We tried this route. It introduced massive runtime friction: background daemons crashing, API keys leaking into third-party servers, and endless configuration debt.

Then we asked a contrarian question:
> **What if AI coding agents don’t need another heavyweight framework? What if all they need is a disciplined, version-controlled operational contract stored directly in the repository?**

That question led us to engineer **[PXOS](https://pxos.madebypx.com)**.

---

## What is PXOS?

**PXOS** is an open-source, document-driven operating system for AI-assisted software engineering. 

It has **zero runtime dependencies** (pure Markdown, POSIX shell, PowerShell, and Python standard library). It lives directly inside your project as a lightweight `.ai/` directory:

```text
your-project/
├── .ai/
│   ├── AI_BASE.md          # Immutable operational rules & autonomy tiers
│   ├── PROJECT_CONTEXT.md  # Stack, architecture, conventions, and invariants
│   ├── CURRENT_SPEC.md     # Active feature spec & acceptance criteria
│   └── DECISION_LOG.md     # Durable architectural decisions (ADRs)
└── ... your actual codebase
```

Instead of relying on volatile chat memory, PXOS establishes an asynchronous, version-controlled communication medium between you and any AI assistant.

---

## 3 Core Principles Behind PXOS

### 1. The 6-Phase Disciplined Lifecycle

Rather than letting an agent immediately vomit code into your files, PXOS forces a deterministic state machine:

```text
Discover ➔ Plan ➔ Execute ➔ Validate ➔ Review ➔ Compact
```

- **Discover:** The agent must inspect `PROJECT_CONTEXT.md` and existing code *before* planning. No blind coding.
- **Plan:** The agent lists which files will change and categorizes risk.
  - *Low Risk (Refactoring, isolated bug fixes):* Agent executes autonomously.
  - *High Risk (Schema migrations, dependency swaps, breaking APIs):* Strictly blocked until explicit human approval.
- **Execute:** Incremental, reversible changes adhering strictly to established patterns.
- **Validate:** Concrete runtime verification (tests, linting, HTTP checks) rather than passive assumptions.
- **Review:** Evaluation against Nielsen's 10 UX heuristics—preventing ugly empty states and broken error recovery.
- **Compact:** At the end of the session, the `/compact` command flushes chat noise, updates the task roadmap, and appends durable Architectural Decision Records (ADRs) to `DECISION_LOG.md`.

### 2. Multi-Agent Concurrency via Git Worktrees

The worst way to run parallel AI agents is on the same working tree or having an orchestrator try to coordinate edits in-memory.

PXOS leverages native Git:
```bash
# Automated multi-agent isolation
pxos task feature/auth-oauth
```
This automatically provisions an isolated **Git Worktree** in a separate directory (`.worktrees/feature-auth-oauth`). Agent A and Agent B work on physically separate files with zero risk of overwriting each other's edits. When ready, changes merge cleanly via standard pull requests.

### 3. Privacy-First: 100% Local, Zero Telemetry in Core

We built PXOS with strict privacy invariants:
- **Zero Network Calls:** Core templates, CLI commands, and rules operate entirely offline.
- **Zero Third-Party APIs:** No external vector DBs, no tracking cookies, no telemetry in the core engine.
- **Permissive Open Source:** Licensed under **Apache 2.0**—completely free for personal, commercial, and enterprise development.

*(Note: We maintain an optional, standalone benchmarking script for developers who want to measure their token economy. It is 100% opt-in, prompts for consent, and sends only anonymous integer token counts with zero code or file names).*

---

## Empirical Benchmarks: Does It Actually Work?

We set up a reproducible benchmarking lab comparing unconstrained AI agents against PXOS-governed agents across 5 identical multi-turn engineering features.

The results surprised even us:

| Metric | Unconstrained Agents | PXOS-Governed Agents | Difference |
|---|---|---|---|
| **Total Tokens Consumed** | 421,450 tokens | 83,120 tokens | **-80.3%** |
| **Architectural Rework Ratio** | 44.1% | **0.0%** | **Eliminated** |
| **Out-of-Bounds Mutations** | 7 files | **0 files** | **Eliminated** |
| **Multi-Agent Collisions** | 3 merge conflicts | **0 (Worktree Isolated)** | **Zero collisions** |

By forcing the agent to read structured context once and keeping context clean via `/compact`, token waste plummets by over 80%.

---

## How to Try PXOS in Your Project

You can install PXOS in any existing repository in under 30 seconds:

### Via Python (PyPI):
```bash
pip install pxos
pxos init
```

### Via Windows PowerShell:
```powershell
irm https://raw.githubusercontent.com/madebypx/PXOS/main/install.ps1 | iex
```

### Via macOS / Linux:
```bash
curl -fsSL https://raw.githubusercontent.com/madebypx/PXOS/main/install.sh | bash
```

Once initialized, open your favorite AI IDE (Cursor, Claude Code, Windsurf, Copilot, or Gemini) and tell the assistant:
> *"Read `.ai/AI_BASE.md` and `.ai/PROJECT_CONTEXT.md` before doing anything."*

Watch how the erratic, chatty agent instantly behaves like a disciplined senior engineering peer.

---

## Open Source & Community

PXOS is an open-source project created by **[PROJECT/X](https://madebypx.com)**:
- 🌐 **Website:** [pxos.madebypx.com](https://pxos.madebypx.com)
- 🐙 **GitHub:** [madebypx/PXOS](https://github.com/madebypx/PXOS)
- 📄 **Empirical Report:** [View Benchmarks](https://github.com/madebypx/PXOS/blob/main/benchmarks/REPORT.md)

### Discussion
How is your team currently handling AI agent drift and token waste? Are you relying on prompt engineering, custom scripts, or external orchestrators? Let’s discuss in the comments below!
