# Crypto Pipeline

Scaffold for the opportunistic miner data workflow.

## Scope of this session

- G1 implemented in `pipeline/fetch_prices.py`
- G2/G3/G4 scaffolded as placeholders only

## Layout

- `pipeline/fetch_prices.py`: CoinGecko market data fetcher
- `pipeline/ingest_whitepaper.py`: G2 placeholder
- `pipeline/signal_engine.py`: G3 placeholder
- `pipeline/mining_switch.py`: G4 placeholder
- `config/coins.json`: holdings + watchlist seed config
- `data/prices/`: CSV snapshots written here
- `data/signals/`: reserved for signal outputs
- `data/whitepapers/`: reserved for whitepaper assets

## Usage

```bash
python pipeline/fetch_prices.py
```
