# FAITHH Multi-Device Deployment Strategy

**Generated**: 2026-01-14  
**Target Devices**: MacBook Pro (dock), Windows WSL, Gen8 HP ProLiant, Synology NAS

---

## 📊 Current System Analysis

### System Requirements (from docker-compose.yml)
- **GPU**: NVIDIA GPU required (2 GPUs configured)
- **Memory**: 80GB minimum, 88GB recommended
- **Storage**: ~58GB current usage, recommend 100GB+ for growth
- **Ports**: 5557 (backend), 8000 (ChromaDB), 11434-11436 (Ollama), 7860 (Langflow)
- **Services**: Ollama (3 instances), ChromaDB, Langflow, PostgreSQL

### Current Architecture
```
┌─────────────────────────────────────────────────┐
│ Windows WSL (Current Host)                      │
│ ├── FAITHH Backend (Flask) :5557                │
│ ├── Docker Services                             │
│ │   ├── Ollama (GPU 0,1) :11434-11436          │
│ │   ├── ChromaDB :8000                          │
│ │   ├── Langflow :7860                          │
│ │   └── PostgreSQL :5432                        │
│ └── UI (Static HTML served by backend)          │
└─────────────────────────────────────────────────┘
```

---

## 🎯 Recommended Multi-Device Architecture

### Option A: Centralized Server (Recommended)

```
┌──────────────────────────────────────────────────────────────┐
│                    Gen8 HP ProLiant                          │
│                    (Central Server)                          │
├──────────────────────────────────────────────────────────────┤
│ Docker Services                                              │
│ ├── Ollama (GPU) :11434-11436                               │
│ ├── ChromaDB :8000                                           │
│ ├── Langflow :7860                                           │
│ ├── PostgreSQL :5432                                         │
│ └── FAITHH Backend :5557                                     │
│                                                              │
│ Storage Mounts                                               │
│ ├── /mnt/nas/ai-stack/AI_Chat_Exports (NAS)                │
│ ├── /mnt/nas/ai-stack/backups (NAS)                        │
│ └── /mnt/nas/ai-stack/models (NAS)                         │
└──────────────────────────────────────────────────────────────┘
                            ▲
                            │ Tailscale/VPN
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────▼────────┐  ┌──────▼──────┐  ┌─────────▼────────┐
│ MacBook Pro    │  │ Windows WSL │  │ Synology NAS     │
│ (Browser UI)   │  │ (Browser UI)│  │ (Storage Only)   │
│ http://gen8:   │  │ http://gen8:│  │ - AI_Chat_Exports│
│   5557         │  │   5557      │  │ - backups/       │
└────────────────┘  └─────────────┘  │ - models/        │
                                     └──────────────────┘
```

**Pros**:
- Single source of truth
- GPU resources on Gen8
- Centralized ChromaDB (shared knowledge base)
- Easy to maintain and update
- NAS handles large file storage

**Cons**:
- Single point of failure
- Network dependency

---

### Option B: Distributed with Sync

```
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ MacBook Pro     │  │ Windows WSL     │  │ Gen8 ProLiant   │
│ - Local Backend │  │ - Local Backend │  │ - Master Backend│
│ - Local ChromaDB│  │ - Local ChromaDB│  │ - ChromaDB      │
│ - No GPU (CPU)  │  │ - GPU (if avail)│  │ - GPU (primary) │
└────────┬────────┘  └────────┬────────┘  └────────┬────────┘
         │                    │                    │
         └────────────────────┼────────────────────┘
                              │
                    ┌─────────▼─────────┐
                    │  Synology NAS     │
                    │  - Shared Storage │
                    │  - Sync Service   │
                    └───────────────────┘
```

**Pros**:
- Works offline
- Redundancy
- Local performance

**Cons**:
- Complex sync logic
- Potential conflicts
- Higher maintenance

---

## 🚀 Deployment Plan: Option A (Centralized)

### Phase 1: Gen8 Server Setup

#### 1.1 Hardware Verification
```bash
# Check GPU availability
nvidia-smi

# Check memory
free -h

# Check storage
df -h

# Check network
ip addr show
```

#### 1.2 Install Prerequisites
```bash
# Docker & Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# NVIDIA Container Toolkit (for GPU)
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker

# Python 3.12+
sudo apt update
sudo apt install python3.12 python3.12-venv python3-pip
```

#### 1.3 Setup Tailscale (Secure Network)
```bash
# Install Tailscale on Gen8
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up

# Install on MacBook
brew install tailscale
sudo tailscale up

# Install on Windows WSL
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
```

### Phase 2: NAS Configuration

#### 2.1 Create Shared Folders on Synology
- `/volume1/ai-stack/AI_Chat_Exports`
- `/volume1/ai-stack/backups`
- `/volume1/ai-stack/models`
- `/volume1/ai-stack/chroma_db` (optional, for backup)

