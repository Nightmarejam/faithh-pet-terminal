# WSL/FAITHH Dependencies Documentation
**Date:** 2026-02-19  
**Environment:** Ubuntu 22.04 on WSL2  
**Purpose:** Document all dependencies for the FAITHH AI stack running in WSL2

---

## Philosophy: Minimal, Intentional Stack

Every package and service in WSL2 exists to support FAITHH. If it's not listed here, it should be reviewed for removal.

---

## Core System Dependencies

### Base System (Ubuntu 22.04)
| Component | Version/Source | Purpose |
|-----------|----------------|---------|
| Ubuntu | 22.04 LTS | Base OS for WSL2 |
| Linux Kernel | 5.15+ | WSL2 kernel with GPU support |
| CUDA | 12.2 | GPU compute for RTX 3090 (GPU 1) |
| Docker | 24.0+ | Container services (ChromaDB, Langflow, Postgres) |
| Git | 2.51+ | Version control |

### Python Environment
| Component | Version | Purpose |
|-----------|---------|---------|
| Python | 3.11.5 (system) | Backend runtime |
| pip | latest | Package management |
| venv | built-in | Isolated environments |
| CUDA Toolkit | 12.2 | PyTorch GPU support |

---

## FAITHH Stack Dependencies

### Backend Services
| Service | Version | Location | Purpose |
|---------|---------|----------|---------|
| Flask | 3.0.0+ | venv | Web framework |
| ChromaDB | 0.4.18 | Docker | Vector database (Gen8) |
| Ollama | 0.5.4 | systemd | Local LLM serving |
| Langflow | 1.0.0+ | Docker | Visual AI workflow builder |
| Postgres | 15+ | Docker | Structured data storage |

### Python Packages (venv: ai-stack)
| Package | Version | Purpose |
|---------|---------|---------|
| torch | 2.5.0+ | ML framework (GPU) |
| transformers | 4.36.0+ | Hugging Face models |
| chromadb | 0.4.18+ | Vector DB client |
| flask | 3.0.0+ | Web framework |
| requests | 2.31.0+ | HTTP client |
| psutil | 5.9.0+ | System monitoring |
| numpy | 1.24.0+ | Numerical computing |
| sentence-transformers | 2.2.0+ | Text embeddings |
| llama-cpp-python | 0.2.0+ | Local model inference |
| unsloth | 2024.1+ | LLM fine-tuning |

### ML/MLX Dependencies (separate venv)
| Component | Location | Purpose |
|-----------|-----------|---------|
| ML Chip Synthesis | ml/venv | Topic clustering, chip generation |
| QLoRA Fine-tuning | ml/grounding_finetune/venv | Model fine-tuning |
| Unsloth | ml/grounding_finetune/venv | Efficient fine-tuning |

---

## Models in Ollama

### Active Models (WSL-side)
| Model | Size | Purpose | Notes |
|-------|------|---------|-------|
| qwen25-grounded:latest | 8.4GB | FAITHH default (anti-hallucination) | Fine-tuned, grounded |
| llama31-faithh:latest | 4.8GB | Daily chat | FAITHH persona |
| qwen3-faithh:latest | 17GB | Deep reasoning | 30.5B parameters |
| qwen2.5-coder:14b | 8.2GB | Coding queries | Specialized |
| deepseek-r1:32b | 20GB | Complex reasoning | Fast reasoning |
| llama3.1:8b | 4.7GB | Base model | General purpose |
| qwen2.5:7b | 3.8GB | Fast queries | Lightweight |
| llama3.3:70b | 42GB | Complex reasoning | Slow, high quality |

### GPU Configuration
- **GPU 0**: GTX 1080 Ti (11GB) - Reserved for gaming
- **GPU 1**: RTX 3090 (24GB) - Primary AI GPU
- **CUDA_VISIBLE_DEVICES**: Set to "1" for all AI processes
- **Ollama GPU Override**: Configured to use RTX 3090 only

---

## Services Configuration

### Systemd Services
| Service | File | Status | Purpose |
|---------|------|--------|---------|
| ollama | /etc/systemd/system/ollama.service | Enabled | LLM serving |
| ollama override | /etc/systemd/system/ollama.service.d/override.conf | Active | GPU selection |

