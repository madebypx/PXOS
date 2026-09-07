#!/usr/bin/env python3
"""PXOS Package Data Synchronization & Parity Validator.

Ensures that bundled package data in `pxos/templates/` and `pxos/scripts/`
remain identical to the canonical repository sources in `templates/` and `scripts/`.
Prevents distribution drift in PyPI wheel builds.

Usage:
    python scripts/sync-package-data.py          # Synchronize package data with root sources
    python scripts/sync-package-data.py --check  # Verify strict parity without modifying files
"""

import argparse
import os
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

SYNC_PAIRS = [
    (REPO_ROOT / "templates", REPO_ROOT / "pxos" / "templates"),
    (REPO_ROOT / "scripts", REPO_ROOT / "pxos" / "scripts"),
]

IGNORED_NAMES = {"__pycache__", ".DS_Store", "Thumbs.db"}
IGNORED_EXTENSIONS = {".pyc", ".pyo"}


def should_ignore(path: Path) -> bool:
    if any(part in IGNORED_NAMES for part in path.parts):
        return True
    if path.suffix in IGNORED_EXTENSIONS:
        return True
    return False


def normalize_content(data: bytes) -> bytes:
    """Normalize line endings (CRLF -> LF) for cross-platform comparison."""
    return data.replace(b"\r\n", b"\n")


def check_parity() -> bool:
    """Check if all files in source directories match target directories."""
    all_synced = True

    for src_dir, dst_dir in SYNC_PAIRS:
        if not src_dir.exists():
            print(f"Error: Source directory {src_dir} does not exist.", file=sys.stderr)
            return False

        for root, _, files in os.walk(src_dir):
            for file in files:
                src_file = Path(root) / file
                if should_ignore(src_file):
                    continue

                rel_path = src_file.relative_to(src_dir)
                dst_file = dst_dir / rel_path

                if not dst_file.exists():
                    print(f"[DRIFT] Missing in package data: {dst_file.relative_to(REPO_ROOT)}", file=sys.stderr)
                    all_synced = False
                    continue

                src_bytes = normalize_content(src_file.read_bytes())
                dst_bytes = normalize_content(dst_file.read_bytes())

                if src_bytes != dst_bytes:
                    print(f"[DRIFT] Content mismatch: {dst_file.relative_to(REPO_ROOT)}", file=sys.stderr)
                    all_synced = False

    return all_synced


def sync_data():
    """Copy all non-ignored files from source directories to package data directories."""
    for src_dir, dst_dir in SYNC_PAIRS:
        if not src_dir.exists():
            print(f"Error: Source directory {src_dir} does not exist.", file=sys.stderr)
            sys.exit(1)

        for root, _, files in os.walk(src_dir):
            for file in files:
                src_file = Path(root) / file
                if should_ignore(src_file):
                    continue

                rel_path = src_file.relative_to(src_dir)
                dst_file = dst_dir / rel_path

                dst_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_file, dst_file)
                print(f"[SYNCED] {dst_file.relative_to(REPO_ROOT)}")


def main():
    parser = argparse.ArgumentParser(description="Synchronize or verify PXOS package data parity")
    parser.add_argument("--check", action="store_true", help="Check parity without writing files")
    args = parser.parse_args()

    if args.check:
        if check_parity():
            print("[OK] Package data is fully synchronized with repository root.")
            sys.exit(0)
        else:
            print("[FAIL] Package data is out of sync. Run 'python scripts/sync-package-data.py' to fix.", file=sys.stderr)
            sys.exit(1)

    sync_data()
    print("[OK] All package data synchronized successfully.")


if __name__ == "__main__":
    main()
