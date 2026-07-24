# FAITHH Ecosystem — Cursor/Windsurf Session Context
Last verified: 2026-05-11

## Stack state (all confirmed working this session)

| Component | Status | Address |
|---|---|---|
| FAITHH backend | ✅ Running | http://faithh.taileb8c60.ts.net:5557 |
| ChromaDB | ✅ Running | servicebox.taileb8c60.ts.net:8000 |
| vLLM | ✅ Running | http://faithh.taileb8c60.ts.net:8000 |
| Groq | ✅ Configured | llama-3.3-70b-versatile |
| SSH | ✅ Working | ssh faithh (jonat@faithh.taileb8c60.ts.net) |

## Backend entrypoint

`~/ai-stack/faithh_professional_backend_fixed.py` — clean Flask rebuild, ~200 lines.

Start via: `bash ~/ai-stack/restart_backend.sh`
Or directly: `cd ~/ai-stack && source venv/bin/activate && python faithh_professional_backend_fixed.py`

### What it does
- `GET /` — serves faithh_pet.html (v4 UI)
- `GET /health` — health check
- `GET /api/status` — service status (Groq, ChromaDB, vLLM)
- `POST /api/chat` — RAG + Groq (primary) + vLLM (fallback)
- `GET /api/pulse/chips` — stub, returns empty (PULSE not rebuilt yet)
- CORS enabled via flask-cors
- BGE embeddings (BAAI/bge-base-en-v1.5) — never use query_texts= directly
- Collection: faithh_knowledge_base (54,342 docs)

### What's missing vs the April 12th monolith (6,482 lines)
- PULSE Reflection Engine (staleness, divergence, branch explorer)
- Compass Director (`/api/compass`, `/api/compass/director`)
- SSE streaming on `/api/chat`
- `/api/pulse/audit/*`, `/api/pulse/health/*`, `/api/pulse/security/scan`
- `/api/context/collectors/status`
- Prometheus `/api/metrics`
- Security middleware, caching, session metrics

These are the next things to rebuild. The monolith exists in git at `097e5f3` for reference.

## Frontend

`~/ai-stack/faithh_pet.html` — recovered faithh_pet_v4.html (3,720 lines, Jan 2026 era)
`~/ai-stack/faithh_cockpit.html` — recovered March 14 cockpit with live data panels
`~/ai-stack/images/faithh.png` — recovered (535KB)
`~/ai-stack/images/pulse.png` — recovered (74KB)
`~/ai-stack/favicon.ico` — recovered

Access: http://faithh.taileb8c60.ts.net:5557 (main UI), http://faithh.taileb8c60.ts.net:5557/faithh_cockpit.html (cockpit)

## Git state

Repo: https://github.com/Nightmarejam/faithh-pet-terminal
Branch: main
Local and origin/main: IN SYNC as of 2026-05-11
Recovery branch: recovery/march14 (keep, useful reference)

### Other GitHub repos
- constella-framework — ALife/civic OS, independent, last updated 2026-04-02
- runbook-to-rule-them-all — ops docs, stale since 2026-04-02
- celestial-equilibrium — dormant since 2025-08-14

### Key commits
- `097e5f3` — April 12 snapshot, last known good full monolith (6,482 lines)
- `0336adc` — March 14, cockpit + live data, compass routes
- `3bfde73` — faithh_pet.html canonicalized (v3 UI)
- `14b06fa` — Feb 7, faithh_pet_v4.html deleted here (recoverable from parent)
- `ab8de12` — Oct 2025, images/faithh.png and images/pulse.png last committed

## Infrastructure

| Host | Role | IP |
|---|---|---|
| faithh VM (Proxmox) | FAITHH backend, vLLM, inference | faithh.taileb8c60.ts.net |
| Gen8 NAS | ChromaDB, Plex, file storage | servicebox.taileb8c60.ts.net |
| Windows (bare metal) | Dev workstation, Windsurf, browser | desktop-iifeikl.taileb8c60.ts.net |

## .env location
`~/ai-stack/.env` — contains GROQ_API_KEY, CHROMA_*, BACKEND_PORT=5557

## Key facts — don't re-investigate
- Inner monologue engine (IME): WAS committed as C++ code (commit 201523d, March 2026) with journal_reader.cpp, resonance_gate.cpp, tests, and documentation. Removed during P2V backup recovery. Can be restored from git history if needed.
- All files in ~/ai-stack/backend/ from P2V backup are Ollama/Gemini era (wrong stack)
- faithh_professional_backend_fixed.py is the ONLY correct entrypoint
- ChromaDB collections: faithh_knowledge_base (54,342), governance_corpus (18,768)
- BGE model caches to ~/.cache/huggingface after first load
- Groq model llama3-70b-8192 is DECOMMISSIONED — use llama-3.3-70b-versatile
- No WSL needed — VM over SSH is the dev environment
- GitHub PAT needs rotation after house project completes

## Parked projects (valid but not now)
- Proxmox/Windows bare metal separation
- MOTU AVB audio (828ES at 192.168.1.5)
- Tom Cat Sound LLC — Kevin Dunn 33% withdrawal not executed
- Crypto trading bot — RTX 3090 mining ETC ~107 MH/s, net -$0.70/day
- vLLM inference quality eval for coding (Continue.dev integration)

## Next session priorities
1. Add SSE streaming to /api/chat
2. Stub remaining compass/pulse endpoints so UI stops erroring
3. Rebuild /api/compass with live project_states.json data
4. Rotate GitHub PAT
5. Test faithh_cockpit.html with live backend data
