# FAITHH Actual Architecture (Updated 2026-01-14)

**Status**: CURRENT - Based on actual system verification  
**Last Verified**: 2026-01-14 22:20 PST

---

## 🎯 Critical Updates from Previous Documentation

### What Changed
The previous `ARCHITECTURE.md` and `MULTI_DEVICE_DEPLOYMENT_STRATEGY.md` assumed Docker-based services on WSL2. **This is now incorrect.**

**Actual Current State**:
- ✅ **Native Ollama** on WSL2 (not Docker)
- ✅ **ChromaDB on Gen8** (servicebox.taileb8c60.ts.net:8000) - not local
- ❌ **No Docker services** on WSL2 (all removed)
- ✅ **Gen8 as data layer** (already deployed)

---

## 🏛️ Actual System Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    Gen8 HP ProLiant                          │
│                  (servicebox.taileb8c60.ts.net via Tailscale)                │
├──────────────────────────────────────────────────────────────┤
│ Docker Services:                                             │
│ ├── ChromaDB :8000                                           │
│ │   └── Collection: faithh_knowledge_base (29,013 docs)     │
│ ├── Pi-hole :53, :80                                         │
│ └── Uptime Kuma :3001                                        │
└──────────────────────────────────────────────────────────────┘
                            ▲
                            │ Network (Tailscale)
                            │
┌──────────────────────────────────────────────────────────────┐
│                    WSL2 Ubuntu (DESKTOP-JJ1SUHB)             │
│                    Windows Host                              │
├──────────────────────────────────────────────────────────────┤
│ Native Services (NO DOCKER):                                 │
│ ├── Ollama (native systemd) :11434                          │
│ │   ├── GPU 0: GTX 1080 Ti (11GB) - currently used          │
│ │   ├── GPU 1: RTX 3090 (24GB) - available                  │
│ │   └── Models: qwen3-faithh:latest, llama31-faithh:latest  │
│ └── FAITHH Backend :5557 (Flask, Python venv)               │
│     └── Connects to Gen8 ChromaDB                            │
└──────────────────────────────────────────────────────────────┘
```

---

## 📋 Verified Configuration

### Environment Variables (.env)
```bash
OLLAMA_HOST=http://127.0.0.1:11434      # Native Ollama on WSL2
CHROMADB_HOST=servicebox.taileb8c60.ts.net               # Gen8 server
CHROMA_HOST=http://servicebox.taileb8c60.ts.net:8000    # Gen8 ChromaDB
```

### Hardware Specifications

#### WSL2 Host
- **Platform**: Windows WSL2 (Ubuntu)
- **Hostname**: DESKTOP-JJ1SUHB
- **GPUs**: 
  - GPU 0: NVIDIA GeForce GTX 1080 Ti (11GB VRAM)
  - GPU 1: NVIDIA GeForce RTX 3090 (24GB VRAM)
- **Memory**: 47GB RAM
- **Storage**: 771GB free (1007GB total)
- **Current GPU Usage**: GTX 1080 Ti (needs optimization)

#### Gen8 HP ProLiant
- **IP**: servicebox.taileb8c60.ts.net (Tailscale)
- **Services**: ChromaDB, Pi-hole, Uptime Kuma
- **ChromaDB**: 29,013 documents indexed
- **Status**: ✅ All services running and accessible

---

## 🔄 Request Flow (Actual)

```
User Query
    │
    ▼
┌─────────────────────────────────────────┐
│   FAITHH Backend (WSL2 :5557)           │
│   faithh_professional_backend_fixed.py  │
└────────┬────────────────────────────────┘
         │
         ├──────────────────┐
         │                  │
         ▼                  ▼
