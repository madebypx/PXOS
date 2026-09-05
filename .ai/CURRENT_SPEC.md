# Spec — T-07: v2.3.1 Patch Release & Distribution Validation

- **Branch:** `main`
- **Status:** `🎉 Done`
- **Assignee / Agent:** `Agent / Rodrigo`
- **Related Issues / Tasks:** `.ai/audits/AUDIT_2026-09-04.md`, `T-06`, `.github/workflows/release.yml`

---

## Goal

Publish the official `v2.3.1` patch release across GitHub and PyPI, ensuring that all 9 critical and major audit remediations from `T-06` (including package data bundling, telemetry connection leak prevention, PII scrubbing, rate limiting, and worktree branch normalization) are propagated to global package distributions, installer scripts, and public AI crawler indices.

---

## User value

- **Immediate PyPI Integrity:** Developers installing via `pip install --upgrade pxos` receive the bundled helper scripts and offline templates (`PKG-01`), preventing runtime crashes when executing `pxos benchmark` or `pxos init`.
- **Audited Production Stability:** Downstream adopters and server operators run fully hardened telemetry ingestion (`SEC-01`, `REL-01`, `SEC-02`, `REL-02`) with zero database descriptor leaks and active rate limiting.
- **Accurate Tooling & Metadata:** All installer scripts (`install.sh`, `install.ps1`), AI index files (`llms.txt`, `llms-full.txt`), and documentation badges accurately reflect version `2.3.1`.

---

## Strategic & Audit Alignment

- **Audit Findings Distributed:** Directly packages and publishes the remediations for all 9 findings documented in [.ai/audits/AUDIT_2026-09-04.md](.ai/audits/AUDIT_2026-09-04.md):
  - `[PKG-01]` (P1): Packages `pxos/templates/` and `pxos/scripts/` into the PyPI wheel so CLI commands work out of the box.
  - `[REL-01]` (P1): Eliminates SQLite connection leaks and unhandled exceptions in `benchmarks/server.py`.
  - `[SEC-01]` (P1): Prevents unscrubbed PII/payload storage in SQLite submissions table.
  - `[SEC-02]` (P2): Activates in-memory sliding-window IP rate limiting and proxy IP verification.
  - `[REL-02]` (P2): Protects telemetry metric sanitization against malformed input types.
  - `[PERF-01]` (P2): Removes temporary file disk thrashing during daily telemetry aggregation.
  - `[REL-03]` (P2): Normalizes multi-slash branch names in worktree spec generation.
  - `[REL-04]` (P3): Enforces release workflow trigger safety (`refs/tags/v*` gating).
  - `[REL-05]` (P3): Handles null JSON values safely in benchmark CLI client.
- **Architectural Invariants:** Preserves pure standard library design, zero external runtime dependencies, and English Conventional Commits standard.

---

## Scope

**In:**
1. **Version Synchronization:**
   - Update `pyproject.toml` version: `2.3.0` → `2.3.1`.
   - Update `pxos/__init__.py`: `__version__ = "2.3.1"`.
   - Update `pxos/cli.py`: `VERSION = "2.3.1"`.
   - Update `install.sh` and `install.ps1`: `2.3.0` → `2.3.1`.
   - Update `README.md` version badge.
   - Run `python scripts/generate-llms-txt.py` to synchronize `llms.txt`, `llms-full.txt`, and templates.
   - Update `templates/site/metadata.json`, `templates/site/public/head-tags.html`, and `pxos/templates/site/...`.
2. **Changelog & Documentation:**
   - Document `## [2.3.1] - 2026-09-04` in `CHANGELOG.md` detailing audit hardening, security fixes, and packaging updates.
3. **Sprint Tracking:**
   - Register task `T-07` in `SPRINT.md`.
4. **Git Operations & Release Triggering:**
   - Push commit `ed973c1` and release bump commit to `origin/main`.
   - Create annotated tag `v2.3.1` (`git tag -a v2.3.1 -m "release: v2.3.1 - audit hardening and packaging integrity"`).
   - Push tag `git push origin v2.3.1`, triggering GitHub Actions workflow `.github/workflows/release.yml` (PyPI Trusted Publishing + GitHub Release).
5. **Distribution Validation:**
   - Build local wheel and sdist with `python -m build`.
   - Verify package contents (`tar -tf` / `unzip -l`) to confirm `scripts/` and `templates/` inclusion in the `v2.3.1` distribution archive.

