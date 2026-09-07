# Decision Log

This file records durable architectural and product decisions (ADRs).
Append only — never delete past entries. If a decision is superseded, mark it as such.
Entries are maintained automatically by AI agents during `/compact` and via `/decision`, or manually by developers.
Only decisions with lasting impact belong here: architectural choices, rejected alternatives, structural shifts, and product invariants.

Multi-Agent Note: Entries are strictly additive and chronological. If a Git merge conflict occurs at the bottom of this file, the resolution rule is always to concatenate both entries without discarding either.

---

## Template

```
## YYYY-MM-DD — [Decision title]

**Decision:**
[What was decided.]

**Context:**
[Why this decision was needed. What problem it solves.]

**Options considered:**
- Option A — [brief description and why it was not chosen]
- Option B — [brief description and why it was not chosen]
- Chosen: Option C — [why this was selected]

**Tradeoffs:**
[What we gain and what we accept as a cost.]

**Impact:**
[What parts of the system are affected.]

**Status:** Active
```

---

<!-- Add decisions below this line, most recent first -->

## 2026-09-07 — Standardized GitHub Releases Procedure & Release Governance Lifecycle

**Decision:**
Formalize official GitHub Releases creation as the mandatory standard release procedure for all current and future versions of PXOS (`docs/RELEASE_PROCESS.md`), automate dynamic tag-based release titles in `.github/workflows/release.yml`, and record the requirement in `.ai/PROJECT_CONTEXT.md` conventions. Every release must attach wheel and source distribution binaries and publish curated release notes from `CHANGELOG.md`.

**Context:**
Previous patch releases occasionally relied on ad-hoc tagging or hardcoded release titles in CI workflows (e.g. legacy `v2.3.0` strings persisting in workflow configs). To ensure complete distribution integrity, transparency for the open-source community, and immutable distribution assets on GitHub across all releases, a documented and programmatic standard operating procedure was required.

**Options considered:**
- Option A — Rely purely on manual GitHub web UI releases: Rejected due to human variance, inconsistent title formatting, and risk of forgotten assets or changelog omissions.
- Option B — Silent git-tag-only releases without GitHub Releases or binary attachments: Rejected because developers and evaluators auditing repository releases expect signed artifacts, attached wheels/sdists, and searchable changelog notes on GitHub.
- Chosen: Option C — Codify `docs/RELEASE_PROCESS.md` with a 9-step checklist, bind GitHub Releases as a mandatory convention in `PROJECT_CONTEXT.md`, make `.github/workflows/release.yml` title resolution dynamic, and automate release publication with `gh release create` and attached `dist/*` binaries.

**Tradeoffs:**
- Gains: Immediate availability of immutable wheel/sdist assets directly from GitHub Releases; eliminates title drift in CI; deterministic, audited release steps followed uniformly by both human maintainers and AI agents.
- Cost: Requires maintaining `docs/RELEASE_PROCESS.md` and verifying GitHub CLI or token permissions during release steps.

**Impact:**
Added `docs/RELEASE_PROCESS.md`, updated `.ai/PROJECT_CONTEXT.md`, `.github/workflows/release.yml`, `.internal/SPRINT.md`, `CHANGELOG.md`, and published GitHub Release `v2.5.0`.

**Status:** Active

---

## 2026-09-06 — Automated Package Parity Verification, AI Crawlability Mirroring, and Multi-OS CI Testing

**Decision:**
Implement automated continuous package parity checks (`scripts/sync-package-data.py --check`) in CI and release workflows, expand AI crawlability mirroring to package data (`pxos/templates/site/public/`), institute a multi-OS GitHub Actions test pipeline (`.github/workflows/test.yml`), and harden the telemetry server with active memory eviction and SQLite busy timeout resilience.

**Context:**
The v2.4.0 audit revealed packaging drift between repository root templates/scripts and bundled PyPI data in `pxos/` (`[PKG-02]`), as well as desynchronization in `llms-full.txt` crawlability checks (`[PKG-03]`), absent CI test automation on PRs/pushes (`[REL-06]`), and unbounded memory growth in the telemetry server rate limiter (`[PERF-02]`). An automated, standard-library enforcement mechanism was required to guarantee that no release can be packaged or merged without byte-level parity across source templates, package data, and crawler indices.

