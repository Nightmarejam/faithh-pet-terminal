#!/usr/bin/env python3
"""
Probe Prometheus with each Grafana panel's expr; print HAS DATA vs NO DATA.

Uses ~/ops/monitoring/.env for Grafana (list/fetch dashboards only);
Prometheus at http://localhost:9090 for instant queries.

Usage:
    python3 scripts/audit_grafana_dashboard_panels.py
"""

from __future__ import annotations

import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

GRAFANA_URL = "http://localhost:3000"
PROM_URL = "http://localhost:9090"
OPS_ENV = Path.home() / "ops" / "monitoring" / ".env"


def grafana_password() -> str:
    if OPS_ENV.is_file():
        for line in OPS_ENV.read_text(encoding="utf-8").splitlines():
            if line.startswith("GRAFANA_PASSWORD="):
                return line.split("=", 1)[1].strip()
    return "admin"


def grafana_get(path: str) -> dict | list:
    import base64

    auth = base64.b64encode(f"admin:{grafana_password()}".encode()).decode()
    req = urllib.request.Request(
        f"{GRAFANA_URL}{path}",
        headers={"Authorization": f"Basic {auth}"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def prom_query(expr: str) -> list:
    if not expr or not expr.strip():
        return []
    q = urllib.parse.urlencode({"query": expr})
    url = f"{PROM_URL}/api/v1/query?{q}"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=10) as r:
        data = json.loads(r.read().decode())
    if data.get("status") != "success":
        return []
    return data.get("data", {}).get("result", [])


def walk_panel_targets(
    panels: list, prefix: str = ""
) -> list[tuple[str, str, str]]:
    """(panel_path, panel_type, expr) for each target."""
    out: list[tuple[str, str, str]] = []
    for p in panels:
        title = p.get("title") or "untitled"
        path = f"{prefix}{title}"
        ptype = p.get("type", "?")
        nested = p.get("panels")
        if nested:
            out.extend(walk_panel_targets(nested, path + " / "))
            continue
        for t in p.get("targets", []):
            expr = t.get("expr", "")
            if isinstance(expr, dict):
                expr = expr.get("query", "") or str(expr)
            expr = str(expr).strip()
            if expr:
                out.append((path, ptype, expr))
    return out


def main() -> int:
    boards = grafana_get("/api/search?type=dash-db")
    if not isinstance(boards, list):
        print(boards, file=sys.stderr)
        return 1

    for meta in boards:
        title = meta["title"]
        uid = meta["uid"]
        print(f"\n{'=' * 60}\nDashboard: {title}\nUID: {uid}")
        raw = grafana_get(f"/api/dashboards/uid/{uid}")
        panels = raw["dashboard"].get("panels", [])
        rows = walk_panel_targets(panels)
        print(f"Panel targets: {len(rows)}")
        seen = set()
        for ppath, ptype, expr in rows:
            key = (ppath, expr)
            if key in seen:
                continue
            seen.add(key)
            try:
                res = prom_query(expr)
                status = "HAS DATA" if res else "NO DATA"
            except Exception as e:
                status = f"ERROR ({e})"
            print(f"  [{status:12s}] [{ptype:12s}] {ppath[:56]}")
            print(f"      {expr[:100]}{'...' if len(expr) > 100 else ''}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
