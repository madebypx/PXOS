# PXOS Universal 5-State UI Verification & Visual Inspector
<!-- pxos:ui-version 1.0.0 -->

A standardized visual verification and resilience protocol for AI-assisted frontend development.

---

## 1. Philosophy & Purpose

A pervasive failure mode in AI-generated user interfaces is **Happy-Path Bias**: an agent styles and tests a screen exclusively with pre-populated, healthy mock data, declaring the frontend "100% complete." In reality:
- Slow network requests leave blank screens with no visual loading feedback.
- First-time users are greeted by awkward empty containers with broken borders.
- Failed API calls display cryptic raw JSON exceptions or silent freezes.
- Irreversible deletions trigger immediately on button click without confirmation guards.

The **PXOS Universal 5-State Matrix** eliminates UI blind spots by establishing five mandatory interactive states that every user-facing component or page must implement and verify before completion.

---

## 2. The 5 Universal UI States

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      PXOS UNIVERSAL 5-STATE MATRIX                      │
├─────────────────────────────────────────────────────────────────────────┤
│ 1. initial_idle             │ Clean populated view with real/mock data  │
│ 2. loading_pending          │ Non-blocking skeletons & active spinners  │
│ 3. empty_data               │ Friendly zero-state card with clear CTA   │
│ 4. error_recovery           │ Human-readable banner with retry pathway  │
│ 5. destructive_action_guard │ Confirmation modal or undo toast guard    │
└─────────────────────────────────────────────────────────────────────────┘
```

### State 1: `initial_idle` (Standard Populated View)
- **Definition:** The component or view populated with valid, representative data.
- **Criteria:**
  - Proper layout alignment, typography, and contrast adhering to design tokens.
  - Interactive elements (links, buttons, inputs) in their default enabled state.
  - No visual clipping, text overflow, or unstyled system fonts.

### State 2: `loading_pending` (Async / Processing Indicator)
- **Definition:** The view during network requests, background calculations, or initial data fetching.
- **Criteria:**
  - **Content Loading:** Accessible skeleton screens matching the geometry of incoming content (preferred over generic full-page spinners).
  - **Action Loading:** Trigger buttons enter disabled state, displaying inline activity indicators to prevent duplicate submissions (double-click debouncing).
  - Layout stability: Content containers preserve their height to eliminate Cumulative Layout Shift (CLS).

### State 3: `empty_data` (Zero-State Graceful Handling)
- **Definition:** The view when an API returns an empty array (`items: []`), search yields zero results, or a new user has no records.
- **Criteria:**
  - Informative headline explaining the lack of data (e.g. *"No projects found"* instead of a blank canvas).
  - Instructive description guiding the user on what goes here.
  - **Call to Action (CTA):** A prominent primary button or link enabling the user to create the first item or reset search filters.

### State 4: `error_recovery` (Resilient Failure Handling)
- **Definition:** The view when an API call fails (4xx, 5xx, offline, or schema validation error).
- **Criteria:**
  - Human-friendly explanation of what went wrong (never expose unformatted stack traces or raw JSON).
  - Non-destructive presentation: local errors isolate within the affected widget without crashing the entire page.
  - **Recovery Pathway:** An explicit **Retry** button that re-triggers the failed operation, or an alternative contact/fallback path.

### State 5: `destructive_action_guard` (Safety Confirmation)
- **Definition:** The protective layer guarding against irreversible user operations (e.g. deleting a database, removing a member, discarding unsaved work).
- **Criteria:**
  - **Pre-execution Modal / Dialog:** A focused dialog clearly summarizing the consequences of the action.
  - **Visual Distinction:** Destructive triggers styled with distinct danger tokens (e.g. red/crimson accents).
  - **Alternative (Undo Toast):** For lower-risk actions, immediate execution paired with a persistent 5-to-10-second "Undo" snackbar.

---

## 3. Standard Audit Matrix Table

When running `/audit` on a frontend component or page, the auditor must evaluate and document all 5 states using this standardized Markdown table:

```markdown
### UI 5-State Verification Matrix

