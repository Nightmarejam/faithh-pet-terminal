# FAITHH Work Tree

> **Generated:** 2026-03-01  
> **Source:** fingerprint_state.json, project_states.json, scaffolding_state.json

This document extracts what's **DONE**, what **NEEDS WORK**, and what's **BLOCKED** from the system fingerprint.

---

## Quick Status

| Category | Status |
|----------|--------|
| **Infrastructure** | ✅ Healthy (backend, ChromaDB, Ollama all operational) |
| **FAITHH Core** | ✅ Phase 3 Complete |
| **Next Phase** | 🔄 Phase 4: Production Hardening |

---

## ✅ DONE (Working, Don't Touch Unless Broken)

### Infrastructure
- [x] Backend running on localhost:5557
- [x] ChromaDB on Gen8 (38,295 docs indexed)
- [x] Ollama with 3 models (deepseek-r1:32b, qwen25-grounded, llama3.3:70b)
- [x] Gen8 MicroServer with 12 Docker services
- [x] Gen8 LAN networking for services (192.158.1.243)

### FAITHH Core Features
- [x] Multi-provider LLM (Ollama, Groq, Gemini)
- [x] RAG integration with 38K+ chunks
- [x] Intent detection and smart routing
- [x] Coherence Arbiter Phase 1-3 (semantic convergence measurement)
- [x] Anchor Validator (ground truth validation)
- [x] PULSE Reflection Engine (3 tiers)
- [x] 15 ML macro-chips with cosine routing
- [x] Self-awareness boost (faithh_memory.json)
- [x] Decision citation (decisions_log.json)
- [x] Project state awareness (project_states.json)
- [x] System Fingerprint (just implemented)

### Models
- [x] qwen25-grounded:latest — default model, grounded responses
- [x] deepseek-r1:32b — heavy reasoning model
- [x] Grounding fine-tune deployed (1914 examples, 16 categories)

### Documentation
- [x] AGENTS.md — repo guidelines
- [x] SYSTEM_FINGERPRINT.md — system identity
- [x] SYSTEMS_MAP.md — infrastructure map
- [x] CONTEXT.md — auto-generated context

---

## 🔄 IN PROGRESS (Active Work)

### FAITHH Phase 4: Production Hardening
| Task | Status | Priority |
|------|--------|----------|
| RAG sources display fix | Not started | High |
| Chat persistence (localStorage) | Partial | High |
| VS Code extension scaffolding | Not started | Medium |
| Strategic review system integration | Not started | Medium |

### Coherence Arbiter Phase 3 Expansion
| Task | Status | Priority |
|------|--------|----------|
| Additional claim types (decisions_log, project_states) | Ready | Medium |
| Adaptive thresholding | Ready | Medium |
| Autonomous PULSE scheduling | Not started | Low |

### IME (Inner Monologue Engine)
| Task | Status | Priority |
|------|--------|----------|
| C++ scaffold | ✅ Done | - |
| Resonance gate tests | ✅ 4 passing | - |
| Harmony docs indexing | Needs run | Medium |

---

## ⏸️ BLOCKED / WAITING

| Item | Blocked By | Action Needed |
|------|------------|---------------|
| Form 1065 filing | CPA | Waiting for CPA to file |
| Claude CLI MCP integration | Known issue | Documented, low priority |

---

## 📋 OPEN LOOPS (From scaffolding_state.json)

1. **coherence-arbiter-phase3-expansion** — Ready for implementation
   - Expand to decisions_log.json claims
   - Add project_states.json metrics validation
   - Implement adaptive thresholding

2. **claude-cli-mcp-integration-issue** — Known issue, documented

3. **form-1065-filing** — Pending CPA

4. **faithh-memory-staleness** — ✅ SOLVED

---

## 🎯 RECOMMENDED NEXT ACTIONS

### Immediate (This Session)
1. **RAG sources display fix** — Users can't see where info comes from
2. **Chat persistence** — Sessions lost on refresh

### Short-term (This Week)
3. **Coherence Arbiter expansion** — Add more claim types
4. **Run harmony docs indexing** — `python3 scripts/index_harmony_docs.py`

### Medium-term (This Month)
5. **VS Code extension scaffolding** — Start the extension
6. **vLLM exploration** — Per the roadmap we created

---

## Git Branch Strategy

### Current Branches
- `main` — Production, stable
- `refactor/clean-architecture` — Created today for improvements

### Recommended Workflow

```
main (stable)
  │
  ├── feature/rag-sources-display
  │     └── Fix RAG sources in UI
  │
  ├── feature/chat-persistence  
  │     └── localStorage + session recovery
  │
  ├── feature/coherence-expansion
  │     └── Additional claim types, adaptive thresholds
  │
  └── feature/vscode-extension
        └── Extension scaffolding
```

### Branch Naming Convention
- `feature/<name>` — New features
- `fix/<name>` — Bug fixes
- `refactor/<name>` — Code improvements
- `docs/<name>` — Documentation only

### Workflow Steps
1. Create branch from main: `git checkout -b feature/rag-sources-display`
2. Make changes, commit frequently
3. Test thoroughly
4. Merge back to main: `git checkout main && git merge feature/rag-sources-display`
5. Delete branch: `git branch -d feature/rag-sources-display`

---

## Project Status Summary

| Project | Phase | Status | Q1 2026 Priority |
|---------|-------|--------|------------------|
| **FAITHH** | Phase 3 → 4 | Operational | High |
| **Gen8 Services** | Production | Operational | Maintenance |
| **Tom Cat Sound** | Operations | Ongoing | Medium |
| **FGS** | Pre-Phase 1 | In Progress | Low |
| **IME** | Architecture | In Progress | Low |
| **Constella** | Phase 1 | In Progress | Low |

---

## How to Use This Document

1. **Before starting work:** Check "IN PROGRESS" section
2. **Pick a task:** Choose from "RECOMMENDED NEXT ACTIONS"
3. **Create a branch:** Follow the branch naming convention
4. **After completing:** Update this document and commit

---

*Last Updated: 2026-03-01*
