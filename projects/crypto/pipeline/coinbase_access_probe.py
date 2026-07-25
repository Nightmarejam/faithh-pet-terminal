#!/usr/bin/env python3
"""Read-only Coinbase Advanced Trade access probe."""

from __future__ import annotations

import json
from pathlib import Path

from coinbase.rest import RESTClient


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


def classify_key_type(api_key: str, api_secret: str) -> str:
    if api_secret.startswith("-----BEGIN"):
        return "cdp_private_key_pem"
    if api_key.startswith("organizations/"):
        return "cdp_key_name_missing_pem"
    if "-" in api_secret and len(api_secret) < 64:
        return "likely_legacy_or_wrong_secret_format"
    return "unknown_format"


def main() -> int:
    env_path = Path(__file__).resolve().parents[1] / ".env"
    env = load_env(env_path)
    api_key = env.get("COINBASE_API_KEY", "")
    api_secret = env.get("COINBASE_API_SECRET", "")
    passphrase = env.get("COINBASE_API_PASSPHRASE", "")

    result: dict[str, object] = {
        "env_path": str(env_path),
        "env_present": env_path.exists(),
        "key_present": bool(api_key),
        "secret_present": bool(api_secret),
        "passphrase_present": bool(passphrase),
        "key_format_guess": classify_key_type(api_key, api_secret),
        "probe_result": "not_run",
        "accounts_visible": None,
        "error_type": None,
        "error_preview": None,
    }

    if not api_key or not api_secret:
        result["probe_result"] = "missing_credentials"
        print(json.dumps(result, indent=2))
        return 0

    try:
        client = RESTClient(api_key=api_key, api_secret=api_secret)
        resp = client.get_accounts(limit=5)
        if isinstance(resp, dict):
            accounts = resp.get("accounts", [])
        else:
            accounts = getattr(resp, "accounts", []) or []
        result["probe_result"] = "ok"
        result["accounts_visible"] = len(accounts)
    except Exception as exc:  # noqa: BLE001
        result["probe_result"] = "error"
        result["error_type"] = type(exc).__name__
        result["error_preview"] = str(exc)[:300]

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
