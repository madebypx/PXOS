# Architecture Board — Durable Technical Decisions (ADR Summary)
<!-- pxos:canvas:architecture-board -->

> **Notice:** This note is a live projection of `.ai/DECISION_LOG.md`. The local repository log is the Single Source of Truth (SSOT). Key decisions and architectural invariants are automatically summarized here upon `/decision` and `/compact`.

---

## Active Architectural Invariants

- **INV-001:** Repository files remain canonical; canvas notes are projections.
- **INV-002:** Parallel execution requires strict Git worktree or isolated floor isolation.
- **INV-003:** Telemetry and chat reporting must use `--progress` to preserve thread cleanliness.

---

## Decision Log Summary

### YYYY-MM-DD — Initial Architecture Setup
- **Decision:** Adopted PXOS with Maestri Spatial Canvas Bridge.
- **Tradeoffs:** Gained visual canvas visibility; accepted ask-back coordination pattern.
- **Impact:** Project root, `.ai/`, and connected terminals.
- **Status:** Active