**Options considered:**
- Option A — Manual sync prior to git tagging: Rejected because manual sync is error-prone, developer amnesia creates PyPI drift, and PRs can merge regressions undetected.
- Option B — Heavy third-party build hooks (e.g. Hatchling/Flit plugins, complex tox setups): Rejected to preserve Core Invariant `INV-003` (zero external core dependencies).
- Chosen: Option C — Lightweight Python stdlib synchronization and parity check script (`scripts/sync-package-data.py`) hooked into `.github/workflows/test.yml` (multi-OS matrix), `release.yml`, and `tests/test_audit_remediation.py`.

**Tradeoffs:**
- Gains: Downstream PyPI users guaranteed to receive identical governance rules (Completion Honesty Protocol, No-Assumption Clause); AI agents consume synchronized `llms.txt`; zero runtime dependencies; telemetry server protected against OOM under high IP churn.
- Cost: Build and CI steps run additional parity verification before publishing.

**Impact:**
Touched `scripts/sync-package-data.py`, `pxos/scripts/sync-package-data.py`, `pxos/templates/`, `scripts/generate-llms-txt.py`, `.github/workflows/test.yml`, `.github/workflows/release.yml`, `benchmarks/server.py`, `WORKFLOWS.md`, `skills/update/SKILL.md`, `.ai/PROJECT_CONTEXT.md`, and `tests/test_audit_remediation.py`.

**Status:** Active

---

## 2026-09-04 — Transition Repository Licensing to Apache License 2.0 (Apache-2.0)

**Decision:**
Standardize PXOS repository licensing on the official, OSI-approved Apache License, Version 2.0 (Apache-2.0) governed by PROJECT/X, replacing the interim Business Source License 1.1 (BSL-1.1).

**Context:**
Prior to syndicating public launch announcements (Hacker News, Reddit, Twitter, Dev.to), analysis revealed that BSL-1.1 (Source-Available) creates severe adoption friction for framework and governance layers. Unlike server-side databases (CockroachDB) or cloud infrastructure (Terraform), PXOS `.ai/` specifications, prompts, and CLI scripts live directly inside user and enterprise repositories. Enterprise compliance scanners (FOSSA, Snyk, Black Duck) automatically flag non-OSI licenses as high-risk, while developer communities view BSL-licensed frameworks with skepticism. Apache 2.0 provides 100% unrestricted open-source adoption while preserving vital intellectual property safeguards: explicit reservation of trademark rights (prohibiting unauthorized use of "PXOS" or "PROJECT/X" names) and an express reciprocal patent retaliation shield.

**Options considered:**
- Option A — Retain BSL-1.1: Rejected because non-OSI status stifles viral framework adoption, triggers enterprise procurement roadblocks, and damages community trust.
- Option B — MIT License: Rejected because MIT lacks explicit trademark reservations and explicit patent cross-licensing protections.
- Chosen: Option C — Apache License, Version 2.0 (Apache-2.0). Provides complete open-source credibility (OSI-approved), zero enterprise compliance friction, and robust trademark/patent protections under PROJECT/X stewardship.

**Tradeoffs:**
- Gains: Immediate zero-friction adoption for individual developers, startups, and Fortune 500 enterprises; 100% positive alignment with open-source communities (Hacker News, Reddit r/LocalLLaMA); explicit trademark shield for PROJECT/X; clean integration with PyPI and open package managers.
- Cost: Permits third-party commercial derivatives as long as Apache 2.0 attribution, notice conditions, and trademark restrictions are respected.

**Impact:**
Updated `LICENSE`, `pyproject.toml`, `pxos/__init__.py`, `README.md`, `llms.txt`, `llms-full.txt`, `scripts/generate-llms-txt.py`, `docs/LAUNCH_WHITEPAPER.md`, `docs/LAUNCH_KIT.md`, and synchronized `pxos-site` components.

**Status:** Active

---

