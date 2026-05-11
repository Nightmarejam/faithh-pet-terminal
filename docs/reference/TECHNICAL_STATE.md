# Technical View - Implementation Details

**Purpose**: Implementation details and system architecture  
**Complexity**: High  
**Update Frequency**: Real-time  
**Navigation**: [📋 Basic Overview] • [🔧 Functional View] • [⚡ Live State]

---

## 🏗️ Backend Architecture

**Framework**: Flask  
**Main File**: faithh_professional_backend_fixed.py  
**Port**: 5557

### API Endpoints
- /api/chat (main chat endpoint)
- /health (system health)
- /api/metrics (performance data)
- /api/chips (chip system status)


## 🎮 Chip System

### Core Components
- **Parallel Engine**: `backend/parallel_chip_engine.py`
- **Enhanced Integration**: `backend/enhanced_chip_integration.py`
- **Integration Script**: `backend/integrate_program_advances.py`

### Processing Details
- **Parallel Processing**: ThreadPoolExecutor with weighted RRF fusion
- **Semantic Detection**: Sentence transformers (CPU-only)

---

## 🗄️ Database Schema

### Primary Data Files
- faithh_memory.json (self-awareness)
- project_states.json (project status)
- decisions_log.json (decision history)
- scaffolding_state.json (open loops)

### Vector Database
- **Location**: ChromaDB @ Gen8:8000 (38K+ chunks)

### Cache System
- **Type**: LRU eviction, 100MB limit

---

## 🔌 API Endpoints

- **Faithh Backend**: http://localhost:5557
- **Project Hub**: http://localhost:5001
- **Chromadb**: http://192.158.1.243:8000
- **Ollama**: http://localhost:11434


## 📊 Performance Metrics

- **Monitoring**: backend/performance.py
- **Tracking**: Real-time metrics collection
- **Optimization**: Local AI optimization active
- **Cache Performance**: Measured and optimized

---

## 🐛 Error Tracking

### Recent Fixes
- NoneType error in coherence metadata (FIXED)
- Rate limiting disabled for single-user (INTENTIONAL)
- Model availability issues (RESOLVED)


---

*Last Updated: 2026-03-26T18:46:53.988688*  
*Navigation: [📋 Basic Overview] • [🔧 Functional View] • [⚡ Live State]*
