# Claude Code Handoff: FAITHH Testing & Maintenance
**Created**: 2025-12-30 (Updated after session break)
**Priority**: Test FAITHH, then cleanup documentation
**Context**: Previous Claude.ai session indexed 6,882 chunks, NAS mounted, but UI testing incomplete

---

## 🚨 Current System State (Verified 4:30 PM)

### What's Running
| Service | Status | Location |
|---------|--------|----------|
| FAITHH Backend | ✅ **RUNNING** | localhost:5557 (Mac) |
| ChromaDB | ✅ **RUNNING** | servicebox.taileb8c60.ts.net:8000 (Gen 8) |
| FAITHH UI | ❌ **NOT RUNNING** | Needs to be started |
| Windows Desktop | ❌ **OFFLINE** | 8+ days, contains 93k ChromaDB |

### Verification Commands
```bash
# Backend health check
curl -s http://localhost:5557/health | jq .

# ChromaDB heartbeat  
curl -s http://servicebox.taileb8c60.ts.net:8000/api/v2/heartbeat

# Check ChromaDB document count
curl -s "http://servicebox.taileb8c60.ts.net:8000/api/v2/tenants/default_tenant/databases/default_database/collections/71e13a01-cbb6-48ba-a126-2a16320d40c0/count"
# Expected: 27547
```

---

## 🎯 Task 1: Start and Test FAITHH UI

### Option A: FAITHH Lite (Simpler - Ollama-based)
```bash
cd /Users/macjohn/faithh
# Check what's here
ls -la
# Look for start script or README
cat README.md 2>/dev/null || cat *.md 2>/dev/null | head -50
```

### Option B: Full NaviGUI (If available)
```bash
# Check if NaviGUI exists on NAS
ls -la /Volumes/AI/NaviGUI/

# Or in ai-stack
ls -la /Users/macjohn/ai-stack/frontend/ 2>/dev/null
ls -la /Users/macjohn/ai-stack/ui/ 2>/dev/null
```

### Option C: Start UI from ai-stack
```bash
cd /Users/macjohn/ai-stack
# Look for UI startup instructions
grep -r "npm start\|npm run\|yarn\|vite" *.md docs/*.md 2>/dev/null | head -10

# Check package.json if exists
cat package.json 2>/dev/null | head -30
```

### What to Test Once UI is Running
1. **Basic chat** - Send "Hello, what can you help me with?"
2. **RAG retrieval** - Ask "What is the Astris formula in Constella?"
3. **Self-awareness** - Ask "What do you know about yourself?"
4. **Project context** - Ask "What are Jonathan's current project priorities?"
5. **Business context** - Ask "Tell me about Tom Cat Sound LLC structure"

---

## 🎯 Task 2: Test RAG Without UI (API-based)

If UI is problematic, test RAG directly via API:

```bash
# Test query endpoint
curl -X POST http://localhost:5557/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the Astris formula?", "use_rag": true}'

# Or if there's a query endpoint
curl -X POST http://localhost:5557/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the Astris formula?"}'
```

### Check Backend Endpoints
```bash
# List available endpoints
curl -s http://localhost:5557/ 2>/dev/null || \
curl -s http://localhost:5557/api 2>/dev/null || \
curl -s http://localhost:5557/routes 2>/dev/null
```

---

## 🎯 Task 3: Documentation Cleanup (Lower Priority)

### Files Needing Updates
After FAITHH testing is working, update these stale docs:

| File | Issue | Action |
|------|-------|--------|
| `docs/CURRENT_STATE.md` | Reflects Nov 2024 | Update to Dec 2025 state |
| `docs/GEN8_SERVICES_PLAN.md` | Says "planned" | Gen 8 is now RUNNING |
| `parity/PARITY_INDEX.md` | Many "unknown" status | Verify and update |
| `project_states.json` | Old dates | Update last_worked fields |
| `LIFE_MAP.md` | Missing recent context | Add Mexico, permaculture, FGS model |

### Re-index After Updates
```bash
cd /Users/macjohn/ai-stack
source venv/bin/activate
python scripts/index_docs_to_gen8.py
```

---

## 📊 Gen 8 ChromaDB Status

### Current Contents (27,547 chunks)
| Source | Chunks | Description |
|--------|--------|-------------|
| chatgpt | 18,401 | Conversations Oct-Dec 2025 |
| documentation | 6,829 | ai-stack + constella .md files |
| claude | 2,264 | Conversations Oct-Dec 2025 |
| nas_business | 53 | Tom Cat Sound LLC docs |

### Collection Details
- **Name**: faithh_knowledge_base
- **UUID**: 71e13a01-cbb6-48ba-a126-2a16320d40c0
- **Embedding**: BGE-base-en-v1.5 (768 dimensions)
- **Host**: servicebox.taileb8c60.ts.net:8000

### What's NOT Indexed (Waiting for Windows)
- Pre-October 2025 conversations (~18 months of history)
- Auto-indexed FAITHH live conversations (unique data in Windows `documents_768`)
- The 93k document database on Windows

---

## 🔧 Troubleshooting

### If Backend Crashes
```bash
cd /Users/macjohn/ai-stack
source venv/bin/activate
python faithh_professional_backend_fixed.py
```

