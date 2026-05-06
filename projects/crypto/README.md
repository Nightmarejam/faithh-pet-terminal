# Crypto Pipeline

Opportunistic mining and trading intelligence workflow.

## Current status

- G1 implemented in `pipeline/fetch_prices.py` (live via cron every 15 minutes)
- G2 implemented in `pipeline/ingest_whitepaper.py` (PDF -> chunk -> ChromaDB)
- G3 implemented in `pipeline/signal_engine.py` (momentum + volume signals)
- G4 implemented in `pipeline/mining_switch.py` (inference/mining mode switch)

## Layout

- `pipeline/fetch_prices.py`: CoinGecko market data fetcher
- `pipeline/ingest_whitepaper.py`: whitepaper ingestion into ChromaDB
- `pipeline/signal_engine.py`: signal generation from CSV snapshots
- `pipeline/mining_switch.py`: mode switch orchestration for faithh
- `config/coins.json`: holdings, mining targets, market context, thresholds
- `data/prices/`: price snapshots + fetch logs
- `data/signals/`: generated signal outputs (`latest_signals.json`)
- `data/whitepapers/`: downloaded PDFs + ingestion logs

## Usage

### G1 fetch prices

```bash
python pipeline/fetch_prices.py
```

### G2 ingest whitepaper

```bash
# URL source
python pipeline/ingest_whitepaper.py \
  --source "https://bitcoin.org/bitcoin.pdf" \
  --symbol BTC \
  --chroma-host 192.158.1.10 \
  --chroma-port 8000 \
  --collection faithh_knowledge_base
```

Notes:

- If `--embedding-model` is omitted, the script infers a compatible model from the existing Chroma collection embedding dimension.
- You can force a model explicitly, e.g. `--embedding-model "sentence-transformers/all-MiniLM-L6-v2"`.

### G3 generate signals

```bash
python pipeline/signal_engine.py
```

Output files:

- timestamped: `data/signals/signals_YYYYMMDDTHHMMSSZ.json`
- rolling pointer: `data/signals/latest_signals.json`

### G4 switch modes

```bash
# derive mode from latest signals (safe dry-run)
python pipeline/mining_switch.py --target auto --dry-run

# force inference mode
python pipeline/mining_switch.py --target inference

# force mining mode (provide miner start command)
python pipeline/mining_switch.py \
  --target mining \
  --require-gpu-free \
  --miner-start-cmd "nohup /opt/miner/start.sh > /tmp/miner.log 2>&1 &"
```

### Monitoring

Run full stack monitoring snapshot:

```bash
python pipeline/monitor_stack.py
```

Outputs:

- `data/monitoring/latest_status.json` (human-readable state + alerts)
- `data/monitoring/crypto_stack.prom` (Prometheus text format)
