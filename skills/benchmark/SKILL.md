---
name: benchmark
description: "PXOS /benchmark workflow: Audit recent session performance, measure token economy, rework ratio, and UX completeness, save structured telemetry cleanly under .ai/audits/, and autonomously dispatch anonymous empirical metrics to the research server upon user consent."
---

# /benchmark — Empirical Performance & Telemetry Audit

Audit development performance on recent tasks, measure token efficiency and UX completeness, generate verifiable benchmark data, and optionally contribute anonymous telemetry to the scientific research study.

---

## Operational Workflow

### 1. Act as Independent Principal Systems Auditor
Examine the active workspace, recent git commits, `.ai/specs/`, and conversation turns for the current or most recent completed task.
Do not flatter or use marketing fluff. Evaluate with objective skepticism.

### 2. Extract Quantitative & Qualitative Telemetry
Collect:
- **Task Metadata:** Task ID, description, complexity tier (`tier_1_micro`, `tier_2_medium`, `tier_3_complex`), and primary subsystem.
- **Token Telemetry:** Total turns, input tokens, output tokens, and framework overhead tokens (`SPEC`, `PLAN`, `COMPACT`).
- **Code Churn / Rework:** Initial lines implemented vs lines modified/deleted in corrective turns.
- **Product Design & UX Completeness:** Universal 5-state coverage (`initial_idle`, `loading_pending`, `empty_data`, `error_recovery`, `destructive_action_guard`) and design token adherence.
- **Architectural Fidelity:** Session amnesia occurrences, ADRs consulted/registered, and audit blockers resolved.
- **Critical Assessment:** Net utility score (-5 to +5), overhead justification, and at least one concrete friction point and one concrete benefit.

### 3. Clean Workspace Storage (Zero Project Pollution)
- **Never pollute the user's project root** with a `benchmarks/` folder or standalone scripts.
- Save the structured JSON audit record inside the existing `.ai/` governance layer:
  ```
  .ai/audits/BENCHMARK_<task_id>.json
  ```
- If the current workspace is the core PXOS framework repository itself, also store in `benchmarks/data/` and run `python benchmarks/analyze.py`.

### 4. Interactive User Consent for Anonymous Research Telemetry
Present the audit summary to the user in chat:
1. Task evaluated & complexity tier.
2. Total tokens & framework overhead percentage.
3. Code churn / rework ratio & UX completeness score.
4. Privacy guarantee: **Strictly numeric metrics and tier enums**. Zero code snippets, file contents, secret keys, or personal identities are transmitted.

Ask the user explicitly for consent:
> *"Deseja que eu transmita estas métricas anônimas para a pesquisa científica do PXOS? (Responda 'sim' ou 'não') / Would you like me to transmit this anonymous telemetry to the PXOS research server? (Reply 'yes' or 'no')"*

### 5. Autonomous Dispatch by the Agent
**CRITICAL:** Do NOT instruct the user to run manual terminal commands. If the user consents:
- The AI agent itself executes the dispatch autonomously using a direct HTTP POST request to:
  `https://telemetry.madebypx.com/api/v1/telemetry`
- Example agent dispatch (cross-platform):
  - Via `curl`:
    ```bash
    curl -s -X POST -H "Content-Type: application/json" -d '<sanitized_json>' https://telemetry.madebypx.com/api/v1/telemetry
    ```
  - Or via Python standard library:
    ```python
    python -c "import urllib.request, json; req = urllib.request.Request('https://telemetry.madebypx.com/api/v1/telemetry', data=json.dumps(<payload>).encode('utf-8'), headers={'Content-Type': 'application/json'}); res = urllib.request.urlopen(req); print(res.read().decode())"
    ```
- Confirm the server's submission status and submission ID back to the user.

---

## Output Summary

Report to the user:
1. Task evaluated and complexity tier.
2. Total tokens and framework overhead percentage.
3. Rework ratio and UX completeness score.
4. Stored local file path in `.ai/audits/BENCHMARK_<task_id>.json`.
5. Dispatch status (Transmitted autonomously with Submission ID, or kept local if declined).
