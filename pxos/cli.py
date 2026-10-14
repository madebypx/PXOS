"""PXOS Command-Line Interface.

Zero-dependency CLI for initializing, updating, and benchmarking PXOS
across any developer workstation or automated CI environment.
"""

import argparse
import os
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

VERSION = "2.7.1"
REPO_RAW_BASE = "https://raw.githubusercontent.com/madebypx/PXOS/main"

# ANSI Color Codes
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"


def log(msg: str):
    print(f"{CYAN}[PXOS]{RESET} {msg}")


def ok(msg: str):
    print(f"{GREEN}[PXOS]{RESET} {msg}")


def warn(msg: str):
    print(f"{YELLOW}[PXOS]{RESET} {msg}")


def err(msg: str):
    print(f"{RED}[PXOS]{RESET} {msg}", file=sys.stderr)


def get_resource_path(relative_path: str) -> Path:
    """Finds a template or script from repository root if in repo, falling back to package data."""
    repo_root = Path(__file__).resolve().parent.parent
    if (repo_root / ".git").exists():
        repo_res = repo_root / relative_path
        if repo_res.exists():
            return repo_res

    pkg_res = Path(__file__).resolve().parent / relative_path
    if pkg_res.exists():
        return pkg_res
    repo_res = repo_root / relative_path
    if repo_res.exists():
        return repo_res
    return pkg_res


def download_or_copy(src_rel: str, dest_path: Path, overwrite: bool = False):
    """Download a file from GitHub raw or copy from local package/repo if available."""
    if dest_path.exists() and not overwrite:
        warn(f"Skipping {dest_path.name} — already exists.")
        return

    dest_path.parent.mkdir(parents=True, exist_ok=True)

    # If running from installed package or local PXOS repository clone
    local_src = get_resource_path(src_rel)
    if local_src.exists() and local_src.is_file():
        dest_path.write_bytes(local_src.read_bytes())
    else:
        url = f"{REPO_RAW_BASE}/{src_rel}"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": f"pxos-cli/{VERSION}"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                dest_path.write_bytes(resp.read())
        except Exception as e:
            err(f"Failed to fetch {url}: {e}")
            return

    if overwrite and dest_path.exists():
        ok(f"Updated {dest_path}")
    else:
        ok(f"Created {dest_path}")


ADDONS = {
    "evidence": {
        "title": "Evidence-First Scientific & DSR Governance Addon",
        "files": [
            ("templates/addons/evidence/.ai/research/00-governance/research-protocol.md", Path(".ai/research/00-governance/research-protocol.md")),
            ("templates/addons/evidence/.ai/research/00-governance/ai-governance.md", Path(".ai/research/00-governance/ai-governance.md")),
            ("templates/addons/evidence/.ai/research/00-governance/adversarial-reviewer.md", Path(".ai/research/00-governance/adversarial-reviewer.md")),
            ("templates/addons/evidence/.ai/research/evidence-matrix.csv", Path(".ai/research/evidence-matrix.csv")),
            ("templates/addons/evidence/.ai/research/source-register.csv", Path(".ai/research/source-register.csv")),
            ("templates/addons/evidence/.ai/research/negative-cases.md", Path(".ai/research/negative-cases.md")),
            ("templates/addons/evidence/.ai/research/rejected-claims.md", Path(".ai/research/rejected-claims.md")),
        ],
        "rules": "templates/addons/evidence/rules/evidence_first_research.md",
    },
    "maestri": {
        "title": "Maestri Spatial Canvas & Multi-Agent Swarm Addon",
        "files": [
            ("templates/addons/maestri/.ai/canvas/operational-board.md", Path(".ai/canvas/operational-board.md")),
            ("templates/addons/maestri/.ai/canvas/architecture-board.md", Path(".ai/canvas/architecture-board.md")),
            ("templates/addons/maestri/.ai/canvas/swarm-protocol.md", Path(".ai/canvas/swarm-protocol.md")),
        ],
        "rules": "templates/addons/maestri/rules/maestri_bridge.md",
    },
}