## 2026-09-04 — AI Indexability Standard (llms.txt) & Zero-Friction Multi-Channel Packaging (v2.3.0)

**Decision:**
Adopt the `llmstxt.org` specification (`llms.txt` and `llms-full.txt`) for direct machine ingestion by LLMs and autonomous web scrapers. Simultaneously introduce a pure Python standard library package (`pyproject.toml` + `pxos/` CLI) and native Windows PowerShell installer (`install.ps1`) to provide zero-friction 1-line installation across all operating systems. Explicitly establish `PROJECT/X` as the governing company/studio with `madebypx` acting as the domain and GitHub organization handle.

**Context:**
To make PXOS globally recognized by future AI models (pre-training datasets like The Stack, RAG agents, search crawlers), the framework needed standard machine-readable endpoints without HTML tags, viral repository backlink badges, and friction-free installation for developers regardless of OS.

**Options considered:**
- Option A — Rely solely on documentation site HTML crawling: Rejected because LLM crawlers suffer from token truncation, cookie banners, and CSS/HTML noise.
- Option B — Heavy Node.js CLI (`npm i -g pxos`): Rejected to uphold PXOS Priority #2 (zero runtime dependencies, avoiding node_modules bloat for lightweight governance).
- Chosen: Option C — `llmstxt.org` standard with automated sync (`scripts/generate-llms-txt.py`), native `install.ps1` for Windows, and pure stdlib PEP 517/621 Python CLI (`pip install pxos`).

**Tradeoffs:**
- Gains: Immediate indexing by modern AI crawlers (Claude, ChatGPT, Perplexity), 1-line bootstrap across Bash, PowerShell, and Python, zero external runtime dependencies, viral repository backlinks.
- Cost: Requires maintaining synchronization between core docs and `llms-full.txt` (automated via `scripts/generate-llms-txt.py`).

**Impact:**
Added `llms.txt`, `llms-full.txt`, `install.ps1`, `pyproject.toml`, `pxos/`, `docs/LAUNCH_WHITEPAPER.md`, `.github/` templates, and updated `README.md` and `CHANGELOG.md` to v2.3.0.

**Status:** Active

---

**Decision:**
Implement a pure Python 3 standard library monitoring utility (`scripts/pxos-telemetry-monitor.py`) to poll `https://telemetry.madebypx.com` (`/api/v1/health` and `/api/v1/stats`) for daemon stability, ping latency, and real-time community submission tracking.

**Context:**
Following the deployment of the PXOS empirical research daemon, maintainers and automated pipelines needed a zero-friction mechanism to verify daemon health, check SLA latency thresholds, and monitor incoming benchmark submission counts without direct SSH or database access to production.

**Options considered:**
- Option A — Full APM agent integration (Prometheus client, Datadog): Rejected due to heavy external dependencies violating the PXOS core philosophy of minimal, standalone tooling.
- Option B — Simple curl one-liners in documentation: Rejected because curl does not provide cross-platform parsing, delta calculation, SLA assertions, or structured JSON reporting across Windows and Unix environments.
- Chosen: Option C — Zero-dependency Python standard library CLI with dual output modes (ANSI terminal dashboard with `--watch` and machine-readable `--json` assertions).

**Tradeoffs:**
- Gains: Immediate zero-dependency portability across any machine with Python 3, cross-platform terminal formatting, robust error containment, and CI assertion capability.
- Cost: Relies on client-side polling rather than push-based websockets/SSE.

**Impact:**
Adds `scripts/pxos-telemetry-monitor.py` and documents the monitoring recipes in `WORKFLOWS.md` and `README.md`.

**Status:** Active

---

**Decision:**
Transition repository licensing from permissive MIT to Business Source License 1.1 (BSL-1.1) governed by PROJECT/X, protecting against unauthorized commercial exploitation while keeping the framework completely free for development, internal operations, and commercial software projects.

