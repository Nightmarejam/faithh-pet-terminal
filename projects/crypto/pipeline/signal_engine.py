#!/usr/bin/env python3
"""Generate ranked opportunistic mining/trading signals from local data."""

from __future__ import annotations

import argparse
import csv
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

LOGGER = logging.getLogger("crypto.signal_engine")

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "coins.json"
PRICES_DIR = ROOT / "data" / "prices"
SIGNALS_DIR = ROOT / "data" / "signals"
CANDIDATES_PATH = SIGNALS_DIR / "latest_candidates.json"

DEFAULTS = {
    "signal_threshold": 0.05,
    "volume_spike_multiplier": 1.15,
    "volume_baseline_samples": 6,
    "strong_momentum_multiplier": 2.5,
    "opportunity_min_score": 2,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build ranked signals from price and candidate data.")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    return parser.parse_args()


def load_config() -> dict[str, Any]:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def resolve_latest_prices_file() -> Path:
    candidates = sorted(PRICES_DIR.glob("prices_*.csv"))
    if not candidates:
        raise FileNotFoundError("No price files found in data/prices/")
    return candidates[-1]


def load_price_history() -> dict[str, list[dict[str, Any]]]:
    history: dict[str, list[dict[str, Any]]] = {}
    with resolve_latest_prices_file().open(newline="", encoding="utf-8") as fp:
        for row in csv.DictReader(fp):
            coin_id = row.get("id")
            if not coin_id:
                continue
            history.setdefault(coin_id, []).append(row)
    return history


def load_candidates() -> dict[str, dict[str, Any]]:
    if not CANDIDATES_PATH.exists():
        return {}
    payload = json.loads(CANDIDATES_PATH.read_text(encoding="utf-8"))
    out: dict[str, dict[str, Any]] = {}
    for row in payload.get("ranked", []):
        coin_id = row.get("coin_id")
        if coin_id:
            out[coin_id] = row
    return out


def tracked_coin_entries(config: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for section, coin_type in [
        ("holdings", "holding"),
        ("mining_targets", "mining_target"),
        ("market_context", "market_context"),
    ]:
        for entry in config.get(section, []):
            out.append({"coin_type": coin_type, **entry})
    return out


def to_float(value: Any, fallback: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return fallback


def baseline_avg(values: list[float], n: int) -> float:
    sample = values[-n:] if len(values) >= n else values
    if not sample:
        return 0.0
    return sum(sample) / len(sample)


def classify_signal(
    entry: dict[str, Any],
    price_rows: list[dict[str, Any]],
    candidate_row: dict[str, Any] | None,
    thresholds: dict[str, float],
) -> dict[str, Any]:
    latest = price_rows[-1]
    threshold = thresholds["signal_threshold"]
    strong_threshold = threshold * thresholds["strong_momentum_multiplier"]

    momentum_7d = to_float(latest.get("price_change_percentage_7d_in_currency"), 0.0) / 100.0
    momentum_24h = to_float(latest.get("price_change_percentage_24h"), 0.0) / 100.0
    latest_volume = to_float(latest.get("total_volume"), 0.0)
    volumes = [to_float(r.get("total_volume"), 0.0) for r in price_rows if r.get("total_volume")]
    volume_base = baseline_avg(volumes[:-1] if len(volumes) > 1 else volumes, int(thresholds["volume_baseline_samples"]))
    volume_ratio = (latest_volume / volume_base) if volume_base > 0 else 0.0
    volume_spike = volume_ratio >= thresholds["volume_spike_multiplier"] if volume_base > 0 else False

    net_daily_usd = None
    profitability_action = None
    if candidate_row:
        net_daily_usd = to_float(candidate_row.get("net_daily_usd"), 0.0)
        profitability_action = candidate_row.get("action")

    score = 0
    if momentum_7d >= threshold:
        score += 1
    if momentum_7d >= strong_threshold or momentum_24h >= strong_threshold:
        score += 1
    if volume_spike:
        score += 1
    if net_daily_usd is not None:
        if net_daily_usd > 0:
            score += 2
        elif net_daily_usd > -0.25:
            score += 1

    classification = "none"
    if score >= int(thresholds["opportunity_min_score"]):
        classification = "opportunity"
    elif score >= 1:
        classification = "watch"

    out = {
        "coin_id": entry["id"],
        "symbol": entry.get("symbol"),
        "name": latest.get("name"),
        "coin_type": entry["coin_type"],
        "fetched_at": latest.get("fetched_at"),
        "price_usd": to_float(latest.get("current_price")),
        "market_cap": to_float(latest.get("market_cap")),
        "total_volume": latest_volume,
        "momentum_24h": round(momentum_24h, 6),
        "momentum_24h_pct": round(momentum_24h * 100, 4),
        "momentum_7d": round(momentum_7d, 6),
        "momentum_7d_pct": round(momentum_7d * 100, 4),
        "momentum_trigger": momentum_7d >= threshold,
        "strong_momentum_trigger": (momentum_7d >= strong_threshold or momentum_24h >= strong_threshold),
        "volume_spike": volume_spike,
        "volume_baseline": round(volume_base, 6),
        "volume_ratio": round(volume_ratio, 4),
        "classification": classification,
        "score": score,
        "thresholds": {
            "signal_threshold": threshold,
            "volume_spike_multiplier": thresholds["volume_spike_multiplier"],
            "volume_baseline_samples": int(thresholds["volume_baseline_samples"]),
            "strong_momentum_multiplier": thresholds["strong_momentum_multiplier"],
            "opportunity_min_score": int(thresholds["opportunity_min_score"]),
        },
    }
    if entry["coin_type"] == "mining_target":
        out["mining"] = {"algorithm": entry.get("algorithm"), "gpu": entry.get("gpu", [])}
    if candidate_row:
        out["profitability"] = {
            "net_daily_usd": round(to_float(candidate_row.get("net_daily_usd")), 6),
            "expected_daily_usd": round(to_float(candidate_row.get("expected_daily_usd")), 6),
            "action": profitability_action,
        }
    return out


def write_outputs(payload: dict[str, Any]) -> tuple[Path, Path]:
    SIGNALS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    timestamped = SIGNALS_DIR / f"signals_{ts}.json"
    latest = SIGNALS_DIR / "latest_signals.json"
    content = json.dumps(payload, indent=2)
    timestamped.write_text(content, encoding="utf-8")
    latest.write_text(content, encoding="utf-8")
    return timestamped, latest


def build_signals(config: dict[str, Any]) -> dict[str, Any]:
    settings = config.get("settings", {})
    engine_settings = settings.get("signal_engine", {})
    thresholds = {
        "signal_threshold": float(settings.get("signal_threshold", DEFAULTS["signal_threshold"])),
        "volume_spike_multiplier": float(
            engine_settings.get("volume_spike_multiplier", DEFAULTS["volume_spike_multiplier"])
        ),
        "volume_baseline_samples": int(
            engine_settings.get("volume_baseline_samples", DEFAULTS["volume_baseline_samples"])
        ),
        "strong_momentum_multiplier": float(
            engine_settings.get("strong_momentum_multiplier", DEFAULTS["strong_momentum_multiplier"])
        ),
        "opportunity_min_score": int(
            engine_settings.get("opportunity_min_score", DEFAULTS["opportunity_min_score"])
        ),
    }

    price_history = load_price_history()
    candidates = load_candidates()
    signals: list[dict[str, Any]] = []

    for entry in tracked_coin_entries(config):
        coin_id = entry.get("id")
        if not coin_id or coin_id not in price_history:
            continue
        signals.append(
            classify_signal(
                entry=entry,
                price_rows=price_history[coin_id],
                candidate_row=candidates.get(coin_id),
                thresholds=thresholds,
            )
        )

    signals.sort(key=lambda s: (s["score"], s.get("momentum_7d", 0.0)), reverse=True)
    opportunities = [s for s in signals if s["classification"] == "opportunity"]
    watch = [s for s in signals if s["classification"] == "watch"]

    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_prices_file": str(resolve_latest_prices_file()),
        "signal_count": len(signals),
        "opportunities": opportunities,
        "watchlist": watch,
        "all_signals": signals,
    }


def main() -> int:
    args = parse_args()
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )
    config = load_config()
    payload = build_signals(config)
    timestamped, latest = write_outputs(payload)
    LOGGER.info("Generated %d signals from %s", payload["signal_count"], payload["source_prices_file"])
    LOGGER.info("Output: %s", timestamped)
    LOGGER.info("Latest: %s", latest)
    LOGGER.info(
        "Opportunities: %d, Watch: %d",
        len(payload["opportunities"]),
        len(payload["watchlist"]),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