def append_pxos_block(
    dest_path: Path,
    content: str,
    start_marker: str = "<!-- pxos:start -->",
    end_marker: str = "<!-- pxos:end -->",
    block_name: str = "PXOS rules",
):
    """Append or replace a managed block inside an existing markdown file."""
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    if dest_path.exists():
        text = dest_path.read_text(encoding="utf-8")
        if start_marker in text:
            pattern = re.compile(rf"{re.escape(start_marker)}.*?{re.escape(end_marker)}", re.DOTALL)
            replacement = f"{start_marker}\n{content}\n{end_marker}"
            new_text = pattern.sub(replacement, text)
            dest_path.write_text(new_text, encoding="utf-8")
            ok(f"Updated {block_name} block in {dest_path}")
            return
        appended = f"{text}\n\n---\n\n{start_marker}\n{content}\n{end_marker}\n"
        dest_path.write_text(appended, encoding="utf-8")
        ok(f"Appended {block_name} to {dest_path}")
    else:
        initial = f"{start_marker}\n{content}\n{end_marker}\n"
        dest_path.write_text(initial, encoding="utf-8")
        ok(f"Created {dest_path}")


def detect_ide() -> str:
    """Auto-detect configured AI IDE in current workspace."""
    if Path(".cursor").exists():
        return "cursor"
    if Path(".windsurf").exists():
        return "windsurf"
    if Path("CLAUDE.md").exists():
        return "claude"
    if Path("GEMINI.md").exists():
        return "gemini"
    if Path(".github/copilot-instructions.md").exists():
        return "copilot"
    return ""


def configure_addon_ide_rules(addon_key: str, ide: str, global_mode: bool = False):
    """Setup editor rules for a specific addon."""
    addon = ADDONS.get(addon_key)
    if not addon or "rules" not in addon:
        return

    rules_src = get_resource_path(addon["rules"])
    content = ""
    if rules_src.exists():
        content = rules_src.read_text(encoding="utf-8")
    else:
        url = f"{REPO_RAW_BASE}/{addon['rules']}"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": f"pxos-cli/{VERSION}"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                content = resp.read().decode("utf-8")
        except Exception as e:
            warn(f"Could not retrieve addon rules template from {url}: {e}")
            return

    if not content:
        warn("Could not retrieve addon IDE rules template.")
        return

    user_home = Path.home()
    ide = ide.lower()
    start_marker = f"<!-- pxos:{addon_key}:start -->"
    end_marker = f"<!-- pxos:{addon_key}:end -->"
    block_name = f"PXOS {addon_key} rules"

    if ide == "cursor":
        rules_path = user_home / f".cursor/rules/pxos-{addon_key}.mdc" if global_mode else Path(f".cursor/rules/pxos-{addon_key}.mdc")
        rules_path.parent.mkdir(parents=True, exist_ok=True)
        rules_path.write_text(f"---\nalwaysApply: true\n---\n\n{content}", encoding="utf-8")
        ok(f"Configured Cursor rules at {rules_path}")
    elif ide == "windsurf":
        rules_path = user_home / f".windsurf/rules/pxos-{addon_key}.md" if global_mode else Path(f".windsurf/rules/pxos-{addon_key}.md")
        rules_path.parent.mkdir(parents=True, exist_ok=True)
        rules_path.write_text(content, encoding="utf-8")
        ok(f"Configured Windsurf rules at {rules_path}")
    elif ide == "claude":
        rules_path = user_home / ".claude/CLAUDE.md" if global_mode else Path("CLAUDE.md")
        append_pxos_block(rules_path, content, start_marker, end_marker, block_name)
    elif ide == "gemini":
        rules_path = user_home / ".gemini/GEMINI.md" if global_mode else Path("GEMINI.md")
        append_pxos_block(rules_path, content, start_marker, end_marker, block_name)
    elif ide == "copilot":
        rules_path = Path(".github/copilot-instructions.md")
        append_pxos_block(rules_path, content, start_marker, end_marker, block_name)
    else:
        warn(f"Unknown IDE '{ide}'. Supported: cursor, windsurf, claude, gemini, copilot.")


