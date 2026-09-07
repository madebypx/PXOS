# PXOS UI Starter Templates — Universal 5-State Architecture
<!-- pxos:template-version 1.0.0 -->

Reference boilerplates and patterns implementing the **PXOS Universal 5-State UI Architecture** (`initial_idle`, `loading_pending`, `empty_data`, `error_recovery`, `destructive_action_guard`).

---

## Included Templates

1. **[`vanilla_5_states.html`](./vanilla_5_states.html):**
   - Zero-dependency, pure HTML/CSS/JavaScript showcase.
   - Interactive state toolbar allowing instant visual inspection of all 5 states.
   - Accessible ARIA attributes (`aria-busy`, `role="alert"`, `role="dialog"`, `aria-modal="true"`).
   - Glassmorphism dark mode design system matching PXOS aesthetics.

2. **[`react_5_states.jsx`](./react_5_states.jsx):**
   - Production-ready React component following a finite state machine pattern.
   - Type-annotated state union: `'initial_idle' | 'loading_pending' | 'empty_data' | 'error_recovery' | 'destructive_action_guard'`.
   - Debounced action triggers and accessible modal focus trap.

---

## Verification Protocol

When building frontend components with PXOS:
1. Copy or adapt one of these templates.
2. Ensure every state is rendered and styled.
3. Run `/audit` or `pxos benchmark --verify-ui` to earn +10 adherence points for Tier A verification.
