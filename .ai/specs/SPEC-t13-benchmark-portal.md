# Spec — T-13: Public Benchmark Portal & Research Dashboard (pxos.madebypx.com/benchmarks)

- **Branch:** `feat/t13-benchmark-portal` (or `main`)
- **Status:** In Spec
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
- **Strategic Blueprint Reference:** Horizon 3 of [`.internal/ROADMAP.md`](../../.internal/ROADMAP.md).
- **Critical Invariants Adherence:**
  - `INV-001` (Telemetry Privacy): Portal displays strictly aggregated and anonymous metrics (`project_hash`, model name, turn counts); zero proprietary code or unhashed project names are exposed.
  - `INV-002` (Internal Quarantine): Preserved.
  - `INV-003` (Zero External Core Dependencies): Standalone vanilla HTML/CSS/JS or lightweight Chart.js without runtime dependencies on backend CLI.

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

### Out:
- Authenticated login or administrative mutations (dashboard is 100% public read-only).
- Heavy server-side rendering architectures.

---

## Constraints

- Pure client-side execution running cleanly on GitHub Pages, Cloudflare Pages, or Vercel static hosting.
- Fast load time (< 1.0s) and zero tracking/analytics cookies.

---

## Existing Patterns

- `/api/v1/stats` payload contract in `benchmarks/server.py`.
- Static site assets in `templates/site/public/`.
- Chart rendering patterns in `skills/slides/` and `skills/design/`.

---

## Proposed Change

1. **`templates/site/public/benchmarks/index.html`:**
   - Semantic HTML5 structure with responsive grid for metric KPI cards and interactive charts.
2. **`templates/site/public/benchmarks/dashboard.js`:**
   - Fetch client for `telemetry.madebypx.com/api/v1/stats` with fallback handling and Chart.js rendering.
3. **`templates/site/public/benchmarks/dashboard.css`:**
   - Modern dark-theme stylesheet with micro-animations and typography from Inter.
4. **`templates/site/public/robots.txt` & `sitemap.xml`:**
   - Index `/benchmarks` for search engines and AI crawlers.
5. **Tests:**
   - Unit tests verifying JSON schema validation and mock fetch handling.

---

## Technical Flow

```
1. User navigates to pxos.madebypx.com/benchmarks
2. Dashboard fetches https://telemetry.madebypx.com/api/v1/stats
3. Client renders:
   ├── KPI Cards (Total Verified Runs, Median Token Cost, Average Rework)
   ├── Model Comparison Bar Chart (Tokens/LOC: Gemini Flash vs Claude 3.7 vs GPT-4o)
   ├── Churn Distribution (Median vs 5% Trimmed Mean)
   └── Live Stream of Anonymized Verified Runs (Tier A)
4. User clicks "Download Dataset" -> Generates clean sanitized CSV/JSON
```

---

## Acceptance Criteria

- [ ] `templates/site/public/benchmarks/index.html` renders interactive dashboard matching PROJECT/X design language.
- [ ] Connects to `/api/v1/stats` with offline graceful error recovery.
- [ ] Visualizes comparative token economy and rework by model.
- [ ] Strictly isolates and defaults to Tier A verified data.
- [ ] Open data export generates valid JSON and CSV downloads.

---

## Validation Plan

1. Local testing against mock server (`benchmarks/server.py`).
2. Verification across viewport sizes (mobile, tablet, desktop).
3. Lighthouse performance and accessibility audit (> 95 score).
