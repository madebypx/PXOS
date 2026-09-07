# Changelog

All notable changes to the **PXOS** framework are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.5.1] - 2026-09-07

### Fixed
- **Telemetry UX Completeness Metric Filtering:** `mean_ux_state_completeness_pct` in `/api/v1/stats` now correctly averages only UI-touching tasks (`ui_touched = 1`), matching the filtering already used in `benchmarks/analyze.py`. Previously, backend-only tasks with `ux_completeness = 0.0` dragged down the aggregate, distorting the reported metric.

### Added
- **`evaluated_ui_tasks_count` in Stats Summary:** New field in the `/api/v1/stats` summary providing transparency on how many submissions contributed to the UX completeness average.
- **Enriched `recent_runs` Response:** Each entry in the `recent_runs` array now includes `task_description`, `ux_completeness_pct`, and `ui_touched` fields, enabling downstream consumers (dashboards, site) to display richer run details without a separate endpoint.
- **Live Telemetry Chart Integration (pxos-site):** `TelemetryCharts.tsx` now consumes `stats.recent_runs` from the live API when available, falling back to the static baseline dataset when offline.

### Changed
- Synchronized release version to `2.5.1` across `pyproject.toml`, `pxos/__init__.py`, `pxos/cli.py`, `generate-llms-txt.py`, and web metadata.

---

## [2.5.0] - 2026-09-07

### Added
- **Benchmark Verifiability & Telemetry Anti-Poisoning Engine (Task T-08):**
  - **Cryptographic Session Fingerprinting (`session_fingerprint`):** Deterministically generated from `sha256(project_salt + git_root_hash + branch + task_id)` and enforced as a `UNIQUE` constraint in SQLite with `UPSERT` semantics (`ON CONFLICT(session_fingerprint) DO UPDATE`), preventing duplicate submissions and Sybil attacks.
  - **Methodological Qualification Engine & Gating (Tiers A/B/C):** Automated scoring (0-100 pts) evaluating repository discipline (project context invariants, completed specs, Conventional Commits adherence, session depth, and decision tracking). Public stats at `/api/v1/stats` and benchmark summaries now strictly gate calculations to **Tier A (`is_qualified = 1`)**.
  - **Deterministic Git Metric Extraction (`pxos benchmark --extract`):** Mathematical extraction of lines added/deleted, churn, tree hash, and commit counts directly from git plumbing (`git diff --numstat`, `git log`), replacing LLM guesswork and hallucinations.
  - **Server-Side Anti-Spoofing & Plausibility Guardrails:** Rejection of impossible telemetry combinations (e.g. 0% rework with multiple fix commits or unrealistic turn-to-token velocity) via HTTP 422.
  - **Robust Statistical Aggregation:** Implementation of medians, 5% trimmed means, and Interquartile Range (**IQR Outlier Filtering**) ($> 1.5 \times \text{IQR}$) in `benchmarks/analyze.py` and `server.py` to isolate statistical anomalies.
  - **Client-Side Irreversible Project Hashing:** Cryptographic hashing of project names (`project_hash = sha256(name)[:16]`), preserving total intellectual property confidentiality per `INV-001`.
  - **Schema Version 2.0:** Standardized payload contract supporting negative utility tracking (`net_utility_score <= -2`) to eliminate survivor bias in AI evaluation.
- **Codebase Hardening, Packaging Integrity & CI Automation (Task T-09):**
  - **Automated Multi-Platform CI Matrix:** Added `.github/workflows/test.yml` running unit tests and crawlability validation on push and PR across Ubuntu and Windows from Python 3.8 to 3.12 (`[REL-06]`).
  - **Package Parity Automation & Validation:** Added `scripts/sync-package-data.py` with `--check` mode to guarantee 100% byte-for-byte parity between root sources and bundled `pxos/templates` and `pxos/scripts` (`[PKG-02]`, `[PKG-04]`).
  - **Formalized Critical Invariants:** Added `INV-001` through `INV-005` to `.ai/PROJECT_CONTEXT.md` defining strict governance for telemetry privacy, internal file quarantine, zero external core dependencies, Conventional Commits, and append-only decision logging (`[DOC-01]`).
