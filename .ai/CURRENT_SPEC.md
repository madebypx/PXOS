# Spec — T-06: Codebase Hardening, Audit Remediation & Packaging Integrity

- **Branch:** `main`
- **Status:** `Done`
- **Assignee / Agent:** `Agent / Rodrigo`
- **Related Issues / Tasks:** `.ai/audits/AUDIT_2026-09-04.md` (`SEC-01`, `PKG-01`, `REL-01`, `SEC-02`, `REL-02`, `PERF-01`, `REL-03`, `REL-04`, `REL-05`)

---

## Goal

Remediate all 9 critical, major, and minor defects identified in the full codebase audit of 2026-09-04 across telemetry ingestion (`benchmarks/server.py`), aggregation performance (`benchmarks/aggregate_daily.py`), Python package data bundling (`pyproject.toml`, `pxos/cli.py`), multi-agent worktree script resilience (`scripts/pxos-task.sh`, `scripts/pxos-task.ps1`), and CI workflow release safety (`.github/workflows/release.yml`).

---

## User value

- **Privacy & PII Protection:** Ensures the telemetry server strictly stores scrubbed, anonymous numeric data and enums in SQLite, discarding arbitrary client fields or proprietary source code snippets.
- **PyPI Package Out-of-the-Box Functionality:** Users installing PXOS via `pip install pxos` gain fully operational `pxos benchmark` and `pxos monitor` subcommands and offline template scaffolding without runtime missing-file exceptions.
- **Server Stability & Leak Prevention:** Guaranteed closure of database connections across all HTTP threads prevents SQLite file descriptor leaks and provides clean JSON error payloads upon failure.
- **Robust Multi-Agent Scripting:** Worktree provisioning scripts handle arbitrarily nested git branch names (e.g. `feat/telemetry/fix-wal`) without failing on missing subdirectories.
- **Safe CI/CD Automation:** Prevents accidental or invalid release tags when triggering manual GitHub Action workflow dispatches on non-tag branches.

---

## Strategic & Audit Alignment