| State | Status | Evidence / Implementation Details | Verified |
|---|---|---|:---:|
| `initial_idle` | PASS | Populated list with 5 mock items, design tokens adhered | [x] |
| `loading_pending` | PASS | Shimmer skeleton cards match layout; form submit debounced | [x] |
| `empty_data` | PASS | "No items yet" card rendered with primary "Create Item" button | [x] |
| `error_recovery` | PASS | Red alert banner on 500 status with working "Retry" trigger | [x] |
| `destructive_action_guard` | PASS | Modal confirmation with explicit "Delete" button required | [x] |
```

> [!NOTE]
> The automated parser in `pxos benchmark --verify-ui` scans audit reports for lines containing `[x]` or `PASS` alongside each state key (`initial_idle`, `loading_pending`, `empty_data`, `error_recovery`, `destructive_action_guard`).

---

## 4. Multi-Modal Visual Snapshot Protocol

For autonomous subagents equipped with browser automation tools (e.g., Antigravity `browser_subagent` or headless test runners):

1. **Snapshot Storage:** Store visual screenshots inside:
   ```
   .ai/audits/screenshots/<task_id>/
   ├── state_initial_idle.png
   ├── state_loading_pending.png
   ├── state_empty_data.png
   ├── state_error_recovery.png
   └── state_destructive_action_guard.png
   ```
2. **Privacy Invariant (`INV-001`):** Never capture or persist screenshots showing real passwords, production auth tokens, or customer PII. Always use synthetic/mock fixtures for visual auditing.
3. **Audit Linking:** Reference captured snapshots directly in the audit report:
   ```markdown
   - **Visual Proof:** ![Initial Idle](screenshots/T-12/state_initial_idle.png)
   ```

---

## 5. Implementation Blueprints

### 5.1 Vanilla JavaScript Finite State Machine

```javascript
// Universal 5-State Container Controller
function renderState(container, state, data = null) {
  container.innerHTML = '';
  switch (state) {
    case 'loading_pending':
      container.innerHTML = `
        <div class="skeleton-card" aria-busy="true">
          <div class="skeleton-line title"></div>
          <div class="skeleton-line text"></div>
        </div>`;
      break;

    case 'empty_data':
      container.innerHTML = `
        <div class="empty-state">
          <h3>No records found</h3>
          <p>Get started by creating your first record.</p>
          <button class="btn btn-primary" onclick="createRecord()">+ Create Item</button>
        </div>`;
      break;

    case 'error_recovery':
      container.innerHTML = `
        <div class="error-banner" role="alert">
          <p>Failed to load records. Check connection and retry.</p>
          <button class="btn btn-secondary" onclick="retryFetch()">Retry</button>
        </div>`;
      break;

    case 'destructive_action_guard':
      container.innerHTML = `
        <div class="dialog-overlay" role="dialog" aria-modal="true">
          <div class="dialog-box">
            <h3>Delete Record?</h3>
            <p>This action cannot be undone. Are you sure?</p>
            <div class="dialog-actions">
              <button class="btn btn-neutral" onclick="cancelDelete()">Cancel</button>
              <button class="btn btn-danger" onclick="confirmDelete()">Confirm Delete</button>
            </div>
          </div>
        </div>`;
      break;

    case 'initial_idle':
    default:
      container.innerHTML = `
        <div class="populated-list">
          ${data.map(item => `<div class="card">${item.title}</div>`).join('')}
        </div>`;
      break;
  }
}
```

### 5.2 React State Machine Pattern

```jsx
import React, { useState } from 'react';

export function Universal5StateWidget({ fetchItems, deleteItem }) {
  // 'initial_idle' | 'loading_pending' | 'empty_data' | 'error_recovery' | 'destructive_action_guard'
  const [uiState, setUiState] = useState('initial_idle');
  const [items, setItems] = useState([]);
  const [targetId, setTargetId] = useState(null);

  if (uiState === 'loading_pending') {
    return <div className="skeleton-loader" aria-busy="true" />;
  }

  if (uiState === 'error_recovery') {
    return (
      <div className="error-alert">
        <p>Something went wrong while fetching data.</p>
        <button onClick={() => fetchItems()}>Retry</button>
      </div>
    );
  }

  if (uiState === 'empty_data' || items.length === 0) {
    return (
      <div className="empty-state">
        <p>No records found.</p>
        <button onClick={() => handleCreate()}>+ Create First Item</button>
      </div>
    );
  }

  return (
    <div>
      {uiState === 'destructive_action_guard' && (
        <ConfirmDialog
          title="Delete Confirmation"
          message="Are you sure? This cannot be reversed."
          onConfirm={() => deleteItem(targetId)}
          onCancel={() => setUiState('initial_idle')}
        />
      )}
      <ul className="item-list">
        {items.map((item) => (
          <li key={item.id}>
            <span>{item.name}</span>
            <button
              className="btn-danger"
              onClick={() => {
                setTargetId(item.id);
                setUiState('destructive_action_guard');
              }}
            >
              Delete
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
```

---

## 6. Benchmark Scoring Integration

The PXOS empirical benchmark engine (`scripts/pxos-benchmark.py`) awards adherence points when UI components are audited:

- `ux_state_completeness_score = verified_states_count / 5.0` (0.0 to 1.0).
- When all 5 states are audited and passed:
  - `ui_components_touched` is marked `true`.
  - An additional **+10 adherence points** (`ui_5_states_verified`) is awarded towards repository qualification (capped at 100 points max).
  - Benchmark reports with 5/5 UI states qualify for Tier A rigor with highest UX confidence.
