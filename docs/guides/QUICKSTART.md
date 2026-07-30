# FAITHH Quick-Start Manual

**Last Updated:** 2026-04-12  
**Backend Version:** v4.x (canonical `faithh_professional_backend_fixed.py`)  
**Port:** 5557

---

## Start FAITHH (One Command)

```bash
cd ~/ai-stack && ./restart_backend.sh
```

This will:
1. Stop any running instances
2. Free port 5557
3. Start the backend using `venv/bin/python`
4. Wait for health check to pass
5. Print the UI URL

**UI:** http://localhost:5557

---

## Stop FAITHH

```bash
cd ~/ai-stack && ./stop_backend.sh
```

---

## WSL2 troubleshooting (stack alignment)

Use this when the UI or RAG “works sometimes” but fails after upgrades or network changes.

| Symptom | What to check |
|--------|-----------------|
| **Wrong GPU / Ollama sees 1080 Ti instead of 3090** | Repo `.env`: `CUDA_VISIBLE_DEVICES`, `FAITHH_CUDA_PHYSICAL_DEVICE`, `FAITHH_STRICT_LLM_GPU`. Windows `.wslconfig` with `gpus=all`, then `wsl --shutdown`. Full notes: [WSL2_MULTI_GPU.md](WSL2_MULTI_GPU.md). |
| **Chroma / RAG timeouts from WSL** | Gen8 Chroma defaults to **LAN** `servicebox.taileb8c60.ts.net:8000` in code and `.env.example`. Set `CHROMA_HOST` in **repo-root `.env`** to the address your WSL box can reach (LAN vs Tailscale). Stale **100.x** examples in old docs are not the canonical default. **Ops vs data:** Prometheus `node_exporter` on Gen8 may stay on **100.x** (`:9100`); the **hot RAG path** is Chroma **:8000** on LAN unless you explicitly override. |
| **Windows Defender / WSL2 “bridge”** | If `localhost:5557` works from WSL `curl` but not from Edge/Chrome on Windows, check **Windows Defender Firewall** rules for WSL/Hyper-V adapters and for **allowing local Node/Python listeners**. Prefer **loopback** access via `http://localhost:5557/` or `http://127.0.0.1:5557/` (same origin as typical dev). After changing firewall or WSL networking mode, run `wsl --shutdown` and reopen the distro. |
| **Browser chat fails with private-network / CORS (file vs localhost)** | The backend enables private-network access for local development (`allow_private_network=True` on CORS). Prefer the served UI at `http://localhost:5557/` rather than opening `faithh_pet_v4.html` as a `file://` URL. |
| **Streaming errors after Werkzeug 3** | `/api/chat` SSE paths yield **bytes** (not `str`) for compatibility with Werkzeug 3. If you patch streaming, keep generator chunks as UTF-8-encoded bytes. |

After changing `.env`, restart: `./restart_backend.sh`.

---

## Check Status

```bash
# Health check
curl http://localhost:5557/health

# Canonical PLC + embedded runtime status (prefer this over /api/status)
curl -s http://localhost:5557/api/plc/state | python3 -m json.tool | head -80
# Runtime slice only (same as GET /api/status)
curl -s http://localhost:5557/api/plc/state | python3 -c "import json,sys; print(json.dumps(json.load(sys.stdin).get('faithh_status',{}), indent=2))"

# Integration test (verifies memory, decisions, project states load)
curl http://localhost:5557/api/test_integrations | python3 -m json.tool
```

---

## Cockpit Smoke Test

Use this before/after cockpit or status-layer changes:

```bash
cd /home/jonat/ai-stack
bash scripts/smoke_cockpit.sh
```

The smoke script ends with **ecosystem baseline probe** (PLC + health + ping chat). For full timing including a minimal LLM call and optional RAG:

```bash
./venv/bin/python scripts/ecosystem_baseline_probe.py
./venv/bin/python scripts/ecosystem_baseline_probe.py --with-rag
```

See `docs/architecture/ECOSYSTEM_METRICS.md`.

Manual fallback (if script is unavailable):

```bash
cd /home/jonat/ai-stack
bash scripts/refresh_dashboard_data.sh
python3 scripts/impact_analyzer.py --component api_plc_state
```

Reference: `docs/guides/COCKPIT_DEPENDENCY_RUNBOOK.md`

---

## Model Providers

FAITHH supports Groq, Ollama, Gemini, and **Anthropic (Claude)**. Set the default in `~/ai-stack/.env`:

```bash
# In .env:
MODEL_PROVIDER=groq    # Cloud (fast, free tier)
# MODEL_PROVIDER=ollama  # Local (RTX 3090, private)
# MODEL_PROVIDER=gemini  # Cloud (Google)
```

You can also override per-request from the UI or API:
```bash
curl -X POST http://localhost:5557/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "provider": "ollama", "model": "llama31-faithh:latest"}'
```

### Anthropic (Claude)