- **Standard Release Procedure & Governance (Task T-10):**
  - Published `docs/RELEASE_PROCESS.md` formalizing the mandatory GitHub Releases lifecycle, asset attachments, and automated distribution procedures.
  - Updated `.ai/PROJECT_CONTEXT.md` conventions establishing GitHub Releases as the standard release procedure for all current and future versions.

### Fixed
- **Rate Limiter Memory Bounds & Active Eviction (`[PERF-02]`):** Memory-bounded IP rate limiter in `benchmarks/server.py` with active expired entry eviction and 10,000 IP capacity cap.
- **SQLite Concurrency & Multi-Threaded Resiliência (`[REL-07]`):** Enforced `PRAGMA busy_timeout = 5000` and `timeout=30.0` on SQLite connections in `benchmarks/server.py`, mitigating `database is locked` errors during concurrent bursts. Added `HOST` environment variable binding (default `127.0.0.1`, allowing `0.0.0.0` for Docker).
- **Project Rate Limiter Anonymous Exemption (`[SEC-03]`):** Removed bypass exemption on literal `'anonymous'` strings, ensuring uniform 10-submissions/day project quotas.
- **Deterministic Git Extractor Initial Commit Fallback (`[REL-08]`):** Added fallback detection against Git's empty tree hash (`4b825dc...`) when executing on newly initialized repositories with a single commit.
- **Dynamic GitHub Release Titles:** Updated `.github/workflows/release.yml` to dynamically use the release tag name instead of hardcoded legacy version titles.

### Changed
- Synchronized release version to `2.5.0` across `pyproject.toml`, `pxos/__init__.py`, `pxos/cli.py`, `install.sh`, `install.ps1`, `llms.txt`, `llms-full.txt`, and web metadata.

---

## [2.4.0] - 2026-09-06

### Added
- **Completion Honesty Protocol (`AI_BASE.md`):**
  - Agents must now report structured confidence when declaring task completion: what was verified, what was NOT verified, and residual risks. Prohibits "100% complete" claims based solely on build/compilation success.
- **No-Assumption Clause (`AI_BASE.md`):**
  - Explicitly prohibits agents from inventing domain-specific values (thresholds, deadlines, ID formats, business rules) to save tokens. Reading the source of truth is mandatory — guessing is always worse than reading.
- **Mutation Lifecycle Check (`/plan` workflow):**
  - Conditional check that activates when a task creates, modifies, or deletes persisted data across multiple sources. Requires agents to trace mutations through every persistence node and confirm no background processes will contradict the change.
- **Spec Satisfaction Check (`/review` workflow):**
  - Review phase now requires agents to re-read acceptance criteria from the active spec and classify each as verified, not directly verified, or not met — closing the gap where agents deliver partial implementations silently.
- **Critical Invariants section (`PROJECT_CONTEXT.md` template):**
  - Optional section for hard domain constraints (with short IDs like INV-001) that agents must cross-reference during Plan. Lives inside PROJECT_CONTEXT.md (already loaded at every `/start`) rather than a separate file.

### Changed
- **Behavioral constraints (`AI_BASE.md`):** Added three new "never" rules: never declare completion based solely on build success, never use assumed/invented constants, never treat multi-node systems as single-node.
- **Rules template (`rules/pxos.md`):** Updated to reference Critical Invariants in PROJECT_CONTEXT.md during Plan phase.
- Synchronized version to `2.4.0` across `AI_BASE.md`, `rules/pxos.md`, and workflow documentation.

---

## [2.3.1] - 2026-09-04

### Fixed
- **PyPI Package Resource Bundling (`[PKG-01]`):**
  - Bundled `scripts/` and `templates/` directly within the `pxos` package data (`[tool.setuptools.package-data]`), resolving missing file errors when running `pxos benchmark`, `pxos monitor`, and offline `pxos init` from PyPI installations.
- **SQLite Connection Lifecycle & Error Handling (`[REL-01]`):**
  - Enclosed all database transactions in `benchmarks/server.py` within `try...finally: conn.close()` and added `sqlite3.Error` exception handling returning JSON 500 status codes, eliminating file descriptor leaks across multi-threaded HTTP requests.
- **PII Scrubbing & Telemetry Governance (`[SEC-01]`):**
  - Enforced strict serialization of only schema-validated fields into the database `raw_payload` column, discarding arbitrary unvalidated client parameters, proprietary code fragments, or user identifiers.
