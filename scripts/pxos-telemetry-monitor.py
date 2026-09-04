#!/usr/bin/env python3
"""
PXOS Telemetry Daemon & Public Submissions Monitor
==================================================
Monitors daemon operational health, ping latency, and public empirical benchmark
submissions from the PXOS research aggregation server.

Zero external dependencies (pure Python 3 standard library).

Usage:
    # Single snapshot dashboard:
    py scripts/pxos-telemetry-monitor.py

    # Continuous watch mode (polls every 15s):
    py scripts/pxos-telemetry-monitor.py --watch

    # Stream logs continuously without clearing screen:
    py scripts/pxos-telemetry-monitor.py --watch --interval 10 --stream

    # Machine-readable JSON output for CI / dashboards:
    py scripts/pxos-telemetry-monitor.py --json

    # Threshold alerts (fails with exit code 1 if latency > 300ms):
    py scripts/pxos-telemetry-monitor.py --max-latency-ms 300
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple

# Enable ANSI terminal sequences and UTF-8 encoding on Windows 10/11
if sys.platform == "win32":
    os.system("")
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

DEFAULT_BASE_URL = os.environ.get("PXOS_TELEMETRY_URL", "https://telemetry.madebypx.com")

# ANSI styling codes
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"
GREEN = "\033[32m"
CYAN = "\033[36m"
YELLOW = "\033[33m"
RED = "\033[31m"
MAGENTA = "\033[35m"
WHITE = "\033[37m"
BG_DARK = "\033[40m"


def clean_base_url(url: str) -> str:
    """Normalizes the base URL, stripping subpaths like /api/v1/stats or /api/v1/telemetry."""
    url = url.strip().rstrip("/")
    # If the user supplied the full endpoint URL, strip down to the domain origin
    url = re.sub(r"/api/v1/(stats|health|telemetry)$", "", url)
    url = re.sub(r"/api/v1$", "", url)
    return url


def fetch_json(url: str, timeout: float = 5.0) -> Tuple[bool, int, Optional[Dict[str, Any]], float, Optional[str]]:
    """
    Fetches JSON from the target URL and measures round-trip time (RTT).
    Returns: (success, status_code, data_dict, latency_ms, error_message)
    """
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "PXOS-Telemetry-Monitor/1.0"
        },
        method="GET"
    )

    start_time = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            body = resp.read().decode("utf-8")
            data = json.loads(body)
            return True, resp.status, data, elapsed_ms, None
    except urllib.error.HTTPError as e:
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        try:
            err_body = e.read().decode("utf-8")
            err_json = json.loads(err_body)
            msg = err_json.get("error", f"HTTP {e.code}: {e.reason}")
        except Exception:
            msg = f"HTTP {e.code}: {e.reason}"
        return False, e.code, None, elapsed_ms, msg
    except urllib.error.URLError as e:
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        return False, 0, None, elapsed_ms, f"Network error: {e.reason}"
    except Exception as e:
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        return False, 0, None, elapsed_ms, f"Unexpected error: {e}"


def probe_telemetry_service(base_url: str, timeout: float = 5.0) -> Dict[str, Any]:
    """Probes /api/v1/health and /api/v1/stats."""
    health_url = f"{base_url}/api/v1/health"
    stats_url = f"{base_url}/api/v1/stats"

    health_ok, health_status, health_data, health_rtt, health_err = fetch_json(health_url, timeout)
    stats_ok, stats_status, stats_data, stats_rtt, stats_err = fetch_json(stats_url, timeout)

    now_iso = datetime.now(timezone.utc).isoformat()

    return {
        "timestamp": now_iso,
        "base_url": base_url,
        "health": {
            "ok": health_ok,
            "status_code": health_status,
            "service_status": health_data.get("status", "unknown") if health_data else "down",
            "service_name": health_data.get("service", "unknown") if health_data else "unknown",
            "server_timestamp": health_data.get("timestamp", "") if health_data else "",
            "latency_ms": round(health_rtt, 1),
            "error": health_err
        },
        "stats": {
            "ok": stats_ok,
            "status_code": stats_status,
            "latency_ms": round(stats_rtt, 1),
            "data": stats_data or {},
            "error": stats_err
        }
    }


def format_dashboard(result: Dict[str, Any], prev_result: Optional[Dict[str, Any]] = None, no_color: bool = False) -> str:
    """Formats the probed state into a sleek, informative terminal dashboard."""
    c_bold = "" if no_color else BOLD
    c_dim = "" if no_color else DIM
    c_reset = "" if no_color else RESET
    c_green = "" if no_color else GREEN
    c_cyan = "" if no_color else CYAN
    c_yellow = "" if no_color else YELLOW
    c_red = "" if no_color else RED
    c_magenta = "" if no_color else MAGENTA

    lines = []
    w = 70
    border = "=" * w

    lines.append(f"{c_cyan}{border}{c_reset}")
    lines.append(f"{c_bold}{c_cyan}      PXOS TELEMETRY DAEMON & PUBLIC SUBMISSIONS MONITOR{c_reset}")
    lines.append(f"{c_cyan}{border}{c_reset}")

    # Health status section
    h = result["health"]
    s = result["stats"]

    if h["ok"] and h["service_status"] == "healthy":
        status_badge = f"{c_green}[HEALTHY]{c_reset}"
    elif h["ok"]:
        status_badge = f"{c_yellow}[DEGRADED: {h['service_status']}]{c_reset}"
    else:
        status_badge = f"{c_red}[DOWN / UNREACHABLE]{c_reset}"

    latency_ms = h["latency_ms"]
    if latency_ms < 250:
        lat_color = c_green
    elif latency_ms < 800:
        lat_color = c_yellow
    else:
        lat_color = c_red
    latency_badge = f"{lat_color}{latency_ms:.1f} ms{c_reset}"

    lines.append(f"  Target Daemon:     {c_bold}{result['base_url']}{c_reset}")
    lines.append(f"  Service Status:    {status_badge} (Health Ping: {latency_badge})")
    if h.get("server_timestamp"):
        lines.append(f"  Server Time:       {c_dim}{h['server_timestamp']}{c_reset}")
    if h.get("error"):
        lines.append(f"  {c_red}Health Error:      {h['error']}{c_reset}")

    lines.append(f"{c_dim}{'-' * w}{c_reset}")

    # Stats Section
    if not s["ok"]:
        lines.append(f"  {c_red}Stats Ingestion:   [ERROR] {s.get('error', 'Unknown error')}{c_reset}")
    else:
        stats_data = s["data"]
        total_sub = stats_data.get("total_submissions", 0)

        # Delta calculation if previous state exists
        delta_str = ""
        if prev_result and prev_result.get("stats", {}).get("ok"):
            prev_total = prev_result["stats"]["data"].get("total_submissions", 0)
            diff = total_sub - prev_total
            if diff > 0:
                delta_str = f" {c_green}(+{diff} new!){c_reset}"
            elif diff < 0:
                delta_str = f" {c_red}({diff}){c_reset}"

        lines.append(f"  {c_bold}Total Submissions:{c_reset}  {c_magenta}{c_bold}{total_sub}{c_reset}{delta_str}")

        if total_sub == 0:
            lines.append(f"  {c_dim}No benchmark submissions recorded yet on server.{c_reset}")
        else:
            summary = stats_data.get("summary", {})
            tier_map = stats_data.get("submissions_by_tier", {})

            use_unicode = True
            try:
                "█•".encode(sys.stdout.encoding or "utf-8")
            except Exception:
                use_unicode = False

            # Complexity Tier Distribution
            lines.append(f"\n  {c_bold}Complexity Tier Breakdown:{c_reset}")
            for tier in ["tier_1_micro", "tier_2_medium", "tier_3_complex"]:
                count = tier_map.get(tier, 0)
                pct = (count / total_sub * 100.0) if total_sub > 0 else 0.0
                tier_label = tier.replace("tier_", "Tier ").replace("_", " ").title()
                bar_len = int(round(pct / 5))  # max 20 chars
                if use_unicode:
                    bar = "█" * bar_len + "░" * (20 - bar_len)
                    bullet = "•"
                else:
                    bar = "#" * bar_len + "-" * (20 - bar_len)
                    bullet = "*"
                lines.append(f"    {bullet} {tier_label:<14} {c_cyan}{count:>2}{c_reset} ({pct:>5.1f}%)  [{c_dim}{bar}{c_reset}]")

            # Quantitative Averages
            mean_tokens = summary.get("mean_total_tokens", 0.0)
            mean_overhead = summary.get("mean_framework_overhead_tokens", 0.0)
            overhead_pct = (mean_overhead / max(1.0, mean_tokens)) * 100.0
            rework_ratio = summary.get("mean_rework_ratio_pct", 0.0)
            ux_score = summary.get("mean_ux_state_completeness_pct", 0.0)
            overhead_just = summary.get("overhead_justified_rate_pct", 0.0)
            turns = summary.get("mean_turns_per_task", 0.0)

            lines.append(f"\n  {c_bold}Empirical Metrics (Mean Aggregates):{c_reset}")
            bullet = "•" if use_unicode else "*"
            lines.append(f"    {bullet} Total Tokens:            {c_bold}{mean_tokens:,.0f}{c_reset}")
            lines.append(f"    {bullet} Framework Overhead:      {c_cyan}{mean_overhead:,.0f} tokens{c_reset} ({overhead_pct:.1f}% of total)")
            lines.append(f"    {bullet} Mean Rework Ratio:       {c_green if rework_ratio < 5.0 else c_yellow}{rework_ratio:.1f}%{c_reset}")
            lines.append(f"    {bullet} UX State Completeness:   {c_cyan}{ux_score:.1f}%{c_reset}")
            lines.append(f"    {bullet} Overhead Justified Rate: {c_green if overhead_just >= 70 else c_yellow}{overhead_just:.1f}%{c_reset}")
            lines.append(f"    {bullet} Average Turns / Task:    {turns:.1f}")

    lines.append(f"{c_cyan}{border}{c_reset}")
    lines.append(f"  {c_dim}Local Check Timestamp: {result['timestamp']}{c_reset}")
    return "\n".join(lines)


def format_stream_line(result: Dict[str, Any], prev_result: Optional[Dict[str, Any]] = None, no_color: bool = False) -> str:
    """Formats a single compact one-line log entry for streaming/continuous logs."""
    c_bold = "" if no_color else BOLD
    c_reset = "" if no_color else RESET
    c_green = "" if no_color else GREEN
    c_yellow = "" if no_color else YELLOW
    c_red = "" if no_color else RED
    c_cyan = "" if no_color else CYAN

    ts = datetime.now().strftime("%H:%M:%S")
    h = result["health"]
    s = result["stats"]

    if h["ok"] and h["service_status"] == "healthy":
        status_txt = f"{c_green}UP{c_reset}"
    else:
        status_txt = f"{c_red}DOWN{c_reset}"

    lat = f"{h['latency_ms']:.0f}ms"
    sub_count = s["data"].get("total_submissions", 0) if s["ok"] else 0

    delta_txt = ""
    if prev_result and prev_result.get("stats", {}).get("ok"):
        p_sub = prev_result["stats"]["data"].get("total_submissions", 0)
        diff = sub_count - p_sub
        if diff > 0:
            delta_txt = f" {c_green}(+{diff}){c_reset}"

    return f"[{ts}] Status: {status_txt} | RTT: {c_cyan}{lat:>5}{c_reset} | Submissions: {c_bold}{sub_count}{c_reset}{delta_txt}"


def clear_screen():
    """Clears terminal screen cross-platform."""
    if sys.platform == "win32":
        os.system("cls")
    else:
        sys.stdout.write("\033[2J\033[H")
        sys.stdout.flush()


def parse_args():
    parser = argparse.ArgumentParser(
        description="PXOS Telemetry Daemon & Public Submissions Monitor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument("--url", default=DEFAULT_BASE_URL, help=f"Telemetry server base URL (default: {DEFAULT_BASE_URL})")
    parser.add_argument("--watch", "-w", action="store_true", help="Continuously monitor in watch mode")
    parser.add_argument("--interval", "-i", type=float, default=15.0, help="Polling interval in seconds for watch mode (default: 15.0, min: 2.0)")
    parser.add_argument("--count", "-n", type=int, default=None, help="Number of iterations to run in watch mode before stopping (default: unlimited)")
    parser.add_argument("--stream", action="store_true", help="In watch mode, stream log lines instead of in-place screen refresh")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON and exit")
    parser.add_argument("--max-latency-ms", type=float, default=None, help="Alert threshold: exit code 1 if health latency exceeds this limit")
    parser.add_argument("--min-submissions", type=int, default=None, help="Assertion: exit code 1 if total submissions is below this count")
    parser.add_argument("--require-healthy", action="store_true", help="Exit code 1 if health check fails or returns non-healthy status")
    parser.add_argument("--no-color", action="store_true", help="Disable ANSI terminal colors")
    parser.add_argument("--timeout", type=float, default=5.0, help="HTTP request timeout in seconds (default: 5.0)")
    return parser.parse_args()


def main():
    args = parse_args()
    base_url = clean_base_url(args.url)
    no_color = args.no_color or not sys.stdout.isatty()

    if args.interval < 2.0:
        args.interval = 2.0

    if args.json:
        result = probe_telemetry_service(base_url, timeout=args.timeout)
        healthy_flag = result["health"]["ok"] and result["health"]["service_status"] == "healthy"
        latency_ok = True
        if args.max_latency_ms is not None:
            latency_ok = result["health"]["latency_ms"] <= args.max_latency_ms

        subs = result["stats"]["data"].get("total_submissions", 0) if result["stats"]["ok"] else 0
        min_subs_ok = True
        if args.min_submissions is not None:
            min_subs_ok = subs >= args.min_submissions

        output_payload = {
            "probe_result": result,
            "checks": {
                "daemon_healthy": healthy_flag,
                "latency_within_threshold": latency_ok,
                "min_submissions_met": min_subs_ok,
                "overall_success": healthy_flag and latency_ok and min_subs_ok
            }
        }
        print(json.dumps(output_payload, indent=2))
        sys.exit(0 if output_payload["checks"]["overall_success"] else 1)

    # Watch Mode
    if args.watch:
        print(f"Starting PXOS Telemetry Monitor watch mode against {base_url} (Interval: {args.interval}s)...")
        print("Press Ctrl+C to stop.\n")
        prev_result = None
        iteration = 0
        try:
            while True:
                result = probe_telemetry_service(base_url, timeout=args.timeout)
                if args.stream:
                    print(format_stream_line(result, prev_result, no_color))
                    sys.stdout.flush()
                else:
                    clear_screen()
                    print(format_dashboard(result, prev_result, no_color))
                    print(f"\n[Watching] Refreshing every {args.interval}s... (Press Ctrl+C to exit)")
                    sys.stdout.flush()

                prev_result = result
                iteration += 1
                if args.count is not None and iteration >= args.count:
                    break
                time.sleep(args.interval)
        except KeyboardInterrupt:
            print("\n\nMonitor stopped by user.")
            sys.exit(0)
        sys.exit(0)

    # Snapshot Mode (default)
    result = probe_telemetry_service(base_url, timeout=args.timeout)
    print(format_dashboard(result, no_color=no_color))
    sys.stdout.flush()

    # Evaluate assertions / thresholds
    h = result["health"]
    s = result["stats"]
    is_healthy = h["ok"] and h["service_status"] == "healthy"
    exit_code = 0

    if args.require_healthy or not h["ok"]:
        if not is_healthy:
            sys.stdout.flush()
            print(f"\n[ALERT] Telemetry daemon is not healthy! (Status: {h.get('service_status')}, Error: {h.get('error')})", file=sys.stderr)
            exit_code = 1

    if args.max_latency_ms is not None:
        if h["latency_ms"] > args.max_latency_ms:
            sys.stdout.flush()
            print(f"\n[ALERT] Latency threshold breached: {h['latency_ms']:.1f}ms > {args.max_latency_ms:.1f}ms", file=sys.stderr)
            exit_code = 1

    if args.min_submissions is not None:
        sub_count = s["data"].get("total_submissions", 0) if s["ok"] else 0
        if sub_count < args.min_submissions:
            sys.stdout.flush()
            print(f"\n[ALERT] Submissions count below threshold: {sub_count} < {args.min_submissions}", file=sys.stderr)
            exit_code = 1

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
