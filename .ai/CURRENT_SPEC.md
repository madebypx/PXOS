# Current Spec — Task T-15: PXOS Evidence Addon (`pxos add evidence`)
<!-- pxos:spec-version 1.0.0 -->

- **Branch:** `feat/evidence-addon`
- **Status:** 🎉 Done
- **Assignee / Agent:** Agent Flash / Rodrigo
- **Related Issues / Tasks:** T-15, `.ai/specs/SPEC-evidence-addon.md`

> **Active Spec Pointer:** Detailed requirements and acceptance criteria are maintained in [.ai/specs/SPEC-evidence-addon.md](.ai/specs/SPEC-evidence-addon.md).

---

## Goal

Create the first official modular addon for PXOS: the **Evidence Addon** (`pxos add evidence` / `pxos init --evidence`), adding scientific governance, an Evidence-First research protocol (DSR / Case Studies), 5-layer epistemic separation, structured audit matrices, and an Adversarial Reviewer workflow (`/peer-review`) without bloating PXOS core.

---

## Acceptance Criteria

- [x] Canonical Addon templates created in `templates/addons/evidence/` (protocol, governance, adversarial reviewer, CSV registers, negative cases, rejected claims, IDE rule).
- [x] Global skill created in `skills/peer-review/SKILL.md`.
- [x] CLI evolved in `pxos/cli.py` with `pxos add <addon>` and `pxos init --evidence`.
- [x] Package data mirrored via `scripts/sync-package-data.py` to `pxos/templates/addons/evidence/`.
- [x] Comprehensive unit tests added in `tests/test_evidence_addon.py`.
- [x] `scripts/sync-package-data.py --check` and `pxos doctor` pass cleanly.
- [x] Documentation updated in `README.md` and `CHANGELOG.md`.
