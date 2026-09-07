# Spec — T-10: v2.5.0 Release Tagging & Packaging

- **Branch:** `main`
- **Status:** In Spec
- **Assignee / Agent:** Agent Flash-1 / Rodrigo Pena
- **Related Issues / Tasks:** T-08, T-09, `.internal/SPRINT.md`, `.internal/ROADMAP.md`, `.ai/audits/AUDIT_2026-09-07.md`, `.ai/audits/AUDIT_2026-09-06.md`

---

## Goal

Publish and package the official **PXOS v2.5.0** release across GitHub and PyPI, synchronizing version identifiers across CLI, installers, templates, AI crawler references (`llms.txt`, `llms-full.txt`), documentation badges, and test assertions, ensuring zero distribution drift in PyPI wheel builds.

---

## User Value

- **Developers & CI/CD Pipelines:** Installing via `pip install --upgrade pxos` or curl/PowerShell one-liners delivers the complete Benchmark Verifiability & Telemetry Anti-Poisoning Engine, deterministic git extraction, adherence qualification tiers, and hardened concurrency without runtime drift or broken package assets.
- **AI Crawlers & Autonomous Agents:** Machine-readable index files (`llms.txt`, `llms-full.txt`) and IDE rule templates cleanly reflect v2.5.0 capabilities, instructions, and operating rules.
- **Maintainers & Community:** GitHub Actions release workflow (`.github/workflows/release.yml`) automatically triggers on annotated tag `v2.5.0`, building and publishing verified sdist/wheel packages with Trusted Publishing.

---

## Strategic & Audit Alignment

- **Audit Findings Cross-Check:** Clean — No active audit blockers touching this scope. All findings through `AUDIT_2026-09-07.md` ([SEC-03], [REL-08]) and `AUDIT_2026-09-06.md` ([PKG-02] through [PKG-04], [REL-06], [PERF-02], [REL-07], [DOC-01]) are fully remediated and verified.
- **Strategic Blueprint Reference:** Completes the medium-term milestone specified in [`.internal/ROADMAP.md`](../../.internal/ROADMAP.md) and Priority #3 in [`.internal/SPRINT.md`](../../.internal/SPRINT.md).
- **Critical Invariants Adherence:**
  - `INV-001` (Telemetry Privacy & Opt-in Anonymization): Preserved.
  - `INV-002` (Internal Quarantine): `.internal/` materials remain strictly quarantined and gitignored.
  - `INV-003` (Zero External Core Dependencies): Only standard library tooling used.
  - `INV-004` (English Conventional Commits): Release commit follows `chore(release): bump version to 2.5.0 and synchronize release metadata`.
  - `INV-005` (Append-Only Decision Log): Unbroken chronological record preserved in `.ai/DECISION_LOG.md`.

---

## Scope

### In:
1. **Version Synchronization (`2.4.0` → `2.5.0`):**
   - Core Python package: `pyproject.toml` (`version = "2.5.0"`), `pxos/__init__.py` (`__version__ = "2.5.0"`), `pxos/cli.py` (`VERSION = "2.5.0"`).
   - Shell installers: `install.sh` (`PXOS_VERSION="2.5.0"`), `install.ps1` (`$PXOS_VERSION = "2.5.0"`).
   - Generator scripts: `scripts/generate-llms-txt.py` (`VERSION = "2.5.0"`).
   - Rules & Core Framework metadata: `.ai/AI_BASE.md`, `.ai/PROJECT_CONTEXT.md`, `templates/rules/pxos.md`, `WORKFLOWS.md`, `skills/update/SKILL.md`.
   - Web & crawler metadata: `templates/site/metadata.json`, `templates/site/public/head-tags.html`, `README.md` (version badge and upgrade instructions).
2. **Package Data Parity & AI Index Regeneration:**
   - Execute `py scripts/sync-package-data.py` to mirror all updated templates and scripts into `pxos/templates/` and `pxos/scripts/`.
   - Execute `py scripts/generate-llms-txt.py` to regenerate `llms.txt` and `llms-full.txt` (and mirror to templates).
   - Verify parity with `py scripts/sync-package-data.py --check` and `py scripts/generate-llms-txt.py --check`.
3. **Test Suite Adaptation:**
   - Update `tests/test_audit_remediation.py` assertion `test_doc_01_version_and_invariants_consistency` to validate `v2.5.0` across documentation and rules.
   - Run full test suite (`py -m unittest discover tests`) verifying 100% pass rate.
4. **Changelog Documentation:**
   - Add `## [2.5.0] - 2026-09-07` entry to `CHANGELOG.md` detailing:
     - Benchmark Verifiability & Telemetry Anti-Poisoning Engine (T-08)
     - Codebase Hardening, Packaging Parity & Concurrency Resilience (T-09)
     - Security and git extraction edge-case fixes from Audit 2026-09-07 ([SEC-03], [REL-08])
5. **Sprint Tracking:**
   - Register task `T-10` in `.internal/SPRINT.md`.
6. **Git Release Operations:**
   - Commit version bump using Conventional Commits.
   - Prepare annotated release tag `v2.5.0` (`git tag -a v2.5.0 -m "release: v2.5.0 - benchmark verifiability and telemetry anti-poisoning engine"`).

