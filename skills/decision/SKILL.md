---
name: decision
description: "PXOS /decision workflow: Record a durable architectural or product decision (ADR) into .ai/DECISION_LOG.md with zero manual formatting."
---

# /decision — Record an Architectural or Product Decision

Record a durable architectural, technical, or product decision into `.ai/DECISION_LOG.md`.

1. **Capture Decision Context:**
   - Ask me to describe the decision (or infer from recent conversation if already discussed):
     - What was decided?
     - What alternatives were considered and why were they rejected?
     - What are the key tradeoffs and impacts?

2. **Format as Standard ADR:**
   Format the entry matching the schema in `.ai/DECISION_LOG.md`:
   ```markdown
   ## YYYY-MM-DD — [Decision Title]

   **Decision:**
   [What was decided]

   **Context:**
   [Why this was needed and what problem it solves]

   **Options considered:**
   - Option A — [Description and why rejected]
   - Chosen: Option B — [Why selected]

   **Tradeoffs:**
   [Gains vs costs accepted]

   **Impact:**
   [Affected subsystems and files]

   **Status:** Active
   ```

3. **Append to Log:**
   - Append the entry directly to the end of `.ai/DECISION_LOG.md`.
   - Confirm to me that the decision has been permanently recorded and summarize the key invariant.
