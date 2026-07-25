# Ecosystem metrics and repeatability

This document separates **dependency health**, **application timing**, and **client-perceived latency** so questions like “why did chat feel slow?” have a repeatable answer.

## Metric tiers

| Tier | What it measures | Where to read it |
|------|------------------|------------------|
| **Dependency** | Chroma heartbeat RTT, Ollama reachability, optional Groq/Gemini probe status | `GET /api/health` → `services.connection_monitor`; `GET /api/plc/state` → `faithh_status.services` |
| **Application (chat)** | Server time for the full `/api/chat` handler vs LLM provider round-trip only | `POST /api/chat` JSON: `response_time` (full handler), `routing_debug.llm_routing.latency_ms` (LLM slice, when present) |
| **Client-perceived** | Wall clock from request start until full response body received | Measured by [scripts/ecosystem_baseline_probe.py](../../scripts/ecosystem_baseline_probe.py) (`wall_ms` per step) |
| **Infra (optional)** | Host CPU/RAM, Prometheus scrape health | Gen8/WSL monitoring docs; not required for baseline probe |

The UI auto-route line often shows **LLM ms only**; “felt” slowness is usually **context build + RAG + Chroma** before the LLM call.

For **`provider: anthropic`**, `routing_debug.llm_routing.latency_ms` is not populated today; **`response_time`** still includes everything before `messages.create` (same ordering as other providers). Use an explicit Claude model and `use_rag: false` when you want to isolate API latency. Anthropic key checks: [QUICKSTART.md § Anthropic (Claude)](../guides/QUICKSTART.md#anthropic-claude).

## Baseline probe (first-class repeatability)

Single command to snapshot **what is running** and **how fast** critical paths are:

```bash
# Default: PLC + health + ping chat + one minimal LLM call (use_rag=false)
./venv/bin/python scripts/ecosystem_baseline_probe.py

# Also run a second chat with RAG on (heavier)
./venv/bin/python scripts/ecosystem_baseline_probe.py --with-rag

# Smoke-style: skip the non-ping LLM call (faster CI)
./venv/bin/python scripts/ecosystem_baseline_probe.py --skip-llm

# Fail if /api/health overall is not healthy
./venv/bin/python scripts/ecosystem_baseline_probe.py --strict-health

# Save JSON artifact
./venv/bin/python scripts/ecosystem_baseline_probe.py --out /tmp/faithh_probe.json --quiet
```

Exit code **0** if all checks pass, **1** otherwise. Compare `wall_ms` vs `response_time_server` vs `llm_routing_latency_ms` in the printed JSON.

## Log correlation

Successful chat responses include **`request_id`** (same id appears in server logs for `/api/chat`). Use it to tie a UI session to backend lines.

## Related artifacts

- [docs/data/ecosystem_connections.json](../data/ecosystem_connections.json) — operational edges (who talks to whom).
- [projects/status/component_map.json](../../projects/status/component_map.json) — logical components and `depends_on`.
- [scripts/smoke_cockpit.sh](../../scripts/smoke_cockpit.sh) — endpoint ping matrix; may invoke the probe after basic pings.

## Session metrics baseline — 2026-04-10

| Field | Value |
|-------|--------|
| Baseline health score (open sessions, pre-flush) | **70.0** |
| Dominant flag | `rag_low_confidence` (~100% of sessions while threshold tight vs observed distances) |
| Stall threshold | `FAITHH_STALL_THRESHOLD_MS` = **30,000** (30s) — **kept** as honest signal |
| Typical full-chat wall time (local 70B-class path) | ~**120s** in early probes → counts as **stall** vs 30s; health score should reflect that until latency improves (model/KV/context), not by raising the stall bar |

**Target:** sustained health score **> 80** over 7 days.

**Blockers (parallel tracks):**

1. **RAG / collection composition** — run `python scripts/analyze_chroma_composition.py` (wraps `generate_db_map.py`). If `live_conversation` (or chat-like buckets) dominates the KB, distances stay high on factual queries; fix is ingestion/collection split, not only threshold tuning.
2. **Response latency** — KV cache, smaller/faster model, shorter prompts where acceptable.

**Dev flush (closed-session data without waiting 1h):**

- Set `FAITHH_DEV_MODE=true` *or* call from **127.0.0.1** only.
- `POST /api/metrics/flush-session` with JSON `{"session_id": "<id>"}` pops the in-memory accumulator and writes `timestamp_close` + outcome to Chroma.

Optional: shorten cleanup for local testing with `FAITHH_SESSION_TIMEOUT_SECONDS` (default **3600**).

## RAG distance threshold calibration — 2026-04-10

**Procedure:** `python scripts/sample_rag_distances.py` (uses `CHROMA_HOST` / `CHROMA_PORT` / `CHROMA_COLLECTION`).

Interpret **Best** per query vs `RAG_MAX_DISTANCE_CONFIDENT`:

- If best distances cluster **above** the current threshold on clearly relevant queries, either the **threshold is too aggressive** for this embedding space *or* the **index is sparse / wrong-domain heavy** (census decides).
- Prefer **census first** when `rag_low_confidence` fires on every session; if knowledge rows dominate and distances are still high, raise threshold toward the **~75th percentile** of per-query bests from the script (document the new value and date here when changed).

**Recorded sample run — 2026-04-10 (Gen8 Chroma, `faithh_knowledge_base`, N=25,259):**

`python scripts/sample_rag_distances.py` — `RAG_MAX_DISTANCE_CONFIDENT=0.55` in env.

| Stat | Value |
|------|--------|
| Best-per-query | min **0.487** / median **0.880** / p75 **1.002** / max **1.101** |
| vs 0.55 | **7/8** probe queries marked `low_confidence=True` |

One query (“RAG signal quality…”) hit **0.487** (confident); stack-specific probes (workspace, session metrics, harmonic body) sat **1.0–1.1+**. **Raising the threshold to ~0.72 alone would not** clear most of these bests — interpret together with census: dominant rows are **coding / faithh / irs_pub** buckets with **78% `unknown` domain** metadata, not a `live_conversation` takeover (see `docs/DATABASE_MAP_2026-04-10.md`).

Re-run after reindex and adjust `RAG_MAX_DISTANCE_CONFIDENT` only when the distance distribution shifts; otherwise prioritize embedding alignment, metadata cleanup, and query-specific collection routing.

## Collection split decision gate (pending census)

**Do not split collections until** `docs/DATABASE_MAP_*.md` from `analyze_chroma_composition.py` is reviewed.

| Census outcome | Action |
|----------------|--------|
| `live_conversation` / chat-like share **> ~60%** of `faithh_knowledge_base` | Plan split: `faithh_conversations` vs `faithh_knowledge_base`; RAG queries only the KB collection. |
| Knowledge docs **dominant** | Threshold calibration (`sample_rag_distances.py` + `RAG_MAX_DISTANCE_CONFIDENT`) is the primary lever. |

## After changes checklist

| Change | Re-run |
|--------|--------|
| Model routing / `llm_providers.py` | Baseline probe + `pytest tests/test_smart_routing.py` |
| PLC / `faithh_status` shape | `scripts/smoke_cockpit.sh` + probe |
| Chroma host or RAG path | Probe with `--with-rag` |
| Session metrics flush / `FAITHH_SESSION_TIMEOUT_SECONDS` | `POST /api/metrics/flush-session` (dev) + `pytest tests/test_session_metrics.py` |
| RAG threshold | `scripts/sample_rag_distances.py` + update this doc |
