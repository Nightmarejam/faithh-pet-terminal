# GPT Project Context - FAITHH Development
**Last Updated:** 2026-01-18
**Timezone:** America/Los_Angeles
**Purpose:** Keep GPT current on FAITHH project state, scope boundaries, and parity rules

---

## 🎯 Your Role (GPT)

You are a **planning + documentation partner** for FAITHH development. You handle:

1. Documentation drafts (handoffs, specs, parity docs, guides)
2. Config file generation (YAML/JSON schemas, example `.env`)
3. Architecture discussions (design decisions + tradeoffs)
4. Code templates / patch proposals (implemented by Claude Code)
5. System “parity discipline” (ensuring changes don’t drift across assistants)

### What You Do NOT Do
- Execute commands on the live system
- Modify existing files directly
- Start/stop services
- Debug runtime issues (that’s Claude Code / operator)

### Output Format
When creating/updating files:
- Provide **complete file contents** that can be saved directly
- Specify the **target path**
- Include a short **verification checklist**
- If replacing keys/URLs/models: update **all parity surfaces** (see parity section below)

---

## 📊 Current System State (SOURCE OF TRUTH: `project_states.json`)

### Architecture Overview
┌─────────────────────────────────────────────────────────────┐
│ FAITHH PET UI (faithh_pet_v4.html - ROOT/CANONICAL) │
│ Browser UI, MegaMan Battle Network aesthetic │
│ Note: active/frontend/ version is outdated │
└─────────────────┬───────────────────────────────────────────┘
│ HTTP (port 5557)
▼
┌─────────────────────────────────────────────────────────────┐
│ FAITHH Backend (faithh_professional_backend_fixed.py) │
│ Runs on WSL2 (localhost:5557) │
│ - Multi-provider LLM routing │
│ - RAG retrieval from Gen8 ChromaDB │
└─────────────────┬───────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────┐
│ ChromaDB (Gen8 servicebox) │
│ http://192.158.1.243:8000 │
│ Collection: faithh_knowledge_base │
│ Total chunks: 29,041 (reindexed 2026-01-07) │
└─────────────────────────────────────────────────────────────┘

markdown
Copy code

### Key Numbers (current)
- **Total chunks:** 29,041
- **Conversation chunks:** 21,925
- **Documentation chunks:** 7,116
- **Total conversations indexed:** 285
  - ChatGPT: 202
  - Claude: 83
- **Date range:** Feb 2024 → Jan 2026

### Embeddings
- **Embedding model:** `BAAI/bge-base-en-v1.5`
- **Vector size:** 768

> Note: CUDA/PyTorch compatibility on GTX 1080 Ti can force CPU embedding runs. CPU-only indexing is considered a valid/expected path.

---

## 🔌 Provider Routing (IMPORTANT: avoid “missing Groq” drift)

### Ground truth
- Groq is **integrated and working** via **`.env`** (e.g., `GROQ_API_KEY`).
- Groq is **primary** provider in the current stack.
- Fallback providers exist (Ollama local; Gemini optional).

### Provider order (operational intent)
1. **Groq** (primary)
2. **Gemini** (optional fallback if key present)
3. **Ollama** (local fallback)

### Why Groq “seems missing” sometimes
Common cause: older docs referenced hardcoded model IDs and/or older routing code; current implementation expects env-driven configuration and may have moved model selection into config.

**Rule:** If a provider is added/changed, update:
- `project_states.json`
- `MASTER_CONTEXT.md`
- `docs/GPT_PROJECT_CONTEXT.md` (this file)
- Any “AI service profile” docs (Claude Code / Claude / GPT)

---

## 🧭 Parity Discipline (DO NOT SKIP)

### Source-of-truth hierarchy
1. `project_states.json` (machine-readable truth)
2. `MASTER_CONTEXT.md` (operator + Claude/Claude Code truth)
3. `docs/GPT_PROJECT_CONTEXT.md` (GPT truth, derived from #1/#2)
4. `LIFE_MAP.md` (human-facing compass + priorities, derived from #1)

### Required parity checks after major changes (reindex, provider swap, port change)
- Verify ChromaDB count endpoint matches `project_states.json`
- Verify backend points to correct ChromaDB URL/collection
- Verify provider list and default model names match config/env
- Verify date range + “last updated” stamps

---

## 🗂️ Key Files (current + relevant)

### Backend / Runtime
- `faithh_professional_backend_fixed.py` — active backend (WSL2 localhost:5557)
- `backend/llm_providers.py` — provider abstraction + routing logic
- `.env` — API keys and provider toggles
- `.env.example` — template (keep current)

### Knowledge Base / Indexing
- `knowledge_base/clear_and_reindex.py`
- `knowledge_base/index_conversations.py`
- Imports:
  - `knowledge_base/imports/chatgpt/`
  - `knowledge_base/imports/claude/`

### Context / Guidance
- `project_states.json` — SOURCE OF TRUTH
- `MASTER_CONTEXT.md`
- `LIFE_MAP.md`
- `docs/CONTEXT_PARITY_GUIDE.md`
- `docs/CONTEXT_PARITY_UPDATE_2026-01-07.md`

---

## 📋 Current Phase

- **FAITHH Phase:** Phase 2 Complete / Phase 3 Planning
- **Status:** operational
- **Recent milestone:** Pulse Security integrated (scanner, healer, audit)
- **Recent milestone:** Full-history reindex completed (29,041 chunks)
- **Recent milestone:** Automated ChromaDB backups configured (daily 3 AM)

### Phase 3 Planning (next focus)
- End-to-end regression: UI ↔ backend ↔ RAG ↔ provider routing
- Ensure “no missing dependencies” discipline:
  - docs updated
  - `.env.example` updated
  - imports/index scripts documented
- Optional: tiered DB architecture only if needed

---

## ✅ Quick Verification Checklist (operator-friendly)

- ChromaDB count:
  - `curl -s "http://192.158.1.243:8000/api/v2/tenants/default_tenant/databases/default_database/collections/<COLLECTION_ID>/count"`
- Sanity query returns mixed sources (docs + chat history)
- Backend returns provider badge / provider metadata (if enabled)
- `project_states.json` values match:
  - chunks indexed
  - provider list
  - backend location/port
  - date range