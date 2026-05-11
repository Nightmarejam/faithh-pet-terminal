# Development Environment Parity File
**Last Updated**: 2025-12-07  
**Purpose**: Document the development infrastructure for FAITHH and related projects

---

## Hardware Ecosystem (6 Devices)

### 1. Windows Desktop (DESKTOP-JJ1SUHB)
```yaml
Role: Primary workstation, FAITHH Full, AI inference
Tailscale IP: 100.115.225.100
Local IP: 192.158.1.232

CPU: AMD Ryzen 9 3900X (12C/24T, 3.8GHz base, 4.65GHz boost)
RAM: 64GB DDR4-3200 (G.Skill TridentZ Neo 2x32GB)
GPU_Primary: NVIDIA RTX 3090 24GB (AI workload, PCIe x16)
GPU_Secondary: NVIDIA GTX 1080 Ti 11GB (display output, PCIe x1)
Motherboard: ASRock X570 Steel Legend
PSU: FSP PT-1000FM (1000W, 80+ Platinum)
Storage:
  - C: Samsung 970 EVO NVMe 1TB (355GB free)
  - E: 1.81TB SSD (925GB free)
  - D: WD My Passport 931GB external

Services Running:
  - FAITHH Backend (port 5557)
  - ChromaDB (port 8000, 93,629 docs)
  - Ollama (port 11434, llama3.1-8b, qwen2.5-coder:7b, qwen2.5-7b)
  - Gemini API (configured, flash-exp)
```

### 2. MacBook Pro M1 Pro (14", 2021)
```yaml
Role: Mobile mastering, FAITHH Lite, Constella development
Tailscale IP: 100.122.56.106
Local IP: 192.158.1.132

Chip: Apple M1 Pro (8-core CPU, 14-core GPU)
RAM: 16GB unified
Storage: 512GB SSD

Services Running:
  - FAITHH Lite (port 5557, Ollama backend)
  - Ollama (port 11434, llama3.1:8b)
  - Context files: life_map, constella, audio

Key Locations:
  - ~/faithh/ (FAITHH Lite installation)
  - ~/Applications/FAITHH Lite.app (app shortcut)
  - ~/Projects/constella-framework/
  - ~/Audio-Scripts/
```

### 3. Phone (iOS/Android)
```yaml
Role: Mobile FAITHH access via Tailscale
Status: Connected to Tailscale network
Access: Can query Windows FAITHH API at 100.115.225.100:5557
```

### 4. DS220J NAS (ISaidGoodDay)
```yaml
Role: File storage (NOT compute)
Tailscale IP: 100.120.68.7
Local IP: 192.158.1.65

CPU: Realtek RTD1296 quad-core (ARM, weak)
RAM: 512MB (too limited for Docker/compute)
Storage: 1x Seagate IronWolf Pro 16TB (ST16000NE000)
  - Total: 13TB
  - Used: 3.0TB (23%)
  - Free: 10TB

Organized Structure:
  - /volume1/Personal/ (1.4TB - videos, photos, docs)
  - /volume1/Audio/ (152GB - Tom Cat Productions, stems)
  - /volume1/Backups/ (1012GB - Windows host, legacy)
  - /volume1/AI/ (177GB - Learning Portal, datasets)
  - /volume1/Archive/ (~30GB - ISOs, old software)
  - /volume1/Inbox_Sorted/ (66GB - needs manual sorting)

Packages Installed (Minimal):
  - Tailscale
  - File Station
  - SMB Service
  - Storage Manager
```

### 5. HP ProLiant MicroServer Gen8 (OFFLINE)
```yaml
Role: Future always-on server (ChromaDB, Plex, Docker)
Status: OFFLINE - awaiting upgrade

Current Specs:
  CPU: Xeon E3-1220L v2 (2C/4T, 2.3GHz, 17W TDP)
  RAM: 4GB DDR3 ECC (insufficient)
  Storage: 4x 3.5" SATA bays available

Upgrade Plan ($110-130):
  - CPU: Xeon E3-1265L v2 (4C/8T, 2.5GHz, 45W) - ~$50-60 eBay
  - RAM: 2x 8GB DDR3 ECC - ~$60-80

When Activated:
  - ChromaDB server (offload from Windows)
  - Plex server (media library fallback)
  - Pi-hole (network ad-blocking)
  - Always-on FAITHH API endpoint
  - ~40-50W power consumption
```

