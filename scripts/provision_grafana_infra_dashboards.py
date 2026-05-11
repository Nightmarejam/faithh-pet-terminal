#!/usr/bin/env python3
"""
Create / update Grafana dashboards: NAS Storage, Windows Host, Infrastructure Overview.

Uses admin credentials from ~/ops/monitoring/.env (GRAFANA_PASSWORD).
Run from WSL when Grafana is up on localhost:3000.

Usage:
    python3 scripts/provision_grafana_infra_dashboards.py
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

GRAFANA_URL = os.environ.get("GRAFANA_URL", "http://localhost:3000")
OPS_ENV = Path.home() / "ops" / "monitoring" / ".env"

DS_UID = os.environ.get("GRAFANA_PROMETHEUS_UID", "")


def load_grafana_password() -> str:
    if p := os.environ.get("GRAFANA_PASSWORD"):
        return p
    if OPS_ENV.is_file():
        for line in OPS_ENV.read_text(encoding="utf-8").splitlines():
            if line.startswith("GRAFANA_PASSWORD="):
                return line.split("=", 1)[1].strip()
    return "admin"


def grafana_request(method: str, path: str, body: dict | None = None) -> dict:
    password = load_grafana_password()
    auth = f"admin:{password}".encode()
    import base64

    headers = {
        "Authorization": "Basic " + base64.b64encode(auth).decode(),
        "Content-Type": "application/json",
    }
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        f"{GRAFANA_URL.rstrip('/')}{path}", data=data, headers=headers, method=method
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        err = e.read().decode()
        raise RuntimeError(f"{method} {path} HTTP {e.code}: {err[:500]}") from e


def get_prometheus_uid() -> str:
    global DS_UID
    if DS_UID:
        return DS_UID
    for ds in grafana_request("GET", "/api/datasources"):
        if ds.get("type") == "prometheus":
            return ds["uid"]
    raise RuntimeError("No Prometheus datasource in Grafana")


def ds_ref(uid: str) -> dict:
    return {"type": "prometheus", "uid": uid}


def timeseries_panel(
    uid: str, panel_id: int, title: str, x: int, y: int, w: int, h: int, expr: str, legend: str, unit: str = "percent"
) -> dict:
    return {
        "id": panel_id,
        "type": "timeseries",
        "title": title,
        "gridPos": {"x": x, "y": y, "w": w, "h": h},
        "datasource": ds_ref(uid),
        "targets": [
            {
                "datasource": ds_ref(uid),
                "expr": expr,
                "refId": "A",
                "legendFormat": legend,
            }
        ],
        "fieldConfig": {
            "defaults": {
                "unit": unit,
                "custom": {"drawStyle": "line", "lineInterpolation": "smooth", "fillOpacity": 10},
            },
            "overrides": [],
        },
        "options": {
            "legend": {"displayMode": "list", "placement": "bottom", "showLegend": True},
            "tooltip": {"mode": "single"},
        },
    }


def bargauge_panel(
    uid: str, panel_id: int, title: str, x: int, y: int, w: int, h: int, expr: str, legend: str
) -> dict:
    return {
        "id": panel_id,
        "type": "bargauge",
        "title": title,
        "gridPos": {"x": x, "y": y, "w": w, "h": h},
        "datasource": ds_ref(uid),
        "targets": [
            {
                "datasource": ds_ref(uid),
                "expr": expr,
                "refId": "A",
                "legendFormat": legend,
            }
        ],
        "fieldConfig": {
            "defaults": {
                "unit": "percent",
                "min": 0,
                "max": 100,
                "thresholds": {
                    "mode": "absolute",
                    "steps": [
                        {"color": "green", "value": None},
                        {"color": "yellow", "value": 80},
                        {"color": "red", "value": 95},
                    ],
                },
            },
            "overrides": [],
        },
        "options": {"displayMode": "gradient", "orientation": "horizontal", "showUnfilled": True},
    }


def stat_panel(uid: str, panel_id: int, title: str, x: int, y: int, w: int, h: int, expr: str) -> dict:
    return {
        "id": panel_id,
        "type": "stat",
        "title": title,
        "gridPos": {"x": x, "y": y, "w": w, "h": h},
        "datasource": ds_ref(uid),
        "targets": [
            {
                "datasource": ds_ref(uid),
                "expr": expr,
                "refId": "A",
                "legendFormat": "{{job}}",
            }
        ],
        "fieldConfig": {"defaults": {"unit": "none"}, "overrides": []},
        "options": {
            "reduceOptions": {"calcs": ["lastNotNull"], "fields": "", "values": False},
            "orientation": "auto",
            "textMode": "value_and_name",
            "colorMode": "value",
            "graphMode": "none",
        },
    }


def build_nas_dashboard(uid: str) -> dict:
    cpu = (
        "100 * (1 - avg by (instance) (rate(node_cpu_seconds_total{job=\"nas\",mode=\"idle\"}[5m])))"
    )
    mem = (
        "100 * (1 - node_memory_MemAvailable_bytes{job=\"nas\"} / node_memory_MemTotal_bytes{job=\"nas\"})"
    )
    disk = (
        "100 * (1 - node_filesystem_avail_bytes{job=\"nas\",fstype!~\"tmpfs|overlay\"} "
        "/ node_filesystem_size_bytes{job=\"nas\",fstype!~\"tmpfs|overlay\"})"
    )
    panels = [
        timeseries_panel(uid, 1, "NAS CPU usage %", 0, 0, 12, 8, cpu, "CPU %"),
        timeseries_panel(uid, 2, "NAS memory usage %", 12, 0, 12, 8, mem, "Memory %"),
        bargauge_panel(
            uid, 3, "NAS disk usage % (by mountpoint)", 0, 8, 12, 8, disk, "{{mountpoint}}"
        ),
        {
            "id": 4,
            "type": "timeseries",
            "title": "NAS network I/O",
            "gridPos": {"x": 12, "y": 8, "w": 12, "h": 8},
            "datasource": ds_ref(uid),
            "targets": [
                {
                    "datasource": ds_ref(uid),
                    "expr": 'rate(node_network_receive_bytes_total{job="nas",device!~"lo|docker.*|veth.*"}[5m])',
                    "refId": "A",
                    "legendFormat": "RX {{device}}",
                },
                {
                    "datasource": ds_ref(uid),
                    "expr": 'rate(node_network_transmit_bytes_total{job="nas",device!~"lo|docker.*|veth.*"}[5m])',
                    "refId": "B",
                    "legendFormat": "TX {{device}}",
                },
            ],
            "fieldConfig": {
                "defaults": {
                    "unit": "Bps",
                    "custom": {"drawStyle": "line", "fillOpacity": 10},
                },
                "overrides": [],
            },
            "options": {
                "legend": {"displayMode": "list", "placement": "bottom", "showLegend": True},
                "tooltip": {"mode": "multi"},
            },
        },
    ]
    return {
        "title": "NAS Storage (Synology)",
        "uid": "nas-storage-synology",
        "tags": ["nas", "storage", "node-exporter"],
        "timezone": "browser",
        "schemaVersion": 38,
        "version": 0,
        "refresh": "30s",
        "panels": panels,
        "time": {"from": "now-6h", "to": "now"},
    }


def build_windows_dashboard(uid: str) -> dict:
    cpu = (
        '100 - (avg by (instance) (rate(windows_cpu_time_total{job="windows_host",mode="idle"}[5m])) * 100)'
    )
    mem = (
        '100 * (1 - windows_memory_available_bytes{job="windows_host"} '
        '/ windows_os_visible_memory_bytes{job="windows_host"})'
    )
    disk = (
        '100 * (1 - windows_logical_disk_free_bytes{job="windows_host",volume!~"HarddiskVolume.*"} '
        '/ windows_logical_disk_size_bytes{job="windows_host",volume!~"HarddiskVolume.*"})'
    )
    panels = [
        timeseries_panel(uid, 1, "Windows CPU usage %", 0, 0, 12, 8, cpu, "CPU %"),
        timeseries_panel(uid, 2, "Windows memory usage %", 12, 0, 12, 8, mem, "Memory %"),
        bargauge_panel(uid, 3, "Windows disk usage % (by volume)", 0, 8, 12, 8, disk, "{{volume}}"),
        {
            "id": 4,
            "type": "timeseries",
            "title": "GPU — placeholder",
            "description": "Requires nvidia_smi_exporter / DCGM. `windows_gpu_utilization` often absent.",
            "gridPos": {"x": 12, "y": 8, "w": 12, "h": 8},
            "datasource": ds_ref(uid),
            "targets": [
                {
                    "datasource": ds_ref(uid),
                    "expr": 'windows_gpu_utilization{job="windows_host"}',
                    "refId": "A",
                    "legendFormat": "GPU",
                }
            ],
            "fieldConfig": {
                "defaults": {"unit": "percent", "custom": {"drawStyle": "line"}},
                "overrides": [],
            },
            "options": {
                "legend": {"displayMode": "list", "placement": "bottom", "showLegend": True},
                "tooltip": {"mode": "single"},
            },
        },
        {
            "id": 5,
            "type": "timeseries",
            "title": "Windows network I/O",
            "gridPos": {"x": 0, "y": 16, "w": 24, "h": 8},
            "datasource": ds_ref(uid),
            "targets": [
                {
                    "datasource": ds_ref(uid),
                    "expr": 'rate(windows_net_bytes_received_total{job="windows_host",nic!~".*isatap.*|.*Teredo.*"}[5m])',
                    "refId": "A",
                    "legendFormat": "RX {{nic}}",
                },
                {
                    "datasource": ds_ref(uid),
                    "expr": 'rate(windows_net_bytes_sent_total{job="windows_host",nic!~".*isatap.*|.*Teredo.*"}[5m])',
                    "refId": "B",
                    "legendFormat": "TX {{nic}}",
                },
            ],
            "fieldConfig": {
                "defaults": {"unit": "Bps", "custom": {"drawStyle": "line", "fillOpacity": 10}},
                "overrides": [],
            },
            "options": {
                "legend": {"displayMode": "list", "placement": "bottom", "showLegend": True},
                "tooltip": {"mode": "multi"},
            },
        },
    ]
    return {
        "title": "Windows Host (DESKTOP-JJ1SUHB)",
        "uid": "windows-host-workstation",
        "tags": ["windows", "workstation", "windows_exporter"],
        "timezone": "browser",
        "schemaVersion": 38,
        "version": 0,
        "refresh": "30s",
        "panels": panels,
        "time": {"from": "now-6h", "to": "now"},
    }


def build_infra_dashboard(uid: str) -> dict:
    # Linux: only node_exporter jobs (shows wsl_node as host.docker.internal:9100, nas as nas)
    node_cpu = (
        '100 * (1 - avg by (job, instance) (rate(node_cpu_seconds_total{job=~"nas|wsl_node",mode="idle"}[5m])))'
    )
    win_cpu = (
        '100 - (avg by (job) (rate(windows_cpu_time_total{job="windows_host",mode="idle"}[5m])) * 100)'
    )
    up_jobs = 'up{job=~"cadvisor|faithh_backend|nas|prometheus|windows_host|wsl_node"}'
    mem_linux = (
        '100 * (1 - node_memory_MemAvailable_bytes{job=~"nas|wsl_node"} '
        '/ node_memory_MemTotal_bytes{job=~"nas|wsl_node"})'
    )
    mem_win = (
        '100 * (1 - windows_memory_available_bytes{job="windows_host"} '
        '/ windows_os_visible_memory_bytes{job="windows_host"})'
    )
    disk_wsl = (
        '100 * (1 - node_filesystem_avail_bytes{job="wsl_node",mountpoint="/"} '
        '/ node_filesystem_size_bytes{job="wsl_node",mountpoint="/"})'
    )
    disk_nas = (
        '100 * (1 - node_filesystem_avail_bytes{job="nas",fstype!~"tmpfs|overlay"} '
        '/ node_filesystem_size_bytes{job="nas",fstype!~"tmpfs|overlay"})'
    )
    panels = [
        {
            "id": 1,
            "type": "timeseries",
            "title": "CPU usage % — Linux (nas + wsl_node) + Windows",
            "gridPos": {"x": 0, "y": 0, "w": 24, "h": 8},
            "datasource": ds_ref(uid),
            "targets": [
                {
                    "datasource": ds_ref(uid),
                    "expr": node_cpu,
                    "refId": "A",
                    "legendFormat": "{{job}} / {{instance}}",
                },
                {
                    "datasource": ds_ref(uid),
                    "expr": win_cpu,
                    "refId": "B",
                    "legendFormat": "windows_host / {{job}}",
                },
            ],
            "fieldConfig": {
                "defaults": {"unit": "percent", "custom": {"drawStyle": "line", "fillOpacity": 10}},
                "overrides": [],
            },
            "options": {
                "legend": {"displayMode": "list", "placement": "bottom", "showLegend": True},
                "tooltip": {"mode": "multi"},
            },
        },
        stat_panel(uid, 2, "Scrape health (up)", 0, 8, 8, 7, up_jobs),
        {
            "id": 3,
            "type": "timeseries",
            "title": "FAITHH — HTTP request rate",
            "gridPos": {"x": 8, "y": 8, "w": 16, "h": 7},
            "datasource": ds_ref(uid),
            "targets": [
                {
                    "datasource": ds_ref(uid),
                    "expr": 'sum by (handler, method) (rate(faithh_http_requests_total[5m]))',
                    "refId": "A",
                    "legendFormat": "faithh {{method}} {{handler}}",
                },
                {
                    "datasource": ds_ref(uid),
                    "expr": 'sum by (endpoint) (rate(flask_http_request_total[5m]))',
                    "refId": "B",
                    "legendFormat": "flask {{endpoint}}",
                },
            ],
            "fieldConfig": {
                "defaults": {"unit": "reqps", "custom": {"drawStyle": "line", "fillOpacity": 10}},
                "overrides": [],
            },
            "options": {
                "legend": {"displayMode": "list", "placement": "bottom", "showLegend": True},
                "tooltip": {"mode": "multi"},
            },
        },
        timeseries_panel(
            uid,
            4,
            "Memory usage % — Linux (nas + wsl_node)",
            0,
            15,
            12,
            7,
            mem_linux,
            "{{job}} / {{instance}}",
        ),
        timeseries_panel(
            uid,
            5,
            "Memory usage % — Windows",
            12,
            15,
            12,
            7,
            mem_win,
            "windows_host",
        ),
        timeseries_panel(
            uid,
            6,
            "Disk usage % — WSL root (/)",
            0,
            22,
            12,
            7,
            disk_wsl,
            "{{job}} / {{instance}}",
        ),
        {
            "id": 7,
            "type": "timeseries",
            "title": "Disk usage % — NAS (by mountpoint)",
            "gridPos": {"x": 12, "y": 22, "w": 12, "h": 7},
            "datasource": ds_ref(uid),
            "targets": [
                {
                    "datasource": ds_ref(uid),
                    "expr": disk_nas,
                    "refId": "A",
                    "legendFormat": "{{mountpoint}}",
                }
            ],
            "fieldConfig": {
                "defaults": {"unit": "percent", "custom": {"drawStyle": "line", "fillOpacity": 10}},
                "overrides": [],
            },
            "options": {
                "legend": {"displayMode": "list", "placement": "bottom", "showLegend": True},
                "tooltip": {"mode": "multi"},
            },
        },
    ]
    return {
        "title": "Infrastructure Overview",
        "uid": "infrastructure-overview",
        "tags": ["overview", "all-hosts"],
        "timezone": "browser",
        "schemaVersion": 38,
        "version": 0,
        "refresh": "30s",
        "panels": panels,
        "time": {"from": "now-6h", "to": "now"},
    }


def push_dashboard(dashboard: dict) -> dict:
    return grafana_request(
        "POST",
        "/api/dashboards/db",
        {"dashboard": dashboard, "overwrite": True, "folderId": 0},
    )


def main() -> int:
    uid = get_prometheus_uid()
    print(f"Prometheus datasource uid: {uid}")
    for name, builder in [
        ("NAS Storage (Synology)", lambda: build_nas_dashboard(uid)),
        ("Windows Host", lambda: build_windows_dashboard(uid)),
        ("Infrastructure Overview", lambda: build_infra_dashboard(uid)),
    ]:
        db = builder()
        out = push_dashboard(db)
        print(f"  {name}: {out.get('status')} -> {out.get('url', out)}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(1)
