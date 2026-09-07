# Current Spec — Codebase Hardening, Packaging Integrity & CI Automation (v2.4.1)
<!-- pxos:spec-version 1.0.0 -->

This file defines the active task specification for remediating the findings identified in the full PXOS framework audit (`AUDIT_2026-09-06.md`), eliminating PyPI distribution drift, restoring AI crawlability parity, automating CI test execution, and strengthening telemetry server resilience.

---

## Goal

Resolve all 7 open findings (`[PKG-02]`, `[PKG-03]`, `[REL-06]`, `[PERF-02]`, `[PKG-04]`, `[DOC-01]`, `[REL-07]`) from `AUDIT_2026-09-06.md` to harden the PXOS codebase, ensure strict byte-for-byte synchronization between repository sources and PyPI packaged assets, institute automated CI verification, and eliminate memory leaks in telemetry ingestion.

---

## User value

- **Downstream Developers (`pip install pxos`):** Receive the full `v2.4.0` cognitive reliability upgrades (Completion Honesty Protocol, No-Assumption Clause, and Critical Invariants format) instead of outdated `v2.2.0` templates when initializing or updating projects.
- **AI Agents & Crawlers:** Ingest synchronized, verified `llms.txt` and `llms-full.txt` files that match the actual codebase architecture and pass strict compliance checking.
- **Maintainers & Contributors:** Protected by automated CI test runs on pull requests and pushes across Windows and Linux, preventing packaging drift or regression merges.
- **Telemetry Infrastructure:** Telemetry ingestion server becomes resilient to long-term memory bloat under high IP churn and eliminates `database is locked` concurrency exceptions.

---

## Strategic & Audit Alignment

- **Audit Findings Cross-Check:**
  - `[PKG-02]` (P1): Synchronize `pxos/templates/` and `pxos/scripts/` with root sources to eliminate PyPI packaging drift.
  - `[PKG-03]` (P2): Fix `generate-llms-txt.py --check` failure, update script to mirror files to `pxos/templates/site/public/`, and re-generate `llms.txt` & `llms-full.txt`.
  - `[REL-06]` (P2): Create `.github/workflows/test.yml` with multi-OS matrix (Ubuntu, Windows) running `unittest` and `generate-llms-txt.py --check` on pushes and PRs.
  - `[PERF-02]` (P2): Implement memory pruning and capacity bounding (LRU/max cap) in `benchmarks/server.py` for `IP_REQUEST_HISTORY`.
  - `[PKG-04]` (P2): Add pre-build/testing synchronization check in packaging pipeline and automated test in `tests/test_audit_remediation.py`.
  - `[DOC-01]` (P3): Harmonize version references to `v2.4.0` across `WORKFLOWS.md`, `skills/update/SKILL.md`, and declare `Critical invariants (INV-001 to INV-005)` in `.ai/PROJECT_CONTEXT.md`.
  - `[REL-07]` (P3): Add `PRAGMA busy_timeout = 5000;`, `sqlite3.connect(..., timeout=30.0)`, and configurable `HOST` environment variable in `benchmarks/server.py`.
- **Strategic / Research Reference:** Clean — checked `.ai/research/INDEX.md` (no conflicting invariant blockers). Adheres to PXOS Core Invariants: zero external runtime dependencies (stdlib only), strict isolation of `.internal/`, and English Conventional Commits.

---

## Scope

### In:
1. **Packaging Synchronization (`[PKG-02]`, `[PKG-04]`):**
   - Synchronize all files in `pxos/templates/` and `pxos/scripts/` with `templates/` and `scripts/`.
   - Add automated test assertions in `tests/test_audit_remediation.py` verifying byte-level parity between root assets and bundled package assets.
2. **AI Crawlability Mirroring & Verification (`[PKG-03]`):**
   - Enhance `scripts/generate-llms-txt.py` to mirror outputs to `pxos/templates/site/public/` in addition to `templates/site/public/`.
   - Re-generate `llms.txt` and `llms-full.txt` from active source documents.
   - Verify that `python scripts/generate-llms-txt.py --check` exits with code 0.
3. **Automated CI Workflow (`[REL-06]`):**
   - Create `.github/workflows/test.yml` triggered on `push` to `main` and `pull_request` to `main`.
   - Matrix testing across `ubuntu-latest` and `windows-latest` running the full `unittest` test suite and `generate-llms-txt.py --check`.
