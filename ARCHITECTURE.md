# FAITHH Architecture Design Document v1.0
**Date**: 2025-11-19  
**Status**: AUTHORITATIVE - All future development follows this  
**Author**: Jonathan + Claude Opus 4.1

---

## 🎯 Core Design Principles

1. **Stability First**: Never break working features
2. **Modular Everything**: Features as importable modules
3. **Documentation Driven**: Code follows design, not vice versa
4. **ADHD-Friendly**: Clear states, comprehensive logging, easy recovery

---

## 🏛️ System Architecture

### Current: Monolithic (Stable)
```
┌─────────────────────────────────────────────────────────┐
│           faithh_professional_backend_fixed.py          │
│                     (Port 5557)                         │
├─────────────────────────────────────────────────────────┤
│ Flask Server                                            │
│ ├── /api/chat          (RAG + Memory + LLM)            │
│ ├── /api/test_memory   (Memory validation)             │
│ ├── /api/status        (Health check)                  │
│ └── /api/rag_search    (Direct RAG query)              │
├─────────────────────────────────────────────────────────┤
│ Core Components                                         │
│ ├── Memory (faithh_memory.json)                        │
│ ├── RAG (ChromaDB - 91,604 docs)                       │
│ ├── Personality (get_faithh_personality())             │
│ └── LLM Router (Ollama ↔ Gemini)                       │
└─────────────────────────────────────────────────────────┘
```

### Future: Modular Monolith (Phase 2+)
```
┌─────────────────────────────────────────────────────────┐
│           FAITHH Backend (Monolithic Core)              │
├─────────────────────────────────────────────────────────┤
│ Flask Blueprints (Hot-swappable modules)                │
│ ├── core_blueprint       (Essential: chat, memory)     │
│ ├── phase2_blueprint     (Auto-index, summaries)       │
│ ├── audio_blueprint      (Workflow automation)         │
│ └── tools_blueprint      (Safe execution engine)       │
├─────────────────────────────────────────────────────────┤
│ Services (Internal)                                     │
│ ├── MemoryService   (Three-tier cache)                 │
│ ├── RAGRouter       (Domain-aware retrieval)           │
│ ├── WorkflowEngine  (Audio/streaming automation)       │
│ └── ParityManager   (Doc auto-update)                  │
└─────────────────────────────────────────────────────────┘
```

**Timeline**: Stay monolithic for 2-4 weeks, split to microservices only when:
- Backend exceeds 2000 lines
- Need independent scaling
- Multiple developers contributing

---

## 💾 Memory Architecture (Three-Tier)

### Design Pattern: CPU Cache Hierarchy

```
┌────────────────────────────────────────────────────────┐
│ HOT MEMORY (L1 Cache) - In RAM, <1KB                  │
├────────────────────────────────────────────────────────┤
│ Content: Current session state                         │
│ {                                                       │
│   "user": "Jonathan",                                  │
│   "session_start": "2025-11-19T10:00:00",             │
│   "current_domain": "audio",                           │
│   "last_5_messages": [...],                            │
│   "active_workflow": "mastering_session"               │
│ }                                                       │
│                                                         │
│ Access: Instant (0ms)                                  │
│ Lifespan: Current conversation only                    │
│ Storage: Python dict in backend memory                 │
└────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────┐
│ WARM MEMORY (L2 Cache) - JSON, <100KB                 │
├────────────────────────────────────────────────────────┤
│ Content: Session summaries + User profile              │
│ {                                                       │
│   "user_profile": {                                    │
│     "name": "Jonathan",                                │
│     "role": "Audio Producer & AI Developer",           │
│     "projects": ["FAITHH", "Constella"],               │
│     "preferences": {...}                               │
│   },                                                    │
│   "recent_sessions": [                                 │
│     {                                                   │
│       "date": "2025-11-18",                            │
│       "summary": "Worked on RAG optimization",         │
│       "decisions": ["Use 768-dim embeddings"],         │
│       "next_steps": ["Integrate Phase 2"]              │
│     }                                                   │
│   ]                                                     │
│ }                                                       │
│                                                         │
│ Access: Fast (5-20ms)                                  │
│ Lifespan: Permanent, manually curated                  │
│ Storage: faithh_memory.json                            │
└────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────┐
│ COLD MEMORY (L3 Cache) - ChromaDB, Unlimited          │
├────────────────────────────────────────────────────────┤
│ Content: Full conversation history + docs              │
│ - 91,604 indexed documents                             │
│ - All past conversations (chunked)                     │
│ - Session transcripts                                  │
│ - Code snippets and solutions                          │
│                                                         │
│ Access: Semantic search (50-200ms)                     │
│ Lifespan: Permanent, auto-indexed                      │
│ Storage: ChromaDB collections                          │
└────────────────────────────────────────────────────────┘
```

