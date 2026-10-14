# PXOS Maestri Bridge — Spatial Canvas & Swarm Rules
<!-- pxos:version 2.8.0 -->

This rule governs collaboration when developing inside the **Maestri** spatial canvas environment.
It enforces non-intrusive, bidirectional synchronization between the local Git repository and connected canvas notes/terminals, while providing strict confinement protocols for multi-agent spatial swarms.

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

### Swarm Protocol Board (Roles & Boundaries)
- Synchronize `.ai/canvas/swarm-protocol.md` with the connected canvas card for swarm roles, active boundary locks, and invariant assignments.

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

---

## 6. Swarm Micro-Context & Boundary Confinement (Pillars 1, 3 & 4)

In multi-agent swarm deployments (8+ specialized agents running in parallel), traditional full-context loading causes severe context bloat and tool hunting. All swarm agents must strictly follow:

1. **Context Sharding:**
   - Specialists must NOT read the entire `.ai/` directory tree or full repository context.
   - Each specialist loads ONLY their assigned shard (e.g., UX Lead loads `DESIGN.md`; Solver/Logistics loads `DOMAIN_RULES.md`; Catalog Engineer loads `DATA_MODEL.md`).
2. **Boundary Locks (Strict Write Isolation):**
   - Each specialist is granted write access to **EXATAMENTE um arquivo alvo** (or isolated component directory).
   - Any modification, refactoring, or creation outside the designated boundary is strictly forbidden without architect re-delegation.
3. **Anti-Exploration Prohibition:**
   - Agents are forbidden from performing exploratory workspace discovery (`ls -R`, recursive grepping, probing unrelated `package.json`/configs).
   - All necessary constraints and operational facts must be supplied in the Capsule Briefing.

---

## 7. Capsule Briefing Protocol (Pillar 2)

When the Maestro or Architect delegates tasks to swarm specialists via `maestri ask` or `maestri ask --batch`, every prompt must use the compact Capsule Briefing format:

```text
Capsule:
- [Target]: <Exact target file path or isolated directory>
- [Invariants]: <Active invariant IDs to uphold, e.g. INV-001, INV-002>
- [Context]: <3 to 5 distilled facts/constraints essential for this execution>
- [Report-back]: maestri ask "<Architect Name>" "DONE: [Brief summary and test verification]"
```

Swarm agents receiving a Capsule Briefing must execute immediately against `[Target]` without initiating repository discovery phases.

---

## 8. Closed Dialectic Peer-Review Cycle (Pillar 5)

To prevent circular chatter and endless multi-agent chat loops, the Dialectic Council operates in a closed, single-round synchronous batch:

1. **Synchronous Batch Dispatch:**
   The Maestro sends the combined output of specialists to the review triad in parallel:
   ```bash
   maestri ask --batch '{"Darwin": "Review empirical claims against evidence-matrix.csv...", "Munger": "Attack economic viability and margin cannibalization..."}'
   ```
2. **Specialized Scrutiny:**
   - **Darwin (Empirical Auditor):** Verifies evidence rigor, detects unsupported claims, and checks data integrity.
   - **Munger (Devil's Advocate / Business Stress-Tester):** Attacks incentive alignment, churn risks, operational debt, and unit economics.
3. **Epistemic Synthesis & Verdict (Veritas):**
   - Veritas arbitrates conflicting findings and issues formal verdicts: `RETAIN`, `QUALIFY`, `REANALYZE`, or `REMOVE`.
   - Veritas drafts the *Honest Trade-offs* section and commits durable ADRs directly to `.ai/DECISION_LOG.md`.
4. **Zero Open Chat:**
   Debates are strictly capped at 1 batch review round. There are no iterative conversational counter-arguments between review agents.

---

## 9. Canvas Notes as Live Shared Projections

- Swarm agents should reference the high-level projections on the canvas (`Architecture Board` and `Operational Board`) for global alignment instead of reloading massive raw log files.
- The repository remains the definitive truth; canvas notes serve as low-overhead, synchronized shared memory.
