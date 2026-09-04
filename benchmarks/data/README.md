# PXOS Benchmark Data Directory

This directory stores empirical evaluation datasets collected from AI agents and automated benchmark runs.

## Data Files in this Directory

- `task_auth_oauth_pxos.json` — Tier 2 feature task (OAuth Authentication) evaluated under PXOS.
- `task_billing_webhook_pxos.json` — Tier 3 complex subsystem task (Stripe Webhook + Concurrency) evaluated under PXOS with audit resolution (`SEC-01`).
- `task_css_button_pxos.json` — Tier 1 micro task (Button UI Polish) demonstrating framework overhead on small tasks.

## How to Add New Agent Data

1. Run the standardized prompt from [`AGENT_INTERVIEW_PROTOCOL.md`](../AGENT_INTERVIEW_PROTOCOL.md) with your AI agent.
2. Save the agent's JSON response as a `.json` file in this directory:
   ```bash
   benchmarks/data/task_<your_task_name>.json
   ```
3. Run the analysis engine to recompute metrics across the entire dataset:
   ```bash
   python benchmarks/analyze.py --input benchmarks/data/ --report benchmarks/REPORT.md --json benchmarks/summary.json
   ```