4. **Telemetry Server Hardening (`[PERF-02]`, `[REL-07]`):**
   - Implement active pruning and a maximum capacity cap (e.g. 10,000 entries) in `benchmarks/server.py` `IP_REQUEST_HISTORY`.
   - Add `timeout=30.0` and `PRAGMA busy_timeout = 5000;` on all SQLite connection openings.
   - Support `HOST = os.environ.get("HOST", "127.0.0.1")` in `server.py` for containerized environments.
   - Add unit tests verifying rate-limiter memory eviction and database connection timeout configuration.
5. **Documentation & Invariants Alignment (`[DOC-01]`):**
   - Update version strings to `v2.4.0` in `WORKFLOWS.md` and `skills/update/SKILL.md`.
   - Update `.ai/PROJECT_CONTEXT.md` and template context files to formally register `Critical invariants` (`INV-001` through `INV-005`).

### Out:
- Implementation of T-08 Benchmark Trust & Anti-Poisoning Engine (cryptographic session fingerprints, git extraction CLI, tier scoring) — scheduled for v2.5.0 per `.internal/ROADMAP.md`.
- PyPI release tag execution / publishing (this spec prepares the codebase and passes all gates for the subsequent patch release).
- Modifying core CLI command arguments or breaking existing programmatic APIs.

---

## Constraints

- **Zero External Dependencies:** Use only Python 3 standard library (`pathlib`, `shutil`, `unittest`, `sqlite3`, `re`, `json`, `os`, `time`, `threading`).
- **Cross-Platform Compatibility:** Ensure scripts and tests work seamlessly on both Windows (`pwsh` / `py -3`) and POSIX environments (`bash` / `python3`).
- **Internal Asset Quarantine:** Do not expose any internal draft or tracking documents outside `.internal/`.

---

## Existing patterns

- **Test Suite Structure:** `tests/test_audit_remediation.py` organizes tests by audit tag (`[SEC-01]`, `[REL-01]`, etc.) using standard `unittest.TestCase`.
- **Package Resource Discovery:** `pxos.cli.get_resource_path()` uses `importlib.resources` or fallback filesystem resolution.
- **llms.txt Generation:** `scripts/generate-llms-txt.py` orchestrates markdown cleanup, section aggregation, and multi-directory mirroring.
- **Sliding Window Rate Limiter:** Thread-safe in-memory sliding window in `benchmarks/server.py`.

---

## Proposed change

1. **`pxos/templates/` & `pxos/scripts/`:** Mirror root files from `templates/` and `scripts/` directly into `pxos/` package data directories.
2. **`scripts/generate-llms-txt.py`:** Add package template path `pxos/templates/site/public/` to the mirroring targets in `main()`. Execute generator to update all mirrors.
3. **`benchmarks/server.py`:**
   - In `is_rate_limited()`, periodically prune keys whose timestamps are entirely outside `RATE_LIMIT_WINDOW_SECS`, and if `len(IP_REQUEST_HISTORY) > MAX_TRACKED_IPS` (10,000), evict the oldest entries.
   - In `init_database()`, `ingest_telemetry()`, and `handle_stats()`, instantiate `sqlite3.connect(DB_PATH, timeout=30.0)` and execute `conn.execute("PRAGMA busy_timeout = 5000;")`.
   - In `run_server()`, read host from `os.environ.get("HOST", "127.0.0.1")`.
4. **`.github/workflows/test.yml`:** Define GitHub Actions workflow for Ubuntu and Windows with Python 3.10+, executing `python -m unittest discover tests` and `python scripts/generate-llms-txt.py --check`.
5. **`tests/test_audit_remediation.py`:** Add test methods:
   - `test_pkg_02_bundled_templates_parity`: checks identical contents between root `templates/` and `pxos/templates/`.
   - `test_pkg_03_crawlability_check`: checks `generate-llms-txt.py --check` succeeds.
   - `test_perf_02_rate_limiter_pruning_and_bounding`: validates key pruning and max capacity cap under high IP churn.
   - `test_rel_07_sqlite_timeout_and_host_binding`: validates `busy_timeout` pragma and `HOST` env var support.
6. **Documentation & Context:** Update `WORKFLOWS.md`, `skills/update/SKILL.md`, and `.ai/PROJECT_CONTEXT.md` to reflect `v2.4.0` and declare the `Critical invariants` table.

---

## Technical flow

