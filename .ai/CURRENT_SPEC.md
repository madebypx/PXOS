# Current Spec
<!-- pxos:version 2.2.0 -->

This file defines the active task or feature. Replace it entirely when starting a new task. The AI reads this file at the start of every session to understand what is being built.

---

## Goal

Provide an autonomous, zero-dependency monitoring utility for the PXOS public telemetry ingestion daemon (`https://telemetry.madebypx.com/api/v1/stats` and `/api/v1/health`) to track health, round-trip latency, public submission volume, complexity tier distribution, and token economy aggregates.

---

## User value

- **Operational Reliability:** Immediate detection of downtime, 5xx errors, or latency spikes in the production telemetry server.
- **Empirical Visibility:** Maintainers and contributors can monitor incoming benchmark submissions in real time, inspecting sample growth and overhead justification rates without needing direct SSH/database access to the production host.
- **Automated Alerting / CI Integration:** A script that can be executed via cron, GitHub Actions, or local terminals (`--watch` or `--json`) to verify service health before submitting benchmark data.

---

## Strategic & Audit Alignment

- **Audit Findings Cross-Check:** Clean — No active audit blockers touching this scope.
- **Strategic / Research Reference:** `benchmarks/METHODOLOGY.md`, `benchmarks/REPORT.md`, `benchmarks/summary.json`. Aligns with the Empirical Telemetry Subsystem introduced in PXOS v2.2.0.

---

## Scope

**In:**
- Standalone zero-dependency Python script: `scripts/pxos-telemetry-monitor.py`.
- Health check polling (`GET /api/v1/health`) with latency measurement (ms).
- Aggregated stats polling (`GET /api/v1/stats`) displaying:
  - Total community submissions
  - Mean total tokens and framework overhead tokens
  - Mean rework ratio % and UX state completeness %
  - Overhead justification rate %
  - Submissions grouped by complexity tier (`tier_1_micro`, `tier_2_medium`, `tier_3_complex`)
- Execution modes:
  - Snapshot mode (default / `--once`): inspects and prints clean formatted dashboard once.
  - Watch mode (`--watch` / `-w` with `--interval`): continuously polls at configured interval (default 30s) and displays deltas.
  - Machine mode (`--json`): outputs clean JSON suitable for ingestion by external monitoring or pipelines.
  - Alert thresholds (`--max-latency-ms`): exits with code 1 if latency exceeds threshold or service is unhealthy.
- Documentation update in `WORKFLOWS.md` or `benchmarks/`.

**Out:**
- Modifying backend server logic in `benchmarks/server.py` unless an API bug is discovered.
- Introducing heavyweight external telemetry or monitoring dependencies (Datadog, Prometheus client, etc.).
- Direct SQLite database access from client (monitoring is strictly HTTP/API-driven).

---

## Constraints

- Pure Python 3 standard library (`urllib.request`, `json`, `argparse`, `time`, `sys`).
- Zero external package dependencies (`pip`).
- Cross-platform support (Windows PowerShell, Linux bash, macOS zsh).
- Timeout protection (5s timeout per HTTP request to avoid hanging).

---

## Existing patterns

- `scripts/pxos-benchmark.py`: uses `urllib.request.Request`, structured ANSI headers, `--url` argument with default endpoint fallback.
- `benchmarks/server.py`: provides `/api/v1/health` returning `{"status": "healthy", ...}` and `/api/v1/stats` returning aggregated numbers and tier breakdowns.

---

## Proposed change

1. Create `scripts/pxos-telemetry-monitor.py` following the architectural patterns of `scripts/pxos-benchmark.py`.
2. Implement health check probing, response time calculation, and stats extraction.
3. Provide terminal styling (clean table / dashboard view) with status badges (`[OK]`, `[WARN]`, `[FAIL]`).
4. Support delta tracking in continuous `--watch` mode so maintainers can see new submissions increment in real time.
5. Add documentation entry in `WORKFLOWS.md` under Telemetry & Benchmarks section.

---

## User flow / Technical flow

1. Maintainer or agent runs:
   ```bash
   py scripts/pxos-telemetry-monitor.py
   ```
2. The monitor probes `https://telemetry.madebypx.com/api/v1/health`, records ping latency (e.g. `48ms`), and verifies `"status": "healthy"`.
3. The monitor probes `https://telemetry.madebypx.com/api/v1/stats`, parses JSON, and displays an ANSI summary table:
   - Server Status: Healthy (48ms)
   - Total Submissions: 4
   - Tier Breakdown: Tier 2 (2), Tier 3 (2)
   - Token & Rework Summary: Avg Tokens 135.9k | Overhead 6.1% | Rework 1.4%
4. If `--watch` is specified:
   - Loops every $N$ seconds, clearing terminal or printing timestamped log lines, highlighting any newly submitted benchmarks.
5. If server returns 5xx or fails connection:
   - Prints `[CRITICAL] Telemetry daemon unreachable at https://telemetry.madebypx.com: <reason>` and exits with status 1.

---

## Edge cases

- **Server Down / Unreachable:** Handle `urllib.error.URLError` and connection refused cleanly with `[OFFLINE]` diagnostic and exit code 1.
- **HTTP Error Codes (e.g. 500, 502 Bad Gateway, 404):** Catch `urllib.error.HTTPError`, print status and body if available.
- **Slow Connection / Gateway Timeout:** Request timeout set to 5 seconds; report timeout error instead of blocking indefinitely.
- **Zero Submissions Recorded:** Server returns `{"total_submissions": 0, "message": "No submissions recorded yet."}` — monitor handles empty summary gracefully without `KeyError`.
- **Unexpected Payload Structure:** Safe dictionary `.get()` navigation with type coercion.

---

## Acceptance criteria

- [x] `scripts/pxos-telemetry-monitor.py` exists, is executable, and runs on pure Python 3 standard library.
- [x] Single snapshot command (`py scripts/pxos-telemetry-monitor.py`) checks both `/api/v1/health` and `/api/v1/stats` and renders a clean dashboard.
- [x] Continuous watch mode (`--watch`, `--interval`) monitors stability and reports live updates/deltas.
- [x] Machine-readable JSON output (`--json`) is supported.
- [x] Failure states (offline, latency threshold exceeded, HTTP error) yield informative error messages and exit code 1.
- [x] Tested live against `https://telemetry.madebypx.com`.

---

## Validation plan

1. **Live Snapshot Verification:** Run `py scripts/pxos-telemetry-monitor.py` against `https://telemetry.madebypx.com` and verify formatted dashboard output. (Passed)
2. **JSON Output Verification:** Run `py scripts/pxos-telemetry-monitor.py --json` and pipe into JSON validator. (Passed)
3. **Failure Handling Verification:** Run `py scripts/pxos-telemetry-monitor.py --url https://invalid.domain.madebypx.com` and verify clean handling with exit code 1. (Passed)
4. **Latency Threshold Verification:** Run `py scripts/pxos-telemetry-monitor.py --max-latency-ms 1` and verify alert trigger. (Passed)

---

## Risks & Cross-Task Dependencies

- **Rate Limiting:** If running `--watch` with very short intervals (e.g. < 5s), reverse proxy could throttle requests. Set default interval to 15s and minimum interval guard to 2s.

---

## Workflow state
<!-- Updated by the agent during the session -->

- **Current phase:** Done
- **Pending decision:** None
- **Execution blocked until:** None
