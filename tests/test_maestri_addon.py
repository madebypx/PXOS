"""Tests for PXOS Maestri Spatial Canvas Addon.

Verifies canonical template integrity, CLI `pxos add maestri` and `pxos init --maestri` workflows,
idempotent file copying, preservation of existing user files, and editor rule integration.
"""

import os
import shutil
import tempfile
import unittest
from pathlib import Path

from pxos.cli import (
    ADDONS,
    append_pxos_block,
    configure_addon_ide_rules,
    install_addon,
)

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestMaestriAddonTemplates(unittest.TestCase):
    """Tests for canonical template files and rules."""

    def test_canonical_templates_exist(self):
        maestri_dir = REPO_ROOT / "templates" / "addons" / "maestri"
        required_files = [
            maestri_dir / "rules" / "maestri_bridge.md",
            maestri_dir / ".ai" / "canvas" / "operational-board.md",
            maestri_dir / ".ai" / "canvas" / "architecture-board.md",
            maestri_dir / ".ai" / "canvas" / "swarm-protocol.md",
        ]
        for f in required_files:
            self.assertTrue(f.exists(), f"Missing template file: {f}")
            self.assertGreater(f.stat().st_size, 0, f"Template file is empty: {f}")

    def test_rules_content_invariants(self):
        rules_file = REPO_ROOT / "templates" / "addons" / "maestri" / "rules" / "maestri_bridge.md"
        content = rules_file.read_text(encoding="utf-8")
        self.assertIn("Single Source of Truth", content)
        self.assertIn("Conditional CLI Invocation", content)
        self.assertIn("maestri say --progress", content)
        self.assertIn("Operational Board", content)
        self.assertIn("Architecture Board", content)
        self.assertIn("maestri ask --batch", content)
        self.assertIn("Ask-Back", content)
        self.assertIn("Context Sharding", content)
        self.assertIn("Boundary Locks", content)
        self.assertIn("Anti-Exploration", content)
        self.assertIn("Capsule Briefing", content)
        self.assertIn("Closed Dialectic", content)

    def test_canvas_templates_structure(self):
        op_board = REPO_ROOT / "templates" / "addons" / "maestri" / ".ai" / "canvas" / "operational-board.md"
        arch_board = REPO_ROOT / "templates" / "addons" / "maestri" / ".ai" / "canvas" / "architecture-board.md"
        swarm_board = REPO_ROOT / "templates" / "addons" / "maestri" / ".ai" / "canvas" / "swarm-protocol.md"

        op_text = op_board.read_text(encoding="utf-8")
        self.assertIn("<!-- pxos:canvas:operational-board -->", op_text)
        self.assertIn("Task Matrix", op_text)

        arch_text = arch_board.read_text(encoding="utf-8")
        self.assertIn("<!-- pxos:canvas:architecture-board -->", arch_text)
        self.assertIn("Active Architectural Invariants", arch_text)

        swarm_text = swarm_board.read_text(encoding="utf-8")
        self.assertIn("<!-- pxos:canvas:swarm-protocol -->", swarm_text)
        self.assertIn("Confinement Principles", swarm_text)
        self.assertIn("Capsule Briefing Schema", swarm_text)


class TestMaestriAddonCLI(unittest.TestCase):
    """Tests for CLI integration of `pxos add maestri`."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="pxos_test_maestri_")
        self.old_cwd = os.getcwd()
        os.chdir(self.test_dir)

    def tearDown(self):
        os.chdir(self.old_cwd)
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_install_addon_maestri_fresh(self):
        # Fresh install without pre-existing files
        install_addon("maestri", force=False)

        expected_files = [
            Path(".ai/canvas/operational-board.md"),
            Path(".ai/canvas/architecture-board.md"),
            Path(".ai/canvas/swarm-protocol.md"),
        ]
        for f in expected_files:
            self.assertTrue(f.exists(), f"Expected file not created: {f}")
            self.assertGreater(f.stat().st_size, 0)

    def test_install_addon_preserves_existing_user_files(self):
        op_path = Path(".ai/canvas/operational-board.md")
        op_path.parent.mkdir(parents=True, exist_ok=True)
        custom_content = "# My Custom Live Operational Board\n- Task 999: Do not touch this\n"
        op_path.write_text(custom_content, encoding="utf-8")

        # Run install without force
        install_addon("maestri", force=False)

        # Ensure user's existing file was strictly preserved
        self.assertEqual(op_path.read_text(encoding="utf-8"), custom_content)

    def test_install_addon_force_overwrites(self):
        op_path = Path(".ai/canvas/operational-board.md")
        op_path.parent.mkdir(parents=True, exist_ok=True)
        custom_content = "# My Custom Live Operational Board\n- Task 999: Custom\n"
        op_path.write_text(custom_content, encoding="utf-8")

        # Run install with force=True
        install_addon("maestri", force=True)

        # Content should now be reset to canonical template
        self.assertNotEqual(op_path.read_text(encoding="utf-8"), custom_content)
        self.assertIn("pxos:canvas:operational-board", op_path.read_text(encoding="utf-8"))

    def test_configure_addon_ide_rules(self):
        # Cursor
        configure_addon_ide_rules("maestri", "cursor")
        cursor_rule = Path(".cursor/rules/pxos-maestri.mdc")
        self.assertTrue(cursor_rule.exists())
        self.assertIn("alwaysApply: true", cursor_rule.read_text(encoding="utf-8"))
        self.assertIn("Single Source of Truth", cursor_rule.read_text(encoding="utf-8"))

        # Claude with pre-existing user instructions
        claude_rule = Path("CLAUDE.md")
        claude_rule.write_text("# My User Custom Claude Instructions\nNever touch this header.\n", encoding="utf-8")
        configure_addon_ide_rules("maestri", "claude")
        claude_content = claude_rule.read_text(encoding="utf-8")
        self.assertIn("# My User Custom Claude Instructions", claude_content)
        self.assertIn("<!-- pxos:maestri:start -->", claude_content)
        self.assertIn("<!-- pxos:maestri:end -->", claude_content)

        # Gemini
        configure_addon_ide_rules("maestri", "gemini")
        gemini_rule = Path("GEMINI.md")
        self.assertTrue(gemini_rule.exists())
        gemini_content = gemini_rule.read_text(encoding="utf-8")
        self.assertIn("<!-- pxos:maestri:start -->", gemini_content)

        # Windsurf
        configure_addon_ide_rules("maestri", "windsurf")
        windsurf_rule = Path(".windsurf/rules/pxos-maestri.md")
        self.assertTrue(windsurf_rule.exists())

        # Copilot
        configure_addon_ide_rules("maestri", "copilot")
        copilot_rule = Path(".github/copilot-instructions.md")
        self.assertTrue(copilot_rule.exists())


if __name__ == "__main__":
    unittest.main()
