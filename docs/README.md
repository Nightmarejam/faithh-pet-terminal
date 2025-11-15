# FAITHH System Documentation Index

**FAITHH** - Friendly AI Teaching & Helping Hub
A MegaMan Battle Network-inspired AI assistant system with RAG capabilities.

## 📚 Documentation Files

### Start Here
- **[CURRENT_STATE.md](CURRENT_STATE.md)** - Current system status, what's working/broken, next steps
  - Read this FIRST to understand where we are
  - Updated after each work session

### System Architecture
- **[DOCKER_SERVICES.md](DOCKER_SERVICES.md)** - What runs in Docker vs WSL
  - Service separation strategy
  - Network architecture diagram
  - Container management

- **[BACKEND_CONFIG.md](BACKEND_CONFIG.md)** - FAITHH backend configuration
  - API endpoints
  - Management commands (start/stop/restart)
  - Common issues & fixes

- **[CHROMADB_STATUS.md](CHROMADB_STATUS.md)** - ChromaDB setup and diagnostics
  - Current configuration
  - Solution options for connection issues
  - Testing commands

## 🎯 Quick Start for Claude Sessions

### For Claude Code:
1. Read `CURRENT_STATE.md` to understand current status
2. Check relevant config file for the task at hand
3. Execute changes and update `CURRENT_STATE.md`

### For Claude Chat:
1. Ask to read `CURRENT_STATE.md` 
2. Discuss strategy before making changes
3. Have Claude Code implement and update docs

## 🔄 Documentation Update Process

**After Each Session:**
1. Update `CURRENT_STATE.md` with:
   - What was fixed/changed
   - New issues discovered
   - Next steps
   
2. Update relevant config files if:
   - Architecture changed
   - New services added
   - Configuration modified

## 📋 System Components

### AI Services
- **FAITHH Backend** (WSL) - Main Flask API on port 5557
- **ChromaDB** (Docker/WSL) - Document embeddings and RAG
- **Ollama** (WSL) - Local LLM inference (qwen, llama)
- **Gemini API** - Cloud LLM for complex queries
- **LangFlow** (Docker) - Visual workflow builder

### User Interface
- **faithh_v4.html** - MegaMan Battle Network themed terminal
  - FAITHH character (cyan theme)
  - PULSE character (blue theme)
  - Voice input support (planned)

### Hardware Integration
- **RTX 3090** - GPU for local inference and image generation
- **UAD Volt 1** - Audio interface for recording
- **PreSonus Studio 1810c** - Expanded recording interface
- **SonoBus** - Network audio for remote collaboration

## 🎨 Project Themes
- MegaMan Battle Network aesthetic
- Retro-futuristic terminal UI
- Cyan (FAITHH) and Blue (PULSE) color schemes
- Net Navi character avatars

## 🔧 Common Tasks

### Check System Status
```bash
curl -s http://localhost:5557/api/status | jq
```

### Restart Backend
```bash
pkill -f faithh_professional_backend.py
cd ~/ai-stack && source venv/bin/activate
nohup python faithh_professional_backend.py > faithh_backend.log 2>&1 &
```

### View Backend Logs
```bash
tail -f ~/ai-stack/faithh_backend.log
```

### Check Docker Services
```bash
docker ps
```

## 🚀 Future Enhancements
- [ ] Voice-to-text integration
- [ ] Session logging system
- [ ] Luna DAW integration
- [ ] Automated documentation updates
- [ ] ComfyUI avatar generation
- [ ] Master action log system

## 📍 File Locations
- **Project Root:** `~/ai-stack/`
- **Documentation:** `~/ai-stack/docs/`
- **Backend:** `~/ai-stack/faithh_professional_backend.py`
- **UI:** `~/ai-stack/faithh_v4.html`
- **ChromaDB:** `~/ai-stack/faithh_rag/`
- **Uploads:** `~/ai-stack/uploads/`
- **Logs:** `~/ai-stack/faithh_backend.log`

---

**Last Updated:** 2024-11-14 23:30
**Maintained By:** Jonathan + Claude (Chat/Code tag-team)
