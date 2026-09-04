#!/usr/bin/env python3
"""
PXOS Telemetry & Benchmark Ingestion Server
===========================================
A lightweight, zero-dependency server that ingests, validates, sanitizes,
and stores anonymous empirical benchmark telemetry from PXOS agents.

Endpoints:
    POST /api/v1/telemetry  - Ingest an audited benchmark JSON payload
    GET  /api/v1/stats      - Public aggregated statistics
    GET  /api/v1/health     - Service health check
"""

import http.server
import json
import os
import sqlite3
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

PORT = int(os.environ.get("PORT", "8090"))
DB_PATH = Path(os.environ.get("DB_PATH", "/opt/pxos-telemetry/data/telemetry.db"))
MAX_PAYLOAD_BYTES = 65536  # 64 KB

DB_LOCK = threading.Lock()

VALID_COMPLEXITY_TIERS = {"tier_1_micro", "tier_2_medium", "tier_3_complex"}
VALID_MODES = {"retrospective", "controlled_ab", "unknown"}


def init_database():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with DB_LOCK:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("PRAGMA journal_mode=WAL;")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                client_ip TEXT,
                evaluation_mode TEXT,
                project_name TEXT,
                model TEXT,
                task_id TEXT,
                task_description TEXT,
                complexity_tier TEXT,
                primary_subsystem TEXT,
                total_turns INTEGER,
                input_tokens INTEGER,
                output_tokens INTEGER,
                framework_overhead_tokens INTEGER,
                initial_loc INTEGER,
                rework_loc INTEGER,
                rework_turns INTEGER,
                compiler_failures INTEGER,
                merge_conflicts INTEGER,
                ui_touched INTEGER,
                ux_completeness REAL,
                design_tokens_adhered INTEGER,
                session_amnesia INTEGER,
                invariants_violated INTEGER,
                duplicate_utils INTEGER,
                adrs_consulted INTEGER,
                new_adrs INTEGER,
                net_utility_score INTEGER,
                overhead_justified INTEGER,
                verified_status TEXT DEFAULT 'community',
                raw_payload JSON
            );
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_tier ON submissions(complexity_tier);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_mode ON submissions(evaluation_mode);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_status ON submissions(verified_status);")
        conn.commit()
        conn.close()


