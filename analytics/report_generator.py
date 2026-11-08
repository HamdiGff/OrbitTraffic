"""
Executive Analytics & Client Report Exporter
Generates client-ready performance audits in CSV and JSON formats:
- Total Impressions & Organic Visits Generated
- SERP RankBrain CTR Boost Uplift
- Average Retention & Dwell Times vs GA4 benchmarks
- Pogo-Sticking Competitor Bounce Metrics
"""
import csv
import json
import time
import os
from typing import List, Dict


def export_client_csv_report(
    sessions: List[Dict],
    filepath: str,
    campaign_name: str = "Enterprise Organic Traffic",
) -> str:
    """Exports structured session audit log for clients."""
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["# ORBITTRAFFIC EXECUTIVE AUDIT REPORT"])
        writer.writerow(["Campaign", campaign_name])
        writer.writerow(["Generated At", time.strftime("%Y-%m-%d %H:%M:%S")])
        writer.writerow([])
        writer.writerow(["Timestamp", "Target Keyword", "Landing URL", "Flow Architecture", "Dwell Time (s)", "Hops", "Status"])

        for s in sessions:
            writer.writerow([
                time.strftime("%H:%M:%S", time.localtime(s.get("timestamp", time.time()))),
                s.get("keyword", "—"),
                s.get("target", "—"),
                "Pogo-Stick + Deep Dwell" if s.get("pogo_used") else "Organic Search Direct",
                f"{s.get('dwell_seconds', 0):.1f}",
                s.get("hops_completed", 1),
                "VERIFIED" if s.get("success") else "FAILED",
            ])
    return filepath


def export_client_json_summary(
    stats: Dict,
    filepath: str,
) -> str:
    """Exports executive metrics summary in JSON."""
    payload = {
        "platform": "OrbitTraffic Enterprise v2.4",
        "generated_at": time.time(),
        "summary": stats,
    }
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    return filepath
