# PXOS Release Process & Governance
<!-- pxos:version 2.5.0 -->

This document formalizes the mandatory, repeatable release procedure for all official releases of the **PXOS** framework.

---

## Core Policy: GitHub Releases as Standard Procedure

Every official version of PXOS (major, minor, or patch) **MUST** be published as a formal GitHub Release on [madebypx/PXOS](https://github.com/madebypx/PXOS/releases). 

A version bump is not considered complete or distributed until:
1. An annotated git tag (`vX.Y.Z`) is pushed to `origin/main`.
2. A GitHub Release is created with structured release notes extracted from `CHANGELOG.md`.
3. Verified source distribution (`.tar.gz`) and wheel (`.whl`) archives are attached to the release.
4. The GitHub Actions release pipeline (`.github/workflows/release.yml`) builds and publishes the release to PyPI via Trusted Publishing.

---

## Release Lifecycle Checklist

Follow these exact steps sequentially when preparing and executing a release:

### 1. Pre-Release Verification & Audit Cleanliness
- [ ] Run full automated test matrix:
  ```powershell
  py -m unittest discover tests
  ```
- [ ] Ensure all active audit items in `.ai/audits/` are addressed, with zero unmitigated P0 (Blocker) or P1 (Critical) defects.
- [ ] Ensure critical invariants (`INV-001` through `INV-005` in `.ai/PROJECT_CONTEXT.md`) are strictly respected.
- [ ] Ensure `.internal/` contains all internal drafts, launch kits, and sprint tracking without leaking into public directories (`INV-002`).

### 2. Version Synchronization
Update the semantic version string (`X.Y.Z`) across all canonical metadata locations:
- [ ] `pyproject.toml` (`[project] version = "X.Y.Z"`)
- [ ] `pxos/__init__.py` (`__version__ = "X.Y.Z"`)
- [ ] `pxos/cli.py` (`VERSION = "X.Y.Z"`)
- [ ] `install.sh` (`PXOS_VERSION="X.Y.Z"`)
- [ ] `install.ps1` (`$PXOS_VERSION = "X.Y.Z"`)
- [ ] `scripts/generate-llms-txt.py` (`VERSION = "X.Y.Z"`)
- [ ] `README.md` (version shield badge and upgrade instructions)
- [ ] `WORKFLOWS.md` (upgrade section version references)
- [ ] `skills/update/SKILL.md` (upgrade instructions)
- [ ] `.ai/AI_BASE.md` and `templates/rules/pxos.md` (`<!-- pxos:version X.Y.Z -->`)
- [ ] `.ai/PROJECT_CONTEXT.md` (`<!-- pxos:version X.Y.Z -->`)
- [ ] `templates/site/metadata.json` and `templates/site/public/head-tags.html` (`softwareVersion`)

### 3. Package Parity & Crawler Regeneration
- [ ] Mirror updated templates and scripts into packaged directories:
  ```powershell
  py scripts/sync-package-data.py
  ```
- [ ] Verify byte-for-byte package parity:
  ```powershell
  py scripts/sync-package-data.py --check
  ```
- [ ] Regenerate `llms.txt` and `llms-full.txt`:
  ```powershell
  py scripts/generate-llms-txt.py
  ```
- [ ] Verify AI crawler references:
  ```powershell
  py scripts/generate-llms-txt.py --check
  ```

### 4. Test Suite Adaptation
- [ ] Update version assertions in `tests/test_audit_remediation.py` (`test_doc_01_version_and_invariants_consistency`).
- [ ] Re-run all tests to guarantee 100% pass:
  ```powershell
  py -m unittest discover tests
  ```

### 5. Changelog Documentation
- [ ] Append new version entry `## [X.Y.Z] - YYYY-MM-DD` at the top of `CHANGELOG.md` following [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format.
- [ ] Group items cleanly under `### Added`, `### Changed`, `### Fixed`, and `### Security`.

### 6. Local Packaging Validation
- [ ] Clean previous artifacts:
  ```powershell
  Remove-Item -Recurse -Force dist, *.egg-info
  ```
- [ ] Build source distribution and wheel:
  ```powershell
  py -m build
  ```
- [ ] Validate distribution archives with `twine`:
  ```powershell
  py -m twine check dist/*
  ```

### 7. Git Commit & Tagging
- [ ] Commit version changes with Conventional Commits message:
  ```bash
  git add .
  git commit -m "chore(release): bump version to X.Y.Z and prepare release"
  ```
- [ ] Create annotated git tag:
  ```bash
  git tag -a vX.Y.Z -m "release: vX.Y.Z - <summary of release>"
  ```
- [ ] Push branch and tag to GitHub:
  ```bash
  git push origin main
  git push origin vX.Y.Z
  ```

### 8. GitHub Release Creation
- [ ] Publish the release using GitHub CLI (`gh`):
  ```bash
  gh release create vX.Y.Z dist/* \
    --title "vX.Y.Z — <Release Title>" \
    --notes-file RELEASE_NOTES.md
  ```
- [ ] Verify release exists on [GitHub Releases](https://github.com/madebypx/PXOS/releases).

### 9. Post-Release Verification
- [ ] Verify GitHub Actions workflow `.github/workflows/release.yml` completes successfully.
- [ ] Verify publication on PyPI: `https://pypi.org/project/pxos/`
- [ ] Test clean installation in an isolated virtual environment:
  ```powershell
  pip install --no-cache-dir --upgrade pxos
  pxos --version
  ```
