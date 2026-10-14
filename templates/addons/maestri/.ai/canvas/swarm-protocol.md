# Swarm Protocol — Micro-Context & Boundary Confinement
<!-- pxos:canvas:swarm-protocol -->

> **Notice:** This note is a live projection of the swarm topology and execution boundaries. The local Git repository is the Single Source of Truth (SSOT). All agents in a spatial swarm must adhere to micro-context boundaries and capsule briefings.

---

## 1. Confinement Principles (Anti-Bloat & Anti-Exploration)

1. **Context Sharding:** Specialists never load the complete `.ai/` directory. Each agent inspects exclusively their designated domain shard.
2. **Boundary Lock:** Each specialist has write permissions confined to exactly **one target file or sub-tree**. Editing files outside your assigned boundary is an invariant violation.
3. **Anti-Exploration Rule:** Autonomous exploration (`ls -R`, tree-scanning, arbitrary file reading) is strictly forbidden. Agents must operate purely based on the Capsule Briefing received in `maestri ask`.
4. **Synchronous Dialectic:** Peer reviews occur in a single síncrono round via `maestri ask --batch`, avoiding endless circular chatter.

---

## 2. Role Boundaries & Context Allocation Matrix

| Agent Name | Specialty Role | Allowed Write Target (`Target`) | Dedicated Context Shards |
|---|---|---|---|
| **Atlas** | Catalog Data Engineer | `docs/case/01_catalog.md` / `src/catalog/` | `DATA_MODEL.md` |
| **Hermes** | Logistics & Solver Engineer | `docs/case/02_logistics.md` / `src/solver/` | `DOMAIN_RULES.md` (Routing/MKP) |
| **Shield** | Fintech & Tax Counsel | `docs/case/03_fintech.md` / `src/fintech/` | `DOMAIN_RULES.md` (Tax/Split) |
| **Canvas** | Mobile UX Lead | `docs/case/04_mobile_ux.md` / `src/app/` | `DESIGN.md` |
| **Chef** | Applied AI Engineer | `docs/case/05_ai_engine.md` / `src/ai/` | Fuzzy matching & prompt specs |
| **Lex** | Legal & Compliance Counsel | `docs/case/06_compliance.md` | CDC, LPI, BCB regulations |
| **Falcon** | Growth Strategist | `docs/case/07_growth.md` | Unit economics & CAC/LTV |
| **Aegis** | Sentinel Auditor | `.ai/audits/` | Invariants INV-001 to INV-004 |

---

## 3. Capsule Briefing Schema

Every task dispatched by the Maestro must follow this 4-tuple schema:

```text
Capsule:
- [Target]: <Exact path to single target file or directory>
- [Invariants]: <List of active invariant codes, e.g. INV-001, INV-002>
- [Context]: <3 to 5 distilled facts and constraints; no extraneous history>
- [Report-back]: maestri ask "<Architect Name>" "DONE: [Brief summary and test verification]"
```

---

## 4. Dialectic Review Pipeline (Escalão 2)

```
       [Specialist Artifacts Produced]
                      │
        ┌─────────────┴─────────────┐
        ▼                           ▼
[Darwin: Empirical Audit]   [Munger: Risk / Churn Attack]
        │                           │
        └─────────────┬─────────────┘
                      ▼
     [Veritas: Final Epistemic Verdict]
  (RETAIN | QUALIFY | REANALYZE | REMOVE)
                      │
                      ▼
        [.ai/DECISION_LOG.md & ADR]
```
