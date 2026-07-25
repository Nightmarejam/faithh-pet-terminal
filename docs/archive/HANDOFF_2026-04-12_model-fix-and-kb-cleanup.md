# FAITHH session handoff — 2026-04-12

**Scope:** Generation runaway on `qwen25-grounded-gen5-delta:latest`, layered fixes, migration to `qwen25-faithh-v3:latest`, KB quality gate, and follow-up audit queue.

**Audience:** Next Cursor session — read this before KB cleanup / uncertainty-surface work.

---

## Session summary

Started with a generation runaway loop on `qwen25-grounded-gen5-delta:latest`. Fixed multiple layered issues. Ended with a working model (`qwen25-faithh-v3:latest`) passing all three operator-contract stress tests.

---

## What was fixed today

### 1. Generation runaway (critical — resolved)

**Problem:** Model looped, repeating git log blocks and system prompt fragments.

**Root causes:**

- No stop sequences in Ollama API calls
- No `num_predict` cap (effectively unlimited output)
- Long equals-bar separators in context acting as a continuation cue

**Fix:** `backend/llm_providers.py`

- `faithh_ollama_stop_sequences()` — stop on `====`, `\nUSER\n`, `\n===`, `[CTX:`, `\nUser:`, `\nAssistant:`
- `default_ollama_num_predict()` — ceiling default 1200; env `OLLAMA_NUM_PREDICT_CAP`
- Wired into `call_ollama_chat`, `iter_ollama_generate_stream`, and the SSE path in `faithh_professional_backend_fixed.py`

**Related:** Injected context delimiters moved to `[CTX:...]` / `[CTX_END]` and markdown `##` headings in personalities (`backend/context_builders.py` + monolith prompt assembly).

### 2. KB contamination (resolved)

**Problem:** Live conversation indexing had no quality gate; bad text was indexed into `faithh_knowledge_base`, feeding RAG feedback loops.

**Fix:** `faithh_professional_backend_fixed.py` — `_finalize_response()` (~line 2843)

- `_index_eligible` before `index_queue.put()`
- Skips if response is under 150 chars, contains `===`, contains `[CTX:`, or starts with `When I ask` / `System data` / `This is important`
- Skip log uses `elif CHROMA_CONNECTED:` to avoid noise when Chroma is offline

### 3. Model configuration (resolved)

**Lineage:**

| Model | Problem | Status |
|-------|---------|--------|
| `qwen25-grounded:latest` | Wrong template, base params | Deprecated for chat |
| `qwen25-faithh-v2:latest` | Fixed temp/ctx, wrong template | Deprecated |
| `qwen25-faithh-v3:latest` | ChatML, stop tokens, temp 0.15 | **Current** |

**Reference Modelfile (verify with `ollama show` locally):**

```dockerfile
FROM qwen25-grounded:latest
TEMPLATE """{{- if .System }}<|im_start|>system
{{ .System }}<|im_end|>
{{ end }}<|im_start|>user
{{ .Prompt }}<|im_end|>
<|im_start|>assistant
"""
SYSTEM You are FAITHH (Friendly AI Teaching & Helping Hub), Jonathan's personal AI assistant. Be accurate, grounded, and never fabricate facts.
PARAMETER num_gpu 99
PARAMETER temperature 0.15
PARAMETER top_p 0.9
PARAMETER num_ctx 16384
PARAMETER stop "<|im_end|>"
PARAMETER stop "<|im_start|>"
```

### 4. Config authority

**Rule:** `config.yaml` overrides `.env` for default model when `ai.default_model` and provider blocks are set. `.env` `DEFAULT_MODEL` is fallback only.

---

## Remaining issues (audit queue)

