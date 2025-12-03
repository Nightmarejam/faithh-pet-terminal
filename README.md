# FAITHH - Friendly AI Teaching & Helping Hub

Personal thought partner and knowledge management system.

**Version**: v3.3-scaffolding  
**Documents Indexed**: 93,606+

## Quick Start

```bash
./restart_backend.sh
# Open http://localhost:5557
```

## Key Files

| Need | File |
|------|------|
| Direction & priorities | `LIFE_MAP.md` |
| Getting started | `START_HERE.md` |
| System architecture | `ARCHITECTURE.md` |
| Testing guide | `FAITHH_TESTING_GUIDE.md` |

## What FAITHH Does

- Maintains context across projects (FAITHH, Constella, FGS audio)
- Searches 93K+ indexed conversations and documents
- Tracks decisions and rationale
- Provides structural orientation ("Where was I?")
- Conversation memory (Phase 1) - multi-turn context tracking

## Current Features

- **RAG System**: 93,606 indexed documents with smart query routing
- **Conversation Memory**: Tracks 5-10 exchanges per session
- **Context Integrations**: 6 layers (conversation, self-awareness, Constella, decisions, scaffolding, RAG)
- **Intent Detection**: Automatic query categorization
- **MegaMan Battle Network UI**: Retro-futuristic interface with battle chips
- **Local LLMs**: Gemini 2.0 Flash + Ollama (Llama 3.1-8B, Qwen 2.5-7B)
- **Auto-Indexing**: Conversations indexed in background

## Repository Structure

See `REPOSITORY_STRUCTURE.md` for full layout.

**Quick Overview**:
```
ai-stack/
├── faithh_professional_backend_fixed.py  # Main backend (v3.3)
├── faithh_pet_v4.html                    # UI with battle chip interface
├── scripts/                              # Utilities and tools
├── docs/                                 # Documentation and guides
└── backups/                              # Git-based version control
```

## Recent Updates

- **2025-12-02**: Repository cleanup, structure clarification
- **2025-11-30**: Phase 1 conversation memory integration complete
- **2025-11-29**: Scaffolding Layer 1 complete, testing framework established
- **2025-11-27**: Backend v3.3 with 6-layer context integration

## Development Status

**Completed**:
- ✅ Phase 1: Conversation Memory
- ✅ Scaffolding Layer 1: Position Awareness
- ✅ 6-layer context integration
- ✅ Intent detection system
- ✅ ChromaDB with 93K+ documents

**In Testing**:
- Daily usage validation
- Context priority tuning
- Integration effectiveness

**Future Phases**:
- Phase 2: Code generation & tool calling
- Multi-user support
- Agent capabilities

---

*Part of Jonathan's Celestial Equilibrium ecosystem*
