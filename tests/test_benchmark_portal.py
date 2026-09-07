#!/usr/bin/env python3
"""
Unit and Integration Test Suite for Task T-13:
Public Benchmark Portal & Research Dashboard (pxos.madebypx.com/benchmarks)
===========================================================================
Verifies:
1. Static HTML structure, semantic SEO, and Schema.org Dataset metadata
2. CSS variables and responsive design rules
3. JavaScript syntax and baseline data consistency
4. Server /api/v1/stats model aggregation, recent runs stream, and tier filtering
5. Package parity between root templates and bundled pxos/templates
"""

import http.server
import json
import re
import sqlite3
import tempfile
import threading
import time
import unittest
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PORTAL_DIR = REPO_ROOT / "templates" / "site" / "public" / "benchmarks"
INDEX_HTML = PORTAL_DIR / "index.html"
DASHBOARD_CSS = PORTAL_DIR / "dashboard.css"
DASHBOARD_JS = PORTAL_DIR / "dashboard.js"


class TestBenchmarkPortalStaticAssets(unittest.TestCase):
    """Test suite verifying static frontend deliverables."""

    def test_html_file_exists(self):
        self.assertTrue(INDEX_HTML.exists(), "index.html must exist in templates/site/public/benchmarks/")
        self.assertGreater(INDEX_HTML.stat().st_size, 1000, "index.html must not be empty")

    def test_css_file_exists(self):
        self.assertTrue(DASHBOARD_CSS.exists(), "dashboard.css must exist in templates/site/public/benchmarks/")
        self.assertGreater(DASHBOARD_CSS.stat().st_size, 1000, "dashboard.css must not be empty")

    def test_js_file_exists(self):
        self.assertTrue(DASHBOARD_JS.exists(), "dashboard.js must exist in templates/site/public/benchmarks/")
        self.assertGreater(DASHBOARD_JS.stat().st_size, 1000, "dashboard.js must not be empty")

    def test_html_semantic_seo_and_metadata(self):
        content = INDEX_HTML.read_text(encoding="utf-8")

        # HTML5 doctype & title
        self.assertIn("<!DOCTYPE html>", content)
        self.assertIn("<title>", content)
        self.assertIn("PXOS Public Benchmark Portal", content)

        # Meta description and canonical link
        self.assertIn('<meta name="description"', content)
        self.assertIn('<link rel="canonical" href="https://pxos.madebypx.com/benchmarks/">', content)

        # OpenGraph and Twitter cards
        self.assertIn('<meta property="og:title"', content)
        self.assertIn('<meta property="og:type" content="website">', content)
        self.assertIn('<meta name="twitter:card"', content)

        # Exact one h1 tag for clean hierarchy
        h1_matches = re.findall(r"<h1[^>]*>.*?</h1>", content, re.DOTALL | re.IGNORECASE)
        self.assertEqual(len(h1_matches), 1, "There must be exactly one <h1> element on the page.")

        # Schema.org Dataset verification
        schema_match = re.search(r'<script type="application/ld\+json">(.*?)</script>', content, re.DOTALL)
        self.assertIsNotNone(schema_match, "Must include Schema.org JSON-LD structured data")
        schema_json = json.loads(schema_match.group(1))
        self.assertEqual(schema_json["@type"], "Dataset")
        self.assertIn("PXOS", schema_json["name"])
        self.assertEqual(schema_json["url"], "https://pxos.madebypx.com/benchmarks/")

    def test_html_required_interactive_elements(self):
        content = INDEX_HTML.read_text(encoding="utf-8")

        required_ids = [
            "network-status",
            "stat-total-runs",
            "stat-tokens-loc",
            "stat-mean-rework",
            "stat-mean-ux",
            "stat-justified-rate",
            "btn-tier-a",
            "btn-tier-all",
            "btn-export-json",
            "btn-export-csv",
            "chart-token-economy",
            "chart-rework-churn",
            "chart-ux-adherence",
            "recent-runs-tbody"
        ]

        for elem_id in required_ids:
            self.assertIn(f'id="{elem_id}"', content, f"Required DOM element id='{elem_id}' not found in index.html")

    def test_css_design_system_tokens(self):
        css = DASHBOARD_CSS.read_text(encoding="utf-8")

        required_tokens = [
            "--bg-base",
            "--bg-surface",
            "--border-subtle",
            "--accent-blue",
            "--accent-emerald",
            "--accent-amber",
            "--font-sans"
        ]

        for token in required_tokens:
            self.assertIn(token, css, f"Design token {token} missing in dashboard.css")

        # Check responsive query
        self.assertIn("@media", css)

    def test_javascript_baseline_consistency(self):
        js = DASHBOARD_JS.read_text(encoding="utf-8")

        # Must define endpoints and baseline
        self.assertIn("https://telemetry.madebypx.com/api/v1/stats", js)
        self.assertIn("BASELINE_DATASET", js)
        self.assertIn("exportDatasetJSON", js)
        self.assertIn("exportDatasetCSV", js)

    def test_sitemap_and_robots_inclusion(self):
        sitemap = (REPO_ROOT / "templates" / "site" / "public" / "sitemap.xml").read_text(encoding="utf-8")
        self.assertIn("https://pxos.madebypx.com/benchmarks/", sitemap)

        robots = (REPO_ROOT / "templates" / "site" / "public" / "robots.txt").read_text(encoding="utf-8")
        self.assertIn("Allow: /benchmarks/", robots)


