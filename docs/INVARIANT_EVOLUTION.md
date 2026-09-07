# Closed-Loop Invariant Evolution & Cognitive Post-Mortem Engine
<!-- pxos:version 2.5.0 -->

The **Closed-Loop Invariant Evolution Engine** is a self-healing governance mechanism within the PXOS framework. It permanently converts coding mistakes, context drift, and agent hallucinations into durable, testable rules recorded in `.ai/PROJECT_CONTEXT.md`.

---

## 1. The Core Philosophy

AI coding assistants are extremely fast, highly capable executors with limited and lossy working context. When an agent experiences excessive rework or breaks existing behavior, it is almost never an isolated syntax error. Rather, it is the result of one of three systemic cognitive blind spots:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        THE 3 ROOTS OF AGENT DRIFT                       │
├────────────────────────────┬────────────────────────────┬───────────────┤
│ 1. Local CRUD Bias         │ 2. Context Economy Paradox │ 3. Completion │
│    vs. Distributed System  │    (Invented Constants)    │    Sycophancy │
│                            │                            │               │
│ Mutating one local table   │ Guessing a threshold or    │ Claiming 100% │
│ while ignoring background  │ cooldown to save tokens    │ based only on │
│ sync, watchers, or nodes.  │ instead of reading rules.  │ syntax build. │
└────────────────────────────┴────────────────────────────┴───────────────┘
```

Without closed-loop feedback, the same cognitive failures repeat across subsequent turns and future sessions. With **Closed-Loop Invariant Evolution**, every failure pattern is diagnosed, synthesized into an atomic invariant, confirmed by the human developer, and permanently remembered.

---

## 2. Invariant Lifecycle

```
[ Session Execution ]
         │
         ▼
[ Git Metric Extraction ] ───> Rework Ratio = Lines Churned / Lines Touched
         │
         ├────────────────────> If Rework Ratio <= 20%: Standard Clean Review
         │
         ▼ If Rework Ratio > 20%
[ Cognitive Post-Mortem ] ───> pxos-invariant.py diagnoses failure mode
         │
         ▼
[ Invariant Synthesis ]   ───> Generates candidate: INV-006 (Canonical Constants)
         │
         ▼
[ Human Gate / Confirm ]  ───> Developer approves, refines, or dismisses
         │
         ▼ (Approved)
[ Safe Injection ]        ───> Appends to ## Critical invariants in PROJECT_CONTEXT.md
         │
         ▼
[ Permanent Memory ]      ───> Loaded at /start on every subsequent session
```

---

## 3. Failure Mode Classification

The engine classifies rework into three distinct cognitive failure categories:

### A. `ASSUMED_CONSTANT`
- **Symptom:** Agent uses magic numbers, invented days (e.g. 35 days vs. canonical 120 days), or assumed statuses to avoid reading the canonical domain definitions.
- **Synthesized Invariant Pattern:**
  `- **INV-### (Canonical Constants):** Never invent or assume business constants, cooldowns, or thresholds without reading their canonical definitions in domain rules.`

### B. `MULTI_NODE_BLINDNESS`
- **Symptom:** Agent updates a local database table or state hook without updating connected sync watchers, IPC bridges, or remote cloud nodes.
- **Synthesized Invariant Pattern:**
  `- **INV-### (Distributed Mutation Lifecycle):** Always trace data mutations across all persistence nodes (local cache, remote database, background sync watchers) before completing updates or deletions.`

### C. `PREMATURE_COMPLETION`
- **Symptom:** Agent declares "100% functional" because `build` exited 0, ignoring empty, loading, error, or confirmation guard states.
- **Synthesized Invariant Pattern:**
  `- **INV-### (Universal State Completeness):** Never declare a frontend feature complete based solely on compilation success without validating empty, loading, error, and destructive action states.`

---

## 4. Standard Invariant Format

All critical invariants in `.ai/PROJECT_CONTEXT.md` must adhere to the standard format:

```markdown
- **INV-### (Short Title):** Imperative statement specifying the exact negative constraint or boundary condition.
```

### Constraints:
1. **Monotonic Sequential Numbering:** Must increment by 1 (`INV-001`, `INV-002`, ...). Gaps or duplicate IDs are rejected.
2. **Imperative Constraint:** Must contain an unambiguous directive keyword (`must`, `never`, `always`, `strictly`).
3. **Token Efficiency:** Must remain concise (<= 3 lines) to avoid context bloat on session startup.

---

## 5. CLI Reference

The invariant engine is built into both `scripts/pxos-invariant.py` and the `pxos` CLI:

### Validate Invariant Integrity
```bash
pxos invariant --check
```
Ensures all IDs are sequential, non-empty, and free of syntax defects.

### List Active Invariants
```bash
pxos invariant --list
```
Prints all active invariants in a structured table.

### Query Next Sequential ID
```bash
pxos invariant --next-id
```
Outputs the next available identifier (e.g. `INV-006`).

### Diagnose & Suggest Invariant
```bash
pxos invariant --suggest --reason "agent assumed 35 days instead of reading canonical rotation rules"
```

### Safely Add an Invariant (Human Gate)
```bash
pxos invariant --add --title "Canonical Domain Constants" --rule "Never assume cooldowns without reading canonical rules."
```
Validates sequential IDs, checks for keyword overlap with existing invariants, and safely injects into `.ai/PROJECT_CONTEXT.md`.

### Repository Health Audit (`doctor`)
```bash
pxos doctor
```
Runs a complete diagnostic suite checking invariant integrity, package parity, AI crawlability indices, and repository cleanliness.
