# Current Spec — Task T-13: Public Benchmark Portal & Research Dashboard
<!-- pxos:spec-version 1.0.0 -->

- **Branch:** `main` (or `feat/t13-benchmark-portal`)
- **Status:** 🎉 Done
- **Assignee / Agent:** Agent Flash-1 / Rodrigo Pena
- **Related Issues / Tasks:** `.internal/ROADMAP.md`, `T-08`, `benchmarks/server.py`, `benchmarks/analyze.py`

---

## Goal

Build and deploy an interactive, high-performance public research dashboard at `pxos.madebypx.com/benchmarks` consuming real-time verified Tier A telemetry from `telemetry.madebypx.com/api/v1/stats`, displaying empirical comparisons between LLM coding models (Gemini Flash vs. Claude Sonnet vs. GPT-4o) under the discipline of the PXOS framework.

---

## User Value

- **Developers & Tech Leads:** Make data-driven decisions on model selection and token budgets based on real-world empirical telemetry rather than synthetic benchmarks.
- **AI Research Community:** Access transparent, peer-auditable open datasets with outlier-trimmed medians and IQR filtering.
- **PXOS Framework:** Showcases empirical proof of token cost reduction (-80%) and rework mitigation.

---

## Strategic & Audit Alignment

- **Audit Findings Cross-Check:** Clean — Built directly upon the verified Tier A qualification gating (`[T-08]`), robust statistical aggregations (`analyze.py`), and rate-limited ingestion endpoints.
- **Strategic Blueprint Reference:** Horizon 3 of [`.internal/ROADMAP.md`](.internal/ROADMAP.md).
- **Critical Invariants Adherence:**
  - `INV-001` (Telemetry Privacy): Portal displays strictly aggregated and anonymous metrics (`project_hash`, model name, turn counts); zero proprietary code or unhashed project names are exposed.
  - `INV-002` (Internal Quarantine): Preserved.
  - `INV-003` (Zero External Core Dependencies): Standalone vanilla HTML/CSS/JS or lightweight Chart.js without runtime dependencies on backend CLI.
  - `INV-004` (Conventional Commits): Standard English commit format.
  - `INV-005` (Append-Only Decision Log): Durable ADR recorded.

---

## Scope

### In:
1. **Interactive Dashboard UI (`templates/site/public/benchmarks/index.html`):**
   - Sleek dark-mode aesthetic adhering to PROJECT/X design language (CSS variables, responsive cards, glassmorphic accents).
   - Real-time client-side fetch from `https://telemetry.madebypx.com/api/v1/stats`.
2. **Model Comparison & Efficiency Visualizations:**
   - Token Economy Comparison: Tokens per LOC delivered by model.
   - Rework Ratio & Churn: Median and 5% Trimmed Mean churn comparison.
   - UX Completeness & Utility: Average net utility and state coverage by model.
3. **Interactive Tier Filter:**
   - Default view locked strictly to **Tier A (Verified Rigor, `is_qualified = 1`)**.
   - Option to toggle exploratory data (Tiers B & C) with visual badge demarcation.
4. **Recent Verified Runs Table:**
   - Tabular stream of recent anonymized runs displaying timestamp, model, task domain, LOC touched, rework ratio, and adherence badge.
5. **Open Science Data Export:**
   - One-click export of current benchmark dataset in sanitized JSON and CSV formats.
6. **Backend Server Extension (`benchmarks/server.py`):**
   - Support `?tier=all` vs `?tier=a` filtering.
   - Return model comparison aggregations (`models`) and recent verified runs stream (`recent_runs`).

### Out:
- Authenticated login or administrative mutations (dashboard is 100% public read-only).
- Heavy server-side rendering architectures.

---

## Constraints

- Pure client-side execution running cleanly on GitHub Pages, Cloudflare Pages, or Vercel static hosting.
- Fast load time (< 1.0s) and zero tracking/analytics cookies.
- Zero external core backend dependencies (`INV-003`).

---

## Existing Patterns

- `/api/v1/stats` payload contract in `benchmarks/server.py`.
- Static site assets in `templates/site/public/`.
- Chart rendering patterns in `skills/slides/` and `skills/design/`.

---

## Acceptance Criteria

- [x] `templates/site/public/benchmarks/index.html` renders interactive dashboard matching PROJECT/X design language.
- [x] Connects to `/api/v1/stats` with offline graceful error recovery.
- [x] Visualizes comparative token economy and rework by model.
- [x] Strictly isolates and defaults to Tier A verified data.
- [x] Open data export generates valid JSON and CSV downloads.
- [x] `benchmarks/server.py` `/api/v1/stats` provides models breakdown and recent runs list while maintaining backward compatibility.
- [x] Package data parity maintained via `scripts/sync-package-data.py`.
- [x] Automated tests pass with 100% success rate.

---

## Workflow State

- **Current phase:** Done
- **Pending decision:** None
- **Execution blocked until:** None
