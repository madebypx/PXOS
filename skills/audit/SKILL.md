---
name: audit
description: "PXOS /audit workflow: Autonomous Principal Auditor workflow to inspect codebase subsystems against quality, security, performance, and memory standards, generating structured findings in .ai/audits/."
---

# /audit — Autonomous Codebase & Subsystem Audit

Act as a Principal Auditor to inspect codebase subsystems against security, memory, performance, and architectural standards.

1. **Determine Scope & Context Protection:**
   - Ask or check which subsystem to inspect (e.g. `auth`, `audio-engine`, `electron-ipc`, `data-layer`, or `full`).
   - **Context Window Protection:** In codebases with multiple modules, always audit modularly:
     - Target one subsystem at a time and write to `.ai/audits/PARTIAL_<subsystem>.md`.
     - For full audits, inspect subsystems sequentially and generate a consolidated summary in `.ai/audits/AUDIT_YYYY-MM-DD.md`.

2. **Inspection Dimensions (Objective & Evidence-Driven):**
   - **Security & Auth:** Hardcoded secrets, input sanitization, injection vectors, unsafe deserialization, exposed IPC/APIs.
   - **Performance & Memory:** Unbounded memory growth, event listeners not cleaned up, unclosed handles/streams, main-thread blocking operations.
   - **Architecture & Invariants:** Boundary violations, circular imports, tightly coupled components, violations of conventions in `PROJECT_CONTEXT.md` or active research invariants.
   - **Reliability & Errors:** Swallowed exceptions, unhandled promises, missing fallback/loading states.
   - **UX & Interaction (if UI):** Destructive actions lacking confirmation, lack of loading indicators.

3. **Format Findings:**
   Each finding must follow the standard structure:
   ```markdown
   ### [CATEGORY-ID]: [Short Title]
   - **Severity:** P0 — Blocker | P1 — Critical | P2 — Major | P3 — Minor
   - **Category:** Security | Performance & Memory | Architecture | Reliability | UX
   - **Location:** `path/to/file.ts#L42-L65`
   - **Description:** [What the defect/risk is and why it matters]
   - **Evidence:** [Exact code snippet or reproduction trace]
   - **Remediation:** [Concrete, minimal fix steps]
   - **Status:** Open
   ```

4. **Output & Summary:**
   - Save the report to `.ai/audits/PARTIAL_<subsystem>.md` or `.ai/audits/AUDIT_YYYY-MM-DD.md`.
   - Provide a concise executive summary to the user:
     - Total findings by severity (P0, P1, P2, P3)
     - Immediate blocking items (if any P0/P1 exist)
     - Recommended next steps (e.g. create task specs to address P0 items)