1. **Pre-commit / Development:**
   - Developer/Agent runs `python scripts/generate-llms-txt.py` to sync all `llms.txt` mirrors.
   - Package assets in `pxos/templates/` and `pxos/scripts/` are kept in lockstep with root directories.
2. **Local Verification:**
   - `python -m unittest discover tests` runs all audit remediation tests including asset parity, server rate limiter pruning, and database resilience.
   - `python scripts/generate-llms-txt.py --check` validates that no crawlability files have drifted.
3. **CI Execution (`.github/workflows/test.yml`):**
   - Automatically triggered on push or PR to `main`.
   - Executes tests across environments, failing PRs that introduce template drift, broken crawlability, or regression in audit standards.
4. **Runtime Ingestion:**
   - Telemetry server handles bursts with 30s connection timeout and 5000ms busy wait, while sliding-window rate limiter bounds its memory consumption to a maximum of 10,000 active client IPs.

---

## Edge cases

- **Directory Creation on Fresh Clones:** Mirroring in `generate-llms-txt.py` must ensure target directories exist before writing (`mkdir(parents=True, exist_ok=True)`).
- **Line Endings (CRLF vs LF):** Parity checks between `templates/` and `pxos/templates/` must normalize line endings (`\r\n` vs `\n`) to prevent false negatives on Windows git checkouts.
- **Race Condition in Rate Limiter Pruning:** Pruning must execute strictly inside `RATE_LIMIT_LOCK` to avoid `RuntimeError: dictionary changed size during iteration`.
- **SQLite Concurrency Under Write Bursts:** Both read and write connections must set `busy_timeout` to ensure SQLite retries automatically rather than failing immediately.

---

## Acceptance criteria

- [x] `[PKG-02]`: All files in `pxos/templates/` and `pxos/scripts/` match `templates/` and `scripts/` (including `AI_BASE.md` v2.4.0 and updated `PROJECT_CONTEXT.md`).
- [x] `[PKG-03]`: `scripts/generate-llms-txt.py` mirrors to `pxos/templates/site/public/`, and `py scripts/generate-llms-txt.py --check` passes with exit code 0.
- [x] `[REL-06]`: `.github/workflows/test.yml` exists, is syntactically valid YAML, and defines push/pull_request triggers for Ubuntu and Windows.
- [x] `[PERF-02]`: `benchmarks/server.py` evicts expired IP keys from `IP_REQUEST_HISTORY` and bounds maximum dictionary size to 10,000 entries.
- [x] `[PKG-04]`: Unit test in `tests/test_audit_remediation.py` validates template and script parity.
- [x] `[DOC-01]`: `WORKFLOWS.md` and `skills/update/SKILL.md` reference `v2.4.0`, and `.ai/PROJECT_CONTEXT.md` registers `Critical invariants (INV-001 through INV-005)`.
- [x] `[REL-07]`: `benchmarks/server.py` uses `timeout=30.0`, sets `PRAGMA busy_timeout = 5000;`, and reads `HOST` from environment.
- [x] All unit tests in `tests/test_audit_remediation.py` pass cleanly (`python -m unittest tests/test_audit_remediation.py`).

---

## Validation plan

1. **Automated Unit Tests:**
   - Execute: `python -m unittest discover tests -v`
   - Assert all tests (existing 9 plus new remediation tests) pass with 0 errors and 0 failures.
2. **AI Indexability & Crawlability Check:**
   - Execute: `python scripts/generate-llms-txt.py --check`
   - Assert clean output: `[OK] llms.txt and llms-full.txt are valid and up to date.`
3. **CI Workflow Syntax Check:**
   - Verify `.github/workflows/test.yml` structure against GitHub Actions schema.
4. **Git Status & Diff Cleanliness:**
   - Run `git status` to ensure only targeted files are modified, with no orphaned temp files or unquarantined internal assets.

---

## Risks & Cross-Task Dependencies

- **Risk:** Modifying `benchmarks/server.py` could disrupt running telemetry server if syntax errors occur.
  - *Mitigation:* Comprehensive unit tests and local execution before deployment.
- **Risk:** Windows CRLF conversion causing parity test failures.
  - *Mitigation:* Normalize newlines (`content.replace('\r\n', '\n')`) in the parity check assertions.
- **Dependency:** Prepares repository cleanly for the subsequent v2.4.1 release tag and PyPI push.

---

## Workflow state

- **Current phase:** Validate / Review
- **Pending decision:** None — ready for user walkthrough review and commit
- **Execution blocked until:** None
