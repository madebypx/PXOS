---
name: benchmark
description: "PXOS /benchmark workflow: Audit recent session performance, measure token economy, rework ratio, and UX completeness, save structured telemetry in benchmarks/data/, and optionally dispatch anonymous empirical data to the research server."
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
- **Task Metadata:** Task ID, description, complexity tier (`tier_1_micro`, `tier_2_medium`, `tier_3_complex`), and subsystem.
- **Token Telemetry:** Total turns, input tokens, output tokens, and documentation overhead tokens (`SPEC`, `PLAN`, `COMPACT`).
- **Code Churn / Rework:** Initial lines implemented vs lines modified/deleted in corrective turns.
- **Product Design & UX Completeness:** Universal 5-state coverage (`initial_idle`, `loading_pending`, `empty_data`, `error_recovery`, `destructive_action_guard`) and design token adherence.
- **Architectural Fidelity:** Session amnesia occurrences, ADRs consulted/registered, and audit blockers resolved.
- **Critical Assessment:** Net utility score (-5 to +5), overhead justification, and at least one concrete friction point and one concrete benefit.

### 3. Generate Local JSON Record
Format the result matching the schema in `benchmarks/AGENT_INTERVIEW_PROTOCOL.md` and save to:
```
benchmarks/data/task_<task_id>.json
```

### 4. Run Local Benchmark Analysis
Run the local analysis engine to update your repository's empirical report:
```bash
python benchmarks/analyze.py --input benchmarks/data/ --report benchmarks/REPORT.md --json benchmarks/summary.json
```

### 5. Privacy & Optional Research Telemetry Dispatch
Run the benchmark dispatcher helper:
```bash
python scripts/pxos-benchmark.py --file benchmarks/data/task_<task_id>.json
```
- The script displays the sanitized numerical payload preview.
- It guarantees zero code snippets, passwords, or personal identities are transmitted.
- It prompts the user for explicit consent (`[y/N]`) before any network transmission occurs.

---

## Output Summary

Report to the user:
1. Task evaluated and complexity tier.
2. Total tokens and framework overhead percentage.
3. Rework ratio and UX completeness score.
4. Stored local file path in `benchmarks/data/`.
5. Status of local report update and optional telemetry dispatch.