1. Add `ANTHROPIC_API_KEY=sk-ant-api03-...` to **repo-root** `.env` (same tree as `faithh_professional_backend_fixed.py`). Create keys in the [Anthropic Console](https://console.anthropic.com/). Use **no** surrounding quotes and **no** trailing space on the line — extra whitespace often causes `401` / `invalid x-api-key`. Valid Console keys start with **`sk-ant-`**; if you pasted a Groq/OpenAI key here, Anthropic will always return `401`. After restart, read the backend startup line: if you see a warning about the prefix, fix the key. The backend reloads `.env` from the repo root with python-dotenv (so it can correct values that bash `source` mishandled).
2. Restart: `cd ~/ai-stack && ./restart_backend.sh`
3. **UI:** Pick a **Claude** model explicitly (not **Auto**). Auto-routing can replace `provider` / `model` and rarely chooses Anthropic. For the shortest path to “just call Claude,” turn **Knowledge Base / RAG** off so the request uses `use_rag: false` and skips heavy retrieval before the LLM. The chat response field **`response_time`** is **end-to-end** handler time (intent, context, optional RAG, then the provider), not Anthropic-only latency.

**Verify the key** (from repo root, with venv; fails fast if the key is missing):

```bash
cd ~/ai-stack
./venv/bin/python -c "from anthropic import Anthropic; import os; from dotenv import load_dotenv; load_dotenv(); c=Anthropic(api_key=os.environ['ANTHROPIC_API_KEY'].strip()); print(c.messages.create(model='claude-3-haiku-20240307', max_tokens=10, messages=[{'role':'user','content':'hi'}]).content[0].text)"
```

### Available Ollama Models (Local)

| Model | Size | Purpose |
|-------|------|---------|
| `llama31-faithh:latest` | 4.9 GB | Default FAITHH model (Llama 3.1 8B) |
| `llama31-clean:latest` | 4.9 GB | Base Llama 3.1 (no persona) |
| `qwen3-faithh:latest` | 18 GB | Qwen 3 with FAITHH config |
| `qwen3-clean:latest` | 18 GB | Base Qwen 3 |
| `deepseek-r1:32b` | 19 GB | DeepSeek reasoning model |
| `qwen2.5-coder:14b` | 9.0 GB | Code-focused model |
| `qwen2.5:7b` | 4.7 GB | General Qwen 2.5 |

### Ollama Management

```bash
# Check if Ollama is running
systemctl status ollama

# Start Ollama (with GPU config)
sudo systemctl start ollama

# List loaded models
ollama list

# Pull a new model
ollama pull llama3.1:8b

# Create custom model from modelfile
ollama create llama31-faithh -f ~/ai-stack/modelfiles/llama31-clean.Modelfile
```

**GPU Config:** Ollama runs on GPU 1 (RTX 3090) via systemd override at  
`/etc/systemd/system/ollama.service.d/override.conf`

**KV cache (long context on 24 GB VRAM):** Set `OLLAMA_FLASH_ATTENTION=1` and `OLLAMA_KV_CACHE_TYPE=q8_0` on the **Ollama** service (not FAITHH `.env` alone). See **[OLLAMA_KV_ENV.md](OLLAMA_KV_ENV.md)**.

---

## Key API Endpoints

### Chat
```bash
curl -X POST http://localhost:5557/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What projects am I working on?"}'
```

### RAG Search (Direct)
```bash
curl -X POST http://localhost:5557/api/rag_search \
  -H "Content-Type: application/json" \
  -d '{"query": "ChromaDB setup"}'
```

### Compass (Project Direction)
```bash
curl http://localhost:5557/api/compass
```

### PULSE (Security/Health)
```bash
curl http://localhost:5557/api/pulse/status
curl http://localhost:5557/api/pulse/health/check
curl http://localhost:5557/api/pulse/chips
```

### Filesystem Operations
```bash
curl http://localhost:5557/api/filesystem/capabilities
```

### Context Collectors
```bash
curl http://localhost:5557/api/context/collectors
```

---

## How FAITHH Thinks (Chip System)

When you send a message, FAITHH runs these steps:

1. **Intent Detection** — Analyzes your query for patterns:
   - `is_self_query` → Asking about FAITHH itself
   - `is_project_query` → Asking about projects
   - `is_why_question` → Asking about decisions/rationale
   - `is_next_action_query` → Asking what to work on
   - `is_business_query` → Tom Cat Sound / audio business
   - `is_constella_query` → Constella framework
   - `needs_orientation` → "Where was I?" type questions

2. **Parallel Chip Retrieval** — 7 chips fire concurrently:
   - `self_awareness` → From `faithh_memory.json`
   - `project_state` → From `project_states.json`
   - `decisions` → From `decisions_log.json`
   - `scaffolding` → From `scaffolding_state.json`
   - `constella` → Constella awareness context
   - `conversation_history` → Recent session turns
   - `rag_search` → ChromaDB semantic search (32,499 chunks)

3. **Token Budgeting** — Each chip gets a token budget (4,500 total):
   - RAG: 40% | Scaffolding: 20% | Decisions: 15%
   - Project State: 10% | Constella: 10% | Self: 10%

4. **LLM Call** — Combined context + personality → provider (Groq/Ollama/Gemini)

---

## Key Files

```
~/ai-stack/
├── faithh_professional_backend_fixed.py  # THE backend (canonical)
├── faithh_pet_v4.html                    # THE frontend (canonical, ROOT level)
├── .env                                  # API keys, provider config
├── config.yaml                           # Tool system config
├── restart_backend.sh                    # Start script
├── stop_backend.sh                       # Stop script
├── backend.log                           # Runtime logs
│
├── faithh_memory.json                    # AI self-awareness + user profile
├── project_states.json                   # Machine-readable project state
├── decisions_log.json                    # Decision history with rationale
├── scaffolding_state.json                # Session continuity
├── faithh_knowledge_graph.yaml           # Entity graph
│
├── CONTEXT.md                            # Auto-generated AI injection doc
├── SYSTEMS_MAP.md                        # Comprehensive systems map
├── LIFE_MAP.md                           # Philosophy and "why"
├── MASTER_CONTEXT.md                     # Technical overview
│
├── scripts/generate_context.py           # Regenerate CONTEXT.md
├── modelfiles/                           # Ollama model definitions
└── venv/                                 # Python virtual environment
```

---

## Troubleshooting

### Backend won't start
```bash
# Check if port is in use
lsof -i :5557

# Check logs
tail -50 ~/ai-stack/backend.log

# Check venv exists
ls ~/ai-stack/venv/bin/python
```

### WSL2: `curl` works in Linux but Windows browser shows NetworkError

`curl http://127.0.0.1:5557/health` inside WSL only proves the server is listening **inside the VM**. The Windows browser uses a separate path (localhost forwarding / loopback policy). Try in order:

**1. Loopback exemption (UWP / Store browsers)**  
From **Windows Command Prompt** (often elevated), for Microsoft Store Edge:

```bat
checknetisolation LoopbackExempt -a -n="Microsoft.MicrosoftEdge_8wekyb3d8bbwe"
```

This mainly helps **packaged** apps. **Desktop Chrome or Firefox** often ignore this; if nothing changes, go to step 2.

**2. Use the WSL IP from Windows**  
In WSL:

```bash
hostname -I
```

Pick the primary IPv4 (commonly `172.x.x.x`). On Windows, open `http://<that-ip>:5557`. The canonical backend binds `0.0.0.0:5557`, so this should work without code changes. If this works but `127.0.0.1` does not, the problem is localhost forwarding, not FAITHH.

**3. Cold reset the WSL network stack**  
Close WSL terminals. On **Windows** (PowerShell or cmd, admin if needed):

```powershell
wsl --shutdown
```

Wait ~10 seconds, reopen WSL, then:

```bash
cd ~/ai-stack && ./restart_backend.sh
```

Retry `http://127.0.0.1:5557`. The same shutdown is documented for GPU resets in [WSL2_MULTI_GPU.md](WSL2_MULTI_GPU.md); it also rebuilds the WSL virtual NIC / NAT and often fixes “ghosted” localhost forwarding.

**4. Firewall (if step 2 is flaky)**  
If you rely on the WSL IP, Windows Defender Firewall may need an **inbound allow** rule for **TCP 5557** (private network scope). Try only if problems persist after step 3.

### Ollama not responding
```bash
# Check systemd status
systemctl status ollama

# Restart with GPU config
sudo systemctl restart ollama

# Verify GPU access
nvidia-smi
```

### ChromaDB unreachable
```bash
# Check Gen8 is up
ping -c 2 servicebox.taileb8c60.ts.net

# Check ChromaDB heartbeat
curl http://servicebox.taileb8c60.ts.net:8000/api/v2/heartbeat
```

### RAG returns irrelevant results
- ChromaDB collection: `faithh_knowledge_base_v2`
- ~63.7k chunks with **`BAAI/bge-base-en-v1.5` (768-dim)** embeddings
- First check the dimension invariant — the backend prints it on the first query.
  A `best_distance` of exactly 1.0 on every query means the embedder and the
  collection disagree, or distances were dropped in code. See
  [EMBEDDINGS.md](../architecture/EMBEDDINGS.md).
- To re-index docs: `python scripts/ingest/index_docs.py` (embed on the workstation,
  never on the Gen8)

---

## Regenerate Context Document

```bash
# Regenerate CONTEXT.md from source files
python3 scripts/generate_context.py

# Also create an immutable framing snapshot
python3 scripts/generate_context.py --snapshot

# Preview without writing
python3 scripts/generate_context.py --dry-run
```

---

## Service Dependencies

| Service | Location | Required? |
|---------|----------|-----------|
| FAITHH Backend | localhost:5557 (WSL2) | ✅ Yes |
| Ollama | localhost:11434 (WSL2, systemd) | For local models only |
| ChromaDB | servicebox.taileb8c60.ts.net:8000 (Gen8) | For RAG search |
| Groq API | api.groq.com | For Groq provider |
| Gemini API | Google Cloud | For Gemini provider |

**Minimum to run:** Backend + at least one LLM provider (Groq works without Ollama or ChromaDB).

---

**End of Quick-Start Manual**
