#!/usr/bin/env python3
"""System metrics MCP sketch for FAITHH ecosystem.

Purpose:
- Expose Prometheus-backed observability tools to MCP clients.
- Keep one "ops capability surface" for FAITHH, Cursor agents, and other MCP-aware clients.

Notes:
- This is a practical draft intended to be adapted to your environment.
- Requires an MCP server package at runtime (FastMCP flavor) and `requests`.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Any

import requests

try:
    # Preferred import path used by many FastMCP examples.
    from mcp.server.fastmcp import FastMCP  # type: ignore
except Exception:  # noqa: BLE001
    # Alternate package path used by some installs.
    from fastmcp import FastMCP  # type: ignore


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prometheus-backed system metrics MCP server")
    parser.add_argument("--prom-url", default=os.getenv("PROM_URL", "http://127.0.0.1:9090"))
    parser.add_argument("--faithh-health-url", default=os.getenv("FAITHH_HEALTH_URL", "http://127.0.0.1:5557/health"))
    parser.add_argument("--chroma-health-url", default=os.getenv("CHROMA_HEALTH_URL", "http://127.0.0.1:8000/api/v2/heartbeat"))
    parser.add_argument("--vllm-health-url", default=os.getenv("VLLM_HEALTH_URL", "http://127.0.0.1:8001/health"))
    parser.add_argument("--backend-log", default=os.getenv("FAITHH_BACKEND_LOG", "/home/jonat/ai-stack/backend.log"))
    parser.add_argument("--host", default=os.getenv("MCP_BIND_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.getenv("MCP_PORT", "9111")))
    return parser.parse_args()


def _prom_query(prom_url: str, query: str) -> dict[str, Any]:
    resp = requests.get(
        f"{prom_url.rstrip('/')}/api/v1/query",
        params={"query": query},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()


def _status_probe(url: str) -> dict[str, Any]:
    try:
        r = requests.get(url, timeout=5)
        return {"ok": r.ok, "status_code": r.status_code, "url": url}
    except requests.RequestException as exc:
        return {"ok": False, "status_code": None, "url": url, "error": str(exc)[:220]}


def _tail_file(path: str, lines: int = 100) -> list[str]:
    p = Path(path)
    if not p.exists():
        return [f"[missing] {path}"]
    data = p.read_text(encoding="utf-8", errors="replace").splitlines()
    return data[-max(1, lines) :]


def build_mcp(args: argparse.Namespace) -> FastMCP:
    mcp = FastMCP("system-metrics-mcp")

    @mcp.tool()
    def system_overview() -> dict[str, Any]:
        """Return high-level CPU, RAM, and disk telemetry snapshots."""
        queries = {
            "cpu_idle_pct": 'avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100',
            "mem_used_pct": "(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100",
            "disk_used_pct_root": '(1 - (node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"})) * 100',
        }
        out: dict[str, Any] = {}
        for key, query in queries.items():
            out[key] = _prom_query(args.prom_url, query)
        return out

    @mcp.tool()
    def gpu_vllm_status() -> dict[str, Any]:
        """Return GPU utilization/memory and vLLM health probe."""
        return {
            "gpu_util_pct": _prom_query(args.prom_url, "avg(nvidia_gpu_utilization)"),
            "gpu_mem_used_bytes": _prom_query(args.prom_url, "sum(nvidia_gpu_memory_used_bytes)"),
            "vllm_health": _status_probe(args.vllm_health_url),
        }

    @mcp.tool()
    def service_health() -> dict[str, Any]:
        """Probe FAITHH backend, ChromaDB, and vLLM health endpoints."""
        return {
            "faithh_backend": _status_probe(args.faithh_health_url),
            "chromadb": _status_probe(args.chroma_health_url),
            "vllm": _status_probe(args.vllm_health_url),
        }

    @mcp.tool()
    def chroma_collection_count() -> dict[str, Any]:
        """Return ChromaDB collection count using API heartbeat/list endpoint pattern."""
        base = args.chroma_health_url.replace("/api/v2/heartbeat", "").rstrip("/")
        try:
            r = requests.get(f"{base}/api/v2/collections", timeout=8)
            if not r.ok:
                return {"ok": False, "status_code": r.status_code, "count": None}
            payload = r.json()
            if isinstance(payload, dict):
                collections = payload.get("collections", [])
            else:
                collections = payload
            return {"ok": True, "status_code": r.status_code, "count": len(collections)}
        except requests.RequestException as exc:
            return {"ok": False, "status_code": None, "count": None, "error": str(exc)[:220]}

    @mcp.tool()
    def vllm_throughput() -> dict[str, Any]:
        """Return vLLM request throughput/latency if metrics are present in Prometheus."""
        return {
            "requests_per_s": _prom_query(args.prom_url, "sum(rate(vllm_request_count_total[5m]))"),
            "avg_latency_ms": _prom_query(
                args.prom_url,
                "1000 * (sum(rate(vllm_request_duration_seconds_sum[5m])) / sum(rate(vllm_request_duration_seconds_count[5m])))",
            ),
        }

    @mcp.tool()
    def tail_backend_log(lines: int = 80) -> dict[str, Any]:
        """Tail backend log lines for fast diagnostics."""
        return {"log_path": args.backend_log, "lines": _tail_file(args.backend_log, lines=lines)}

    @mcp.tool()
    def promql_query(query: str) -> dict[str, Any]:
        """Execute an ad-hoc PromQL query (read-only)."""
        return _prom_query(args.prom_url, query)

    return mcp


def main() -> int:
    args = _parse_args()
    mcp = build_mcp(args)
    # Most FastMCP servers use SSE transport for remote clients.
    mcp.run(transport="sse", host=args.host, port=args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
