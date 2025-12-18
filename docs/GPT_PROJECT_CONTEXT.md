# GPT Project Context - FAITHH Development
**Last Updated:** 2025-12-18
**Purpose:** Keep GPT current on FAITHH project state and its role

---

## 🎯 Your Role (GPT)

You are a **planning and documentation partner** for FAITHH development. You handle:

1. **Documentation drafts** - Handoff docs, specs, guides
2. **Config file generation** - YAML, JSON schemas  
3. **Architecture discussions** - Design decisions, tradeoffs
4. **Code templates** - Modules to be implemented by Claude Code/Sonnet
5. **Theoretical design** - PML, Harmony framework, governance systems

### What You Do NOT Do
- Execute commands on the live system
- Modify existing files directly
- Start/stop services
- Debug runtime issues (that's Opus + Desktop Commander)

### Output Format
When creating files, provide **complete contents** that can be saved directly. Always specify the target path.

---

## 📊 Current System State (as of Dec 17, 2025)

### Architecture Overview
```
┌─────────────────────────────────────────────────────────────┐
│  FAITHH PET UI (faithh_pet_v4.html)                        │
│  Browser-based, MegaMan Battle Network aesthetic           │
└─────────────────┬───────────────────────────────────────────┘
                  │ HTTP (port 5557)
                  ▼
┌─────────────────────────────────────────────────────────────┐
│  FAITHH Backend (faithh_professional_backend_fixed.py)     │
│  Flask + CORS, handles routing and RAG                     │
│  ├── RAG: ChromaDB (93k docs, all-mpnet-base-v2, 768-dim) │
│  ├── Primary LLM: Groq API (qwen3-32b) ← WORKING          │
│  └── Local: text-gen-webui (port 7001, 32 tok/s)          │
└─────────────────┬───────────────────────────────────────────┘
                  │
        ┌─────────┼─────────┐
        ▼         ▼         ▼
   ┌─────────┐ ┌─────────┐ ┌─────────────────┐
   │  Groq   │ │ Ollama  │ │ text-gen-webui  │
   │  Cloud  │ │ :11434  │ │ :7001 (API)     │
   │  qwen3  │ │         │ │ RTX 3090        │
   └─────────┘ └─────────┘ └─────────────────┘
```

### Service Ports
| Service | Port | Status |
|---------|------|--------|
| FAITHH Backend | 5557 | ✅ Active |
| ChromaDB | 8000 | ✅ Active |
| text-gen-webui UI | 7861 | ✅ Active |
| text-gen-webui API | 7001 | ✅ Active |
| Ollama | 11434 | ✅ Active |

### Hardware
- **Windows Desktop (WSL2 Ubuntu 24.04)**
  - Ryzen 9 3900X, 48GB RAM
  - RTX 3090 (24GB) - Primary LLM inference
  - GTX 1080 Ti (11GB) - Embeddings/overflow
- **Tailscale Network** - 6 devices connected

---

## 🗂️ Key Files

### Backend
```
~/ai-stack/
├── faithh_professional_backend_fixed.py  # ACTIVE - Main backend
├── faithh_backend_temp_v2.py             # Has multi-provider routing (reference)
├── configs/model_config.yaml             # Provider configuration
└── .env                                  # API keys (GROQ_API_KEY, etc.)
```

### Frontend
```
~/ai-stack/
├── faithh_pet_v4.html                    # Main UI (port 5557)
└── images/                               # faithh.png, pulse.png
```

### Documentation
```
~/ai-stack/docs/
├── CLAUDE_CODE_HANDOFF_PHASE2.md        # Implementation spec for Claude Code
├── GPT_PROJECT_CONTEXT.md               # This file
├── MASTER_CONTEXT.md                    # AI operational context
├── HARMONY_CONTEXT.md                   # Harmony framework reference
└── session-reports/                     # Session summaries
```

---

## 🔧 Provider Configuration

### Working Groq Models
```yaml
groq:
  type: "groq"
  model: "qwen/qwen3-32b"      # Primary reasoning
  # Also available:
  # - llama-3.3-70b-versatile  (general)
  # - llama-3.1-8b-instant     (fast)
```

### Local Models
```yaml
local_webui:
  type: "openai_compatible"
  base_url: "http://localhost:7001/v1"
  model: "qwen2.5-14b-instruct-q4_k_m"  # 32 tok/s on RTX 3090

ollama:
  type: "ollama"
  base_url: "http://localhost:11434"
  model: "llama3.1:8b"
```

---

## 📋 Current Phase: Phase 3 - Future Enhancements

### Completed (Phase 1) ✅
- [x] Groq cloud integration (qwen3-32b working)
- [x] text-gen-webui on RTX 3090 (32 tok/s)
- [x] OpenAI-compatible API on port 7001
- [x] UI connected to backend (port 5557)
- [x] RAG functional (93k docs)
- [x] GPT drafted llm_providers.py module
- [x] GPT drafted model_config.yaml
- [x] GPT drafted provider badge component
- [x] Claude Code handoff document created

### Completed (Phase 2) ✅
- [x] Create `backend/llm_providers.py` module
- [x] Update model_config.yaml with correct models
- [x] Patch backend with multi-provider routing
- [x] Add doc-grounded mode enforcement
- [x] Add evidence packets to responses
- [x] Add provider badge to UI
- [x] Enhanced /api/status with RAG activity

### Future (Phase 3-4)
- [ ] BGE-M3 embedding migration (if needed)
- [ ] Phase Mediation Layer (PML) implementation

---

## 🚨 Critical Behaviors to Enforce

### Doc-Grounded Mode
When user says "from my docs" / "from project docs" / "summarize from docs":
1. **MUST** run RAG retrieval
2. **MUST** return evidence sources
3. If no hits: **MUST** refuse gracefully (no hallucination)
4. **MUST NOT** substitute persona/self-awareness as if from docs

### Evidence Packet Structure
```json
{
  "routing": {
    "route": "auto|code|fast|local|cloud",
    "provider": "groq|ollama|local_webui",
    "model": "...",
    "latency_ms": 123,
    "used_fallback": false
  },
  "evidence": {
    "mode": "doc_grounded|hybrid|freeform",
    "rag_used": true,
    "rag_hits": 4,
    "sources": ["HARMONY_CONTEXT.md"],
    "snippets": [{"source": "...", "text": "..."}]
  }
}
```

---

## ⚠️ Important Context

### Memory Truth
- **Conversation memory**: Ephemeral (within session only)
- **Project memory**: Persistent via ChromaDB RAG
- FAITHH should NOT claim to "remember" past conversations unless in RAG

### Embedding Dimension
ChromaDB uses `all-mpnet-base-v2` (768-dim). Do NOT suggest changing without a migration plan.

### User Context (Jonathan)
- Has ADHD - needs comprehensive documentation
- Audio producer (Tom Cat Sound LLC / Floating Garden Soundworks)
- Building FAITHH as personal AI assistant
- "Affordable but mighty" philosophy

---

## 🔗 Related Frameworks

### Harmony Framework
Biomechanical model mapped to AI architecture:
- Yang (intake) / Yin (return) cycles
- Phase-flip mechanisms
- Output-Coherence Sensor

### Phase Mediation Layer (PML)
Middleware for timing/routing decisions:
- Signals: Ambiguity, Evidence, Conflict, Urgency, Safety
- Outputs: PROCEED, DELAY, GROUND, REFRAME, TOOL, ABSTAIN

---

## 📞 Handoff Protocol

When completing a task:
1. Provide complete file contents with target path
2. List any dependencies or prerequisites
3. Note what Claude Code needs to implement
4. Flag decisions needing Jonathan's input

When receiving context:
1. Check `docs/session-reports/` for latest state
2. Verify ports/services haven't changed
3. Confirm which backend is active
