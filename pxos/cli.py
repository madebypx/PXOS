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

VERSION = "2.4.0"
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
    """Finds a template or script from package data, falling back to repository root."""
    pkg_res = Path(__file__).resolve().parent / relative_path
    if pkg_res.exists():
        return pkg_res
    repo_res = Path(__file__).resolve().parent.parent / relative_path
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


def append_pxos_block(dest_path: Path, content: str):
    """Append or replace a managed PXOS block inside an existing markdown file."""
    start_marker = "<!-- pxos:start -->"
    end_marker = "<!-- pxos:end -->"
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    if dest_path.exists():
        text = dest_path.read_text(encoding="utf-8")
        if start_marker in text:
            pattern = re.compile(rf"{re.escape(start_marker)}.*?{re.escape(end_marker)}", re.DOTALL)
            replacement = f"{start_marker}\n{content}\n{end_marker}"
            new_text = pattern.sub(replacement, text)
            dest_path.write_text(new_text, encoding="utf-8")
            ok(f"Updated PXOS rules block in {dest_path}")
            return
        appended = f"{text}\n\n---\n\n{start_marker}\n{content}\n{end_marker}\n"
        dest_path.write_text(appended, encoding="utf-8")
        ok(f"Appended PXOS rules to {dest_path}")
    else:
        initial = f"{start_marker}\n{content}\n{end_marker}\n"
        dest_path.write_text(initial, encoding="utf-8")
        ok(f"Created {dest_path}")


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

    ide = args.ide
    if not ide:
        if Path(".cursor").exists():
            ide = "cursor"
        elif Path(".windsurf").exists():
            ide = "windsurf"
        elif Path("CLAUDE.md").exists():
            ide = "claude"
        elif Path("GEMINI.md").exists():
            ide = "gemini"
        elif Path(".github/copilot-instructions.md").exists():
            ide = "copilot"

    if ide:
        configure_ide_rules(ide, global_mode=args.global_mode)

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
    p_init.add_argument("--ide", type=str, choices=["cursor", "windsurf", "claude", "gemini", "copilot"], help="Configure IDE rules")
    p_init.add_argument("--global", dest="global_mode", action="store_true", help="Install IDE rules globally to home directory")
    p_init.set_defaults(func=cmd_init)

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

    args, unknown = parser.parse_known_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)

    args.func(args)


if __name__ == "__main__":
    main()
