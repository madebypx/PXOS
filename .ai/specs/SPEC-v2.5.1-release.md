# Spec — T-14: v2.5.1 Telemetry API Refinement & UX Metric Filtering

- **Branch:** `main`
- **Status:** 🎉 Done
- **Assignee / Agent:** Agent Flash-1 / Rodrigo Pena
- **Related Issues / Tasks:** T-08, T-13, `.internal/SPRINT.md`, `benchmarks/server.py`, `benchmarks/analyze.py`

---

## Goal

Refine the telemetry backend API (`telemetry.madebypx.com`) and data aggregation to:
1. Filter `mean_ux_state_completeness_pct` in `/api/v1/stats` strictly to UI-touching tasks (`ui_touched = 1`), preventing non-UI tasks (scripts, CLI, backend logic) from distorting UX completeness scores.
2. Add `evaluated_ui_tasks_count` to `/api/v1/stats` summary for transparency.
3. Enrich `recent_runs` in `/api/v1/stats` with `task_description`, `ux_completeness_pct`, and `ui_touched` to power richer live charts and dashboards.
4. Synchronize release version to `2.5.1` across all package metadata, templates, and changelog, and publish GitHub Release `v2.5.1`.

---

## User Value

- **Landing Page & Research Dashboard:** Reflect accurate UX Completeness metrics (matching benchmarked UI tasks) without artificial dilution from backend-only tasks.
- **API Consumers & Community:** Access richer run details directly in the `/api/v1/stats` payload without requiring separate queries or unauthenticated introspection endpoints.
- **Maintainers & Ecosystem:** Continuous zero-drift versioning across package distributions and GitHub releases.

---

## Acceptance Criteria

- [x] `benchmarks/server.py` `/api/v1/stats` computes `mean_ux_state_completeness_pct` filtering by `ui_touched = 1`.
- [x] `evaluated_ui_tasks_count` is included in the summary object.
- [x] `recent_runs` includes `task_description`, `ux_completeness_pct`, and `ui_touched`.
- [x] Backward compatibility preserved for all existing test suites.
- [x] Version bumped to `2.5.1` across `pyproject.toml`, `pxos/__init__.py`, `pxos/cli.py`, `generate-llms-txt.py`, web metadata.
- [x] Package parity verified (`scripts/sync-package-data.py --check`).
- [x] `CHANGELOG.md` updated with `[2.5.1] - 2026-09-07`.
- [x] 60/60 unit tests pass.
- [x] Git committed, tagged `v2.5.1`, pushed to origin, and official GitHub Release published.

---

## Workflow State

- **Current phase:** Done
- **Pending decision:** None
- **Execution blocked until:** None
