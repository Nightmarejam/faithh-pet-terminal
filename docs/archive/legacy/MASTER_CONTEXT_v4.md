# 🎯 FAITHH Master Context - Professional Workspace
**Version**: 4.0  
**Last Updated**: 2025-11-06  
**System Status**: ✅ Operational (Embedding fix needed)  
**Current Chat Model**: Llama 3.1-8B (Meta via Ollama)

---

## 🔧 IMMEDIATE FIXES NEEDED

### 1. ChromaDB Embedding Dimension Issue
**Problem**: Collection expects 768 dimensions, getting 384  
**Cause**: Documents indexed with different embedding model  
**Solution**: Using `query_texts` instead of embeddings (implemented in v3 backend)  
**Status**: ✅ Fixed in faithh_professional_backend.py

### 2. Model Identification
**Current Model**: Llama 3.1-8B (confirmed from your screenshot)  
**Provider**: Meta (via Ollama local instance)  
**Response Time**: ~2-3 seconds locally  
**Status**: ✅ Model detection implemented

---

## 📊 CURRENT SYSTEM INVENTORY

### 🖥️ Hardware Assets
| Item | Model | Purpose | Status |
|------|-------|---------|--------|
| MacBook Pro | M1 | Primary workstation | ✅ Active |
| PreSonus Studio 1810c | USB-C Interface | Multi-track recording | ✅ Ready |
| UAD Volt 1 | Audio Interface | DI Recording | ✅ Ready |
| Partner's Mac Mini | M2 | Collaboration hub | ✅ Available |

### 💾 Software Stack
| Category | Software | Purpose | Status |
|----------|----------|---------|--------|
| DAW | Luna | Audio production | 📋 To Install |
| Streaming | OBS Studio | Live streaming | ✅ Installed |
| Routing | BlackHole | Audio routing | 📋 To Install |
| Collaboration | SonosBus | Network audio | 📋 To Install |
| AI Backend | Ollama | Local LLMs | ✅ Running |
| RAG | ChromaDB | Document search | ✅ 91,302 docs |
| Framework | Flask | Web backend | ✅ Running |

### 🤖 AI Models Available
| Model | Provider | Size | Purpose | Status |
|-------|----------|------|---------|--------|
| Llama 3.1-8B | Meta/Ollama | 8B | General chat | ✅ Active |
| Qwen 2.5-7B | Alibaba/Ollama | 7B | Code/Technical | ✅ Available |
| Gemini 2.0 Flash | Google | Cloud | Advanced reasoning | ⚠️ Needs API key |
| Claude Opus | Anthropic | Cloud | Complex tasks | 📋 Future |

### 📁 Project Structure (Current)
```
~/ai-stack/
├── faithh_pet_v3.html (current UI)
├── faithh_enhanced_backend.py (v2)
├── faithh_professional_backend.py (v3 - recommended)
├── Audio/
│   ├── Immediate_Workflow_Setup_Guide.md
│   ├── Three_Tier_Audio_Workflow.md
│   └── Audio_AI_Ecosystem_Master_Plan.docx
├── uploads/ (file attachments)
├── venv/ (Python environment)
└── [93 other files needing organization]
```

---

## 🎯 STABLE BUILD REQUIREMENTS

### Phase 1: Core Stabilization (THIS WEEK)
- [x] Fix ChromaDB embedding dimension ✅
- [x] Identify active model correctly ✅
- [x] Create enhanced UI with more chat space ✅
- [ ] Clean up redundant files
- [ ] Implement file upload system
- [ ] Test all services together

### Phase 2: Workspace Organization (NEXT WEEK)
```bash
# Proposed clean structure
~/ai-stack/
├── active/
│   ├── backend/
│   │   └── faithh_pro_v3.py (main backend)
│   ├── frontend/
│   │   └── faithh_v4.html (enhanced UI)
│   └── config/
│       └── settings.yaml
├── archive/
│   └── [old versions moved here]
├── data/
│   ├── chromadb/
│   ├── uploads/
│   └── sessions/
├── audio/
│   ├── workflows/
│   ├── templates/
│   └── projects/
└── docs/
    └── MASTER_CONTEXT.md (this file)
```

### Phase 3: Professional Features (MONTH 1)
- [ ] Voice-to-text integration
- [ ] Auto session logging
- [ ] Luna DAW templates
- [ ] OBS scene switching
- [ ] Streaming overlays

---

## 🎮 USE CASE WORKFLOWS

### 1. Video Game Streaming
**Components Needed**:
- OBS Studio scenes
- Chat overlay from FAITHH
- Battle chip activations as stream alerts
- Voice commands for scene switching

**Data Flow**:
```
Game Audio/Video → OBS → Stream
FAITHH Chat → Overlay → Stream  
Voice Commands → FAITHH → OBS Control
```

