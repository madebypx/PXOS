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