### If ChromaDB Unreachable
```bash
# Check Gen 8 is online
ping -c 1 servicebox.taileb8c60.ts.net

# SSH to Gen 8 and check Docker
ssh user@servicebox.taileb8c60.ts.net
docker ps | grep chroma
```

### If Ollama Not Running (for FAITHH Lite)
```bash
ollama serve &
ollama list  # Should show llama3.2:3b or llama3.1:8b
```

---

## 📁 Key File Locations

### Mac Paths
```
/Users/macjohn/ai-stack/                    # Main FAITHH repo
/Users/macjohn/ai-stack/faithh_professional_backend_fixed.py  # Running backend
/Users/macjohn/ai-stack/scripts/            # Indexing scripts
/Users/macjohn/ai-stack/venv/               # Python environment
/Users/macjohn/faithh/                      # FAITHH Lite
/Volumes/AI/                                # NAS mount (Tom Cat Sound, NaviGUI)
```

### Network
```
Mac:        100.122.56.106 (Tailscale)
Gen 8:      servicebox.taileb8c60.ts.net (ChromaDB, Pi-hole)
NAS:        100.120.68.7 (Storage)
Windows:    100.115.225.100 (OFFLINE)
```

---

## ✅ Success Criteria

1. [ ] FAITHH UI accessible and responding
2. [ ] RAG queries return relevant indexed content
3. [ ] Can ask about Constella, FAITHH, Tom Cat Sound and get accurate answers
4. [ ] Documentation updates completed (if time permits)
5. [ ] Re-indexed after any doc updates

---

## 🚫 Do NOT Do

1. **Don't re-index conversations** - Wait for Windows to understand the 93k DB
2. **Don't modify `index_conversations.py`** - It's set up for Windows workflow
3. **Don't clear ChromaDB collections** - We just added 6,882 valuable chunks
4. **Don't run long embedding jobs** - Previous session had timeout issues

---

## 📝 Session Context

### What Was Done Today (Dec 30)
1. Full Tailscale network inventory
2. Gen 8 ChromaDB analysis (found 20,665 → now 27,547)
3. Indexed ai-stack docs (+6,829 chunks)
4. Indexed NAS business docs (+53 chunks)
5. Created FAITHH test questions document
6. Mounted NAS at /Volumes/AI

### What Caused Previous Session Breaks
Likely long-running processes (embedding generation, large queries) that timed out. Keep operations short and incremental.

---

*Handoff created for Claude Code - Dec 30, 2025*


---

## Appendix: FAITHH Lite Details

### Location
`/Users/macjohn/faithh/`

### Structure
```
faithh/
├── start.sh           # Start script (checks Ollama, creates venv)
├── stop.sh            # Stop script
├── faithh_lite.py     # Main backend (Flask)
├── faithh_lite.html   # Web UI
├── context/           # Context files loaded at startup
│   ├── audio.md
│   ├── constella.md
│   └── life_map.md
└── venv/              # Python virtual environment
```

### ⚠️ Port Conflict Warning
FAITHH Lite uses **port 5557** - same as the professional backend currently running.

**Before starting FAITHH Lite**, either:
1. Stop the professional backend first
2. Or modify `faithh_lite.py` to use a different port (e.g., 5558)

### To Start FAITHH Lite
```bash
# First, stop the professional backend if running
pkill -f faithh_professional_backend

# Then start Lite
cd /Users/macjohn/faithh
./start.sh

# Opens at http://localhost:5557
```

### To Start Professional Backend Instead
```bash
cd /Users/macjohn/ai-stack
source venv/bin/activate
python faithh_professional_backend_fixed.py

# Also at http://localhost:5557
```

### Key Difference
| Feature | FAITHH Lite | Professional Backend |
|---------|-------------|---------------------|
| LLM | Ollama (local) | Groq API (cloud) |
| RAG | Local context files | ChromaDB (Gen 8) |
| Features | Basic chat | Full integration (scaffolding, decisions, etc.) |
| Port | 5557 | 5557 |

**Recommendation**: Use Professional Backend for testing RAG retrieval since it connects to Gen 8 ChromaDB with all the indexed content.


---

## Appendix: UI Files Available

### HTML UI Options (No build required)
These can be opened directly in browser while backend runs on localhost:5557:

| File | Purpose |
|------|---------|
| `/Users/macjohn/ai-stack/faithh_pet_v4.html` | Main FAITHH Pet UI (MegaMan style) |
| `/Users/macjohn/ai-stack/frontend/html/faithh_pet_v4_enhanced.html` | Enhanced version |
| `/Users/macjohn/ai-stack/frontend/html/rag-chat.html` | RAG-focused chat interface |

### Quick Test
```bash
# Backend should already be running on 5557
# Just open the HTML file in browser:
open /Users/macjohn/ai-stack/faithh_pet_v4.html

# Or the RAG chat:
open /Users/macjohn/ai-stack/frontend/html/rag-chat.html
```

### If UI Doesn't Connect
1. Check backend is running: `curl http://localhost:5557/health`
2. Check browser console for CORS errors
3. The HTML files expect backend at `http://localhost:5557`
