# PXOS Public Launch Kit & Content Syndication

This document contains publication-ready copy, submission titles, and introductory narratives formatted for premier developer platforms.

---

## 1. Hacker News (Show HN)

### Submission Details
- **Title:** `Show HN: PXOS – A document-driven OS for AI coding agents that cuts token waste by 80%`
- **URL:** `https://github.com/madebypx/PXOS`

### Founder First Comment (Post immediately after submitting)

```markdown
Hi HN! We’re the team at PROJECT/X, and today we’re releasing PXOS: a minimal, zero-dependency operating system and governance layer for AI-assisted software engineering.

GitHub: https://github.com/madebypx/PXOS
Whitepaper: https://github.com/madebypx/PXOS/blob/main/docs/LAUNCH_WHITEPAPER.md
Empirical Benchmarks: https://github.com/madebypx/PXOS/blob/main/benchmarks/REPORT.md
LLM Reference: https://raw.githubusercontent.com/madebypx/PXOS/main/llms.txt

### The Problem
If you’ve used Claude 3.7 Sonnet, Gemini Pro, GPT-4o, or Cursor on a real codebase for more than a few sessions, you’ve likely seen the breakdown:
1. Architectural Amnesia: The model silently replaces established patterns, swaps libraries, or reintroduces bugs you solved days ago.
2. Conversational Token Hemorrhage: You burn tens of thousands of tokens re-explaining the system architecture on every turn.
3. Multi-Agent Git Collisions: Parallel agents on the same branch stomp each other’s files and produce nasty merge conflicts.
4. Premature Coding: Agents generate hundreds of lines of plausible-looking code before even understanding what problem they were supposed to solve.

### What is PXOS?
PXOS is NOT another heavyweight Python framework, vector DB, or agent swarm server. It has zero runtime dependencies. It’s an operational contract stored directly in your repository (`.ai/`) that governs how any AI agent (Cursor, Claude Code, AGY, Copilot, Windsurf) behaves.

It enforces a deterministic 6-phase state machine:
Discover → Plan → Execute → Validate → Review → Compact

- Discover: The agent reads durable project context and constraints before touching a line of code.
- Plan: The agent specifies affected files and surfaces risks. If the task is complex, it automatically provisions parallel git worktrees so agents never collide on disk.
- Execute: Autonomy tiers dictate what can be done automatically (refactoring, isolated bug fixes) vs. what strictly requires human sign-off (schema migrations, dependency additions).
- Validate: Concrete runtime evidence before declaring done.
- Review: Automated evaluation against Nielsen's 10 UX heuristics.
- Compact: At the end of the session, durable decisions are appended as ADRs to DECISION_LOG.md and context is compacted.

### Empirical Benchmarks
We built an open-source benchmarking lab (in `benchmarks/`) comparing unconstrained agents vs. PXOS-governed agents across 5 identical multi-turn features:
- 80.3% reduction in token consumption (from 421k tokens down to 83k tokens per multi-turn session).
- Rework ratio dropped from 44% down to 0% (zero regressions or rewritten architectural files).
- Multi-agent collisions eliminated via git worktree branch isolation.

### Installation
You can try PXOS in any project right now:

Python (PyPI):
pip install pxos
pxos init

Windows (PowerShell):
irm https://raw.githubusercontent.com/madebypx/PXOS/main/install.ps1 | iex

macOS / Linux:
curl -fsSL https://raw.githubusercontent.com/madebypx/PXOS/main/install.sh | bash

We’d love to hear how you manage agent drift and what workflows have worked best for your team. All feedback and critiques are welcome!
```

---

## 2. Dev.to / Hashnode / Medium

### Article Frontmatter & Metadata
- **Title:** Why We Built a Document-Driven Operating System for AI Coding Agents (and Cut Token Waste by 80%)
- **Tags:** `#ai`, `#programming`, `#opensource`, `#devtools`
- **Canonical URL:** `https://pxos.madebypx.com`

*(Body text is located in [`docs/LAUNCH_WHITEPAPER.md`](./LAUNCH_WHITEPAPER.md) — ready to paste verbatim).*

---

## 3. Reddit

### Community: `r/programming`

**Title:** *Why We Built a Document-Driven Operating System for AI Coding Agents (and Cut Token Waste by 80%)*