def install_addon(addon_key: str, force: bool = False, ide: str = None, global_mode: bool = False):
    """Installs a modular PXOS addon into workspace."""
    if addon_key not in ADDONS:
        err(f"Unknown addon '{addon_key}'. Available addons: {', '.join(ADDONS.keys())}")
        sys.exit(1)

    addon = ADDONS[addon_key]
    log(f"Installing {addon['title']}...")

    for src_rel, dest_path in addon["files"]:
        download_or_copy(src_rel, dest_path, overwrite=force)

    # Scaffolding index link if .ai/research/INDEX.md exists
    research_idx = Path(".ai/research/INDEX.md")
    if research_idx.exists():
        text = research_idx.read_text(encoding="utf-8")
        if "00-governance/research-protocol.md" not in text:
            entry = "| [Research Protocol](00-governance/research-protocol.md) | Epistemic Governance & FAIR | 5-Layer Epistemic Model (`INSUFFICIENT EVIDENCE — DO NOT CONCLUDE`) | Active | Initial |"
            if "| *None yet*" in text:
                text = text.replace("| *None yet* | *Initial project setup* | *No active research constraints registered* | Active | YYYY-MM-DD |", entry)
            elif "## Active Research & Invariants" in text:
                header_block = "## Active Research & Invariants\n\n| Document | Topic / Subsystem | Key Takeaway / Invariant | Status | Last Updated |\n|---|---|---|---|---|"
                if header_block in text:
                    text = text.replace(header_block, f"{header_block}\n{entry}")
            research_idx.write_text(text, encoding="utf-8")
            ok(f"Linked research protocol in {research_idx}")

    target_ide = ide or detect_ide()
    if target_ide:
        configure_addon_ide_rules(addon_key, target_ide, global_mode=global_mode)

    print(f"\n{BOLD}{GREEN}PXOS addon '{addon_key}' installed successfully.{RESET}\n")
    if addon_key == "evidence":
        print("  Next steps:")
        print(f"  1. Consult {BOLD}.ai/research/00-governance/research-protocol.md{RESET} for epistemic guidelines.")
        print(f"  2. Register findings in {BOLD}.ai/research/evidence-matrix.csv{RESET} and sources in {BOLD}source-register.csv{RESET}.")
        print(f"  3. Use {BOLD}/peer-review{RESET} in your editor to adversarial stress-test claims before proposing ADRs.\n")
    elif addon_key == "maestri":
        print("  Next steps:")
        print(f"  1. Ensure the {BOLD}maestri{RESET} CLI is available on your PATH or via $MAESTRI_CLI.")
        print(f"  2. Consult your editor rules (e.g. {BOLD}.cursor/rules/pxos-maestri.mdc{RESET}) for spatial swarm guidelines.")
        print(f"  3. Use {BOLD}maestri list{RESET} and link {BOLD}.ai/canvas/operational-board.md{RESET} to your canvas.\n")


def configure_ide_rules(ide: str, global_mode: bool = False):
    """Setup editor rules for Cursor, Windsurf, Claude, Gemini, or Copilot."""
    rules_src = get_resource_path("templates/rules/pxos.md")
    content = ""
    if rules_src.exists():
        content = rules_src.read_text(encoding="utf-8")
    else:
        url = f"{REPO_RAW_BASE}/templates/rules/pxos.md"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": f"pxos-cli/{VERSION}"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                content = resp.read().decode("utf-8")
        except Exception:
            # Fallback to local AI_BASE.md
            ai_base = Path(".ai/AI_BASE.md")
            if ai_base.exists():
                content = ai_base.read_text(encoding="utf-8")

    if not content:
        warn("Could not retrieve IDE rules template.")
        return

    user_home = Path.home()
    ide = ide.lower()

    if ide == "cursor":
        rules_path = user_home / ".cursor/rules/pxos.mdc" if global_mode else Path(".cursor/rules/pxos.mdc")
        rules_path.parent.mkdir(parents=True, exist_ok=True)
        rules_path.write_text(f"---\nalwaysApply: true\n---\n\n{content}", encoding="utf-8")
        ok(f"Configured Cursor rules at {rules_path}")
    elif ide == "windsurf":
        rules_path = user_home / ".windsurf/rules/pxos.md" if global_mode else Path(".windsurf/rules/pxos.md")
        rules_path.parent.mkdir(parents=True, exist_ok=True)
        rules_path.write_text(content, encoding="utf-8")
        ok(f"Configured Windsurf rules at {rules_path}")
    elif ide == "claude":
        rules_path = user_home / ".claude/CLAUDE.md" if global_mode else Path("CLAUDE.md")
        append_pxos_block(rules_path, content)
    elif ide == "gemini":
        rules_path = user_home / ".gemini/GEMINI.md" if global_mode else Path("GEMINI.md")
        append_pxos_block(rules_path, content)
    elif ide == "copilot":
        rules_path = Path(".github/copilot-instructions.md")
        append_pxos_block(rules_path, content)
    else:
        warn(f"Unknown IDE '{ide}'. Supported: cursor, windsurf, claude, gemini, copilot.")


