# Spec — T-08: Benchmark Verifiability & Telemetry Anti-Poisoning Engine (v2.5.0)

- **Branch:** `main` (or `feat/t08-telemetry-integrity`)
- **Status:** In Spec
- **Assignee / Agent:** Agent Flash-1 / Rodrigo Pena
- **Related Issues / Tasks:** T-08, [`.internal/TELEMETRY_INTEGRITY_RFC.md`](../../.internal/TELEMETRY_INTEGRITY_RFC.md), [`.internal/ROADMAP.md`](../../.internal/ROADMAP.md)

---

## Goal

Harden the `/benchmark` operational pipeline and public telemetry ingestion infrastructure (`telemetry.madebypx.com`), transforming empirical performance metrics into an irrefutable, scientific, and tamper-resistant dataset immune to Sybil attacks, client spoofing, and exploratory noise.

---

## User Value

- **Research Community & Evaluators:** Gain mathematically trustworthy, peer-auditable empirical benchmarks on real-world AI coding efficiency (token consumption, rework ratio, UX completeness) filtered from noise and tampering.
- **Developers & Teams:** Retain absolute IP privacy through irreversible cryptographic hashing (`project_hash`) while gaining automated, zero-effort git metric extraction (`pxos benchmark --extract`) that eliminates manual guesswork.
- **Framework Maintainers:** Protect public endpoints against Sybil/spam loops via session fingerprint idempotency (`session_fingerprint` UPSERT) and daily project submission quotas, while public dashboards automatically reflect verified Tier A methodology.

---

## Strategic & Audit Alignment

- **Audit Findings Cross-Check:** Clean — No active audit blockers touching this scope. Builds upon `[PERF-02]` (rate limiter eviction/bounding) and `[REL-07]` (SQLite busy_timeout concurrency) resolved in `AUDIT_2026-09-06.md`.
- **Strategic Blueprint Reference:** Fully implements the architectural requirements defined in [`.internal/TELEMETRY_INTEGRITY_RFC.md`](../../.internal/TELEMETRY_INTEGRITY_RFC.md) and [`.internal/ROADMAP.md`](../../.internal/ROADMAP.md).
- **Critical Invariants Adherence:**
  - `INV-001` (Telemetry Privacy & Opt-in Anonymization): Project names irreversibly hashed with SHA-256; zero source code, commit messages, or PII transmitted.
  - `INV-002` (Internal Quarantine): All internal notes and benchmarks remain strictly isolated.
  - `INV-003` (Zero External Core Dependencies): Implemented exclusively with Python 3 standard library (`hashlib`, `sqlite3`, `subprocess`, `math`, `statistics`, `urllib`, `json`).
  - `INV-004` (English Conventional Commits): Follows standard commit conventions.
  - `INV-005` (Append-Only Decision Log): Durable architectural decisions recorded in `.ai/DECISION_LOG.md`.

---

## Scope

### In:
1. **Cryptographic Session Fingerprinting & Ingestion Idempotency (`benchmarks/server.py`):**
   - Introduce `session_fingerprint` field generated deterministically from `sha256(project_salt + git_root_hash + branch + task_id)`.
   - SQLite schema update: `session_fingerprint TEXT UNIQUE` on `submissions` table with index.
   - Database UPSERT (`ON CONFLICT(session_fingerprint) DO UPDATE SET ...`) or idempotent update semantics, ensuring one task execution yields exactly one consolidated database record.
   - Project-level daily submission rate limiter (maximum 10 submissions per 24 hours per `project_hash`).
2. **Methodological Qualification Engine (`scripts/pxos-benchmark.py` & `benchmarks/server.py`):**
   - Calculate objective repository `adherence_score` (0–100 points) based on concrete artifacts:
     - Valid `.ai/PROJECT_CONTEXT.md` with declared invariants (+20 pts)
     - At least one completed specification in `.ai/specs/` or `.ai/CURRENT_SPEC.md` (+25 pts)
     - Git commit history adherence to Conventional Commits format (+15 pts)
     - Execution depth (minimum 3 turns and >= 15 lines touched) (+20 pts)
     - Active architectural decision tracking in `.ai/DECISION_LOG.md` (+20 pts)
   - Assign `qualification_tier`:
     - **Tier A (Verified Rigor, 70–100 pts):** Marked `is_qualified = 1`.
     - **Tier B (Partial / Casual Adoption, 40–69 pts):** Marked `is_qualified = 0`.
     - **Tier C (Unqualified / Noise, < 40 pts):** Marked `is_qualified = 0`.
3. **Deterministic Git Metric Extraction (`scripts/pxos-benchmark.py` & `pxos/cli.py`):**
   - Add `pxos benchmark --extract` (and internal python function) to extract LOC and churn mathematically from `git log --stat` and `git diff` relative to branch base/initial commit.
   - Compute `git_tree_hash` and commit count deterministically, removing LLM hallucinations or guesswork for lines of code and rework.
