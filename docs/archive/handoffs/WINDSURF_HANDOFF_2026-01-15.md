# Windsurf + GPT 5.2 Codex XHigh Handoff
**Date:** 2026-01-15
**From:** Claude (claude.ai session)
**To:** Windsurf AI with GPT 5.2 Codex XHigh

> **Note:** This v1 handoff is superseded by `docs/WINDSURF_HANDOFF_v2_2026-01-15.md`.

---

## Executive Summary

Jonathan needs a **major cleanup and consolidation** of his FAITHH (Faithful AI Terminal Helper Hub) project. The codebase has accumulated technical debt from rapid iteration across multiple AI assistants, and needs systematic reconciliation.

**Core Goal:** Create a single, clean, canonical version of FAITHH that combines the best working features from multiple branches/files.

---

## Current State (Verified 2026-01-15)

### What's Working ✅
- **Backend:** `faithh_professional_backend_fixed.py` on localhost:5557
- **Endpoints verified:**
  - `/health` - Returns healthy
  - `/api/status` - Shows Ollama online, ChromaDB degraded
  - `/api/pulse/chips` - Program Advances working (Project Historian unlocked)
  - `/api/compass` - Compass dashboard data flowing
- **Models:** `llama31-faithh:latest` and `qwen3-faithh:latest` available in Ollama

### What's Broken/Degraded ⚠️
- **ChromaDB:** Showing `connected:false`, `documents:0` despite being reachable at servicebox.taileb8c60.ts.net:8000
  - Gen8 server has 28,876 chunks indexed
  - Likely a collection name or API version mismatch
- **UI File Confusion:** Backend serves `faithh_pet_v4.html` but Compass was built in `faithh_pet.html`
  - Recent session ported Compass to v4, but needs verification
- **Model List Mismatch:** Docs reference old `llama3.1:8b`, actual is `llama31-faithh:latest`

### Git State (Very Dirty)
```
## main...origin/main [ahead 3]
- 43 modified/deleted files
- 25+ untracked new files
- Last push: 070c843 (2026-01-08)
```

---

## Files of Interest

### Canonical Files (Source of Truth)
| File | Purpose |
|------|---------|
| `faithh_professional_backend_fixed.py` | Main backend (DO NOT rename) |
| `faithh_pet_v4.html` | Canonical UI (served by backend) |
| `project_states.json` | Machine-readable project state |
| `MASTER_CONTEXT.md` | Human-readable overview |
| `pulse_pattern_tracker.py` | Chip synthesis logic |
| `personalized_chips.json` | Program Advances store |

### Files to Reconcile/Merge
| File | Issue |
|------|-------|
| `faithh_pet.html` | Has Compass, but not served |
| `faithh_pet_v3.html` | Deleted but may have features |
| Multiple docs in `docs/` | Need parity updates |

### Files in Windows Downloads to Ingest
**High Priority (RAG exports - Jan 7, 2026):**
- `C:\Users\jonat\Downloads\ChatGPT_Jan7\conversations.json` (~95MB)
- `C:\Users\jonat\Downloads\Claude_Jan7\conversations.json` (~44MB)

**Project Documentation:**
- `tomcat_sound_llc_handoff_2025-12-19.md` → `projects/tomcat-sound/`
- `fgs-business-plan.md` → `projects/tomcat-sound/` or new FGS folder
- `next_steps_action_plan.md` → review for actionable items
- `hardware_inventory.md` → `parity/` or `infrastructure/`

**DO NOT INGEST (sensitive):**
- `Vertex AI API Key.txt`
- `Firefox_passwords.csv`
- `Google Passwords.csv`

---

## Immediate Tasks (Priority Order)

### 1. Fix ChromaDB Connection
**Symptoms:** Backend shows ChromaDB reachable but 0 documents
**Location:** `scripts/collect_system_state.py` lines 312-385

**Debug Steps:**
```bash
# Check Gen8 ChromaDB directly
curl -s "http://servicebox.taileb8c60.ts.net:8000/api/v2/heartbeat"
curl -s "http://servicebox.taileb8c60.ts.net:8000/api/v2/collections"

# Check collection name matches
# Backend expects: faithh_knowledge_base
```

**Likely Fix:** Update `CHROMA_URL` in `.env` or fix collection name reference in backend.

### 2. UI Reconciliation
**Goal:** Ensure `faithh_pet_v4.html` has all features from all versions

**Features to verify in v4:**
- [ ] Compass Dashboard tab + panel + JS
- [ ] PULSE chip display (active chips panel)
- [ ] Program Advance overlay/celebration
- [ ] RAG toggle
- [ ] Model selector with correct model names
- [ ] Error handling for `success:false` responses

**Reference:** Compare against worktree at `/home/jonat/ai-stack/worktrees/faithh-070c843`

### 3. Model Parity Update
**Change all docs from:**
- `llama3.1:8b` → `llama31-faithh:latest`
- `llama3:8b` → `llama31-faithh:latest`

**Files needing update:**
- `MASTER_CONTEXT.md`
- `docs/GPT_PROJECT_CONTEXT.md`
- `docs/CURRENT_STATE.md`
- Any `.env.example` files

### 4. Git Cleanup
**Strategy:**
1. Review deletions - are they intentional moves or accidents?
2. Stage intentional changes
3. Create meaningful commit: "Reconcile UI + fix model references + cleanup"
4. Push to origin

