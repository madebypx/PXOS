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

import hashlib
import http.server
import json
import os
import sqlite3
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import parse_qs, urlparse

HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", "8090"))
DB_PATH = Path(os.environ.get("DB_PATH", "/opt/pxos-telemetry/data/telemetry.db"))
MAX_PAYLOAD_BYTES = 65536  # 64 KB
DB_TIMEOUT_SECS = 30.0
DB_BUSY_TIMEOUT_MS = 5000

DB_LOCK = threading.Lock()
RATE_LIMIT_LOCK = threading.Lock()
RATE_LIMIT_WINDOW_SECS = 60.0
MAX_REQUESTS_PER_WINDOW = 20
MAX_TRACKED_IPS = 10000
IP_REQUEST_HISTORY: Dict[str, list] = {}
TRUSTED_PROXIES = {"127.0.0.1", "::1"}

PROJECT_RATE_LIMIT_LOCK = threading.Lock()
PROJECT_RATE_LIMIT_WINDOW_SECS = 86400.0  # 24 hours
MAX_PROJECT_SUBMISSIONS_PER_DAY = 10
MAX_TRACKED_PROJECTS = 10000
PROJECT_REQUEST_HISTORY: Dict[str, list] = {}

VALID_COMPLEXITY_TIERS = {"tier_1_micro", "tier_2_medium", "tier_3_complex"}
VALID_MODES = {"retrospective", "controlled_ab", "unknown"}
VALID_QUALIFICATION_TIERS = {"tier_a_rigor", "tier_b_partial", "tier_c_noise"}


def is_project_rate_limited(project_hash: str) -> bool:
    """Sliding-window rate limiter per project hash (max 10 submissions per 24 hours)."""
    if not project_hash:
        return False
    now = time.time()
    with PROJECT_RATE_LIMIT_LOCK:
        history = PROJECT_REQUEST_HISTORY.get(project_hash, [])
        valid_history = [t for t in history if now - t < PROJECT_RATE_LIMIT_WINDOW_SECS]

        # Periodic cleanup of stale projects
        if len(PROJECT_REQUEST_HISTORY) > 500:
            stale_keys = [
                k for k, timestamps in PROJECT_REQUEST_HISTORY.items()
                if not timestamps or (now - timestamps[-1] >= PROJECT_RATE_LIMIT_WINDOW_SECS)
            ]
            for stale_k in stale_keys:
                del PROJECT_REQUEST_HISTORY[stale_k]

        if len(PROJECT_REQUEST_HISTORY) >= MAX_TRACKED_PROJECTS:
            overflow = len(PROJECT_REQUEST_HISTORY) - MAX_TRACKED_PROJECTS + 50
            for k in list(PROJECT_REQUEST_HISTORY.keys())[:overflow]:
                del PROJECT_REQUEST_HISTORY[k]

        if len(valid_history) >= MAX_PROJECT_SUBMISSIONS_PER_DAY:
            PROJECT_REQUEST_HISTORY[project_hash] = valid_history
            return True

        valid_history.append(now)
        PROJECT_REQUEST_HISTORY[project_hash] = valid_history
        return False



def is_rate_limited(ip: str) -> bool:
    """Sliding-window in-memory rate limiter per client IP with active memory pruning."""
    now = time.time()
    with RATE_LIMIT_LOCK:
        # Prune stale timestamps for current IP
        history = IP_REQUEST_HISTORY.get(ip, [])
        valid_history = [t for t in history if now - t < RATE_LIMIT_WINDOW_SECS]

        # Periodic eviction of stale IPs if tracked dictionary expands
        if len(IP_REQUEST_HISTORY) > 500:
            stale_ips = [
                k for k, timestamps in IP_REQUEST_HISTORY.items()
                if not timestamps or (now - timestamps[-1] >= RATE_LIMIT_WINDOW_SECS)
            ]
            for stale_ip in stale_ips:
                del IP_REQUEST_HISTORY[stale_ip]

        # Capacity cap bounding: if still exceeding max capacity, evict oldest entries
        if len(IP_REQUEST_HISTORY) >= MAX_TRACKED_IPS:
            overflow = len(IP_REQUEST_HISTORY) - MAX_TRACKED_IPS + 50
            for k in list(IP_REQUEST_HISTORY.keys())[:overflow]:
                del IP_REQUEST_HISTORY[k]

        if len(valid_history) >= MAX_REQUESTS_PER_WINDOW:
            IP_REQUEST_HISTORY[ip] = valid_history
            return True

        valid_history.append(now)
        IP_REQUEST_HISTORY[ip] = valid_history
        return False


