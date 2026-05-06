#!/usr/bin/env python3
"""Poll 2Miners + price feeds and log mining profitability snapshots."""

from __future__ import annotations

import argparse
import csv
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import requests

LOGGER = logging.getLogger("crypto.mining_ledger")

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "coins.json"
OUTPUT_DIR = ROOT / "data" / "mining"
TWOMINERS_API = "https://etc.2miners.com/api/accounts/{address}"
UNITS_PER_ETC = 1_000_000_000

FIELDNAMES = [
    "timestamp",
    "worker",
    "reported_hashrate_mhs",
    "effective_hashrate_mhs",
    "pool_hashrate_mhs",
    "shares_valid",
    "shares_stale",
    "shares_invalid",
    "unpaid_etc",
    "immature_etc",
    "total_pending_etc",
    "usd_per_etc",
    "pending_usd",
    "estimated_daily_etc",
    "estimated_daily_usd",
    "electricity_cost_usd",
    "net_daily_usd",
]


def load_config() -> dict:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def fetch_pool_stats(address: str) -> dict:
    response = requests.get(TWOMINERS_API.format(address=address), timeout=15)
    response.raise_for_status()
    return response.json()


def fetch_etc_price() -> float:
    response = requests.get(
        "https://api.coingecko.com/api/v3/simple/price",
        params={"ids": "ethereum-classic", "vs_currencies": "usd"},
        timeout=15,
    )
    response.raise_for_status()
    return float(response.json()["ethereum-classic"]["usd"])


def extract_daily_etc(pool_data: dict) -> float:
    # Prefer pool-provided 24h reward, fallback to rolling pending snapshot.
    daily_reward_units = pool_data.get("24hreward")
    if isinstance(daily_reward_units, (int, float)):
        return float(daily_reward_units) / UNITS_PER_ETC
    stats = pool_data.get("stats", {})
    pending_units = float(stats.get("balance", 0)) + float(stats.get("immature", 0))
    return pending_units / UNITS_PER_ETC


def infer_power_watts(worker_name: str, workers_cfg: dict) -> int:
    worker_cfg = workers_cfg.get(worker_name, {}) if workers_cfg else {}
    gpu_label = str(worker_cfg.get("gpu", "")).lower()
    name = worker_name.lower()
    if "3090" in name or "3090" in gpu_label:
        return 300
    if "1080" in name or "1080" in gpu_label:
        return 200
    return 250


def parse_rows(
    pool_data: dict,
    etc_price_usd: float,
    electricity_cost_usd_per_kwh: float,
    workers_cfg: dict,
) -> list[dict]:
    stats = pool_data.get("stats", {})
    workers = pool_data.get("workers", {})
    timestamp = datetime.now(timezone.utc).isoformat()

    unpaid_etc = float(stats.get("balance", 0)) / UNITS_PER_ETC
    immature_etc = float(stats.get("immature", 0)) / UNITS_PER_ETC
    total_pending_etc = unpaid_etc + immature_etc
    estimated_daily_etc = extract_daily_etc(pool_data)
    pending_usd = total_pending_etc * etc_price_usd
    estimated_daily_usd = estimated_daily_etc * etc_price_usd
    pool_hashrate_mhs = float(pool_data.get("hashrate", 0)) / 1_000_000

    rows: list[dict] = []
    for worker_name, worker in workers.items():
        reported_mhs = float(worker.get("rhr", 0)) / 1_000_000
        effective_mhs = float(worker.get("hr2", 0)) / 1_000_000
        watts = infer_power_watts(worker_name, workers_cfg)
        electricity_cost_usd = (watts / 1000) * 24 * electricity_cost_usd_per_kwh
        net_daily_usd = estimated_daily_usd - electricity_cost_usd

        rows.append(
            {
                "timestamp": timestamp,
                "worker": worker_name,
                "reported_hashrate_mhs": round(reported_mhs, 2),
                "effective_hashrate_mhs": round(effective_mhs, 2),
                "pool_hashrate_mhs": round(pool_hashrate_mhs, 2),
                "shares_valid": int(worker.get("sharesValid", 0)),
                "shares_stale": int(worker.get("sharesStale", 0)),
                "shares_invalid": int(worker.get("sharesInvalid", 0)),
                "unpaid_etc": round(unpaid_etc, 9),
                "immature_etc": round(immature_etc, 9),
                "total_pending_etc": round(total_pending_etc, 9),
                "usd_per_etc": round(etc_price_usd, 4),
                "pending_usd": round(pending_usd, 4),
                "estimated_daily_etc": round(estimated_daily_etc, 9),
                "estimated_daily_usd": round(estimated_daily_usd, 4),
                "electricity_cost_usd": round(electricity_cost_usd, 4),
                "net_daily_usd": round(net_daily_usd, 4),
            }
        )

    if not rows:
        rows.append(
            {
                "timestamp": timestamp,
                "worker": "total",
                "reported_hashrate_mhs": 0.0,
                "effective_hashrate_mhs": round(pool_hashrate_mhs, 2),
                "pool_hashrate_mhs": round(pool_hashrate_mhs, 2),
                "shares_valid": int(pool_data.get("sharesValid", 0)),
                "shares_stale": int(pool_data.get("sharesStale", 0)),
                "shares_invalid": int(pool_data.get("sharesInvalid", 0)),
                "unpaid_etc": round(unpaid_etc, 9),
                "immature_etc": round(immature_etc, 9),
                "total_pending_etc": round(total_pending_etc, 9),
                "usd_per_etc": round(etc_price_usd, 4),
                "pending_usd": round(pending_usd, 4),
                "estimated_daily_etc": round(estimated_daily_etc, 9),
                "estimated_daily_usd": round(estimated_daily_usd, 4),
                "electricity_cost_usd": 0.0,
                "net_daily_usd": round(estimated_daily_usd, 4),
            }
        )

    return rows


def write_ledger(rows: list[dict]) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    file_path = OUTPUT_DIR / f"mining_ledger_{datetime.now(timezone.utc):%Y%m}.csv"
    write_header = not file_path.exists()
    with file_path.open("a", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=FIELDNAMES)
        if write_header:
            writer.writeheader()
        writer.writerows(rows)
    return file_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Poll mining stats into a CSV ledger.")
    parser.add_argument("--electricity-cost", type=float, default=0.12)
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )

    cfg = load_config()
    wallet_cfg = cfg.get("wallet_addresses", {})
    workers_cfg = wallet_cfg.get("workers", {})
    address = wallet_cfg.get("ETC")
    if not address:
        raise ValueError("wallet_addresses.ETC missing in config/coins.json")

    pool_data = fetch_pool_stats(address)
    etc_price_usd = fetch_etc_price()
    rows = parse_rows(pool_data, etc_price_usd, args.electricity_cost, workers_cfg)
    output_path = write_ledger(rows)

    for row in rows:
        LOGGER.info(
            "worker=%s reported=%.2fMH/s effective=%.2fMH/s pending=%.6fETC est_day=$%.4f net_day=$%.4f",
            row["worker"],
            row["reported_hashrate_mhs"],
            row["effective_hashrate_mhs"],
            row["total_pending_etc"],
            row["estimated_daily_usd"],
            row["net_daily_usd"],
        )
    LOGGER.info("ledger_written=%s", output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