**Context:**
As PXOS prepares for public distribution (GitHub Release v2.3.0, PyPI packaging, Hacker News and Reddit syndication), permissive MIT licensing introduced a critical vulnerability: third parties or competitors could re-package the governance layer, strip PROJECT/X attribution, or sell a competing hosted/managed platform without legal recourse. The author and PROJECT/X required a licensing model that shields commercial intellectual property while preserving zero-friction adoption for individual developers, teams, and enterprises.

**Options considered:**
- Option A — Closed Source / Proprietary (All Rights Reserved): Rejected because it destroys developer trust and virality in open AI developer communities (Hacker News, Reddit).
- Option B — Retain MIT License: Rejected because it grants third parties complete permission to commercialize, close-source, or fork PXOS as a competing paid service without compensation or attribution.
- Chosen: Option C — Business Source License 1.1 (BSL-1.1) by PROJECT/X. Developers and companies enjoy unrestricted free use to build, test, and govern their own software. Competing managed services or standalone resale require a commercial license from PROJECT/X.

**Tradeoffs:**
- Gains: Total protection of PROJECT/X intellectual property, preventing unauthorized competing commercial SaaS products while granting full freedom for developer and enterprise adoption.
- Cost: Not classified as OSI-approved open source (categorized as Source-Available / Fair-Code), consistent with industry standards adopted by Sentry, CockroachDB, and Redis.

**Impact:**
Updated `LICENSE`, `pyproject.toml`, `pxos/__init__.py`, `README.md`, `llms.txt`, `llms-full.txt`, `templates/site/`, `docs/LAUNCH_KIT.md`, and `docs/LAUNCH_WHITEPAPER.md`.

**Status:** Superseded by 2026-09-04 Apache-2.0 transition

---

**Decision:**
Enforce strict sanitized-only payload persistence in SQLite, in-memory aggregation parsing, and self-contained PyPI package data distribution (`templates/` and `scripts/` inside `pxos/`).

**Context:**
A full codebase audit on 2026-09-04 identified 9 security, reliability, packaging, and performance defects across PXOS subsystems:
1. `raw_payload` in `server.py` stored unscrubbed input JSON, risking PII and code leakage.
2. PyPI wheels omitted `templates/` and `scripts/`, causing `pxos benchmark` and offline `pxos init` to fail in production.
3. `aggregate_daily.py` wrote and unlinked temporary JSON files inside the publicly served web directory `PUBLIC_DIR`.
4. Multi-level branch names crashed `pxos-task.sh` / `pxos-task.ps1` during spec creation.

**Options considered:**
- Option A — Rely on client-side sanitization only: Rejected because untrusted clients or third-party agents could still send unvalidated payloads or malicious PII directly to the public API.
- Option B — Keep templates hosted exclusively on GitHub raw: Rejected because offline, enterprise, and air-gapped developer environments fail during `pxos init`.
- Chosen: Option C — Dual-layer enforcement: server-side schema reconstruction for `raw_payload`, in-memory record loading via `load_record_from_dict()`, package data bundling inside `pxos/` via `get_resource_path()`, and multi-slash branch sanitization.

**Tradeoffs:**
- Gains: Guaranteed adherence to privacy invariants (zero PII storage), complete offline portability for `pip install pxos`, leak-free database connection lifecycles, and zero temporary disk thrashing during aggregation.
- Cost: Minor (~50 KB) package size increase for the distribution wheel, which remains lightweight and has zero external dependencies.

**Impact:**
Modified `benchmarks/server.py`, `benchmarks/analyze.py`, `benchmarks/aggregate_daily.py`, `pxos/cli.py`, `pyproject.toml`, `scripts/pxos-benchmark.py`, `scripts/pxos-task.sh`, `scripts/pxos-task.ps1`, `.github/workflows/release.yml`, and created `tests/test_audit_remediation.py`.

**Status:** Active

---

**Decision:**
Enforce mandatory quarantine of all internal, sensitive, draft, marketing, launch copy, sprint tracking, and team-exclusive materials inside `.internal/` (strictly `.gitignore`d). Never place internal or unreleased assets in public repository directories (`docs/`, `templates/`, `scripts/`, or repository root).