1. **KB noise (high)** — Sample `faithh_knowledge_base` by category; document purge scope.
2. **Uncertainty surface (new)** — `faithh_uncertainty_surface` collection for gated-out index paths; not RAG.
3. **Chat export quality (medium)** — `scripts/index_chat_exports.py` length / URL filters.
4. **RAG score UI (low)** — `faithh_pet_v4.html` distance/score display.
5. **Warm-up script (low)** — Optional Ollama warm in `restart_backend.sh`.

**Unsloth retrain:** After KB cleanup; do not train on noisy KB.

---

## Contract test baseline (v3)

| Test | Topic |
|------|--------|
| A | FGS ownership — cite context, flag gaps |
| B | Latency split — refuse to speculate without telemetry |
| C | Commit 8354808 UI — subject only, no invented visuals |

---

## File authority map

| Change | File |
|--------|------|
| Default model | `config.yaml` `ai.default_model` + `providers.ollama.model` |
| Fallback | `.env` `DEFAULT_MODEL` |
| Ollama timeout | `.env` `OLLAMA_TIMEOUT_S` |
| Output cap | `.env` `OLLAMA_NUM_PREDICT_CAP` |
| Stops | `.env` `OLLAMA_STOP` or YAML `ollama_stop` |
| RAG threshold | `.env` `RAG_MAX_DISTANCE_CONFIDENT` |
| Chip budgets | `faithh_professional_backend_fixed.py` `CHIP_TOKEN_BUDGETS` |
| Personality | `backend/context_builders.py` `get_faithh_personality()` |
| Indexing gate | `faithh_professional_backend_fixed.py` `_index_eligible` |

Formalize as `docs/guides/FILE_AUTHORITY_MAP.md` when ready.

---

## Key commands

```bash
grep -E "faithh-v|default_model" config.yaml
curl -s http://localhost:5557/health | python3 -m json.tool | head -10
```

Chroma: use `CHROMA_HOST` / LAN per `docs/guides/QUICKSTART.md`.

---

## IME uncertainty surface

Gated-out responses = maintenance signal (knowledge gaps), not RAG knowledge. **Not implemented** at handoff.

---

*End of handoff — consume into runbooks or FILE_AUTHORITY_MAP when stable.*

## Post-Session KB Audit (same day)
- Confirmed full KB is `chat_export` category only — no live_conversation contamination found
- Total chunks: 53,982
- Migrated 175 noise chunks to `faithh_uncertainty_surface`:
  - 119 × `Continuing previous conversation` (handoff_boilerplate)
  - 40 × `System check` (deflection_response)
  - 16 × `Conversation history highlights` (circular_meta_conversation)
- KB clean count: 53,807
- `faithh_uncertainty_surface` collection created and operational
- Migration script saved: `scripts/migrate_noise_to_uncertainty.py`

## Issue 3 Complete — Chat Export Quality Filter
- Added `_is_low_quality()` function to `scripts/indexing/index_chat_exports.py`
- Raises minimum chunk length from 50 → 150 chars
- Adds URL density check (>50% URLs = skip)
- Adds file listing check (>5 image/pdf refs = skip)
- Backup saved: `scripts/indexing/index_chat_exports.py.bak`
- Syntax verified clean
- Future re-indexing runs will filter low-quality chunks at source

## Critical Stale Docs — Next Cursor Session
These 7 docs are flagged critical in doc_update_queue and need updating:

1. `docs/architecture/API_INTEGRATION_HARDENING.md`
2. `docs/architecture/CHROMADB_API_VERSION_ISSUES.md`
3. `docs/architecture/INFRASTRUCTURE.md`
4. `docs/architecture/SYSTEM_OVERVIEW.md`
5. `scaffolding_state.json`
6. `docs/architecture/FAITHH_UI_COMPONENT_MAP.md`
7. `MASTER_CONTEXT.md`

Also pending for Cursor:
- Issue 4: RAG score display bug (faithh_pet_v4.html)
- Issue 5: Warm-up script (restart_backend.sh)
- Large uncommitted diff: commit remaining changes in focused batches by topic
