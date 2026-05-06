#!/usr/bin/env python3
"""Score paper trade decisions against future price snapshots."""

from __future__ import annotations

import argparse
import csv
import json
import logging
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

LOGGER = logging.getLogger("crypto.paper_trade_journal")

ROOT = Path(__file__).resolve().parents[1]
TRADING_DIR = ROOT / "data" / "trading"
PRICES_DIR = ROOT / "data" / "prices"
HORIZONS_MIN = [60, 360, 1440]  # 1h, 6h, 24h

JOURNAL_FIELDS = [
    "order_timestamp",
    "symbol",
    "coin_id",
    "side",
    "quantity",
    "order_price_usd",
    "horizon_min",
    "future_timestamp",
    "future_price_usd",
    "decision_edge_usd",
    "decision_outcome",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate paper trade outcomes across time horizons.")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    return parser.parse_args()


def parse_iso(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def load_orders() -> list[dict[str, Any]]:
    files = sorted(TRADING_DIR.glob("paper_orders_*.csv"))
    if not files:
        return []
    rows: list[dict[str, Any]] = []
    for path in files:
        with path.open(newline="", encoding="utf-8") as fp:
            rows.extend(csv.DictReader(fp))
    return rows


def load_price_index() -> dict[str, list[tuple[datetime, float]]]:
    index: dict[str, list[tuple[datetime, float]]] = defaultdict(list)
    for path in sorted(PRICES_DIR.glob("prices_*.csv")):
        with path.open(newline="", encoding="utf-8") as fp:
            for row in csv.DictReader(fp):
                coin_id = row.get("id")
                ts = row.get("fetched_at")
                px = row.get("current_price")
                if not coin_id or not ts or not px:
                    continue
                try:
                    index[coin_id].append((parse_iso(ts), float(px)))
                except ValueError:
                    continue
    for coin_id in index:
        index[coin_id].sort(key=lambda x: x[0])
    return index


def first_price_at_or_after(series: list[tuple[datetime, float]], target: datetime) -> tuple[datetime, float] | None:
    for ts, px in series:
        if ts >= target:
            return ts, px
    return None


def evaluate_order(order: dict[str, Any], prices: dict[str, list[tuple[datetime, float]]]) -> list[dict[str, Any]]:
    coin_id = order.get("coin_id")
    side = str(order.get("side", "")).upper()
    if not coin_id or coin_id not in prices:
        return []
    try:
        order_ts = parse_iso(order["timestamp"])
        qty = float(order["quantity"])
        order_px = float(order["price_usd"])
    except (KeyError, ValueError):
        return []

    out: list[dict[str, Any]] = []
    for horizon in HORIZONS_MIN:
        future_target = order_ts + timedelta(minutes=horizon)
        matched = first_price_at_or_after(prices[coin_id], future_target)
        if not matched:
            out.append(
                {
                    "order_timestamp": order["timestamp"],
                    "symbol": order.get("symbol"),
                    "coin_id": coin_id,
                    "side": side,
                    "quantity": qty,
                    "order_price_usd": order_px,
                    "horizon_min": horizon,
                    "future_timestamp": "",
                    "future_price_usd": "",
                    "decision_edge_usd": "",
                    "decision_outcome": "pending",
                }
            )
            continue

        future_ts, future_px = matched
        # For SELL decisions, positive edge means selling beat holding.
        edge_usd = (order_px - future_px) * qty
        outcome = "good" if edge_usd > 0 else "bad" if edge_usd < 0 else "neutral"
        out.append(
            {
                "order_timestamp": order["timestamp"],
                "symbol": order.get("symbol"),
                "coin_id": coin_id,
                "side": side,
                "quantity": round(qty, 8),
                "order_price_usd": round(order_px, 8),
                "horizon_min": horizon,
                "future_timestamp": future_ts.isoformat(),
                "future_price_usd": round(future_px, 8),
                "decision_edge_usd": round(edge_usd, 8),
                "decision_outcome": outcome,
            }
        )
    return out


def write_journal(rows: list[dict[str, Any]]) -> Path:
    TRADING_DIR.mkdir(parents=True, exist_ok=True)
    path = TRADING_DIR / f"paper_journal_{datetime.now(timezone.utc):%Y%m}.csv"
    with path.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=JOURNAL_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    return path


def write_summary(rows: list[dict[str, Any]]) -> Path:
    by_horizon: dict[int, dict[str, float]] = {}
    grouped: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[int(row["horizon_min"])].append(row)

    for horizon, items in grouped.items():
        resolved = [i for i in items if i["decision_outcome"] != "pending" and i["decision_edge_usd"] != ""]
        if not resolved:
            by_horizon[horizon] = {"count": 0, "avg_edge_usd": 0.0, "win_rate": 0.0}
            continue
        wins = sum(1 for i in resolved if i["decision_outcome"] == "good")
        avg_edge = sum(float(i["decision_edge_usd"]) for i in resolved) / len(resolved)
        by_horizon[horizon] = {
            "count": len(resolved),
            "avg_edge_usd": round(avg_edge, 8),
            "win_rate": round(wins / len(resolved), 4),
        }

    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "horizons": by_horizon,
    }
    out = TRADING_DIR / "latest_paper_journal_summary.json"
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return out


def main() -> int:
    args = parse_args()
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )

    orders = load_orders()
    if not orders:
        LOGGER.warning("No paper orders found to evaluate.")
        return 0

    prices = load_price_index()
    journal_rows: list[dict[str, Any]] = []
    for order in orders:
        journal_rows.extend(evaluate_order(order, prices))

    journal_path = write_journal(journal_rows)
    summary_path = write_summary(journal_rows)
    LOGGER.info("journal_rows=%d journal_path=%s", len(journal_rows), journal_path)
    LOGGER.info("summary_path=%s", summary_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