**Body:**
```markdown
Over the past 6 months, we observed a consistent pattern across our teams using AI coding tools (Claude Code, Cursor, Copilot, AGY): the bottleneck is no longer code generation speed—it's cognitive drift and token waste.

An LLM is essentially a brilliant senior engineer with a severe working memory deficit. If you let it free-wheel in a chat loop, it forgets architectural invariants, rewrites working components, and burns 400k+ tokens on circular conversations.

Instead of writing another complex Python agent orchestrator, we built **PXOS**: an in-repo, document-driven governance layer with zero external dependencies.

How it works:
1. Version-controlled Markdown artifacts in `.ai/` (`AI_BASE.md`, `PROJECT_CONTEXT.md`, `DECISION_LOG.md`, `CURRENT_SPEC.md`).
2. A strict 6-phase lifecycle: Discover → Plan → Execute → Validate → Review → Compact.
3. Multi-agent concurrency via standard `git worktrees`—independent agents work in physically isolated directories, preventing merge conflicts.
4. Autonomy rules: strict classification of Low, Medium, and High-risk actions (e.g. schema changes require explicit human approval).

We ran rigorous empirical benchmarks comparing unconstrained agents vs. PXOS agents across identical tasks:
- Total Tokens: 421,450 (Unconstrained) vs. 83,120 (PXOS) — **80.3% reduction**
- Rework Ratio: 44.1% vs. **0.0%**
- Out-of-bounds file mutations: 7 vs. **0**

The project is published under the Business Source License 1.1 (BSL-1.1 by PROJECT/X) and is completely free for personal, internal, and commercial development use. Check out the repository, benchmarks, and installers:
GitHub: https://github.com/madebypx/PXOS
Laboratory Report: https://github.com/madebypx/PXOS/blob/main/benchmarks/REPORT.md

Would love your thoughts on how your teams are structuring human-in-the-loop AI workflows.
```

---

### Community: `r/LocalLLaMA`

**Title:** *Open-source framework to stop agent token rot: benchmarks show 80% reduction using document-driven state machines*

**Body:**
```markdown
Hey r/LocalLLaMA,

One of the biggest issues when running local coding agents or large frontier models in multi-turn sessions is "context rot"—as conversational history grows, models hallucinate past invariants, re-read files repeatedly, and degrade rapidly in reasoning quality.

We published PXOS (an open-source framework and CLI) designed around a strict 6-phase state machine: Discover → Plan → Execute → Validate → Review → Compact.

Key highlights for local & self-hosted workflows:
- Zero runtime dependencies: pure standard library Python, POSIX sh, pwsh.
- Includes `/compact` protocol: flushes context noise, summarizes progress, and appends ADRs to `.ai/DECISION_LOG.md` before memory degradation hits.
- Standardized `llms.txt` and `llms-full.txt` (following `llmstxt.org`) for zero-overhead agent ingestion.
- Built-in empirical benchmarking tool (`pxos benchmark`) to measure token expenditure, rework ratio, and task efficiency across different models.

Repo: https://github.com/madebypx/PXOS
Empirical Data: https://github.com/madebypx/PXOS/blob/main/benchmarks/REPORT.md

Try it:
`pip install pxos && pxos init`
```

---

### Community: `r/ChatGPTCoding`

**Title:** *Stop letting Cursor / Claude Code rewrite your architecture: PXOS (open source framework for deterministic agent pairing)*

**Body:**
```markdown
If you use Cursor (`.cursorrules`) or Claude Code (`CLAUDE.md`), you know the frustration of an agent casually refactoring files it was never supposed to touch or inventing new state management libraries halfway through a session.

We built PXOS to turn erratic AI agents into disciplined senior engineering partners:
- Multi-tier governance: Low risk (auto-approved), Medium risk (needs reasoning), High risk (strictly requires human sign-off).
- Pre-execution planning: The agent drafts an implementation spec and plan before writing any code.
- Auto-worktree provisioning: Spawns clean `git worktrees` for parallel agent branches so agents don't overwrite each other.
- One-liner setup:
  - PowerShell: `irm https://raw.githubusercontent.com/madebypx/PXOS/main/install.ps1 | iex`
  - Linux/macOS: `curl -fsSL https://raw.githubusercontent.com/madebypx/PXOS/main/install.sh | bash`
  - PyPI: `pip install pxos && pxos init`

GitHub: https://github.com/madebypx/PXOS
Check it out and let us know what you think!
```