### 6. Partner's Mac Mini M2 (South Dakota)
```yaml
Role: Remote audio collaboration
Status: Awaiting Tailscale installation
Setup Guide: tailscale_partner_setup.md sent

Specs: M2 Mac Mini
DAW: Luna
Collaboration: JackTrip/SonoBus for audio over network
```

---

## Network Topology

```
┌─────────────────────────────────────────────────────────┐
│                 TAILSCALE NETWORK                        │
│            (100.x.x.x private addresses)                 │
│                                                          │
│  ┌──────────────┐         ┌──────────────┐             │
│  │   Windows    │◄───────►│   MacBook    │             │
│  │   Desktop    │         │   Pro M1     │             │
│  │ 100.115.225  │         │ 100.122.56   │             │
│  │              │         │              │             │
│  │ FAITHH Full  │         │ FAITHH Lite  │             │
│  │ 93K docs     │         │ 3 context    │             │
│  └──────────────┘         └──────────────┘             │
│         ▲                        ▲                      │
│         │                        │                      │
│         ▼                        ▼                      │
│  ┌──────────────┐         ┌──────────────┐             │
│  │   DS220J     │         │    Phone     │             │
│  │    NAS       │         │              │             │
│  │ 100.120.68.7 │         │ Tailscale    │             │
│  │              │         │ connected    │             │
│  │ 13TB storage │         │              │             │
│  └──────────────┘         └──────────────┘             │
│                                                          │
│  ┌──────────────┐         ┌──────────────┐             │
│  │  ProLiant    │         │ Partner Mac  │             │
│  │  Gen8        │         │ Mini M2      │             │
│  │  (offline)   │         │ (pending)    │             │
│  └──────────────┘         └──────────────┘             │
└─────────────────────────────────────────────────────────┘

Local Network: 192.158.1.x (intentional obfuscation)
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
  - ~/ai-stack/docs (technical documentation)
```

---

## Docker Containers

**Managed via**: `~/ai-stack/docker-compose.yml`  
**Network**: ai-stack (shared Docker network)

| Container | Port | Purpose | GPU | RAM Limit |
|-----------|------|---------|-----|-----------|
| chromadb | 8000 | Vector database | - | 2GB |
| ollama | 11434 | Primary LLM | RTX 3090 | 28GB |
| ollama-embed | 11435 | Embeddings | GTX 1080 Ti | 12GB |
| ollama-qwen | 11436 | Qwen models | RTX 3090 | 32GB |
| langflow | 7860 | Visual workflows | - | 4GB |
| postgres | 5432 | LangFlow DB | - | 2GB |

---

## Services & Ports

| Service | Port | Status Check | Host |
|---------|------|--------------|------|
| FAITHH Backend | 5557 | `curl http://localhost:5557/api/status` | Windows |
| FAITHH Lite | 5557 | `curl http://localhost:5557/api/status` | MacBook |
| ChromaDB | 8000 | `curl http://localhost:8000/api/v1/heartbeat` | Windows |
| Ollama | 11434 | `curl http://localhost:11434/api/tags` | Both |

---

## Startup Sequence (Windows)
```bash
# 1. Start Docker Desktop (if not running)

# 2. Start containers
cd ~/ai-stack
docker-compose up -d

# 3. Activate Python environment
source venv/bin/activate

# 4. Start FAITHH backend
./restart_backend.sh

# 5. Verify services
curl http://localhost:5557/api/status
```

## Startup (MacBook)
```bash
# Double-click FAITHH Lite.app on Desktop
# OR
cd ~/faithh && ./start.sh
```

---

## Common Issues

### Port 5557 Already in Use
```bash
lsof -ti:5557 | xargs kill -9
```

### ChromaDB Connection Failed
```bash
docker ps | grep chroma
docker start chromadb
docker logs chromadb
```

### NAS Permission Issues
```bash
ssh Nightmarejam@100.120.68.7
sudo chown -R Nightmarejam:users /volume1/[folder]
```

---

**Status**: Complete - All devices documented  
**Last Verified**: 2025-12-07