4. **Plausibility & Anti-Spoofing Guardrails (`benchmarks/server.py`):**
   - Server-side validation rejecting physically or logically impossible telemetry:
     - 0% rework reported when `rework_turn_count > 0` or multiple `fix:` commits exist.
     - 0 framework overhead tokens when spec file exists.
     - Unrealistic throughput (> 500 LOC/min per turn or total tokens inconsistent with turn count).
     - Range checks on `adherence_score` (0-100) and `qualification_tier`.
5. **Robust Statistical Aggregation (`benchmarks/analyze.py` & `server.py`):**
   - Upgrade `/api/v1/stats` and `analyze.py` to:
     - Exclusively compute public metrics, summaries, and dashboard averages from **Tier A (`is_qualified = 1`)**.
     - Employ **Medians** and **5% Trimmed Means** to discard outlier spikes.
     - Implement Interquartile Range (**IQR Outlier Filtering**) ($> 1.5 \times \text{IQR}$) to isolate anomalous entries.
6. **Client Anonymization & Schema Version 2.0:**
   - Replace plaintext project name with `project_hash = sha256(project_name + salt)[:16]`.
   - Add `schema_version: "2.0"` to the payload contract.
   - Allow and properly qualify aborted/frustrated sessions (`net_utility_score <= -2`) to eliminate survivor bias.
7. **Automated Unit & Integration Tests:**
   - Comprehensive test suite in `tests/test_telemetry_integrity.py` testing fingerprint generation, server UPSERT idempotency, project rate limiting, adherence scoring, git extraction, and IQR filtering.

### Out:
- Replacing SQLite with external database systems (e.g. Postgres) — SQLite in WAL mode with `busy_timeout` remains standard per `INV-003`.
- Breaking changes to legacy v1 telemetry ingestion: server maintains backward compatibility by defaulting missing fields safely.
- Modifying UI components of `pxos-site` (will ingest the enhanced `/api/v1/stats` payload automatically via its existing contract).

---

## Constraints

- **Zero External Dependencies (`INV-003`):** Pure Python 3 standard library (`hashlib`, `sqlite3`, `subprocess`, `math`, `statistics`, `urllib`, `json`).
- **Strict Privacy (`INV-001`):** No plaintext project names, source code, git messages, author emails, or tokens transmitted.
- **Cross-Platform Execution:** All git inspection and hashing routines must execute identically on Windows (`pwsh`), macOS, and Linux (`sh`).
- **Concurrency Resilience:** SQLite connection timeouts (`30.0s`) and `busy_timeout = 5000` must be maintained across all transactions.

---

## Existing Patterns

- **CLI Resource Resolution:** `pxos.cli.get_resource_path()` for dispatching package/repo scripts.
- **Rate Limiting:** Sliding-window in-memory rate limiter with memory pruning in `benchmarks/server.py`.
- **Sliding Aggregation:** `benchmarks/analyze.py` dataclasses and reporting pipelines.
- **Skill Dispatch Protocol:** `skills/benchmark/SKILL.md` principal auditor prompt.

---

## Proposed Change

1. **`benchmarks/server.py`:**
   - Update `init_database()` schema:
     - Add columns: `schema_version TEXT`, `session_fingerprint TEXT UNIQUE`, `project_hash TEXT`, `adherence_score INTEGER`, `qualification_tier TEXT`, `is_qualified INTEGER DEFAULT 0`, `git_tree_hash TEXT`.
   - Implement `ON CONFLICT(session_fingerprint) DO UPDATE` in `ingest_telemetry()`.
   - Add project-level submission rate limiting table/dictionary (max 10 submissions/day per `project_hash`).
   - Add plausibility validation functions (`validate_plausibility(data)`).
   - Filter `handle_stats()` queries to `WHERE is_qualified = 1` for primary metrics.
2. **`scripts/pxos-benchmark.py`:**
   - Add deterministic git metric extractor (`extract_git_metrics()`) querying `git diff --shortstat` and `git log`.
   - Add adherence scoring calculator (`calculate_adherence_score()`) inspecting `.ai/` files and git log.
   - Enforce irreversible hashing of project names (`hashlib.sha256(name.encode()).hexdigest()[:16]`).
   - Add `--extract` flag to CLI for automatic local audit population.
   - Emit schema v2.0 payload with `session_fingerprint`, `project_hash`, `adherence_score`, and `qualification_tier`.
3. **`pxos/cli.py`:**
   - Support `pxos benchmark --extract` passing through to `scripts/pxos-benchmark.py`.
4. **`benchmarks/analyze.py`:**
   - Segment analysis into Tier A (primary) and Tier B/C (exploratory).
   - Implement `calculate_trimmed_mean(values, trim_percent=0.05)` and `filter_iqr_outliers(values)`.
   - Output median, mean, and trimmed mean in `summary.json` and `REPORT.md`.
