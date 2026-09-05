# Current Spec — Release Engineering, Automated PyPI Publishing & Public Launch v2.3.0
<!-- pxos:version 2.2.0 -->

This file defines the active task or feature. Replace it entirely when starting a new task. The AI reads this file at the start of every session to understand what is being built.

---

## Goal

Execute the release engineering cycle for PXOS v2.3.0 across all distribution channels: tag the repository, generate GitHub release assets, build and validate the PyPI package with an automated CI/CD publishing pipeline (`.github/workflows/release.yml`), assemble static deployment assets for `pxos.madebypx.com`, and package the multi-platform launch kit for technical developer communities (Hacker News, Dev.to, Reddit).

---

## User value

- **Seamless Installation:** Developers can install PXOS via `pip install pxos` without compiling from source or cloning the repository.
- **Auditable Versioning:** Releases and git tags follow strict Semantic Versioning (`v2.3.0`) with cryptographically traceable releases and automated changelog generation on GitHub.
- **Continuous Distribution:** Future releases can publish to PyPI and GitHub Releases automatically upon pushing signed tags via GitHub Actions OIDC / Trusted Publishing.
- **Web & SEO Indexing:** The public domain `pxos.madebypx.com` receives validated metadata, JSON-LD, `llms.txt`, and robots directives for immediate crawler ingestion.
- **High-Impact Public Launch:** Ready-to-use launch drafts allow the author to syndicate the technical whitepaper across developer communities with zero friction.

---

## Strategic & Audit Alignment

- **Audit Findings Cross-Check:** Clean — No active audit blockers touching this scope.
- **Strategic / Research Reference:** Fulfills tasks T-02 through T-05 of `SPRINT.md` v2.3.0 and complies with PXOS core priorities (Zero Runtime Dependencies, Correctness, Deterministic Workflows).

---

## Scope

**In:**
1. **Task T-02 — Release Engineering & Git Tagging:**
   - Create and push annotated tag `v2.3.0`.
   - Draft comprehensive GitHub Release notes using `gh release create` matching `CHANGELOG.md` v2.3.0.
2. **Task T-03 — PyPI Package Build & CI/CD Pipeline:**
   - Validate local distribution artifact generation (`sdist` and `wheel`) in `dist/`.
   - Validate packaging metadata (`twine check dist/*` or internal integrity check).
   - Create `.github/workflows/release.yml` with GitHub Actions for automated build, release asset upload, and PyPI publishing via Trusted Publishing.
3. **Task T-04 — Web Deployment Bundle (`pxos.madebypx.com`):**
   - Package ready-to-deploy static assets (`llms.txt`, `llms-full.txt`, `robots.txt`, and HTML metadata snippet) matching `templates/site/metadata.json`.
   - Provide zero-dependency verification and sync instructions.
4. **Task T-05 — Multi-Platform Public Launch Kit:**
   - Create `docs/LAUNCH_KIT.md` containing formatted launch posts for:
     - **Hacker News:** Show HN title, URL, and founder intro comment.
     - **Dev.to / Hashnode / Medium:** Article markdown with frontmatter and cross-post canonical link.
     - **Reddit:** Tailored posts for `r/programming`, `r/LocalLLaMA`, and `r/ChatGPTCoding`.

**Out:**
- Adding third-party runtime dependencies to `pxos` package.
- Direct DNS record modifications (hosting credentials are kept private to the human).
- Automated live social media posting (human reviews and posts).

---

## Constraints

- Zero runtime dependencies for the Python package (`dependencies = []` in `pyproject.toml`).
- Use GitHub CLI (`gh`) for release automation since credentials and scopes are already active.
- CI/CD workflow must use standard, audited GitHub Actions (`actions/checkout`, `actions/setup-python`, `pypa/gh-action-pypi-publish`).

---

## Existing patterns

