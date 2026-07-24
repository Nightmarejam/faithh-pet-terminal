#!/usr/bin/env python3
"""Monitor mining + inference + pipeline freshness for FAITHH crypto stack."""

from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.request import urlopen


@dataclass
class CommandResult:
    returncode: int
    stdout: str
    stderr: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Collect health metrics for FAITHH mining/inference stack."
    )
    parser.add_argument("--faithh-host", default="faithh.taileb8c60.ts.net")
    parser.add_argument("--faithh-user", default="jonat")
    parser.add_argument("--chroma-host", default="servicebox.taileb8c60.ts.net")
    parser.add_argument("--chroma-port", type=int, default=8000)
    parser.add_argument(
        "--monitor-dir",
        default=str(Path(__file__).resolve().parents[1] / "data" / "monitoring"),
    )
    parser.add_argument(
        "--signals-file",
        default=str(
            Path(__file__).resolve().parents[1] / "data" / "signals" / "latest_signals.json"
        ),
    )
    parser.add_argument(
        "--prices-file",
        default="",
        help="Optional explicit prices CSV path. If omitted, latest prices_*.csv is used.",
    )
    parser.add_argument(
        "--max-fetch-age-min",
        type=int,
        default=25,
        help="Max allowed age for latest price fetch timestamp.",
    )
    parser.add_argument(
        "--max-signal-age-min",
        type=int,
        default=25,
        help="Max allowed age for latest signal generation timestamp.",
    )
    return parser.parse_args()


def run_ssh(user: str, host: str, remote_cmd: str) -> CommandResult:
    proc = subprocess.run(
        ["ssh", f"{user}@{host}", remote_cmd],
        capture_output=True,
        text=True,
    )
    return CommandResult(
        returncode=proc.returncode,
        stdout=proc.stdout.strip(),
        stderr=proc.stderr.strip(),
    )


def http_ok(url: str, timeout: int = 3) -> bool:
    try:
        with urlopen(url, timeout=timeout) as resp:  # nosec B310
            return 200 <= resp.status < 300
    except URLError:
        return False


def parse_latest_hashrate_mhs(lines: list[str]) -> float | None:
    if not lines:
        return None
    pattern = re.compile(r"([0-9]+(?:\.[0-9]+)?)\s*MH/s")
    for line in reversed(lines):
        m = pattern.search(line)
        if m:
            return float(m.group(1))
    return None


def parse_last_share_ok(lines: list[str]) -> str | None:
    if not lines:
        return None
    for line in reversed(lines):
        if "[ OK ]" in line:
            # T-Rex logs begin with YYYYMMDD HH:MM:SS
            ts = line[:17]
            try:
                dt = datetime.strptime(ts, "%Y%m%d %H:%M:%S").replace(tzinfo=timezone.utc)
                return dt.isoformat()
            except ValueError:
                return line
    return None


def parse_latest_fetch_time(prices_file: Path) -> str | None:
    if not prices_file.exists():
        return None
    with prices_file.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        return None
    return rows[-1].get("fetched_at")


def parse_signal_time(signals_file: Path) -> str | None:
    if not signals_file.exists():
        return None
    payload = json.loads(signals_file.read_text(encoding="utf-8"))
    return payload.get("generated_at_utc")


def age_minutes(timestamp: str | None) -> float | None:
    if not timestamp:
        return None
    try:
        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        return (datetime.now(timezone.utc) - dt).total_seconds() / 60.0
    except ValueError:
        return None