#### 2.2 Mount NAS on Gen8
```bash
# Install NFS client
sudo apt install nfs-common

# Create mount points
sudo mkdir -p /mnt/nas/ai-stack

# Add to /etc/fstab
echo "nas.local:/volume1/ai-stack /mnt/nas/ai-stack nfs defaults 0 0" | \
  sudo tee -a /etc/fstab

# Mount
sudo mount -a
```

### Phase 3: Deploy FAITHH on Gen8

#### 3.1 Clone Repository
```bash
cd /home/jonat
git clone <your-repo-url> ai-stack
cd ai-stack
```

#### 3.2 Configure Environment
```bash
# Copy and edit .env
cp .env.example .env
nano .env

# Update config.yaml for network access
nano config.yaml
```

**Key config.yaml changes**:
```yaml
api:
  host: 0.0.0.0  # Listen on all interfaces
  port: 5557
  enable_cors: true
  allowed_origins:
    - "*"  # Or specific Tailscale IPs
```

#### 3.3 Update docker-compose.yml for NAS
```yaml
services:
  ollama:
    volumes:
      - ollama_models:/root/.ollama
      - /mnt/nas/ai-stack/models/active:/models:ro
      
  chromadb:
    volumes:
      - chromadb_data:/chroma/chroma
      # Optional: backup to NAS
      - /mnt/nas/ai-stack/chroma_db:/backup:rw
```

#### 3.4 Start Services
```bash
# Start Docker services
docker-compose up -d

# Install Python dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Start FAITHH backend
./restart_backend.sh
```

#### 3.5 Verify Deployment
```bash
# Check services
docker-compose ps

# Check backend
curl http://localhost:5557/health

# Check from another device (use Tailscale IP)
curl http://gen8-tailscale-ip:5557/health
```

### Phase 4: Client Access

#### 4.1 MacBook Pro Access
```bash
# Open browser
open http://gen8-tailscale-ip:5557

# Or create alias
echo "alias faithh='open http://gen8-tailscale-ip:5557'" >> ~/.zshrc
```

#### 4.2 Windows WSL Access
```bash
# Open browser (from Windows)
start http://gen8-tailscale-ip:5557

# Or from WSL
explorer.exe http://gen8-tailscale-ip:5557
```

#### 4.3 Create Desktop Shortcuts
**MacBook**: Create `.command` file
```bash
#!/bin/bash
open http://gen8-tailscale-ip:5557
```

**Windows**: Create `.bat` file
```batch
@echo off
start http://gen8-tailscale-ip:5557
```

---

## 🔧 Configuration Files for Multi-Device

### Updated docker-compose.yml
```yaml
version: '3.8'

services:
  ollama:
    image: ollama/ollama:latest
    container_name: ollama
    restart: unless-stopped
    network_mode: host  # For easier Tailscale access
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              device_ids: ['0']
              capabilities: [gpu]
    volumes:
      - ollama_models:/root/.ollama
      - /mnt/nas/ai-stack/models:/models:ro
    environment:
      - OLLAMA_HOST=0.0.0.0:11434
      - OLLAMA_ORIGINS=*

  chromadb:
    image: chromadb/chroma:latest
    container_name: chromadb
    restart: unless-stopped
    ports:
      - "0.0.0.0:8000:8000"
    volumes:
      - chromadb_data:/chroma/chroma
      - /mnt/nas/ai-stack/backups/chromadb:/backup:rw
    environment:
      - IS_PERSISTENT=TRUE
      - CHROMA_SERVER_HOST=0.0.0.0

volumes:
  ollama_models:
  chromadb_data:
```

### Updated config.yaml
```yaml
security:
  allowed_directories:
    - /home/jonat/ai-stack
    - /mnt/nas/ai-stack
    - /tmp/faithh

api:
  host: 0.0.0.0  # Listen on all interfaces
  port: 5557
  enable_cors: true
  allowed_origins:
    - "*"  # Or list specific Tailscale IPs

ai:
  ollama:
    base_url: http://localhost:11434  # Local on Gen8
```

---

## 📋 Device Specifications

### Gen8 HP ProLiant (Recommended Specs)
- **CPU**: Intel Xeon E3-1265L v2 or better
- **RAM**: 32GB minimum, 64GB+ recommended
- **Storage**: 500GB SSD for OS/Docker, NAS for data
- **GPU**: NVIDIA GPU with 8GB+ VRAM (optional but recommended)
- **Network**: Gigabit Ethernet
- **OS**: Ubuntu Server 22.04 LTS

### MacBook Pro
- **Role**: Client only (browser access)
- **Requirements**: Modern browser, Tailscale
- **Optional**: Local development copy for offline work