def get_db_connection() -> sqlite3.Connection:
    """Create a SQLite connection with busy_timeout pragma and configured timeout."""
    conn = sqlite3.connect(DB_PATH, timeout=DB_TIMEOUT_SECS)
    conn.execute(f"PRAGMA busy_timeout = {DB_BUSY_TIMEOUT_MS};")
    return conn


def init_database():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = None
    with DB_LOCK:
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("PRAGMA journal_mode=WAL;")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS submissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    session_fingerprint TEXT UNIQUE,
                    schema_version TEXT DEFAULT '2.0',
                    project_hash TEXT,
                    adherence_score INTEGER DEFAULT 0,
                    qualification_tier TEXT DEFAULT 'tier_c_noise',
                    is_qualified INTEGER DEFAULT 0,
                    git_tree_hash TEXT,
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

            # Dynamic column migration for existing tables
            cur.execute("PRAGMA table_info(submissions);")
            existing_cols = {row[1] for row in cur.fetchall()}
            migrations = [
                ("session_fingerprint", "TEXT"),
                ("schema_version", "TEXT DEFAULT '2.0'"),
                ("project_hash", "TEXT"),
                ("adherence_score", "INTEGER DEFAULT 0"),
                ("qualification_tier", "TEXT DEFAULT 'tier_c_noise'"),
                ("is_qualified", "INTEGER DEFAULT 0"),
                ("git_tree_hash", "TEXT"),
            ]
            for col_name, col_def in migrations:
                if col_name not in existing_cols:
                    try:
                        cur.execute(f"ALTER TABLE submissions ADD COLUMN {col_name} {col_def};")
                    except sqlite3.OperationalError:
                        pass

            cur.execute("CREATE INDEX IF NOT EXISTS idx_tier ON submissions(complexity_tier);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_mode ON submissions(evaluation_mode);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_status ON submissions(verified_status);")
            cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_fingerprint ON submissions(session_fingerprint);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_qualified ON submissions(is_qualified);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_project_hash ON submissions(project_hash);")
            conn.commit()
        finally:
            if conn:
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

    schema_version = str(meta.get("schema_version", "2.0")).strip()[:16]
    session_fingerprint = str(meta.get("session_fingerprint", "")).strip()[:64]
    git_tree_hash = str(meta.get("git_tree_hash", "")).strip()[:64]

    raw_project_name = str(meta.get("project_name", "anonymous"))[:64]
    project_hash = str(meta.get("project_hash", "")).strip()[:16]
    if not project_hash:
        project_hash = hashlib.sha256(raw_project_name.encode("utf-8")).hexdigest()[:16]

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
        invariants_violated = int(arch.get("invariants_violated_count", 0))
        duplicate_utils = int(arch.get("duplicate_utilities_introduced", 0))
        adrs_consulted = int(arch.get("adrs_consulted_count", 0))
        new_adrs = int(arch.get("new_adrs_registered", 0))
        adherence_score = int(arch.get("adherence_score", 0))

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
        if not (0 <= adherence_score <= 100):
            return False, "adherence_score must be between 0 and 100", None

        # Plausibility constraints & anti-spoofing guards
        if rework_turns > 0 and rework_loc == 0:
            return False, "Plausibility violation: rework_turn_count > 0 cannot have 0 rework LOC", None
        if total_turns > 0 and (input_tokens + output_tokens) == 0:
            return False, "Plausibility violation: active turns recorded but 0 tokens consumed", None
        if total_turns >= 5 and (input_tokens + output_tokens) / total_turns < 10:
            return False, "Plausibility violation: token consumption abnormally low for turn count", None
        if total_turns > 0 and initial_loc / max(1, total_turns) > 2000:
            return False, "Plausibility violation: throughput exceeds plausible human/agent threshold (>2000 LOC/turn)", None

    except (ValueError, TypeError) as e:
        return False, f"Type validation error in numeric telemetry: {e}", None

    # Derive qualification tier objectively based on adherence score
    if adherence_score >= 70:
        qualification_tier = "tier_a_rigor"
        is_qualified = 1
    elif adherence_score >= 40:
        qualification_tier = "tier_b_partial"
        is_qualified = 0
    else:
        qualification_tier = "tier_c_noise"
        is_qualified = 0

    # Scrub and construct schema-only payload representation to guarantee no PII or extra keys leak into DB
    sanitized_raw_dict = {
        "audit_metadata": {
            "schema_version": schema_version,
            "session_fingerprint": session_fingerprint,
            "project_hash": project_hash,
            "git_tree_hash": git_tree_hash,
            "evaluation_mode": mode,
            "project_name": raw_project_name,
            "evaluator_agent_model": str(meta.get("evaluator_agent_model", "unknown"))[:64],
            "timestamp_iso": str(meta.get("timestamp_iso", ""))[:32]
        },
        "task_profile": {
            "task_id": str(task.get("task_id", "unknown"))[:32],
            "task_description": str(task.get("task_description", ""))[:256],
            "complexity_tier": tier,
            "primary_subsystem": str(task.get("primary_subsystem", "general"))[:64]
        },
        "quantitative_telemetry": {
            "total_turns": total_turns,
            "input_tokens_total": input_tokens,
            "output_tokens_total": output_tokens,
            "framework_overhead_tokens": overhead_tokens,
            "initial_implementation_loc": initial_loc,
            "rework_lines_modified_or_deleted": rework_loc,
            "rework_turn_count": rework_turns,
            "unresolved_compiler_or_test_failures": compiler_failures,
            "merge_conflicts_encountered": merge_conflicts
        },
        "product_design_and_ux": {
            "ui_components_touched": 1 if ux.get("ui_components_touched") else 0,
            "ux_state_completeness_score": round(ux_completeness, 3),
            "design_tokens_adhered": 1 if ux.get("design_tokens_adhered", True) else 0
        },
        "architectural_fidelity": {
            "adherence_score": adherence_score,
            "qualification_tier": qualification_tier,
            "is_qualified": is_qualified,
            "session_amnesia_occurred": 1 if arch.get("session_amnesia_occurred") else 0,
            "invariants_violated_count": invariants_violated,
            "duplicate_utilities_introduced": duplicate_utils,
            "adrs_consulted_count": adrs_consulted,
            "new_adrs_registered": new_adrs
        },
        "critical_assessment": {
            "net_utility_score": net_utility_score,
            "overhead_justified": 1 if crit.get("overhead_justified", True) else 0
        }
    }

    sanitized = {
        "schema_version": schema_version,
        "session_fingerprint": session_fingerprint if session_fingerprint else None,
        "project_hash": project_hash,
        "adherence_score": adherence_score,
        "qualification_tier": qualification_tier,
        "is_qualified": is_qualified,
        "git_tree_hash": git_tree_hash,
        "evaluation_mode": mode,
        "project_name": raw_project_name,
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
        "invariants_violated": invariants_violated,
        "duplicate_utils": duplicate_utils,
        "adrs_consulted": adrs_consulted,
        "new_adrs": new_adrs,
        "net_utility_score": net_utility_score,
        "overhead_justified": 1 if crit.get("overhead_justified", True) else 0,
        "raw_payload": json.dumps(sanitized_raw_dict)
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
        parsed_url = urlparse(self.path)
        path = parsed_url.path.rstrip("/")
        query_params = parse_qs(parsed_url.query)

        if path == "/api/v1/health":
            self.send_json(200, {
                "status": "healthy",
                "service": "pxos-telemetry-server",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            return

        if path == "/api/v1/stats":
            conn = None
            try:
                with DB_LOCK:
                    conn = get_db_connection()
                    cur = conn.cursor()

                    cur.execute("SELECT COUNT(*) FROM submissions")
                    total_submissions = cur.fetchone()[0] or 0

                    if total_submissions == 0:
                        self.send_json(200, {
                            "total_submissions": 0,
                            "qualified_tier_a_count": 0,
                            "qualification_scope": "tier_a_verified",
                            "message": "No submissions recorded yet.",
                            "summary": {
                                "mean_total_tokens": 0.0,
                                "mean_framework_overhead_tokens": 0.0,
                                "mean_rework_ratio_pct": 0.0,
                                "mean_ux_state_completeness_pct": 0.0,
                                "evaluated_ui_tasks_count": 0,
                                "overhead_justified_rate_pct": 0.0,
                                "mean_turns_per_task": 0.0,
                                "mean_adherence_score": 0.0,
                            },
                            "models": [],
                            "recent_runs": [],
                            "submissions_by_tier": {},
                            "submissions_by_qualification_tier": {},
                            "timestamp": datetime.now(timezone.utc).isoformat()
                        })
                        return

                    # Check Tier A qualified submissions
                    cur.execute("SELECT COUNT(*) FROM submissions WHERE is_qualified = 1")
                    qualified_tier_a_count = cur.fetchone()[0] or 0

                    tier_req = query_params.get("tier", ["a"])[0].lower()
                    if tier_req == "all":
                        filter_clause = ""
                        scope = "all_exploratory"
                    else:
                        filter_clause = "WHERE is_qualified = 1" if qualified_tier_a_count > 0 else ""
                        scope = "tier_a_verified" if qualified_tier_a_count > 0 else "all_exploratory"

                    cur.execute(f"""
                        SELECT 
                            COUNT(*),
                            AVG(total_turns),
                            AVG(input_tokens + output_tokens),
                            AVG(framework_overhead_tokens),
                            AVG(rework_loc),
                            AVG(initial_loc),
                            AVG(overhead_justified),
                            AVG(adherence_score)
                        FROM submissions
                        {filter_clause}
                    """)
                    row = cur.fetchone()

                    avg_turns = round(row[1] or 0.0, 1)
                    avg_total_tokens = round(row[2] or 0.0, 1)
                    avg_overhead = round(row[3] or 0.0, 1)
                    avg_rework = round(row[4] or 0.0, 1)
                    avg_initial_loc = round(row[5] or 1.0, 1)
                    overhead_justified_pct = round((row[6] or 0.0) * 100, 1)
                    rework_ratio_pct = round((avg_rework / max(1.0, avg_initial_loc)) * 100, 1)
                    avg_adherence = round(row[7] or 0.0, 1)

                    # UX Completeness: filter to UI-touching tasks only (matches analyze.py behavior)
                    ui_filter = "ui_touched = 1"
                    if filter_clause:
                        ui_filter_clause = f"{filter_clause} AND {ui_filter}"
                    else:
                        ui_filter_clause = f"WHERE {ui_filter}"
                    cur.execute(f"""
                        SELECT AVG(ux_completeness), COUNT(*)
                        FROM submissions
                        {ui_filter_clause}
                    """)
                    ux_row = cur.fetchone()
                    avg_ux = round((ux_row[0] or 0.0) * 100, 1)
                    evaluated_ui_tasks_count = ux_row[1] or 0

                    # Model comparative aggregates
                    cur.execute(f"""
                        SELECT 
                            model,
                            COUNT(*),
                            AVG(input_tokens + output_tokens),
                            AVG(initial_loc),
                            AVG(rework_loc),
                            AVG(ux_completeness),
                            AVG(adherence_score),
                            AVG(net_utility_score)
                        FROM submissions
                        {filter_clause}
                        GROUP BY model
                        ORDER BY COUNT(*) DESC
                    """)
                    models_list = []
                    for m in cur.fetchall():
                        m_model = m[0] or "unknown"
                        m_count = m[1] or 0
                        m_tokens = round(m[2] or 0.0, 1)
                        m_init = round(m[3] or 1.0, 1)
                        m_rework = round(m[4] or 0.0, 1)
                        m_ratio = round((m_rework / max(1.0, m_init)) * 100, 1)
                        m_tok_per_loc = round(m_tokens / max(1.0, m_init), 1)
                        m_ux_pct = round((m[5] or 0.0) * 100, 1)
                        m_adh = round(m[6] or 0.0, 1)
                        m_util = round(m[7] or 0.0, 1)

                        models_list.append({
                            "model": m_model,
                            "run_count": m_count,
                            "mean_total_tokens": m_tokens,
                            "tokens_per_loc": m_tok_per_loc,
                            "rework_ratio_pct": m_ratio,
                            "ux_completeness_pct": m_ux_pct,
                            "adherence_score": m_adh,
                            "net_utility_score": m_util
                        })

                    # Recent anonymized verified runs
                    cur.execute(f"""
                        SELECT 
                            received_at,
                            model,
                            primary_subsystem,
                            complexity_tier,
                            initial_loc,
                            rework_loc,
                            total_turns,
                            input_tokens + output_tokens,
                            adherence_score,
                            qualification_tier,
                            is_qualified,
                            project_hash,
                            task_description,
                            ux_completeness,
                            ui_touched
                        FROM submissions
                        {filter_clause}
                        ORDER BY id DESC
                        LIMIT 25
                    """)
                    recent_runs_list = []
                    for r in cur.fetchall():
                        r_init = r[4] or 0
                        r_rework = r[5] or 0
                        r_ratio = round((r_rework / max(1.0, float(r_init))) * 100, 1)
                        recent_runs_list.append({
                            "timestamp": r[0],
                            "model": r[1] or "unknown",
                            "primary_subsystem": r[2] or "general",
                            "complexity_tier": r[3] or "tier_2_medium",
                            "initial_loc": r_init,
                            "rework_loc": r_rework,
                            "rework_ratio_pct": r_ratio,
                            "total_turns": r[6] or 0,
                            "total_tokens": r[7] or 0,
                            "adherence_score": r[8] or 0,
                            "qualification_tier": r[9] or "tier_c_noise",
                            "is_qualified": bool(r[10]),
                            "project_hash": (r[11] or "")[:12],
                            "task_description": r[12] or "",
                            "ux_completeness_pct": round((r[13] or 0.0) * 100, 1),
                            "ui_touched": bool(r[14])
                        })

                    cur.execute("SELECT complexity_tier, COUNT(*) FROM submissions GROUP BY complexity_tier")
                    tier_counts = dict(cur.fetchall())

                    cur.execute("SELECT qualification_tier, COUNT(*) FROM submissions GROUP BY qualification_tier")
                    qualification_counts = dict(cur.fetchall())
            except sqlite3.Error as e:
                self.send_json(500, {"error": f"Database query failed: {e}"})
                return
            finally:
                if conn:
                    conn.close()

            self.send_json(200, {
                "total_submissions": total_submissions,
                "qualified_tier_a_count": qualified_tier_a_count,
                "qualification_scope": scope,
                "summary": {
                    "mean_total_tokens": avg_total_tokens,
                    "mean_framework_overhead_tokens": avg_overhead,
                    "mean_rework_ratio_pct": rework_ratio_pct,
                    "mean_ux_state_completeness_pct": avg_ux,
                    "evaluated_ui_tasks_count": evaluated_ui_tasks_count,
                    "overhead_justified_rate_pct": overhead_justified_pct,
                    "mean_turns_per_task": avg_turns,
                    "mean_adherence_score": avg_adherence,
                },
                "models": models_list,
                "recent_runs": recent_runs_list,
                "submissions_by_tier": tier_counts,
                "submissions_by_qualification_tier": qualification_counts,
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

        direct_peer = self.client_address[0]
        if direct_peer in TRUSTED_PROXIES:
            client_ip = self.headers.get("X-Forwarded-For", direct_peer).split(",")[0].strip()
        else:
            client_ip = direct_peer

        if is_rate_limited(client_ip):
            self.send_json(429, {"error": "Too Many Requests. Submission rate limit exceeded."})
            return

        if is_project_rate_limited(sanitized["project_hash"]):
            self.send_json(429, {"error": "Too Many Requests. Project submission quota exceeded (max 10/day)."})
            return

        conn = None
        try:
            with DB_LOCK:
                conn = get_db_connection()
                cur = conn.cursor()

                if sanitized["session_fingerprint"]:
                    cur.execute("""
                        INSERT INTO submissions (
                            session_fingerprint, schema_version, project_hash, adherence_score,
                            qualification_tier, is_qualified, git_tree_hash, client_ip, evaluation_mode,
                            project_name, model, task_id, task_description, complexity_tier, primary_subsystem,
                            total_turns, input_tokens, output_tokens, framework_overhead_tokens, initial_loc,
                            rework_loc, rework_turns, compiler_failures, merge_conflicts, ui_touched,
                            ux_completeness, design_tokens_adhered, session_amnesia, invariants_violated,
                            duplicate_utils, adrs_consulted, new_adrs, net_utility_score, overhead_justified,
                            raw_payload
                        ) VALUES (
                            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                        )
                        ON CONFLICT(session_fingerprint) DO UPDATE SET
                            received_at = CURRENT_TIMESTAMP,
                            schema_version = excluded.schema_version,
                            project_hash = excluded.project_hash,
                            adherence_score = excluded.adherence_score,
                            qualification_tier = excluded.qualification_tier,
                            is_qualified = excluded.is_qualified,
                            git_tree_hash = excluded.git_tree_hash,
                            client_ip = excluded.client_ip,
                            evaluation_mode = excluded.evaluation_mode,
                            model = excluded.model,
                            task_description = excluded.task_description,
                            complexity_tier = excluded.complexity_tier,
                            primary_subsystem = excluded.primary_subsystem,
                            total_turns = excluded.total_turns,
                            input_tokens = excluded.input_tokens,
                            output_tokens = excluded.output_tokens,
                            framework_overhead_tokens = excluded.framework_overhead_tokens,
                            initial_loc = excluded.initial_loc,
                            rework_loc = excluded.rework_loc,
                            rework_turns = excluded.rework_turns,
                            compiler_failures = excluded.compiler_failures,
                            merge_conflicts = excluded.merge_conflicts,
                            ui_touched = excluded.ui_touched,
                            ux_completeness = excluded.ux_completeness,
                            design_tokens_adhered = excluded.design_tokens_adhered,
                            session_amnesia = excluded.session_amnesia,
                            invariants_violated = excluded.invariants_violated,
                            duplicate_utils = excluded.duplicate_utils,
                            adrs_consulted = excluded.adrs_consulted,
                            new_adrs = excluded.new_adrs,
                            net_utility_score = excluded.net_utility_score,
                            overhead_justified = excluded.overhead_justified,
                            raw_payload = excluded.raw_payload;
                    """, (
                        sanitized["session_fingerprint"], sanitized["schema_version"], sanitized["project_hash"],
                        sanitized["adherence_score"], sanitized["qualification_tier"], sanitized["is_qualified"],
                        sanitized["git_tree_hash"], client_ip, sanitized["evaluation_mode"], sanitized["project_name"],
                        sanitized["model"], sanitized["task_id"], sanitized["task_description"],
                        sanitized["complexity_tier"], sanitized["primary_subsystem"], sanitized["total_turns"],
                        sanitized["input_tokens"], sanitized["output_tokens"], sanitized["framework_overhead_tokens"],
                        sanitized["initial_loc"], sanitized["rework_loc"], sanitized["rework_turns"],
                        sanitized["compiler_failures"], sanitized["merge_conflicts"], sanitized["ui_touched"],
                        sanitized["ux_completeness"], sanitized["design_tokens_adhered"], sanitized["session_amnesia"],
                        sanitized["invariants_violated"], sanitized["duplicate_utils"], sanitized["adrs_consulted"],
                        sanitized["new_adrs"], sanitized["net_utility_score"], sanitized["overhead_justified"],
                        sanitized["raw_payload"]
                    ))
                    cur.execute("SELECT id FROM submissions WHERE session_fingerprint = ?", (sanitized["session_fingerprint"],))
                    row_res = cur.fetchone()
                    row_id = row_res[0] if row_res else cur.lastrowid
                else:
                    cur.execute("""
                        INSERT INTO submissions (
                            schema_version, project_hash, adherence_score, qualification_tier, is_qualified,
                            git_tree_hash, client_ip, evaluation_mode, project_name, model, task_id,
                            task_description, complexity_tier, primary_subsystem, total_turns, input_tokens,
                            output_tokens, framework_overhead_tokens, initial_loc, rework_loc, rework_turns,
                            compiler_failures, merge_conflicts, ui_touched, ux_completeness,
                            design_tokens_adhered, session_amnesia, invariants_violated, duplicate_utils,
                            adrs_consulted, new_adrs, net_utility_score, overhead_justified, raw_payload
                        ) VALUES (
                            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                        )
                    """, (
                        sanitized["schema_version"], sanitized["project_hash"], sanitized["adherence_score"],
                        sanitized["qualification_tier"], sanitized["is_qualified"], sanitized["git_tree_hash"],
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
        except sqlite3.Error as e:
            self.send_json(500, {"error": f"Database error: {e}"})
            return
        finally:
            if conn:
                conn.close()

        print(f"[{datetime.now(timezone.utc).isoformat()}] Ingested benchmark #{row_id} from {client_ip} (Tier: {sanitized['complexity_tier']}, Qualified: {sanitized['is_qualified']}, Model: {sanitized['model']})")

        self.send_json(201, {
            "status": "accepted",
            "submission_id": row_id,
            "session_fingerprint": sanitized["session_fingerprint"],
            "qualification_tier": sanitized["qualification_tier"],
            "is_qualified": bool(sanitized["is_qualified"]),
            "message": "Anonymous empirical benchmark telemetry stored successfully."
        })


def run_server():
    init_database()
    host = os.environ.get("HOST", "127.0.0.1")
    server_address = (host, PORT)
    httpd = http.server.ThreadingHTTPServer(server_address, TelemetryRequestHandler)
    print(f"PXOS Telemetry Server listening on http://{host}:{PORT}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.server_close()


if __name__ == "__main__":
    run_server()
