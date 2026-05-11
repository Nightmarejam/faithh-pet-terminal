#!/usr/bin/env python3
"""Paper-first trade execution for mined coin -> USDC conversion."""

from __future__ import annotations

import argparse
import csv
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

LOGGER = logging.getLogger("crypto.trader_execution")

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "coins.json"
ENV_PATH = ROOT / ".env"
TRADING_DIR = ROOT / "data" / "trading"
BALANCES_PATH = TRADING_DIR / "paper_balances.json"
SUMMARY_PATH = TRADING_DIR / "latest_paper_summary.json"
ORDERS_PREFIX = "paper_orders"

ORDER_FIELDS = [
    "timestamp",
    "mode",
    "symbol",
    "coin_id",
    "side",
    "price_usd",
    "quantity",
    "notional_usd",
    "fee_pct",
    "fee_usd",
    "net_usdc",
    "reason",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Paper-first trader execution runner.")
    parser.add_argument(
        "--mode",
        default="paper",
        choices=["paper", "live"],
        help="Execution mode. Live mode is not implemented yet.",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
    )
    return parser.parse_args()


def load_config() -> dict[str, Any]:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def load_env_file(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    parsed: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        parsed[key.strip()] = value.strip()
    return parsed


def merged_env() -> dict[str, str]:
    # OS vars override file vars for easy local overrides.
    result = load_env_file(ENV_PATH)
    result.update({k: v for k, v in os.environ.items() if isinstance(v, str)})
    return result


def coinbase_credentials_status(env: dict[str, str]) -> dict[str, bool]:
    key = bool(env.get("COINBASE_API_KEY"))
    secret = bool(env.get("COINBASE_API_SECRET"))
    passphrase = bool(env.get("COINBASE_API_PASSPHRASE"))
    return {"key_present": key, "secret_present": secret, "passphrase_present": passphrase}


def resolve_latest_prices_file() -> Path:
    prices_dir = ROOT / "data" / "prices"
    candidates = sorted(prices_dir.glob("prices_*.csv"))
    if not candidates:
        raise FileNotFoundError("No price snapshots found in data/prices/")
    return candidates[-1]


def load_latest_prices() -> dict[str, dict[str, Any]]:
    path = resolve_latest_prices_file()
    with path.open(newline="", encoding="utf-8") as fp:
        rows = list(csv.DictReader(fp))
    if not rows:
        raise RuntimeError(f"Price file has no rows: {path}")

    # Keep most recent row per coin id.
    latest: dict[str, dict[str, Any]] = {}
    for row in rows:
        coin_id = row.get("id")
        if coin_id:
            latest[coin_id] = row
    return latest


def seed_balances_from_holdings(config: dict[str, Any]) -> dict[str, float]:
    balances: dict[str, float] = {"USDC": 0.0}
    for holding in config.get("holdings", []):
        symbol = holding.get("symbol")
        held = holding.get("held")
        if not symbol:
            continue
        if isinstance(held, (int, float)):
            balances[symbol.upper()] = float(held)
        else:
            balances[symbol.upper()] = 0.0
    return balances


def load_balances(config: dict[str, Any]) -> dict[str, float]:
    if BALANCES_PATH.exists():
        data = json.loads(BALANCES_PATH.read_text(encoding="utf-8"))
        return {k.upper(): float(v) for k, v in data.items()}
    return seed_balances_from_holdings(config)


def save_balances(balances: dict[str, float]) -> None:
    TRADING_DIR.mkdir(parents=True, exist_ok=True)
    BALANCES_PATH.write_text(json.dumps(balances, indent=2), encoding="utf-8")


def holdings_map(config: dict[str, Any]) -> dict[str, str]:
    out: dict[str, str] = {}
    for entry in config.get("holdings", []):
        symbol = entry.get("symbol")
        coin_id = entry.get("id")
        if symbol and coin_id:
            out[symbol.upper()] = coin_id
    return out


def append_orders(orders: list[dict[str, Any]]) -> Path:
    TRADING_DIR.mkdir(parents=True, exist_ok=True)
    out_path = TRADING_DIR / f"{ORDERS_PREFIX}_{datetime.now(timezone.utc):%Y%m}.csv"
    write_header = not out_path.exists()
    with out_path.open("a", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=ORDER_FIELDS)
        if write_header:
            writer.writeheader()
        writer.writerows(orders)
    return out_path


def write_summary(summary: dict[str, Any]) -> None:
    TRADING_DIR.mkdir(parents=True, exist_ok=True)
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2), encoding="utf-8")


