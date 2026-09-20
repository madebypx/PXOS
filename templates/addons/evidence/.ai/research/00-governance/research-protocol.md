# Evidence-First Research Protocol (DSR & Empirical Governance)
<!-- pxos:evidence:protocol v1.0.0 -->

This protocol establishes methodological rigor, reproducibility, and epistemic discipline for research, Design Science Research (DSR), empirical case studies, and architectural evaluations within PXOS.

---

## 1. Core Principles: FAIR Research

All research artifacts produced or evaluated under this protocol must satisfy FAIR principles:

1. **Findable:** Every empirical claim must have a unique identifier (`EVD-xxx`), registered in `.ai/research/evidence-matrix.csv` and indexed in `.ai/research/INDEX.md`.
2. **Accessible:** Raw data, interview transcripts, and benchmark dumps must reside in designated, auditable paths (`.ai/research/data/` or `.internal/` for sensitive assets).
3. **Interoperable:** Data models, CSV schemas, and qualitative coding follow standard schemas without proprietary or undocumented formats.
4. **Reusable:** Methodology, search queries, extraction criteria, and environmental parameters must be explicitly specified to allow independent replication.

---

## 2. The 5 Epistemic Layers

To eliminate cognitive drift, confirmation bias, and model hallucinations, all information must be strictly categorized into one of 5 discrete layers. **Never collapse or jump layers without explicit audit trails.**

```
[ Layer 1: Raw Data ]
       │
       ▼
[ Layer 2: Finding / Inference ]
       │
       ▼
[ Layer 3: Design Hypothesis ]
       │
       ▼
[ Layer 4: Architectural Decision (ADR) ]
       │
       ▼
[ Layer 5: Validated Conclusion ]
```

### Layer 1: Raw Data (`Raw Data`)
- **Definition:** Direct, uninterpreted empirical materials: execution logs, benchmark CSVs, telemetry dumps, verbatim interview transcripts, git diff outputs, API responses.
- **Rules:** Immutable. Preserved with timestamps, source URLs, commit SHAs, or exact file paths.

### Layer 2: Finding / Inference (`Finding`)
- **Definition:** Empirical observations and statistical summaries derived strictly from Layer 1.
- **Rules:** Must cite specific Layer 1 data points (line numbers, record IDs, table rows). No extrapolation beyond the immediate data.

### Layer 3: Design Hypothesis (`Hypothesis`)
- **Definition:** Proposed design theories, architectural conjectures, invariant candidates, or causal assertions.
- **Rules:** Must be formulated in testable terms (*"If X is introduced under condition Y, metric Z will improve by W% without degrading M"*).

### Layer 4: Architectural Decision (`ADR`)
- **Definition:** Formal, durable choices made based on tested hypotheses.
- **Rules:** Must be logged in `.ai/DECISION_LOG.md` adhering to `INV-005`. Must link back to the supporting findings and hypothesis.

### Layer 5: Validated Conclusion (`Conclusion`)
- **Definition:** Synthesized high-level claims, scientific paper contributions, or executive architectural guidance.
- **Rules:** Permitted ONLY when Layers 1–4 are fully audited with zero unresolved critical methodological vulnerabilities.

---

## 3. The Mandatory Stop Gate

> [!CAUTION]
> **INSUFFICIENT EVIDENCE — DO NOT CONCLUDE**
> If an empirical assertion lacks a direct primary source citation, if the sample size is anecdotal, if negative cases are unexamined, or if the source location cannot be verified:
> **The agent MUST emit `INSUFFICIENT EVIDENCE — DO NOT CONCLUDE` and halt progression to Layer 4/5.**
> Speculative assertions must be explicitly downgraded to Layer 3 (Hypothesis) or logged in `.ai/research/negative-cases.md`.

---

## 4. Double-Stage Approval & Audit Gates

No claim or design conclusion may be codified without progressing through four checkpoints:

```
[ Primary Research Agent ]
          │ (Draft Claim + Citation)
          ▼
[ Adversarial Methodological Reviewer (/peer-review) ]
          │ (Stress-test, Hunt Biases, Issue Verdict: REMOVE / QUALIFY / VERIFY / REANALYZE / RETAIN)
          ▼
[ Human Technical Lead / Researcher ]
          │ (Strategic validation & final approval)
          ▼
[ Evidence Matrix & Decision Log Consolidation ]
```

1. **Stage 1 — Primary Formulation:** The Primary Agent drafts claims, notes citations in `source-register.csv`, and records entries in `evidence-matrix.csv`.
2. **Stage 2 — Adversarial Stress-Test:** The Adversarial Reviewer invokes `/peer-review`, challenging logical leaps, selection bias, and threats to validity.
3. **Stage 3 — Human Gate:** The human engineer/researcher verifies high-impact claims and resolves disputed verdicts.
4. **Stage 4 — Ledger Commitment:** Approved claims are finalized in `evidence-matrix.csv`; refutations are permanently recorded in `rejected-claims.md` to prevent historical regression.
