# llama.cpp Integration Assessment

_Last updated: 2026-04-03_

## Installation status

| Check | Result |
|-------|--------|
| `which llama-server` / `which llama-cli` on PATH | **Not on PATH** in the scan run (`which` only resolved `ollama`). |
| Repo binary | **`/home/jonat/ai-stack/llama.cpp/llama-server`** exists as an **ELF x86-64 executable** (built artifact in the submodule/tree). |
| `build/bin` | **No** `llama.cpp/build/` tree in this checkout; binary lives at repo root of `llama.cpp`. |
| `~/.local/bin`, `/usr/local/bin` | No `llama*` matches in the quick scan. |

## Capability: server mode

**Yes.** `/home/jonat/ai-stack/llama.cpp/llama-server --help` prints standard llama.cpp server flags (common params, threads, etc.). Typical usage:

```bash
/home/jonat/ai-stack/llama.cpp/llama-server -m /path/to/model.gguf --port 8090 -ngl 99
```

FAITHH can treat it as an **OpenAI-compatible HTTP** endpoint by configuring a `type: openai_compatible` provider pointing at `http://localhost:<port>/v1` (same pattern as `local_webui` in `configs/model_config.yaml`).

## Available GGUF models (sample from host scan)

**Instruction / chat weights**

- `/home/jonat/text-generation-webui/user_data/models/qwen2.5-14b-instruct-q4_k_m-00001-of-00003.gguf` (multi-part)
- `/home/jonat/text-generation-webui/user_data/models/qwen2.5-14b-instruct-q4_k_m-00002-of-00003.gguf`
- `/home/jonat/text-generation-webui/user_data/models/qwen2.5-14b-instruct-q4_k_m-00003-of-00003.gguf`

**llama.cpp bundled vocab assets (not full LLMs)**

- Many `ggml-vocab-*.gguf` under `/home/jonat/ai-stack/llama.cpp/models/` (vocabulary blobs, not standalone chat models).

A full `find ~ /mnt -name '*.gguf'` was truncated at 20 lines; expect more GGUFs elsewhere on your machines.

## Recommended use cases for direct llama.cpp (vs keeping Ollama)

| Use case | Recommended runtime | Reason |
|----------|--------------------|--------|
| Simple/fast queries (3B–7B) | llama.cpp **server** | Lower moving parts than Ollama if you only need one fixed GGUF and OpenAI-compatible clients. |
| Grounded / RAG-heavy (custom Ollama models) | **Ollama** | Model pulls, tags, and existing FAITHH defaults target Ollama. |
| Large models (32B+) / multi-GPU | **Ollama** | Operational simplicity; already integrated in `docker-compose.yml`. |
| Custom fine-tuned GGUF only on disk | **llama.cpp** | Load file directly without importing into Ollama’s store. |

## Migration path for simple-query slot

1. Confirm `llama-server` runs: `/home/jonat/ai-stack/llama.cpp/llama-server --help`.
2. Obtain a small instruct GGUF (e.g. Qwen2.5-3B-Instruct Q5_K_M).
3. Start server on a dedicated port, e.g. **8090**, with suitable `-ngl` / `--ctx-size`.
4. Add a provider in `configs/model_config.yaml`, e.g. `llamacpp_local: type: openai_compatible, base_url: http://localhost:8090/v1`.
5. Extend `routes` / `build_provider_order` defaults in `backend/llm_providers.py` if you want it in the **fallback chain** (e.g. `local_webui → llamacpp_local → ollama → groq`).
6. Smoke-test with `run_llm_route` or wired `/api/chat` and verify `provider` / `model` metadata.

## Decision: migrate simple-query slot?

- [ ] **Yes** — `llama-server` confirmed, a small GGUF chosen, ops OK with an extra process.
- [x] **Defer** — Ollama already satisfies local inference; add llama.cpp when you have a concrete GGUF + port strategy.
- [ ] **No** — Ollama overhead acceptable indefinitely.

## Startup runbook (placeholder)

```bash
# Example only — adjust model path and GPU layers.
/home/jonat/ai-stack/llama.cpp/llama-server \
  -m /home/jonat/text-generation-webui/user_data/models/qwen2.5-14b-instruct-q4_k_m-00001-of-00003.gguf \
  --port 8090 \
  --ctx-size 4096 \
  -ngl 99
```

Multi-part GGUF: use the **first** shard or a merged file per llama.cpp documentation for your build.