**Deletions to verify:**
- `ARCHIVE/2026-01-07_dedupe/*` - Likely intentional archive
- `projects/tomcat-sound/*.md` - Moved to subdirectories?
- `faithh_pet_v3.html` - Replaced by v4?

### 5. Ingest New Chat Exports
**Location:** `~/ai-stack/AI_Chat_Exports/`

**Process:**
```bash
# Copy from Windows Downloads
cp /mnt/c/Users/jonat/Downloads/ChatGPT_Jan7/* ~/ai-stack/AI_Chat_Exports/ChatGPT/
cp /mnt/c/Users/jonat/Downloads/Claude_Jan7/* ~/ai-stack/AI_Chat_Exports/Claude/

# Run indexing script (if exists)
python scripts/index_conversations.py
```

---

## Architecture Reference

### Infrastructure
```
Windows Desktop (DESKTOP-JJ1SUHB)
├── WSL2 Ubuntu 24.04
│   └── ~/ai-stack/ (main repo)
│       ├── FAITHH Backend (localhost:5557)
│       ├── Local ChromaDB (WSL - dev/backup)
│       └── Ollama (localhost:11434)
│
Gen8 MicroServer (servicebox)
├── Tailscale: servicebox.taileb8c60.ts.net
├── ChromaDB (port 8000) - PRODUCTION
│   └── Collection: faithh_knowledge_base
│   └── Documents: 28,876 chunks
└── Pi-hole (DNS)
```

### Key Paths
```bash
# Repo root
/home/jonat/ai-stack/

# Backend
/home/jonat/ai-stack/faithh_professional_backend_fixed.py

# UI
/home/jonat/ai-stack/faithh_pet_v4.html

# Project states (source of truth)
/home/jonat/ai-stack/project_states.json

# Worktree for comparison
/home/jonat/ai-stack/worktrees/faithh-070c843/

# Windows Downloads
/mnt/c/Users/jonat/Downloads/
```

### Environment Variables Needed
```bash
GROQ_API_KEY=<key>
GROQ_MODEL=llama-3.3-70b-versatile
CHROMA_URL=http://servicebox.taileb8c60.ts.net:8000
OLLAMA_HOST=http://127.0.0.1:11434
```

---

## Feature Inventory (What Should Work)

### Backend Features
- [x] Multi-provider LLM (Groq, Ollama, Gemini fallback)
- [x] RAG integration via ChromaDB
- [x] PULSE pattern tracking
- [x] Program Advance detection
- [x] Filesystem chip operations
- [x] Compass dashboard endpoints (`/api/compass`, `/api/compass/log`)
- [x] Self-awareness boost (`faithh_memory.json`)
- [x] Decision citation (`decisions_log.json`)

### UI Features (verify all in v4)
- [x] MegaMan Battle Network theme
- [x] Chat interface with streaming
- [x] RAG toggle
- [x] Model selector
- [ ] Compass Dashboard tab
- [ ] Active chips display
- [ ] Program Advance celebration overlay
- [ ] PULSE status panel

---

## Known Issues to Debug

### 1. Empty Chip Arrays in PULSE
`pulse_patterns.json` shows recent entries with `"chips": []`:
```json
{
  "chips": [],
  "timestamp": "2026-01-15T01:08:34.896277"
}
```
**Suggests:** Chip detection may not be triggering properly.

### 2. PCIe Bandwidth (Low Priority)
RTX 3090 was showing Gen1 speeds, but recent session verified it's at Gen3 x16. May be resolved.

### 3. Parity Drift
Multiple context files exist:
- `MASTER_CONTEXT.md`
- `docs/GPT_PROJECT_CONTEXT.md`
- `docs/CURRENT_STATE.md`
- `docs/FAITHH_REVIEW_NEXT_STEPS.md`

These need systematic synchronization. Consider:
- Single source of truth (project_states.json)
- Generated markdown files from JSON
- Parity check script

---

## Recommended Workflow

1. **Start with ChromaDB fix** - This blocks RAG functionality
2. **UI verification** - Open localhost:5557 and test all tabs
3. **Run full test suite** (if exists) or manual smoke test
4. **Git cleanup** - Stage, commit, push
5. **Ingest new exports** - Update RAG with latest conversations
6. **Update parity docs** - Sync all context files

---

## Contact Points

- **Gen8 SSH:** `ssh -i ~/.ssh/servicebox_ed25519 jonat@servicebox.taileb8c60.ts.net`
- **Backend health:** `curl http://localhost:5557/health`
- **ChromaDB health:** `curl http://servicebox.taileb8c60.ts.net:8000/api/v2/heartbeat`
- **Git remote:** `github.com:Nightmarejam/faithh-pet-terminal.git`

---

## Success Criteria

After this session, Jonathan should have:
1. ✅ Working ChromaDB connection (showing 28K+ docs)
2. ✅ Unified UI with all features in `faithh_pet_v4.html`
3. ✅ Clean git state (committed and pushed)
4. ✅ Updated parity docs with correct model names
5. ✅ New chat exports indexed into RAG
6. ✅ Clear path for ongoing maintenance

---

## Jonathan's Preferences (from memory)

- **Iterative building** over big-bang designs
- **Machine-readable outputs** that AI can query
- **Low-friction data capture** (organic logging, not manual)
- **Passive journaling** via work_log.json and synthesis
- **Complete visibility** into processes and work patterns

---

**End of Handoff**

*Generated by Claude on 2026-01-15 for session continuity*
