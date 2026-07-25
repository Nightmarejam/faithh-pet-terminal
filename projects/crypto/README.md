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
<<<<<<< HEAD
  --chroma-host 192.158.1.10 \
=======
  --chroma-host servicebox.taileb8c60.ts.net \
>>>>>>> origin/main
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

### Paper execution (trader bot)

Run paper-first execution for mined coin -> USDC conversion:

```bash
python pipeline/trader_execution.py --mode paper --log-level INFO
```

Outputs:

- `data/trading/paper_balances.json` (virtual balances)
- `data/trading/paper_orders_YYYYMM.csv` (simulated executed orders)
- `data/trading/latest_paper_summary.json` (run summary + skipped reasons)

Notes:

- Live mode is intentionally blocked until paper results are validated.
- Put future Coinbase credentials in `projects/crypto/.env` (see `.env.example`).

### Paper trade journal (learning loop)

Score paper decisions over 1h/6h/24h horizons:

```bash
python pipeline/paper_trade_journal.py --log-level INFO
```

Outputs:

- `data/trading/paper_journal_YYYYMM.csv` (decision outcomes by horizon)
- `data/trading/latest_paper_journal_summary.json` (win-rate and average edge)

### Miner stats in shared data pool

`pipeline/mining_ledger.py` now exports miner context for other pipeline stages:

- `data/pool/latest_miner_stats.json` (latest snapshot)
- `data/pool/miner_stats_YYYYMMDD.jsonl` (append-only stream)

### Profit candidates (hourly ranking)

Generate ranked mine-now / hold / avoid candidates:

```bash
python pipeline/profit_candidates.py --log-level INFO
```

Outputs:

- `data/signals/profit_candidates_YYYYMMDD.json`
- `data/signals/latest_candidates.json`
<<<<<<< HEAD

### API readiness check

Validate env format and endpoint access:

```bash
python pipeline/api_readiness_check.py
```

Outputs:

- `data/ops/api_readiness_YYYYMMDDTHHMMSSZ.json`
- `data/ops/api_readiness_latest.json`

### Coinbase account snapshot (read-only)

Capture accounts + tradable USD/USDC products:

```bash
python pipeline/coinbase_account_snapshot.py --quote-currency USD
```

Outputs:

- `data/ops/coinbase_snapshot_YYYYMMDDTHHMMSSZ.json`
- `data/ops/coinbase_snapshot_latest.json`

### Datadog Knowledge Center snapshot

Collect Datadog observability reference pages into machine-readable local files:

```bash
python pipeline/datadog_knowledge_snapshot.py --max-pages 25
```

Outputs:

- `data/ops/datadog_kc_snapshot_YYYYMMDDTHHMMSSZ.json`
- `data/ops/datadog_kc_snapshot_latest.json`
- `data/ops/datadog_kc_pages_YYYYMMDDTHHMMSSZ.jsonl`
=======
>>>>>>> origin/main
