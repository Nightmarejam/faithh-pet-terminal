from __future__ import annotations

import os
from typing import Optional
from web3 import Web3

DEFAULT_BASE_RPC = "https://mainnet.base.org"


def get_connection() -> Web3:
    rpc_url = os.getenv("BASE_RPC_URL", DEFAULT_BASE_RPC)
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    if not w3.is_connected():
        raise ConnectionError(f"Cannot connect to RPC: {rpc_url}")
    return w3


def get_wallet_address_or_none() -> Optional[str]:
    wallet = os.getenv("TRADING_WALLET_ADDRESS", "").strip()
    if not wallet:
        return None
    if not Web3.is_address(wallet):
        raise ValueError("TRADING_WALLET_ADDRESS is not a valid EVM address")
    return Web3.to_checksum_address(wallet)


def get_signing_account_or_none(w3: Web3):
    key = os.getenv("TRADING_WALLET_KEY", "").strip()
    if not key:
        return None
    return w3.eth.account.from_key(key)
