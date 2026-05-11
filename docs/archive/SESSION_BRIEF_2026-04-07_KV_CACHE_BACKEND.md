# Session Brief: KV Cache Optimization & Backend Stabilization

**Date:** 2026-04-07  
**Focus:** llama.cpp KV quantization testing, Ollama configuration, backend API fixes, observability framework

---

## Quick Start (If You're Jumping In Mid-Project)

**First, fix Anthropic auth (if broken):**

1. Check `.env` has `ANTHROPIC_API_KEY=sk-ant-api03-...` (no quotes; Unix line endings).
2. `./restart_backend.sh`
3. Verify log shows `🔑 Anthropic API key configured (length=~100+ chars, no preview)` (exact wording may vary slightly; length should be large for a real Console key).
4. Run the verification script below (see **Current Blockers → Anthropic API 401**).

**Then validate the stack:**

1. UI → Model: `claude-sonnet-4-6`, RAG: **OFF**
2. Send `Hello test` → expect a response in **under ~5s** (with a valid key and RAG off).
3. Check Ollama KV: `journalctl -u ollama | grep type_k` → should show `q8_0` (when the service is configured per `docs/guides/OLLAMA_KV_ENV.md`).

This is a 30-second entry point before the rest of this brief.

---

## What We Accomplished

### 1. KV Cache Benchmarking (Complete)

Four-way VRAM benchmark: f16 @ 8K/32K + q4_0 @ 8K/32K for `qwen25-grounded-gen5-delta`.

Quality ablation: Five-prompt test across f16/q4_0/q8_0 at 8K and 32K context.

**Key findings:**

- **q8_0 @ 32K:** ~10.7 GiB total VRAM (vs ~15.1 GiB f16)
- **q4_0** sometimes refuses/clarifies prompts (behavioral regression)
- **q8_0** stays on-task with different wording (better quality-to-compression ratio)

**Recommendation:** q8_0 KV as default for 32K context on RTX 3090

### 2. PolarQuant Experiment A (Research)

Python-based compression test: 4.13× theoretical vs f16, but block-q4 beat it on reconstruction quality in this test.

**Conclusion:** Research-grade only; no llama.cpp kernel integration path today.

**Artifacts committed:** `experiment_a_results.json`, scripts, doc section

### 3. Ollama KV Configuration

**Problem:** Need `OLLAMA_FLASH_ATTENTION=1` + `OLLAMA_KV_CACHE_TYPE=q8_0` on the **Ollama server** process (not only FAITHH `.env`).

**Solution path:** systemd override at `/etc/systemd/system/ollama.service.d/override.conf`

**Status:** Instructions documented; verification pending (check `journalctl` for `type_k = 'q8_0'`)

### 4. Backend API Fixes

**Fixed:**

- Double `/api/chat` POST bug (UI was calling twice per message, discarding first response)
- Groq `_safe_get()` couldn't read list indices → empty content even on 200 OK
- Qwen3-32B reasoning model support (reads reasoning field when content is empty)
- Send button re-entrancy guard

**Remaining issue (at time of brief):**

- Anthropic 401 error: `invalid x-api-key`

**Mitigations applied in backend:**

- Load repo-root `.env` with `load_dotenv(path, override=True)` so parsed values win over bash `source` / mangled `os.environ`
- Normalize key (BOM, whitespace, wrapping quotes)
- Warn at startup if key does not start with `sk-ant-` (wrong provider’s secret is a common 401 cause)

**Next step:** Verify `ANTHROPIC_API_KEY=sk-ant-api03-...` in `.env` (no quotes), restart backend, check startup log for key length and prefix warning.

### 5. Observability Framework (New)

- **Baseline probe:** `scripts/ecosystem_baseline_probe.py` — PLC/health/chat wall-clock vs server latency
- **Metrics doc:** `docs/architecture/ECOSYSTEM_METRICS.md` (tiers: host → dependency → app → eval)
- **Connections data:** `docs/data/ecosystem_connections.json` (transport/auth/contracts)
- **Component map:** Updated `consumed_by` to match actual code paths

---

## Current Blockers

### 1. Anthropic API 401 (High Priority)

**Symptom:** `invalid x-api-key` even after backend restart

**Root cause candidates:**

