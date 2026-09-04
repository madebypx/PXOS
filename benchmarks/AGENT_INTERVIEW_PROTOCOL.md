# PXOS Agent Interview & Empirical Elicitation Protocol
<!-- pxos:benchmark:protocol:v1.0.0 -->

## Objective

This protocol defines the standardized interview prompts, scoring rubrics, and machine-readable JSON schema used to elicit objective, empirical data from AI agents regarding their operational performance with and without PXOS.

> [!CAUTION]
> **Anti-Sycophancy Directive:** LLMs naturally tend to flatter frameworks and user prompts. This protocol enforces an **Adversarial Auditor framing**: the interviewed agent is explicitly penalized for ungrounded praise and rewarded for identifying friction, token waste, rigid overhead, and factual evidence.

---

## 1. Interview Modes

There are two primary modes for gathering benchmark data:

1. **Mode A — Retrospective Project Audit:** Use this when an agent has already completed work on one or more projects utilizing PXOS. The agent audits its own past session logs, Git commits, and file modifications.
2. **Mode B — Controlled A/B Evaluation:** Use this when conducting a fresh side-by-side experiment comparing a task solved via **Vanilla Chat ($C$)** versus **PXOS ($T$)**.

---

## 2. Standardized JSON Output Schema

When interviewing an agent, it **MUST** respond strictly in the following valid JSON schema. No conversational preamble or postamble is allowed outside the JSON structure.

```json
{
  "$schema": "https://raw.githubusercontent.com/madebypx/PXOS/main/benchmarks/schema.json",
  "audit_metadata": {
    "evaluation_mode": "retrospective | controlled_ab",
    "project_name": "string",
    "evaluator_agent_model": "string (e.g. Claude 3.5 Sonnet, Gemini 2.0 Flash, GPT-4o)",
    "timestamp_iso": "YYYY-MM-DDTHH:MM:SSZ",
    "git_commit_hash": "string (optional)"
  },
  "task_profile": {
    "task_id": "string",
    "task_description": "string",
    "complexity_tier": "tier_1_micro | tier_2_medium | tier_3_complex",
    "primary_subsystem": "frontend | backend | auth | data_model | devops | multi_module"
  },
  "quantitative_telemetry": {
    "total_turns": 0,
    "input_tokens_total": 0,
    "output_tokens_total": 0,
    "framework_overhead_tokens": 0,
    "initial_implementation_loc": 0,
    "rework_lines_modified_or_deleted": 0,
    "rework_turn_count": 0,
    "unresolved_compiler_or_test_failures": 0,
    "merge_conflicts_encountered": 0
  },
  "product_design_and_ux": {
    "ui_components_touched": true,
    "states_evaluated": {
      "initial_idle": true,
      "loading_pending": true,
      "empty_data": true,
      "error_recovery": true,
      "destructive_action_guard": false
    },
    "ux_state_completeness_score": 0.8,
    "design_tokens_adhered": true,
    "nielsen_heuristics_violations_detected": [
      {
        "heuristic_id": "H1 | H5 | H6 | H8",
        "description": "string",
        "file_location": "string"
      }
    ]
  },
  "architectural_fidelity": {
    "session_amnesia_occurred": false,
    "invariants_violated_count": 0,
    "duplicate_utilities_introduced": 0,
    "adrs_consulted_count": 0,
    "new_adrs_registered": 0,
    "audit_findings_resolved": ["string (e.g. SEC-01)"]
  },
  "critical_assessment": {
    "net_utility_score": 0,
    "overhead_justified": true,
    "identified_frictions": [
      "string (concrete critique of where PXOS added unnecessary ceremony or friction)"
    ],
    "concrete_benefits": [
      "string (concrete instance with file citation where PXOS prevented errors or saved tokens)"
    ],
    "evidence_citations": [
      {
        "claim": "string",
        "file_path": "string",
        "line_numbers": "string"
      }
    ]
  }
}
```

---

## 3. Copy-Paste Interview Prompts

### Prompt A: Retrospective Project Audit (For Agents on Existing Projects)

Paste this prompt into the AI agent currently active in a project that uses PXOS:

```markdown
You are acting as an Independent Principal Systems Auditor and Benchmark Researcher.
Your mission is to perform an objective, unvarnished, empirical audit of your recent development work in this repository under the PXOS framework.

CRITICAL INSTRUCTIONS:
1. Do NOT produce flattery, vague praise, or marketing buzzwords. You are being scored on your objectivity, skepticism, and empirical rigor.
2. If PXOS was cumbersome, slow, or wasted tokens on small tasks, you MUST state it explicitly.
3. Every metric and claim you make must be backed by tangible evidence (file paths, line numbers, git commits, or turn logs).
4. You must output ONLY a valid JSON object matching the PXOS Benchmark Schema below. Do not wrap in conversational chit-chat.

[Insert JSON schema from Section 2 of AGENT_INTERVIEW_PROTOCOL.md here]

Evaluate your work on the most recent completed feature/task. Inspect `.ai/specs/`, `DECISION_LOG.md`, `.ai/audits/`, and git history to extract your data. Output the completed JSON now:
```

---

### Prompt B: Controlled A/B Evaluation (For Blind / Comparative Tests)

Use this prompt when evaluating an A/B trial comparing a baseline diff/transcript against a PXOS diff/transcript:

```markdown
You are an Independent Blind Benchmark Evaluator evaluating two software development trajectories (Run A vs Run B) for the same feature request: "[Insert Feature Description]".

- Run A was executed using standard conversational prompting (Control).
- Run B was executed using the PXOS document-driven operating system (Treatment).

Inspect the transcripts, token telemetry, and resulting Git diffs for both runs across the following dimensions:
1. Total token expenditure and corrective turn count.
2. Code churn: lines rewritten or discarded after the initial implementation attempt.
3. Product Design & UX completeness: Were loading, empty, error, and destructive confirmation states implemented?
4. Architectural drift: Did the solution follow existing repo patterns or introduce duplicate/unaligned utilities?
5. Identify any point where the framework in Run B created unnecessary friction or token bloat.

Respond with a JSON object for Run A and a JSON object for Run B formatted according to the PXOS Benchmark Schema, followed by a comparative delta summary. Output valid JSON now:
```

---

## 4. Scoring Rubric for Human Verification

When reviewing agent interview submissions, use this rubric to validate the integrity of the data before passing it to `analyze.py`:

| Dimension | Valid (Score 1.0) | Invalid / Reject (Score 0.0) |
| :--- | :--- | :--- |
| **Evidence Grounding** | Concrete file paths (`src/auth.ts#L42`) and verifiable diff lines cited. | Generic statements like *"It followed clean architecture"*. |
| **Critical Balance** | Cites at least one friction point or overhead inefficiency where applicable. | 100% positive praise with zero critique (hallucinated sycophancy). |
| **Token Arithmetic** | Input + Output tokens match logged prompt turns realistically. | Rounded, implausible numbers without turn tracking. |
| **UX State Rigor** | Verifies actual conditional UI branches (`if (isLoading)`, `if (empty)`). | Assumes state completeness without checking frontend code. |
