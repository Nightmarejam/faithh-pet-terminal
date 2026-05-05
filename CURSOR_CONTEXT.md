# CURSOR_CONTEXT.md
# Single source of truth for all Cursor sessions
# Updated: 2026-05-05
# ALWAYS read this before touching anything

## OWNER
Jonathan Morales, Albany OR. Solo developer.
Projects: FAITHH (AI infrastructure), Tom Cat Sound LLC / Floating Garden Soundworks (audio business), Constella (civic governance research), Crypto pipeline (in progress).

## INFRASTRUCTURE

| Host | LAN IP | Tailscale | Role |
|------|--------|-----------|------|
| Gen8 / servicebox | 192.158.1.10 | 100.79.85.32 | Always-on, Docker, ChromaDB, THIS REPO |
| FAITHH VM (VM 100) | 192.158.1.204 | — | RTX 3090, vLLM inference, future mining |
| Windows VM (VM 101) | — | — | GTX 1080 Ti, streaming |
| Synology NAS | 192.158.1.12 | 100.120.68.7 | 13TB, models at /mnt/nas |
| Proxmox host | 192.158.1.X | — | Ryzen 9 3900X, 64GB RAM |

Gen8 Docker services: ChromaDB :8000, Prometheus :9090, Grafana :3000, Gitea, Pihole, Vaultwarden, Plex, Uptime Kuma, cAdvisor, Alertmanager

## FAITHH BACKEND

Entry point: ~/ai-stack/faithh_professional_backend_fixed.py
Shim: ~/ai-stack/faithh_backend.py
Start: ~/ai-stack/restart_backend.sh
Log: ~/ai-stack/backend.log
Port: 5557
Python: ALWAYS use /home/jonat/ai-stack/venv/bin/python

LLM priority order (DO NOT revert):
1. Groq — llama-3.3-70b-versatile (primary)
2. Gemini 2.0 Flash (secondary)
3. vLLM on 192.158.1.204:8000 (local inference)
4. Ollama localhost:11434 (last resort)

Embedding: BAAI/bge-base-en-v1.5 — manual encoding
NEVER use query_texts= in ChromaDB calls
ALWAYS use query_embeddings=bge_model.encode([query]).tolist()

ChromaDB collections:
- faithh_knowledge_base (54,342 docs) — main RAG
- governance_corpus (18,768 docs) — Constella/civic
- faithh_session_metrics (43)
- alife_lineage (99)
- faithh_uncertainty_surface (175)

Env vars (in .env — NEVER COMMIT):
GROQ_API_KEY, GEMINI_API_KEY, ANTHROPIC_API_KEY
VLLM_HOST=http://192.158.1.204:8000
VLLM_MODEL=/mnt/nas/models/qwen2.5-14b-awq

Offline flags set in restart_backend.sh:
HF_HUB_OFFLINE=1
TRANSFORMERS_OFFLINE=1

## REPO STRUCTURE

~/ai-stack/
  faithh_professional_backend_fixed.py  ← MAIN BACKEND
  faithh_pet_v4.html                    ← MAIN UI
  restart_backend.sh                    ← start script
  config.yaml                           ← paths/security
  requirements.txt                      ← main venv deps
  .env                                  ← secrets (NEVER COMMIT)
  RUNBOOK.md
  ARCHITECTURE.md                       ← needs update to reflect current stack
  LIFE_MAP.md                           ← project compass
  FAITHH_TESTING_GUIDE.md
  CURSOR_CONTEXT.md                     ← this file
  app/
  backend/                              ← LLM provider modules
  configs/                              ← model_config.yaml
  docs/ops/
  experiments/
  knowledge_base/                       ← GITIGNORED, do not commit
    imports/claude/, chatgpt/, grok/
  projects/
    alife/                              ← ALife experiments
    tomcat-sound/                       ← Tom Cat Sound LLC
      audio-workflows/
      03_member_docs/
    crypto/                             ← NEW, to be scaffolded
  venv/                                 ← NEVER COMMIT

## ACTIVE TRACKS

### TRACK 1: Crypto Pipeline (NEXT — scaffold this session)
Location: projects/crypto/ (does not exist yet)
Host: Gen8 (always-on)
Separate venv: projects/crypto/venv/ (DO NOT use main venv)

Structure to create:
  projects/crypto/
    pipeline/
      __init__.py
      fetch_prices.py       ← G1: CoinGecko price fetcher
      ingest_whitepaper.py  ← G2: PDF → ChromaDB
      signal_engine.py      ← G3: signal logic
      mining_switch.py      ← G4: stop vLLM, start miner
    data/
      prices/
      signals/
      whitepapers/
    config/
      coins.json
    requirements.txt
    README.md

coins.json holdings: ETC (20), ZEC (1), POLY, PENGU
coins.json watchlist: BTC, ETH, KAS, RVN, ERG
New deps: pycoingecko, pandas, schedule

### TRACK 2: Mining (PENDING — parts arriving)
Host: FAITHH VM (192.158.1.204), RTX 3090
Miner: T-Rex or lolMiner (ETChash)
Pool: 2Miners
Payout: Coinbase ETC deposit address
Switch: hard line — stop vLLM then start miner, never concurrent

### TRACK 3: FAITHH Maintenance
Open: ARCHITECTURE.md needs update (Groq primary, BGE embeddings, new collection names)
Open: Verify governance_corpus intent routing (is_legal_query) still works
RAG preflight threshold: best_distance > 0.60

### TRACK 4: Proxmox Drive Migration (PENDING — parts arriving)
Plan: PVE OS → new NVMe, Windows → 970 Evo
Order: backup VMs → install drives → reinstall PVE → restore

### TRACK 5: Tom Cat Sound LLC
Location: projects/tomcat-sound/
Tax return due: Sept 15 2026 (Form 7004 filed)
Members: Jonathan 34%, Thomas 33%, Kevin 33%
Open: member meeting required before any restructuring

### TRACK 6: Gen8 T1000 Install (PENDING)
Card: NVIDIA T1000 8GB low-profile
Role: 7B inference, pipeline compute
PCIe slot: currently empty

## HARD RULES — NEVER VIOLATE

1. Never commit .env or any file with API keys
2. Never use query_texts= in ChromaDB — always use query_embeddings=
3. Never revert LLM priority order (Groq is primary)
4. Never pip install in main venv without updating requirements.txt
5. Always use venv python: /home/jonat/ai-stack/venv/bin/python
6. Never modify faithh_professional_backend_fixed.py without a backup commit first
7. Never add knowledge_base/ to git
8. Crypto pipeline uses its own venv at projects/crypto/venv/
9. Commit after each working milestone — small, descriptive commits
10. After any backend change: curl http://localhost:5557/health

## SESSION STARTUP CHECKLIST

cd ~/ai-stack && git status
curl http://localhost:5557/health
git pull origin main

## MONITORING

Grafana: http://192.158.1.10:3000
Prometheus: http://192.158.1.10:9090
FAITHH metrics: http://192.158.1.10:5557/metrics
Gen8 node_exporter: :9100