def validate_and_sanitize_payload(data: Dict[str, Any]) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
    if not isinstance(data, dict):
        return False, "Payload must be a JSON object", None

    meta = data.get("audit_metadata", {})
    task = data.get("task_profile", {})
    telemetry = data.get("quantitative_telemetry", {})
    ux = data.get("product_design_and_ux", {})
    arch = data.get("architectural_fidelity", {})
    crit = data.get("critical_assessment", {})

    mode = str(meta.get("evaluation_mode", "unknown")).lower()
    if mode not in VALID_MODES:
        mode = "unknown"

    tier = str(task.get("complexity_tier", "tier_2_medium")).lower()
    if tier not in VALID_COMPLEXITY_TIERS:
        tier = "tier_2_medium"

    try:
        total_turns = int(telemetry.get("total_turns", 0))
        input_tokens = int(telemetry.get("input_tokens_total", 0))
        output_tokens = int(telemetry.get("output_tokens_total", 0))
        overhead_tokens = int(telemetry.get("framework_overhead_tokens", 0))
        initial_loc = int(telemetry.get("initial_implementation_loc", 0))
        rework_loc = int(telemetry.get("rework_lines_modified_or_deleted", 0))
        rework_turns = int(telemetry.get("rework_turn_count", 0))
        compiler_failures = int(telemetry.get("unresolved_compiler_or_test_failures", 0))
        merge_conflicts = int(telemetry.get("merge_conflicts_encountered", 0))
        ux_completeness = float(ux.get("ux_state_completeness_score", 0.0))
        net_utility_score = int(crit.get("net_utility_score", 0))

        # Sanity range constraints
        if not (0 <= total_turns <= 1000):
            return False, "total_turns out of reasonable bounds (0-1000)", None
        if not (0 <= input_tokens <= 10_000_000):
            return False, "input_tokens out of reasonable bounds (0-10M)", None
        if not (0 <= output_tokens <= 2_000_000):
            return False, "output_tokens out of reasonable bounds (0-2M)", None
        if not (0.0 <= ux_completeness <= 1.0):
            return False, "ux_state_completeness_score must be between 0.0 and 1.0", None
        if not (-5 <= net_utility_score <= 5):
            return False, "net_utility_score must be between -5 and 5", None

    except (ValueError, TypeError) as e:
        return False, f"Type validation error in numeric telemetry: {e}", None

    sanitized = {
        "evaluation_mode": mode,
        "project_name": str(meta.get("project_name", "anonymous"))[:64],
        "model": str(meta.get("evaluator_agent_model", "unknown"))[:64],
        "task_id": str(task.get("task_id", "unknown"))[:32],
        "task_description": str(task.get("task_description", ""))[:256],
        "complexity_tier": tier,
        "primary_subsystem": str(task.get("primary_subsystem", "general"))[:64],
        "total_turns": total_turns,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "framework_overhead_tokens": overhead_tokens,
        "initial_loc": initial_loc,
        "rework_loc": rework_loc,
        "rework_turns": rework_turns,
        "compiler_failures": compiler_failures,
        "merge_conflicts": merge_conflicts,
        "ui_touched": 1 if ux.get("ui_components_touched") else 0,
        "ux_completeness": round(ux_completeness, 3),
        "design_tokens_adhered": 1 if ux.get("design_tokens_adhered", True) else 0,
        "session_amnesia": 1 if arch.get("session_amnesia_occurred") else 0,
        "invariants_violated": int(arch.get("invariants_violated_count", 0)),
        "duplicate_utils": int(arch.get("duplicate_utilities_introduced", 0)),
        "adrs_consulted": int(arch.get("adrs_consulted_count", 0)),
        "new_adrs": int(arch.get("new_adrs_registered", 0)),
        "net_utility_score": net_utility_score,
        "overhead_justified": 1 if crit.get("overhead_justified", True) else 0,
        "raw_payload": json.dumps(data)
    }

    return True, None, sanitized


