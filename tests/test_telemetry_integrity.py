#!/usr/bin/env python3
"""
Unit and Integration Tests for Telemetry Integrity, Verifiability & Anti-Poisoning Engine
========================================================================================
Validates cryptographic session fingerprinting, project anonymization, deterministic git
metric extraction, repository adherence scoring, server UPSERT idempotency, plausibility
guards, project-level rate limiting, and robust statistical filters (trimmed mean & IQR).
"""

import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from typing import Any, Dict

import importlib.util

from benchmarks import analyze, server

_script_path = Path(__file__).resolve().parent.parent / "scripts" / "pxos-benchmark.py"
_spec = importlib.util.spec_from_file_location("pxos_benchmark", _script_path)
pxos_benchmark = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pxos_benchmark)


class TestTelemetryIntegrityEngine(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.test_path = Path(self.test_dir.name)

    def tearDown(self):
        self.test_dir.cleanup()

    # --------------------------------------------------------------------------
    # 1. Cryptographic Anonymization & Session Fingerprint Idempotency
    # --------------------------------------------------------------------------

    def test_project_name_anonymization(self):
        raw_name = "ProprietaryCommercialFintechApp"
        anon_hash = pxos_benchmark.anonymize_project_name(raw_name)
        self.assertEqual(len(anon_hash), 16)
        self.assertNotIn("Proprietary", anon_hash)
        self.assertNotIn("Fintech", anon_hash)
        # Deterministic
        self.assertEqual(anon_hash, pxos_benchmark.anonymize_project_name(raw_name))

    def test_session_fingerprint_determinism(self):
        fp1 = pxos_benchmark.generate_session_fingerprint("salt123", "roothash456", "feat/auth", "T-01")
        fp2 = pxos_benchmark.generate_session_fingerprint("salt123", "roothash456", "feat/auth", "T-01")
        fp_diff = pxos_benchmark.generate_session_fingerprint("salt123", "roothash456", "feat/billing", "T-02")

        self.assertEqual(fp1, fp2)
        self.assertEqual(len(fp1), 64)
        self.assertNotEqual(fp1, fp_diff)

    # --------------------------------------------------------------------------
    # 2. Methodological Adherence Scoring & Qualification Tiers
    # --------------------------------------------------------------------------

    def test_adherence_scoring_empty_repo(self):
        # Empty repo should be Tier C (< 40 pts)
        score, tier, is_qualified, breakdown = pxos_benchmark.calculate_adherence_score(self.test_path)
        self.assertLess(score, 40)
        self.assertEqual(tier, "tier_c_noise")
        self.assertFalse(is_qualified)

    def test_adherence_scoring_rigorous_repo(self):
        # Create full PXOS structure
        ai_dir = self.test_path / ".ai"
        ai_dir.mkdir(parents=True, exist_ok=True)
        specs_dir = ai_dir / "specs"
        specs_dir.mkdir(parents=True, exist_ok=True)

        # 1. Context
        ctx_file = ai_dir / "PROJECT_CONTEXT.md"
        ctx_file.write_text("# Project Context\n<!-- pxos:version 2.4.0 -->\nCritical invariants:\n- INV-001: Privacy\n" * 5, encoding="utf-8")

        # 2. Spec
        spec_file = specs_dir / "SPEC-auth.md"
        spec_file.write_text("# Spec — Auth\n## Goal\nImplement OAuth.\n## User value\nSecure logins.\n" * 10, encoding="utf-8")

        # 3. Decision Log
        dec_file = ai_dir / "DECISION_LOG.md"
        dec_file.write_text("# Decision Log\n## ADR-001: SQLite WAL mode.\n" * 10, encoding="utf-8")

        score, tier, is_qualified, breakdown = pxos_benchmark.calculate_adherence_score(self.test_path)
        self.assertGreaterEqual(score, 65)  # 20 + 25 + 20 = 65 (without git history)
        self.assertEqual(breakdown["project_context_declared"], 20)
        self.assertEqual(breakdown["task_spec_grounding"], 25)
        self.assertEqual(breakdown["architectural_tracking"], 20)

    # --------------------------------------------------------------------------
    # 3. Server Plausibility Validation & Anti-Spoofing
    # --------------------------------------------------------------------------

    def test_plausibility_zero_rework_with_rework_turns(self):
        payload = {
            "audit_metadata": {"evaluation_mode": "retrospective"},
            "task_profile": {"task_id": "T-01", "complexity_tier": "tier_2_medium"},
            "quantitative_telemetry": {
                "total_turns": 5,
                "input_tokens_total": 10000,
                "output_tokens_total": 2000,
                "framework_overhead_tokens": 500,
                "initial_implementation_loc": 200,
                "rework_lines_modified_or_deleted": 0,  # 0 LOC
                "rework_turn_count": 2                  # but 2 rework turns!
            },
            "product_design_and_ux": {},
            "architectural_fidelity": {"adherence_score": 80},
            "critical_assessment": {}
        }
        valid, err, _ = server.validate_and_sanitize_payload(payload)
        self.assertFalse(valid)
        self.assertIn("Plausibility violation", err)

    def test_plausibility_active_turns_with_zero_tokens(self):
        payload = {
            "audit_metadata": {"evaluation_mode": "retrospective"},
            "task_profile": {"task_id": "T-01", "complexity_tier": "tier_2_medium"},
            "quantitative_telemetry": {
                "total_turns": 8,
                "input_tokens_total": 0,  # 0 tokens with 8 turns!
                "output_tokens_total": 0,
                "initial_implementation_loc": 100,
                "rework_lines_modified_or_deleted": 0,
                "rework_turn_count": 0
            },
            "product_design_and_ux": {},
            "architectural_fidelity": {"adherence_score": 80},
            "critical_assessment": {}
        }
        valid, err, _ = server.validate_and_sanitize_payload(payload)
        self.assertFalse(valid)
        self.assertIn("active turns recorded but 0 tokens", err)

    def test_plausibility_abnormal_token_to_turn_ratio(self):
        payload = {
            "audit_metadata": {"evaluation_mode": "retrospective"},
            "task_profile": {"task_id": "T-01", "complexity_tier": "tier_2_medium"},
            "quantitative_telemetry": {
                "total_turns": 10,
                "input_tokens_total": 20,  # 20 tokens across 10 turns (2 tokens/turn)
                "output_tokens_total": 10,
                "initial_implementation_loc": 100,
                "rework_lines_modified_or_deleted": 0,
                "rework_turn_count": 0
            },
            "product_design_and_ux": {},
            "architectural_fidelity": {"adherence_score": 80},
            "critical_assessment": {}
        }
        valid, err, _ = server.validate_and_sanitize_payload(payload)
        self.assertFalse(valid)
        self.assertIn("token consumption abnormally low", err)

    # --------------------------------------------------------------------------
    # 4. Project-Level Rate Limiter
    # --------------------------------------------------------------------------

    def test_project_rate_limiter(self):
        project_hash = "proj_test_quota_123"
        with server.PROJECT_RATE_LIMIT_LOCK:
            server.PROJECT_REQUEST_HISTORY.clear()

        for i in range(server.MAX_PROJECT_SUBMISSIONS_PER_DAY):
            self.assertFalse(server.is_project_rate_limited(project_hash))

        # 11th request should be throttled
        self.assertTrue(server.is_project_rate_limited(project_hash))

    # --------------------------------------------------------------------------
    # 5. SQLite UPSERT & Idempotency
    # --------------------------------------------------------------------------

    def test_database_upsert_idempotency(self):
        db_file = self.test_path / "test_upsert.db"
        server.DB_PATH = db_file
        server.init_database()

        conn = sqlite3.connect(db_file)
        cur = conn.cursor()

        payload = {
            "audit_metadata": {
                "schema_version": "2.0",
                "session_fingerprint": "abc123unique_fingerprint",
                "project_name": "TestApp",
                "evaluator_agent_model": "test-model"
            },
            "task_profile": {
                "task_id": "T-01",
                "task_description": "Initial task attempt",
                "complexity_tier": "tier_2_medium"
            },
            "quantitative_telemetry": {
                "total_turns": 4,
                "input_tokens_total": 10000,
                "output_tokens_total": 2500,
                "framework_overhead_tokens": 500,
                "initial_implementation_loc": 150,
                "rework_lines_modified_or_deleted": 15,
                "rework_turn_count": 1
            },
            "product_design_and_ux": {"ux_state_completeness_score": 0.8},
            "architectural_fidelity": {"adherence_score": 85},
            "critical_assessment": {"net_utility_score": 4}
        }

        # 1. First Ingestion
        valid, _, sanitized1 = server.validate_and_sanitize_payload(payload)
        self.assertTrue(valid)

        cur.execute("""
            INSERT INTO submissions (
                session_fingerprint, schema_version, project_hash, adherence_score,
                qualification_tier, is_qualified, client_ip, evaluation_mode, project_name,
                model, task_id, task_description, complexity_tier, primary_subsystem,
                total_turns, input_tokens, output_tokens, framework_overhead_tokens,
                initial_loc, rework_loc, rework_turns, compiler_failures, merge_conflicts,
                ui_touched, ux_completeness, design_tokens_adhered, session_amnesia,
                invariants_violated, duplicate_utils, adrs_consulted, new_adrs,
                net_utility_score, overhead_justified, raw_payload
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            sanitized1["session_fingerprint"], sanitized1["schema_version"], sanitized1["project_hash"],
            sanitized1["adherence_score"], sanitized1["qualification_tier"], sanitized1["is_qualified"],
            "127.0.0.1", sanitized1["evaluation_mode"], sanitized1["project_name"], sanitized1["model"],
            sanitized1["task_id"], sanitized1["task_description"], sanitized1["complexity_tier"],
            sanitized1["primary_subsystem"], sanitized1["total_turns"], sanitized1["input_tokens"],
            sanitized1["output_tokens"], sanitized1["framework_overhead_tokens"], sanitized1["initial_loc"],
            sanitized1["rework_loc"], sanitized1["rework_turns"], 0, 0, 0, 0.8, 1, 0, 0, 0, 0, 0, 4, 1, "{}"
        ))
        conn.commit()

        cur.execute("SELECT COUNT(*) FROM submissions")
        self.assertEqual(cur.fetchone()[0], 1)

        # 2. Second Ingestion with SAME session_fingerprint but updated description and tokens
        payload["task_profile"]["task_description"] = "Refined task attempt"
        payload["quantitative_telemetry"]["input_tokens_total"] = 12000
        _, _, sanitized2 = server.validate_and_sanitize_payload(payload)

        cur.execute("""
            INSERT INTO submissions (
                session_fingerprint, schema_version, project_hash, adherence_score,
                qualification_tier, is_qualified, client_ip, evaluation_mode, project_name,
                model, task_id, task_description, complexity_tier, primary_subsystem,
                total_turns, input_tokens, output_tokens, framework_overhead_tokens,
                initial_loc, rework_loc, rework_turns, compiler_failures, merge_conflicts,
                ui_touched, ux_completeness, design_tokens_adhered, session_amnesia,
                invariants_violated, duplicate_utils, adrs_consulted, new_adrs,
                net_utility_score, overhead_justified, raw_payload
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(session_fingerprint) DO UPDATE SET
                received_at = CURRENT_TIMESTAMP,
                task_description = excluded.task_description,
                input_tokens = excluded.input_tokens
        """, (
            sanitized2["session_fingerprint"], sanitized2["schema_version"], sanitized2["project_hash"],
            sanitized2["adherence_score"], sanitized2["qualification_tier"], sanitized2["is_qualified"],
            "127.0.0.1", sanitized2["evaluation_mode"], sanitized2["project_name"], sanitized2["model"],
            sanitized2["task_id"], sanitized2["task_description"], sanitized2["complexity_tier"],
            sanitized2["primary_subsystem"], sanitized2["total_turns"], sanitized2["input_tokens"],
            sanitized2["output_tokens"], sanitized2["framework_overhead_tokens"], sanitized2["initial_loc"],
            sanitized2["rework_loc"], sanitized2["rework_turns"], 0, 0, 0, 0.8, 1, 0, 0, 0, 0, 0, 4, 1, "{}"
        ))
        conn.commit()

        # Must still be exactly 1 row!
        cur.execute("SELECT COUNT(*) FROM submissions")
        self.assertEqual(cur.fetchone()[0], 1)

        # Fields must be updated!
        cur.execute("SELECT task_description, input_tokens FROM submissions WHERE session_fingerprint = ?", (sanitized1["session_fingerprint"],))
        updated_row = cur.fetchone()
        self.assertEqual(updated_row[0], "Refined task attempt")
        self.assertEqual(updated_row[1], 12000)

        conn.close()

    # --------------------------------------------------------------------------
    # 6. Robust Statistical Filters (Trimmed Mean & IQR Outliers)
    # --------------------------------------------------------------------------

    def test_trimmed_mean(self):
        # 20 numbers: 1 to 20. 5% trim trims 1 from each end (1 and 20)
        data = list(range(1, 21))
        # untrimmed mean is 10.5
        # trimmed data: 2 to 19 -> mean is still 10.5
        t_mean = analyze.calculate_trimmed_mean(data, 0.05)
        self.assertEqual(t_mean, 10.5)

        # Extreme outlier sensitivity
        data_with_outlier = [10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 1000.0]
        # Trimmed mean removes the 1000.0
        t_mean_outlier = analyze.calculate_trimmed_mean(data_with_outlier, 0.10)
        self.assertEqual(t_mean_outlier, 10.0)

    def test_iqr_outlier_detection(self):
        # Normal cluster around 10, with one massive outlier at 100
        normal_cluster = [10.0, 10.2, 9.8, 10.1, 10.0, 9.9, 10.3, 10.0, 10.1, 100.0]
        lower, upper, iqr, outliers = analyze.calculate_iqr_bounds(normal_cluster)

        self.assertIn(100.0, outliers)
        self.assertEqual(len(outliers), 1)
        self.assertLess(upper, 100.0)

    def test_descriptive_stats_structure(self):
        sample = [12.0, 14.0, 15.0, 16.0, 18.0, 20.0, 22.0, 200.0]
        stats = analyze.calculate_descriptive_stats(sample)

        self.assertIn("mean", stats)
        self.assertIn("median", stats)
        self.assertIn("trimmed_mean_5pct", stats)
        self.assertIn("iqr", stats)
        self.assertIn("outliers_count", stats)
    def test_end_to_end_http_server(self):
        import http.server
        import threading
        import urllib.request

        db_file = self.test_path / "test_http.db"
        server.DB_PATH = db_file
        server.init_database()

        httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), server.TelemetryRequestHandler)
        port = httpd.server_port
        t = threading.Thread(target=httpd.serve_forever, daemon=True)
        t.start()

        try:
            url = f"http://127.0.0.1:{port}/api/v1/telemetry"
            payload = {
                "audit_metadata": {
                    "schema_version": "2.0",
                    "session_fingerprint": "fp_http_test_12345",
                    "project_name": "TestHttpApp",
                    "evaluator_agent_model": "test-agent"
                },
                "task_profile": {
                    "task_id": "T-08",
                    "task_description": "Verifiability engine test",
                    "complexity_tier": "tier_2_medium"
                },
                "quantitative_telemetry": {
                    "total_turns": 6,
                    "input_tokens_total": 20000,
                    "output_tokens_total": 5000,
                    "framework_overhead_tokens": 1000,
                    "initial_implementation_loc": 300,
                    "rework_lines_modified_or_deleted": 20,
                    "rework_turn_count": 1
                },
                "product_design_and_ux": {"ux_state_completeness_score": 0.95},
                "architectural_fidelity": {"adherence_score": 90},
                "critical_assessment": {"net_utility_score": 5}
            }

            # 1. First submission
            req1 = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req1, timeout=5) as resp:
                self.assertEqual(resp.status, 201)
                data1 = json.loads(resp.read().decode("utf-8"))
                self.assertEqual(data1["qualification_tier"], "tier_a_rigor")
                self.assertTrue(data1["is_qualified"])
                self.assertEqual(data1["session_fingerprint"], "fp_http_test_12345")

            # 2. Second submission with identical session_fingerprint (testing UPSERT)
            payload["task_profile"]["task_description"] = "Updated verifiability test"
            req2 = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req2, timeout=5) as resp:
                self.assertEqual(resp.status, 201)
                data2 = json.loads(resp.read().decode("utf-8"))
                self.assertEqual(data2["submission_id"], data1["submission_id"])

            # 3. Query Stats endpoint
            stats_url = f"http://127.0.0.1:{port}/api/v1/stats"
            with urllib.request.urlopen(stats_url, timeout=5) as resp:
                self.assertEqual(resp.status, 200)
                stats = json.loads(resp.read().decode("utf-8"))
                self.assertEqual(stats["total_submissions"], 1)
                self.assertEqual(stats["qualified_tier_a_count"], 1)
                self.assertEqual(stats["qualification_scope"], "tier_a_verified")
                self.assertEqual(stats["submissions_by_qualification_tier"]["tier_a_rigor"], 1)

        finally:
            httpd.shutdown()
            httpd.server_close()


if __name__ == "__main__":
    unittest.main()

