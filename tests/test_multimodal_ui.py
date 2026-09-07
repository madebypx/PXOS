#!/usr/bin/env python3
"""PXOS Multi-Modal UI Verification & Universal 5-State Inspector Test Suite.

Validates the 5-state matrix parser, benchmark telemetry integration,
adherence scoring bonuses, and privacy invariants.
"""

import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

import importlib.util

REPO_ROOT = Path(__file__).resolve().parent.parent
_script_path = REPO_ROOT / "scripts" / "pxos-benchmark.py"
_spec = importlib.util.spec_from_file_location("pxos_benchmark", _script_path)
pxos_benchmark = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pxos_benchmark)

UI_5_UNIVERSAL_STATES = pxos_benchmark.UI_5_UNIVERSAL_STATES
extract_ui_5_states = pxos_benchmark.extract_ui_5_states
find_latest_ui_audit = pxos_benchmark.find_latest_ui_audit
calculate_adherence_score = pxos_benchmark.calculate_adherence_score
build_extracted_benchmark = pxos_benchmark.build_extracted_benchmark
sanitize_payload = pxos_benchmark.sanitize_payload


class MultiModalUITestSuite(unittest.TestCase):
    """Test suite for Universal 5-State UI Verification and Benchmark Scoring."""

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.ai_dir = self.temp_dir / ".ai"
        self.audits_dir = self.ai_dir / "audits"
        self.audits_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_extract_ui_5_states_complete(self):
        """Test parsing complete 5/5 UI state verification matrix."""
        sample_audit = """
# Subsystem Audit Report
### UI 5-State Verification Matrix
| State | Status | Verified |
|---|---|:---:|
| `initial_idle` | PASS | [x] |
| `loading_pending` | PASS | [x] |
| `empty_data` | PASS | [x] |
| `error_recovery` | PASS | [x] |
| `destructive_action_guard` | PASS | [x] |
"""
        states = extract_ui_5_states(sample_audit)
        for st in UI_5_UNIVERSAL_STATES:
            self.assertTrue(states.get(st), f"Expected state {st} to be verified")
        self.assertEqual(sum(1 for v in states.values() if v), 5)

    def test_extract_ui_5_states_partial(self):
        """Test parsing partial 3/5 UI state verification matrix."""
        sample_audit = """
### UI 5-State Verification Matrix
- initial_idle: [x] clean populated screen
- loading_pending: [x] skeleton loader
- empty_data: [ ] zero state missing
- error_recovery: [x] retry banner works
- destructive_action_guard: [ ] immediate delete without confirmation
"""
        states = extract_ui_5_states(sample_audit)
        self.assertTrue(states["initial_idle"])
        self.assertTrue(states["loading_pending"])
        self.assertFalse(states["empty_data"])
        self.assertTrue(states["error_recovery"])
        self.assertFalse(states["destructive_action_guard"])
        self.assertEqual(sum(1 for v in states.values() if v), 3)

    def test_extract_ui_5_states_empty_or_missing(self):
        """Test parsing audit report with no UI state mentions."""
        sample_audit = """
# Backend Security Audit Report
Everything looks good. No issues found.
"""
        states = extract_ui_5_states(sample_audit)
        for st in UI_5_UNIVERSAL_STATES:
            self.assertFalse(states.get(st))
        self.assertEqual(sum(1 for v in states.values() if v), 0)

    def test_find_latest_ui_audit(self):
        """Test finding the latest relevant UI audit report in .ai/audits/."""
        # Non-UI audit
        (self.audits_dir / "AUDIT_2026-09-01.md").write_text("Backend DB Audit", encoding="utf-8")
        
        # UI audit
        ui_audit = self.audits_dir / "AUDIT_2026-09-07_UI.md"
        ui_audit.write_text("""
### UI 5-State Verification Matrix
| initial_idle | PASS | [x] |
| loading_pending | PASS | [x] |
""", encoding="utf-8")

        found = find_latest_ui_audit(self.temp_dir, task_id="T-12")
        self.assertIsNotNone(found)
        self.assertEqual(found.name, "AUDIT_2026-09-07_UI.md")

    def test_adherence_score_with_ui_bonus(self):
        """Test that 5/5 UI states awards +10 adherence points capped at 100."""
        # Setup mock project context
        ctx = self.ai_dir / "PROJECT_CONTEXT.md"
        ctx.write_text("# Project Context\nDurable context description here " * 10, encoding="utf-8")
        
        # Base adherence score without UI states
        base_score, _, _, base_breakdown = calculate_adherence_score(self.temp_dir, ui_states_count=0)
        
        # Adherence score with all 5 states verified
        boosted_score, _, _, boosted_breakdown = calculate_adherence_score(self.temp_dir, ui_states_count=5)
        
        self.assertEqual(boosted_breakdown.get("ui_5_states_verified"), 10)
        self.assertEqual(boosted_score, min(100, base_score + 10))
        self.assertLessEqual(boosted_score, 100)

    def test_adherence_score_partial_ui_no_bonus(self):
        """Test that partial UI verification (< 5) does NOT award the +10 adherence bonus."""
        score, _, _, breakdown = calculate_adherence_score(self.temp_dir, ui_states_count=4)
        self.assertEqual(breakdown.get("ui_5_states_verified"), 0)

    def test_build_extracted_benchmark_ui_verification(self):
        """Test build_extracted_benchmark with --verify-ui pointing to mock audit."""
        audit_file = self.audits_dir / "AUDIT_T-12.md"
        audit_file.write_text("""
### UI 5-State Verification Matrix
| `initial_idle` | PASS | [x] |
| `loading_pending` | PASS | [x] |
| `empty_data` | PASS | [x] |
| `error_recovery` | PASS | [x] |
| `destructive_action_guard` | PASS | [x] |
""", encoding="utf-8")

        benchmark = build_extracted_benchmark(
            task_id="T-12",
            repo_root=self.temp_dir,
            verify_ui=True,
            audit_file=str(audit_file),
        )

        ux = benchmark.get("product_design_and_ux", {})
        self.assertTrue(ux.get("ui_components_touched"))
        self.assertEqual(ux.get("ux_state_completeness_score"), 1.0)
        self.assertEqual(ux.get("ui_states_verified"), 5)

    def test_sanitize_payload_preserves_ui_fields(self):
        """Test that sanitize_payload validates and clamps ui_states_verified safely."""
        raw_payload = {
            "audit_metadata": {
                "schema_version": "2.0",
                "session_fingerprint": "1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
                "project_name": "test-project",
                "evaluation_mode": "retrospective",
            },
            "task_profile": {
                "task_id": "T-12",
                "complexity_tier": "tier_2_medium",
                "primary_subsystem": "frontend",
            },
            "quantitative_telemetry": {
                "total_turns": 5,
                "input_tokens_total": 10000,
                "output_tokens_total": 2000,
                "initial_implementation_loc": 200,
            },
            "product_design_and_ux": {
                "ui_components_touched": True,
                "ux_state_completeness_score": 0.8,
                "ui_states_verified": 4,
                "design_tokens_adhered": True,
            },
            "architectural_fidelity": {
                "adherence_score": 85,
            },
        }

        is_valid, err_msg, clean = sanitize_payload(raw_payload)
        self.assertTrue(is_valid, f"Sanitization failed: {err_msg}")
        ux = clean["product_design_and_ux"]
        self.assertTrue(ux["ui_components_touched"])
        self.assertEqual(ux["ux_state_completeness_score"], 0.8)
        self.assertEqual(ux["ui_states_verified"], 4)

    def test_templates_exist_and_zero_external_dependencies(self):
        """Verify that starter templates exist and enforce zero core external dependencies."""
        vanilla_template = REPO_ROOT / "templates" / "ui" / "vanilla_5_states.html"
        react_template = REPO_ROOT / "templates" / "ui" / "react_5_states.jsx"
        readme = REPO_ROOT / "templates" / "ui" / "README.md"
        doc = REPO_ROOT / "docs" / "UI_5_STATES.md"

        self.assertTrue(vanilla_template.exists(), "vanilla_5_states.html must exist")
        self.assertTrue(react_template.exists(), "react_5_states.jsx must exist")
        self.assertTrue(readme.exists(), "templates/ui/README.md must exist")
        self.assertTrue(doc.exists(), "docs/UI_5_STATES.md must exist")

        # Invariant INV-003: Vanilla template should be self-contained HTML
        vanilla_content = vanilla_template.read_text(encoding="utf-8")
        self.assertIn("initial_idle", vanilla_content)
        self.assertIn("destructive_action_guard", vanilla_content)


if __name__ == "__main__":
    unittest.main()
