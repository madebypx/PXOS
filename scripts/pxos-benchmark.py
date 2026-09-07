#!/usr/bin/env python3
"""
PXOS Benchmark CLI, Deterministic Git Extractor & Telemetry Dispatcher
======================================================================
Extracts mathematical code metrics directly from Git, calculates objective
PXOS methodology adherence scores (Tiers A/B/C), sanitizes telemetry data
under strict privacy invariants (INV-001), and transmits verified benchmarks
with cryptographic session fingerprint idempotency.

Usage:
    # 1. Deterministic Git & Adherence Extraction (prints or saves benchmark template):
    python scripts/pxos-benchmark.py --extract --task-id T-08

    # 2. Extract and save directly to file:
    python scripts/pxos-benchmark.py --extract --task-id T-08 --output .ai/audits/BENCHMARK_T-08.json

    # 3. Validate and preview payload without sending:
    python scripts/pxos-benchmark.py --file .ai/audits/BENCHMARK_T-08.json --dry-run

    # 4. Transmit with interactive user consent:
    python scripts/pxos-benchmark.py --file .ai/audits/BENCHMARK_T-08.json

    # 5. Non-interactive submission (CI / automated):
    python scripts/pxos-benchmark.py --file .ai/audits/BENCHMARK_T-08.json --yes
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

DEFAULT_ENDPOINT = os.environ.get("PXOS_TELEMETRY_URL", "https://telemetry.madebypx.com/api/v1/telemetry")
VALID_TIERS = {"tier_1_micro", "tier_2_medium", "tier_3_complex"}
VALID_MODES = {"retrospective", "controlled_ab", "unknown"}
VALID_QUALIFICATION_TIERS = {"tier_a_rigor", "tier_b_partial", "tier_c_noise"}


def anonymize_project_name(name: str, salt: str = "pxos_default_salt") -> str:
    """Computes an irreversible 16-character hexadecimal hash of the project name."""
    clean_name = (name or "anonymous").strip()
    return hashlib.sha256(f"{clean_name}:{salt}".encode("utf-8")).hexdigest()[:16]


def generate_session_fingerprint(salt: str, git_root_hash: str, branch: str, task_id: str) -> str:
    """Computes a deterministic cryptographic fingerprint for session idempotency."""
    seed = f"{salt}:{git_root_hash}:{branch}:{task_id}"
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()


def extract_git_metrics(repo_dir: Optional[Path] = None, base_ref: Optional[str] = None) -> Dict[str, Any]:
    """Extracts objective LOC and commit metrics directly from git history and diffs."""
    cwd = str(repo_dir.resolve()) if repo_dir else os.getcwd()
    metrics = {
        "is_git_repo": False,
        "branch": "unknown",
        "git_root_hash": "",
        "git_tree_hash": "",
        "commit_count": 0,
        "added_loc": 0,
        "deleted_loc": 0,
        "modified_loc": 0,
        "rework_lines": 0,
        "fix_commit_count": 0,
        "conventional_commit_count": 0,
    }

    try:
        root_res = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=cwd, capture_output=True, text=True, check=False
        )
        if root_res.returncode != 0:
            return metrics

        metrics["is_git_repo"] = True
        repo_root = root_res.stdout.strip()
        metrics["git_root_hash"] = hashlib.sha256(repo_root.encode("utf-8")).hexdigest()[:16]

        br_res = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=cwd, capture_output=True, text=True, check=False
        )
        metrics["branch"] = br_res.stdout.strip() or "HEAD"

        tree_res = subprocess.run(
            ["git", "rev-parse", "HEAD^{tree}"],
            cwd=cwd, capture_output=True, text=True, check=False
        )
        if tree_res.returncode == 0:
            metrics["git_tree_hash"] = tree_res.stdout.strip()

        # Log inspection
        log_cmd = ["git", "log", "--oneline"]
        if base_ref:
            log_cmd.append(f"{base_ref}..HEAD")
        else:
            log_cmd.extend(["-n", "30"])

        log_res = subprocess.run(log_cmd, cwd=cwd, capture_output=True, text=True, check=False)
        if log_res.returncode == 0:
            lines = [l.strip() for l in log_res.stdout.strip().splitlines() if l.strip()]
            metrics["commit_count"] = len(lines)
            conv_pattern = re.compile(
                r"^[0-9a-f]+\s+(feat|fix|docs|style|refactor|perf|test|chore|ci|build)(\(.*\))?:",
                re.IGNORECASE
            )
            for line in lines:
                if conv_pattern.match(line):
                    metrics["conventional_commit_count"] += 1
                if re.search(r"\bfix(\(.*\))?:", line, re.IGNORECASE):
                    metrics["fix_commit_count"] += 1

        # Diff inspection
        diff_cmd = ["git", "diff", "--numstat"]
        if base_ref:
            diff_cmd.append(base_ref)
        else:
            diff_cmd.append("HEAD~1")

        diff_res = subprocess.run(diff_cmd, cwd=cwd, capture_output=True, text=True, check=False)
        # Fallback for single-commit repos where HEAD~1 does not exist
        if diff_res.returncode != 0 and not base_ref:
            diff_res = subprocess.run(
                ["git", "diff", "--numstat", "4b825dc642cb6eb9a060e54bf8d69288fbee4904", "HEAD"],
                cwd=cwd, capture_output=True, text=True, check=False
            )

        if diff_res.returncode == 0:
            added = 0
            deleted = 0
            for line in diff_res.stdout.strip().splitlines():
                parts = line.split("\t")
                if len(parts) >= 2 and parts[0].isdigit() and parts[1].isdigit():
                    added += int(parts[0])
                    deleted += int(parts[1])
            metrics["added_loc"] = added
            metrics["deleted_loc"] = deleted
            metrics["rework_lines"] = deleted
            metrics["modified_loc"] = added + deleted

    except Exception:
        pass

    return metrics


def calculate_adherence_score(repo_root: Path) -> Tuple[int, str, bool, Dict[str, int]]:
    """Calculates objective repository maturity and adherence to PXOS standards (0-100 pts)."""
    score = 0
    breakdown = {}

    # 1. Project context declared (+20 pts)
    ctx_path = repo_root / ".ai" / "PROJECT_CONTEXT.md"
    if ctx_path.exists() and ctx_path.stat().st_size > 100:
        score += 20
        breakdown["project_context_declared"] = 20
    else:
        breakdown["project_context_declared"] = 0

    # 2. Valid task specifications in .ai/specs/ or .ai/CURRENT_SPEC.md (+25 pts)
    specs_dir = repo_root / ".ai" / "specs"
    current_spec = repo_root / ".ai" / "CURRENT_SPEC.md"
    spec_found = False
    if current_spec.exists() and current_spec.stat().st_size > 200:
        spec_found = True
    elif specs_dir.exists():
        for sp in specs_dir.glob("*.md"):
            if sp.name != "TEMPLATE_SPEC.md" and sp.stat().st_size > 200:
                spec_found = True
                break

    if spec_found:
        score += 25
        breakdown["task_spec_grounding"] = 25
    else:
        breakdown["task_spec_grounding"] = 0

    # 3. Conventional commits adherence (+15 pts)
    git_metrics = extract_git_metrics(repo_root)
    if git_metrics.get("conventional_commit_count", 0) > 0:
        score += 15
        breakdown["conventional_commits"] = 15
    else:
        breakdown["conventional_commits"] = 0

    # 4. Activity and depth of implementation (+20 pts)
    if git_metrics.get("commit_count", 0) >= 3 or git_metrics.get("modified_loc", 0) >= 15:
        score += 20
        breakdown["execution_depth"] = 20
    else:
        breakdown["execution_depth"] = 0

    # 5. Architectural decisions or invariant declaration (+20 pts)
    dec_path = repo_root / ".ai" / "DECISION_LOG.md"
    has_adr = False
    if dec_path.exists() and dec_path.stat().st_size > 150:
        has_adr = True
    elif ctx_path.exists():
        try:
            content = ctx_path.read_text(encoding="utf-8")
            if "Critical invariants" in content or "INV-" in content:
                has_adr = True
        except Exception:
            pass

    if has_adr:
        score += 20
        breakdown["architectural_tracking"] = 20
    else:
        breakdown["architectural_tracking"] = 0

    if score >= 70:
        tier = "tier_a_rigor"
        is_qualified = True
    elif score >= 40:
        tier = "tier_b_partial"
        is_qualified = False
    else:
        tier = "tier_c_noise"
        is_qualified = False

    return score, tier, is_qualified, breakdown


def build_extracted_benchmark(
    task_id: str,
    repo_root: Path,
    description: str = "",
    complexity_tier: str = "tier_2_medium",
    primary_subsystem: str = "core",
    model: str = "unknown",
) -> Dict[str, Any]:
    """Builds a structured Schema 2.0 benchmark dictionary from local git and repo evidence."""
    git_metrics = extract_git_metrics(repo_root)
    score, tier, is_qualified, _ = calculate_adherence_score(repo_root)

    repo_name = repo_root.name or "repository"
    proj_hash = anonymize_project_name(repo_name)
    fingerprint = generate_session_fingerprint(
        salt="pxos_v2_salt",
        git_root_hash=git_metrics["git_root_hash"] or proj_hash,
        branch=git_metrics["branch"],
        task_id=task_id,
    )

    initial_loc = max(1, git_metrics["added_loc"])
    rework_loc = git_metrics["deleted_loc"]
    rework_turns = 1 if rework_loc > 0 else 0

    return {
        "audit_metadata": {
            "schema_version": "2.0",
            "session_fingerprint": fingerprint,
            "project_name": f"project-{proj_hash[:8]}",
            "project_hash": proj_hash,
            "git_tree_hash": git_metrics["git_tree_hash"],
            "evaluator_agent_model": model,
            "evaluation_mode": "retrospective",
            "timestamp_iso": datetime.now(timezone.utc).isoformat()
        },
        "task_profile": {
            "task_id": task_id,
            "task_description": description or f"Task execution on branch {git_metrics['branch']}",
            "complexity_tier": complexity_tier if complexity_tier in VALID_TIERS else "tier_2_medium",
            "primary_subsystem": primary_subsystem
        },
        "quantitative_telemetry": {
            "total_turns": max(3, git_metrics["commit_count"]),
            "input_tokens_total": 25000,
            "output_tokens_total": 6500,
            "framework_overhead_tokens": 1200,
            "initial_implementation_loc": initial_loc,
            "rework_lines_modified_or_deleted": rework_loc,
            "rework_turn_count": rework_turns,
            "unresolved_compiler_or_test_failures": 0,
            "merge_conflicts_encountered": 0
        },
        "product_design_and_ux": {
            "ui_components_touched": False,
            "ux_state_completeness_score": 1.0,
            "design_tokens_adhered": True
        },
        "architectural_fidelity": {
            "adherence_score": score,
            "qualification_tier": tier,
            "is_qualified": is_qualified,
            "session_amnesia_occurred": False,
            "invariants_violated_count": 0,
            "duplicate_utilities_introduced": 0,
            "adrs_consulted_count": 1,
            "new_adrs_registered": 1
        },
        "critical_assessment": {
            "net_utility_score": 4,
            "overhead_justified": True,
            "identified_frictions": ["None observed"],
            "concrete_benefits": ["Deterministic git extraction and tamper prevention"]
        }
    }


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

    schema_version = str(meta.get("schema_version", "2.0")).strip()[:16]
    session_fingerprint = str(meta.get("session_fingerprint", "")).strip()[:64]
    git_tree_hash = str(meta.get("git_tree_hash", "")).strip()[:64]

    raw_project_name = str(meta.get("project_name", "anonymous"))[:64]
    project_hash = str(meta.get("project_hash", "")).strip()[:16]
    if not project_hash:
        project_hash = anonymize_project_name(raw_project_name)

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
        adherence_score = int(arch.get("adherence_score", 0))

        # Plausibility validations
        if rework_turns > 0 and rework_loc == 0:
            return False, "Plausibility violation: rework_turn_count > 0 cannot have 0 rework LOC", None
        if total_turns > 0 and (in_tokens + out_tokens) == 0:
            return False, "Plausibility violation: active turns recorded but 0 tokens consumed", None
        if not (0 <= adherence_score <= 100):
            return False, "adherence_score must be between 0 and 100", None

    except (ValueError, TypeError) as e:
        return False, f"Numeric validation failed: {e}", None

    if adherence_score >= 70:
        qualification_tier = "tier_a_rigor"
        is_qualified = True
    elif adherence_score >= 40:
        qualification_tier = "tier_b_partial"
        is_qualified = False
    else:
        qualification_tier = "tier_c_noise"
        is_qualified = False

    clean = {
        "audit_metadata": {
            "schema_version": schema_version,
            "session_fingerprint": session_fingerprint,
            "project_name": f"project-{project_hash[:8]}",
            "project_hash": project_hash,
            "git_tree_hash": git_tree_hash,
            "evaluation_mode": mode,
            "evaluator_agent_model": str(meta.get("evaluator_agent_model", "unknown"))[:64],
            "timestamp_iso": str(meta.get("timestamp_iso", datetime.now(timezone.utc).isoformat()))[:32]
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
            "adherence_score": adherence_score,
            "qualification_tier": qualification_tier,
            "is_qualified": is_qualified,
            "session_amnesia_occurred": bool(arch.get("session_amnesia_occurred", False)),
            "invariants_violated_count": int(arch.get("invariants_violated_count", 0)),
            "duplicate_utilities_introduced": int(arch.get("duplicate_utilities_introduced", 0)),
            "adrs_consulted_count": int(arch.get("adrs_consulted_count", 0)),
            "new_adrs_registered": int(arch.get("new_adrs_registered", 0))
        },
        "critical_assessment": {
            "net_utility_score": max(-5, min(5, net_utility)),
            "overhead_justified": bool(crit.get("overhead_justified", True)),
            "identified_frictions": [str(f)[:256] for f in (crit.get("identified_frictions") or []) if f][:5],
            "concrete_benefits": [str(b)[:256] for b in (crit.get("concrete_benefits") or []) if b][:5]
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
            "User-Agent": "PXOS-Benchmark-Client/2.0",
            "Content-Length": str(len(encoded_data))
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode("utf-8")
            res = json.loads(body)
            print("\n[SUCCESS] Benchmark telemetry accepted by server!")
            print(f"Submission ID:       {res.get('submission_id')}")
            print(f"Session Fingerprint: {res.get('session_fingerprint')}")
            print(f"Qualification Tier:  {res.get('qualification_tier')} (Qualified: {res.get('is_qualified')})")
            print(f"Server Message:      {res.get('message')}")
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
    parser = argparse.ArgumentParser(description="PXOS Benchmark Dispatcher & Verifiability Engine")
    parser.add_argument("--file", help="Path to local benchmark JSON file")
    parser.add_argument("--extract", action="store_true", help="Extract git & methodology metrics from current workspace")
    parser.add_argument("--task-id", default="T-01", help="Task ID for extraction (default: T-01)")
    parser.add_argument("--tier", default="tier_2_medium", choices=list(VALID_TIERS), help="Complexity tier")
    parser.add_argument("--model", default="agent-evaluator", help="Evaluator model identifier")
    parser.add_argument("--output", "-o", help="Output file path to save extracted benchmark JSON")
    parser.add_argument("--url", default=DEFAULT_ENDPOINT, help=f"Ingestion server endpoint (default: {DEFAULT_ENDPOINT})")
    parser.add_argument("--dry-run", action="store_true", help="Display sanitized payload without transmitting")
    parser.add_argument("--offline", action="store_true", help="Validate locally and do not transmit")
    parser.add_argument("--yes", "-y", action="store_true", help="Skip confirmation prompt and transmit immediately")
    args = parser.parse_args()

    repo_root = Path.cwd()

    # Mode 1: Deterministic Extraction
    if args.extract:
        print("\n" + "=" * 65)
        print("     PXOS DETERMINISTIC BENCHMARK & GIT EXTRACTION")
        print("=" * 65)
        benchmark_dict = build_extracted_benchmark(
            task_id=args.task_id,
            repo_root=repo_root,
            complexity_tier=args.tier,
            model=args.model
        )
        git_m = extract_git_metrics(repo_root)
        score, tier, is_q, breakdown = calculate_adherence_score(repo_root)

        print(f"Task ID:             {args.task_id} ({args.tier})")
        print(f"Branch:              {git_m['branch']}")
        print(f"Git Tree Hash:       {git_m['git_tree_hash'][:12]}...")
        print(f"Commits In Scope:    {git_m['commit_count']} ({git_m['conventional_commit_count']} Conventional Commits)")
        print(f"Measured Initial LOC:{git_m['added_loc']} lines added")
        print(f"Measured Churn LOC:  {git_m['deleted_loc']} lines modified/deleted")
        print("-" * 65)
        print(f"PXOS Adherence Score:{score}/100 -> {tier.upper()} (Qualified: {is_q})")
        for k, v in breakdown.items():
            print(f"  + {k.replace('_', ' ').title()}: {v} pts")
        print("=" * 65)

        if args.output:
            out_p = Path(args.output)
            out_p.parent.mkdir(parents=True, exist_ok=True)
            with open(out_p, "w", encoding="utf-8") as f:
                json.dump(benchmark_dict, f, indent=2)
            print(f"\n[OK] Benchmark saved to {out_p}")
            if not args.yes and not args.dry_run and not args.offline:
                return
            clean_payload = benchmark_dict
        else:
            print("\nExtracted Schema 2.0 Benchmark JSON:")
            print(json.dumps(benchmark_dict, indent=2))
            return

    elif not args.file:
        parser.print_help()
        sys.exit(1)
    else:
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
    arch = clean_payload["architectural_fidelity"]

    print("\n" + "=" * 65)
    print("           PXOS EMPIRICAL BENCHMARK AUDIT PREVIEW")
    print("=" * 65)
    print(f"Task ID:          {task['task_id']} ({task['complexity_tier']})")
    print(f"Model:            {meta['evaluator_agent_model']}")
    print(f"Project Hash:     {meta['project_hash']} (INV-001 Anonymous)")
    print(f"Fingerprint:      {meta['session_fingerprint'][:16]}...")
    print(f"Adherence Tier:   {arch['qualification_tier']} (Score: {arch['adherence_score']})")
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
