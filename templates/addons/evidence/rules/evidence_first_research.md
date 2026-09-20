# PXOS Evidence-First Research & Epistemic Governance Rules
<!-- pxos:evidence:rule v1.0.0 -->

When conducting research, evaluating architectural trade-offs, designing empirical studies, or synthesizing findings in this workspace:

1. **Epistemic Layer Separation:** Strictly classify information into 5 layers:
   - Layer 1: Raw Data (logs, traces, verbatim quotes)
   - Layer 2: Finding / Inference (empirical facts directly backed by Layer 1)
   - Layer 3: Design Hypothesis (testable conjectures or proposed invariants)
   - Layer 4: Architectural Decision (ADRs in `.ai/DECISION_LOG.md`)
   - Layer 5: Validated Conclusion (peer-reviewed synthesis)
   Never jump layers or present an unverified hypothesis as a validated conclusion.

2. **Absolute Anti-Hallucination:**
   - NEVER invent or approximate DOIs, URLs, publication years, quotes, papers, benchmark numbers, or sample sizes.
   - If a source is unverified, mark it as `UNVERIFIED SOURCE — REQUIRES EMPIRICAL CITATION`.

3. **Mandatory Insufficient Evidence Gate:**
   - If data is missing, anecdotal, or ungrounded, you MUST state:
     `INSUFFICIENT EVIDENCE — DO NOT CONCLUDE`.

4. **Traceability:**
   - Record all claims in `.ai/research/evidence-matrix.csv` with source IDs mapped to `.ai/research/source-register.csv`.
   - Log counterexamples and boundary conditions in `.ai/research/negative-cases.md`.
   - Log refuted claims in `.ai/research/rejected-claims.md`.

5. **Adversarial Peer Review:**
   - Use `/peer-review` to stress-test claims before proposing architectural decisions or final conclusions.
   - Respect the 5 canonical verdicts: `REMOVE`, `QUALIFY`, `VERIFY`, `REANALYZE`, `RETAIN`.
