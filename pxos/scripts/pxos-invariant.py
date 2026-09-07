#!/usr/bin/env python3
"""PXOS Invariant Evolution & Cognitive Post-Mortem Engine.

Zero-dependency utility for auditing, validating, diagnosing, and evolving
critical project invariants (INV-xxx) in `.ai/PROJECT_CONTEXT.md`.

Usage:
    python scripts/pxos-invariant.py --check
    python scripts/pxos-invariant.py --list
    python scripts/pxos-invariant.py --next-id
    python scripts/pxos-invariant.py --suggest --reason "<failure_reason>"
    python scripts/pxos-invariant.py --add --title "<Title>" --rule "<Imperative rule>"
"""

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONTEXT_FILE = REPO_ROOT / ".ai" / "PROJECT_CONTEXT.md"

# Regular expression to match standard PXOS invariant entries:
# e.g.: - **INV-001 (Title):** Rule description...
INVARIANT_PATTERN = re.compile(
    r"^\s*-\s*\*\*([A-Z]+-(\d{3,4}))\s*\(([^)]+)\):\*\*\s*(.+)$",
    re.MULTILINE,
)

STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "if", "then", "else", "when",
    "at", "by", "for", "with", "about", "against", "between", "into",
    "through", "during", "before", "after", "above", "below", "to", "from",
    "up", "down", "in", "out", "on", "off", "over", "under", "again", "is",
    "are", "was", "were", "be", "been", "being", "have", "has", "had", "do",
    "does", "did", "must", "never", "always", "should", "not", "no", "this",
    "that", "these", "those", "it", "its", "all", "any", "both", "each"
}


@dataclass
class Invariant:
    id: str
    number: int
    title: str
    rule: str
    raw_line: str


@dataclass
class ValidationResult:
    is_valid: bool
    invariants: List[Invariant]
    errors: List[str]
    warnings: List[str]


def parse_invariants(content: str) -> List[Invariant]:
    """Extracts all declared invariants from markdown content."""
    invariants = []
    for match in INVARIANT_PATTERN.finditer(content):
        full_id = match.group(1).strip()
        number = int(match.group(2))
        title = match.group(3).strip()
        rule = match.group(4).strip()
        raw_line = match.group(0).strip()
        invariants.append(
            Invariant(
                id=full_id,
                number=number,
                title=title,
                rule=rule,
                raw_line=raw_line,
            )
        )
    return invariants


def validate_invariants(context_path: Path) -> ValidationResult:
    """Validates sequential numbering, syntax, and integrity of critical invariants."""
    errors = []
    warnings = []

    if not context_path.exists():
        return ValidationResult(
            is_valid=False,
            invariants=[],
            errors=[f"File does not exist: {context_path}"],
            warnings=[],
        )

    content = context_path.read_text(encoding="utf-8")
    invariants = parse_invariants(content)

    if not invariants:
        errors.append(f"No invariants matching pattern found in {context_path.name}")
        return ValidationResult(
            is_valid=False, invariants=[], errors=errors, warnings=warnings
        )

    # 1. Monotonic sequential numbering check
    expected_num = 1
    seen_ids = set()
    for inv in invariants:
        if inv.id in seen_ids:
            errors.append(f"Duplicate invariant ID: {inv.id}")
        seen_ids.add(inv.id)

        if inv.number != expected_num:
            errors.append(
                f"Non-sequential invariant numbering: expected INV-{expected_num:03d}, got {inv.id}"
            )
        expected_num = inv.number + 1

        # 2. Minimum length check
        if len(inv.rule) < 15:
            errors.append(f"Invariant {inv.id} rule is too brief or incomplete: '{inv.rule}'")

        # 3. Warning on non-imperative tone
        lower_rule = inv.rule.lower()
        if not any(token in lower_rule for token in ["must", "never", "always", "strictly", "only"]):
            warnings.append(
                f"Invariant {inv.id} ('{inv.title}') lacks explicit imperative constraint keyword (must/never/always)."
            )

    return ValidationResult(
        is_valid=len(errors) == 0,
        invariants=invariants,
        errors=errors,
        warnings=warnings,
    )


def get_next_invariant_id(context_path: Path) -> str:
    """Returns the next available sequential invariant ID (e.g. 'INV-006')."""
    if not context_path.exists():
        return "INV-001"
    content = context_path.read_text(encoding="utf-8")
    invariants = parse_invariants(content)
    if not invariants:
        return "INV-001"
    highest = max(inv.number for inv in invariants)
    return f"INV-{highest + 1:03d}"