- **Audit Findings Cross-Check:** Resolves all 9 findings documented in [.ai/audits/AUDIT_2026-09-04.md](file:///c:/Users/digo_/Documents/Programação/GitHub/PXOS/.ai/audits/AUDIT_2026-09-04.md):
  - `[SEC-01]` (P1): Storage of unsanitized raw payload violating privacy invariants.
  - `[PKG-01]` (P1): PyPI package missing CLI helper scripts and offline templates.
  - `[REL-01]` (P1): Unhandled SQLite exceptions & leaked connections in request handlers.
  - `[SEC-02]` (P2): Unvalidated `X-Forwarded-For` header and lack of IP rate limiting.
  - `[REL-02]` (P2): Unhandled type conversions outside exception block in telemetry sanitizer.
  - `[PERF-01]` (P2): Temporary file disk thrashing in public directory during telemetry aggregation.
  - `[REL-03]` (P2): Script crash on nested branch slashes in worktree spec provisioning.
  - `[REL-04]` (P3): GitHub release step tag collision on manual `workflow_dispatch`.
  - `[REL-05]` (P3): Potential NoneType iteration crash in benchmark client on null JSON attributes.
- **Strategic / Research Reference:** Enforces core architectural invariants defined in [.ai/PROJECT_CONTEXT.md](file:///c:/Users/digo_/Documents/Programação/GitHub/PXOS/.ai/PROJECT_CONTEXT.md) (Zero Runtime Dependencies, Token Economy, Strict Privacy & Anonymity, Deterministic Workflows).

---

## Scope

**In:**
1. **Telemetry Server & Ingestion (`benchmarks/server.py`):**
   - Sanitize `raw_payload` storage: serialize only schema-validated fields into SQLite, never raw input.
   - Guard database transactions with `try...finally: conn.close()` and catch `sqlite3.Error` with 500 JSON responses.
   - Enclose `invariants_violated_count` and related `arch` fields within the numerical `try...except` block.
   - Trust `X-Forwarded-For` only when direct peer IP is localhost (`127.0.0.1`) or configured proxy; add in-memory sliding-window IP rate limiter.
2. **Aggregation & In-Memory Analysis (`benchmarks/analyze.py`, `benchmarks/aggregate_daily.py`):**
   - Add `load_record_from_dict(data: dict, source_label: str)` in `analyze.py`.
   - Update `aggregate_daily.py` to parse records directly in memory, eliminating temporary file creation in `PUBLIC_DIR`.
3. **Packaging & Resource Resolution (`pyproject.toml`, `pxos/cli.py`):**
   - Move or bundle `templates/` and `scripts/` into `pxos` package data, or configure `[tool.setuptools.package-data]`.
   - Update `pxos/cli.py` to resolve templates and helper scripts relative to package root with fallback to repo root.
4. **Worktree Automation (`scripts/pxos-task.sh`, `scripts/pxos-task.ps1`):**
   - Normalize all forward slashes in `$SPEC_SUFFIX` to hyphens, preventing invalid nested paths in `.ai/specs/`.
5. **CI/CD Pipeline (`.github/workflows/release.yml`):**
   - Condition GitHub Release and PyPI publishing steps to execute only when `startsWith(github.ref, 'refs/tags/v')`.
6. **Benchmark Dispatcher (`scripts/pxos-benchmark.py`):**
   - Use safe list fallback `(crit.get("...") or [])` to avoid `NoneType` iteration.

**Out:**
- Adding third-party package dependencies (must stay pure Python stdlib).
- Altering the SQLite schema or existing table columns.
- Modifying core operating rules in `AI_BASE.md`.

---

## Constraints

- Pure Python 3 standard library (`urllib`, `sqlite3`, `json`, `argparse`, `dataclasses`).
- POSIX-compliant syntax for `install.sh` and `scripts/pxos-task.sh`.
- Windows PowerShell 5.1 & PowerShell 7+ compatibility for `.ps1` scripts.
- Backward compatibility for existing `.ai/` directory layouts and commands.

---

## Existing patterns

- `benchmarks/server.py`: `ThreadingHTTPServer` with `PRAGMA journal_mode=WAL;`.
- `pxos/cli.py`: ANSI color helpers, `download_or_copy` idempotent file copier, `argparse` subparsers.
- `scripts/pxos-task.sh` & `pxos-task.ps1`: Git worktree manager for parallel agent branches.

---

## Proposed change

1. **`benchmarks/server.py`:**
   - In `validate_and_sanitize_payload`, move lines 151-154 inside `try...except (ValueError, TypeError)`.
   - Create a sanitized representation for `raw_payload` that omits unvalidated keys.
   - Refactor database access in `do_GET` and `do_POST` to:
     ```python
     conn = None
     try:
         with DB_LOCK:
             conn = sqlite3.connect(DB_PATH)
             ...
     except sqlite3.Error as e:
         self.send_json(500, {"error": f"Database error: {e}"})
     finally:
         if conn:
             conn.close()
     ```
   - Implement simple IP rate limiting dictionary with timestamp expiration.
2. **`benchmarks/analyze.py` & `benchmarks/aggregate_daily.py`:**
   - Extract `load_record_from_dict(data: dict, file_path: str = "") -> Optional[AuditRecord]` in `analyze.py`.
   - Have `load_record_from_json` delegate to `load_record_from_dict`.
   - In `aggregate_daily.py`, directly invoke `analyze.load_record_from_dict(tmp_data, f"db_record_{idx}")`.
3. **`pyproject.toml` & `pxos/cli.py`:**
   - Add `[tool.setuptools.package-data] pxos = ["templates/**", "scripts/**"]` or vendor resources into `pxos/`.
   - Update `download_or_copy`, `cmd_benchmark`, and `cmd_monitor` to probe package resources first before checking `parent.parent`.
4. **`scripts/pxos-task.sh` & `scripts/pxos-task.ps1`:**
   - Pipe `$SPEC_SUFFIX` through `tr '/' '-'` (bash) and `-replace '/', '-'` (pwsh).
5. **`.github/workflows/release.yml`:**
   - Add `if: startsWith(github.ref, 'refs/tags/v')` to `Publish GitHub Release` and `Publish to PyPI`.
6. **`scripts/pxos-benchmark.py`:**
   - Guard friction and benefit list comprehensions against `None` values.

---

## Technical flow

```
[Agent runs /spec] ──► [Spec T-06 Approved] ──► [Agent runs /plan]
                                                        │
                                                        ▼
                                          [Execute Modular Fixes]
                                          ├─ Telemetry Server & Ingestion
                                          ├─ In-Memory Aggregation
                                          ├─ Package Data & CLI Resolvers
                                          ├─ Worktree Normalization
                                          └─ CI Gating
                                                        │
                                                        ▼
                                          [Validate via Test Suite]
                                          ├─ Unit test server endpoints
                                          ├─ Test pip wheel contents
                                          ├─ Verify worktree script slashes
                                          └─ Validate dry-run benchmark
                                                        │
                                                        ▼
                                            [/review & /compact]
```

---

## Edge cases

- **Database Locks / Busy:** Handled cleanly with `sqlite3.BusyError` or general `sqlite3.Error` without file descriptor leak.
- **Corrupted Submission JSON:** Returns 400 Bad Request with descriptive message.
- **Offline CLI Execution:** `pxos init` falls back to package-bundled templates without making network calls.
- **Worktree branch with multiple levels:** `feat/auth/oauth/google` converts cleanly to `SPEC-auth-oauth-google.md`.

---

## Acceptance criteria

- [x] Telemetry server never persists un-scrubbed `raw_payload` attributes in SQLite (`SEC-01`).
- [x] Database connections in `server.py` are enclosed in `try...finally: conn.close()` (`REL-01`).
- [x] `validate_and_sanitize_payload` catches malformed types on architectural metrics (`REL-02`).
- [x] `X-Forwarded-For` is verified against trusted peers, and basic IP rate limiting is enforced (`SEC-02`).
- [x] `aggregate_daily.py` processes SQLite payloads in memory without writing temporary files to `PUBLIC_DIR` (`PERF-01`).
- [x] Python package includes necessary templates/scripts or bundles resources so `pxos benchmark` and offline `pxos init` succeed from PyPI (`PKG-01`).
- [x] Worktree creation in `pxos-task.sh` and `pxos-task.ps1` correctly creates modular specs for multi-slash branch names (`REL-03`).
- [x] GitHub release step in `.github/workflows/release.yml` is guarded against branch runs on `workflow_dispatch` (`REL-04`).
- [x] `pxos-benchmark.py` handles `null` attribute values in JSON payloads without raising `TypeError` (`REL-05`).

---

## Validation plan

1. **Server Unit & Ingestion Test:** Write and run a test script (`tests/test_audit_remediation.py`) asserting:
   - Malformed types in `invariants_violated_count` return 422, not 500. (Passed)
   - Extra fields in payload are excluded from database `raw_payload`. (Passed)
   - Repeated requests trigger rate limiting (429 Too Many Requests). (Passed)
   - Simulating database exceptions returns 500 and closes connections cleanly. (Passed)
2. **In-Memory Aggregation Test:** Test `load_record_from_dict` and ensure `aggregate_daily.py` generates daily reports without creating `_tmp_*.json` files. (Passed)
3. **Packaging Build Test:** Build wheel via `python -m build`, inspect wheel archive, verify template and script presence. (Passed)
4. **Worktree Script Test:** Verify branch normalization logic for multi-slash branch names. (Passed)
5. **Benchmark Dispatcher Test:** Pass JSON with `"identified_frictions": null` to `scripts/pxos-benchmark.py --dry-run` and verify successful sanitization. (Passed)

---

## Risks & Cross-Task Impact

- **Package Size:** Bundling templates into `pxos/` adds ~50 KB to the package wheel, which is negligible and compliant with zero-dependency requirements.
- **Breaking Changes:** Zero breaking changes to API endpoints or user-facing CLI syntax.

---

## Workflow state

- **Current phase:** Validate / Done
- **Pending decision:** None
- **Execution blocked until:** None
