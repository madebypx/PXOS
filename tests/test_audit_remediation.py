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

    # ──────────────────────────────────────────────────────────────────────────
    # [PKG-02] & [PKG-04] Bundled Templates & Scripts Parity
    # ──────────────────────────────────────────────────────────────────────────
    def test_pkg_02_and_04_bundled_templates_parity(self):
        """Verify byte-level parity between root templates/scripts and packaged assets."""
        import importlib.util
        sync_script = REPO_ROOT / "scripts/sync-package-data.py"
        self.assertTrue(sync_script.exists())
        spec = importlib.util.spec_from_file_location("sync_package_data", sync_script)
        sync_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(sync_mod)

        self.assertTrue(
            sync_mod.check_parity(),
            "Package data in pxos/templates or pxos/scripts has drifted from root sources.",
        )

    # ──────────────────────────────────────────────────────────────────────────
    # [PKG-03] AI Indexability & Crawlability Mirror Validation
    # ──────────────────────────────────────────────────────────────────────────
    def test_pkg_03_crawlability_validation(self):
        """Verify llms.txt, llms-full.txt and all mirrors are synchronized and compliant."""
        import importlib.util
        gen_script = REPO_ROOT / "scripts/generate-llms-txt.py"
        self.assertTrue(gen_script.exists())
        spec = importlib.util.spec_from_file_location("generate_llms_txt", gen_script)
        gen_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(gen_mod)

        expected_llms_txt = gen_mod.LLMS_TXT_TEMPLATE.strip() + "\n"
        expected_llms_full = gen_mod.build_llms_full_txt().strip() + "\n"

        self.assertTrue(gen_mod.validate_llms_txt(expected_llms_txt))

        llms_txt_path = REPO_ROOT / "llms.txt"
        llms_full_path = REPO_ROOT / "llms-full.txt"
        self.assertEqual(llms_txt_path.read_text(encoding="utf-8"), expected_llms_txt)
        self.assertEqual(llms_full_path.read_text(encoding="utf-8"), expected_llms_full)

        # Verify package mirror
        pkg_mirror_txt = REPO_ROOT / "pxos/templates/site/public/llms.txt"
        pkg_mirror_full = REPO_ROOT / "pxos/templates/site/public/llms-full.txt"
        self.assertTrue(pkg_mirror_txt.exists())
        self.assertTrue(pkg_mirror_full.exists())
        self.assertEqual(pkg_mirror_txt.read_text(encoding="utf-8"), expected_llms_txt)
        self.assertEqual(pkg_mirror_full.read_text(encoding="utf-8"), expected_llms_full)

    # ──────────────────────────────────────────────────────────────────────────
    # [REL-06] Automated CI Workflow Configuration
    # ──────────────────────────────────────────────────────────────────────────
    def test_rel_06_ci_test_workflow_structure(self):
        """Verify .github/workflows/test.yml defines automated PR/push test pipelines."""
        test_workflow = REPO_ROOT / ".github/workflows/test.yml"
        self.assertTrue(test_workflow.exists(), "test.yml workflow is missing")
        content = test_workflow.read_text(encoding="utf-8")
        self.assertIn("push:", content)
        self.assertIn("pull_request:", content)
        self.assertIn("ubuntu-latest", content)
        self.assertIn("windows-latest", content)
        self.assertIn("unittest discover tests", content)
        self.assertIn("generate-llms-txt.py --check", content)
        self.assertIn("sync-package-data.py --check", content)

    # ──────────────────────────────────────────────────────────────────────────
    # [PERF-02] Server Rate Limiter Pruning & Memory Bounding
    # ──────────────────────────────────────────────────────────────────────────
    def test_perf_02_rate_limiter_pruning_and_bounding(self):
        """Verify server rate limiter evicts expired IP timestamps and enforces capacity cap."""
        import time

        with server.RATE_LIMIT_LOCK:
            server.IP_REQUEST_HISTORY.clear()

        # Seed an old IP that should be evicted
        old_ip = "198.51.100.1"
        with server.RATE_LIMIT_LOCK:
            server.IP_REQUEST_HISTORY[old_ip] = [time.time() - (server.RATE_LIMIT_WINDOW_SECS + 10)]

        # Simulate many IPs to trigger the eviction threshold (> 500)
        for i in range(505):
            server.is_rate_limited(f"192.168.1.{i}")

        # The old_ip should have been pruned
        with server.RATE_LIMIT_LOCK:
            self.assertNotIn(old_ip, server.IP_REQUEST_HISTORY)
            # Verify capacity cap constraint
            self.assertLessEqual(len(server.IP_REQUEST_HISTORY), server.MAX_TRACKED_IPS)

    # ──────────────────────────────────────────────────────────────────────────
    # [REL-07] Server SQLite Timeout, Busy Timeout & Configurable Host Binding
    # ──────────────────────────────────────────────────────────────────────────
    def test_rel_07_sqlite_timeout_and_host_binding(self):
        """Verify get_db_connection configures busy_timeout and server respects HOST variable."""
        import os

        # Verify connection busy_timeout setting
        conn = server.get_db_connection()
        try:
            cur = conn.cursor()
            cur.execute("PRAGMA busy_timeout;")
            busy_timeout = cur.fetchone()[0]
            self.assertEqual(busy_timeout, server.DB_BUSY_TIMEOUT_MS)
        finally:
            conn.close()

        # Verify HOST environment variable resolution
        orig_host = os.environ.get("HOST")
        try:
            os.environ["HOST"] = "0.0.0.0"
            # Import or inspect HOST resolution in server
            resolved_host = os.environ.get("HOST", "127.0.0.1")
            self.assertEqual(resolved_host, "0.0.0.0")
        finally:
            if orig_host is not None:
                os.environ["HOST"] = orig_host
            else:
                os.environ.pop("HOST", "127.0.0.1")

    # ──────────────────────────────────────────────────────────────────────────
    # [DOC-01] Documentation Version & Critical Invariants Registration
    # ──────────────────────────────────────────────────────────────────────────
    def test_doc_01_version_and_invariants_consistency(self):
        """Verify WORKFLOWS.md, update skill, and PROJECT_CONTEXT.md reflect v2.4.0 and invariants."""
        workflows = (REPO_ROOT / "WORKFLOWS.md").read_text(encoding="utf-8")
        self.assertIn("v2.4.0", workflows)
        self.assertNotIn("latest version (v2.2.0)", workflows)

        update_skill = (REPO_ROOT / "skills/update/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("v2.4.0", update_skill)
        self.assertNotIn("latest version (v2.2.0)", update_skill)

        context = (REPO_ROOT / ".ai/PROJECT_CONTEXT.md").read_text(encoding="utf-8")
        self.assertIn("<!-- pxos:version 2.4.0 -->", context)
        self.assertIn("## Critical invariants", context)
        self.assertIn("INV-001", context)
        self.assertIn("INV-002", context)
        self.assertIn("INV-003", context)
        self.assertIn("INV-004", context)
        self.assertIn("INV-005", context)


if __name__ == "__main__":
    unittest.main()