### Docker Compose
| Service | Image | Port | Purpose |
|---------|-------|------|---------|
| ChromaDB | chromadb/chroma:latest | 8000 | Vector DB |
| Langflow | langflow/langflow:latest | 8080 | Visual workflows |
| Postgres | postgres:15 | 5432 | Structured data |

---

## Key Configuration Files

### FAITHH Backend
| File | Purpose |
|------|---------|
| faithh_professional_backend_fixed.py | Main backend (port 5557) |
| .env | Environment variables |
| config.yaml | Runtime configuration |
| faithh_memory.json | Long-term memory |
| decisions_log.json | Decision tracking |
| project_states.json | Project context |
| scaffolding_state.json | Milestone tracking |

### ML Systems
| File/Dir | Purpose |
|----------|---------|
| ml/chip_synthesis.py | Topic clustering |
| ml/output/chips.json | 15 macro-chips |
| ml/grounding_finetune/ | QLoRA training pipeline |
| pulse_patterns.json | PULSE reflection data |

---

## Network Configuration

### Port Usage
| Port | Service | Direction |
|------|---------|-----------|
| 5557 | FAITHH Backend | Outbound (Windows) |
| 11434 | Ollama | Internal WSL |
| 8000 | ChromaDB | Internal (Gen8) |
| 8080 | Langflow | Internal WSL |
| 5432 | Postgres | Internal WSL |

### Tailscale
- **Gen8 IP**: 192.158.1.243
- **Purpose**: Remote access to ChromaDB
- **Status**: Active, stable connection

---

## Data Storage

### Vector Database
- **Location**: Gen8 MicroServer via Tailscale
- **Chunks**: 37,000+ documents indexed
- **Embedding Model**: all-MiniLM-L6-v2 (384-dim)
- **Active Files**: 35 docs (excludes archive/)

### Model Files
- **Location**: ~/.ollama/models
- **Total Size**: ~150GB
- **Format**: GGUF quantized (q4_k_m, q8_0)

### State Files
- **Location**: Project root
- **Backup**: Handoffs to docs/archive/
- **Sync**: Manual via git

---

## Performance Optimizations

### GPU Memory Management
- **RTX 3090**: 24GB VRAM for AI
- **Offloading**: Large models use CPU RAM when needed
- **Batch Size**: 1 for inference, 1-8 for training

### Model Routing
- **Simple queries**: qwen25-grounded:latest (14B)
- **Coding**: qwen2.5-coder:14b
- **Reasoning**: deepseek-r1:32b (or llama3.3:70b)
- **Gaming mode**: llama3.1:8b (lightweight)

---

## Maintenance Commands

### Service Management
```bash
# Restart backend
./restart_backend.sh

# Check Ollama
systemctl status ollama
ollama list

# Check ChromaDB
curl http://192.158.1.243:8000/api/v2/heartbeat

# Docker services
cd /home/jonat/ai-stack && docker-compose ps
```

### Model Management
```bash
# Pull new model
ollama pull modelname

# Check GPU usage
nvidia-smi

# Monitor resources
htop
```

---

## Future Improvements

### Performance
- [ ] Multi-GPU support (llama.cpp)
- [ ] Model sharding across RAM+VRAM
- [ ] Faster inference engines

### Architecture
- [ ] Microservices for backend components
- [ ] Redis for caching
- [ ] Automated model updates

### Monitoring
- [ ] Prometheus metrics
- [ ] Grafana dashboards
- [ ] Alert system for GPU memory

---

## Troubleshooting

### Common Issues
1. **CUDA out of memory**: Reduce batch size or use smaller model
2. **Ollama not responding**: Check systemd service status
3. **ChromaDB connection**: Verify Tailscale connection to Gen8
4. **GPU not detected**: Check CUDA_VISIBLE_DEVICES=1

### Log Locations
- Backend: ~/ai-stack/backend.log
- Ollama: journalctl -u ollama
- Docker: docker-compose logs

---

**Rule**: Every dependency serves FAITHH's purpose. Document before installing, review quarterly.
