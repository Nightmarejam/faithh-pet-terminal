# FAITHH Architecture Document v2.0
**Date**: 2025-12-02  
**Status**: CURRENT - Reflects actual system state  
**Version**: v3.3-scaffolding

---

## 🎯 What FAITHH Is

FAITHH (Friendly AI Teaching & Helping Hub) is a personal thought partner and knowledge management system. It's not a tool—it's infrastructure for maintaining coherence across projects and conversations.

**Core Purpose**: Help Jonathan maintain context and make decisions across FAITHH development, Constella framework, and Floating Garden Soundworks audio production.

---

## 🏛️ Current System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│         faithh_professional_backend_fixed.py                │
│                   v3.3-scaffolding                          │
│                     (Port 5557)                             │
├─────────────────────────────────────────────────────────────┤
│ Flask Server + Static File Serving                          │
│ ├── /                  (Serves faithh_pet_v4.html)         │
│ ├── /api/chat          (Main endpoint - all integrations)  │
│ ├── /api/status        (System health + stats)             │
│ ├── /api/rag_search    (Direct RAG query)                  │
│ ├── /api/upload        (Document upload)                   │
│ └── /health            (Simple health check)               │
├─────────────────────────────────────────────────────────────┤
│ Integration Layer (build_integrated_context)                │
│ ├── Self-Awareness     (faithh_memory.json)                │
│ ├── Decision Citation  (decisions_log.json)                │
│ ├── Project States     (project_states.json)               │
│ ├── Scaffolding        (scaffolding_state.json)            │
│ ├── Constella Awareness (constella_awareness prompt)       │
│ └── RAG Search         (ChromaDB - 93,533 docs)            │
├─────────────────────────────────────────────────────────────┤
│ Intent Detection                                            │
│ ├── is_self_query      (Questions about FAITHH)            │
│ ├── is_why_question    (Decision rationale requests)       │
│ ├── is_next_action     (What should I work on?)            │
│ ├── is_constella_query (Civic framework questions)         │
│ └── needs_orientation  (Where was I? Catch me up)          │
├─────────────────────────────────────────────────────────────┤
│ LLM Layer                                                   │
│ ├── Ollama llama31-faithh:latest / qwen3-faithh:latest (localhost:11434) - Primary │
│ └── Gemini 2.0 Flash   (API) - Fallback (key expired)      │
└─────────────────────────────────────────────────────────────┘
```

---

## 💾 Data Architecture

### State Files (JSON)

| File | Purpose | Update Frequency |
|------|---------|------------------|
| `faithh_memory.json` | FAITHH's identity, capabilities, personality | Rarely (manual) |
| `decisions_log.json` | Why decisions were made, alternatives considered | Per major decision |
| `project_states.json` | Current phase of each project | Per session |
| `scaffolding_state.json` | Structural position, open loops, milestones | Per session |

### Vector Database (ChromaDB)

```
ChromaDB (localhost:8000)
├── Collection: "documents"
│   └── 93,533 documents indexed
│       ├── Claude conversation exports
│       ├── ChatGPT conversation exports  
│       ├── Grok conversation exports
│       ├── Constella framework docs
│       ├── Session summaries
│       └── Technical documentation
│
└── Embedding Model: nomic-embed-text (768 dimensions)
```

### Source Data

```
AI_Chat_Exports/
├── Claude_Chats/
│   ├── conversations.json
│   └── memories.json
├── Chat_GPT_Chats/
│   ├── conversations.json
│   ├── memories.json
│   └── [100+ image artifacts]
└── Grok_Chats/
    └── [exports]
```

---

## 🔄 Request Flow

```
User Query
    │
    ▼
┌─────────────────┐
│ Intent Detection │ ← Regex patterns for query classification
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│       build_integrated_context()         │
│                                          │
│  if is_self_query:                      │
│      → inject faithh_memory.json        │
│                                          │
│  if is_why_question:                    │
│      → inject decisions_log.json        │
│                                          │
│  if is_next_action or needs_orientation:│
│      → inject scaffolding_state.json    │
│      → inject project_states.json       │
│                                          │
│  if is_constella_query:                 │
│      → inject constella_awareness       │
│                                          │
│  if not pure_self_query:                │
│      → RAG search (top 5 docs)          │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────┐
│   LLM Request   │ ← System prompt + context + user query
└────────┬────────┘
         │
         ▼
    Response