**Context:**
Draft launch articles, social media submission copy, internal sprint notes, and team-exclusive strategy documents were inadvertently placed in public documentation paths (`docs/`). This created risk of leaking unreleased materials, exposing team strategy, and cluttering public-facing documentation. The team and author require a strict, non-negotiable boundary: "Coisas INTERNAS ficam no `.internal/`".

**Options considered:**
- Option A — Rely on ad-hoc developer discretion: Rejected because automated agents or contributors may casually place draft or sensitive files into public documentation folders.
- Option B — Encrypted git submodules: Rejected due to unnecessary complexity and toolchain friction for internal notes.
- Chosen: Option C — Mandatory `.internal/` quarantine enforced across global operating rules (`GEMINI.md`), project context (`PROJECT_CONTEXT.md`), operational base rules (`AI_BASE.md`), and repository templates. All internal drafts, marketing copy, launch kits, and team coordination files live exclusively in `.internal/`, which is permanently excluded by `.gitignore`.

**Tradeoffs:**
- Gains: Total protection against accidental leaks of internal strategy, clean public documentation for end users, and clear psychological and technical boundaries for both humans and AI agents.
- Cost: Team members must explicitly use `.internal/` for work-in-progress drafts and internal notes.

**Impact:**
Removed `docs/DEVTO_POST.md` from git tracking, confirmed `.internal/` in `.gitignore`, and codified the invariant in `~/.gemini/GEMINI.md`, `.ai/PROJECT_CONTEXT.md`, `.ai/AI_BASE.md`, and all `templates/.ai/AI_BASE.md`.

**Status:** Active

---

**Decision:**
Implement cryptographic session fingerprint idempotency, objective methodological adherence scoring (Tiers A/B/C), deterministic git metric extraction (`pxos benchmark --extract`), server-side anti-spoofing plausibility filters, and robust statistical aggregation (5% trimmed mean & IQR outlier rejection) for the PXOS empirical benchmarking subsystem.

**Context:**
The `/benchmark` workflow audits empirical developer and AI agent efficiency. However, without server-side verification and client determinism, public telemetry was vulnerable to: (1) Sybil loops and database spam from repeated runs on the same task; (2) exploratory noise from casual repos claiming full framework rigor; (3) LLM estimation hallucinations regarding LOC churn; and (4) malicious or corrupted outlier submissions skewing arithmetic averages.

**Options considered:**
- Option A — Rely solely on client self-reporting and raw arithmetic averages: Rejected because it leaves telemetry vulnerable to spoofing, client hallucinations, Sybil spam, and outlier poisoning.
- Option B — Heavy cryptographic attestation with centralized PKI certificates: Rejected because it violates Critical Invariant INV-003 (Zero External Dependencies) and burdens open-source users with complex key management.
- Chosen: Option C — Zero-dependency multi-layer verifiability engine:
  1. Cryptographic session fingerprint idempotency (`session_fingerprint` UNIQUE with SQLite UPSERT) and project-level submission throttling (max 10/day).
  2. Objective repository adherence scoring (0-100 pts based on `.ai/PROJECT_CONTEXT.md`, specs, Conventional Commits, and ADRs) gating public stats strictly to Tier A (`is_qualified = 1`).
  3. Deterministic git metric extraction via `git diff --numstat` and `git log` (`pxos benchmark --extract`), removing LLM guesswork.
  4. Server-side plausibility constraints rejecting impossible combinations.
  5. Robust statistical aggregation computing medians, 5% trimmed means, and IQR outlier boundaries.
  6. Irreversible project name hashing (`project_hash`) preserving privacy under INV-001.

**Tradeoffs:**
- Gains: Irrefutable, peer-auditable scientific dataset, total immunity to Sybil duplicate inflation, zero LLM guesswork on LOC metrics, and robust statistical immunity to outliers.
- Cost: Client execution requires access to local git plumbing (which falls back gracefully if git is unavailable).

**Impact:**
Modified `benchmarks/server.py`, `benchmarks/analyze.py`, `scripts/pxos-benchmark.py`, `pxos/scripts/pxos-benchmark.py`, `skills/benchmark/SKILL.md`, and created `tests/test_telemetry_integrity.py`.

**Status:** Active


