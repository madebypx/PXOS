# Contributing to PXOS

Thank you for contributing to **PXOS**! PXOS is an open-source, document-driven operating system designed to eliminate token waste, architectural amnesia, and cognitive drift in AI-assisted software development.

We welcome contributions from developers, researchers, and AI agents adhering to the standards outlined below.

---

## Code of Conduct

Be welcoming, constructive, and respectful. Focus on empirical rigor, clarity, and maintainable software design.

---

## Core Priorities for Contributions

1. **Zero Runtime Dependencies**: Core tooling (CLI, installers, task scripts) must rely strictly on standard libraries (Python 3 stdlib, POSIX `sh`, PowerShell `pwsh`). Avoid introducing external package dependencies (`npm`, `pip`) unless explicitly approved for optional laboratory plugins.
2. **Context Efficiency**: Keep documentation, templates, and specifications token-dense and free of marketing fluff.
3. **Strict Workflow Adherence**: All non-trivial PRs touching PXOS should have followed the 6-phase lifecycle:
   ```
   Discover → Plan → Execute → Validate → Review → Compact
   ```
4. **Git Commit Messages**: Follow the [Conventional Commits](https://www.conventionalcommits.org/) format in English:
   - `feat: add support for ...`
   - `fix: correct parsing of ...`
   - `docs: update workflow guide for ...`
   - `chore: update dependencies or scripts`

---

## Ways to Contribute

### 1. Empirical Telemetry Benchmarks
Help grow the public benchmark dataset by auditing your real-world coding sessions:
- Run `/benchmark` at the end of a session in any PXOS-governed project.
- Submit the anonymous metrics to the public research laboratory via `scripts/pxos-benchmark.py`.
- Open a PR to update `benchmarks/data/` if submitting historical batches.

### 2. IDE Rules & Slash Command Skills
- Improve templates in `templates/rules/` for new or emerging AI coding environments.
- Author or refine slash command skills in `skills/` adhering to the PXOS discipline.

### 3. Cross-Platform Scripting
- Ensure parity between POSIX bash (`scripts/*.sh`, `install.sh`) and PowerShell (`scripts/*.ps1`, `install.ps1`).

---

## Development & Testing Workflow

1. **Fork and Clone**:
   ```bash
   git clone https://github.com/madebypx/PXOS.git
   cd PXOS
   ```
2. **Validate LLM Indexability Files**:
   After modifying any core documentation or specifications, verify that `llms.txt` and `llms-full.txt` remain synchronized:
   ```bash
   python scripts/generate-llms-txt.py --check
   ```
3. **Test Installers**:
   - On Linux/macOS: `bash -n install.sh`
   - On Windows: `pwsh -File .\install.ps1 -Version`
   - Python CLI: `python -m pxos.cli --help`

---

## Submitting a Pull Request

1. Create a descriptive feature branch:
   ```bash
   git checkout -b feat/your-feature-name
   ```
2. Ensure your changes follow existing naming conventions and pass local checks.
3. Submit the Pull Request using our [PR Template](.github/PULL_REQUEST_TEMPLATE.md).
