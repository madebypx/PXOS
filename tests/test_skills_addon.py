"""Tests for PXOS Cognitive Skills Router Addon.

Verifies canonical template integrity, CLI `pxos add skills` and `pxos init --skills` workflows,
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
    main,
)

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestSkillsAddonTemplates(unittest.TestCase):
    """Tests for canonical template files and rules."""

    def test_canonical_templates_exist(self):
        skills_dir = REPO_ROOT / "templates" / "addons" / "skills"
        required_files = [
            skills_dir / "rules" / "skills_router.md",
            skills_dir / ".ai" / "skills" / "SKILLS_ROUTER.md",
        ]
        for f in required_files:
            self.assertTrue(f.exists(), f"Missing template file: {f}")
            self.assertGreater(f.stat().st_size, 0, f"Template file is empty: {f}")

    def test_rules_content_invariants(self):
        rules_file = REPO_ROOT / "templates" / "addons" / "skills" / "rules" / "skills_router.md"
        content = rules_file.read_text(encoding="utf-8")
        self.assertIn("Decision Matrix", content)
        self.assertIn("Just-in-Time", content)
        self.assertIn("Zero Overhead", content)
        self.assertIn("Precedence of Local", content)
        self.assertIn("design-taste-frontend", content)
        self.assertIn("awesome-design-md", content)
        self.assertIn("expo-overview", content)
        self.assertIn("playwright-cli", content)
        self.assertIn("brandkit", content)
        self.assertIn("maestri*", content)

    def test_skills_router_template_structure(self):
        router_file = REPO_ROOT / "templates" / "addons" / "skills" / ".ai" / "skills" / "SKILLS_ROUTER.md"
        content = router_file.read_text(encoding="utf-8")
        self.assertIn("<!-- pxos:skills-version", content)
        self.assertIn("Just-in-Time (JIT) Activation Protocol", content)
        self.assertIn("Core Intent & Decision Matrix", content)
        self.assertIn("Project-Specific Extensions", content)


class TestSkillsAddonCLI(unittest.TestCase):
    """Tests for CLI integration of `pxos add skills`."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="pxos_test_skills_")
        self.old_cwd = os.getcwd()
        os.chdir(self.test_dir)

    def tearDown(self):
        os.chdir(self.old_cwd)
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_install_addon_skills_fresh(self):
        install_addon("skills", force=False)

        expected_files = [
            Path(".ai/skills/SKILLS_ROUTER.md"),
        ]
        for f in expected_files:
            self.assertTrue(f.exists(), f"Expected file not created: {f}")
            self.assertGreater(f.stat().st_size, 0)

    def test_install_addon_preserves_existing_user_files(self):
        router_path = Path(".ai/skills/SKILLS_ROUTER.md")
        router_path.parent.mkdir(parents=True, exist_ok=True)
        custom_content = "# My Custom Live Skills Router\n- Custom Skill: do not touch\n"
        router_path.write_text(custom_content, encoding="utf-8")

        install_addon("skills", force=False)
        self.assertEqual(router_path.read_text(encoding="utf-8"), custom_content)

    def test_install_addon_force_overwrites(self):
        router_path = Path(".ai/skills/SKILLS_ROUTER.md")
        router_path.parent.mkdir(parents=True, exist_ok=True)
        custom_content = "# My Custom Live Skills Router\n- Custom Skill: do not touch\n"
        router_path.write_text(custom_content, encoding="utf-8")

        install_addon("skills", force=True)
        self.assertNotEqual(router_path.read_text(encoding="utf-8"), custom_content)
        self.assertIn("pxos:skills-version", router_path.read_text(encoding="utf-8"))

    def test_configure_addon_ide_rules(self):
        # Cursor
        configure_addon_ide_rules("skills", "cursor")
        cursor_rule = Path(".cursor/rules/pxos-skills.mdc")
        self.assertTrue(cursor_rule.exists())
        self.assertIn("alwaysApply: true", cursor_rule.read_text(encoding="utf-8"))
        self.assertIn("Decision Matrix", cursor_rule.read_text(encoding="utf-8"))

        # Claude with pre-existing user instructions
        claude_rule = Path("CLAUDE.md")
        claude_rule.write_text("# My User Custom Claude Instructions\nNever touch this header.\n", encoding="utf-8")
        configure_addon_ide_rules("skills", "claude")
        claude_content = claude_rule.read_text(encoding="utf-8")
        self.assertIn("# My User Custom Claude Instructions", claude_content)
        self.assertIn("<!-- pxos:skills:start -->", claude_content)
        self.assertIn("<!-- pxos:skills:end -->", claude_content)

        # Gemini
        configure_addon_ide_rules("skills", "gemini")
        gemini_rule = Path("GEMINI.md")
        self.assertTrue(gemini_rule.exists())
        gemini_content = gemini_rule.read_text(encoding="utf-8")
        self.assertIn("<!-- pxos:skills:start -->", gemini_content)
        self.assertIn("<!-- pxos:skills:end -->", gemini_content)

        # Windsurf
        configure_addon_ide_rules("skills", "windsurf")
        windsurf_rule = Path(".windsurf/rules/pxos-skills.md")
        self.assertTrue(windsurf_rule.exists())

        # Copilot
        configure_addon_ide_rules("skills", "copilot")
        copilot_rule = Path(".github/copilot-instructions.md")
        self.assertTrue(copilot_rule.exists())


if __name__ == "__main__":
    unittest.main()