```

---

## 📁 Repository Structure

```
ai-stack/
├── 📄 Core Documentation
│   ├── README.md
│   ├── START_HERE.md
│   ├── LIFE_MAP.md              ⭐ Your compass
│   ├── ARCHITECTURE.md          ⭐ This file
│   └── FAITHH_TESTING_GUIDE.md  ⭐ Testing framework
│
├── 🐍 Core Application
│   ├── faithh_professional_backend_fixed.py  ⭐ THE backend
│   ├── faithh_pet_v4.html                    ⭐ THE UI
│   ├── scaffolding_integration.py
│   └── phase1_conversation_memory.py
│
├── 📋 State Files
│   ├── faithh_memory.json
│   ├── project_states.json
│   ├── decisions_log.json
│   └── scaffolding_state.json
│
├── ⚙️ Config
│   ├── .env
│   ├── config.yaml
│   ├── docker-compose.yml
│   └── requirements.txt
│
├── 🔧 Scripts
│   ├── restart_backend.sh       ⭐ Start FAITHH
│   ├── stop_backend.sh
│   └── scripts/                 (utilities, indexing, maintenance)
│
├── 📁 Data
│   ├── AI_Chat_Exports/         (source conversations)
│   ├── chroma_db/               (vector database)
│   ├── faithh_rag/              (RAG index)
│   └── constella-framework/     (Constella docs, own git repo)
│
├── 📁 Support
│   ├── docs/
│   ├── parity/
│   ├── backend/
│   └── tests/
│
└── 📁 archive/                  (historical reference)
    ├── sessions/
    ├── handoffs/
    ├── development/
    ├── planning/
    ├── legacy/
    └── ui_reference/            (v3 UI for chip aesthetic)
```

---

## 🎴 UI Architecture (v4)

### Three-Page Structure

```
┌─────────────────────────────────────────────┐
│  CHAT  │  CHIPS  │  STATUS                  │
├─────────────────────────────────────────────┤
│                                             │
│  ┌─────────┐  ┌─────────────────────────┐  │
│  │ FAITHH  │  │                         │  │
│  │ Avatar  │  │     Chat Messages       │  │
│  │         │  │                         │  │
│  ├─────────┤  │  [User]: Query          │  │
│  │ Active  │  │  [FAITHH]: Response     │  │
│  │ Chips   │  │  Chips used: 📚 🏛️      │  │
│  │ ┌─┬─┬─┐ │  │                         │  │
│  │ │📚│🏛️│🧭│ │  │                         │  │
│  │ └─┴─┴─┘ │  │                         │  │
│  └─────────┘  └─────────────────────────┘  │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │ Type your message...          [Send]│   │
│  └─────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

### Battle Chips (Integrations)

| Chip | Icon | Integration | Fires When |
|------|------|-------------|------------|
| RAG Search | 📚 | ChromaDB semantic search | Most queries |
| Constella | 🏛️ | Civic framework context | Constella keywords |
| Scaffolding | 🧭 | Position awareness | "Where was I?" |
| Decisions | 📋 | Decision rationale | "Why did we...?" |
| Life Map | 🗺️ | High-level direction | Priority questions |
| Self Query | 🤖 | FAITHH self-awareness | "What is FAITHH?" |

---

## 🔌 External Dependencies

| Service | Port | Purpose | Status |
|---------|------|---------|--------|
| FAITHH Backend | 5557 | Main API + UI serving | ✅ Active |
| ChromaDB | 8000 | Vector database | ✅ Active |
| Ollama | 11434 | Local LLM inference | ✅ Active |
| Gemini API | - | Fallback LLM | ⚠️ Key expired |

### LLM Models (Ollama)

| Model | Size | Purpose |
|-------|------|---------|
| llama31-faithh:latest | 8.0B | General chat + reasoning |
| qwen3-faithh:latest | 30.5B | Heavy reasoning + coding |

---

## 📊 Current Metrics

- **Indexed Documents**: 93,533
- **Average Performance**: 4.58★
- **Backend Version**: v3.3-scaffolding
- **UI Version**: v4

---

## 🎯 What's Working

✅ RAG search with 93K+ documents  
✅ Intent detection (self, why, orientation, constella)  
✅ Scaffolding awareness (position, completions, open loops)  
✅ Decision citation from decisions_log.json  
✅ Project state awareness  
✅ Constella framework context injection  
✅ Three-page UI with chip visualization  

## ⚠️ Known Limitations

- Gemini API key expired (Ollama-only for now)
- Backend doesn't return `integrations_used` (chips display as fallback)
- No auto-indexing of new conversations yet
- Data deduplication not implemented
- Observation layer not built

---

## 🔮 Future Architecture (When Stable)

```
┌─────────────────────────────────────────────────────────┐
│                   FAITHH Ecosystem                       │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐    ┌──────────────┐    ┌───────────┐ │
│  │ Observation  │───▶│   FAITHH     │◀───│  MacBook  │ │
│  │    Layer     │    │   Backend    │    │ Companion │ │
│  └──────────────┘    └──────────────┘    └───────────┘ │
│         │                   │                           │
│         ▼                   ▼                           │
│  ┌──────────────┐    ┌──────────────┐                  │
│  │  Auto-Sync   │    │   ChromaDB   │                  │
│  │    Docs      │    │   93K+ docs  │                  │
│  └──────────────┘    └──────────────┘                  │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**Not building this yet**—FAITHH needs to be stable first (per LIFE_MAP Path B decision).

---

## 📚 Key Files Reference

| Need | File |
|------|------|
| Understand direction | `LIFE_MAP.md` |
| Test FAITHH | `FAITHH_TESTING_GUIDE.md` |
| Start FAITHH | `./restart_backend.sh` |
| System architecture | `ARCHITECTURE.md` (this file) |
| Quick reference | `QUICK_START_GUIDE.md` |
| Decision history | `decisions_log.json` |
| Project status | `project_states.json` |

---

*Last updated: 2025-12-02 by Claude Opus 4.5*
