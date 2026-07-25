#!/usr/bin/env python3
"""
CLI summary of FAITHH session metrics (Chroma collection faithh_session_metrics).

Examples:
  python3 scripts/analyze_session_metrics.py --days 30
  python3 scripts/analyze_session_metrics.py --days 7 --export-csv out.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _load_repo_dotenv() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    p = REPO_ROOT / ".env"
    if p.is_file():
        load_dotenv(p, override=False)


_load_repo_dotenv()

from backend.session_metrics import (  # noqa: E402
    compute_summary_from_parsed_sessions,
    fetch_session_documents,
    flag_combination_key,
)


def _chroma_client_from_env():
    import chromadb

    host = os.environ.get("CHROMA_HOST", "localhost")
    port = int(os.environ.get("CHROMA_PORT", "8000"))
    if host.startswith("http://") or host.startswith("https://"):
        u = urlparse(host)
        host = u.hostname or "localhost"
        port = u.port or port
    elif ":" in host and host.count(":") == 1 and not host.startswith("http"):
        h, _, p = host.partition(":")
        host = h
        try:
            port = int(p)
        except ValueError:
            pass
    return chromadb.HttpClient(host=host, port=port)


def main() -> int:
    ap = argparse.ArgumentParser(description="Summarize FAITHH session metrics from Chroma.")
    ap.add_argument("--days", type=int, default=30, help="Lookback window (default 30).")
    ap.add_argument("--limit", type=int, default=500, help="Max sessions to load (default 500).")
    ap.add_argument("--collection", default=os.environ.get("CHROMA_METRICS_COLLECTION", "faithh_session_metrics"))
    ap.add_argument("--export-csv", metavar="PATH", help="Write per-session rows to CSV.")
    args = ap.parse_args()

    try:
        client = _chroma_client_from_env()
        coll = client.get_collection(name=args.collection)
    except Exception as e:
        print(f"Chroma error: {e}", file=sys.stderr)
        return 1

    raw = fetch_session_documents(coll, max(1, args.days), max(1, min(args.limit, 2000)))
    if not raw:
        print("No session documents in window.")
        return 0

    summary = compute_summary_from_parsed_sessions(raw, window_days=args.days, limit=len(raw))

    dates = sorted({(r.get("metadata") or {}).get("date") or r.get("timestamp_open", "")[:10] for r in raw})
    print(f"Sessions: {summary['sessions_total']}  Date span: {dates[0]} … {dates[-1]}")
    print(f"Avg latency (ms): {summary['avg_latency_ms']}  Avg turns/session: {summary['avg_turns_per_session']}")

    latencies = []
    for r in raw:
        so = r.get("session_outcome") or {}
        if so.get("turns", 0) > 0 and so.get("max_latency_ms"):
            latencies.append(float(so["max_latency_ms"]))
    latencies.sort()
    p95 = latencies[int(0.95 * (len(latencies) - 1))] if latencies else 0.0
    print(f"Max latency p95 (per-session max): {p95:.0f} ms")

    n = summary["sessions_total"]
    fb_n = summary["sessions_with_fallback"]
    print(f"Fallback rate: {fb_n / n:.2%} ({fb_n}/{n})")

    prov = summary.get("provider_distribution") or {}
    top_p = max(prov, key=lambda k: prov[k]) if prov else None
    print(f"Provider touches (session unique lists): {prov}")
    print(f"Most common provider: {top_p!r}")

    print(f"RAG low-confidence rate: {summary['rag_low_confidence_rate']:.2%}")
    print(f"Top flags: {', '.join(summary.get('top_flags') or [])}")
    print(f"Trend: {summary.get('trend')}")

    combo = Counter(flag_combination_key(s) for s in raw)
    print("Top 5 flag combinations:")
    for k, v in combo.most_common(5):
        print(f"  {v:4d}  {k}")

    if args.export_csv:
        path = Path(args.export_csv)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(
                [
                    "id",
                    "timestamp_open",
                    "timestamp_close",
                    "duration_seconds",
                    "turns",
                    "avg_latency_ms",
                    "fallback_count",
                    "stall_count",
                    "rag_low_confidence",
                    "flags",
                ]
            )
            for r in raw:
                so = r.get("session_outcome") or {}
                fl = r.get("flags") or {}
                w.writerow(
                    [
                        r.get("id"),
                        r.get("timestamp_open"),
                        r.get("timestamp_close"),
                        r.get("duration_seconds"),
                        so.get("turns"),
                        so.get("avg_latency_ms"),
                        so.get("fallback_count"),
                        so.get("stall_count"),
                        fl.get("rag_low_confidence"),
                        json.dumps(fl, sort_keys=True),
                    ]
                )
        print(f"Wrote {path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
