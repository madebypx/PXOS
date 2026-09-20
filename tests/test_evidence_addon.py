"""Tests for PXOS Evidence Addon (T-15).

Verifies canonical template integrity, peer-review skill frontmatter,
CLI `pxos add evidence` and `pxos init --evidence` workflows,
idempotent file copying, and editor rule integration.
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


class TestEvidenceAddonTemplates(unittest.TestCase):
    """Tests for canonical template files and skill definition."""

    def test_canonical_templates_exist(self):
        evidence_dir = REPO_ROOT / "templates" / "addons" / "evidence"
        required_files = [
            evidence_dir / ".ai" / "research" / "00-governance" / "research-protocol.md",
            evidence_dir / ".ai" / "research" / "00-governance" / "ai-governance.md",
            evidence_dir / ".ai" / "research" / "00-governance" / "adversarial-reviewer.md",
            evidence_dir / ".ai" / "research" / "evidence-matrix.csv",
            evidence_dir / ".ai" / "research" / "source-register.csv",
            evidence_dir / ".ai" / "research" / "negative-cases.md",
            evidence_dir / ".ai" / "research" / "rejected-claims.md",
            evidence_dir / "rules" / "evidence_first_research.md",
        ]
        for f in required_files:
            self.assertTrue(f.exists(), f"Missing template file: {f}")
            self.assertGreater(f.stat().st_size, 0, f"Template file is empty: {f}")

    def test_csv_schemas(self):
        matrix_csv = REPO_ROOT / "templates" / "addons" / "evidence" / ".ai" / "research" / "evidence-matrix.csv"
        source_csv = REPO_ROOT / "templates" / "addons" / "evidence" / ".ai" / "research" / "source-register.csv"

        matrix_header = matrix_csv.read_text(encoding="utf-8").splitlines()[0]
        self.assertIn("id,claim,classification,source_id,source_location", matrix_header)
        self.assertIn("evidence_strength,limitations,verification_status", matrix_header)

        source_header = source_csv.read_text(encoding="utf-8").splitlines()[0]
        self.assertIn("id,source_title,author_or_institution,year,type,url_or_filepath", source_header)
        self.assertIn("access_date,verification_status,notes", source_header)

    def test_research_protocol_invariants(self):
        protocol_file = REPO_ROOT / "templates" / "addons" / "evidence" / ".ai" / "research" / "00-governance" / "research-protocol.md"
        content = protocol_file.read_text(encoding="utf-8")
        self.assertIn("FAIR Research", content)
        self.assertIn("5 Epistemic Layers", content)
        self.assertIn("Layer 1: Raw Data", content)
        self.assertIn("Layer 2: Finding / Inference", content)
        self.assertIn("Layer 3: Design Hypothesis", content)
        self.assertIn("Layer 4: Architectural Decision (ADR)", content)
        self.assertIn("Layer 5: Validated Conclusion", content)
        self.assertIn("INSUFFICIENT EVIDENCE — DO NOT CONCLUDE", content)

    def test_adversarial_verdicts(self):
        reviewer_file = REPO_ROOT / "templates" / "addons" / "evidence" / ".ai" / "research" / "00-governance" / "adversarial-reviewer.md"
        content = reviewer_file.read_text(encoding="utf-8")
        for verdict in ["REMOVE", "QUALIFY", "VERIFY", "REANALYZE", "RETAIN"]:
            self.assertIn(verdict, content)

    def test_peer_review_skill(self):
        skill_file = REPO_ROOT / "skills" / "peer-review" / "SKILL.md"
        self.assertTrue(skill_file.exists(), "Missing skills/peer-review/SKILL.md")
        content = skill_file.read_text(encoding="utf-8")
        self.assertTrue(content.startswith("---"))
        self.assertIn("name: peer-review", content)
        self.assertIn("/peer-review — Adversarial Methodological Review", content)
        for verdict in ["REMOVE", "QUALIFY", "VERIFY", "REANALYZE", "RETAIN"]:
            self.assertIn(verdict, content)


class TestEvidenceAddonCLI(unittest.TestCase):
    """Tests for CLI integration of `pxos add evidence` and `pxos init --evidence`."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="pxos_test_addon_")
        self.old_cwd = os.getcwd()
        os.chdir(self.test_dir)

    def tearDown(self):
        os.chdir(self.old_cwd)
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_install_addon_evidence_fresh(self):
        # Fresh install without pre-existing files
        install_addon("evidence", force=False)

        expected_files = [
            Path(".ai/research/00-governance/research-protocol.md"),
            Path(".ai/research/00-governance/ai-governance.md"),
            Path(".ai/research/00-governance/adversarial-reviewer.md"),
            Path(".ai/research/evidence-matrix.csv"),
            Path(".ai/research/source-register.csv"),
            Path(".ai/research/negative-cases.md"),
            Path(".ai/research/rejected-claims.md"),
        ]
        for f in expected_files:
            self.assertTrue(f.exists(), f"Expected file not created: {f}")
            self.assertGreater(f.stat().st_size, 0)

    def test_install_addon_preserves_existing_files(self):
        matrix_path = Path(".ai/research/evidence-matrix.csv")
        matrix_path.parent.mkdir(parents=True, exist_ok=True)
        custom_content = "id,claim\nCUSTOM-001,Keep this claim safe\n"
        matrix_path.write_text(custom_content, encoding="utf-8")

        # Run addon install without force
        install_addon("evidence", force=False)

        # Ensure custom content was NOT overwritten
        self.assertEqual(matrix_path.read_text(encoding="utf-8"), custom_content)

    def test_install_addon_force_overwrites(self):
        matrix_path = Path(".ai/research/evidence-matrix.csv")
        matrix_path.parent.mkdir(parents=True, exist_ok=True)
        custom_content = "id,claim\nCUSTOM-001,Keep this claim safe\n"
        matrix_path.write_text(custom_content, encoding="utf-8")

        # Run addon install with force=True
        install_addon("evidence", force=True)

        # Content should now be the canonical template
        self.assertNotEqual(matrix_path.read_text(encoding="utf-8"), custom_content)
        self.assertIn("EVD-001", matrix_path.read_text(encoding="utf-8"))

    def test_install_addon_links_research_index(self):
        index_path = Path(".ai/research/INDEX.md")
        index_path.parent.mkdir(parents=True, exist_ok=True)
        initial_index = """# Research Index
<!-- pxos:research:index -->

## Active Research & Invariants

| Document | Topic / Subsystem | Key Takeaway / Invariant | Status | Last Updated |
|---|---|---|---|---|
| *None yet* | *Initial project setup* | *No active research constraints registered* | Active | YYYY-MM-DD |
"""
        index_path.write_text(initial_index, encoding="utf-8")

        install_addon("evidence", force=False)

        updated_text = index_path.read_text(encoding="utf-8")
        self.assertIn("00-governance/research-protocol.md", updated_text)
        self.assertIn("5-Layer Epistemic Model", updated_text)

    def test_configure_addon_ide_rules(self):
        # Cursor
        configure_addon_ide_rules("evidence", "cursor")
        cursor_rule = Path(".cursor/rules/pxos-evidence.mdc")
        self.assertTrue(cursor_rule.exists())
        self.assertIn("alwaysApply: true", cursor_rule.read_text(encoding="utf-8"))
        self.assertIn("Epistemic Layer Separation", cursor_rule.read_text(encoding="utf-8"))

        # Claude
        configure_addon_ide_rules("evidence", "claude")
        claude_rule = Path("CLAUDE.md")
        self.assertTrue(claude_rule.exists())
        claude_content = claude_rule.read_text(encoding="utf-8")
        self.assertIn("<!-- pxos:evidence:start -->", claude_content)
        self.assertIn("<!-- pxos:evidence:end -->", claude_content)

        # Gemini
        configure_addon_ide_rules("evidence", "gemini")
        gemini_rule = Path("GEMINI.md")
        self.assertTrue(gemini_rule.exists())
        gemini_content = gemini_rule.read_text(encoding="utf-8")
        self.assertIn("<!-- pxos:evidence:start -->", gemini_content)

        # Windsurf
        configure_addon_ide_rules("evidence", "windsurf")
        windsurf_rule = Path(".windsurf/rules/pxos-evidence.md")
        self.assertTrue(windsurf_rule.exists())

        # Copilot
        configure_addon_ide_rules("evidence", "copilot")
        copilot_rule = Path(".github/copilot-instructions.md")
        self.assertTrue(copilot_rule.exists())

    def test_unknown_addon_exits(self):
        with self.assertRaises(SystemExit):
            install_addon("non_existent_addon")


if __name__ == "__main__":
    unittest.main()
