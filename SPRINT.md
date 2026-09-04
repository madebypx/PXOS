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
| T-02 | GitHub Tag & Release v2.3.0 (`git tag v2.3.0 && git push --tags`) | `main` | Roadmap | 📋 Pending Next Session | Human / Agent |
| T-03 | PyPI Package Build & Publishing (`python -m build`, `twine upload`) | `main` | Roadmap | 📋 Pending Next Session | Human / Agent |
| T-04 | Deploy `llms.txt` & metadata to `pxos.madebypx.com` | `main` | [templates/site/metadata.json](templates/site/metadata.json) | 📋 Pending Next Session | Human / Agent |
| T-05 | Public Launch: Post Whitepaper to Hacker News (Show HN), Dev.to, Reddit | `main` | [docs/LAUNCH_WHITEPAPER.md](docs/LAUNCH_WHITEPAPER.md) | 📋 Pending Next Session | Rodrigo |

*Statuses: 📝 In Spec | 📋 In Plan / Pending | 🔄 Executing | 🔍 In Review | ✅ Ready for PR | 🎉 Done | ⏸ Blocked*

---

## Blockers & Cross-Task Dependencies

- **T-03 (PyPI)** requires PyPI maintainer token/credentials for `twine upload`.
- **T-04 (Landing Page)** requires DNS/hosting access to `pxos.madebypx.com`.

---

## Completed This Sprint

- [x] **T-01** — Implemented `llms.txt` and `llms-full.txt` complying with `llmstxt.org`, created native Windows `install.ps1`, PEP 517/621 `pyproject.toml` and `pxos` Python CLI, downstream badges in `README.md`, GitHub community templates (`.github/`), technical launch whitepaper, and established **PROJECT/X** as the governing company/studio.

---

## Next Session Priorities

1. **Immediate Next Action:** Tag and create GitHub Release v2.3.0.
2. **Package Publishing:** Build sdist/wheel and upload to PyPI for `pip install pxos`.
3. **Public Dissemination:** Publish `docs/LAUNCH_WHITEPAPER.md` on technical developer forums.