### 2. Professional Audio Production
**Three-Tier System**:
1. **Home**: Volt 1 + Luna + FAITHH logging
2. **Mobile Light**: Software only + remote review
3. **Mobile Pro**: Full Gator case setup (future)

**Integration Points**:
- Session notes → ChromaDB indexing
- Plugin settings → Searchable knowledge
- Client feedback → RAG retrieval
- Collaboration logs → Training data

### 3. Live Online Work
**Requirements**:
- Real-time transcription
- Screen sharing with annotation
- Client portal access
- Session recording and indexing

---

## 🚀 STARTUP SEQUENCE

### Quick Start (Daily Use)
```bash
cd ~/ai-stack
source venv/bin/activate
python3 faithh_professional_backend.py
# Open browser to http://localhost:5557
```

### Full System Start
```bash
# 1. Check all services
python3 system_health_check.py

# 2. Start enhanced backend
python3 faithh_professional_backend.py

# 3. Open enhanced UI
# Browser → http://localhost:5557 (v4 UI)
```

### Add Gemini (One-time)
```bash
export GEMINI_API_KEY="your-key-here"
# Or
echo "GEMINI_API_KEY=your-key-here" > .env
```

---

## 📈 METRICS & MONITORING

### Current System Performance
- **Documents Indexed**: 91,302
- **Average Response Time**: 2-3 seconds (Llama)
- **RAM Usage**: ~2GB (Ollama models)
- **Storage Used**: ~15GB (models + data)
- **Uptime**: Varies (manual start)

### Target Metrics
- Response time < 1 second for cache hits
- 99.9% uptime with auto-restart
- Session logging for all interactions
- Weekly backup of all data

---

## 🎯 DECISION TREE

### When to Use Which Model:
```
Simple Chat → Llama 3.1 (fast, local)
Technical/Code → Qwen 2.5 (specialized)
Complex Reasoning → Gemini (when configured)
Creative Writing → Claude (future)
```

### When to Use RAG:
```
Past Conversations → Always
Technical Documentation → Always
Session History → Always
General Knowledge → Only if specific
```

### File Organization Priority:
```
1. Archive old API versions → /archive
2. Keep only v3 backend → /active
3. Move audio guides → /audio/workflows
4. Clean Python cache → delete *.pyc
5. Organize by function → not by date
```

---

## 🔄 LIVING DOCUMENT UPDATES

This document should be updated:
- After each major code change
- When new services are added
- Weekly metrics review
- After client sessions (learnings)

### Update Command:
```python
# Auto-update from FAITHH chat
POST /api/update_context
{
  "type": "technical|session|learning",
  "content": "update details"
}
```

---

## 🎨 UI/UX IMPROVEMENTS (v4)

### Implemented in faithh_pet_v4.html:
- ✅ Larger chat area (70% of screen)
- ✅ Collapsible sidebars for more space
- ✅ File upload with preview
- ✅ Model identification display
- ✅ Response time tracking
- ✅ Battle chips as quick actions
- ✅ Minimized avatar display

### Still Needed:
- [ ] Dark/Light theme toggle
- [ ] Export chat history
- [ ] Search within chat
- [ ] Code syntax highlighting
- [ ] Image preview in chat
- [ ] Voice input button

---

## 🚨 CRITICAL PATHS

### If Backend Crashes:
```bash
# Quick restart
pkill -f faithh
python3 faithh_professional_backend.py
```

### If ChromaDB Won't Connect:
```bash
# Check if running
curl http://localhost:8000/api/v1
# Restart if needed
docker-compose restart chromadb
```

### If Ollama Not Responding:
```bash
# Check models
curl http://localhost:11434/api/tags
# Restart service
systemctl restart ollama  # or
docker restart ollama
```

---

## 📋 TODAY'S PRIORITY TASKS

1. **Switch to v3 Backend**:
   ```bash
   cp faithh_professional_backend.py ~/ai-stack/
   python3 ~/ai-stack/faithh_professional_backend.py
   ```

2. **Test New UI**:
   ```bash
   cp faithh_pet_v4.html ~/ai-stack/
   # Then open http://localhost:5557
   ```

3. **Clean Workspace**:
   ```bash
   # Create archive
   mkdir -p ~/ai-stack/archive
   # Move old versions
   mv ~/ai-stack/*api*.py ~/ai-stack/archive/
   mv ~/ai-stack/*v1*.py ~/ai-stack/archive/
   mv ~/ai-stack/*v2*.py ~/ai-stack/archive/
   ```

4. **Test File Upload**:
   - Drag files into new UI
   - Verify they appear in chat
   - Check ~/ai-stack/uploads/

5. **Document Session**:
   - What worked
   - What broke
   - What's needed next

---

**End of Master Context v4.0**  
**Next Review**: End of day today  
**Maintained by**: FAITHH System + Human