def write_prometheus(path: Path, metrics: dict[str, float]) -> None:
    lines = []
    for key, val in metrics.items():
        lines.append(f"{key} {val}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def resolve_prices_file(prices_hint_raw: str, prices_dir: Path) -> Path:
    if prices_hint_raw:
        prices_hint = Path(prices_hint_raw).expanduser().resolve()
        if prices_hint.exists():
            return prices_hint
        return prices_hint
    candidates = sorted(prices_dir.glob("prices_*.csv"))
    if not candidates:
        return prices_dir / "prices_latest_missing.csv"
    return candidates[-1]


def main() -> int:
    args = parse_args()
    monitor_dir = Path(args.monitor_dir).expanduser().resolve()
    monitor_dir.mkdir(parents=True, exist_ok=True)
    prices_dir = Path(__file__).resolve().parents[1] / "data" / "prices"
    prices_file = resolve_prices_file(args.prices_file, prices_dir)
    signals_file = Path(args.signals_file).expanduser().resolve()
    miner_log = Path("/home/jonat/miners/trex/miner.log")

    vllm_state = run_ssh(args.faithh_user, args.faithh_host, "systemctl is-active faithh-vllm.service || true")
    miner_proc = run_ssh(args.faithh_user, args.faithh_host, "pgrep -af '/home/jonat/miners/trex/t-rex' || true")
    miner_tail = run_ssh(
        args.faithh_user,
        args.faithh_host,
        "python3 - <<'PY'\nfrom pathlib import Path\np=Path('/home/jonat/miners/trex/miner.log')\nif not p.exists():\n    print('')\nelse:\n    lines=p.read_text(errors='ignore').splitlines()[-500:]\n    print('\\n'.join(lines))\nPY",
    )
    gpu_procs = run_ssh(
        args.faithh_user,
        args.faithh_host,
        "nvidia-smi --query-compute-apps=pid,process_name,used_gpu_memory --format=csv,noheader || true",
    )

    chroma_ok = http_ok(f"http://{args.chroma_host}:{args.chroma_port}/api/v2/heartbeat")
    faithh_ok = http_ok(f"http://{args.faithh_host}:5557/health")
    vllm_ok = http_ok(f"http://{args.faithh_host}:8000/v1/models")

    fetch_ts = parse_latest_fetch_time(prices_file)
    signal_ts = parse_signal_time(signals_file)
    fetch_age = age_minutes(fetch_ts)
    signal_age = age_minutes(signal_ts)

    miner_lines = miner_tail.stdout.splitlines() if miner_tail.stdout else []
    hashrate_mhs = parse_latest_hashrate_mhs(miner_lines)
    last_share_ok = parse_last_share_ok(miner_lines)

    miner_running = bool(miner_proc.stdout)
    vllm_active = vllm_state.stdout.strip() == "active"
    mode = "mixed"
    if miner_running and not vllm_active:
        mode = "mining"
    elif vllm_active and not miner_running:
        mode = "inference"

    alerts: list[str] = []
    if not chroma_ok:
        alerts.append("chroma_unreachable")
    if not faithh_ok:
        alerts.append("faithh_backend_unreachable")
    if fetch_age is None or fetch_age > args.max_fetch_age_min:
        alerts.append("prices_stale")
    if signal_age is None or signal_age > args.max_signal_age_min:
        alerts.append("signals_stale")
    if mode == "mining" and not hashrate_mhs:
        alerts.append("mining_no_hashrate")

    payload: dict[str, Any] = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "mode": mode,
        "services": {
            "faithh_backend_http_ok": faithh_ok,
            "chroma_http_ok": chroma_ok,
            "vllm_http_ok": vllm_ok,
            "vllm_systemd_active": vllm_active,
            "miner_process_running": miner_running,
        },
        "pipeline_freshness": {
            "prices_file": str(prices_file),
            "signals_file": str(signals_file),
            "latest_fetch_at": fetch_ts,
            "latest_signal_at": signal_ts,
            "fetch_age_min": fetch_age,
            "signal_age_min": signal_age,
        },
        "mining": {
            "hashrate_mhs": hashrate_mhs,
            "last_share_ok": last_share_ok,
            "miner_log": str(miner_log),
        },
        "raw": {
            "vllm_state": vllm_state.stdout,
            "miner_process": miner_proc.stdout,
            "gpu_compute_processes": gpu_procs.stdout,
        },
        "alerts": alerts,
        "status": "ok" if not alerts else "degraded",
    }

    status_json = monitor_dir / "latest_status.json"
    status_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    prom_metrics = {
        "faithh_backend_up": 1.0 if faithh_ok else 0.0,
        "chroma_up": 1.0 if chroma_ok else 0.0,
        "vllm_up": 1.0 if vllm_ok else 0.0,
        "vllm_systemd_active": 1.0 if vllm_active else 0.0,
        "miner_running": 1.0 if miner_running else 0.0,
        "monitor_alerts_total": float(len(alerts)),
        "prices_age_minutes": float(fetch_age or -1.0),
        "signals_age_minutes": float(signal_age or -1.0),
        "miner_hashrate_mhs": float(hashrate_mhs or 0.0),
    }
    prom_file = monitor_dir / "crypto_stack.prom"
    write_prometheus(prom_file, prom_metrics)

    print(f"Status: {payload['status']} (alerts={len(alerts)})")
    print(f"Mode: {mode}")
    print(f"JSON: {status_json}")
    print(f"Prometheus: {prom_file}")
    if alerts:
        print("Alerts:", ", ".join(alerts))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