### Memory Update Flow

```python
def update_memory_tiers(conversation):
    # HOT: Update every message (in-memory)
    hot_memory['last_5_messages'].append(new_message)
    hot_memory['current_domain'] = detect_domain(new_message)
    
    # WARM: Update every 10 messages OR at key moments
    if len(conversation) % 10 == 0 or is_key_decision(new_message):
        warm_summary = summarize_last_10(conversation)
        save_to_json(warm_summary)
    
    # COLD: Auto-index every conversation (Phase 2)
    if PHASE2_ENABLED:
        auto_index_conversation(conversation)
```

**Decision**: 
- ✅ Keep JSON for hot/warm (fast, simple)
- ✅ ChromaDB for cold (semantic search)
- ❌ No SQLite needed (yet)

---

## 🎯 Domain Routing System

### Domain Detection Strategy

```python
DOMAIN_CONFIG = {
    'audio': {
        'keywords': ['mastering', 'luna', 'wavelab', 'db', 'gain', 'compression', 
                     'voicemeeter', 'sonobus', 'uad', 'presonus'],
        'priority': 1,  # Highest
        'collection': 'audio_production',
        'context_size': 'large'  # More context for technical work
    },
    'development': {
        'keywords': ['python', 'flask', 'api', 'backend', 'frontend', 'git',
                     'docker', 'chromadb', 'function', 'code'],
        'priority': 2,
        'collection': 'dev_docs',
        'context_size': 'medium'
    },
    'constella': {
        'keywords': ['civic', 'framework', 'constella', 'portfolio', 'municipality'],
        'priority': 1,
        'collection': 'constella_framework',
        'context_size': 'large'
    },
    'streaming': {
        'keywords': ['obs', 'twitch', 'stream', 'game', 'capture', 'elgato'],
        'priority': 2,
        'collection': 'streaming_setup',
        'context_size': 'medium'
    },
    'general': {
        'keywords': [],  # Catch-all
        'priority': 3,
        'collection': 'documents',
        'context_size': 'small'
    }
}

def route_to_domain(query: str) -> str:
    """Detect domain from query keywords"""
    query_lower = query.lower()
    
    # Score each domain
    scores = {}
    for domain, config in DOMAIN_CONFIG.items():
        score = sum(1 for kw in config['keywords'] if kw in query_lower)
        if score > 0:
            scores[domain] = score * config['priority']
    
    # Return highest scoring domain
    return max(scores.items(), key=lambda x: x[1])[0] if scores else 'general'
```

**ChromaDB Collections** (Separate by domain):

```python
# Create domain-specific collections
collections = {
    'audio_production': chroma_client.get_or_create_collection("audio_production"),
    'dev_docs': chroma_client.get_or_create_collection("dev_docs"),
    'constella_framework': chroma_client.get_or_create_collection("constella_framework"),
    'streaming_setup': chroma_client.get_or_create_collection("streaming_setup"),
    'live_conversations': chroma_client.get_or_create_collection("live_conversations"),
    'documents': chroma_client.get_or_create_collection("documents")  # General
}
```

**Migration Strategy**:
1. Keep current single collection working
2. Create new domain collections in parallel
3. Gradually migrate docs (bulk script)
4. Switch routing once migrated
5. Archive old single collection

---

## 🔧 Phase 2 Integration Strategy

### Flask Blueprint Architecture (Safe & Modular)

