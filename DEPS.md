# FAITHH Dependency Map
<!-- 
  Purpose: When you change X, this tells you what else needs updating.
  Usage: Any agent or human must consult this before marking a task complete.
  Maintained by: Jonathan + AI assistants
  Last updated: 2026-04-09
-->

## Change Impact Registry

| When you change...            | Must also update...                                                                 | Why |
|-------------------------------|-------------------------------------------------------------------------------------|-----|
| ChromaDB collection/reindex   | `faithh_memory.json` (chunk count, embedding model, collection name), `project_states.json`, `README.md` | These all hardcode chunk counts and model names |
| Default LLM model             | `decisions_log.json` (new decision entry), `faithh_memory.json`, `CONTEXT.md`      | Model identity is referenced across files |
| ML chips regenerated          | `scaffolding_state.json` (note which embedding model was used), `project_states.json` | Chips must match active embedding space |
| Backend version bump          | `scaffolding_state.json`, `AGENTS.md` (if structure changed), `README.md`           | Version is referenced in multiple places |
| Phase transition              | `project_states.json`, `scaffolding_state.json`, `CONTEXT.md`                      | Phase is pulled from project_states by generate_context.py |
| New API endpoint added        | `docs/architecture/BACKEND_API.md`, `tests/` (add test)                            | API doc is the contract |
| Major backend module wiring (`faithh_professional_backend_fixed.py` ↔ `backend/*`) | `docs/architecture/BACKEND_STRUCTURE_OVERVIEW.md` (flow + file roles) | Structural map and “Logic for Humans” comments stay accurate |
| New Canvas panel or API poll in `faithh_pet_v4.html` | `docs/architecture/FAITHH_UI_COMPONENT_MAP.md` (UI → route → chips → GPU) | Keeps the “full circuit” doc honest for operators |
| `FAITHH_STRICT_LLM_GPU` / `FAITHH_CUDA_PHYSICAL_DEVICE` / `apply_faithh_llm_cuda_env` | `.env.example`, Ollama unit/docker env (must match), `docs/guides/WSL2_MULTI_GPU.md` if narrative changes, `GET /api/health/gpu-hint` + `faithh_pet_v4.html` badge | Flask + Ollama must agree on which physical card runs inference |
| `GET /api/health/gpu-hint` / `build_gpu_hint_payload` | `faithh_pet_v4.html`, `docs/architecture/FAITHH_UI_COMPONENT_MAP.md`, `docs/architecture/BACKEND_API.md`, `tests/test_gpu_hint.py` | Canvas diagnostic handshake for CUDA env vs configured physical index |
| Gen8 service added/removed    | `project_states.json` (gen8_services section), `SYSTEMS_MAP.md`, `README.md`       | Service inventory lives in multiple places |
| Partner change (Tom Cat)      | `project_states.json`, `SYSTEMS_MAP.md`, operating agreement docs                  | Ownership percentages are in multiple docs |
| Ollama model added/removed    | `faithh_memory.json` (model roster), `project_states.json`                         | Model list is referenced for routing |
| `scripts/run_llama_kv_quality_ablation.sh` or `llama_kv_prompt_ablation.py` behavior / output paths | `docs/experiments/KV_CACHE_QUANT_BENCHMARK_20260405.md` (llama-server f16 vs q4_0 prompt section) | Doc is the operator contract for JSON locations and env vars |
| New or updated `data/kv_vectors/llama_kv_ablation_*.json` captures (f16 / q4_0 / optional q8_0) | Same KV benchmark doc (“Captured run” table + interpretation) | Keeps committed artifacts explained in one place |
| `data/kv_vectors/experiment_a_results.json` or `extraction_meta.json` | KV benchmark doc (Experiment A artifacts) + `KV_EXPERIMENT_REPRO_CHECKLIST.md` if methodology changes | PolarQuant numbers and HF extraction provenance stay documented |
| `docs/experiments/KV_EXPERIMENT_REPRO_CHECKLIST.md` | Cross-link from `KV_CACHE_QUANT_BENCHMARK_20260405.md` and `docs/README.md` | Single checklist for operators |
| `data/kv_vectors/KV_ABLATION_SUMMARY.md` or matrix script behavior | `KV_CACHE_QUANT_BENCHMARK_20260405.md` (“Choosing KV settings”) | Summary must stay aligned with how we pick f16/q8/q4 profiles |
| `docs/experiments/KV_RESEARCH_FORMATS_POLARQUANT.md` | Cross-link from `KV_CACHE_QUANT_BENCHMARK_20260405.md` + `docs/README.md` | Single place for “PolarQuant = fork/kernels, not config” |
| `docs/guides/OLLAMA_KV_ENV.md` | `.env.example` note + `KV_CACHE_QUANT_BENCHMARK_20260405.md` intro + `docs/README.md` + `QUICKSTART.md` Ollama section | Ollama KV env must stay discoverable from FAITHH without implying .env drives Ollama |
| `backend/llm_providers.py` routing (`ollama_is_healthy`, `run_llm_route*`, Groq gate) | `docs/architecture/dependency_map.md` (runtime section), optional `reports/faithh/routing_smoke_test_*.md` after verification | Architecture map and smoke logs should reflect routing behavior |
| `/api/chat` auto mode (`get_optimal_model_for_query`, `routing_debug`, `ollama_num_ctx`) | `faithh_pet_v4.html` (chat payload + metrics line), `projects/status/component_map.json` (`auto_model_selector`, `api_chat` deps), `tests/test_auto_model_selector.py` | UI and PLC map stay aligned with backend selector |
| `projects/status/component_map.json` (components, change_log) | `scripts/impact_analyzer.py` output, `projects/status/dashboard.html`, `/api/plc/state` `recent_component_changes` | Self-awareness and PLC payload stay in sync |
| `docs/architecture/process_registry.json` | Run `scripts/refresh_dashboard_data.sh` to refresh `projects/status/process_registry.json` for the static dashboard | Dashboard health row reads the local snapshot |
| `/api/plc/state` response shape | `faithh_cockpit.html`, `faithh_pet_v4.html`, `scripts/maintenance/automated_health_check.py`, `scripts/ecosystem_baseline_probe.py`, smoke/tests that assert `faithh_status` | Avoid breaking polls; this is the canonical contract |
| `GET /api/metrics/summary` / `GET /api/metrics/sessions` | `faithh_cockpit.html` (SESSION METRICS panel + diagnostics probe), `docs/architecture/BACKEND_API.md` | Cockpit weekly trend + drill-down list; query params `days`, `limit`, optional `date` |
| Chroma `faithh_session_metrics` + `backend/session_metrics.py` | `.env.example` (`CHROMA_METRICS_COLLECTION`, `FAITHH_STALL_THRESHOLD_MS`, `FAITHH_SESSION_ACCUMULATOR_MAX`), `AGENTS.md`, `docs/RELEVANCY_REPORT.md`, `tests/test_session_metrics.py`, `scripts/analyze_session_metrics.py`, `POST /api/chat` open/bump/close wiring in `faithh_professional_backend_fixed.py` | Operational telemetry silo; must never feed RAG |
| `POST /api/chat` session lifecycle | `get_or_create_session` tuple return, `record_session_open` / `bump_from_chat_response` / `record_session_close` (timeout cleanup) | New sessions get an open snapshot; each response updates the in-memory accumulator; cleanup closes Chroma rows |
| `POST /api/metrics/flush-session` | `faithh_cockpit.html` (optional future), `docs/architecture/BACKEND_API.md`, `AGENTS.md` / `.env.example` (`FAITHH_DEV_MODE`) | Dev/localhost-only forced close + Chroma outcome flush |
| `scripts/analyze_chroma_composition.py` | `scripts/generate_db_map.py`, `docs/DATABASE_MAP_*.md` | Dated census wrapper; `--dry-run` for smoke |
| `scripts/sample_rag_distances.py` | `.env` `RAG_MAX_DISTANCE_CONFIDENT`, `docs/architecture/ECOSYSTEM_METRICS.md` | Operator calibration for low-confidence rate vs embedding distances |
| `docs/data/ecosystem_connections.json` (edges, probes) | `docs/architecture/ECOSYSTEM_METRICS.md`, optional `connection_ids` on `projects/status/component_map.json` | Operational topology stays aligned with `connection_monitor` URLs |
| `scripts/ecosystem_baseline_probe.py` (steps, thresholds) | `docs/architecture/ECOSYSTEM_METRICS.md`, `scripts/smoke_cockpit.sh`, `docs/guides/QUICKSTART.md`, `tests/test_ecosystem_baseline_probe.py` | Baseline SLO and smoke stay in sync |
| `/api/chat` success payload (`request_id`, `routing_debug`) | `faithh_pet_v4.html` if ever displaying debug, probe JSON consumers, log correlation docs | Contract for repeatability and support |
| `build_faithh_status_payload()` / embedded `faithh_status` | Same row as `/api/plc/state`; `/api/status` stays in sync automatically | Change payload in one function only |
| Cockpit status contract (`/api/plc/state`) or cockpit UI polling | `docs/guides/COCKPIT_DEPENDENCY_RUNBOOK.md`, `scripts/smoke_cockpit.sh`, `projects/status/component_map.json` change_log | Prevent UI/backend drift and keep smoke checks aligned |
| `docs/RELEVANCY_REPORT.md` (Canvas, Nightmarejam mapping, submodule policy) | `.gitmodules`, `docs/README.md` index, `AGENTS.md` if canonical paths change | Single audit doc for org alignment |
| `services/rag_api.py` or `services/project_hub/app.py` (paths, ports) | `docs/RELEVANCY_REPORT.md`, `docs/architecture/GITHUB_CANVAS_SYNC_2026-04-07.md`, `AGENTS.md` | Sidecars must stay discoverable; `POST /search` returns `{ hits, low_confidence, best_distance, threshold }` (not a bare array) |
| `faithh_cockpit.html` diagnostic panel (`cockpit_diagnostics_panel`) | `projects/status/component_map.json` | PLC / status map stays aligned with UI polls |
| `GET /api/workspace/registry` (`build_workspace_registry`) | `faithh_pet_v4.html` (`WorkspaceManager`, nav tabs, Engine Room strip, `workspace_registry` on `/api/chat`), `AGENTS.md` Service Registry rule | Canvas shell must stay aligned with backend capabilities |
| RAG relevance env (`RAG_MAX_DISTANCE_CONFIDENT`, `RAG_SIGNAL_STALE_SECONDS`) | `.env.example`, `faithh_professional_backend_fixed.py`, `services/rag_api.py`, `faithh_pet_v4.html` (`rag_relevance` banner) | Thresholds must stay aligned across main backend and sidecar |
| `scripts/purge_chroma_noise.py` (metadata/body heuristics, paged `get`) | Operator docs or `docs/guides/QUICKSTART.md` if purge becomes part of standard hygiene | Callers need collection name + dry-run vs `--execute`; tunables: `CHROMA_MAINT_BATCH_SIZE`, `CHROMA_MAINT_DOC_SUBCHUNK`, `CHROMA_MAINT_DELETE_CHUNK`, `CHROMA_MAINT_REQUEST_TIMEOUT_S` |
| `scripts/deduplicate_chroma.py` (paged scan + batched delete) | Same row as purge + `tests/` if behavior assertions added | Run purge before dedupe when cleaning polluted indexes; both load repo `.env` (`override=False`) and honor `CHROMA_HOST` / legacy `CHROMADB_*`; tunables: `CHROMA_MAINT_BATCH_SIZE`, `CHROMA_MAINT_DELETE_CHUNK`, `CHROMA_MAINT_REQUEST_TIMEOUT_S` |
| `scripts/generate_db_map.py` (paged metadata census) | `docs/DATABASE_MAP_*.md` (default dated filename); `docs/README.md` index if operators should discover it | Regenerate after large reindexes; optional `--output`, `--batch-size`, `--seed` (canary sampling); honors same Chroma env as purge/dedupe |
| `scripts/chroma_spike_cohort.py` | `scripts/sample_spike_data.py`, `scripts/purge_spike_data.py` | Shared spike date/category predicate only; keep in sync with census field names |
| `scripts/sample_spike_data.py` | `docs/DATABASE_MAP_*.md` (cohort definition); run before `purge_spike_data.py` | Random cohort samples + optional `--output-json`; uses `CHROMA_HOST` / legacy `CHROMADB_*` |
| `scripts/purge_spike_data.py` | Same as sample + regenerate `docs/DATABASE_MAP_*.md` after `--execute` | Default dry-run; `--execute` deletes in chunks; tunables `--date`, `--category`, `CHROMA_MAINT_*` |
| `scripts/list_chroma_collections.py` | Operator silo audit (Step 4 handoff) | Lists HTTP collections and counts; same env as other Chroma scripts |
| `scripts/system_pulse.py` (disk I/O, network vital, Chroma count, RAM vs `.wslconfig`) | Same Chroma env as above; optional `rich` for layout; `PULSE_DSM_HOST` (default `192.158.1.65`) for DSM ping; checks `/mnt/nas-staging` for NFS | Pulse dashboard; `CHROMA_COLLECTION`; `RAW_DATA_STAGING` not read here |
| `scripts/chroma_ingest_guard.py` | Bulk indexers that call it (`scripts/index_staged_nas_sources.py`, `scripts/indexing/index_documents_chromadb.py`, `scripts/indexing/index_faithh_kb_markdown.py`) | Required metadata keys + 3× growth guard; extend `validate_bulk_metadata` if schema changes |
| `scripts/index_staged_nas_sources.py` (metadata / upsert) | NAS intake docs, Chroma census path columns | Now sets `source` (repo-relative) + `--force` for growth guard; keep `domain`/`category`/`source` populated |
| `scripts/indexing/index_documents_chromadb.py` | Local PersistentClient chat-export indexer | Adds `domain`/`category`/repo-relative `source`, `--force`, and post-run growth guard |
| `scripts/indexing/index_faithh_kb_markdown.py` | HTTP `faithh_knowledge_base` indexer | `--file` *or* `--source DIR --recursive`; `--domain`/`--category`; optional `--document-type`, `--collection`; parses `CHROMA_HOST` like `generate_db_map.py`; `--force` for growth guard |
| `POST /api/chat` with `stream: true` (SSE + final `meta`) | `faithh_pet_v4.html` (`applyStreamChatMeta`, fetch body), `backend/llm_providers.py` (`iter_ollama_generate_stream`) | Ollama-first route only; Groq-first falls back to JSON |
| `tests/test_compass_reasoning.py` | Phase 5 handoff / operator runbook if formalized | Documents compass+RAG scenario and optional live LLM gate |
| `/api/chat` success fields `system_data_attached`, `rag_relevance` | `faithh_pet_v4.html` (`validateApiResponse`, chat header badge), optional `docs/architecture/BACKEND_API.md` | UI contract for Phase 4 contextual attachments |
| AGENTS.md rules changed       | Communicate to all active AI assistants — rules affect agent behavior               | Agents read this at session start |
| `docs/guides/FAITHH_OPERATOR_CONTRACT.md` (operator / evidence rules) | `AGENTS.md` (Operational standards link), `backend/context_builders.py` `get_faithh_personality()` (runtime mirror) | Policy doc and system prompt must stay aligned |
| `backend/llm_providers.py` Ollama `num_predict` / `stop` / `OLLAMA_NUM_PREDICT_CAP` | `.env.example`, `configs/model_config.yaml` (`ollama_stop` comment), `faithh_professional_backend_fixed.py` SSE `iter_ollama_generate_stream` args | Runaway generate + delimiter echo mitigation stays aligned |
| `get_faithh_personality()` accuracy / operator-contract text | `docs/guides/FAITHH_OPERATOR_CONTRACT.md` if behavior changes | Runtime prompt is the enforceable copy; update the doc when rules change |
| generate_context.py updated   | Re-run it: `python scripts/generate_context.py` to refresh `CONTEXT.md`            | CONTEXT.md is generated, not edited directly |
| decisions_log.json updated    | Re-run context generator if a decision affects current phase or model               | Decision summaries appear in CONTEXT.md |

