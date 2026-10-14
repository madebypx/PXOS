# PXOS Maestri Bridge — Spatial Canvas & Swarm Rules
<!-- pxos:version 2.7.0 -->

This rule governs collaboration when developing inside the **Maestri** spatial canvas environment.
It enforces non-intrusive, bidirectional synchronization between the local Git repository and connected canvas notes/terminals.

---

## 1. Single Source of Truth (SSOT) Priority

- The local Git repository (`.ai/`, `SPRINT.md`, `.ai/DECISION_LOG.md`, source code) is the **Canonical Source of Truth**.
- Canvas notes, cards, and stacks are **projections (mirrors)** of repository state.
- In any case of conflict or divergence between a canvas note and a repository file, the local file always wins. Overwrite or sync the canvas note (`maestri note write` / `maestri note edit`), never the reverse without human approval.

---

## 2. Conditional CLI Invocation

- Every Maestri integration action is conditional upon verifying that `maestri` (or `$MAESTRI_CLI`) exists.
- If `maestri` is unavailable or fails, fall back silently to standard PXOS Git worktree workflows and terminal output without throwing errors.

---

## 3. Real-Time Telemetry & Phase Reporting

During the standard PXOS 6-phase lifecycle (`Discover → Plan → Execute → Validate → Review → Compact`):

- **Interim Progress Updates:**
  Emit non-intrusive progress updates on phase boundaries using:
  ```bash
  maestri say --progress 'Phase: [Discover|Plan|Execute|Validate|Review|Compact] — [Status]'
  ```
  *Note:* Never use plain `maestri say` for interim status to avoid polluting the user's permanent chat history.

- **Completion & Milestones:**
  When an entire task or sprint phase is completed, deliver the structured summary directly or via:
  ```bash
  maestri say --progress 'Phase: Compact — SPRINT & ADR synchronized with canvas'
  ```

---

## 4. Canvas Note Mirroring (Bidirectional Hygiene)

### Operational Board (Sprint & Task Matrix)
- When `SPRINT.md` or `.ai/CURRENT_SPEC.md` is updated:
  1. Inspect connected notes using `maestri list`.
  2. Locate the connected operational note (e.g., `"Operational Board"` or `"Partitura Operacional"`).
  3. If the note is marked `locked: true`, do not attempt to write to it.
  4. If unlocked, use `maestri note edit` or `maestri note write` to update the specific task status row, keeping other agents' entries intact.

### Architecture Board (Durable Decisions / ADRs)
- When a durable ADR is logged via `/decision` or `/compact` into `.ai/DECISION_LOG.md`:
  1. Locate the architecture note on the canvas (e.g., `"Architecture Board"` or `"Partitura Técnica"`).
  2. Append an executive ADR summary:
     ```markdown
     ### YYYY-MM-DD — [Decision Title]
     - **Decision:** [What was chosen]
     - **Tradeoffs:** [Key tradeoffs accepted]
     - **Impact:** [Subsystems touched]
     ```

---

## 5. Parallel Swarm Task Orchestration (/plan Phase)

When formulating an implementation plan in `/plan` for complex, parallelizable tasks:

1. **Teammate Inspection:**
   Run `maestri list` to inspect connected teammates and existing agent terminals.

2. **Role & Floor Assignment:**
   - **Architect (Maestro):** Retains high-level governance, `/spec`, and `/plan` orchestration.
   - **Executors:** Pinned strictly to their own Git worktrees (`--floor <Floor>` or `--dir <Path>`).
   - **Auditor / Sentinel:** Runs autonomous regression test suites and `/audit`.

3. **Batch Task Dispatch:**
   If multiple independent sub-tasks were approved by the developer, dispatch them in parallel:
   ```bash
   maestri ask --batch '{"Executor A": "<prompt & worktree spec>", "Executor B": "<prompt & worktree spec>"}'
   ```

4. **Mandatory Ask-Back Etiquette:**
   Every delegated prompt MUST end with an explicit report-back command:
   ```
   When finished, report your verified findings via: maestri ask "<Architect Name>" "DONE: [Brief summary and test verification]"
   ```
   Do not poll terminals in a tight loop. Wait for the ask-back notification.