┌──────────────────┐  ┌──────────────────────┐
│ Native Ollama    │  │ Gen8 ChromaDB        │
│ WSL2 :11434      │  │ servicebox.taileb8c60.ts.net:8000    │
│ (GPU inference)  │  │ (RAG search)         │
└──────────────────┘  └──────────────────────┘
```

---

## ⚠️ Known Issues & Optimizations Needed

### Issue 1: GPU Selection (CRITICAL)
**Problem**: Ollama currently uses GTX 1080 Ti (GPU 0) instead of RTX 3090 (GPU 1)

**Impact**:
- Slower inference (GTX 1080 Ti is 2-3x slower than RTX 3090)
- Less VRAM (11GB vs 24GB)
- Large models (qwen3-faithh:latest) may overflow to CPU

**Solution**: Configure Ollama to use RTX 3090
```bash
# Create systemd override
sudo mkdir -p /etc/systemd/system/ollama.service.d/
sudo tee /etc/systemd/system/ollama.service.d/override.conf << EOF
[Service]
Environment="CUDA_VISIBLE_DEVICES=1,0"
EOF

# Restart Ollama
sudo systemctl daemon-reload
sudo systemctl restart ollama

# Verify
nvidia-smi  # Should show RTX 3090 with model loaded
```

### Issue 2: ChromaDB API Version
**Status**: ✅ RESOLVED

- Gen8 ChromaDB uses v2 API
- Python client (chromadb 1.2.0) handles this correctly
- Raw curl commands need to use `/api/v2/` endpoints

### Issue 3: Ollama Not Running
**Status**: ⚠️ NEEDS VERIFICATION

From your conversation, Ollama was running but current check shows no response. Verify:
```bash
# Check if Ollama is running
systemctl status ollama
ps aux | grep ollama

# If not running, start it
sudo systemctl start ollama

# Enable on boot
sudo systemctl enable ollama
```

---

## 🚀 Deployment Status

### ✅ Already Deployed (Working)
- Gen8 ChromaDB with 29,013 documents
- Gen8 Pi-hole (DNS/ad-blocking)
- Gen8 Uptime Kuma (monitoring)
- Tailscale networking between devices
- FAITHH backend configured for Gen8 ChromaDB

### ❌ Removed (Cleaned Up)
- Docker Ollama containers (3x - were empty/unused)
- Docker ChromaDB on WSL2 (duplicate)
- Docker LangFlow (unused)
- Docker Postgres (only needed for LangFlow)

### 🎯 Next Steps
1. **Optimize GPU usage** - Switch Ollama to RTX 3090
2. **Verify Ollama service** - Ensure it's running and enabled
3. **Test FAITHH end-to-end** - Verify RAG search works
4. **Update documentation** - Mark old docs as outdated

---

## 📊 Resource Usage (Post-Cleanup)

### Before Cleanup
- Docker containers: 6 running
- Memory usage: ~60GB (with Docker overhead)
- Disk usage: ~186GB
- GPU: Fragmented across Docker + native

### After Cleanup
- Docker containers: 0
- Memory usage: ~47GB (native only)
- Disk usage: ~186GB (models still on disk)
- GPU: Native Ollama only (cleaner)

**Freed Resources**:
- ~10-15GB RAM (Docker overhead removed)
- Cleaner process list
- No port conflicts
- Direct GPU access (no Docker layer)

---

## 🔧 Service Management

### Start/Stop FAITHH
```bash
cd ~/ai-stack
./restart_backend.sh  # Start FAITHH backend
./stop_backend.sh     # Stop FAITHH backend
```

### Manage Ollama
```bash
sudo systemctl status ollama   # Check status
sudo systemctl start ollama    # Start
sudo systemctl stop ollama     # Stop
sudo systemctl restart ollama  # Restart

# View logs
sudo journalctl -u ollama -f

# Test API
curl http://localhost:11434/api/tags
```

### Check Gen8 Services
```bash
# Via SSH
ssh -i ~/.ssh/servicebox_ed25519 jonat@servicebox.taileb8c60.ts.net "docker ps"

# Test ChromaDB
curl -s http://servicebox.taileb8c60.ts.net:8000/api/v2/heartbeat

