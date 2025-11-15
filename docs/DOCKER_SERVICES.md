# Docker vs WSL Service Separation

## Current Docker Services

### Running
- **LangFlow** (Port: ?)
  - Status: Running (PIDs 1250, 2195, 2196)
  - Purpose: Visual workflow builder for LLM chains
  - Location: Docker container

### Not Running / Unknown
- **ChromaDB** - NOT RUNNING (see CHROMADB_STATUS.md)
- Other services? (Need audit)

## Recommended Architecture

### 🐳 Should Run in Docker
1. **ChromaDB**
   - Why: Service isolation, easy restart, network accessible
   - Port: 8000
   - Volume: Mount `~/ai-stack/faithh_rag` to `/chroma/chroma`
   
2. **LangFlow** (already running)
   - Why: Complex dependencies, web service
   - Current status: Running
   
3. **Future considerations:**
   - Redis (for session management)
   - PostgreSQL (if needed for metadata)
   - Monitoring tools (Prometheus, Grafana)

### 💻 Should Run in WSL
1. **FAITHH Backend** (faithh_professional_backend.py)
   - Why: Direct filesystem access, easier development/debugging
   - Port: 5557
   - Current status: Running (PID 16440, 16481)

2. **Ollama**
   - Why: Direct GPU access needed for RTX 3090
   - Models: qwen2.5-coder:7b, qwen2.5-7b, llama3.1-8b
   - Current status: Running

3. **ComfyUI**
   - Why: Direct GPU access for image generation
   - Current status: Not running (start when needed)

4. **SonoBus**
   - Why: Audio routing needs direct hardware access
   - For: Remote collaboration with business partner

5. **Development Tools**
   - Python venv
   - Git repositories
   - Project files

## Docker Audit Needed

**Action Items:**
- [ ] Run `docker ps -a` to see all containers
- [ ] Identify what's installed but not running
- [ ] Document purpose of each container
- [ ] Clean up unused containers
- [ ] Create docker-compose.yml for easy management

## Network Architecture

```
┌─────────────────────────────────────────┐
│           WSL Ubuntu                     │
│                                          │
│  ┌──────────────────┐   ┌────────────┐ │
│  │ FAITHH Backend   │   │  Ollama    │ │
│  │   :5557          │   │            │ │
│  └────────┬─────────┘   └─────┬──────┘ │
│           │                   │         │
│           │                   │         │
│  ┌────────▼───────────────────▼──────┐ │
│  │         Docker Network            │ │
│  │                                   │ │
│  │  ┌──────────┐    ┌──────────┐   │ │
│  │  │ ChromaDB │    │ LangFlow │   │ │
│  │  │  :8000   │    │          │   │ │
│  │  └──────────┘    └──────────┘   │ │
│  └──────────────────────────────────┘ │
│                                        │
│  Volume Mounts:                        │
│  ~/ai-stack/faithh_rag → ChromaDB     │
└────────────────────────────────────────┘
```

## Benefits of This Separation

**Docker Services:**
- Easy to restart without affecting development
- Isolated environments
- Portable across machines
- Can scale horizontally if needed

**WSL Services:**
- Direct GPU access (critical for ML)
- Faster file system access
- Easier debugging and development
- Direct hardware access (audio interfaces)

## Next Actions
1. Audit all Docker containers
2. Start ChromaDB container with proper volume mount
3. Document LangFlow usage/purpose
4. Create docker-compose.yml for easy management
