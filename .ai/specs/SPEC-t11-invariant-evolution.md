# Spec — T-11: Closed-Loop Invariant Evolution & Cognitive Post-Mortem Engine

- **Branch:** `feat/t11-invariant-evolution` (or `main`)
- **Status:** In Spec
- **Assignee / Agent:** Agent Flash-1 / Rodrigo Pena
- **Related Issues / Tasks:** `.internal/postmortem_ai_cognition_and_pxos.md`, `.internal/ROADMAP.md`, `T-08`, `T-09`

---

## Goal

Create a self-healing governance mechanism within PXOS that automatically detects cognitive drift and high rework (`rework_ratio > 20%`) during `/review` and `/compact`, diagnoses the root failure cause (CRUD bias, unstated constants, or multi-node blindness), and autonomously synthesizes atomic, human-confirmed `INV-xxx` invariants for insertion into `.ai/PROJECT_CONTEXT.md`.

---

## User Value

- **Developers & Teams:** Never suffer from the same agent hallucination or architectural regression twice. Project mistakes convert permanently into durable rules.
- **AI Coding Agents:** Receive concise, unambiguous negative constraints (`never assume...`) loaded on every session `/start`, preventing token waste and rework loops.
- **Framework Maintainers:** Transforms empirical telemetry (`rework_turn_count`, `churn`) from passive metrics into proactive self-improving prompt engineering.

---

## Strategic & Audit Alignment

- **Audit Findings Cross-Check:** Clean — No active audit blockers touching this scope. Builds upon Completion Honesty Protocol and No-Assumption Clause introduced in v2.4.0.
- **Strategic Blueprint Reference:** Implements Section 5 of [`.internal/postmortem_ai_cognition_and_pxos.md`](../../.internal/postmortem_ai_cognition_and_pxos.md) and Horizon 1 of [`.internal/ROADMAP.md`](../../.internal/ROADMAP.md).
- **Critical Invariants Adherence:**
  - `INV-001` (Telemetry Privacy): Invariant evolution operates strictly on local diffs and metrics; no proprietary code is uploaded.
  - `INV-002` (Internal Quarantine): Preserved.
  - `INV-003` (Zero External Core Dependencies): Standard Python stdlib (`re`, `json`, `pathlib`, `subprocess`).
  - `INV-004` (Conventional Commits): Standard English commit format.
  - `INV-005` (Append-Only Decision Log): New durable invariants and ADRs recorded chronologically.

---

## Scope

### In:
1. **Rework Spike Detection Trigger (`skills/review/SKILL.md` & `skills/compact/SKILL.md`):**
   - Automatically calculate or query local task churn: if `rework_ratio > 0.20` (or `rework_turn_count >= 2`), activate Cognitive Post-Mortem protocol.
2. **Cognitive Drift Diagnostic Engine (`scripts/pxos-invariant.py`):**
   - Inspect the git diff and commit history to classify the error pattern:
     - *Pattern A (Assumed Constant / Value Drift):* Hardcoded threshold or status not present in `PROJECT_CONTEXT.md`.
     - *Pattern B (Partial CRUD / Multi-Node Blindness):* Mutated one state source while neglecting related storage or background sync processes.
     - *Pattern C (Premature Completion):* Build passed but spec criteria were missing.
3. **Atomic Invariant Synthesizer:**
   - Format proposed invariant adhering to PXOS standard:
     `- **INV-### (Short Title):** Imperative statement prohibiting the failure mode, citing the exact boundary.`
4. **Interactive Confirmation & Safe Injection:**
   - Present candidate `INV-###` to the human developer during `/compact` or `/review`.
   - Upon confirmation, safely append the invariant into `.ai/PROJECT_CONTEXT.md` under `## Critical invariants` with automatic index incrementation.
5. **CLI Integration (`pxos invariant` or `pxos doctor`):**
   - CLI command to audit existing invariants in `.ai/PROJECT_CONTEXT.md`, ensure sequential numbering, and verify that universal rules (`AI_BASE.md`) are satisfied.

### Out:
- Autonomous modification of `.ai/PROJECT_CONTEXT.md` without explicit human confirmation (strictly prohibited by governance).
- Cloud-based LLM fine-tuning or remote rule ingestion.

---

## Constraints

- Zero external dependencies (`INV-003`).
- Invariant IDs must be monotonically sequential (`INV-001`, `INV-002`, ... `INV-006`).
- Max length of synthesized invariant: <= 3 lines to maintain token economy.

---

## Existing Patterns

- Invariant declaration block in `.ai/PROJECT_CONTEXT.md`.
- Deterministic churn calculation in `scripts/pxos-benchmark.py`.
- Skill operational workflows in `skills/review/SKILL.md` and `skills/compact/SKILL.md`.

---

## Proposed Change

1. **`scripts/pxos-invariant.py`:**
   - CLI utility to parse, check, and safely insert `INV-xxx` entries into `.ai/PROJECT_CONTEXT.md`.
2. **`skills/review/SKILL.md` & `WORKFLOWS.md`:**
   - Add post-mortem trigger check when rework lines exceed 20% of total diff.
3. **`skills/compact/SKILL.md`:**
   - Add prompt instruction to synthesize and propose an invariant candidate if rework occurred during the session.
4. **`pxos/cli.py`:**
   - Expose `pxos invariant --check` and `pxos invariant --add`.
5. **`tests/test_invariant_evolution.py`:**
   - Automated unit tests for ID extraction, formatting validation, and injection idempotency.

---

## Technical Flow

```
1. Developer runs /review or /compact after session with rework
2. System checks git diff: rework_ratio = lines_deleted_or_modified / lines_total
3. If rework_ratio > 0.20:
   ├── Trigger Cognitive Drift Diagnoser
   ├── Classify root cause (Assumed Constant / Multi-Node / Premature Completion)
   └── Propose Candidate: "- **INV-006 (Quarantine Period):** Minimum territory quarantine must always..."
4. Developer approves or edits proposal
5. Script pxos-invariant.py appends candidate to .ai/PROJECT_CONTEXT.md
6. Invariant is immediately active for all subsequent /start sessions
```

---

## Edge Cases

- **Legitimate Heavy Refactoring:** User intentionally deletes and rewrites old code.
  - *Mitigation:* Agent asks developer if rework was due to an agent cognitive error before synthesizing an invariant.
- **Invariant Duplication:** Candidate rule overlaps with existing `INV-xxx`.
  - *Mitigation:* Script performs substring and keyword similarity check against existing invariants.

---

## Acceptance Criteria

- [x] `scripts/pxos-invariant.py` implements parsing, sequential ID assignment, and validation for `PROJECT_CONTEXT.md`.
- [x] `skills/review/SKILL.md` and `skills/compact/SKILL.md` include the Closed-Loop Invariant check on `rework_ratio > 20%`.
- [x] `pxos invariant --check` and `pxos invariant --add` exposed via `pxos/cli.py`.
- [x] Proposed invariants strictly adhere to the single-sentence imperative standard.
- [x] Full unit test suite in `tests/test_invariant_evolution.py` passes 100%.

---

## Validation Plan

1. Test CLI parsing on valid and invalid `PROJECT_CONTEXT.md` files.
2. Test sequential ID generation (`INV-006`, etc.).
3. Test simulation with simulated rework session.

---

## Workflow State

- **Current phase:** Done
- **Pending decision:** None
- **Execution blocked until:** None
