# CODEX HANDOFF — Chip Synthesis + Program Advances + Groq (v2 Combined)
**Date:** 2026-01-03  
**Goal:** Implement privacy-first, offline-capable “Chip Synthesis” + “Program Advances” (PA) in FAITHH, plus robust Groq provider integration (OpenAI-compatible), building on existing chip routing + PULSE.

---

## 0) Non-negotiables (guardrails)
1. **Local-first learning artifacts:** learned chips, clusters, PA stats, and user controls stored locally and deletable.
2. **User controls ship Day 1:** `pause_learning`, `do_not_learn` per message, `export`, `delete`, and “show me what you learned” transparency.
3. **No creepy reflection:** do not infer or surface sensitive patterns (health/finances/relationships) unless user explicitly opts in.
4. **Version everything:** `embedding_model_id`, `schema_version`, `code_version`, timestamps.
5. **Idempotent migrations:** any new DB tables/JSON schemas must be backward compatible.

---

## 1) What the 2nd research pass *confirmed* (implementation facts)
### Groq OpenAI compatibility (lock these in)
- Base URL: `https://api.groq.com/openai/v1`.  
- Chat Completions endpoint: `POST /chat/completions`.  
- Models list: `GET /models` (use this instead of hardcoding IDs).  
- Rate limits: implement 429 backoff; use Groq rate-limit headers:
  - `retry-after` (only on 429)
  - `x-ratelimit-remaining-requests`, `x-ratelimit-remaining-tokens`
  - `x-ratelimit-reset-requests`, `x-ratelimit-reset-tokens`
- Deprecations exist: implement dynamic model discovery + alias mapping + deprecation awareness.

### Groq caveats you must handle
- “Mostly” OpenAI-compatible — some OpenAI fields are unsupported (e.g., `logprobs`, `logit_bias`, `top_logprobs`, `messages[].name`, and `n` must be 1).
- `temperature=0` is treated specially; avoid hard 0.

### Clustering direction (offline-friendly)
- Start with **MiniBatchKMeans** (fast enough, incremental).
- Keep DBSCAN/HDBSCAN as v2 (harder in high-dim embeddings).

### Privacy UX patterns (ship)
- Avoid dark-pattern consent. Make opt-out as easy as opt-in.
- Provide symmetric controls: pause learning, per-message “don’t learn”, export/delete.

---

## 2) Key holes to fix (must implement or explicitly defer)
### Hole A — cosine vs euclidean clustering
Embedding similarity is usually cosine. scikit KMeans/MiniBatchKMeans uses Euclidean.
**Fix:** L2-normalize embeddings before clustering (approximates cosine in Euclidean space), OR add a v2 “spherical k-means”.  
**Deliverable:** `normalize_embedding(vec) -> unit vec` + tests.

### Hole B — choosing K (number of clusters)
MiniBatchKMeans requires K. If you pick K wrong, chips will be garbage.
**Fix:** implement a simple K-selection heuristic:
- start K small (e.g., 8–15) per domain bucket,
- periodically evaluate inertia trend / silhouette (approx) on a sample,
- allow K to grow when cluster “crowding” exceeds threshold.
**Deliverable:** `cluster_config.json` and `auto_k` strategy (documented).

### Hole C — concept drift + embedding model changes
If you change the embedding model, clusters become invalid.
**Fix:** store `embedding_model_id` per cluster + per event; if it changes, mark clusters “needs_rebuild” and rebuild offline.
**Deliverable:** migration + rebuild command.

### Hole D — privacy creep via logs
Raw event logs can contain sensitive content.
**Fix:** store *features*, not full content, for learning:
- chip ids used, timestamp, token count, response mode, topic tags
- optional hashed n-grams if needed (off by default)
**Deliverable:** redact/feature extraction pipeline.

---

## 3) Architecture targets
### New components
1. **Pulse Events Store** (append-only)
2. **Learning Engine** (batch job)
3. **Chip Registry** (static + learned)
4. **PA Detector** (rules + stats)
5. **User Controls** (pause/do-not-learn/export/delete)
6. **Groq Provider** (OpenAI-compatible client wrapper)

### Where this lives (suggested paths)
- `backend/pulse_events.py` (store + schema)
- `backend/learning_engine.py` (batch clustering + chip proposals)
- `backend/chip_registry.py` (merge static + learned chips)
- `backend/program_advances.py` (PA rules + unlock tracking)
- `backend/providers/groq_provider.py` (OpenAI-compatible wrapper)
- `backend/routes/pulse.py` (status/export/delete)
- `frontend/components/PulsePanel.tsx` (optional UI)

---

