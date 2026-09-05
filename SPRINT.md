# Sprint — v2.3.0 Distribution & Public Indexability

This file tracks the active sprint and coordinates pending roadmap items.
The human defines goals and task assignments. Agents update their specific task status via `/compact`.

---

## Sprint Goal

Maximize global AI crawlability and developer adoption of PXOS through standardized machine-readable documentation (`llms.txt`), cross-platform zero-dependency CLI tooling, and public community distribution.

---

## Task Matrix

| ID | Task | Branch | Spec | Status | Assignee / Agent |
|---|---|---|---|---|---|
| T-01 | AI Indexability Engine, `llms.txt`, PowerShell & Python CLI v2.3.0 | `main` | [.ai/CURRENT_SPEC.md](.ai/CURRENT_SPEC.md) | 🎉 Done | Agent / Rodrigo |
| T-02 | GitHub Tag & Release v2.3.0 (`git tag v2.3.0 && git push --tags`) | `main` | [.ai/CURRENT_SPEC.md](.ai/CURRENT_SPEC.md) | 🎉 Done | Agent / Rodrigo |
| T-03 | PyPI Package Build & Publishing (`.github/workflows/release.yml`, CI/CD) | `main` | [.ai/CURRENT_SPEC.md](.ai/CURRENT_SPEC.md) | 🎉 Done | Agent / Rodrigo |
| T-04 | Deploy `llms.txt` & metadata bundle (`templates/site/public/`) | `main` | [.ai/CURRENT_SPEC.md](.ai/CURRENT_SPEC.md) | 🎉 Done | Agent / Rodrigo |
| T-05 | Public Launch Kit: Formatted posts for HN, Dev.to, Reddit | `main` | [.ai/CURRENT_SPEC.md](.ai/CURRENT_SPEC.md) | 🎉 Done | Rodrigo |
| T-06 | Audit Hardening, Packaging Integrity & Telemetry Reliability | `main` | [.ai/CURRENT_SPEC.md](.ai/CURRENT_SPEC.md) | 🎉 Done | Agent / Rodrigo |

*Statuses: 📝 In Spec | 📋 In Plan / Pending | 🔄 Executing | 🔍 In Review | ✅ Ready for PR | 🎉 Done | ⏸ Blocked*

---

## Blockers & Cross-Task Dependencies

- **T-03 (PyPI):** Automated via GitHub Actions `.github/workflows/release.yml` with Trusted Publishing (OIDC).
- **T-04 (Landing Page):** Deployment bundle ready in `templates/site/public/` awaiting DNS/hosting deployment.

---

## Completed This Sprint

- [x] **T-01** — Implemented `llms.txt` and `llms-full.txt` complying with `llmstxt.org`, created native Windows `install.ps1`, PEP 517/621 `pyproject.toml` and `pxos` Python CLI, downstream badges in `README.md`, GitHub community templates (`.github/`), technical launch whitepaper, and established **PROJECT/X** as the governing company/studio.
- [x] **T-02** — Tagged `v2.3.0` and created official GitHub Release with changelog and attached wheel/sdist packages.
- [x] **T-03** — Built distribution archives, verified with `twine check`, and configured `.github/workflows/release.yml` for continuous PyPI & GitHub release deployment.
- [x] **T-04** — Assembled static SEO, Schema.org JSON-LD, OpenGraph, and crawler bundle in `templates/site/public/` for `pxos.madebypx.com`.
- [x] **T-05** — Published comprehensive `docs/LAUNCH_KIT.md` with tailored submission copy for Hacker News (Show HN), Dev.to, and Reddit.
- [x] **T-06** — Remediated all 9 audit findings from `AUDIT_2026-09-04`: scrubbed `raw_payload` PII storage (`SEC-01`), enclosed SQLite in `try...finally` with connection leak prevention (`REL-01`), added sliding-window rate limiting & proxy checks (`SEC-02`), protected against malformed type conversions (`REL-02`), extracted in-memory record parsing eliminating temp files in `PUBLIC_DIR` (`PERF-01`), bundled templates and scripts in `pxos` package data (`PKG-01`), normalized multi-slash branch specs in `pxos-task` (`REL-03`), gated CI release workflows on tag pushes (`REL-04`), added null safety in benchmark client (`REL-05`), and verified via automated test suite (`tests/test_audit_remediation.py`).

---

## Next Session Priorities

1. **Immediate Next Action:** Execute public community launch on Hacker News (*Show HN*), Dev.to, and Reddit using [`docs/LAUNCH_KIT.md`](docs/LAUNCH_KIT.md).
2. **Web Deployment:** Upload static assets from [`templates/site/public/`](templates/site/public/) to the hosting/CDN provider for `pxos.madebypx.com`.
3. **Future Follow-up:** Monitor community feedback and telemetry ingestion on `telemetry.madebypx.com`, triaging roadmap ideas for v2.4.0.

