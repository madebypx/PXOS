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