- Wrong provider’s key (Groq `gsk_...` or OpenAI `sk-proj-...` instead of Anthropic `sk-ant-...`)
- Bash `source .env` mangling the value (quotes, CRLF, BOM) — mitigated by backend `override=True` + normalization; still verify file contents
- Revoked/expired key at [Anthropic Console](https://console.anthropic.com/)

**Verification script** (from `~/ai-stack`, use **`venv`** not `.venv`):

```bash
cd ~/ai-stack
source venv/bin/activate
python3 -c "
from pathlib import Path
from anthropic import Anthropic
import os
from dotenv import load_dotenv
load_dotenv(Path('.env').resolve(), override=True)
key = os.getenv('ANTHROPIC_API_KEY', '').strip()
print(f'Key prefix: {key[:12]!r} length={len(key)}')
client = Anthropic(api_key=key)
msg = client.messages.create(
    model='claude-3-haiku-20240307',
    max_tokens=10,
    messages=[{'role': 'user', 'content': 'ping'}],
)
print('OK:', msg.content[0].text)
"
```

If still 401: generate a fresh key at [console.anthropic.com/settings/keys](https://console.anthropic.com/settings/keys).

### 2. Server Response Time (68s local, 120s with RAG)

**Measured:**

- `llm_routing_latency_ms`: ~302ms (Groq) or ~68,208ms (local Ollama)
- `response_time` (server): 68–125 seconds end-to-end

**Gap = pre-LLM work:**

- RAG retrieval (Chroma @ `192.158.1.243:8000` over Tailscale)
- Chip embedding (806K+ docs indexed)
- Context assembly

**Fast path (for testing Claude API without lag):**

- UI: Turn Knowledge Base (RAG) toggle **OFF**
- Model dropdown: Select explicit `claude-sonnet-4-6` (not Auto)
- Short prompt → expect **under ~5s** with valid Anthropic key

---

## What to Test Next

### Immediate

**Fix Anthropic auth:**

```bash
# In ~/ai-stack/.env, ensure single line:
ANTHROPIC_API_KEY=sk-ant-api03-YOUR_ACTUAL_KEY_HERE
# No quotes, Unix line endings

./restart_backend.sh
# Check backend.log for:
#   🔑 Anthropic API key configured (length=... chars, no preview)
```

**Verify Ollama q8_0 KV:**

```bash
sudo systemctl daemon-reload
sudo systemctl restart ollama
MAIN=$(systemctl show -p MainPID --value ollama)
tr '\0' '\n' < /proc/$MAIN/environ | grep OLLAMA_KV
# Should show: OLLAMA_KV_CACHE_TYPE=q8_0

ollama run qwen25-grounded-gen5-delta:latest "ping"
# Check journalctl for type_k/type_v = q8_0
```

**Claude API smoke test (UI):**

- RAG: OFF  
- Model: `claude-sonnet-4-6`  
- Prompt: `Hello, test message`  
- Expected: **under ~5s**, no 401  

### This Week

**Baseline probe regression check:**

```bash
./venv/bin/python scripts/ecosystem_baseline_probe.py --out /tmp/probe_$(date +%F).json
# Compare wall_ms trends over days
```

**Real FAITHH prompts on q8_0 KV:**

- Set Pulse dashboard → OLLAMA CONTEXT = 32768
- Run 5–10 design/refactor prompts
- Compare coherence to old f16 baseline

---

## Documentation State

### New/Updated

| Document | Role |
|----------|------|
| `docs/experiments/KV_CACHE_QUANT_BENCHMARK_20260405.md` | Full benchmark + ablation tables |
| `docs/experiments/KV_EXPERIMENT_REPRO_CHECKLIST.md` | Repeatability matrix |
| `docs/architecture/ECOSYSTEM_METRICS.md` | Observability tiers |
| `docs/guides/OLLAMA_KV_ENV.md` | systemd setup |
| `docs/data/ecosystem_connections.json` | Transport/auth contracts |
| `scripts/ecosystem_baseline_probe.py` | Automated PLC/health/chat check |

### Committed Artifacts (KV vectors)

- `data/kv_vectors/llama_kv_ablation_{f16,q4_0,q8_0}_{8192,32768}.json`
- `data/kv_vectors/experiment_a_results.json` (PolarQuant)
- `data/kv_vectors/KV_ABLATION_SUMMARY.md` (auto-generated)

---

## Decisions Made

- **Default KV profile:** q8_0 @ 32K context (~10.7 GiB VRAM, quality acceptable)
- **PolarQuant:** Research only; no production integration until kernel work
- **Observability:** Layered model (connections + metrics + repeatability) alongside component map
- **Frontend chat:** Single POST `/api/chat` (fixed double-call bug)
- **Groq/Qwen3:** Added reasoning-field fallback for reasoning models

---

## Open Questions

### Architecture

**“Document crawl” for staleness:** Want PLC → auto-generate system state snapshot doc?

- **Current:** Manual reviews, `DEPS.md`, staleness scripts separate
- **Proposed:** Scheduled job: `/api/plc/state` → `docs/architecture/SYSTEM_STATE_SNAPSHOT.md`

**Git workflow for experiments:** Branches? Worktrees? Separate repo?

- **Current:** Single repo (`ai-stack`), experiments in `docs/experiments/`
- **Recommendation:** Feature branches for big spikes; `projects/status/` for active work

### Performance

**Chroma latency:** Is Tailscale to NAS (`192.158.1.243:8000`) the bottleneck for 68–120s server time?

- **Test:** Run probe with `--with-rag` on localhost Chroma vs NAS
- **Alternative:** Cache embeddings, batch queries, or move Chroma to same host

---

## Next Session Prep

**Before next Cursor session:**

- Anthropic key verified (run verification script above)
- Ollama q8_0 confirmed (`journalctl` check)
- One successful Claude chat in UI (no 401, **under ~5s** with RAG off)

**Bring to next session:**

- Probe JSON output (`/tmp/probe_*.json`)
- `nvidia-smi` screenshot during 32K Ollama chat
- **Decision:** PLC → doc auto-sync pipeline? (Y/N)

---

## System Health Snapshot *(example — 2026-04-07 session; not live)*

| Component | Notes |
|-----------|--------|
| **Backend** | `faithh_professional_backend_fixed.py` (example PID 1455, port 5557) |
| **Status** | Healthy (`GET /api/health` → 200, plc → idle) |
| **Ollama** | systemd (example PID 219), port 11434 |
| **Chroma** | NAS @ `192.158.1.243:8000`, 806K+ docs |
| **GPU** | RTX 3090, CUDA 0, ~10.7 GiB with q8_0 @ 32K (measured) |
| **Groq** | 401 if no/invalid key (example: 389 consecutive failures) |
| **Gemini** | 403 if no/invalid key |
| **Anthropic** | 401 until valid `sk-ant-` key — **fix first** |

**Priority:** Get Anthropic working, then validate q8_0 KV in production use. Everything else is optimization.
