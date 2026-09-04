---
name: update
description: "PXOS /update workflow: Upgrade an existing project to the latest PXOS version, updating operating rules and spec templates while preserving custom project context."
---

# /update — Upgrade PXOS to latest version

Upgrade PXOS in this project by following these steps:

1. **Check current PXOS version:**
   - Read the version marker in `.ai/AI_BASE.md` (e.g. `<!-- pxos:version ... -->`).
   - If missing, note that this is a pre-v2.0 project.

2. **Execute safe upgrade:**
   - Run the upgrade command:
     `curl -sSL https://raw.githubusercontent.com/madebypx/PXOS/main/install.sh | bash -s -- --update`

3. **Report upgrade summary:**
   - Confirm that universal operating rules (`.ai/AI_BASE.md`) have been upgraded to the latest version (v2.2.0).
   - Confirm that `.ai/research/` and `.ai/audits/` directories and starter indexes are in place.
   - Confirm that `.ai/specs/TEMPLATE_SPEC.md` includes the Strategic & Audit Alignment block.
   - Confirm that `.ai/PROJECT_CONTEXT.md`, `.ai/DECISION_LOG.md`, and all active specs remain completely preserved.
   - Inform the user that the project is now upgraded to v2.2.0 with native Research, Audits, automated `/decision` ADR logging, empirical `/benchmark` telemetry, and UX review heuristics.