class TelemetryRequestHandler(http.server.BaseHTTPRequestHandler):
    server_version = "PXOS-Telemetry/1.0.0"

    def send_json(self, status_code: int, payload: Dict[str, Any]):
        response_bytes = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, User-Agent")
        self.end_headers()
        self.wfile.write(response_bytes)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, User-Agent")
        self.end_headers()

    def do_GET(self):
        path = self.path.split("?")[0].rstrip("/")

        if path == "/api/v1/health":
            self.send_json(200, {
                "status": "healthy",
                "service": "pxos-telemetry-server",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            return

        if path == "/api/v1/stats":
            with DB_LOCK:
                conn = sqlite3.connect(DB_PATH)
                cur = conn.cursor()
                cur.execute("""
                    SELECT 
                        COUNT(*),
                        AVG(total_turns),
                        AVG(input_tokens + output_tokens),
                        AVG(framework_overhead_tokens),
                        AVG(rework_loc),
                        AVG(initial_loc),
                        AVG(ux_completeness),
                        AVG(overhead_justified)
                    FROM submissions
                """)
                row = cur.fetchone()
                total_submissions = row[0] or 0
                if total_submissions == 0:
                    conn.close()
                    self.send_json(200, {
                        "total_submissions": 0,
                        "message": "No submissions recorded yet."
                    })
                    return

                avg_turns = round(row[1] or 0.0, 1)
                avg_total_tokens = round(row[2] or 0.0, 1)
                avg_overhead = round(row[3] or 0.0, 1)
                avg_rework = round(row[4] or 0.0, 1)
                avg_initial_loc = round(row[5] or 1.0, 1)
                avg_ux = round((row[6] or 0.0) * 100, 1)
                overhead_justified_pct = round((row[7] or 0.0) * 100, 1)
                rework_ratio_pct = round((avg_rework / max(1.0, avg_initial_loc)) * 100, 1)

                cur.execute("SELECT complexity_tier, COUNT(*) FROM submissions GROUP BY complexity_tier")
                tier_counts = dict(cur.fetchall())
                conn.close()

            self.send_json(200, {
                "total_submissions": total_submissions,
                "summary": {
                    "mean_total_tokens": avg_total_tokens,
                    "mean_framework_overhead_tokens": avg_overhead,
                    "mean_rework_ratio_pct": rework_ratio_pct,
                    "mean_ux_state_completeness_pct": avg_ux,
                    "overhead_justified_rate_pct": overhead_justified_pct,
                    "mean_turns_per_task": avg_turns,
                },
                "submissions_by_tier": tier_counts,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            return

        self.send_json(404, {"error": "Endpoint not found"})

    def do_POST(self):
        path = self.path.split("?")[0].rstrip("/")
        if path != "/api/v1/telemetry":
            self.send_json(404, {"error": "Endpoint not found"})
            return

        content_length_str = self.headers.get("Content-Length")
        if not content_length_str:
            self.send_json(411, {"error": "Content-Length required"})
            return

        try:
            content_length = int(content_length_str)
        except ValueError:
            self.send_json(400, {"error": "Invalid Content-Length"})
            return

        if content_length > MAX_PAYLOAD_BYTES:
            self.send_json(413, {
                "error": f"Payload too large. Maximum allowed size is {MAX_PAYLOAD_BYTES} bytes."
            })
            return

        try:
            body = self.rfile.read(content_length)
            data = json.loads(body.decode("utf-8"))
        except Exception as e:
            self.send_json(400, {"error": f"Invalid JSON payload: {e}"})
            return

        is_valid, err_msg, sanitized = validate_and_sanitize_payload(data)
        if not is_valid or not sanitized:
            self.send_json(422, {"error": f"Validation failed: {err_msg}"})
            return

        client_ip = self.headers.get("X-Forwarded-For", self.client_address[0]).split(",")[0].strip()

        with DB_LOCK:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO submissions (
                    client_ip, evaluation_mode, project_name, model, task_id, task_description,
                    complexity_tier, primary_subsystem, total_turns, input_tokens, output_tokens,
                    framework_overhead_tokens, initial_loc, rework_loc, rework_turns,
                    compiler_failures, merge_conflicts, ui_touched, ux_completeness,
                    design_tokens_adhered, session_amnesia, invariants_violated, duplicate_utils,
                    adrs_consulted, new_adrs, net_utility_score, overhead_justified, raw_payload
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
            """, (
                client_ip, sanitized["evaluation_mode"], sanitized["project_name"], sanitized["model"],
                sanitized["task_id"], sanitized["task_description"], sanitized["complexity_tier"],
                sanitized["primary_subsystem"], sanitized["total_turns"], sanitized["input_tokens"],
                sanitized["output_tokens"], sanitized["framework_overhead_tokens"], sanitized["initial_loc"],
                sanitized["rework_loc"], sanitized["rework_turns"], sanitized["compiler_failures"],
                sanitized["merge_conflicts"], sanitized["ui_touched"], sanitized["ux_completeness"],
                sanitized["design_tokens_adhered"], sanitized["session_amnesia"],
                sanitized["invariants_violated"], sanitized["duplicate_utils"], sanitized["adrs_consulted"],
                sanitized["new_adrs"], sanitized["net_utility_score"], sanitized["overhead_justified"],
                sanitized["raw_payload"]
            ))
            row_id = cur.lastrowid
            conn.commit()
            conn.close()

        print(f"[{datetime.now(timezone.utc).isoformat()}] Ingested benchmark #{row_id} from {client_ip} (Tier: {sanitized['complexity_tier']}, Model: {sanitized['model']})")

        self.send_json(201, {
            "status": "accepted",
            "submission_id": row_id,
            "message": "Anonymous empirical benchmark telemetry stored successfully."
        })


def run_server():
    init_database()
    server_address = ("127.0.0.1", PORT)
    httpd = http.server.ThreadingHTTPServer(server_address, TelemetryRequestHandler)
    print(f"PXOS Telemetry Server listening on http://127.0.0.1:{PORT}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.server_close()


if __name__ == "__main__":
    run_server()
