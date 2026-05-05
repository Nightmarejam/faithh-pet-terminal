#!/usr/bin/env python3
"""G1 market data fetcher using CoinGecko public API."""

from __future__ import annotations

import argparse
import csv
import json
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

LOGGER = logging.getLogger("crypto.fetch_prices")
COINGECKO_MARKETS_URL = "https://api.coingecko.com/api/v3/coins/markets"


@dataclass(frozen=True)
class CoinTarget:
    id: str
    symbol: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch price snapshots from CoinGecko.")
    parser.add_argument(
        "--config",
        default=str(Path(__file__).resolve().parents[1] / "config" / "coins.json"),
        help="Path to coins.json config file.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(Path(__file__).resolve().parents[1] / "data" / "prices"),
        help="Directory where price CSV snapshots are written.",
    )
    parser.add_argument(
        "--vs-currency",
        default="usd",
        help="Quote currency for CoinGecko markets endpoint.",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=20,
        help="HTTP timeout for CoinGecko request.",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logger verbosity.",
    )
    return parser.parse_args()


def load_targets(config_path: Path) -> list[CoinTarget]:
    payload = json.loads(config_path.read_text(encoding="utf-8"))
    targets: dict[str, CoinTarget] = {}

    for section in ("holdings", "watchlist"):
        for entry in payload.get(section, []):
            coin_id = entry.get("id")
            symbol = entry.get("symbol")
            if not coin_id or not symbol:
                continue
            targets[coin_id] = CoinTarget(id=coin_id, symbol=symbol.upper())

    if not targets:
        raise ValueError("No valid coin targets found in config.")

    return list(targets.values())


def fetch_market_data(
    targets: list[CoinTarget],
    vs_currency: str,
    timeout_seconds: int,
) -> list[dict[str, Any]]:
    response = requests.get(
        COINGECKO_MARKETS_URL,
        params={
            "vs_currency": vs_currency,
            "ids": ",".join(target.id for target in targets),
            "price_change_percentage": "24h,7d",
            "sparkline": "false",
        },
        timeout=timeout_seconds,
    )
    response.raise_for_status()
    market_rows = response.json()
    if not isinstance(market_rows, list):
        raise ValueError("Unexpected CoinGecko response shape; expected list.")
    return market_rows


def normalize_rows(
    market_rows: list[dict[str, Any]],
    symbol_by_id: dict[str, str],
) -> list[dict[str, Any]]:
    fetched_at = datetime.now(timezone.utc).isoformat()
    normalized: list[dict[str, Any]] = []

    for row in market_rows:
        coin_id = row.get("id")
        if not coin_id:
            continue
        normalized.append(
            {
                "fetched_at": fetched_at,
                "id": coin_id,
                "symbol": symbol_by_id.get(coin_id, str(row.get("symbol", "")).upper()),
                "name": row.get("name"),
                "current_price": row.get("current_price"),
                "market_cap": row.get("market_cap"),
                "market_cap_rank": row.get("market_cap_rank"),
                "total_volume": row.get("total_volume"),
                "high_24h": row.get("high_24h"),
                "low_24h": row.get("low_24h"),
                "price_change_24h": row.get("price_change_24h"),
                "price_change_percentage_24h": row.get("price_change_percentage_24h"),
                "price_change_percentage_7d_in_currency": row.get(
                    "price_change_percentage_7d_in_currency"
                ),
                "circulating_supply": row.get("circulating_supply"),
                "last_updated": row.get("last_updated"),
            }
        )

    return normalized


def write_snapshot(output_dir: Path, rows: list[dict[str, Any]]) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    snapshot_path = output_dir / f"prices_{datetime.now(timezone.utc).strftime('%Y%m%d')}.csv"

    fieldnames = [
        "fetched_at",
        "id",
        "symbol",
        "name",
        "current_price",
        "market_cap",
        "market_cap_rank",
        "total_volume",
        "high_24h",
        "low_24h",
        "price_change_24h",
        "price_change_percentage_24h",
        "price_change_percentage_7d_in_currency",
        "circulating_supply",
        "last_updated",
    ]

    write_header = not snapshot_path.exists()
    with snapshot_path.open("a", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        writer.writerows(rows)

    return snapshot_path


def main() -> int:
    args = parse_args()
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )

    config_path = Path(args.config).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()

    targets = load_targets(config_path)
    market_rows = fetch_market_data(
        targets=targets,
        vs_currency=args.vs_currency,
        timeout_seconds=args.timeout_seconds,
    )
    symbol_by_id = {target.id: target.symbol for target in targets}
    normalized_rows = normalize_rows(market_rows, symbol_by_id=symbol_by_id)
    snapshot_path = write_snapshot(output_dir, normalized_rows)

    LOGGER.info(
        "Fetched %s coins and appended snapshot to %s",
        len(normalized_rows),
        snapshot_path,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