**Out:**
- Functional code rewrites outside version strings and release metadata.
- Launching public community posts on HN/Dev.to/Reddit (reserved for follow-up syndication session).

---

## Constraints

- Strictly follow Semantic Versioning (`PATCH` release for backwards-compatible bug and audit fixes).
- Maintain Conventional Commits in English (`chore(release): bump version to 2.3.1`).
- Ensure `release.yml` runs smoothly against the tagged commit.

---

## Existing patterns

- Version declarations in `pyproject.toml`, `pxos/__init__.py`, `pxos/cli.py`.
- Automated AI index generation via `scripts/generate-llms-txt.py`.
- Keep a Changelog standard in `CHANGELOG.md`.

---

## Proposed change

1. **Modify `pyproject.toml`:**
   ```toml
   version = "2.3.1"
   ```
2. **Modify `pxos/__init__.py` & `pxos/cli.py`:**
   Set `__version__ = "2.3.1"` and `VERSION = "2.3.1"`.
3. **Modify `install.sh` & `install.ps1`:**
   Set default version variable to `"2.3.1"`.
4. **Modify `CHANGELOG.md`:**
   Insert `## [2.3.1] - 2026-09-04` section detailing Fixed and Changed items from audit remediation.
5. **Execute `python scripts/generate-llms-txt.py`:**
   Refreshes machine-readable files with new version stamp.
6. **Update `SPRINT.md`:**
   Add task `T-07` row and description.
7. **Commit, Tag & Push:**
   Push to GitHub and publish tag `v2.3.1`.

---

## Technical flow

```
[Spec T-07 Approved] ──► [Run /plan] ──► [Implementation Plan Confirmed]
                                                   │
                                                   ▼
                                    [Execute Version Bump & Sync]
                                    ├─ Bump pyproject.toml, pxos/, installers
                                    ├─ Update CHANGELOG.md & SPRINT.md
                                    └─ Regenerate llms.txt via script
                                                   │
                                                   ▼
                                        [Validate Package Build]
                                        ├─ Build wheel & inspect archive
                                        └─ Run audit tests on new build
                                                   │
                                                   ▼
                                          [Push & Tag v2.3.1]
                                        ├─ git push origin main
                                        ├─ git tag -a v2.3.1 -m "..."
                                        └─ git push origin v2.3.1
                                                   │
                                                   ▼
                                       [CI/CD Release Triggered]
                                       ├─ PyPI Trusted Publishing
                                       └─ GitHub Release with assets
```

---

## Edge cases

- **Git Remote Authentication / Permissions:** Handled by standard SSH/HTTPS git credentials configured in the environment.
- **PyPI Release Overwrite:** PyPI rejects re-uploading existing versions; bumping to `2.3.1` ensures a clean, rejected-free deployment.
- **Tag Collision:** Verifying `git tag -l v2.3.1` confirms the tag does not already exist.

---

## Acceptance criteria

- [x] `pyproject.toml`, `pxos/__init__.py`, `pxos/cli.py`, `install.sh`, and `install.ps1` reflect version `2.3.1`.
- [x] `CHANGELOG.md` includes comprehensive release notes under `## [2.3.1] - 2026-09-04`.
- [x] `llms.txt` and `llms-full.txt` reflect version `2.3.1`.
- [x] `SPRINT.md` records task `T-07` with current tracking.
- [x] Built wheel archive contains `pxos/scripts/` and `pxos/templates/`.
- [x] All commits are pushed to `origin/main` and tag `v2.3.1` is published to `origin`.

---

## Validation plan

1. **Local Build & Archive Inspection:**
   Run `python -m build` and inspect wheel contents to verify `2.3.1` version and bundled assets.
2. **Automated Test Suite:**
   Run `pytest tests/test_audit_remediation.py` to confirm all remediations pass under the updated version.
3. **Git Tag Verification:**
   Verify `git describe --tags` and `git status` clean before push.

---

## Risks & Cross-Task Dependencies

- **Low Risk:** Patch release consists strictly of audit fixes and version metadata without breaking API changes.
- **Dependency:** Must push commits to `origin/main` before pushing tag `v2.3.1` so the tag points to the final release commit.

---

## Workflow state

- **Current phase:** Done
- **Pending decision:** None
- **Execution blocked until:** None
