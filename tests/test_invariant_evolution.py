#!/usr/bin/env python3
"""Tests for PXOS Closed-Loop Invariant Evolution & Cognitive Post-Mortem Engine.

Validates parsing, sequential numbering, similarity overlap detection,
safe markdown injection, failure mode diagnosis, and CLI interfaces.
"""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

# Add scripts directory to sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import importlib.util

spec = importlib.util.spec_from_file_location(
    "pxos_invariant", REPO_ROOT / "scripts" / "pxos-invariant.py"
)
pxos_invariant = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pxos_invariant)


SAMPLE_VALID_CONTEXT = """# Project Context
<!-- pxos:version 2.5.0 -->

## Critical invariants

Hard constraints that must never be violated by any agent.

- **INV-001 (Privacy Invariant):** The system must never transmit unconsented user data or plaintext secrets.
- **INV-002 (Quarantine Isolation):** All internal files must remain strictly quarantined in `.internal/`.
- **INV-003 (Zero Dependencies):** Tools must rely exclusively on Python standard library without third-party dependencies.
"""

SAMPLE_GAP_CONTEXT = """# Project Context
## Critical invariants
- **INV-001 (First Rule):** Must always validate inputs before executing actions.
- **INV-003 (Third Rule):** Must never bypass authorization checks.
"""

SAMPLE_DUPLICATE_CONTEXT = """# Project Context
## Critical invariants
- **INV-001 (First Rule):** Must always validate inputs.
- **INV-001 (Duplicate Rule):** Must always validate inputs twice.
"""


class TestInvariantEvolution(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.context_file = self.temp_dir / "PROJECT_CONTEXT.md"
        self.context_file.write_text(SAMPLE_VALID_CONTEXT, encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_parse_invariants(self):
        invariants = pxos_invariant.parse_invariants(SAMPLE_VALID_CONTEXT)
        self.assertEqual(len(invariants), 3)
        self.assertEqual(invariants[0].id, "INV-001")
        self.assertEqual(invariants[0].number, 1)
        self.assertEqual(invariants[0].title, "Privacy Invariant")
        self.assertIn("must never transmit", invariants[0].rule)
        self.assertEqual(invariants[1].id, "INV-002")
        self.assertEqual(invariants[2].id, "INV-003")

    def test_validate_real_repo_invariants(self):
        real_context = REPO_ROOT / ".ai" / "PROJECT_CONTEXT.md"
        res = pxos_invariant.validate_invariants(real_context)
        self.assertTrue(res.is_valid, f"Real repo invariants invalid: {res.errors}")
        self.assertGreaterEqual(len(res.invariants), 5)
        self.assertEqual(res.invariants[0].id, "INV-001")
        self.assertEqual(res.invariants[4].id, "INV-005")

    def test_validate_invariants_detects_gap(self):
        gap_file = self.temp_dir / "GAP_CONTEXT.md"
        gap_file.write_text(SAMPLE_GAP_CONTEXT, encoding="utf-8")
        res = pxos_invariant.validate_invariants(gap_file)
        self.assertFalse(res.is_valid)
        self.assertTrue(any("Non-sequential" in err for err in res.errors))

    def test_validate_invariants_detects_duplicate_id(self):
        dup_file = self.temp_dir / "DUP_CONTEXT.md"
        dup_file.write_text(SAMPLE_DUPLICATE_CONTEXT, encoding="utf-8")
        res = pxos_invariant.validate_invariants(dup_file)
        self.assertFalse(res.is_valid)
        self.assertTrue(any("Duplicate" in err for err in res.errors))

    def test_get_next_invariant_id(self):
        next_id = pxos_invariant.get_next_invariant_id(self.context_file)
        self.assertEqual(next_id, "INV-004")

        real_context = REPO_ROOT / ".ai" / "PROJECT_CONTEXT.md"
        real_next = pxos_invariant.get_next_invariant_id(real_context)
        self.assertEqual(real_next, "INV-006")

    def test_inject_invariant_success(self):
        ok, msg = pxos_invariant.inject_invariant(
            self.context_file,
            title="English Conventional Commits",
            rule="All git commit messages must be written in English.",
            check_duplicates=True,
        )
        self.assertTrue(ok)
        self.assertIn("Successfully appended INV-004", msg)

        # Validate file after injection
        res = pxos_invariant.validate_invariants(self.context_file)
        self.assertTrue(res.is_valid)
        self.assertEqual(len(res.invariants), 4)
        self.assertEqual(res.invariants[-1].id, "INV-004")
        self.assertEqual(res.invariants[-1].title, "English Conventional Commits")

    def test_inject_invariant_duplicate_rejection(self):
        # Reject identical title
        ok, msg = pxos_invariant.inject_invariant(
            self.context_file,
            title="Privacy Invariant",
            rule="Something different about privacy.",
            check_duplicates=True,
        )
        self.assertFalse(ok)
        self.assertIn("already exists", msg)

        # Reject high overlap
        ok, msg = pxos_invariant.inject_invariant(
            self.context_file,
            title="Different Title",
            rule="The system must never transmit unconsented user data or plaintext secrets.",
            check_duplicates=True,
        )
        self.assertFalse(ok)
        self.assertIn("too similar", msg)

    def test_diagnose_failure_mode(self):
        d1 = pxos_invariant.diagnose_failure_mode("invented cooldown days threshold 35d")
        self.assertEqual(d1["category"], "ASSUMED_CONSTANT")
        self.assertEqual(d1["suggested_title"], "Canonical Domain Constants")

        d2 = pxos_invariant.diagnose_failure_mode("supabase updated but desktop watcher was not notified")
        self.assertEqual(d2["category"], "MULTI_NODE_BLINDNESS")
        self.assertEqual(d2["suggested_title"], "Distributed Mutation Lifecycle")

        d3 = pxos_invariant.diagnose_failure_mode("build passed but empty data screen was broken")
        self.assertEqual(d3["category"], "PREMATURE_COMPLETION")
        self.assertEqual(d3["suggested_title"], "Universal State Completeness")

    def test_cli_subcommands(self):
        script = REPO_ROOT / "scripts" / "pxos-invariant.py"

        # 1. Check
        res_check = subprocess.run(
            [sys.executable, str(script), "--check"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(res_check.returncode, 0)
        self.assertIn("[OK]", res_check.stdout)

        # 2. List
        res_list = subprocess.run(
            [sys.executable, str(script), "--list"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(res_list.returncode, 0)
        self.assertIn("INV-001", res_list.stdout)
        self.assertIn("INV-005", res_list.stdout)

        # 3. Next ID
        res_next = subprocess.run(
            [sys.executable, str(script), "--next-id"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(res_next.returncode, 0)
        self.assertEqual(res_next.stdout.strip(), "INV-006")

        # 4. Suggest
        res_sug = subprocess.run(
            [sys.executable, str(script), "--suggest", "--reason", "cooldown threshold assumed"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(res_sug.returncode, 0)
        self.assertIn("ASSUMED_CONSTANT", res_sug.stdout)


if __name__ == "__main__":
    unittest.main()
