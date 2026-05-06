#!/usr/bin/env python3
"""Rank mineable coin candidates by estimated net daily USD."""

from __future__ import annotations

import argparse
import csv
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

LOGGER = logging.getLogger("crypto.profit_candidates")

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "coins.json"
ENV_PATH = ROOT / ".env"
SIGNALS_DIR = ROOT / "data" / "signals"

DEFAULT_SWITCH_THRESHOLD_PCT = 20.0

# Symbol to 2Miners subdomain for /api/stats.
COIN_STATS_SUBDOMAIN = {
    "ETC": "etc",
    "RVN": "rvn",
    "ERG": "erg",
    "ZEC": "zec",
    # 2Miners does not currently expose a VTC pool endpoint.
}

# 3090 baseline hashrates for this setup (override via .env if desired).
ALGO_HASHRATE_DEFAULTS = {
    "ETChash": 65_000_000.0,    # H/s
    "KawPoW": 45_000_000.0,     # H/s
    "Autolykos2": 200_000_000.0,  # H/s
    "Equihash": 800.0,          # Sol/s
    "Verthash": 2_000_000.0,    # H/s (fallback only)
}

# Conservative 2026-era block rewards (override via .env BLOCK_REWARD_<SYM>).
BLOCK_REWARD_DEFAULTS = {
    "ETC": 2.048,
    "RVN": 2500.0,
    "ERG": 3.0,
    "ZEC": 1.5625,
    "VTC": 12.5,
}

