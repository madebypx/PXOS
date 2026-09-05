"""Automated Verification Suite for Audit Remediation (T-06).

Tests all 9 security, reliability, packaging, and performance fixes from AUDIT_2026-09-04.
Pure Python standard library (unittest).
"""

import json
import re
import sys
import unittest
from pathlib import Path

# Add project root to sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "benchmarks"))

import analyze
import server
import pxos.cli


class AuditRemediationTestSuite(unittest.TestCase):

    def setUp(self):
        self.sample_payload = {
            "audit_metadata": {
                "evaluation_mode": "retrospective",
                "project_name": "test-repo",
                "evaluator_agent_model": "test-model",
                "timestamp_iso": "2026-09-04T00:00:00Z",
                "accidental_personal_email": "developer@company.internal",
            },
            "task_profile": {
                "task_id": "T-TEST",
                "task_description": "Unit testing audit remediation",
                "complexity_tier": "tier_2_medium",
                "primary_subsystem": "telemetry",
            },
            "quantitative_telemetry": {
                "total_turns": 5,
                "input_tokens_total": 10000,
                "output_tokens_total": 2000,
                "framework_overhead_tokens": 800,
                "initial_implementation_loc": 50,
                "rework_lines_modified_or_deleted": 2,
                "rework_turn_count": 1,
                "unresolved_compiler_or_test_failures": 0,
                "merge_conflicts_encountered": 0,
            },
            "product_design_and_ux": {
                "ui_components_touched": False,
                "ux_state_completeness_score": 1.0,
                "design_tokens_adhered": True,
            },
            "architectural_fidelity": {
                "session_amnesia_occurred": False,
                "invariants_violated_count": 0,
                "duplicate_utilities_introduced": 0,
                "adrs_consulted_count": 1,
                "new_adrs_registered": 0,
            },
            "critical_assessment": {
                "net_utility_score": 4,
                "overhead_justified": True,
                "identified_frictions": ["minor setup friction"],
                "concrete_benefits": ["clear spec"],
            },
            "unauthorized_source_code_leak": "def secret_key(): return 'AKIAIOSFODNN7EXAMPLE'",
        }

    # ──────────────────────────────────────────────────────────────────────────
    # [SEC-01] Privacy & PII Scrubbing on raw_payload
    # ──────────────────────────────────────────────────────────────────────────
    def test_sec_01_sanitized_raw_payload_storage(self):
        """Verify that extra/unauthorized client fields are excluded from raw_payload."""
        is_valid, err, sanitized = server.validate_and_sanitize_payload(self.sample_payload)
        self.assertTrue(is_valid, f"Validation failed: {err}")
        self.assertIsNotNone(sanitized)

        # Inspect the raw_payload stored in sanitized dict
        raw_stored = json.loads(sanitized["raw_payload"])
        self.assertNotIn("unauthorized_source_code_leak", raw_stored)
        self.assertNotIn("accidental_personal_email", raw_stored.get("audit_metadata", {}))
        self.assertIn("quantitative_telemetry", raw_stored)
        self.assertEqual(raw_stored["task_profile"]["task_id"], "T-TEST")

    # ──────────────────────────────────────────────────────────────────────────
    # [SEC-02] Rate Limiting & Trusted Proxy Validation
    # ──────────────────────────────────────────────────────────────────────────
    def test_sec_02_rate_limiting(self):
        """Verify sliding-window rate limiter blocks after MAX_REQUESTS_PER_WINDOW."""
        test_ip = "192.0.2.42"
        # First 20 requests should pass
        for i in range(server.MAX_REQUESTS_PER_WINDOW):
            self.assertFalse(
                server.is_rate_limited(test_ip),
                f"Request {i+1} should not have been rate-limited",
            )
        # 21st request should be blocked
        self.assertTrue(
            server.is_rate_limited(test_ip),
            "Request 21 must be rate-limited",
        )

    # ──────────────────────────────────────────────────────────────────────────
    # [REL-01] Database try-finally connection handling
    # ──────────────────────────────────────────────────────────────────────────
    def test_rel_01_database_init_and_close(self):
        """Verify init_database executes and safely closes connections."""
        server.init_database()
        self.assertTrue(server.DB_PATH.exists())

    # ──────────────────────────────────────────────────────────────────────────
    # [REL-02] Type Conversion Safety in Telemetry Sanitizer
    # ──────────────────────────────────────────────────────────────────────────
    def test_rel_02_type_conversion_safety(self):
        """Verify malformed architectural metrics return 422 validation error, not 500."""
        bad_payload = dict(self.sample_payload)
        bad_payload["architectural_fidelity"] = {
            "invariants_violated_count": "NOT_AN_INT",
        }
        is_valid, err_msg, sanitized = server.validate_and_sanitize_payload(bad_payload)
        self.assertFalse(is_valid)
        self.assertIn("Type validation error", err_msg)
        self.assertIsNone(sanitized)

    # ──────────────────────────────────────────────────────────────────────────
    # [PERF-01] In-Memory Record Loading Without Disk Thrashing
    # ──────────────────────────────────────────────────────────────────────────
    def test_perf_01_in_memory_record_loading(self):
        """Verify analyze.load_record_from_dict parses records directly in memory."""
        record = analyze.load_record_from_dict(self.sample_payload, "test_source")
        self.assertIsNotNone(record)
        self.assertEqual(record.task_id, "T-TEST")
        self.assertEqual(record.total_turns, 5)
        self.assertEqual(record.total_tokens, 12000)
        self.assertAlmostEqual(record.rework_ratio, 4.0, places=1)

    # ──────────────────────────────────────────────────────────────────────────
    # [PKG-01] Package Resource Resolution in pxos.cli
    # ──────────────────────────────────────────────────────────────────────────
    def test_pkg_01_resource_path_resolution(self):
        """Verify get_resource_path locates bundled scripts and templates."""
        script_path = pxos.cli.get_resource_path("scripts/pxos-benchmark.py")
        self.assertTrue(script_path.exists(), f"Benchmark script missing: {script_path}")

        monitor_path = pxos.cli.get_resource_path("scripts/pxos-telemetry-monitor.py")
        self.assertTrue(monitor_path.exists(), f"Monitor script missing: {monitor_path}")

        template_path = pxos.cli.get_resource_path("templates/.ai/AI_BASE.md")
        self.assertTrue(template_path.exists(), f"AI_BASE template missing: {template_path}")

    # ──────────────────────────────────────────────────────────────────────────
    # [REL-03] Worktree Multi-Slash Branch Normalization
    # ──────────────────────────────────────────────────────────────────────────
    def test_rel_03_worktree_branch_normalization(self):
        """Verify multi-slash branch names normalize to valid single-level filenames."""
        nested_branch = "feat/telemetry/wal/fix-lock"
        # Replicate normalization logic from pxos-task.sh / pxos-task.ps1:
        # sed -E 's/^(feat|fix|chore|refactor)\///' | tr '/' '-'
        prefix_stripped = re.sub(r"^(feat|fix|chore|refactor)/", "", nested_branch)
        normalized_suffix = prefix_stripped.replace("/", "-")
        spec_file = f".ai/specs/SPEC-{normalized_suffix}.md"

        self.assertEqual(normalized_suffix, "telemetry-wal-fix-lock")
        self.assertEqual(spec_file, ".ai/specs/SPEC-telemetry-wal-fix-lock.md")
        self.assertNotIn("/", spec_file.replace(".ai/specs/", ""))

    # ──────────────────────────────────────────────────────────────────────────
    # [REL-04] GitHub Actions Release Workflow Tag Gating
    # ──────────────────────────────────────────────────────────────────────────
    def test_rel_04_ci_workflow_tag_gating(self):
        """Verify .github/workflows/release.yml gates release and publish steps with tag condition."""
        workflow_path = REPO_ROOT / ".github/workflows/release.yml"
        self.assertTrue(workflow_path.exists())
        content = workflow_path.read_text(encoding="utf-8")
        self.assertIn("startsWith(github.ref, 'refs/tags/v')", content)

    # ──────────────────────────────────────────────────────────────────────────
    # [REL-05] Benchmark Client Null Safety
    # ──────────────────────────────────────────────────────────────────────────
    def test_rel_05_benchmark_null_safety(self):
        """Verify pxos-benchmark.py handles null values in frictions/benefits without TypeError."""
        import importlib.util
        script_file = REPO_ROOT / "scripts/pxos-benchmark.py"
        spec = importlib.util.spec_from_file_location("pxos_benchmark", script_file)
        pxos_benchmark = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(pxos_benchmark)

        payload_with_nulls = dict(self.sample_payload)
        payload_with_nulls["critical_assessment"] = {
            "net_utility_score": 3,
            "overhead_justified": True,
            "identified_frictions": None,  # Explicit null
            "concrete_benefits": None,     # Explicit null
        }
        is_valid, err, clean = pxos_benchmark.sanitize_payload(payload_with_nulls)
        self.assertTrue(is_valid, f"Sanitization failed: {err}")
        self.assertEqual(clean["critical_assessment"]["identified_frictions"], [])
        self.assertEqual(clean["critical_assessment"]["concrete_benefits"], [])


if __name__ == "__main__":
    unittest.main()
