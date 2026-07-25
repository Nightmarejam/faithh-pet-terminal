from __future__ import annotations

from decimal import Decimal
from typing import Dict, Any

from web3 import Web3
from .connect import get_connection, get_wallet_address_or_none

ERC20_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "", "type": "uint256"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "symbol",
        "outputs": [{"name": "", "type": "string"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    },
]

USDC_BASE = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
WETH_BASE = "0x4200000000000000000000000000000000000006"


def get_native_balance_eth(wallet: str) -> Decimal:
    w3 = get_connection()
    wei = w3.eth.get_balance(wallet)
    return Decimal(str(w3.from_wei(wei, "ether")))


def get_erc20_balance(token_address: str, wallet: str) -> Dict[str, str]:
    w3 = get_connection()
    token = w3.eth.contract(address=Web3.to_checksum_address(token_address), abi=ERC20_ABI)

    raw = token.functions.balanceOf(wallet).call()
    decimals = int(token.functions.decimals().call())
    symbol = str(token.functions.symbol().call())
    normalized = Decimal(raw) / (Decimal(10) ** Decimal(decimals))

    return {
        "token": symbol,
        "address": Web3.to_checksum_address(token_address),
        "raw": str(raw),
        "decimals": str(decimals),
        "balance": str(normalized),
    }


def get_default_portfolio_snapshot() -> Dict[str, Any]:
    wallet = get_wallet_address_or_none()
    if not wallet:
        return {
            "wallet": None,
            "note": "Set TRADING_WALLET_ADDRESS in .env for real balance reads",
            "eth": None,
            "usdc": None,
            "weth": None,
        }

    return {
        "wallet": wallet,
        "eth": str(get_native_balance_eth(wallet)),
        "usdc": get_erc20_balance(USDC_BASE, wallet)["balance"],
        "weth": get_erc20_balance(WETH_BASE, wallet)["balance"],
    }