def calculate_jaccard_similarity(text_a: str, text_b: str) -> float:
    """Computes keyword Jaccard similarity between two rule texts."""
    words_a = {
        w.lower()
        for w in re.findall(r"\b[a-zA-Z0-9_-]{3,}\b", text_a)
        if w.lower() not in STOPWORDS
    }
    words_b = {
        w.lower()
        for w in re.findall(r"\b[a-zA-Z0-9_-]{3,}\b", text_b)
        if w.lower() not in STOPWORDS
    }
    if not words_a or not words_b:
        return 0.0
    intersection = words_a.intersection(words_b)
    union = words_a.union(words_b)
    return len(intersection) / len(union)


def find_similar_invariants(
    rule: str, existing_invariants: List[Invariant], threshold: float = 0.55
) -> List[Tuple[Invariant, float]]:
    """Identifies existing invariants with high semantic or keyword overlap."""
    similar = []
    for inv in existing_invariants:
        combined_text = f"{inv.title} {inv.rule}"
        sim = calculate_jaccard_similarity(rule, combined_text)
        if sim >= threshold:
            similar.append((inv, sim))
    return sorted(similar, key=lambda x: x[1], reverse=True)


def inject_invariant(
    context_path: Path, title: str, rule: str, check_duplicates: bool = True
) -> Tuple[bool, str]:
    """Safely and idempotently appends a new invariant to ## Critical invariants."""
    if not context_path.exists():
        return False, f"File not found: {context_path}"

    content = context_path.read_text(encoding="utf-8")
    existing_invariants = parse_invariants(content)

    # Check for duplicates or high similarity
    if check_duplicates:
        for inv in existing_invariants:
            if inv.title.strip().lower() == title.strip().lower():
                return False, f"Invariant with title '{title}' already exists as {inv.id}."

        similar = find_similar_invariants(rule, existing_invariants)
        if similar:
            match, sim = similar[0]
            if sim > 0.70:
                return (
                    False,
                    f"Candidate rule too similar to {match.id} ('{match.title}', {sim:.0%} overlap).",
                )

    next_id = get_next_invariant_id(context_path)
    formatted_entry = f"- **{next_id} ({title}):** {rule}"

    # Locate insertion point inside ## Critical invariants
    invariants_header = re.search(r"##\s+Critical\s+invariants", content, re.IGNORECASE)
    if not invariants_header:
        # If section doesn't exist, append to end of file
        new_content = (
            content.rstrip()
            + "\n\n---\n\n## Critical invariants\n\n"
            + "Hard constraints that must never be violated by any agent. Use short IDs for traceability.\n\n"
            + formatted_entry
            + "\n"
        )
    else:
        # Find the last invariant entry in the file
        matches = list(INVARIANT_PATTERN.finditer(content))
        if matches:
            last_match = matches[-1]
            insert_pos = last_match.end()
            new_content = (
                content[:insert_pos] + "\n" + formatted_entry + content[insert_pos:]
            )
        else:
            # Header exists but no list items yet
            insert_pos = invariants_header.end()
            new_content = (
                content[:insert_pos] + "\n\n" + formatted_entry + "\n" + content[insert_pos:]
            )

    context_path.write_text(new_content, encoding="utf-8")
    return True, f"Successfully appended {next_id} ({title}) to {context_path.name}."


def diagnose_failure_mode(
    reason: str, diff_text: str = "", commit_msgs: Optional[List[str]] = None
) -> Dict[str, str]:
    """Diagnoses failure pattern from cognitive post-mortem analysis and suggests an atomic rule."""
    combined = f"{reason} {diff_text} {' '.join(commit_msgs or [])}".lower()

    if any(k in combined for k in ["constant", "threshold", "hardcode", "magic number", "days", "status", "timeout", "cooldown"]):
        category = "ASSUMED_CONSTANT"
        suggested_title = "Canonical Domain Constants"
        suggested_rule = "Never invent or assume business constants, cooldowns, or thresholds without reading their canonical definitions in domain rules."
    elif any(k in combined for k in ["sync", "distributed", "multi-node", "database", "desktop", "supabase", "localstorage", "watcher", "cache"]):
        category = "MULTI_NODE_BLINDNESS"
        suggested_title = "Distributed Mutation Lifecycle"
        suggested_rule = "Always trace data mutations across all persistence nodes (local cache, remote database, background sync watchers) before completing updates or deletions."
    elif any(k in combined for k in ["empty", "loading", "error", "premature", "build passed", "100%", "incomplete"]):
        category = "PREMATURE_COMPLETION"
        suggested_title = "Universal State Completeness"
        suggested_rule = "Never declare a frontend feature complete based solely on compilation success without validating empty, loading, error, and destructive action states."
    else:
        category = "GENERAL_COGNITIVE_DRIFT"
        suggested_title = "Domain Invariant Guard"
        suggested_rule = f"Strictly enforce verified constraints on touched subsystem: {reason.strip()}."

    return {
        "category": category,
        "suggested_title": suggested_title,
        "suggested_rule": suggested_rule,
    }


