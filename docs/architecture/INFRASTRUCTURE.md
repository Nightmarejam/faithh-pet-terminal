# Infrastructure & Hardware

**Last Updated:** 2026-04-12 (aligned with `fingerprint_state.json` / `AGENTS.md`)

---

## Hardware

### Primary Workstation (Windows/WSL2)
| Property | Value |
|----------|-------|
| OS | Windows + WSL2 Ubuntu 24.04 |
| CPU | AMD Ryzen 9 3900X (24 threads) |
| RAM | 47GB |
| GPU 0 | NVIDIA GTX 1080 Ti (11GB VRAM) |
| GPU 1 | NVIDIA RTX 3090 (24GB VRAM) |
| Primary Use | Development, AI inference, audio production, image generation |

### Gen8 MicroServer (servicebox)
| Property | Value |
|----------|-------|
| Model | HP ProLiant MicroServer Gen8 |
| CPU | Intel Xeon E3-1265L V2 (4C/8T) |
| RAM | 15GB DDR3 ECC |
| Storage | ~840GB free |
| OS | Ubuntu 22.04 LTS |
| LAN IP | servicebox.taileb8c60.ts.net (canonical in repo docs for Chroma / SSH / metrics) |

---

## GPU Assignment

| GPU | Device | Used By | Notes |
|-----|--------|---------|-------|
| GTX 1080 Ti | GPU 0 (PCI_BUS_ID) | Ollama (Docker containers) | Embedding + inference |
| RTX 3090 | GPU 1 (PCI_BUS_ID) | Ollama (systemd), ComfyUI, LoRA training | 24GB VRAM |

**Important:** ComfyUI uses `CUDA_VISIBLE_DEVICES=0` (default ordering). ML scripts and LoRA training use `CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=1`. Ollama systemd override: `/etc/systemd/system/ollama.service.d/override.conf` sets `CUDA_VISIBLE_DEVICES=1`.

---

## Services (WSL2 / Local)

| Service | Port | Start Command | Notes |
|---------|------|---------------|-------|
| FAITHH Backend | 5557 | `./restart_backend.sh` | Flask, serves UI + API |
| Ollama | 11434 | `systemctl start ollama` | systemd managed, RTX 3090 |
| ComfyUI | 8188 | `scripts/start_comfyui.sh` | Image generation, RTX 3090 |

## Services (Docker — WSL2)

| Container | Port | Purpose |
|-----------|------|---------|
| chromadb | 8000 | Vector database (RAG) |
| ollama-embed | 11435 | Embedding model server |
| ollama-qwen | 11436 | Qwen model family |
| langflow | 7860 | Visual AI workflow builder |
| postgres | 5432 | Database for LangFlow |

**Manage:** `docker-compose up -d` / `docker-compose down`

## Services (Gen8 Server)

| Service | Port | Purpose |
|---------|------|---------|
| ChromaDB | 8000 | Primary RAG database (`faithh_knowledge_base_v2` — ~63.7k chunks, BGE 768-dim; see live `GET /health`) |
| Grafana | 3000 | Monitoring UI |
| Prometheus | 9090 | Metrics collection |
| Pi-hole | 80/53 | DNS filtering |
| Gitea | 3002 (SSH: 2222) | Git hosting |
| Vaultwarden | 8080 | Password manager |
| Uptime Kuma | 3001 | Service monitoring |
| Docker Registry | 5000/5001 | Private images + UI |

---

## Ollama Models (localhost:11434)

**Default for `/api/chat` (April 2026):** `qwen25-faithh-v3:latest` via `config.yaml` `ai.default_model` (see `AGENTS.md`).

Installed set varies by host; examples recently present: `qwen25-grounded:latest`, `qwen25-grounded-32k:latest`, `deepseek-r1:32b`, `llama3.3:70b`, etc. Use `ollama list` on the workstation and `grep default_model config.yaml` for the pinned default.

---

## Network Access

### SSH
```bash
# Gen8 (LAN)
ssh -i ~/.ssh/servicebox_ed25519 jonat@servicebox.taileb8c60.ts.net
```

### Service URLs
```
FAITHH UI:    http://localhost:5557
FAITHH API:   http://localhost:5557/api/chat
ChromaDB:     http://servicebox.taileb8c60.ts.net:8000
Ollama:       http://localhost:11434
ComfyUI:      http://localhost:8188
Grafana:      http://servicebox.taileb8c60.ts.net:3000
```

---

## Startup After Reboot

```bash
# 1. Docker containers (usually auto-start)
docker-compose up -d

# 2. Ollama (usually auto-starts via systemd)
systemctl start ollama

# 3. FAITHH backend
cd ~/ai-stack && ./restart_backend.sh

# 4. ComfyUI (optional, when needed for image generation)
scripts/start_comfyui.sh
```

---

*Consolidated from ECOSYSTEM_MAP.md, DOCKER_SERVICES.md, GEN8_*.md, hardware_inventory.md — refreshed 2026-04-12.*