- **Client IP Rate Limiting & Proxy Safety (`[SEC-02]`):**
  - Implemented an in-memory sliding-window IP rate limiter (60 requests/minute) in `benchmarks/server.py` returning HTTP 429 upon bursts.
  - Restricted `X-Forwarded-For` header evaluation exclusively to requests originating from loopback/trusted proxy addresses.
- **Telemetry Payload Sanitization Hardening (`[REL-02]`):**
  - Guarded architectural and invariant integer metrics within `try...except (ValueError, TypeError)` blocks, responding with HTTP 422 Unprocessable Entity on malformed types instead of unhandled HTTP 500 crashes.
- **In-Memory Telemetry Aggregation Performance (`[PERF-01]`):**
  - Added `load_record_from_dict()` in `benchmarks/analyze.py` and refactored `benchmarks/aggregate_daily.py` to parse database records directly in memory, eliminating disk thrashing and temporary file writes in the public web directory.
- **Multi-Slash Git Branch Normalization (`[REL-03]`):**
  - Normalized branch slashes in `scripts/pxos-task.sh` and `scripts/pxos-task.ps1` (e.g. `feat/auth/oauth` -> `SPEC-auth-oauth.md`), preventing filesystem path failures when provisioning worktree task specs.
- **Continuous Integration Release Trigger Gating (`[REL-04]`):**
  - Added conditional guards (`startsWith(github.ref, 'refs/tags/v')`) to the GitHub Release and PyPI publishing steps in `.github/workflows/release.yml`, preventing accidental releases on manual workflow dispatches.
- **Benchmark Client Null Safety (`[REL-05]`):**
  - Guarded list iterations in `scripts/pxos-benchmark.py` against null values in incoming telemetry JSON files.

### Changed
- Synchronized release version to `2.3.1` across `pyproject.toml`, `pxos/__init__.py`, `pxos/cli.py`, `install.sh`, `install.ps1`, `llms.txt`, and web metadata.

---

## [2.3.0] - 2026-09-04

### Added
- **AI Indexability Standard (`llms.txt` & `llms-full.txt`):**
  - Root `llms.txt` compliant with `llmstxt.org` for direct AI crawler and search agent indexing.
  - Dense single-file `llms-full.txt` aggregating complete framework reference for direct LLM context injection.
  - Autonomous synchronization and validation utility (`scripts/generate-llms-txt.py`).
- **Cross-Platform Native Distribution:**
  - Native Windows PowerShell installer (`install.ps1`) enabling one-liner installation (`irm https://raw.githubusercontent.com/madebypx/PXOS/main/install.ps1 | iex`).
  - PEP 517/621 packaging metadata (`pyproject.toml`) and pure Python stdlib CLI (`pxos/`) providing global `pxos init`, `pxos update`, `pxos benchmark`, `pxos monitor`.
- **Downstream Adoption Badges & Community Infrastructure:**
  - Official copy-paste badges for downstream repositories (`Governed by PXOS`, `PXOS Multi-Agent`, `Context Cost -80%`).
  - GitHub community templates (`.github/CONTRIBUTING.md`, YAML issue templates, and PR template).
- **Technical Authority Whitepaper & Web Metadata:**
  - Ready-to-publish technical essay (`docs/WHITEPAPER.md`) highlighting empirical benchmark results (-80% token waste).
  - Schema.org `SoftwareApplication` JSON-LD and OpenGraph specification (`templates/site/metadata.json`) for `pxos.madebypx.com`.

### Changed
- **OSI-Approved Open-Source Licensing (Apache-2.0):**
  - Standardized on the Apache License, Version 2.0 (Apache-2.0) by PROJECT/X.
  - Grants unrestricted free use for developers, startups, and enterprise teams to inspect, modify, embed, and govern personal, internal, and commercial software without corporate compliance roadblocks (FOSSA/Snyk/Black Duck).
  - Enforces explicit trademark protections for PROJECT/X and PXOS names while providing a reciprocal patent infringement defense shield.

---

## [2.2.0] - 2026-09-04