## 4) Data schemas (minimal v1)
### 4.1 pulse_events (SQLite recommended)
Table: `pulse_events`
- `id` TEXT (uuid)
- `ts` INTEGER (unix)
- `conversation_id` TEXT
- `message_id` TEXT
- `chip_ids` TEXT (json array)
- `intent` TEXT
- `embedding_model_id` TEXT
- `features` TEXT (json; NO raw user text)
- `do_not_learn` INTEGER (0/1)

### 4.2 learned_chips
Table: `learned_chips`
- `chip_id` TEXT (uuid)
- `name` TEXT
- `description` TEXT
- `created_ts` INTEGER
- `last_used_ts` INTEGER
- `status` TEXT ('proposed'|'active'|'archived')
- `cluster_id` TEXT
- `rules` TEXT (json; conditions for auto-activation)
- `safety_tags` TEXT (json; e.g., ['non_sensitive_only'])

### 4.3 program_advances
Table: `program_advances`
- `pa_id` TEXT
- `name` TEXT
- `sequence` TEXT (json array of chip_ids/intent pattern)
- `unlock_count` INTEGER
- `unlocked_ts` INTEGER NULL
- `level` INTEGER default 1

---

## 5) Implementation plan (go down the list)
### Phase 0 — Foundation (safe even if strategy changes)
1. Add `do_not_learn` support:
   - API accepts `do_not_learn: true` per request.
   - Store in `pulse_events.do_not_learn=1`.
2. Add `/api/pulse/status`:
   - returns counts, last PA, learning paused, learned chip counts.
3. Add export/delete:
   - `GET /api/pulse/export` -> zip/json of events + learned chips + PAs
   - `POST /api/pulse/delete` -> wipes local learning db (confirm flag required)

**Acceptance tests**
- unit tests for schema creation, insert, export, delete.
- smoke test hits status/export/delete.

### Phase 1 — Chip discovery (batch)
1. Create `learning_engine.run()`:
   - load recent events (e.g., last 30 days)
   - build per-domain buckets (audio, infra, constella, etc.) using existing intent tags
   - L2-normalize embeddings
   - run MiniBatchKMeans per bucket
2. Propose chips:
   - pick top clusters by size + coherence proxy
   - auto-generate *non-creepy* names: “Studio Producer”, “Morning Briefing”
   - status = `proposed`

**Acceptance**
- deterministic run on fixture data produces same proposals.
- proposals exclude events marked `do_not_learn`.

### Phase 2 — User approval + lifecycle
1. Add endpoints:
   - `GET /api/chips/learned` (list proposed/active/archived)
   - `POST /api/chips/{id}/approve`
   - `POST /api/chips/{id}/archive`
   - `POST /api/chips/{id}/edit` (name/desc/rules)
2. Add bloat control:
   - auto-archive chips unused for N days (configurable)
   - merge suggestion if cosine centroid similarity > threshold (proposal only)

### Phase 3 — Program Advances (PA)
1. Implement PA detector:
   - start rule: frequent co-activation sequences over rolling window
   - store `unlock_count`; unlock when count >= threshold (e.g., 5)
2. PA behavior:
   - PA maps to a **macro-chip** (bundle prompt + tools)
   - example: “Project Historian” = Scaffolding + Decisions + Retrieval narrative
3. Add `GET /api/pa` to list PAs + unlock progress.

### Phase 4 — Groq provider integration (robust)
1. Implement `GroqProvider` using OpenAI-compatible base URL:
   - configurable: `GROQ_API_KEY`, `GROQ_BASE_URL` default above
   - dynamic model discovery via `GET /models`
2. Add retry/backoff:
   - on 429, respect `retry-after` else compute from `x-ratelimit-reset-*`
3. Add “unsupported params scrubber”:
   - remove unsupported fields when routing to Groq
   - ensure `n=1`, avoid `temperature=0`
4. Add provider health in `/api/status`.

**Acceptance**
- unit tests: header parsing, backoff calculation, param scrubbing.
- integration smoke: optional (skipped if no key).

---

## 6) Deliverables Codex must produce
1. A single PR-style diff (or patch) touching the backend paths above.
2. Tests:
   - `pytest -q` for new modules
   - update `scripts/smoke_backend.py` to include `/api/pulse/status`
3. Documentation:
   - `docs/CHIP_SYNTHESIS.md` (short; includes controls + lifecycle)
   - `docs/PROVIDER_GROQ.md` (env vars + caveats)

---

## 7) Codex run instructions (output contract)
- Output: unified diff + test commands run + results.
- Do not invent secrets. Read env from `.env.example` and update it if needed.
- Keep functions small and separately testable.

