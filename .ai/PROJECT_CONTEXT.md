# Project Context
<!-- pxos:version 2.2.0 -->

This file contains durable, project-specific facts for PXOS development.

---

## Product

**Name:** PXOS

**Summary:**
A minimal, disciplined operating system and governance layer for AI-assisted software engineering, eliminating token waste, cognitive drift, and rework across multi-turn sessions.

**Target user:**
Software engineers, tech leads, and autonomous AI coding agents collaborating across modern IDEs (Cursor, Claude, Gemini/AGY, Windsurf, Copilot).

**Core value:**
Deterministic workflow enforcement (`Discover → Plan → Execute → Validate → Review → Compact`) paired with zero-spoiler specifications, durable ADR logs, and empirical telemetry benchmarking.

---

## Product priorities

In order:

1. Correctness and deterministic workflow enforcement
2. Zero external dependencies for core CLI and daemon tooling (pure Python stdlib, POSIX sh, pwsh)
3. Clarity and human-in-the-loop governance
4. Token economy and context efficiency
5. Backward compatibility across templates and skill definitions

**Anti-priorities — explicitly avoid:**
- Heavy runtime dependencies (avoid Node/pip packages for lightweight core tools)
- Premature abstraction or overly complex telemetry architectures
- Unconsented or opaque data collection (strict privacy and opt-in standards)

---

## Technical stack

**Core & CLI:** Python 3 (stdlib: `urllib`, `sqlite3`, `http.server`, `json`, `argparse`), POSIX Shell (`bash`), PowerShell (`pwsh`).
**Specifications & Governance:** Markdown, YAML frontmatter, Git worktrees.
**Telemetry Server:** Lightweight Python `http.server.ThreadingHTTPServer` backed by SQLite in WAL mode (`benchmarks/server.py`).
**Telemetry Ingestion Endpoint:** `https://telemetry.madebypx.com/api/v1/telemetry`
**Health & Stats Endpoint:** `https://telemetry.madebypx.com/api/v1/health` and `https://telemetry.madebypx.com/api/v1/stats`

---

## Architecture

**Style:** Modular framework, declarative templates, skill-based operational layer, and empirical telemetry subsystem.

**Key patterns:**
- Autonomous Grounding: inspecting `.ai/audits/` and `.ai/research/` before planning.
- Zero-dependency scripts: `scripts/pxos-benchmark.py`, `scripts/pxos-task.sh`, `scripts/pxos-task.ps1`.
- Safe ingestion: payload sanitization, range checks, and PII scrubbing before SQLite storage.

---

## Conventions

- Git commits: Conventional Commits in English (`feat: ...`, `fix: ...`, `chore: ...`).
- Scripts: Python 3 with type hints, POSIX compliance for bash scripts.
- Telemetry: strictly anonymous, numeric metrics and categorical enums only.
