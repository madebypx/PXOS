#!/usr/bin/env python3
"""PXOS llms.txt and llms-full.txt Generator & Validator.

Complies with the llmstxt.org standard to ensure seamless ingestion by
modern AI models, web crawlers, and LLM-assisted developer tools.

Usage:
    python scripts/generate-llms-txt.py          # Generate/update llms.txt & llms-full.txt
    python scripts/generate-llms-txt.py --check  # Verify up-to-date and validate format
"""

import argparse
import os
import re
import sys
from pathlib import Path

VERSION = "2.3.0"
REPO_ROOT = Path(__file__).resolve().parent.parent

# Core documentation files included in llms-full.txt in curated reading order
SOURCE_DOCS = [
    ("Executive & Core Architecture", "README.md"),
    ("Universal Operating Rules", ".ai/AI_BASE.md"),
    ("Workflows & Slash Commands", "WORKFLOWS.md"),
    ("Empirical Benchmark Report", "benchmarks/REPORT.md"),
    ("Benchmark Methodology & Formulas", "benchmarks/METHODOLOGY.md"),
]

LLMS_TXT_TEMPLATE = f"""# PXOS
> The minimal, document-driven operating system and governance layer for AI-assisted software engineering.

PXOS standardizes the operational contract between human developers and AI coding agents. It replaces chaotic conversational chat loops with a disciplined 6-phase lifecycle (Discover -> Plan -> Execute -> Validate -> Review -> Compact), multi-agent isolation via Git worktrees, zero-spoiler specifications, and empirical telemetry benchmarking.

- **Version**: {VERSION}
- **Company / Organization**: PROJECT/X (https://madebypx.com)
- **Website**: https://pxos.madebypx.com
- **Repository**: https://github.com/madebypx/PXOS
- **License**: MIT
- **Primary Paradigms**: Document-Driven Development, Context Economy, Git Worktree Multi-Agent Isolation, Nielsen UX Heuristics inside.

## Core Documentation

- [README.md](README.md): Complete framework overview, empirical benchmarks, and 6-phase lifecycle.
- [.ai/AI_BASE.md](.ai/AI_BASE.md): Universal operational rules, autonomy boundaries, and multi-agent etiquette.
- [WORKFLOWS.md](WORKFLOWS.md): Full directory of 12 slash commands (/start, /spec, /plan, /review, /compact, /benchmark, /audit, etc.).
- [benchmarks/REPORT.md](benchmarks/REPORT.md): Empirical laboratory findings demonstrating 80% token waste reduction and 1.4% rework ratio.
- [benchmarks/METHODOLOGY.md](benchmarks/METHODOLOGY.md): Statistical research methodology, complexity tiers, and cost formulas.

## Optional & Developer Resources

- [install.sh](install.sh): Zero-dependency POSIX installation script for macOS/Linux.
- [install.ps1](install.ps1): Zero-dependency native PowerShell installer for Windows.
- [CHANGELOG.md](CHANGELOG.md): Historical releases and semantic version history.
- [llms-full.txt](llms-full.txt): Dense, aggregated single-file complete reference for LLM context windows.
"""


def clean_markdown_for_llm(content: str) -> str:
    """Strip unnecessary HTML badges, comments, and non-semantic noise."""
    # Remove HTML comments like <!-- pxos:version ... -->
    content = re.sub(r"<!--.*?-->", "", content, flags=re.DOTALL)
    # Remove SVG badge blocks at top of README
    content = re.sub(r"\[!\[.*?\]\(.*?\)\]\(.*?\)\s*", "", content)
    # Collapse 3+ newlines to 2
    content = re.sub(r"\n{3,}", "\n\n", content)
    return content.strip()


def build_llms_full_txt() -> str:
    """Build a consolidated single-file context document."""
    sections = [
        f"# PXOS Complete LLM Reference (v{VERSION})",
        "> Aggregated documentation for direct AI context injection, indexing, and RAG pipelines.",
        f"Generated automatically from repository sources (https://github.com/madebypx/PXOS).\n",
        "---",
    ]

    for title, rel_path in SOURCE_DOCS:
        file_path = REPO_ROOT / rel_path
        if not file_path.exists():
            print(f"Error: Source file {rel_path} does not exist.", file=sys.stderr)
            sys.exit(1)

        raw_content = file_path.read_text(encoding="utf-8")
        cleaned = clean_markdown_for_llm(raw_content)

        sections.append(f"\n\n## DOCUMENT: {rel_path} ({title})\n")
        sections.append(cleaned)
        sections.append("\n\n" + ("=" * 80) + "\n")

    return "\n".join(sections)


def validate_llms_txt(content: str) -> bool:
    """Verify llms.txt follows the specification guidelines."""
    if not content.startswith("# "):
        print("Validation Error: llms.txt must start with '# <ProjectName>'", file=sys.stderr)
        return False
    if "\n> " not in content:
        print("Validation Error: llms.txt must include a blockquote summary '> ...'", file=sys.stderr)
        return False
    if "## " not in content:
        print("Validation Error: llms.txt must include at least one markdown section ('## ...')", file=sys.stderr)
        return False
    return True


def main():
    parser = argparse.ArgumentParser(description="Generate or validate PXOS llms.txt and llms-full.txt")
    parser.add_argument("--check", action="store_true", help="Check that files are current and valid without modifying them")
    args = parser.parse_args()

    llms_txt_path = REPO_ROOT / "llms.txt"
    llms_full_path = REPO_ROOT / "llms-full.txt"

    expected_llms_txt = LLMS_TXT_TEMPLATE.strip() + "\n"
    expected_llms_full = build_llms_full_txt().strip() + "\n"

    if args.check:
        errors = False
        if not llms_txt_path.exists() or llms_txt_path.read_text(encoding="utf-8") != expected_llms_txt:
            print("Check Failed: llms.txt is missing or out of sync.", file=sys.stderr)
            errors = True
        elif not validate_llms_txt(expected_llms_txt):
            errors = True

        if not llms_full_path.exists() or llms_full_path.read_text(encoding="utf-8") != expected_llms_full:
            print("Check Failed: llms-full.txt is missing or out of sync.", file=sys.stderr)
            errors = True

        if errors:
            sys.exit(1)
        print("[OK] llms.txt and llms-full.txt are valid and up to date.")
        sys.exit(0)

    # Write files
    llms_txt_path.write_text(expected_llms_txt, encoding="utf-8")
    print(f"[CREATED/UPDATED] {llms_txt_path}")

    llms_full_path.write_text(expected_llms_full, encoding="utf-8")
    print(f"[CREATED/UPDATED] {llms_full_path} ({len(expected_llms_full)} bytes)")

    if validate_llms_txt(expected_llms_txt):
        print("[OK] Validation passed against llmstxt.org standard.")


if __name__ == "__main__":
    main()