def main():
    parser = argparse.ArgumentParser(
        description="PXOS Invariant Evolution & Cognitive Post-Mortem Engine"
    )
    parser.add_argument(
        "--context-file",
        type=Path,
        default=DEFAULT_CONTEXT_FILE,
        help="Path to PROJECT_CONTEXT.md (default: .ai/PROJECT_CONTEXT.md)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate sequential numbering and formatting of active invariants",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all active critical invariants in structured format",
    )
    parser.add_argument(
        "--next-id",
        action="store_true",
        help="Print next sequential invariant ID",
    )
    parser.add_argument(
        "--suggest",
        action="store_true",
        help="Diagnose failure mode and suggest a candidate invariant",
    )
    parser.add_argument(
        "--reason",
        type=str,
        default="",
        help="Failure description or rework context for --suggest",
    )
    parser.add_argument(
        "--add",
        action="store_true",
        help="Safely append a new invariant to the context file",
    )
    parser.add_argument(
        "--title",
        type=str,
        default="",
        help="Title for the invariant (used with --add)",
    )
    parser.add_argument(
        "--rule",
        type=str,
        default="",
        help="Imperative constraint statement for the invariant (used with --add)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Bypass similarity overlap checks on --add",
    )

    args = parser.parse_args()

    if args.check:
        res = validate_invariants(args.context_file)
        if res.is_valid:
            print(f"[OK] Invariant integrity verified in {args.context_file.name} ({len(res.invariants)} active invariants).")
            if res.warnings:
                for w in res.warnings:
                    print(f"  [WARN] {w}")
            sys.exit(0)
        else:
            print(f"[FAIL] Invariant validation failed in {args.context_file.name}:", file=sys.stderr)
            for err in res.errors:
                print(f"  - {err}", file=sys.stderr)
            sys.exit(1)

    elif args.list:
        res = validate_invariants(args.context_file)
        if not res.invariants:
            print(f"No invariants declared in {args.context_file.name}.")
            sys.exit(0)
        print(f"\nActive Critical Invariants ({args.context_file.name}):\n" + "=" * 60)
        for inv in res.invariants:
            print(f"{inv.id:<10} | {inv.title:<35}\n           {inv.rule}\n")
        sys.exit(0)

    elif args.next_id:
        print(get_next_invariant_id(args.context_file))
        sys.exit(0)

    elif args.suggest:
        diagnosis = diagnose_failure_mode(args.reason)
        next_id = get_next_invariant_id(args.context_file)
        print("\n--- Cognitive Post-Mortem Diagnosis ---")
        print(f"Classified Failure Mode : {diagnosis['category']}")
        print(f"Proposed Invariant ID   : {next_id}")
        print(f"Proposed Title          : {diagnosis['suggested_title']}")
        print(f"Proposed Rule           :\n  - **{next_id} ({diagnosis['suggested_title']}):** {diagnosis['suggested_rule']}\n")
        print("To inject this invariant with confirmation, run:")
        print(f'  pxos invariant add "{diagnosis["suggested_title"]}" "{diagnosis["suggested_rule"]}"\n')
        sys.exit(0)

    elif args.add:
        if not args.title or not args.rule:
            print("Error: Both --title and --rule are required when using --add.", file=sys.stderr)
            sys.exit(1)
        ok, msg = inject_invariant(
            args.context_file,
            title=args.title,
            rule=args.rule,
            check_duplicates=not args.force,
        )
        if ok:
            print(f"[OK] {msg}")
            sys.exit(0)
        else:
            print(f"[REJECTED] {msg}", file=sys.stderr)
            sys.exit(1)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