### Added
- **Empirical Telemetry & Benchmark Laboratory (`benchmarks/`):**
  - Formal research design and statistical methodology ([`METHODOLOGY.md`](./benchmarks/METHODOLOGY.md)) defining hypotheses, control vs. treatment setups, and mathematical cost models.
  - Adversarial agent elicitation protocol ([`AGENT_INTERVIEW_PROTOCOL.md`](./benchmarks/AGENT_INTERVIEW_PROTOCOL.md)) with anti-sycophancy directives and machine-readable JSON schemas.
  - Zero-dependency statistical analysis engine ([`benchmarks/analyze.py`](./benchmarks/analyze.py)) computing token expenditures, rework ratios, and UX completeness across complexity tiers.
  - Ingestion server daemon ([`benchmarks/server.py`](./benchmarks/server.py)) with SQLite WAL storage, payload validation, and public telemetry endpoints (`/api/v1/telemetry`, `/api/v1/stats`, `/api/v1/health`).
  - Automated daily aggregation utility ([`benchmarks/aggregate_daily.py`](./benchmarks/aggregate_daily.py)) for cron-driven research dataset compaction.
  - Open empirical dataset ([`benchmarks/data/`](./benchmarks/data/)) and live laboratory summary report ([`benchmarks/REPORT.md`](./benchmarks/REPORT.md)).
- **Standardized Benchmark CLI Dispatcher (`scripts/pxos-benchmark.py`):**
  - Standalone utility supporting `--dry-run`, `--offline`, and interactive opt-in confirmation gates.

### Changed
- **Zero Consumer Project Pollution in `/benchmark` ([`skills/benchmark/SKILL.md`](./skills/benchmark/SKILL.md)):**
  - Fully decoupled consumer projects from internal framework tooling.
  - Audited telemetry records in consumer workspaces are now stored strictly within the existing `.ai/` governance layer (`.ai/audits/BENCHMARK_<task_id>.json`), completely preventing foreign folders in the consumer root.
- **Autonomous Telemetry Dispatch:**
  - AI agents now present sanitized numerical metrics directly in conversation and ask for explicit user consent.
  - Upon user approval, the agent conducts the HTTP POST transmission autonomously via direct network commands, eliminating manual terminal copy-paste friction for developers.
- Upgraded `install.sh` and templates to v2.2.0.

### Fixed
- Fixed 404 broken link on GitHub `main` branch for `benchmarks/METHODOLOGY.md`.
- Purged untracked `benchmarks/` generation from consumer workspace roots.

---

## [2.1.0] - 2026-09-04

### Added
- **Native Research & Audit Subsystems:**
  - Introduced `.ai/research/` with token-efficient index (`INDEX.md`) for technical spikes, domain rules, and UX benchmarks.
  - Introduced `.ai/audits/` with taxonomy guide (`README.md`) and modular severity-based audits (`PARTIAL_<subsystem>.md`).
- **Autonomous ADR Logging (`/decision`):**
  - Instant command to record durable architectural decisions directly to `.ai/DECISION_LOG.md` with zero formatting effort.
- **Product Design & UX Heuristics:**
  - Embedded Jakob Nielsen's 10 usability heuristics, Universal 5-State UI Matrix, and interaction safety gates directly into `/spec` and `/review`.
- **Standardized IDE Rules:**
  - Added unified rules template (`templates/rules/pxos.md`) supporting Cursor, Windsurf, Claude Code, Gemini CLI, and GitHub Copilot.

---

## [2.0.0] - 2026-09-03

### Added
- **Parallel Multi-Agent Engine (Git Worktrees):**
  - Autonomous task parallelization orchestrators (`scripts/pxos-task.sh` and `scripts/pxos-task.ps1`).
  - Physical workspace isolation in `../trees/<branch>` preventing concurrent file clobbering.
- **Modular Specification Matrix:**
  - Replaced monolithic spec with modular specs (`.ai/specs/SPEC-<branch>.md`).
  - Collaborative sprint dashboard (`SPRINT.md`) with multi-agent task state matrix.
- **Guided Continuity & Safe Upgrades:**
  - Added `/start` phase-aware session initializer with automatic branch and spec discovery.
  - Added `/update` workflow and `install.sh --update` flag for safe upgrades without overwriting project context.

---

## [1.0.0] - 2026-09-01

### Added
- Initial release of the PXOS framework.
- Minimal document-driven operational core (`.ai/`):
  - Universal operating contract (`AI_BASE.md`).
  - Project facts and conventions (`PROJECT_CONTEXT.md`).
  - Active task specification (`CURRENT_SPEC.md`).
  - Append-only architectural memory (`DECISION_LOG.md`).
- One-line installer script (`install.sh`).