# Estimated 3090 mining power by algorithm (override via .env POWER_WATTS_<ALGO>).
ALGO_POWER_WATTS_DEFAULTS = {
    "ETChash": 300.0,
    "KawPoW": 320.0,
    "Autolykos2": 250.0,
    "Equihash": 260.0,
    "Verthash": 240.0,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate ranked profitability candidates.")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    parser.add_argument("--switch-threshold-pct", type=float, default=DEFAULT_SWITCH_THRESHOLD_PCT)
    parser.add_argument("--current-miner", default="ETC")
    return parser.parse_args()


def load_config() -> dict[str, Any]:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def load_env_file(path: Path) -> dict[str, str]:
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


def merged_env() -> dict[str, str]:
    env = load_env_file(ENV_PATH)
    env.update({k: v for k, v in os.environ.items() if isinstance(v, str)})
    return env


def resolve_latest_prices_file() -> Path:
    prices_dir = ROOT / "data" / "prices"
    candidates = sorted(prices_dir.glob("prices_*.csv"))
    if not candidates:
        raise FileNotFoundError("No price snapshot found in data/prices/")
    return candidates[-1]


def load_latest_prices() -> dict[str, float]:
    latest: dict[str, float] = {}
    with resolve_latest_prices_file().open(newline="", encoding="utf-8") as fp:
        for row in csv.DictReader(fp):
            coin_id = row.get("id")
            price = row.get("current_price")
            if coin_id and price:
                try:
                    latest[coin_id] = float(price)
                except ValueError:
                    continue
    return latest


def fetch_pool_stats(symbol: str) -> dict[str, Any] | None:
    subdomain = COIN_STATS_SUBDOMAIN.get(symbol.upper())
    if not subdomain:
        return None
    url = f"https://{subdomain}.2miners.com/api/stats"
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
    except requests.RequestException:
        LOGGER.warning("stats_fetch_failed symbol=%s url=%s", symbol, url)
        return None
    return resp.json()


def env_float(env: dict[str, str], key: str, default: float) -> float:
    raw = env.get(key)
    if raw is None:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def expected_daily_coin_units(
    your_hashrate_hs: float,
    network_hashrate_hs: float,
    avg_block_time_s: float,
    block_reward_coin: float,
) -> float:
    if your_hashrate_hs <= 0 or network_hashrate_hs <= 0 or avg_block_time_s <= 0 or block_reward_coin <= 0:
        return 0.0
    blocks_per_day = 86400.0 / avg_block_time_s
    return (your_hashrate_hs / network_hashrate_hs) * blocks_per_day * block_reward_coin


def rank_candidates(
    config: dict[str, Any],
    prices: dict[str, float],
    env: dict[str, str],
    switch_threshold_pct: float,
    current_miner: str,
) -> dict[str, Any]:
    electricity_cost = env_float(env, "ELECTRICITY_COST_KWH", 0.12)
    ranked: list[dict[str, Any]] = []

    for target in config.get("mining_targets", []):
        symbol = str(target.get("symbol", "")).upper()
        coin_id = target.get("id")
        algo = target.get("algorithm")
        if not symbol or not coin_id or not algo:
            continue

        price_usd = prices.get(coin_id)
        if price_usd is None:
            ranked.append(
                {
                    "coin": symbol,
                    "coin_id": coin_id,
                    "algorithm": algo,
                    "action": "unknown",
                    "reason": "missing_price",
                }
            )
            continue

        stats = fetch_pool_stats(symbol)
        if not stats:
            ranked.append(
                {
                    "coin": symbol,
                    "coin_id": coin_id,
                    "algorithm": algo,
                    "action": "unknown",
                    "reason": "missing_stats",
                }
            )
            continue

        node = (stats.get("nodes") or [{}])[0]
        network_hashrate_hs = float(node.get("networkhashps") or 0.0)
        avg_block_time_s = float(node.get("avgBlockTime") or 0.0)
        block_reward_coin = env_float(env, f"BLOCK_REWARD_{symbol}", BLOCK_REWARD_DEFAULTS.get(symbol, 0.0))
        hashrate_hs = env_float(env, f"HASHRATE_{algo.upper()}", ALGO_HASHRATE_DEFAULTS.get(algo, 0.0))
        power_watts = env_float(env, f"POWER_WATTS_{algo.upper()}", ALGO_POWER_WATTS_DEFAULTS.get(algo, 300.0))

        daily_coin = expected_daily_coin_units(hashrate_hs, network_hashrate_hs, avg_block_time_s, block_reward_coin)
        gross_usd = daily_coin * price_usd
        power_cost_usd = (power_watts / 1000.0) * 24.0 * electricity_cost
        net_usd = gross_usd - power_cost_usd

        action = "avoid"
        if net_usd > 0.0:
            action = "mine"
        elif net_usd > -0.25:
            action = "consider"

        ranked.append(
            {
                "coin": symbol,
                "coin_id": coin_id,
                "algorithm": algo,
                "network_hashrate_hs": round(network_hashrate_hs, 4),
                "avg_block_time_s": round(avg_block_time_s, 4),
                "block_reward_coin": round(block_reward_coin, 8),
                "price_usd": round(price_usd, 8),
                "hashrate_hs": round(hashrate_hs, 4),
                "power_watts": round(power_watts, 4),
                "electricity_cost_kwh": electricity_cost,
                "expected_daily_coin": round(daily_coin, 8),
                "expected_daily_usd": round(gross_usd, 8),
                "power_cost_usd": round(power_cost_usd, 8),
                "net_daily_usd": round(net_usd, 8),
                "action": action,
            }
        )

    ranked.sort(key=lambda x: x.get("net_daily_usd", float("-inf")), reverse=True)

    current_row = next((r for r in ranked if r.get("coin") == current_miner.upper()), None)
    top_row = ranked[0] if ranked else None
    switch_recommended = False
    switch_to: str | None = None

    if top_row and current_row and top_row.get("coin") != current_row.get("coin"):
        current_net = float(current_row.get("net_daily_usd", 0.0))
        top_net = float(top_row.get("net_daily_usd", 0.0))
        if current_net <= 0 and top_net > 0:
            switch_recommended = True
            switch_to = str(top_row["coin"])
        elif current_net > 0:
            uplift_pct = ((top_net - current_net) / current_net) * 100.0 if current_net else 0.0
            if uplift_pct >= switch_threshold_pct:
                switch_recommended = True
                switch_to = str(top_row["coin"])

    return {
        "ranked": ranked,
        "current_miner": current_miner.upper(),
        "switch_recommended": switch_recommended,
        "switch_to": switch_to,
        "switch_threshold_pct": switch_threshold_pct,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def write_outputs(payload: dict[str, Any]) -> tuple[Path, Path]:
    SIGNALS_DIR.mkdir(parents=True, exist_ok=True)
    daily_path = SIGNALS_DIR / f"profit_candidates_{datetime.now(timezone.utc):%Y%m%d}.json"
    latest_path = SIGNALS_DIR / "latest_candidates.json"
    daily_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    latest_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return daily_path, latest_path


def main() -> int:
    args = parse_args()
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )
    config = load_config()
    env = merged_env()
    prices = load_latest_prices()
    payload = rank_candidates(
        config=config,
        prices=prices,
        env=env,
        switch_threshold_pct=args.switch_threshold_pct,
        current_miner=args.current_miner,
    )
    daily_path, latest_path = write_outputs(payload)
    LOGGER.info("candidates_written daily=%s latest=%s", daily_path, latest_path)
    if payload["ranked"]:
        top = payload["ranked"][0]
        LOGGER.info(
            "top_candidate coin=%s algo=%s net_daily_usd=%s action=%s",
            top.get("coin"),
            top.get("algorithm"),
            top.get("net_daily_usd"),
            top.get("action"),
        )
    LOGGER.info(
        "switch current=%s recommended=%s to=%s",
        payload["current_miner"],
        payload["switch_recommended"],
        payload["switch_to"],
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
