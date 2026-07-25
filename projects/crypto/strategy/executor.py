from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, Any

from strategy.conditions import evaluate_dip_buy
from chain.balance import get_default_portfolio_snapshot


def run_dry_strategy(coin_id: str = "ethereum", dip_threshold_pct: float = 5.0, intended_usdc_size: float = 25.0) -> Dict[str, Any]:
    signal = evaluate_dip_buy(coin_id=coin_id, dip_threshold_pct=dip_threshold_pct)
    balances = get_default_portfolio_snapshot()

    decision = "hold"
    reason = "dip threshold not met"
    if signal["should_buy"]:
        decision = "paper-buy"
        reason = "dip threshold met"

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "mode": "dry-run",
        "decision": decision,
        "reason": reason,
        "intended_usdc_size": intended_usdc_size,
        "signal": signal,
        "balances": balances,
        "execution": "no transaction submitted",
    }