5. **`skills/benchmark/SKILL.md`:**
   - Update operational workflow to guide agents to run deterministic extraction (`pxos benchmark --extract`) rather than guessing LOC/churn metrics.
6. **`tests/test_telemetry_integrity.py`:**
   - Full suite covering all new security, idempotency, qualification, and statistical algorithms.

---

## Technical Flow

```
1. Developer / Agent completes task
2. Agent runs `pxos benchmark --extract`
   ├── Git extractor measures exact initial LOC, churn, and commit count
   └── Adherence evaluator scores repository maturity (Tiers A/B/C)
3. Agent audits UX completeness & net utility score
4. Audit saved locally in `.ai/audits/BENCHMARK_<task_id>.json`
5. User consents to research telemetry transmission
6. Client computes:
   ├── project_hash = SHA256(project_name + salt)[:16]
   └── session_fingerprint = SHA256(project_salt + git_root + branch + task_id)
7. Client POSTs schema v2.0 payload to `/api/v1/telemetry`
8. Server Ingestion:
   ├── IP & Project daily quota validation
   ├── Plausibility & Anti-spoofing constraint checks
   └── SQLite UPSERT on `session_fingerprint` (1 session = 1 record)
9. Server & Analyze Aggregation:
   ├── Filters strictly on `is_qualified = 1` (Tier A)
   └── Computes Medians, 5% Trimmed Means, and IQR outlier boundaries
```

---

## Edge Cases

- **Detached HEAD or Fresh Repo with No Commits:** Git extractor falls back to local workspace file diff or zeroes gracefully without throwing unhandled exceptions.
- **Re-running Benchmark Multiple Times:** Same task and branch produce identical `session_fingerprint`, performing safe UPSERT without duplicating stats or inflating submission counts.
- **Outlier Flooding (Malicious Benchmarks):** IQR filter and trimmed mean exclude extreme values even if an unexpected payload passes basic sanity ranges.
- **Network Glitch or Server Downtime:** Client saves benchmark locally; no data lost, with clear offline warning.
- **Legacy Schema Ingestion:** Telemetry server detects missing `schema_version` and gracefully treats record as legacy/unqualified (`is_qualified = 0`) without database corruption.

---

## Acceptance Criteria

- [x] `session_fingerprint` computed deterministically and enforced as `UNIQUE` with UPSERT semantics in `benchmarks/server.py`.
- [x] Project-level rate limiting prevents > 10 submissions per day per `project_hash`.
- [x] Repository adherence score (0-100) implemented in `scripts/pxos-benchmark.py` and classified into Tiers A, B, and C.
- [x] Deterministic git extraction via `pxos benchmark --extract` accurately tallies added/deleted LOC and commit counts.
- [x] Plausibility guardrails reject impossible telemetry combinations (e.g. 0% rework with multiple fix commits).
- [x] `benchmarks/analyze.py` and `/api/v1/stats` filter public metrics to Tier A (`is_qualified = 1`) and compute medians and 5% trimmed means with IQR anomaly rejection.
- [x] Telemetry payload irreversibly hashes project names (`project_hash`) and complies with `INV-001`.
- [x] `skills/benchmark/SKILL.md` updated with deterministic extraction guidelines.
- [x] All new test cases in `tests/test_telemetry_integrity.py` pass cleanly with 100% success.

---

## Validation Plan

1. **Unit & Integration Tests (`tests/test_telemetry_integrity.py`):**
   - Test session fingerprint determinism and SQLite UPSERT idempotency.
   - Test project-level submission throttling.
   - Test adherence scoring logic against sample project structures.
   - Test git extraction parser against simulated git outputs.
   - Test server plausibility validation rejections.
   - Test median, trimmed mean, and IQR calculation functions.
2. **End-to-End Local Server Test:**
   - Spin up `benchmarks/server.py` on test port with temporary SQLite DB.
   - Dispatch schema v2.0 payload via `scripts/pxos-benchmark.py --file <fixture> --yes`.
   - Re-dispatch identical payload to verify UPSERT without duplicate row creation.
   - Query `/api/v1/stats` to verify Tier A filtering and robust metrics calculation.
3. **Repository Cleanliness Check:**
   - Ensure zero unquarantined internal assets or untracked temporary database files.

---

## Risks & Cross-Task Impact

- **Database Migration for Existing Submissions:** Existing `telemetry.db` databases need backward-compatible schema alterations (`ALTER TABLE ADD COLUMN`).
  - *Mitigation:* `init_database()` inspects column names via `PRAGMA table_info(submissions)` and adds missing columns dynamically if the table already exists.
- **Cross-Platform Git Command Variances:** Line breaks or quote handling in Windows vs Unix git outputs.
  - *Mitigation:* Use standard plumbing commands (`git diff --numstat`, `git rev-parse`) with explicit encoding and fallback handling.

---

## Workflow State

- **Current phase:** Done
- **Pending decision:** None — ready for tag/release review
- **Execution blocked until:** None
