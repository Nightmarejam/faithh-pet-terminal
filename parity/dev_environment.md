# Development Environment Parity File
**Last Updated**: 2025-11-25  
**Purpose**: Document the development infrastructure for FAITHH and related projects

---

## Hardware

### Windows Desktop
```yaml
CPU: AMD Ryzen 9 3900X 12-Core Processor, 3801 Mhz, 12 Core(s), 24 Logical Processor(s)
RAM: 64GB (G.Skill TridentZ Neo 2x32GB DDR4-3200 C16)
GPU_Primary: RTX 3090 (CUDA workloads, ComfyUI, AI inference)
GPU_Secondary: RTX 1080 Ti (display output, game capture via Elgato)
Storage: [Fill in - check with `df -h` or Windows Disk Management]
```

### MacBook Pro M1
```yaml
Purpose: Mobile mastering, Constella development
Storage: 500GB
Key Software: WaveLab, Luna DAW (when mobile)
```

---

## WSL2 Environment
```yaml
Distribution: Ubuntu 24.04.3 LTS (GNU/Linux 6.6.87.2-microsoft-standard-WSL2 x86_64)
Location: \\wsl.localhost\Ubuntu\home\jonat

Python:
  Version: 3.11
  Venv: ~/ai-stack/venv
  Activation: source ~/ai-stack/venv/bin/activate

Key Directories:
  - ~/ai-stack (FAITHH project root)
  - ~/ai-stack/uploads (file uploads)
  - ~/ai-stack/parity (state documentation)
```

---

## Docker Containers

**Managed via**: `~/ai-stack/docker-compose.yml`  
**Network**: ai-stack (shared Docker network)

```yaml
Container 1 - ollama:
  Image: ollama/ollama:latest
  Purpose: Primary LLM inference server
  GPU: Device 1 (RTX 3090 or RTX 1080 Ti)
  RAM Limit: 28GB
  Port: 11434
  Models: llama3.1-8b (primary), others available
  Keep Alive: 24h
  Volume: ollama_models

Container 2 - ollama-embed:
  Image: ollama/ollama:latest
  Purpose: Embedding model server (text → vectors for RAG)
  GPU: Device 0
  RAM Limit: 12GB
  Port: 11435
  Keep Alive: 24h
  Volume: ollama_embed_models

Container 3 - ollama-qwen:
  Image: ollama/ollama:latest
  Purpose: Qwen model family server
  GPU: Device 1
  RAM Limit: 32GB
  Port: 11436
  Keep Alive: 1h
  Volume: ollama_qwen_models

Container 4 - chromadb:
  Image: chromadb/chroma:latest
  Purpose: Vector database (knowledge base)
  Port: 8000
  RAM Limit: 2GB
  Persistent: YES
  Volume: chromadb_data
  Current Documents: 91,604

Container 5 - langflow:
  Image: langflowai/langflow:latest
  Purpose: Visual AI workflow builder
  Port: 7860
  RAM Limit: 4GB
  Depends On: ollama, postgres
  Database: PostgreSQL
  Volume: langflow_data

Container 6 - postgres:
  Image: postgres:15-alpine
  Purpose: Database for LangFlow
  RAM Limit: 2GB
  Internal Port: 5432
  Credentials: langflow/langflow (dev only)
  Volume: postgres_data
```

**Container Management**:
```bash
# View all containers
docker ps -a

# Start all services
cd ~/ai-stack && docker-compose up -d

# Stop all services
docker-compose down

# Restart specific container
docker restart chromadb

# View logs
docker logs -f chromadb

# Check resource usage
docker stats
```

---

## Services & Ports

| Service | Port | Status Check | Container |
|---------|------|--------------|-----------|
| FAITHH Backend | 5557 | `curl http://localhost:5557/health` | Native Python |
| ChromaDB | 8000 | `curl http://localhost:8000/api/v1/heartbeat` | chromadb |
| Ollama (Primary) | 11434 | `curl http://localhost:11434/api/tags` | ollama |
| Ollama (Embed) | 11435 | `curl http://localhost:11435/api/tags` | ollama-embed |
| Ollama (Qwen) | 11436 | `curl http://localhost:11436/api/tags` | ollama-qwen |
| LangFlow | 7860 | Open http://localhost:7860 | langflow |
| PostgreSQL | 5432 | Internal only | postgres |

---

## Startup Sequence
```bash
# 1. Start Docker (if not running - check Docker Desktop on Windows)

# 2. Start all containers (or just ChromaDB if others aren't needed)
cd ~/ai-stack
docker-compose up -d          # Start all
# OR
docker start chromadb         # Start just ChromaDB

# 3. Activate Python environment
source venv/bin/activate

# 4. Start FAITHH backend
python faithh_professional_backend_fixed.py > faithh_backend.log 2>&1 &

# 5. Verify services
curl http://localhost:5557/api/status
```

---

## Common Issues

### Port 5557 Already in Use
```bash
lsof -ti:5557 | xargs kill -9
```

### ChromaDB Connection Failed
```bash
docker ps | grep chroma  # Check if running
docker start chromadb    # Start if stopped
docker logs chromadb     # Check for errors
```

### Ollama Container Not Starting
```bash
# Check GPU availability
nvidia-smi

# Check Docker GPU access
docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi

# Restart Ollama
docker restart ollama
```

---

**Status**: Complete - All containers documented  
**Last Verified**: 2025-11-25
