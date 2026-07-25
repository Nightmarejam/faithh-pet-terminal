# Performance baseline cycle (CLI vs API vs UI)

Use this to estimate **where time goes** for the same natural-language query: context/RAG assembly, local LLM, HTTP/JSON, and browser work.

## Shared query

Use the same string for all three paths, for example:

`How does ALIFE integrate with FAITHH RAG?`

## Path A — Baseline (in-process Python)

No Flask, no browser. Loads `faithh_professional_backend_fixed` once (Chroma + embedder init), then times:

1. `detect_query_intent` + `get_optimal_model_for_query`
2. `build_integrated_context` → logged as **`rag_ms`**
3. Optional local **`call_ollama_chat`** → logged as **`llm_ms`**

```bash
cd ~/ai-stack
venv/bin/python scripts/benchmark_baseline.py
# Align with local grounded calibration (same model as OLLAMA_GROUNDED_MODEL):
venv/bin/python scripts/benchmark_baseline.py --grounded
# Context + chips only (no Ollama call):
venv/bin/python scripts/benchmark_baseline.py --context-only
venv/bin/python scripts/benchmark_baseline.py --context-only --grounded
```

Rows in `logs/performance.log` have **`"request_source": "baseline_cli"`**.

## Path B — API (curl)

Minimal JSON (no lean registry); matches a simple CLI client.

```bash
curl -s -X POST http://127.0.0.1:5557/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "How does ALIFE integrate with FAITHH RAG?", "stream": false}'
```

Rows use **`request_source": "api"`** (or **`ui`** if the browser sends `Origin` / a typical UA).

## Path C — UI

Open `http://localhost:5557/`, send the **same** message in chat. Rows typically show **`request_source": "ui"`** plus **`workspace_registry_json_bytes`** and **`lean_workspace_registry`** when the lean snapshot is attached.

## Reading `logs/performance.log`

Each line is JSON. Compare **`total_ms`**, **`rag_ms`**, **`llm_ms`** for the same `query_preview`.

Rough “tax” estimates (same machine, same query):

| Tax | Idea |
|-----|------|
| **Network / API** | `(API total_ms) − (baseline total_ms)` — Flask, JSON, extra middleware |
| **UI / registry** | `(UI total_ms) − (API total_ms)` — fetch, SSE vs JSON, larger payloads, DOM |

If **UI − API** is large while **`workspace_registry_json_bytes`** is high, registry/context attachment is a likely contributor. If **`rag_ms`** dominates everywhere, Chroma / embedding / chip parallelism is the bottleneck before the LLM.

## Emergency recovery (surgical)

```bash
./scripts/emergency_recovery.sh
```

This targets **gunicorn** and **`faithh_professional_backend_fixed.py`**, frees **:5557**, then runs **`restart_backend.sh`**. It does **not** run `pkill -9 -f "python"`.

## UI note: streaming and markdown

During SSE, the assistant bubble updates on a **50ms throttle** via `flushUpdateBuffer`, which runs **`marked.parse(updateBuffer)`** on the **entire growing assistant reply** each flush, with **highlight.js** inside Marked’s code renderer. That is **not** a full-history re-render of all messages, but it **does** re-parse the **whole partial answer** repeatedly and can get expensive for long, code-heavy streams.
