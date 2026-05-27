# FAITHH stack runbook

*Last updated: 2026-05-25*

---

## Architecture

```
Claude Code CLI  ──► cc_proxy.py (5558)  ──► vLLM (8000)
                                               qwen3-coder-30b-a3b-awq

Browser / tools  ──► Backend Flask (5557) ──► configs/model_config.yaml
                                               routes: vllm → ollama → groq
                      anthropic_shim.py
                      (speaks /v1/messages)

ChromaDB         ──► 192.158.1.10:8000
                     faithh_knowledge_base_v2  (canonical, 33k docs)
                     governance_corpus          (18k docs)
                     alife_lineage              (339k docs)
```

---

## Starting the stack

```bash
cd ~/ai-stack
bash start_faithh.sh
# monitor in tmux:
tmux attach -t faithh
```

The orchestrator (`.faithh_orch.sh`) starts in order:
1. vLLM on port 8000 — waits up to 180s for health check
2. cc_proxy on port 5558
3. Backend Flask on port 5557

### Start vLLM only

```bash
cd ~/ai-stack
bash start_vllm.sh
# takes ~60-90s to load, watch with:
tail -f vllm.log
```

### Start Claude Code against local stack

```bash
export ANTHROPIC_BASE_URL=http://localhost:5558
export ANTHROPIC_API_KEY=faithh-local
claude
```

---

## vLLM configuration

**Model:** `~/models/qwen3-coder-30b-a3b-awq` (16G, AWQ quantized)

**Key parameters in `start_vllm.sh`:**

| Parameter | Value | Notes |
|---|---|---|
| `--max-model-len` | 65536 | max context window; clients must not exceed this |
| `--gpu-memory-utilization` | 0.90 | leaves ~2.4GB for OS/other |
| `--kv-cache-dtype` | fp8_e5m2 | reduces KV cache memory by ~2x |
| `--enable-prefix-caching` | on | reuses KV cache across similar prompts |
| `--tool-call-parser` | qwen3_coder | required for tool use |
| served names | qwen3-coder-30b, claude-sonnet-4-6, claude-opus-4-7 | all route to same model |

**Known fix (2026-05-25):** `max_model_len` raised from 32768 → 65536 to stop
`VLLMValidationError: max_completion_tokens=64000` errors.

---

## cc_proxy configuration

File: `~/ai-stack/cc_proxy.py`

- Listens on port **5558**
- Translates Anthropic `/v1/messages` → OpenAI `/v1/chat/completions`
- Forwards to `localhost:8000` (vLLM)
- Token cap: `min(requested, 32768)` — raised from 4096 on 2026-05-25
- Model names `claude-sonnet-4-6` and `claude-opus-4-7` both route to qwen3-coder-30b

---

## Backend routing

File: `~/ai-stack/configs/model_config.yaml`

Route priority order:
- `auto`: vllm → local_webui → ollama → groq
- `code`: vllm → local_webui → groq → ollama
- `local`: vllm → local_webui → ollama
- `fast`: groq → vllm → local_webui → ollama

The backend falls through to the next provider if the current one is down.
When vLLM is not running, requests fall through to ollama or groq automatically.

---

## Claude export pipeline

### What exists

| Script | Purpose |
|---|---|
| `scripts/ingest_claude_export.py` | Diff-based ingestion into v2 — canonical entry point |
| `scripts/faithh_conversation_tagger.py` | Tag by category/novelty/canvas, write CANVAS.md |
| `scripts/audit_exports.py` | Inspect export files for structure |
| `scripts/chunk_claude_chats.py` | Chunking utility |
| `scripts/indexing/index_chat_exports.py` | Older indexing path — use ingest_claude_export.py instead |

### Running an ingestion

```bash
cd ~/ai-stack
source venv/bin/activate

# 1. ingest new export
python3 scripts/ingest_claude_export.py \
  ~/ai-stack/knowledge_base/imports/claude/conversations.json

# 2. tag + build canvas
python3 scripts/faithh_conversation_tagger.py

# dry run first to preview classifications
python3 scripts/faithh_conversation_tagger.py --dry-run

# re-tag everything (after changing category signals)
python3 scripts/faithh_conversation_tagger.py --reset
```

### Canvas output

`~/ai-stack/docs/CANVAS.md` — auto-generated, do not edit by hand.
Big picture items are conversations tagged `big_picture` (novelty ≥ 0.3 +
canvas topic keywords). Re-run tagger after each ingestion to keep current.

---

## ChromaDB collections

Only use `faithh_knowledge_base_v2` for new work. All others are legacy.

| Collection | Docs | Status |
|---|---|---|
| faithh_knowledge_base_v2 | 33,853 | **canonical** — correct embedding dimensions |
| faithh_knowledge_base | 56,066 | legacy — wrong dimensions for ML chips |
| governance_corpus | 18,768 | active |
| alife_lineage | 339,900 | active |
| faithh_session_metrics | 43 | active |
| faithh_uncertainty_surface | 175 | active |
| tomcat_sound_kb | 0 | empty |
| fgs_research_kb | 0 | empty |

### Metadata schema in v2

```
conversation_id    str    uuid from Claude export
conversation_title str    human-readable title
source             str    "claude" | "chatgpt"
chunk_index        int    0-based chunk position
export_date        str    ISO date
indexed_at         str    ISO datetime
document_type      str    "chat_export"
domain             str    "live_conversation"
category           str    coding|hypothesis|learning|civic|system|personal|misc
novelty_score      str    "0.0"-"1.0"
canvas_tag         str    big_picture|active|background|archive
```

---

## Performance

At current settings on RTX 3090 (24GB):

- Load time: ~60-90s
- VRAM used: ~20-21GB (90% of 24GB)
- Throughput: ~25-35 tokens/sec for 30B AWQ at 32k context
- Prefix cache hit rate: improves significantly after first few requests

### Tuning levers

To improve throughput at the cost of max context:
```bash
# in start_vllm.sh
--max-model-len 32768     # halves KV cache reservation
--gpu-memory-utilization 0.92
```

To improve quality at the cost of speed, remove `--kv-cache-dtype fp8_e5m2`.

---

## Troubleshooting

**vLLM won't start / OOM:**
```bash
# check VRAM is clear
nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits
# should be < 1000 MiB before starting
pkill -9 -f "vllm serve"
fuser -k 8000/tcp
```

**max_completion_tokens error:**
The client is requesting more output tokens than `max_model_len`. Either
raise `--max-model-len` in `start_vllm.sh` or cap the client request.
Current limit: 65536.

**cc_proxy returns empty / error:**
```bash
tail -20 ~/ai-stack/cc_proxy.log
curl -s http://localhost:8000/health
curl -s http://localhost:5558/
```

**Backend not routing to vLLM:**
Check `configs/model_config.yaml` — vllm must be first in the route list.
Check vLLM is healthy: `curl -s http://localhost:8000/v1/models`.
