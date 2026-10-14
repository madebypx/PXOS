# Current Spec — Task T-16: PXOS Swarm Protocol & Boundary Confinement (v2.7.1)
<!-- pxos:spec-version 1.0.0 -->

- **Branch:** `main`
- **Status:** 🎉 Done
- **Assignee / Agent:** Agent Flash / Rodrigo
- **Related Issues / Tasks:** T-16, `pxos add maestri`

---

## Goal

Extend the **Maestri Spatial Canvas Addon** (`pxos add maestri`) with the official **PXOS Swarm Protocol** (v2.7.1): codifying Context Sharding, Single-Target Boundary Locks, Anti-Exploration Prohibitions, Capsule Briefing Schemas, and the Closed Dialectic Review Pipeline (Darwin/Munger/Veritas in 1 synchronous round) without creating a separate framework.

---

## Acceptance Criteria

- [x] Canonical template created in `templates/addons/maestri/.ai/canvas/swarm-protocol.md`.
- [x] Editor rule updated in `templates/addons/maestri/rules/maestri_bridge.md` (Sections 6–9).
- [x] CLI manifest in `pxos/cli.py` (`ADDONS["maestri"]["files"]`) updated to provision `swarm-protocol.md`.
- [x] Package parity verified and synchronized via `scripts/sync-package-data.py` (0 drift).
- [x] Automated test suite expanded in `tests/test_maestri_addon.py` (78 tests passing).
- [x] Audit report generated in `.ai/audits/AUDIT_2026-10-14_SWARM.md` (P0: 0, P1: 0, P2: 0, P3: 0).
- [x] ADR appended chronologically to `.ai/DECISION_LOG.md`.
- [x] Version synchronized to `v2.7.1` across all files, installers, and crawler docs (`llms.txt`).
- [x] Committed and tagged `v2.7.1`, pushed to GitHub, and official GitHub Release published with binary assets.
