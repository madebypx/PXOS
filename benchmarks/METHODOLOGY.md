# Empirical Benchmark Methodology for PXOS
<!-- pxos:benchmark:methodology:v1.0.0 -->

## Abstract

This document outlines the formal empirical methodology designed to scientifically evaluate the quantitative and qualitative performance impact of **PXOS (Product & eXperience Operating System)** in AI-assisted software engineering. 

The objective of this methodology is to eliminate speculation, marketing hyperbole, and LLM sycophancy, establishing an **incontestable, reproducible, and mathematically grounded evaluation framework** for assessing:
1. Context token economy and cost efficiency.
2. Architectural stability and regression reduction.
3. User experience (UX) and interaction state completeness.
4. Concurrency scaling and merge collision frequency in multi-agent workflows.

---

## 1. Research Questions (RQs)

The benchmark framework is structured around five core empirical questions:

- **RQ1 (Token Economy):** *To what extent does document-driven asynchronous artifact passing reduce total token consumption compared to unconstrained conversational memory across identical feature implementations?*
- **RQ2 (Cost & Model Routing):** *How does the 80/20 model specialization tier (routing high-throughput execution to lightweight models and strategic specs/reviews to reasoning models) impact total monetary cost per delivered feature?*
- **RQ3 (Architectural Stability & Rework):** *Does the mandatory Discover → Plan operational gate significantly reduce code churn, duplicate utilities, and regression of pre-identified audit findings?*
- **RQ4 (UX & Interaction Quality):** *Does enforcing explicit state modeling (empty, loading, error, destructive guards) and Nielsen Norman heuristics during specification and review measurably increase front-end completeness?*
- **RQ5 (Concurrency & Multi-Agent Isolation):** *How does physical Git Worktree isolation compare to shared-branch multi-agent execution regarding file collisions, merge conflicts, and time-to-PR?*

---

## 2. Experimental Design

### 2.1 Subject Groups

Every empirical trial evaluates a paired comparison between two groups across identical initial repository states:

| Group | Identifier | Configuration Description |
| :--- | :--- | :--- |
| **Control Group** | **$C$ (Vanilla / Unconstrained)** | Standard AI assistant interaction without PXOS. The agent operates via free-form conversational prompting, continuous chat history, unguided architectural planning, and direct file editing on a single shared branch. |
| **Treatment Group** | **$T$ (PXOS Operating System)** | AI assistant operating strictly under the PXOS contract (`AI_BASE.md`, `PROJECT_CONTEXT.md`, `.ai/specs/`, `DECISION_LOG.md`, `.ai/audits/`, and Git Worktrees). Follows the 6-phase lifecycle: Discover → Plan → Execute → Validate → Review → Compact. |

### 2.2 Task Stratification & Complexity Tiers

Tasks must be categorized across three complexity tiers to identify the **Overhead Inflection Point** (the task size where framework overhead becomes net-positive):

1. **Tier 1 — Micro Tasks (Small):**
   - *Scope:* Isolated bug fixes, CSS tweaks, single-file utility additions.
   - *LOC Changed:* $< 50$ lines.
   - *Expected Finding:* Treatment group may exhibit token overhead due to specification scaffolding.
2. **Tier 2 — Subsystem Features (Medium):**
   - *Scope:* New API endpoints, database migration + repository layer, interactive UI component with async state.
   - *LOC Changed:* $50 - 300$ lines.
   - *Expected Finding:* Treatment group breaks even on token usage while achieving superior architectural alignment.
3. **Tier 3 — Complex Systems & Refactors (Large / Multi-Session):**
   - *Scope:* Authentication subsystem, billing integration, state management refactor, multi-agent parallel workflows.
   - *LOC Changed:* $> 300$ lines across multiple modules.
   - *Expected Finding:* Treatment group exhibits drastic token reduction, zero session amnesia, and zero merge collisions.

---

## 3. Quantitative Metrics & Mathematical Formulations

### 3.1 Token Consumption & Efficiency Delta ($\Delta T$)

Let $T_{in}$ represent prompt input tokens, $T_{out}$ represent generated completion tokens, and $T_{total} = T_{in} + T_{out}$ across all turns $k \in [1, K]$ in a task session.

$$\Delta T = \left( \frac{T_{total}(C) - T_{total}(T)}{T_{total}(C)} \right) \times 100\%$$

- A positive $\Delta T$ indicates percentage token savings achieved by PXOS.
- A negative $\Delta T$ indicates framework overhead.

### 3.2 Monetary Cost Function ($Cost$)

Monetary cost is computed using standardized provider pricing tiers per million tokens:

$$Cost = \sum_{m \in M} \left( \frac{T_{in}^{(m)} \times P_{in}^{(m)}}{10^6} + \frac{T_{out}^{(m)} \times P_{out}^{(m)}}{10^6} \right)$$

Where:
- $m$ denotes the model class (e.g., High-Reasoning / Pro vs High-Throughput / Flash).
- $P_{in}^{(m)}, P_{out}^{(m)}$ are the published price per $10^6$ tokens for model $m$.
- Under PXOS, $T$ utilizes $m_{reasoning}$ for $\approx 10\%-15\%$ of tokens (`/spec`, `/review`), and $m_{throughput}$ for $\approx 85\%-90\%$ of tokens (`execute`, `tests`). Group $C$ typically runs a single monolithic model for all turns.