### Out:
- Functional rewrites to the telemetry ingestion server or benchmark client (already tested and audited).
- Public community launch distribution on Hacker News/Dev.to/Reddit (handled separately by human developer via `LAUNCH_KIT.md`).

---

## Constraints

- Pure Python 3 standard library (`INV-003`).
- Strict Semantic Versioning: `2.5.0` (minor release introducing verifiable telemetry, adherence tiers, and git metric extraction).
- English Conventional Commits standard (`INV-004`).
- All package data files must match repository source files byte-for-byte (`[PKG-02]`, `[PKG-04]`).

---

## Existing Patterns

- Version synchronization pattern established in `SPEC-v2.3.1-release.md`.
- Automated package data parity check via `scripts/sync-package-data.py`.
- Automated LLM context indexing via `scripts/generate-llms-txt.py`.
- Keep a Changelog structure in `CHANGELOG.md`.

---

## Proposed Change

1. **Update Version Identifiers:**
   Update version string from `2.4.0` to `2.5.0` in:
   - `pyproject.toml`
   - `pxos/__init__.py`
   - `pxos/cli.py`
   - `install.sh`
   - `install.ps1`
   - `scripts/generate-llms-txt.py`
   - `README.md`
   - `WORKFLOWS.md`
   - `skills/update/SKILL.md`
   - `templates/rules/pxos.md`
   - `templates/site/metadata.json`
   - `templates/site/public/head-tags.html`
   - `.ai/AI_BASE.md`
   - `.ai/PROJECT_CONTEXT.md`
2. **Execute Automation Scripts:**
   - Run `py scripts/sync-package-data.py`
   - Run `py scripts/generate-llms-txt.py`
3. **Update Test Assertions:**
   - Modify `tests/test_audit_remediation.py` to check `v2.5.0`.
4. **Append Changelog:**
   - Insert `## [2.5.0] - 2026-09-07` in `CHANGELOG.md`.
5. **Update Sprint Matrix:**
   - Add Task `T-10` in `.internal/SPRINT.md`.
6. **Validation & Tagging:**
   - Run `py -m unittest discover tests`.
   - Run `--check` validations.
   - Commit and tag `v2.5.0`.

---

## Technical Flow

```
1. Version Bump across source files & installer scripts
2. Execute sync-package-data.py (mirrors to pxos/templates & pxos/scripts)
3. Execute generate-llms-txt.py (regenerates llms.txt, llms-full.txt)
4. Update tests/test_audit_remediation.py for v2.5.0 assertion
5. Run test suite: py -m unittest discover tests (28+ tests pass)
6. Run parity checks: sync-package-data.py --check && generate-llms-txt.py --check
7. Update CHANGELOG.md and SPRINT.md
8. Git commit & tag v2.5.0
```

---

## Edge Cases

- **Package Data Drift:** If files in `templates/` or `scripts/` change during version bump without syncing to `pxos/`, PyPI distribution build will drift.
  - *Mitigation:* `scripts/sync-package-data.py` copies all changes, and `check_parity()` validates exact byte equivalence.
- **Stale Crawler Reference:** If `generate-llms-txt.py` is not re-run, `llms.txt` will cite v2.4.0 while package is v2.5.0.
  - *Mitigation:* Running `py scripts/generate-llms-txt.py --check` in CI and local validation guarantees consistency.

---

## Acceptance Criteria

- [x] `pyproject.toml`, `pxos/__init__.py`, and `pxos/cli.py` set to version `2.5.0`.
- [x] `install.sh` and `install.ps1` default to `2.5.0`.
- [x] `README.md`, `WORKFLOWS.md`, `skills/update/SKILL.md`, and templates updated to `v2.5.0`.
- [x] `py scripts/sync-package-data.py --check` passes with zero drift.
- [x] `py scripts/generate-llms-txt.py --check` passes with zero drift.
- [x] `tests/test_audit_remediation.py` assertions updated and full test suite passes 100%.
- [x] `CHANGELOG.md` updated with comprehensive `[2.5.0]` release notes.
- [x] `.internal/SPRINT.md` task matrix updated with Task `T-10`.
- [x] Git commit and annotated tag `v2.5.0` prepared and pushed to origin.
- [x] Official GitHub Release created with attached wheel and sdist binaries and `docs/RELEASE_PROCESS.md` codified.

---

## Validation Plan

1. **Automated Unit & Integration Tests:**
   - `py -m unittest discover tests` (All tests must pass).
2. **Parity & Consistency Checks:**
   - `py scripts/sync-package-data.py --check`
   - `py scripts/generate-llms-txt.py --check`
   - `git diff` review to ensure no untracked or unwanted files are introduced.

---

## Risks & Cross-Task Impact

- **Tag Push Trigger:** Pushing `v2.5.0` to GitHub triggers `.github/workflows/release.yml`. Ensure all tests pass locally first before pushing.

---

## Workflow State

- **Current phase:** Done
- **Pending decision:** None
- **Execution blocked until:** None
