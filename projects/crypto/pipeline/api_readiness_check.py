#!/usr/bin/env python3
"""Check API credential readiness and endpoint reachability."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT / ".env"
OUT_DIR = ROOT / "data" / "ops"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="API readiness check for crypto pipeline")
    parser.add_argument("--timeout", type=float, default=10.0)
    return parser.parse_args()


def load_env(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    out: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip()
    return out


def coinbase_key_format(env: dict[str, str]) -> dict[str, Any]:
    key = env.get("COINBASE_API_KEY", "")
    secret = env.get("COINBASE_API_SECRET", "")
    secret_file = env.get("COINBASE_API_SECRET_FILE", "")
    has_inline_pem = secret.startswith("-----BEGIN")
    has_cdp_key_name = key.startswith("organizations/")
    has_secret_file = bool(secret_file and Path(secret_file).expanduser().exists())

    ready = bool(key) and (has_inline_pem or has_secret_file)
    reason = "ok"
    if not key:
        reason = "missing_api_key"
    elif not (has_inline_pem or has_secret_file):
        reason = "secret_not_pem_or_missing_secret_file"

    return {
        "present": {"api_key": bool(key), "api_secret": bool(secret), "api_secret_file": bool(secret_file)},
        "format": {
            "cdp_key_name_format": has_cdp_key_name,
            "inline_pem_format": has_inline_pem,
            "secret_file_exists": has_secret_file,
        },
        "ready_for_sdk": ready,
        "reason": reason,
    }


def http_probe(url: str, timeout: float) -> dict[str, Any]:
    try:
        resp = requests.get(url, timeout=timeout)
        return {"ok": resp.ok, "status_code": resp.status_code, "error": None}
    except requests.RequestException as exc:
        return {"ok": False, "status_code": None, "error": str(exc)[:240]}


def build_report(timeout: float) -> dict[str, Any]:
    env = load_env(ENV_PATH)
    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "env_path": str(ENV_PATH),
        "env_exists": ENV_PATH.exists(),
        "coinbase": coinbase_key_format(env),
        "execution_mode": env.get("TRADER_EXECUTION_MODE", "paper"),
        "public_endpoints": {
            "coingecko_ping": http_probe("https://api.coingecko.com/api/v3/ping", timeout),
            "two_miners_accounts_sample": http_probe(
                "https://etc.2miners.com/api/accounts/0xF99275b70cB816c76F4E19328dF229483d6Ce8D2",
                timeout,
            ),
            "two_miners_stats_etc": http_probe("https://etc.2miners.com/api/stats", timeout),
        },
        "next_actions": [],
    }

    if not report["coinbase"]["ready_for_sdk"]:
        report["next_actions"].append(
            "Create CDP API key and use COINBASE_API_KEY plus PEM secret (inline or COINBASE_API_SECRET_FILE)."
        )
    if report["execution_mode"] != "paper":
        report["next_actions"].append("Set TRADER_EXECUTION_MODE=paper until live execution is explicitly enabled.")
    if not report["public_endpoints"]["coingecko_ping"]["ok"]:
        report["next_actions"].append("Check outbound connectivity to CoinGecko.")
    if not report["public_endpoints"]["two_miners_stats_etc"]["ok"]:
        report["next_actions"].append("Check outbound connectivity to 2Miners.")

    if not report["next_actions"]:
        report["next_actions"].append("API environment looks ready for paper workflows.")
    return report


def write_report(report: dict[str, Any]) -> tuple[Path, Path]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    ts_path = OUT_DIR / f"api_readiness_{stamp}.json"
    latest_path = OUT_DIR / "api_readiness_latest.json"
    payload = json.dumps(report, indent=2)
    ts_path.write_text(payload, encoding="utf-8")
    latest_path.write_text(payload, encoding="utf-8")
    return ts_path, latest_path


def main() -> int:
    args = parse_args()
    report = build_report(args.timeout)
    ts_path, latest_path = write_report(report)
    print(json.dumps({"timestamped": str(ts_path), "latest": str(latest_path), "next_actions": report["next_actions"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