```python
# phase2_blueprint.py
from flask import Blueprint, request, jsonify
from datetime import datetime

def create_phase2_blueprint(collection, chroma_connected):
    """Factory function - gets backend state, returns configured blueprint"""
    
    phase2 = Blueprint('phase2', __name__)
    
    @phase2.route('/api/auto_index', methods=['POST'])
    def auto_index():
        """Endpoint to manually test auto-indexing"""
        data = request.json
        # Implementation here
        pass
    
    @phase2.route('/api/session_summary', methods=['GET'])
    def session_summary():
        """Generate summary of current session"""
        # Implementation here
        pass
    
    @phase2.route('/api/memory_suggestions', methods=['GET'])
    def memory_suggestions():
        """Analyze recent convos for memory updates"""
        # Implementation here
        pass
    
    return phase2

# In main backend:
from phase2_blueprint import create_phase2_blueprint

# After ChromaDB initialization
phase2_bp = create_phase2_blueprint(collection, CHROMA_CONNECTED)
app.register_blueprint(phase2_bp)
```

**Benefits**:
- ✅ No modification to main backend code
- ✅ Can enable/disable entire Phase 2 with one line
- ✅ Easy to test independently
- ✅ No indentation hell

---

## 🎵 Audio Workspace Architecture

### VoiceMeeter Configuration (Documented)

```yaml
# Audio Routing Map
INPUTS:
  Hardware1:
    device: "Blue Yeti"
    type: "Mono"
    routing: [A1, B1]  # Headphones + OBS
    use: "Voice/Commentary"
    
  Hardware2:
    device: "Elgato 4K X Audio"
    type: "Stereo"
    routing: [A1, B1]
    use: "Game audio capture"
    
  Hardware3:
    device: "UAD Volt 1"
    type: "Stereo"
    routing: [A1]  # Monitor only
    use: "DAW monitoring"
    
  Virtual_VAIO:
    device: "System Audio (Windows)"
    routing: [A1, B1]
    use: "Desktop sounds"
    
  Virtual_AUX:
    device: "Discord"
    routing: [A1]  # Your ears only
    use: "Communication"
    
  Virtual_VAIO3:
    device: "Games/Apps"
    routing: [A1, B1]
    use: "Game audio"

OUTPUTS:
  A1:
    device: "Headphones"
    processing: "Sonarworks correction"
    use: "Personal monitoring"
    
  B1:
    device: "OBS Stream Mix"
    processing: "None (flat)"
    use: "Stream output"
    
  B2:
    device: "Sonobus"
    use: "Remote collaboration"
    enabled: false  # Enable when needed
    
  B3:
    device: "DAW Recording"
    use: "Session capture"
    enabled: false  # Future use
```

### OBS Configuration

```yaml
# OBS Settings (for automation)
Canvas: "2560x1440"  # Native monitor resolution
Output: "1920x1080"  # Standard streaming
FPS: 60
Encoder: "NVENC (1080 Ti)"
Bitrate: "6000-9000 kbps"

Scenes:
  - name: "Game + Webcam"
    sources:
      - "Game Capture (1080 Ti)"
      - "Elgato 4K X (passthrough display)"
      - "Razer Kiyo Pro (webcam)"
      - "Audio: VoiceMeeter B1"
      
  - name: "Just Chatting"
    sources:
      - "Webcam (fullscreen)"
      - "Audio: VoiceMeeter B1"
      
  - name: "Screen Share"
    sources:
      - "Display Capture"
      - "Webcam (corner)"
      - "Audio: VoiceMeeter B1"
```

### Automation Goals

```python
# Future workflow automation
class AudioWorkflow:
    def start_mastering_session(self):
        """Setup for mastering work"""
        # 1. Load VoiceMeeter config (mastering preset)
        # 2. Set Volt 1 monitoring
        # 3. Disable stream outputs (B1, B2)
        # 4. Open WaveLab
        # 5. Log session start in FAITHH
        
    def start_streaming_session(self):
        """Setup for game streaming"""
        # 1. Load VoiceMeeter config (streaming preset)
        # 2. Enable all outputs
        # 3. Launch OBS
        # 4. Start game
        # 5. Log session start
        
    def start_remote_recording(self):
        """Setup for remote collaboration"""
        # 1. Load VoiceMeeter config (recording preset)
        # 2. Enable Sonobus output (B2)
        # 3. Connect to partner's M2 Mac Mini
        # 4. Open Luna DAW
        # 5. Log session
```

---

## 📊 Parity System Design

### Daily Batch Update Strategy