class TestBenchmarkServerEnrichment(unittest.TestCase):
    """Test suite verifying backend server /api/v1/stats enrichment."""

    @classmethod
    def setUpClass(cls):
        # Dynamically import server components
        import benchmarks.server as srv
        cls.srv = srv

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_telemetry.db"
        self.prev_db = self.srv.DB_PATH
        self.srv.DB_PATH = self.db_path
        self.srv.init_database()

    def tearDown(self):
        self.srv.DB_PATH = self.prev_db
        self.temp_dir.cleanup()

    def test_stats_empty_database_schema(self):
        handler = self.srv.TelemetryRequestHandler
        httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
        port = httpd.server_port
        server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        server_thread.start()

        try:
            url = f"http://127.0.0.1:{port}/api/v1/stats"
            with urllib.request.urlopen(url, timeout=5) as resp:
                self.assertEqual(resp.status, 200)
                data = json.loads(resp.read().decode("utf-8"))
                self.assertEqual(data["total_submissions"], 0)
                self.assertIn("models", data)
                self.assertEqual(data["models"], [])
                self.assertIn("recent_runs", data)
                self.assertEqual(data["recent_runs"], [])
        finally:
            httpd.shutdown()
            httpd.server_close()

    def test_stats_populated_with_models_and_recent_runs(self):
        handler = self.srv.TelemetryRequestHandler
        httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
        port = httpd.server_port
        server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        server_thread.start()

        try:
            # 1. Ingest Tier A run for Gemini Flash
            p1 = {
                "audit_metadata": {
                    "session_fingerprint": "fp_test_gemini_01",
                    "schema_version": "2.0",
                    "evaluator_agent_model": "gemini-2-flash"
                },
                "task_profile": {
                    "task_id": "T-01",
                    "task_description": "Telemetry test",
                    "complexity_tier": "tier_2_medium",
                    "primary_subsystem": "telemetry"
                },
                "quantitative_telemetry": {
                    "total_turns": 4,
                    "input_tokens_total": 30000,
                    "output_tokens_total": 5000,
                    "framework_overhead_tokens": 1000,
                    "initial_implementation_loc": 350,
                    "rework_lines_modified_or_deleted": 10,
                    "rework_turn_count": 1
                },
                "product_design_and_ux": {"ux_state_completeness_score": 0.96},
                "architectural_fidelity": {"adherence_score": 95},
                "critical_assessment": {"net_utility_score": 5}
            }

            req1 = urllib.request.Request(
                f"http://127.0.0.1:{port}/api/v1/telemetry",
                data=json.dumps(p1).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req1, timeout=5) as resp:
                self.assertEqual(resp.status, 201)

            # 2. Ingest Tier A run for Claude Sonnet
            p2 = {
                "audit_metadata": {
                    "session_fingerprint": "fp_test_claude_01",
                    "schema_version": "2.0",
                    "evaluator_agent_model": "claude-3-5-sonnet"
                },
                "task_profile": {
                    "task_id": "T-02",
                    "task_description": "Worktree test",
                    "complexity_tier": "tier_3_complex",
                    "primary_subsystem": "worktree"
                },
                "quantitative_telemetry": {
                    "total_turns": 5,
                    "input_tokens_total": 50000,
                    "output_tokens_total": 10000,
                    "framework_overhead_tokens": 2000,
                    "initial_implementation_loc": 500,
                    "rework_lines_modified_or_deleted": 25,
                    "rework_turn_count": 1
                },
                "product_design_and_ux": {"ux_state_completeness_score": 0.92},
                "architectural_fidelity": {"adherence_score": 90},
                "critical_assessment": {"net_utility_score": 5}
            }

            req2 = urllib.request.Request(
                f"http://127.0.0.1:{port}/api/v1/telemetry",
                data=json.dumps(p2).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req2, timeout=5) as resp:
                self.assertEqual(resp.status, 201)

            # 3. Query stats endpoint
            url = f"http://127.0.0.1:{port}/api/v1/stats"
            with urllib.request.urlopen(url, timeout=5) as resp:
                self.assertEqual(resp.status, 200)
                stats = json.loads(resp.read().decode("utf-8"))

                self.assertEqual(stats["total_submissions"], 2)
                self.assertEqual(stats["qualified_tier_a_count"], 2)

                # Models breakdown check
                models = stats.get("models", [])
                self.assertEqual(len(models), 2)
                model_names = {m["model"] for m in models}
                self.assertIn("gemini-2-flash", model_names)
                self.assertIn("claude-3-5-sonnet", model_names)

                # Recent runs check
                recent = stats.get("recent_runs", [])
                self.assertEqual(len(recent), 2)
                self.assertEqual(recent[0]["model"], "claude-3-5-sonnet")
                self.assertEqual(recent[1]["model"], "gemini-2-flash")
                self.assertIn("rework_ratio_pct", recent[0])
                self.assertIn("project_hash", recent[0])

                # Enriched recent_runs fields
                self.assertIn("task_description", recent[0])
                self.assertIn("ux_completeness_pct", recent[0])
                self.assertIn("ui_touched", recent[0])
                self.assertEqual(recent[0]["task_description"], "Worktree test")
                self.assertEqual(recent[1]["task_description"], "Telemetry test")

                # evaluated_ui_tasks_count in summary
                self.assertIn("evaluated_ui_tasks_count", stats["summary"])

        finally:
            httpd.shutdown()
            httpd.server_close()


