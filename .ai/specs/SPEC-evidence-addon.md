# Spec — T-15: PXOS Evidence Addon (`pxos add evidence`)

- **Branch:** `feat/evidence-addon`
- **Status:** 🎉 Done
- **Assignee / Agent:** Agent Flash / Rodrigo
- **Related Issues / Tasks:** T-15

---

## Goal

Create the first official modular addon for PXOS: the **Evidence Addon** (`pxos add evidence` / `pxos init --evidence`), adding scientific governance, an Evidence-First research protocol (DSR / Case Studies), 5-layer epistemic separation, structured audit matrices, and an Adversarial Reviewer workflow (`/peer-review`) without bloating PXOS core.

---

## User value

Engineers, researchers, and AI agents conducting complex investigations or architectural trade-offs can install rigorous epistemic governance on demand. LLM sycophancy and unsubstantiated conclusions are eliminated through strict gatekeeping (`INSUFFICIENT EVIDENCE — DO NOT CONCLUDE`), reproducible CSV registers, and adversarial stress-testing.

---

## Strategic & Audit Alignment

- **Audit Findings Cross-Check:** Clean — No active audit blockers touching this scope. Adheres strictly to `INV-001` (Privacy), `INV-002` (Internal Quarantine), `INV-003` (Zero External Dependencies: pure Python 3 stdlib), and `INV-004` (Conventional Commits).
- **Strategic / Research Reference:** Builds upon `.ai/research/INDEX.md` and establishes `.ai/research/00-governance/`.

---

## Scope

**In:**
1. Canonical Addon templates in `templates/addons/evidence/`:
   - `.ai/research/00-governance/research-protocol.md` (FAIR principles, 5 epistemic layers, double-stage approval gates).
   - `.ai/research/00-governance/ai-governance.md` (Evidence-First Research Agent system prompt, zero hallucination of DOIs/quotes, structured analytical response format).
   - `.ai/research/00-governance/adversarial-reviewer.md` (Adversarial Methodological Reviewer system prompt, confirmation bias hunting, 5 canonical verdicts: REMOVE, QUALIFY, VERIFY, REANALYZE, RETAIN).
   - `.ai/research/evidence-matrix.csv` (headers: `id,claim,classification,source_id,source_location,supporting_excerpt,evidence_strength,limitations,verification_status`).
   - `.ai/research/source-register.csv` (headers: `id,source_title,author_or_institution,year,type,url_or_filepath,access_date,verification_status,notes`).
   - `.ai/research/negative-cases.md` (counterevidence register and threats to validity).
   - `.ai/research/rejected-claims.md` (refuted claims ledger preventing cognitive regression).
   - `rules/evidence_first_research.md` (IDE rule template for evidence governance).
2. Global Skill in `skills/peer-review/SKILL.md`:
   - Frontmatter and prompt instructions for adversarial review of research claims, logical leaps, and source audit against `evidence-matrix.csv`.
3. CLI evolution in `pxos/cli.py`:
   - `pxos add <addon>` command supporting `evidence`.
   - `pxos init --evidence` flag to scaffold both core and evidence addon in one command.
   - Idempotent copy from local resources/raw fallback to target `.ai/research/` and editor rules without clobbering existing files.
4. Package parity & validation:
   - Sinking templates into `pxos/templates/addons/evidence/` via `scripts/sync-package-data.py`.
   - Unit tests in `tests/test_evidence_addon.py`.
   - Documentation updates in `README.md` and `CHANGELOG.md`.

**Out:**
- Modifying core PXOS `templates/.ai/AI_BASE.md` defaults (evidence remains an opt-in addon).
- Third-party Python dependencies (remains pure stdlib `shutil`, `urllib`, `pathlib`, `argparse`).

---

## Constraints

- Zero external dependencies (`INV-003`).
- Idempotency: `pxos add evidence` must not overwrite pre-existing user files without warning, preserving any existing `.ai/research/INDEX.md` or existing CSV rows.
- IDE integration must use non-conflicting blocks (`<!-- pxos:evidence:start -->` ... `<!-- pxos:evidence:end -->`).
- All tests must pass with `py -3.10 -m unittest discover tests`.

---

## Acceptance criteria

- [x] `templates/addons/evidence/` contains all 8 required files/templates.
- [x] `skills/peer-review/SKILL.md` contains valid YAML frontmatter and structured review instructions.
- [x] `pxos add evidence` scaffolds `.ai/research/` governance and matrix files and attaches IDE rules.
- [x] `pxos init --evidence` initializes PXOS and installs the evidence addon seamlessly.
- [x] `scripts/sync-package-data.py --check` passes with zero parity drift.
- [x] `tests/test_evidence_addon.py` passes with 100% assertions across CLI commands, flags, and idempotent operations.
- [x] `pxos doctor` passes cleanly.