```python
# scripts/maintenance/daily_parity_update.py

class ParityManager:
    def run_daily_update(self):
        """Runs once per day via cron"""
        
        # 1. Scan codebase for changes
        changes = self.detect_changes()
        
        # 2. Generate update suggestions
        suggestions = self.analyze_doc_gaps(changes)
        
        # 3. Auto-update safe docs (CURRENT_STATE.md)
        self.safe_auto_update(suggestions['safe'])
        
        # 4. Create PR for manual review (README, ARCHITECTURE)
        self.create_review_branch(suggestions['review'])
        
        # 5. Log to MASTER_ACTION_LOG.md
        self.log_parity_run(changes, suggestions)
```

**Update Schedule**:
- **Every commit**: Update CURRENT_STATE.md (automated)
- **Daily**: Run parity check, suggest updates
- **Weekly**: Manual review of documentation
- **Per session**: Update session handoff

---

## 🔐 Tool Execution Safety (Future)

### Rollback Pattern

```python
class SafeExecutor:
    def execute_with_rollback(self, command, target):
        """Git-style rollback for any operation"""
        
        # 1. Create snapshot
        snapshot = self.git_snapshot()
        
        # 2. Dry run
        if not self.dry_run(command):
            return {"error": "Dry run failed"}
        
        # 3. Execute with timeout
        try:
            result = self.run_with_timeout(command, 30)
            
            # 4. Validate
            if self.validate(result):
                return {"success": True, "result": result}
            else:
                self.git_rollback(snapshot)
                return {"error": "Validation failed", "rolled_back": True}
                
        except TimeoutError:
            self.git_rollback(snapshot)
            return {"error": "Timeout", "rolled_back": True}
```

---

## 📁 File Structure (Final)

```
~/ai-stack/
├── faithh_professional_backend_fixed.py  # Main monolith
├── phase2_blueprint.py                   # Phase 2 module
├── audio_blueprint.py                    # Audio automation (future)
├── tools_blueprint.py                    # Safe execution (future)
│
├── faithh_memory.json                    # Warm memory
├── parity_state.json                     # Last parity check
│
├── scripts/
│   ├── indexing/
│   │   ├── index_by_domain.py           # Domain-aware indexing
│   │   └── migrate_to_domains.py        # Bulk migration
│   ├── maintenance/
│   │   ├── daily_parity_update.py       # Automated doc sync
│   │   └── health_check.sh
│   ├── audio/
│   │   ├── start_mastering.py           # Workflow automation
│   │   ├── start_streaming.py
│   │   └── voicemeeter_control.py
│   └── memory/
│       └── summarize_session.py
│
├── parity/
│   ├── USER_PROFILE.md                  # Jonathan's context
│   ├── PROJECT_STATE.md                 # Live system state
│   └── DOMAIN_CONFIGS/
│       ├── audio.yaml
│       ├── streaming.yaml
│       └── development.yaml
│
├── docs/
│   ├── ARCHITECTURE.md                  # This file
│   ├── FAITHH_HANDBOOK.md              # Operator manual
│   └── session-reports/
│
└── streaming/
    ├── voicemeeter_presets/
    ├── obs_scenes.json
    └── automation_scripts/
```

---

## ✅ Implementation Checklist

### This Week
- [ ] Create phase2_blueprint.py
- [ ] Test auto-indexing independently
- [ ] Integrate Phase 2 blueprint
- [ ] Create domain migration script
- [ ] Document audio workflows
- [ ] Set up daily parity cron job

### Next Week
- [ ] Migrate docs to domain collections
- [ ] Implement three-tier memory
- [ ] Build audio automation scripts
- [ ] Create session summarizer
- [ ] Test rollback system

### Future (Month 2+)
- [ ] Consider microservices split
- [ ] Advanced tool execution
- [ ] Voice integration
- [ ] DAW automation

---

## 🎯 Success Criteria

**Phase 2 Complete When:**
- ✅ Auto-indexing works without crashes
- ✅ Session summaries generate on command
- ✅ Memory suggestions detect new projects
- ✅ No regression in existing features

**Architecture Stable When:**
- ✅ Documentation matches reality
- ✅ Parity runs without manual intervention
- ✅ Rollback system tested and proven
- ✅ All workflows documented and automated

---

**Next Actions**: Create phase2_blueprint.py following this architecture