def run_paper_execution(config: dict[str, Any]) -> int:
    prices_by_id = load_latest_prices()
    balances = load_balances(config)
    symbol_to_id = holdings_map(config)
    settings = config.get("settings", {})
    trader_bot = settings.get("trader_bot", {})
    sell_triggers = trader_bot.get("sell_triggers", {})
    fee_pct = float(trader_bot.get("max_direct_fee_pct", 0.5)) / 100.0
    target_currency = str(trader_bot.get("job1_target_currency", "USDC")).upper()

    orders: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    timestamp = datetime.now(timezone.utc).isoformat()

    for symbol, trigger in sell_triggers.items():
        symbol_up = symbol.upper()
        qty = float(balances.get(symbol_up, 0.0))
        min_balance = float(trigger.get("min_balance", 0.0))
        min_usd = float(trigger.get("min_usd_value", 0.0))
        coin_id = symbol_to_id.get(symbol_up)

        if not coin_id:
            skipped.append({"symbol": symbol_up, "reason": "not_in_holdings"})
            continue
        if qty < min_balance or qty <= 0:
            skipped.append({"symbol": symbol_up, "reason": "below_min_balance"})
            continue

        price_row = prices_by_id.get(coin_id)
        if not price_row:
            skipped.append({"symbol": symbol_up, "reason": "no_price"})
            continue

        price_usd = float(price_row["current_price"])
        notional_usd = qty * price_usd
        if notional_usd < min_usd:
            skipped.append({"symbol": symbol_up, "reason": "below_min_usd_value"})
            continue

        fee_usd = notional_usd * fee_pct
        net_usdc = notional_usd - fee_usd

        # Paper conversion into target stablecoin.
        balances[symbol_up] = 0.0
        balances[target_currency] = float(balances.get(target_currency, 0.0)) + net_usdc

        orders.append(
            {
                "timestamp": timestamp,
                "mode": "paper",
                "symbol": symbol_up,
                "coin_id": coin_id,
                "side": "SELL",
                "price_usd": round(price_usd, 8),
                "quantity": round(qty, 8),
                "notional_usd": round(notional_usd, 6),
                "fee_pct": round(fee_pct * 100.0, 6),
                "fee_usd": round(fee_usd, 6),
                "net_usdc": round(net_usdc, 6),
                "reason": "sell_trigger_met",
            }
        )

    save_balances(balances)
    order_log_path = append_orders(orders) if orders else None
    summary = {
        "generated_at_utc": timestamp,
        "mode": "paper",
        "orders_executed": len(orders),
        "orders_path": str(order_log_path) if order_log_path else None,
        "balances_path": str(BALANCES_PATH),
        "summary": {
            "estimated_usdc_balance": round(float(balances.get(target_currency, 0.0)), 6),
            "target_currency": target_currency,
            "fee_pct_assumed": round(fee_pct * 100.0, 6),
        },
        "skipped": skipped,
    }
    write_summary(summary)

    for order in orders:
        LOGGER.info(
            "PAPER SELL %s qty=%.8f at $%.6f -> +%.4f USDC (fee %.4f)",
            order["symbol"],
            order["quantity"],
            order["price_usd"],
            order["net_usdc"],
            order["fee_usd"],
        )
    LOGGER.info(
        "paper execution complete: orders=%d usdc=%.4f summary=%s",
        len(orders),
        balances.get(target_currency, 0.0),
        SUMMARY_PATH,
    )
    return 0


def main() -> int:
    args = parse_args()
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )

    env = merged_env()
    env_mode = str(env.get("TRADER_EXECUTION_MODE", "paper")).lower()
    creds = coinbase_credentials_status(env)
    LOGGER.info(
        "env loaded: mode=%s coinbase_key=%s coinbase_secret=%s passphrase=%s",
        env_mode,
        "yes" if creds["key_present"] else "no",
        "yes" if creds["secret_present"] else "no",
        "yes" if creds["passphrase_present"] else "no",
    )

    if args.mode == "live":
        if env_mode != "live":
            raise RuntimeError(
                "Refusing live mode: TRADER_EXECUTION_MODE is not set to 'live' in projects/crypto/.env."
            )
        if not (creds["key_present"] and creds["secret_present"]):
            raise RuntimeError("Refusing live mode: missing Coinbase API key/secret in projects/crypto/.env.")
        raise NotImplementedError(
            "Live mode is intentionally disabled. Use paper mode until strategy is validated."
        )

    config = load_config()
    return run_paper_execution(config)


if __name__ == "__main__":
    raise SystemExit(main())
