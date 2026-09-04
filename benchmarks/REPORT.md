# PXOS Empirical Benchmark & Audit Report
<!-- pxos:empirical:report -->

**Sample Size:** 4 evaluated tasks across AI agents.
**Overhead Justification Rate:** 75.0% of tasks reported net positive utility.

## 1. Quantitative Telemetry & Token Efficiency

| Metric | Mean | Median | Std Dev | Min | Max |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Total Tokens** | 133,725.0 | 57,100.0 | 178,741.2 | 20,300.0 | 400,400.0 |
| **Input Tokens** | 114,675.0 | 49,250.0 | 152,354.92 | 18,200.0 | 342,000.0 |
| **Output Tokens** | 19,050.0 | 7,850.0 | 26,386.93 | 2,100.0 | 58,400.0 |
| **PXOS Overhead Tokens** | 8,900.0 | 5,000.0 | 9,633.97 | 2,400.0 | 23,200.0 |

- **Total Framework Overhead:** 6.66% of total token consumption was dedicated to `.ai/` operational artifacts (`SPEC`, `PLAN`, `COMPACT`).

## 2. Code Churn & Rework Reduction

- **Mean Rework Ratio:** 3.37% (lines modified or discarded after initial diff).
- **Mean Corrective Turns:** 1.0 turns before PR readiness.
- **Session Amnesia Incidents:** 0.0% of sessions.
- **Duplicate Utilities Prevented/Introduced:** 0 duplicate helpers registered.
- **Audit Findings Formally Resolved:** 8 items (e.g. security/memory fixes).

## 3. Product Design & UX State Coverage

- **UI Tasks Evaluated:** 3
- **Mean UX State Completeness:** 93.0% (Evaluating Initial, Loading, Empty, Error, and Destructive confirmation branches).

## 4. Complexity Tier Breakdown

| Complexity Tier | Tasks ($N$) | Mean Tokens | Mean Overhead | Overhead % | Mean Rework % |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **tier_2_medium** | 1 | 49,300.0 | 4,200.0 | 8.5% | 6.4% |
| **tier_3_complex** | 2 | 232,650.0 | 14,500.0 | 6.2% | 3.5% |
| **tier_1_micro** | 1 | 20,300.0 | 2,400.0 | 11.8% | 0.0% |

> [!NOTE]
> **Overhead Inflection Insight:** In Tier 1 (micro tasks), specification scaffolding represents a higher token proportion. In Tier 2 and Tier 3 tasks, the overhead drops significantly while rework savings scale exponentially.

## 5. Cost Analysis (USD)

| Model Pricing Profile | Total Expenditure (USD) | Mean Cost per Task |
| :--- | :--- | :--- |
| **claude-3-5-sonnet** | $2.5191 | $0.6298 |
| **gemini-2-flash** | $0.0764 | $0.0191 |
| **gemini-1-5-pro** | $0.9544 | $0.2386 |
| **gpt-4o** | $1.9087 | $0.4772 |
| **default-blended** | $1.1452 | $0.2863 |

## 6. Critical Qualitative Synthesis

### Identified Friction Points & Overhead Critiques:
- Filling the Strategic & Audit Alignment block in SPEC-auth.md took an extra prompt turn when no audits were directly touching auth.
- Had to run pxos-task.sh to set up the worktree tree, which required verifying bash permissions on the developer machine.
- Running the full /spec and /plan sequence for a 20-line CSS change produced 2,400 tokens of documentation overhead (11.8% of total tokens), which felt excessive for a simple aesthetic adjustment.
- The Low-Risk autonomy rule in AI_BASE.md should have allowed moving directly to execution without full spec scaffolding.
- Maintaining separate SPEC files for all 7 milestones (.ai/specs/SPEC-*.md) created 23,200 tokens of documentation overhead, requiring explicit workflow state tracking turns.
- Node.js native ESM execution without a runtime loader failed on test scripts until bundled via esbuild in package.json, which was not caught during initial script authoring.

### Concrete Empirical Benefits Cited:
- Mandatory error state in spec forced the implementation of OAuth callback timeout handling in auth/callback.ts#L48-L62, avoiding an uncaught promise rejection in production.
- Append-only DECISION_LOG.md preserved the cookie encryption strategy for future sessions.
- Worktree isolation allowed parallel work with feat/auth without touching shared package.json or src/index.ts until final merge.
- The Plan phase explicitly checked audit SEC-01 (raw body parsing requirement for Stripe webhooks), preventing a signature verification failure that typically requires multiple debugging turns.
- Consulting docs/DESIGN.md ensured the button used the canonical --radius-md variable instead of hardcoding 6px.
- Strict Zero-Spoiler invariant specified in .ai/CURRENT_SPEC.md and enforced in src/shared/utils/sanitizer.ts completely prevented confidential narrative leaks to the Player View window.
- The append-only DECISION_LOG.md entry for 2D Sweep-Line Raycasting prevented subsequent turns from attempting battery-draining WebGL fragment shaders.
- Pre-specifying the 4-sub-bus Web Audio routing graph in Milestone 2 allowed Milestone 5 (3D Dice) to seamlessly hook collision SFX directly into AudioEngine without touching existing channel faders.