def cmd_add(args):
    """Install a modular PXOS addon."""
    install_addon(
        addon_key=args.addon.lower(),
        force=args.force,
        ide=args.ide,
        global_mode=args.global_mode,
    )


def cmd_init(args):
    """Initialize PXOS in the current workspace."""
    print(f"\n{BOLD}Installing PXOS v{VERSION}...{RESET}\n")
    target_dir = Path(".ai")

    log("Configuring .ai/")
    download_or_copy("templates/.ai/AI_BASE.md", target_dir / "AI_BASE.md")
    download_or_copy("templates/.ai/PROJECT_CONTEXT.md", target_dir / "PROJECT_CONTEXT.md")
    download_or_copy("templates/.ai/CURRENT_SPEC.md", target_dir / "CURRENT_SPEC.md")
    download_or_copy("templates/.ai/DECISION_LOG.md", target_dir / "DECISION_LOG.md")
    download_or_copy("templates/.ai/specs/TEMPLATE_SPEC.md", target_dir / "specs/TEMPLATE_SPEC.md")
    download_or_copy("templates/.ai/research/INDEX.md", target_dir / "research/INDEX.md")
    download_or_copy("templates/.ai/audits/README.md", target_dir / "audits/README.md")

    if args.full:
        log("Installing optional planning files...")
        download_or_copy("templates/ROADMAP.md", Path("ROADMAP.md"))
        download_or_copy("templates/SPRINT.md", Path("SPRINT.md"))

    ide = args.ide or detect_ide()
    if ide:
        configure_ide_rules(ide, global_mode=args.global_mode)

    if getattr(args, "evidence", False):
        install_addon("evidence", force=False, ide=ide, global_mode=args.global_mode)

    if getattr(args, "maestri", False):
        install_addon("maestri", force=False, ide=ide, global_mode=args.global_mode)

    print(f"\n{BOLD}{GREEN}PXOS v{VERSION} installed successfully.{RESET}\n")
    print("  Next steps:")
    print(f"  1. Review {BOLD}.ai/PROJECT_CONTEXT.md{RESET} to declare product context.")
    print(f"  2. Run {BOLD}/start{RESET} in your AI IDE to auto-resolve active specs.")
    print(f"  3. Use {BOLD}/spec{RESET} and {BOLD}/plan{RESET} before executing non-trivial code.")
    print("\n  Documentation: https://github.com/madebypx/PXOS\n")


def cmd_update(args):
    """Safely update PXOS rules and templates without clobbering project context."""
    print(f"\n{BOLD}Upgrading PXOS to v{VERSION}...{RESET}\n")
    target_dir = Path(".ai")

    log("Updating universal operational rules and modular specs...")
    download_or_copy("templates/.ai/AI_BASE.md", target_dir / "AI_BASE.md", overwrite=True)
    download_or_copy("templates/.ai/specs/TEMPLATE_SPEC.md", target_dir / "specs/TEMPLATE_SPEC.md", overwrite=True)

    # Scaffolding research/audits without clobbering
    (target_dir / "research").mkdir(parents=True, exist_ok=True)
    (target_dir / "audits").mkdir(parents=True, exist_ok=True)
    download_or_copy("templates/.ai/research/INDEX.md", target_dir / "research/INDEX.md", overwrite=False)
    download_or_copy("templates/.ai/audits/README.md", target_dir / "audits/README.md", overwrite=False)

    log("Preserved PROJECT_CONTEXT.md, DECISION_LOG.md, and all active specs.")

    if args.ide:
        configure_ide_rules(args.ide, global_mode=args.global_mode)

    print(f"\n{BOLD}{GREEN}PXOS upgraded to v{VERSION}.{RESET}\n")


def cmd_benchmark(args):
    """Run the empirical benchmark telemetry dispatcher."""
    script = get_resource_path("scripts/pxos-benchmark.py")
    if script.exists():
        cmd = [sys.executable, str(script)] + sys.argv[2:]
        sys.exit(subprocess.call(cmd))
    else:
        err(f"scripts/pxos-benchmark.py not found at {script}.")
        sys.exit(1)


def cmd_monitor(args):
    """Run the telemetry daemon monitor utility."""
    script = get_resource_path("scripts/pxos-telemetry-monitor.py")
    if script.exists():
        cmd = [sys.executable, str(script)] + sys.argv[2:]
        sys.exit(subprocess.call(cmd))
    else:
        err(f"scripts/pxos-telemetry-monitor.py not found at {script}.")
        sys.exit(1)