class TestUxCompletenessFiltering(unittest.TestCase):
    """Test that mean_ux_state_completeness_pct only averages tasks where ui_touched=1."""

    @classmethod
    def setUpClass(cls):
        import benchmarks.server as srv
        cls.srv = srv

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_ux_filter.db"
        self.prev_db = self.srv.DB_PATH
        self.srv.DB_PATH = self.db_path
        self.srv.init_database()

    def tearDown(self):
        self.srv.DB_PATH = self.prev_db
        self.temp_dir.cleanup()

    def _make_payload(self, fingerprint, model, ui_touched, ux_score, adherence=80):
        """Helper to create a minimal valid test payload."""
        return {
            "audit_metadata": {
                "session_fingerprint": fingerprint,
                "schema_version": "2.0",
                "evaluator_agent_model": model
            },
            "task_profile": {
                "task_id": f"T-{fingerprint}",
                "task_description": f"Test task {fingerprint}",
                "complexity_tier": "tier_2_medium",
                "primary_subsystem": "test"
            },
            "quantitative_telemetry": {
                "total_turns": 4,
                "input_tokens_total": 20000,
                "output_tokens_total": 5000,
                "framework_overhead_tokens": 500,
                "initial_implementation_loc": 200,
                "rework_lines_modified_or_deleted": 10,
                "rework_turn_count": 1
            },
            "product_design_and_ux": {
                "ui_components_touched": ui_touched,
                "ux_state_completeness_score": ux_score
            },
            "architectural_fidelity": {"adherence_score": adherence},
            "critical_assessment": {"net_utility_score": 4}
        }

    def test_ux_metric_filters_non_ui_tasks(self):
        """Backend-only tasks (ui_touched=0) must not drag down the UX average."""
        handler = self.srv.TelemetryRequestHandler
        httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
        port = httpd.server_port
        server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        server_thread.start()

        try:
            # Submit a UI task with ux_completeness=0.93
            p1 = self._make_payload("fp_ui_task_1", "gemini-2-flash", True, 0.93)
            req1 = urllib.request.Request(
                f"http://127.0.0.1:{port}/api/v1/telemetry",
                data=json.dumps(p1).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req1, timeout=5) as resp:
                self.assertEqual(resp.status, 201)

            # Submit a backend task with ux_completeness=0.0 (no UI)
            p2 = self._make_payload("fp_backend_task_1", "gemini-2-flash", False, 0.0)
            req2 = urllib.request.Request(
                f"http://127.0.0.1:{port}/api/v1/telemetry",
                data=json.dumps(p2).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req2, timeout=5) as resp:
                self.assertEqual(resp.status, 201)

            # Submit another UI task with ux_completeness=0.97
            p3 = self._make_payload("fp_ui_task_2", "claude-3-5-sonnet", True, 0.97)
            req3 = urllib.request.Request(
                f"http://127.0.0.1:{port}/api/v1/telemetry",
                data=json.dumps(p3).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req3, timeout=5) as resp:
                self.assertEqual(resp.status, 201)

            # Query stats — UX should average only the 2 UI tasks: (0.93 + 0.97) / 2 = 0.95 → 95.0%
            url = f"http://127.0.0.1:{port}/api/v1/stats"
            with urllib.request.urlopen(url, timeout=5) as resp:
                stats = json.loads(resp.read().decode("utf-8"))

                summary = stats["summary"]
                ux_pct = summary["mean_ux_state_completeness_pct"]
                ui_count = summary["evaluated_ui_tasks_count"]

                # Without filtering, this would be (0.93 + 0.0 + 0.97)/3 = 63.3%
                # With filtering, it should be (0.93 + 0.97)/2 = 95.0%
                self.assertEqual(ui_count, 2, "Only UI-touching tasks should be counted")
                self.assertAlmostEqual(ux_pct, 95.0, places=0,
                    msg=f"UX avg should be ~95.0% (UI tasks only), got {ux_pct}")

                # Total submissions should still be 3
                self.assertEqual(stats["total_submissions"], 3)

        finally:
            httpd.shutdown()
            httpd.server_close()

    def test_ux_metric_zero_ui_tasks(self):
        """When no UI tasks exist, UX completeness should be 0.0 with count 0."""
        handler = self.srv.TelemetryRequestHandler
        httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
        port = httpd.server_port
        server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        server_thread.start()

        try:
            # Submit only backend tasks
            p1 = self._make_payload("fp_no_ui_1", "gemini-2-flash", False, 0.0)
            req1 = urllib.request.Request(
                f"http://127.0.0.1:{port}/api/v1/telemetry",
                data=json.dumps(p1).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req1, timeout=5) as resp:
                self.assertEqual(resp.status, 201)

            url = f"http://127.0.0.1:{port}/api/v1/stats"
            with urllib.request.urlopen(url, timeout=5) as resp:
                stats = json.loads(resp.read().decode("utf-8"))
                summary = stats["summary"]
                self.assertEqual(summary["evaluated_ui_tasks_count"], 0)
                self.assertEqual(summary["mean_ux_state_completeness_pct"], 0.0)

        finally:
            httpd.shutdown()
            httpd.server_close()

    def test_recent_runs_enriched_fields(self):
        """Recent runs must include task_description, ux_completeness_pct, and ui_touched."""
        handler = self.srv.TelemetryRequestHandler
        httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
        port = httpd.server_port
        server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        server_thread.start()

        try:
            p1 = self._make_payload("fp_enrich_1", "gemini-2-flash", True, 0.88)
            req1 = urllib.request.Request(
                f"http://127.0.0.1:{port}/api/v1/telemetry",
                data=json.dumps(p1).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req1, timeout=5) as resp:
                self.assertEqual(resp.status, 201)

            url = f"http://127.0.0.1:{port}/api/v1/stats"
            with urllib.request.urlopen(url, timeout=5) as resp:
                stats = json.loads(resp.read().decode("utf-8"))
                recent = stats["recent_runs"]
                self.assertEqual(len(recent), 1)

                run = recent[0]
                self.assertEqual(run["task_description"], "Test task fp_enrich_1")
                self.assertAlmostEqual(run["ux_completeness_pct"], 88.0, places=0)
                self.assertTrue(run["ui_touched"])

        finally:
            httpd.shutdown()
            httpd.server_close()


class TestBenchmarkPortalPackageParity(unittest.TestCase):
    """Test suite verifying package data synchronization."""

    def test_benchmarks_package_parity(self):
        src_dir = REPO_ROOT / "templates" / "site" / "public" / "benchmarks"
        dst_dir = REPO_ROOT / "pxos" / "templates" / "site" / "public" / "benchmarks"

        self.assertTrue(dst_dir.exists(), "pxos/templates/site/public/benchmarks must exist")

        for f in ["index.html", "dashboard.css", "dashboard.js"]:
            src_f = src_dir / f
            dst_f = dst_dir / f
            self.assertTrue(dst_f.exists(), f"{dst_f} must exist in package data")
            src_bytes = src_f.read_bytes().replace(b"\r\n", b"\n")
            dst_bytes = dst_f.read_bytes().replace(b"\r\n", b"\n")
            self.assertEqual(src_bytes, dst_bytes, f"Parity mismatch in {f}")


if __name__ == "__main__":
    unittest.main()

