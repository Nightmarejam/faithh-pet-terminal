from __future__ import annotations

from typing import Dict
import requests

COINGECKO_SIMPLE = "https://api.coingecko.com/api/v3/simple/price"
COINGECKO_COIN = "https://api.coingecko.com/api/v3/coins/{id}"


def get_price_usd(coin_id: str = "ethereum") -> float:
    r = requests.get(COINGECKO_SIMPLE, params={"ids": coin_id, "vs_currencies": "usd"}, timeout=10)
    r.raise_for_status()
    return float(r.json()[coin_id]["usd"])


def get_24h_change(coin_id: str = "ethereum") -> float:
    r = requests.get(COINGECKO_COIN.format(id=coin_id), params={"localization": "false", "tickers": "false"}, timeout=10)
    r.raise_for_status()
    return float(r.json()["market_data"]["price_change_percentage_24h"])


def evaluate_dip_buy(coin_id: str = "ethereum", dip_threshold_pct: float = 5.0) -> Dict[str, float | bool]:
    price = get_price_usd(coin_id)
    change_24h = get_24h_change(coin_id)
    should_buy = change_24h <= -abs(dip_threshold_pct)
    return {
        "coin_id": coin_id,
        "price_usd": price,
        "change_24h_pct": change_24h,
        "dip_threshold_pct": -abs(dip_threshold_pct),
        "should_buy": should_buy,
    }