### Windows WSL
- **Role**: Client + optional development
- **Requirements**: WSL2, Docker Desktop (optional), Tailscale
- **Can run**: Local instance for development/testing

### Synology NAS
- **Role**: Centralized storage
- **Requirements**: 
  - NFS enabled
  - 100GB+ free space
  - Gigabit network connection
- **Stores**: AI_Chat_Exports, backups, models, logs

---

## 🔒 Security Considerations

### Network Security
1. **Use Tailscale** for encrypted mesh network
2. **Firewall Rules**: Only expose ports within Tailscale network
3. **No Public Exposure**: Keep services internal only

### Access Control
```yaml
# config.yaml
security:
  require_auth: true  # Future enhancement
  allowed_ips:
    - "100.x.x.x/32"  # Tailscale IPs only
```

### Backup Strategy
1. **Daily**: ChromaDB snapshot to NAS
2. **Weekly**: Full system backup to NAS
3. **Monthly**: Off-site backup (external drive)

```bash
# Add to crontab on Gen8
0 2 * * * /home/jonat/ai-stack/scripts/backup_chromadb.sh
0 3 * * 0 /home/jonat/ai-stack/scripts/full_backup.sh
```

---

## 🧪 Testing Multi-Device Setup

### Test Checklist
- [ ] Gen8 services start successfully
- [ ] ChromaDB accessible from Gen8
- [ ] Ollama responds to requests
- [ ] Backend serves UI on 0.0.0.0:5557
- [ ] MacBook can access via Tailscale IP
- [ ] Windows WSL can access via Tailscale IP
- [ ] NAS mounts correctly on Gen8
- [ ] File uploads save to NAS
- [ ] RAG search works across devices
- [ ] Backup scripts run successfully

### Test Script
```bash
#!/bin/bash
# test_multi_device.sh

echo "Testing FAITHH Multi-Device Setup"
echo "=================================="

# Test Gen8 services
echo "1. Testing Gen8 services..."
docker-compose ps

# Test backend
echo "2. Testing backend..."
curl -s http://localhost:5557/health | jq

# Test ChromaDB
echo "3. Testing ChromaDB..."
curl -s http://localhost:8000/api/v1/heartbeat

# Test Ollama
echo "4. Testing Ollama..."
curl -s http://localhost:11434/api/tags | jq

# Test NAS mount
echo "5. Testing NAS mount..."
ls -lh /mnt/nas/ai-stack/

echo "=================================="
echo "All tests complete!"
```

---

## 📈 Monitoring & Maintenance

### Health Monitoring
```bash
# Create monitoring script
cat > /home/jonat/ai-stack/scripts/health_monitor.sh << 'EOF'
#!/bin/bash
# Check all services and send alerts if down

services=("ollama" "chromadb" "langflow" "postgres")
for service in "${services[@]}"; do
    if ! docker ps | grep -q $service; then
        echo "ALERT: $service is down!"
        # Add notification logic here
    fi
done
EOF

# Add to crontab (every 5 minutes)
*/5 * * * * /home/jonat/ai-stack/scripts/health_monitor.sh
```

### Resource Monitoring
```bash
# GPU monitoring
watch -n 1 nvidia-smi

# Docker stats
docker stats

# Disk usage
df -h /mnt/nas/ai-stack
```

---

## 🎯 Migration Checklist

### Pre-Migration
- [ ] Backup current WSL setup
- [ ] Document current configuration
- [ ] Test Gen8 hardware
- [ ] Setup NAS shares
- [ ] Install Tailscale on all devices

### Migration
- [ ] Deploy to Gen8
- [ ] Migrate ChromaDB data
- [ ] Test from each device
- [ ] Update documentation
- [ ] Train on new workflow

### Post-Migration
- [ ] Monitor for 1 week
- [ ] Optimize performance
- [ ] Document issues/solutions
- [ ] Update backup procedures

---

## 📚 Additional Resources

### Useful Commands
```bash
# View logs
docker-compose logs -f ollama
docker-compose logs -f chromadb

# Restart services
docker-compose restart

# Update images
docker-compose pull
docker-compose up -d

# Backup ChromaDB
docker exec chromadb tar czf /backup/chroma_$(date +%Y%m%d).tar.gz /chroma/chroma
```

### Troubleshooting
- **Can't connect from MacBook**: Check Tailscale status, firewall rules
- **GPU not detected**: Verify nvidia-container-toolkit installation
- **NAS mount fails**: Check NFS service on Synology, network connectivity
- **ChromaDB slow**: Check disk I/O, consider SSD for ChromaDB volume

---

*This deployment strategy provides a scalable, secure foundation for FAITHH across multiple devices.*
