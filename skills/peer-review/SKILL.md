---
name: peer-review
description: "PXOS /peer-review workflow: Methodological adversarial review to stress-test claims, find logical leaps, and audit sources against evidence-matrix.csv."
---

# /peer-review — Adversarial Methodological Review

Operate as an **Adversarial Methodological Reviewer** to rigorously audit research claims, design assertions, and empirical findings against evidence registers and epistemological standards.

---

## Review Scope & Grounding

1. **Locate Evidence Artifacts:**
   - Read `.ai/research/00-governance/research-protocol.md` (if present) for governing standards.
   - Inspect active research files in `.ai/research/` or the current branch diff.
   - Inspect `.ai/research/evidence-matrix.csv` and `.ai/research/source-register.csv`.
   - Inspect `.ai/research/negative-cases.md` and `.ai/research/rejected-claims.md`.

2. **Epistemic Layer Audit:**
   - Verify that information is correctly layered (`Raw Data` ➔ `Finding` ➔ `Hypothesis` ➔ `ADR` ➔ `Conclusion`).
   - Flag any instance where an unverified hypothesis (Layer 3) is treated as a proven conclusion (Layer 5).
   - Ensure the stop-gate rule was triggered where evidence was insufficient: `INSUFFICIENT EVIDENCE — DO NOT CONCLUDE`.

---

## Adversarial Heuristics Checklist

Evaluate each target claim against the core cognitive failure modes:

1. **Logical Leaps:** Does the conclusion logically follow from the premise, or is there an unstated assumption?
2. **Confirmation & Sycophancy Bias:** Were disconfirming instances or competing explanations actively investigated?
3. **Selection / Survivorship Bias:** Were failing runs, discarded test samples, or non-responsive subjects omitted?
4. **Construct Validity:** Does the chosen metric truly capture the real-world property claimed?
5. **Traceability & Verification:** Does the cited source ID and location actually contain the data excerpt supporting the claim?

---

## Assign the 5 Canonical Verdicts

For every evaluated claim, assign exactly one verdict:

- `REMOVE` — Factually inaccurate, ungrounded, or based on fabricated sources. Discard immediately and record in `rejected-claims.md`.
- `QUALIFY` — Partially true, but overgeneralized. Restrict scope and state boundary conditions.
- `VERIFY` — Source cited exists, but line numbers, quotations, or metrics must be independently verified.
- `REANALYZE` — Empirical data is valid, but inferences contain fallacies, confounding factors, or wrong statistical models.
- `RETAIN` — Robust, methodologically sound, traceable, and survives adversarial stress.

---

## Report Structure

Format the audit output clearly:

```markdown
# Peer Review Audit Report: [Target Scope / Document]

## Claim-by-Claim Stress Analysis

| Claim ID / Excerpt | Epistemic Layer | Vulnerability / Bias | Verdict | Action Required |
|---|---|---|---|---|
| "[Quote claim]" | Layer 3 | Selection bias in sample | QUALIFY | Restrict claim to evaluated models |

## Negative Cases & Boundary Conditions
- [List any counterevidence that must be logged to negative-cases.md]

## Recommended Next Steps
- [ ] Update evidence-matrix.csv with verified claims
- [ ] Log refuted claims in rejected-claims.md
- [ ] Refine spec or ADR before code implementation
```
