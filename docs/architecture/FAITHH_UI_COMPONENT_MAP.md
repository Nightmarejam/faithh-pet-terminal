# FAITHH UI component map (`faithh_pet_v4.html` → backend)

**Purpose (Logic for Humans):** Trace what each part of the Canvas UI calls over the network, what Flask route answers, whether that path runs **context “chips”** (parallel context fetches) and/or hits the **GPU** (via Ollama on the workstation).

**RAG hit scores (2026-04-12):** Chroma returns per-hit **`distance`** (lower = stronger). The Sources list shows **similarity** as `max(0, min(1, 1 - distance))`, matching the reranker’s cosine-style interpretation in `faithh_professional_backend_fixed.py` (`_apply_reranking`). `null` / non-finite distances omit the badge (avoids bogus “1.00” from `1 - null`). **`rag_relevance`** on `/api/chat` carries `low_confidence`, `best_distance`, and `threshold` for the banner.

**GPU rule of thumb:** The Flask process pins `CUDA_VISIBLE_DEVICES` (default **physical GPU `1`** = RTX 3090 next to a 1080 Ti). **Chat inference** still runs inside the **Ollama** process — start Ollama with the **same** `CUDA_VISIBLE_DEVICES` / `FAITHH_CUDA_PHYSICAL_DEVICE` so tensor math lands on the 3090. RAG **embeddings** in the backend use **CPU** on purpose (`get_query_embedder`).

---

## A. Main chat (the circuit everyone cares about)

| UI action | HTTP | Backend | Context chips (parallel in `build_integrated_context`) | GPU? |
|-----------|------|---------|--------------------------------------------------------|------|
| Send message / stream reply | `POST /api/chat` | `chat()` | **Always scheduled:** `conversation_history`, `self_awareness`, `constella`, `decisions`, `project_state`, `scaffolding`, `project_structure`, `rag_search` — each chip runs only if intent flags match (except `project_structure` and `rag` pipeline rules). | **Yes (local Ollama path):** Ollama server performs matmul on its GPU. Groq/Gemini/Anthropic = cloud GPU, not yours. |
| RAG toggle in payload | same | `use_rag: true/false` | Disables **RAG chip** when false; others unchanged. | Indirect: fewer Chroma queries → less **CPU** embed work; LLM still uses Ollama GPU when provider is Ollama. |
| Workspace registry snapshot sent with chat | same | `workspace_registry` / `lean_workspace_registry` | No extra chips — metadata for routing/UI only. | No. |

### Chip names ↔ Python `retrieve_*` (Logic for Humans)

| Chip key (API / UI badge) | Backend function | Plain English |
|---------------------------|------------------|---------------|
| `conversation_history` | `retrieve_conversation_history` | Last few turns in this session. |
| `self_awareness` | `retrieve_self_awareness` | “Who is FAITHH” block from memory when user asks about the assistant. |
| `constella` | `retrieve_constella` | Constella framework blurb when query is Constella-shaped. |
| `decisions` | `retrieve_decisions` | Snippets from `decisions_log.json` for “why did we…” questions. |
| `project_state` | `retrieve_project_state` | `project_states.json` overview or one project. |
| `scaffolding` | `retrieve_scaffolding` | “You are here” orientation from `scaffolding_state.json`. |
| `project_structure` | `retrieve_project_structure` | Live file tree + git log — **not** always labeled in older UI lists but is injected. |
| `rag_search` | `retrieve_rag` → `smart_rag_query` → `query_collection` | Chroma semantic search; **CPU** embed in backend, then network to Chroma host. |

**Program Advance:** `get_pa_chips_for_query` can **force** extra chips (e.g. scaffolding/decisions) before the thread pool runs.

**Tool-intent auto-attach:** If the user message matches pulse/genomic regexes, `augment_context_for_tool_intents` prepends JSON snapshots (no extra chip *names*, but extra context).

---

## B. Other UI → API calls (no full chip stack unless noted)

| UI area (typical) | HTTP | Backend | Chips / GPU |
|-------------------|------|---------|-------------|
| Shell boot / registry | `GET /api/workspace/registry` | `get_workspace_registry` | None / no. |
| GPU / CUDA pin hint (header badge on load) | `GET /api/health/gpu-hint` | `gpu_hint_health` → `build_gpu_hint_payload` | None; compares Flask `CUDA_VISIBLE_DEVICES` to `FAITHH_CUDA_PHYSICAL_DEVICE` (see `ollama_note` in JSON for Ollama). |
| PLC / status strip | `GET /api/plc/state` | `get_plc_state` | None / no. |
| Pulse security | `POST /api/pulse/security/scan` | `pulse_security_scan` | None / no. |
| Pulse health | `GET /api/pulse/health/check` | `pulse_health_check` | None / no. |
| Pulse heal | `POST /api/pulse/health/heal` | `pulse_heal` | None / no. |
| Pulse audit | `GET /api/pulse/audit/summary` / `recent` | `pulse_audit_*` | None / no. |
| Pulse state / avatar | `GET /api/pulse/state` | `pulse_state_refresh` etc. | None / no. |
| Pulse personalized chips API | `GET /api/pulse/chips` | `get_personalized_chips` | None / no. |
| Compass director / refresh / log | `GET/POST /api/compass/*` | compass routes | None / no. |
| Constitution | `GET /api/constitution/*` | constitution routes | None / no. |
| Focus panels | `GET /api/focus/*` | focus routes | None / no. |
| Genomic dashboard | `GET /api/genomic/analyze-sensors` | `analyze_genomic_sensors` | None / no (unless service internally uses GPU — not Flask). |
| Collectors | `GET /api/context/collectors/status` | `get_collector_status` | None / no. |
| ML chip library | `GET /api/ml/chips` | `get_ml_chips` | None / no. |
| ML chip test | `POST /api/ml/chips/activate` | `ml_chip_activate` | **CPU** embed + cosine sim to centroids (no LLM). |
| Journal | `GET/POST /api/journal*` | journal routes | May call LLM on generate — same Ollama GPU rules as chat. |

---

## C. End-to-end “button → GPU” shorthand

1. **User sends chat** → browser `fetch(POST /api/chat)`  
2. **`chat()`** → `detect_query_intent` → optional `augment_context_for_tool_intents`  
3. **`build_integrated_context`** → thread pool runs chips (file/JSON + maybe Chroma RAG)  
4. **`run_llm_route_with_pin`** → HTTP to **Ollama** / Groq / etc.  
5. **GPU:** only when the chosen provider is **local Ollama** (or local webui) and that service is bound to the 3090 via its own `CUDA_VISIBLE_DEVICES`.

---

## Related

- `docs/architecture/BACKEND_STRUCTURE_OVERVIEW.md` — module graph.  
- `backend/llm_providers.py` — `apply_faithh_llm_cuda_env()`, `get_faithh_cuda_physical_device_index()`.  
- `.env.example` — `FAITHH_STRICT_LLM_GPU`, `FAITHH_CUDA_PHYSICAL_DEVICE`.
