# Decision Log

This file records durable architectural and product decisions (ADRs).
Append only — never delete past entries. If a decision is superseded, mark it as such.
Entries are maintained automatically by AI agents during `/compact` and via `/decision`, or manually by developers.
Only decisions with lasting impact belong here: architectural choices, rejected alternatives, structural shifts, and product invariants.

Multi-Agent Note: Entries are strictly additive and chronological. If a Git merge conflict occurs at the bottom of this file, the resolution rule is always to concatenate both entries without discarding either.

---

## Template

```
## YYYY-MM-DD — [Decision title]

**Decision:**
[What was decided.]

**Context:**
[Why this decision was needed. What problem it solves.]

**Options considered:**
- Option A — [brief description and why it was not chosen]
- Option B — [brief description and why it was not chosen]
- Chosen: Option C — [why this was selected]

**Tradeoffs:**
[What we gain and what we accept as a cost.]

**Impact:**
[What parts of the system are affected.]

**Status:** Active
```

---

<!-- Add decisions below this line, most recent first -->