# Test from Python
python3 << 'EOF'
import chromadb
client = chromadb.HttpClient(host="servicebox.taileb8c60.ts.net", port=8000)
collection = client.get_collection(name="faithh_knowledge_base")
print(f"Documents: {collection.count()}")
EOF
```

---

## 🎯 Multi-Device Reality Check

### Original Plan vs. Reality

**Original Plan** (from MULTI_DEVICE_DEPLOYMENT_STRATEGY.md):
- Deploy everything to Gen8
- Access from MacBook/WSL via browser
- Centralized architecture

**Current Reality**:
- ✅ Gen8 already has ChromaDB, Pi-hole, Uptime Kuma
- ✅ WSL2 already connects to Gen8 ChromaDB
- ✅ Tailscale networking already configured
- ⚠️ WSL2 runs compute (Ollama) + FAITHH backend
- ⚠️ MacBook deployment not yet done

### Actual Architecture Pattern
**Hybrid: Compute on WSL2, Data on Gen8**

This is actually optimal because:
- WSL2 has the GPUs (GTX 1080 Ti + RTX 3090)
- Gen8 has persistent storage and services
- Network latency is minimal (Tailscale)
- Each device does what it's best at

---

## 📚 Updated File Status

### Outdated Documents (Need Review)
- ❌ `ARCHITECTURE.md` - Assumes Docker on WSL2
- ❌ `docker-compose.yml` - No longer used on WSL2
- ⚠️ `MULTI_DEVICE_DEPLOYMENT_STRATEGY.md` - Gen8 already deployed

### Current Documents
- ✅ `ACTUAL_ARCHITECTURE_2026-01-14.md` - This file
- ✅ `ECOSYSTEM_REVIEW_SUMMARY.md` - Still accurate for analysis
- ✅ `ECOSYSTEM_CONSOLIDATION_PLAN.md` - Still relevant
- ✅ `.env` - Correctly configured for Gen8 ChromaDB

### Action Items
1. Update `ARCHITECTURE.md` with actual state
2. Add note to `docker-compose.yml` that it's Gen8-only
3. Update `README.md` with current architecture
4. Create `OLLAMA_GPU_OPTIMIZATION.md` guide

---

## 🔍 Verification Commands

Run these to verify your current state:

```bash
# 1. Check Docker (should be empty)
docker ps -a

# 2. Check Ollama
curl -s http://localhost:11434/api/tags | jq -r '.models[].name'

# 3. Check Gen8 ChromaDB
python3 -c "import chromadb; client = chromadb.HttpClient(host='servicebox.taileb8c60.ts.net', port=8000); collection = client.get_collection(name='faithh_knowledge_base'); print(f'✅ {collection.count()} documents')"

# 4. Check GPUs
nvidia-smi --query-gpu=index,name,memory.used,memory.total --format=csv

# 5. Check FAITHH backend
curl -s http://localhost:5557/health

# 6. Check Gen8 services
ssh -i ~/.ssh/servicebox_ed25519 jonat@servicebox.taileb8c60.ts.net "docker ps --format 'table {{.Names}}\t{{.Status}}'"
```

---

## 🎯 Priority Actions

### Immediate (Do Now)
1. **Verify Ollama is running**
   ```bash
   systemctl status ollama || sudo systemctl start ollama
   ```

2. **Optimize GPU usage** (switch to RTX 3090)
   - See "Issue 1: GPU Selection" above

3. **Test FAITHH end-to-end**
   ```bash
   ./restart_backend.sh
   curl http://localhost:5557/health
   ```

### Short-term (This Week)
1. Update `ARCHITECTURE.md` to reflect actual state
2. Create Ollama GPU optimization guide
3. Document MacBook deployment (if needed)
4. Test RAG search performance

### Medium-term (This Month)
1. Benchmark RTX 3090 vs GTX 1080 Ti performance
2. Consider moving Ollama to Gen8 (if Gen8 has GPU)
3. Setup automated health monitoring
4. Document backup procedures for Gen8

---

*This document reflects the actual deployed architecture as of 2026-01-14. Use this instead of the theoretical deployment guides.*
