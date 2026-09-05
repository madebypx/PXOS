#!/usr/bin/env python3
"""
Daily Telemetry Aggregation & Report Generator
==============================================
Extracts all ingested telemetry from SQLite, executes the analyze.py pipeline,
and writes updated public daily_report.md and daily_summary.json.
"""

import json
import sqlite3
import os
import sys
from pathlib import Path

# Add current and root directory to sys.path to reliably import analyze and server
CUR_DIR = Path(__file__).resolve().parent
REPO_ROOT = CUR_DIR.parent
sys.path.extend([str(CUR_DIR), str(REPO_ROOT)])

DEFAULT_TELEMETRY_DIR = Path(os.environ.get("PXOS_TELEMETRY_DIR", "/opt/pxos-telemetry"))
TELEMETRY_DIR = DEFAULT_TELEMETRY_DIR if DEFAULT_TELEMETRY_DIR.exists() else CUR_DIR

import analyze
from server import DB_PATH

PUBLIC_DIR = TELEMETRY_DIR / "public"


def run_daily_aggregation():
    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
    if not DB_PATH.exists():
        print(f"[INFO] No database found at {DB_PATH}. Nothing to aggregate.")
        return

    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT raw_payload FROM submissions WHERE verified_status != 'rejected'")
        rows = cur.fetchall()
    finally:
        if conn:
            conn.close()

    print(f"[INFO] Fetched {len(rows)} raw payloads from {DB_PATH}")
    if not rows:
        print("[INFO] No submissions to aggregate.")
        return

    records = []
    for idx, (raw_str,) in enumerate(rows):
        if not raw_str:
            continue
        try:
            tmp_data = json.loads(raw_str)
            rec = analyze.load_record_from_dict(tmp_data, f"db_record_{idx}")
            if rec:
                records.append(rec)
        except Exception as e:
            print(f"[WARN] Failed to parse payload #{idx}: {e}")

    if not records:
        print("[WARN] No valid records parsed from database.")
        return

    analysis = analyze.analyze_dataset(records)
    report_md = analyze.generate_markdown_report(analysis)

    report_file = PUBLIC_DIR / "daily_report.md"
    summary_file = PUBLIC_DIR / "daily_summary.json"

    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report_md)

    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(analysis, f, indent=2)

    print(f"[SUCCESS] Aggregated {len(records)} records.")
    print(f"Report written to: {report_file}")
    print(f"Summary written to: {summary_file}")


if __name__ == "__main__":
    run_daily_aggregation()