def cmd_invariant(args):
    """Run the invariant evolution and audit utility."""
    script = get_resource_path("scripts/pxos-invariant.py")
    if script.exists():
        cmd = [sys.executable, str(script)] + sys.argv[2:]
        sys.exit(subprocess.call(cmd))
    else:
        err(f"scripts/pxos-invariant.py not found at {script}.")
        sys.exit(1)


def cmd_doctor(args):
    """Run repository health check and diagnostic suite."""
    log("Running PXOS Diagnostic Suite & Repository Health Audit...")
    all_ok = True

    # 1. Invariant Integrity
    inv_script = get_resource_path("scripts/pxos-invariant.py")
    if inv_script.exists():
        code = subprocess.call([sys.executable, str(inv_script), "--check"])
        if code != 0:
            all_ok = False
    else:
        warn("scripts/pxos-invariant.py not found.")

    # 2. Package Parity (if running inside repo)
    sync_script = get_resource_path("scripts/sync-package-data.py")
    if sync_script.exists():
        code = subprocess.call([sys.executable, str(sync_script), "--check"])
        if code != 0:
            all_ok = False

    # 3. AI Crawlability (if running inside repo)
    llms_script = get_resource_path("scripts/generate-llms-txt.py")
    if llms_script.exists():
        code = subprocess.call([sys.executable, str(llms_script), "--check"])
        if code != 0:
            all_ok = False

    if all_ok:
        ok("All system integrity and governance checks passed.")
    else:
        err("One or more diagnostic checks failed. Review output above.")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        prog="pxos",
        description=f"PXOS — The AI Operating System for Product & Software Engineering (v{VERSION})",
    )
    parser.add_argument("--version", "-v", action="version", version=f"PXOS v{VERSION}")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # init
    p_init = subparsers.add_parser("init", help="Initialize PXOS in the current workspace")
    p_init.add_argument("--full", action="store_true", help="Install optional planning files (ROADMAP.md, SPRINT.md)")
    p_init.add_argument("--evidence", action="store_true", help="Install scientific evidence-first research addon")
    p_init.add_argument("--maestri", action="store_true", help="Install Maestri spatial canvas and multi-agent swarm addon")
    p_init.add_argument("--ide", type=str, choices=["cursor", "windsurf", "claude", "gemini", "copilot"], help="Configure IDE rules")
    p_init.add_argument("--global", dest="global_mode", action="store_true", help="Install IDE rules globally to home directory")
    p_init.set_defaults(func=cmd_init)

    # add (addons)
    p_add = subparsers.add_parser("add", help="Install modular addons into the workspace")
    p_add.add_argument("addon", choices=list(ADDONS.keys()), help="Name of addon to install (e.g. evidence)")
    p_add.add_argument("--force", action="store_true", help="Overwrite existing files if already present")
    p_add.add_argument("--ide", type=str, choices=["cursor", "windsurf", "claude", "gemini", "copilot"], help="Configure IDE rules for addon")
    p_add.add_argument("--global", dest="global_mode", action="store_true", help="Install IDE rules globally to home directory")
    p_add.set_defaults(func=cmd_add)

    # update
    p_update = subparsers.add_parser("update", help="Update operating rules to latest version without losing project context")
    p_update.add_argument("--ide", type=str, choices=["cursor", "windsurf", "claude", "gemini", "copilot"], help="Re-sync IDE rules")
    p_update.add_argument("--global", dest="global_mode", action="store_true", help="Update IDE rules globally")
    p_update.set_defaults(func=cmd_update)

    # benchmark
    p_bench = subparsers.add_parser("benchmark", help="Dispatch empirical telemetry benchmarks")
    p_bench.set_defaults(func=cmd_benchmark)

    # monitor
    p_mon = subparsers.add_parser("monitor", help="Monitor public telemetry ingestion daemon")
    p_mon.set_defaults(func=cmd_monitor)

    # invariant
    p_inv = subparsers.add_parser("invariant", help="Audit and evolve project invariants")
    p_inv.set_defaults(func=cmd_invariant)

    # doctor
    p_doc = subparsers.add_parser("doctor", help="Run comprehensive repository health check")
    p_doc.set_defaults(func=cmd_doctor)

    args, unknown = parser.parse_known_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)

    args.func(args)


if __name__ == "__main__":
    main()
