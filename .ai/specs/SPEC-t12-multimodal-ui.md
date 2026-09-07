# Spec — T-12: Autonomous Multi-Modal UI Verification & Universal 5-State Inspector

- **Branch:** `feat/t12-multimodal-ui` (or `main`)
- **Status:** In Spec
- **Assignee / Agent:** Agent Flash-1 / Rodrigo Pena
- **Related Issues / Tasks:** `.internal/ROADMAP.md`, `skills/audit/SKILL.md`, `skills/benchmark/SKILL.md`

---

## Goal

Incorporate an autonomous visual verification protocol into PXOS `/audit` and `/benchmark`, requiring agents to verify and document the **5 Universal UI States** (`initial_idle`, `loading_pending`, `empty_data`, `error_recovery`, `destructive_action_guard`) before declaring frontend tasks complete, eliminating UI blind spots and broken interactive edge cases.

---

## User Value

- **End Users:** Experience zero broken empty screens, unhandled loading freezes, or missing confirmation prompts on dangerous operations.
- **Product Engineers:** AI agents autonomously generate visual proof (screenshots or structured state audits) rather than declaring "frontend 100% complete" when only the happy path was styled.
- **Design System Consistency:** Standardizes state handling across all PXOS-managed web applications.

---

## Strategic & Audit Alignment

- **Audit Findings Cross-Check:** Clean — Directly builds upon Nielsen's UX Heuristics in `AI_BASE.md` (status visibility, error prevention, cognitive load).
- **Strategic Blueprint Reference:** Horizon 2 of [`.internal/ROADMAP.md`](../../.internal/ROADMAP.md).
- **Critical Invariants Adherence:**
  - `INV-001` (Privacy): Screen captures must never capture unscrubbed production secrets or credentials.
  - `INV-002` (Internal Quarantine): Preserved.
  - `INV-003` (Zero External Core Dependencies): Standard CLI scripts use headless browser automation (Playwright/Puppeteer/Selenium if present, or native OS screenshot tools/HTTP status validation without imposing rigid core package dependencies).

---

## Scope

### In:
1. **Universal 5-State Matrix Definition:**
   - Formalize the 5 universal states in `docs/UI_5_STATES.md` and template rules:
     1. `initial_idle`: Standard populated view.
     2. `loading_pending`: Clear skeleton loaders or disabled buttons with activity indicators.
     3. `empty_data`: Graceful zero-state handling with helpful guidance or CTA.
     4. `error_recovery`: Human-readable error message with retry or recovery pathway.
     5. `destructive_action_guard`: Modal confirmation or undo toast for deletions/overwrites.
2. **Autonomous Multi-Modal Audit Workflow (`skills/audit/SKILL.md`):**
   - When `/audit` inspects a UI component or page, require a structured 5-state checklist table.
   - For subagents with browser capabilities, mandate capturing visual artifacts for each state into `.ai/audits/screenshots/<task_id>/`.
3. **Benchmark Score Integration (`scripts/pxos-benchmark.py`):**
   - Include `ui_states_verified` count (0–5) in `ux_completeness_score` calculation, awarding +10 adherence points when all 5 states are audited.
4. **Starter Templates & Snippets:**
   - Provide standard HTML/CSS/React boilerplate patterns for the 5 states in `templates/ui/`.

### Out:
- Heavy headless browser dependencies bundled directly inside the core `pxos` wheel (maintains `INV-003`; uses optional runner or subagent browser tools).

---

## Constraints

- Zero mandatory external core package dependencies (`INV-003`).
- Works seamlessly in both text-only agents and multi-modal browser-equipped subagents.

---

## Existing Patterns

- Nielsen UX Heuristics check in `AI_BASE.md`.
- Benchmark auditing framework in `skills/benchmark/SKILL.md`.

---

## Proposed Change

1. **`docs/UI_5_STATES.md`:**
   - Documentation guide and reference for the 5 universal states.
2. **`skills/audit/SKILL.md`:**
   - Add Section on Multi-Modal UI Verification requiring the 5-state matrix table.
3. **`scripts/pxos-benchmark.py` & `pxos/scripts/pxos-benchmark.py`:**
   - Add `--verify-ui` flag checking state coverage in audit reports.
4. **`tests/test_multimodal_ui.py`:**
   - Unit tests validating state extraction from audit reports and scoring calculation.

---

## Technical Flow

```
1. Agent completes UI task
2. Agent runs /audit or /benchmark --verify-ui
3. Auditor evaluates UI against 5 Universal States:
   ├── [x] initial_idle: Rendered cleanly with mock data
   ├── [x] loading_pending: Skeleton loader visible on fetch
   ├── [x] empty_data: "No tasks found" banner with "Create Task" button
   ├── [x] error_recovery: Red alert banner with "Retry" trigger on 500
   └── [x] destructive_action_guard: Confirmation dialog before deletion
4. Audit saved in .ai/audits/AUDIT_<date>.md with 5/5 score
5. Benchmark reflects verified UX completeness
```

---

## Acceptance Criteria

- [ ] `docs/UI_5_STATES.md` created with clear specifications and code patterns for all 5 states.
- [ ] `skills/audit/SKILL.md` updated with mandatory 5-state verification protocol for frontend scopes.
- [ ] `scripts/pxos-benchmark.py` supports 5-state scoring in adherence calculation.
- [ ] Unit tests in `tests/test_multimodal_ui.py` pass 100%.

---

## Validation Plan

1. Run test suite against mock audit documents containing partial and complete state matrices.
2. Verify scoring calculation awards appropriate points to Tier A benchmark qualifications.
