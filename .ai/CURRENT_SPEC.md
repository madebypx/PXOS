# Current Spec — PXOS AI Indexability & Zero-Friction Distribution Engine
<!-- pxos:version 2.2.0 -->

This file defines the active task or feature. Replace it entirely when starting a new task. The AI reads this file at the start of every session to understand what is being built.

---

## Goal

Implement the technical foundations for public AI crawlability, standard LLM consumption (`llms.txt`), repository backlink viral loops, and zero-friction cross-platform distribution (PowerShell installer + PyPI `pxos` CLI) to maximize global indexing across AI training corpora and developer tools.

---

## User value

- **Native AI Comprehension:** Any AI agent or web crawler (Claude, ChatGPT, Perplexity, Cursor) browsing PXOS immediately digests the architecture via standardized `/llms.txt` and dense semantic text without parsing HTML.
- **Zero-Friction Adoption:** Developers can initialize PXOS in any project in one single command on Windows, macOS, or Linux (`pip install pxos`, `install.sh`, or `install.ps1`) without manual repository cloning.
- **Organic Indexing Loop:** Downstream repositories adopting PXOS propagate backlinks via official badges and structured metadata, populating search engines and future LLM training datasets (e.g. The Stack, GitHub public archives).
- **Public Authority:** Ready-to-publish technical whitepaper highlighting empirical benchmarks (80% token reduction) positions PXOS as a premier document-driven governance layer.

---

## Strategic & Audit Alignment

- **Audit Findings Cross-Check:** Clean — No active audit blockers touching this scope.
- **Strategic / Research Reference:** Aligns with PXOS Core Priorities (Correctness, Clarity, Simplicity, Context Efficiency, Zero External Dependencies) and empirical benchmark distribution (`benchmarks/REPORT.md`).

---

## Scope

**In:**
1. **AI Indexability Standard (`llms.txt` & `llms-full.txt`):**
   - Create root `llms.txt` (curated index of core principles, workflows, and CLI specs adhering to `llmstxt.org`).
   - Create `llms-full.txt` (single-file dense documentation of PXOS ready for direct LLM agent ingestion).
   - Create `scripts/generate-llms-txt.py` to autonomously compile and validate these files.
2. **Cross-Platform Zero-Friction Bootstrap:**
   - Native Windows PowerShell installer `install.ps1` matching `install.sh` functionality.
   - Python package structure (`pyproject.toml`, `pxos/`) providing the global `pxos` CLI (`pxos init`, `pxos update`, `pxos benchmark`, `pxos monitor`) with zero runtime dependencies.
3. **Viral Adoption Loops & Community Infrastructure:**
   - Standardized README badges for downstream projects (`Governed by PXOS`, `PXOS Inside`).
   - GitHub community templates (`.github/ISSUE_TEMPLATE/`, `.github/PULL_REQUEST_TEMPLATE.md`, `.github/CONTRIBUTING.md`).
4. **Technical Authority Whitepaper:**
   - Publication-ready essay `docs/LAUNCH_WHITEPAPER.md` for Hacker News, Dev.to, and Reddit.
5. **SEO & Structured Metadata:**
   - Schema.org JSON-LD and OpenGraph metadata template for `pxos.madebypx.com`.

**Out:**
- External third-party dependencies (strictly pure Python stdlib, POSIX sh, pwsh).
- Manual off-platform social media account management.

---

## Constraints

- Pure standard library Python 3 (zero `pip` dependencies at runtime).
- Strict adherence to `llmstxt.org` specification.
- Full parity between `install.sh` and `install.ps1`.
- Clean backward compatibility for existing PXOS projects.

---

## Existing patterns

- `install.sh`: structured CLI flag parsing, markers for `.cursorrules`, `.ai/` bootstrapping.
- `scripts/pxos-benchmark.py` and `scripts/pxos-telemetry-monitor.py`: ANSI color helpers, zero external deps, argparse architecture.
- `benchmarks/REPORT.md`: empirical benchmark source for whitepaper and `llms.txt`.

---

## Proposed change

1. Author `llms.txt` and `llms-full.txt` with autonomous generation script `scripts/generate-llms-txt.py`.
2. Author `install.ps1` replicating all `install.sh` features for PowerShell environments.
3. Author `pyproject.toml` and `pxos/` package CLI module.
4. Author community health files in `.github/` and `CONTRIBUTING.md`.
5. Update `README.md` with downstream badges and new installation options.
6. Author `docs/LAUNCH_WHITEPAPER.md` and `templates/site/metadata.json`.

---

## Acceptance criteria

- [x] `llms.txt` and `llms-full.txt` exist and pass specification validation.
- [x] `scripts/generate-llms-txt.py` runs cleanly and updates files idempotently.
- [x] `install.ps1` executes successfully in PowerShell, creating `.ai/` and supporting `--ide` and `--update` flags.
- [x] `pyproject.toml` and `pxos` package CLI provide `pxos init`, `pxos update`, `pxos benchmark`, `pxos monitor`.
- [x] Community templates (`CONTRIBUTING.md`, issue/PR templates) exist and are properly formatted.
- [x] Downstream badges documented in `README.md` with rendered markdown snippets.
- [x] `docs/LAUNCH_WHITEPAPER.md` written with technical depth and benchmark evidence.
- [x] All automated validations pass with exit code 0.

---

## Validation plan

1. Run `py scripts/generate-llms-txt.py` and verify file content integrity. (Passed)
2. Execute `pwsh -File .\install.ps1 -TestPath "$env:TEMP\pxos_test_ps1"` and verify generated structure. (Passed)
3. Test `python -m pxos.cli --help` and verify subcommands. (Passed)
4. Verify `install.sh` syntax with `bash -n install.sh`. (Passed)

---

## Workflow state

- **Current phase:** Done
- **Pending decision:** None
- **Execution blocked until:** None