- `pyproject.toml`: standard PEP 517/621 setuptools configuration with entry point `pxos = pxos.cli:main`.
- `CHANGELOG.md`: structured Keep a Changelog entries for `[2.3.0]`.
- `templates/site/metadata.json`: specification for JSON-LD, OpenGraph, and `robots.txt`.
- `docs/LAUNCH_WHITEPAPER.md`: established technical narrative and benchmark data.

---

## Proposed change

1. **GitHub Actions Release Workflow:**
   - Create `.github/workflows/release.yml` triggering on `push: tags: ['v*']`.
   - Jobs:
     - Build `sdist` and `wheel`.
     - Create GitHub Release with `softprops/action-gh-release` attaching release notes and distribution packages.
     - Publish to PyPI via `pypa/gh-action-pypi-publish` (optional / gated on environment secrets).
2. **Local Packaging Validation:**
   - Build package locally using `pip wheel` / `build` to verify wheel/sdist contents.
   - Verify `pxos --help` installs cleanly in a clean virtual environment.
3. **Git Tagging & Release Execution:**
   - Tag `v2.3.0` and create release via `gh release create v2.3.0 --title "v2.3.0 — AI Indexability & Zero-Friction Distribution Engine" --notes-file ...`.
4. **Web Bundle Preparation:**
   - Generate static assets for `pxos.madebypx.com` in `templates/site/public/` (`robots.txt`, `index.html` head snippet, `llms.txt`, `llms-full.txt`).
5. **Launch Kit Compilation:**
   - Create `docs/LAUNCH_KIT.md` with copy-paste community submissions.
6. **Sprint Tracking:**
   - Update `SPRINT.md` with active status changes.

---

## User flow / Technical flow

```
[Local Build & Validation]
        │
        ▼
[Commit & Push Tag v2.3.0] ──► [GitHub Actions Release Pipeline]
        │                                 │
        ▼                                 ▼
[GH Release Created]              [PyPI Package Published]
        │
        ▼
[Export Web Assets for Site]
        │
        ▼
[Human Uses Launch Kit for HN/Reddit/Dev.to]
```

---

## Edge cases

- **Tag collision:** Verify `git tag -l v2.3.0` before tagging (confirmed empty).
- **PyPI credentials:** GitHub Actions workflow should support both OIDC Trusted Publishing (preferred, tokenless) and API token fallback via GitHub Secrets (`PYPI_API_TOKEN`).
- **Wheel completeness:** Ensure package data (`pxos/` files) and CLI entry point are properly packaged in the wheel without missing modules.

---

## Acceptance criteria

- [x] `.github/workflows/release.yml` created and validated for GitHub Actions syntax.
- [x] Local build generates valid `sdist` (`.tar.gz`) and `wheel` (`.whl`) without warnings (twine passed).
- [x] CLI runs correctly from built package (`pxos --version` / `pxos --help`).
- [x] Git tag `v2.3.0` created and pushed to `origin`.
- [x] GitHub Release v2.3.0 published via `gh release create` with attached release notes and package assets.
- [x] Web asset bundle in `templates/site/public/` ready for immediate upload to `pxos.madebypx.com`.
- [x] `docs/LAUNCH_KIT.md` published with tailored copy for Hacker News, Dev.to, and Reddit.
- [x] `SPRINT.md` updated with completed statuses.

---

## Validation plan

1. **Package integrity:** `python -m pip install dist/*.whl` into a temporary environment and test `pxos --version` and `pxos init --help`. (Passed)
2. **Workflow validation:** Validate `.github/workflows/release.yml` with YAML linter. (Passed)
3. **GitHub release verification:** Run `gh release view v2.3.0` to confirm live publication on GitHub. (Passed)
4. **Site asset validation:** Verify `robots.txt` and `templates/site/public/` files against `templates/site/metadata.json`. (Passed)

---

## Risks & Cross-Task Dependencies

- **PyPI Namespace Reservation:** Handled via GitHub Actions workflow and manual fallback.
- **Host Deployment for Site:** Static bundle in `templates/site/public/` ready for CDN push.

---

## Workflow state

- **Current phase:** Done
- **Pending decision:** None
- **Execution blocked until:** None