### 3.3 Code Churn & Rework Ratio ($R_{rework}$)

Rework measures the efficiency of the implementation phase by calculating lines modified or deleted in subsequent corrective turns after the initial implementation attempt:

$$R_{rework} = \left( \frac{L_{modified} + L_{deleted}}{L_{added\_initial}} \right) \times 100\%$$

Where:
- $L_{added\_initial}$ is the total lines of code introduced in the agent's first implementation diff.
- $L_{modified} + L_{deleted}$ are the corrective line edits forced by compilation errors, broken tests, or missed requirements before PR readiness.

### 3.4 Decision Retention & Drift Index ($D_{drift}$)

To measure architectural amnesia across multi-session tasks, we define the Drift Index:

$$D_{drift} = \frac{N_{violated\_invariants} + N_{duplicate\_utilities}}{N_{historical\_decisions}}$$

Where:
- $N_{historical\_decisions}$ is the count of established ADRs in `DECISION_LOG.md` or prior session agreements.
- $N_{violated\_invariants}$ is the count of regressions violating established architectural boundaries.
- $N_{duplicate\_utilities}$ is the count of redundant helper functions created because the agent forgot existing utils.

### 3.5 UX State Completeness Index ($S_{ux}$)

Front-end components must be evaluated against the **Universal 5-State Matrix**:

$$S_{ux} = \frac{1}{5} \sum_{i=1}^{5} w_i \cdot s_i, \quad s_i \in \{0, 1\}$$

Where states $s_1 \dots s_5$ represent:
1. $s_1$ (**Initial / Idle State**): Base rendering.
2. $s_2$ (**Loading / Pending State**): Skeletons, spinners, or optimistic feedback.
3. $s_3$ (**Empty State**): Clear visual and textual cue when zero data is available.
4. $s_4$ (**Error / Recovery State**): Actionable error messages and retry mechanisms.
5. $s_5$ (**Destructive Action Guard**): Confirmation dialogs or undo mechanisms for high-impact actions.

Weights $w_i = 1.0$ unless a state is demonstrably non-applicable (e.g., non-destructive flows omit $s_5$, renormalizing to $\frac{1}{4}$).

### 3.6 Framework Overhead-to-Value Ratio ($OVR$)

The metric determining whether PXOS overhead is justified:

$$OVR = \frac{T_{overhead}}{T_{saved\_rework}}$$

Where:
- $T_{overhead}$ is the token cost of generating and maintaining `.ai/` documentation (`SPEC`, `PLAN`, `COMPACT`).
- $T_{saved\_rework}$ is the estimated token cost avoided by preventing correction turns and architectural re-writes.
- An $OVR < 1.0$ indicates that PXOS was mathematically net-beneficial.

---

## 4. Qualitative Heuristics & Audit Taxonomy

### 4.1 Nielsen Norman Usability Heuristics Compliance
Every UI diff is evaluated against Jakob Nielsen's 10 Usability Heuristics, specifically:
- **H1: Visibility of system status:** Timely, appropriate feedback.
- **H5: Error prevention:** Careful design preventing slip-ups and destructive errors.
- **H6: Recognition rather than recall:** Reduced cognitive load; options and actions visible.
- **H8: Aesthetic and minimalist design:** Zero ad-hoc styles, strict adherence to design system tokens.

### 4.2 Architectural Violation Taxonomy
Audit findings are classified according to severity:
- **P0 (Blocker):** Security flaw, memory leak, unhandled race condition.
- **P1 (Critical):** Broken invariant, severe regression, architectural layering violation.
- **P2 (Major):** Technical debt, code duplication, missing unit test coverage.
- **P3 (Minor):** Non-standard naming, stylistic inconsistency.

---

## 5. Threats to Validity & Mitigation

| Threat Category | Potential Risk | Scientific Mitigation Strategy |
| :--- | :--- | :--- |
| **LLM Sycophancy** | Agents praise PXOS because they are asked about it. | **Blind Evaluation:** Reviewer agents are presented with anonymized diffs without knowing which framework was used.<br>**Adversarial Elicitation:** The interview protocol explicitly instructs the agent to audit inefficiencies, friction, and failures. |
| **Non-Determinism** | LLM temperature causing variance between runs. | Set temperature to $0.0$ (or minimum allowed) for evaluation tasks. Run all trials $N \ge 3$ times and report mean ($\mu$) and standard deviation ($\sigma$). |
| **Task Selection Bias** | Choosing only tasks that favor structured planning. | Include micro-tasks (where PXOS is expected to have overhead) alongside complex refactors. |
| **Telemetry Inaccuracy** | Hallucinated token counts. | Ingest raw IDE telemetry logs or direct API billing responses rather than relying on self-reported agent estimates whenever possible. |

---

## 6. Reproducibility Protocol

To reproduce any benchmark:
1. Clone the target repository at the designated baseline commit hash.
2. Ensure identical tooling configurations (Node/Python runtime, linters, test harnesses).
3. Execute the controlled prompts specified in `AGENT_INTERVIEW_PROTOCOL.md`.
4. Store all raw output JSONs in `benchmarks/data/`.
5. Run `python benchmarks/analyze.py --input benchmarks/data/` to generate the consolidated report.
