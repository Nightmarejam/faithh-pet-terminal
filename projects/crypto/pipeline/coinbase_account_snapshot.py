#!/usr/bin/env python3
"""Read-only Coinbase Advanced Trade account and product snapshot."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from coinbase.rest import RESTClient

ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT / ".env"
OUT_DIR = ROOT / "data" / "ops"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Capture read-only Coinbase account/product snapshot")
    parser.add_argument("--accounts-limit", type=int, default=100)
    parser.add_argument("--products-limit", type=int, default=200)
    parser.add_argument("--quote-currency", default="USD")
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


def to_plain(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: to_plain(v) for k, v in value.items()}
    if isinstance(value, list):
        return [to_plain(v) for v in value]
    if hasattr(value, "__dict__"):
        return {k: to_plain(v) for k, v in vars(value).items() if not k.startswith("_")}
    return value


def normalized(value: str) -> str:
    return value.replace("\\n", "\n").strip().strip('"').strip("'")


def load_secret_candidates(env: dict[str, str]) -> list[str]:
    candidates: list[str] = []
    inline = normalized(env.get("COINBASE_API_SECRET", ""))
    if inline:
        candidates.append(inline)
    file_path = env.get("COINBASE_API_SECRET_FILE", "").strip()
    if file_path:
        p = Path(file_path).expanduser()
        if p.exists():
            candidates.append(normalized(p.read_text(encoding="utf-8")))
    return [c for c in candidates if c]


def summarize_accounts(raw: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for acc in raw.get("accounts", []) or []:
        available = acc.get("available_balance") or {}
        hold = acc.get("hold") or {}
        out.append(
            {
                "uuid": acc.get("uuid"),
                "name": acc.get("name"),
                "currency": acc.get("currency"),
                "type": acc.get("type"),
                "ready": acc.get("ready"),
                "default": acc.get("default"),
                "available_value": available.get("value"),
                "available_currency": available.get("currency"),
                "hold_value": hold.get("value"),
                "hold_currency": hold.get("currency"),
            }
        )
    return out


def summarize_products(raw: dict[str, Any], quote_ccy: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for p in raw.get("products", []) or []:
        product_id = str(p.get("product_id", ""))
        if f"-{quote_ccy}" not in product_id and f"-USDC" not in product_id:
            continue
        out.append(
            {
                "product_id": product_id,
                "status": p.get("status"),
                "trading_disabled": p.get("trading_disabled"),
                "is_disabled": p.get("is_disabled"),
                "base_currency_id": p.get("base_currency_id"),
                "quote_currency_id": p.get("quote_currency_id"),
                "base_increment": p.get("base_increment"),
                "quote_increment": p.get("quote_increment"),
                "price": p.get("price"),
                "volume_24h": p.get("volume_24h"),
            }
        )
    out.sort(key=lambda r: r.get("product_id", ""))
    return out


def fetch_snapshot(args: argparse.Namespace) -> dict[str, Any]:
    env = load_env(ENV_PATH)
    api_key = env.get("COINBASE_API_KEY", "")
    api_secrets = load_secret_candidates(env)
    if not api_key or not api_secrets:
        raise RuntimeError("Missing COINBASE_API_KEY or API secret (inline or file) in projects/crypto/.env")

    last_error: Exception | None = None
    accounts_resp: dict[str, Any] | None = None
    products_resp: dict[str, Any] | None = None
    for secret in api_secrets:
        try:
            client = RESTClient(api_key=api_key, api_secret=secret)
            accounts_resp = to_plain(client.get_accounts(limit=args.accounts_limit))
            products_resp = to_plain(client.get_products(limit=args.products_limit))
            last_error = None
            break
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            continue
    if last_error or accounts_resp is None or products_resp is None:
        raise RuntimeError(f"Coinbase snapshot auth failed: {last_error}")

    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "quote_currency_filter": args.quote_currency,
        "accounts_summary": summarize_accounts(accounts_resp),
        "products_summary": summarize_products(products_resp, args.quote_currency.upper()),
        "raw_counts": {
            "accounts_total": len(accounts_resp.get("accounts", []) or []),
            "products_total": len(products_resp.get("products", []) or []),
        },
    }


def write_snapshot(payload: dict[str, Any]) -> tuple[Path, Path]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    ts_path = OUT_DIR / f"coinbase_snapshot_{stamp}.json"
    latest_path = OUT_DIR / "coinbase_snapshot_latest.json"
    blob = json.dumps(payload, indent=2)
    ts_path.write_text(blob, encoding="utf-8")
    latest_path.write_text(blob, encoding="utf-8")
    return ts_path, latest_path


def main() -> int:
    args = parse_args()
    payload = fetch_snapshot(args)
    ts_path, latest_path = write_snapshot(payload)
    print(
        json.dumps(
            {
                "timestamped": str(ts_path),
                "latest": str(latest_path),
                "accounts_total": payload["raw_counts"]["accounts_total"],
                "products_total": payload["raw_counts"]["products_total"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
