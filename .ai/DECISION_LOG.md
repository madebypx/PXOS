# Decision Log

This file records durable architectural and product decisions (ADRs).
Append only — never delete past entries. If a decision is superseded, mark it as such.
Entries are maintained automatically by AI agents during `/compact` and via `/decision`, or manually by developers.
Only decisions with lasting impact belong here: architectural choices, rejected alternatives, structural shifts, and product invariants.

Multi-Agent Note: Entries are strictly additive and chronological. If a Git merge conflict occurs at the bottom of this file, the resolution rule is always to concatenate both entries without discarding either.

---

## Template

```
## YYYY-MM-DD — [Decision title]

**Decision:**
[What was decided.]

**Context:**
[Why this decision was needed. What problem it solves.]

**Options considered:**
- Option A — [brief description and why it was not chosen]
- Option B — [brief description and why it was not chosen]
- Chosen: Option C — [why this was selected]

**Tradeoffs:**
[What we gain and what we accept as a cost.]

**Impact:**
[What parts of the system are affected.]

**Status:** Active
```

---

<!-- Add decisions below this line, most recent first -->

## 2026-09-04 — Zero-Dependency Telemetry Health & Submissions Monitor

**Decision:**
Implement a pure Python 3 standard library monitoring utility (`scripts/pxos-telemetry-monitor.py`) to poll `https://telemetry.madebypx.com` (`/api/v1/health` and `/api/v1/stats`) for daemon stability, ping latency, and real-time community submission tracking.

**Context:**
Following the deployment of the PXOS empirical research daemon, maintainers and automated pipelines needed a zero-friction mechanism to verify daemon health, check SLA latency thresholds, and monitor incoming benchmark submission counts without direct SSH or database access to production.

**Options considered:**
- Option A — Full APM agent integration (Prometheus client, Datadog): Rejected due to heavy external dependencies violating the PXOS core philosophy of minimal, standalone tooling.
- Option B — Simple curl one-liners in documentation: Rejected because curl does not provide cross-platform parsing, delta calculation, SLA assertions, or structured JSON reporting across Windows and Unix environments.
- Chosen: Option C — Zero-dependency Python standard library CLI with dual output modes (ANSI terminal dashboard with `--watch` and machine-readable `--json` assertions).

**Tradeoffs:**
- Gains: Immediate zero-dependency portability across any machine with Python 3, cross-platform terminal formatting, robust error containment, and CI assertion capability.
- Cost: Relies on client-side polling rather than push-based websockets/SSE.

**Impact:**
Adds `scripts/pxos-telemetry-monitor.py` and documents the monitoring recipes in `WORKFLOWS.md` and `README.md`.

**Status:** Active