---

## Embedding Space Compatibility

This is the highest-risk area. If chips and ChromaDB use different embedding models, routing breaks silently.

**Current state (verify before each chip regeneration):**
- ChromaDB embedding model: `all-MiniLM-L6-v2` (384-dim)
- Chips generated with: _(verify in ml/output/chips.json — should match above)_
- Last chip regeneration date: _(fill in)_

**Rule:** Chips MUST be regenerated after any ChromaDB reindex that changes embedding model.

---

## Pre-Commit Checklist (for AI agents)

Before marking any task complete, confirm:

- [ ] Did this change affect chunk counts, model names, or phase? → Update relevant files per table above
- [ ] Did this change the embedding model? → Chips must be regenerated
- [ ] Did this add a new API endpoint? → BACKEND_API.md needs updating
- [ ] Did this change project phase? → Both project_states.json AND scaffolding_state.json need updating
- [ ] Run consistency_checker.py and confirm no new mismatches

---

## Known Chronic Drift Points

These files have historically gone stale and caused confusion:

1. **faithh_memory.json** — tends to lag 1-2 months behind reality. High priority to keep current.
2. **CONTEXT.md** — generated file; only as fresh as its sources. Re-run generator after major changes.
3. **ML chips** — embedding space compatibility silently breaks after reindexes. Always verify.
4. **decisions_log.json** — decisions get made verbally/in-session but never logged. Log them when they happen.
