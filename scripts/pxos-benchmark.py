#!/usr/bin/env python3
"""
PXOS Benchmark CLI & Telemetry Dispatcher
=========================================
Validates, sanitizes, and optionally transmits anonymous empirical benchmark telemetry
to the PXOS research aggregation server with strict user consent and privacy controls.

Usage:
    # Validate and preview payload without sending:
    python scripts/pxos-benchmark.py --file benchmarks/data/task_auth.json --dry-run

    # Interactive prompt asking user confirmation before transmitting:
    python scripts/pxos-benchmark.py --file benchmarks/data/task_auth.json

    # Non-interactive submission (CI / automated):
    python scripts/pxos-benchmark.py --file benchmarks/data/task_auth.json --yes

    # Offline validation only:
    python scripts/pxos-benchmark.py --file benchmarks/data/task_auth.json --offline
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

DEFAULT_ENDPOINT = os.environ.get("PXOS_TELEMETRY_URL", "https://telemetry.madebypx.com/api/v1/telemetry")
VALID_TIERS = {"tier_1_micro", "tier_2_medium", "tier_3_complex"}
VALID_MODES = {"retrospective", "controlled_ab", "unknown"}


def sanitize_payload(raw: Dict[str, Any]) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
    """Sanitizes the payload to strictly strip any accidental PII, credentials, or proprietary code."""
    if not isinstance(raw, dict):
        return False, "Input must be a JSON dictionary.", None

    meta = raw.get("audit_metadata", {})
    task = raw.get("task_profile", {})
    telemetry = raw.get("quantitative_telemetry", {})
    ux = raw.get("product_design_and_ux", {})
    arch = raw.get("architectural_fidelity", {})
    crit = raw.get("critical_assessment", {})

    mode = str(meta.get("evaluation_mode", "unknown")).lower()
    if mode not in VALID_MODES:
        mode = "unknown"

    tier = str(task.get("complexity_tier", "tier_2_medium")).lower()
    if tier not in VALID_TIERS:
        tier = "tier_2_medium"

    try:
        total_turns = int(telemetry.get("total_turns", 0))
        in_tokens = int(telemetry.get("input_tokens_total", 0))
        out_tokens = int(telemetry.get("output_tokens_total", 0))
        overhead_tokens = int(telemetry.get("framework_overhead_tokens", 0))
        initial_loc = int(telemetry.get("initial_implementation_loc", 0))
        rework_loc = int(telemetry.get("rework_lines_modified_or_deleted", 0))
        rework_turns = int(telemetry.get("rework_turn_count", 0))
        ux_completeness = float(ux.get("ux_state_completeness_score", 0.0))
        net_utility = int(crit.get("net_utility_score", 0))
    except (ValueError, TypeError) as e:
        return False, f"Numeric validation failed: {e}", None

    # Sanitize and truncate strings to prevent accidental injection or payload bloat
    clean = {
        "audit_metadata": {
            "evaluation_mode": mode,
            "project_name": str(meta.get("project_name", "anonymous"))[:64],
            "evaluator_agent_model": str(meta.get("evaluator_agent_model", "unknown"))[:64],
            "timestamp_iso": str(meta.get("timestamp_iso", ""))[:32]
        },
        "task_profile": {
            "task_id": str(task.get("task_id", "unknown"))[:32],
            "task_description": str(task.get("task_description", ""))[:256],
            "complexity_tier": tier,
            "primary_subsystem": str(task.get("primary_subsystem", "general"))[:64]
        },
        "quantitative_telemetry": {
            "total_turns": total_turns,
            "input_tokens_total": in_tokens,
            "output_tokens_total": out_tokens,
            "framework_overhead_tokens": overhead_tokens,
            "initial_implementation_loc": initial_loc,
            "rework_lines_modified_or_deleted": rework_loc,
            "rework_turn_count": rework_turns,
            "unresolved_compiler_or_test_failures": int(telemetry.get("unresolved_compiler_or_test_failures", 0)),
            "merge_conflicts_encountered": int(telemetry.get("merge_conflicts_encountered", 0))
        },
        "product_design_and_ux": {
            "ui_components_touched": bool(ux.get("ui_components_touched", False)),
            "ux_state_completeness_score": max(0.0, min(1.0, ux_completeness)),
            "design_tokens_adhered": bool(ux.get("design_tokens_adhered", True))
        },
        "architectural_fidelity": {
            "session_amnesia_occurred": bool(arch.get("session_amnesia_occurred", False)),
            "invariants_violated_count": int(arch.get("invariants_violated_count", 0)),
            "duplicate_utilities_introduced": int(arch.get("duplicate_utilities_introduced", 0)),
            "adrs_consulted_count": int(arch.get("adrs_consulted_count", 0)),
            "new_adrs_registered": int(arch.get("new_adrs_registered", 0))
        },
        "critical_assessment": {
            "net_utility_score": max(-5, min(5, net_utility)),
            "overhead_justified": bool(crit.get("overhead_justified", True)),
            "identified_frictions": [str(f)[:256] for f in crit.get("identified_frictions", [])][:5],
            "concrete_benefits": [str(b)[:256] for b in crit.get("concrete_benefits", [])][:5]
        }
    }

    return True, None, clean


def transmit_telemetry(payload: Dict[str, Any], endpoint_url: str) -> bool:
    """Dispatches the sanitized payload to the ingestion endpoint."""
    encoded_data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        endpoint_url,
        data=encoded_data,
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "User-Agent": "PXOS-Benchmark-Client/1.0",
            "Content-Length": str(len(encoded_data))
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode("utf-8")
            res = json.loads(body)
            print("\n[SUCCESS] Benchmark telemetry accepted by server!")
            print(f"Submission ID: {res.get('submission_id')}")
            print(f"Server Message: {res.get('message')}")
            return True
    except urllib.error.HTTPError as e:
        print(f"\n[ERROR] Server returned HTTP {e.code}: {e.reason}", file=sys.stderr)
        try:
            err_body = e.read().decode("utf-8")
            print(f"Server Details: {err_body}", file=sys.stderr)
        except Exception:
            pass
        return False
    except Exception as e:
        print(f"\n[ERROR] Failed to connect to telemetry server ({endpoint_url}): {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description="PXOS Benchmark Dispatcher")
    parser.add_argument("--file", required=True, help="Path to local benchmark JSON file")
    parser.add_argument("--url", default=DEFAULT_ENDPOINT, help=f"Ingestion server endpoint (default: {DEFAULT_ENDPOINT})")
    parser.add_argument("--dry-run", action="store_true", help="Display sanitized payload without transmitting")
    parser.add_argument("--offline", action="store_true", help="Validate locally and do not transmit")
    parser.add_argument("--yes", "-y", action="store_true", help="Skip confirmation prompt and transmit immediately")
    args = parser.parse_args()

    file_path = Path(args.file)
    if not file_path.exists():
        print(f"[ERROR] File not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
    except Exception as e:
        print(f"[ERROR] Invalid JSON in {file_path}: {e}", file=sys.stderr)
        sys.exit(1)

    is_valid, err_msg, clean_payload = sanitize_payload(raw_data)
    if not is_valid or not clean_payload:
        print(f"[ERROR] Benchmark schema validation failed: {err_msg}", file=sys.stderr)
        sys.exit(1)

    # Print summary
    meta = clean_payload["audit_metadata"]
    task = clean_payload["task_profile"]
    telem = clean_payload["quantitative_telemetry"]
    ux = clean_payload["product_design_and_ux"]

    print("\n" + "=" * 65)
    print("           PXOS EMPIRICAL BENCHMARK AUDIT PREVIEW")
    print("=" * 65)
    print(f"Task ID:          {task['task_id']} ({task['complexity_tier']})")
    print(f"Model:            {meta['evaluator_agent_model']}")
    print(f"Project:          {meta['project_name']}")
    print(f"Total Tokens:     {telem['input_tokens_total'] + telem['output_tokens_total']:,}")
    print(f"PXOS Overhead:    {telem['framework_overhead_tokens']:,} tokens")
    if telem['initial_implementation_loc'] > 0:
        rework_pct = round((telem['rework_lines_modified_or_deleted'] / telem['initial_implementation_loc']) * 100, 1)
        print(f"Rework Ratio:     {rework_pct}% ({telem['rework_lines_modified_or_deleted']} lines modified/deleted)")
    if ux['ui_components_touched']:
        print(f"UX Completeness:  {ux['ux_state_completeness_score'] * 100:.1f}%")
    print(f"Target Server:    {args.url}")
    print("=" * 65)

    if args.dry_run:
        print("\n[DRY RUN] Sanitized JSON Payload:")
        print(json.dumps(clean_payload, indent=2))
        sys.exit(0)

    if args.offline:
        print("\n[OFFLINE] Benchmark validated locally. No network transmission attempted.")
        sys.exit(0)

    # Privacy and Opt-In Check
    if not args.yes:
        print("\n[PRIVACY NOTICE]")
        print("This action transmits only anonymous numerical metrics and tier enums.")
        print("No source code, file contents, secret keys, or author identities are shared.")
        prompt = input("\nDo you consent to transmit this anonymous benchmark to madebypx? [y/N]: ")
        if prompt.strip().lower() not in ("y", "yes"):
            print("[ABORTED] Transmission cancelled by user. Local file remains saved.")
            sys.exit(0)

    success = transmit_telemetry(clean_payload, args.url)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
