# Jonathan's Tech Ecosystem - Infrastructure Map

**Last Updated:** 2026-01-25
**Purpose:** Complete visibility into all devices, services, and network topology

---

## Network Topology

```
ISP Router (DHCP Server)
│
├── Network Switch
│   │
│   ├── Gen8 Server (servicebox)
│   │   IP: 192.158.1.243 (needs static)
│   │   Tailscale: 192.158.1.243
│   │
│   └── [Other wired devices]
│
└── WiFi
    └── [Wireless devices]

OWC Thunderbolt 3 Dock
├── Windows Desktop (DESKTOP-JJ1SUHB)
│   └── Ethernet? / USB peripherals / Displays
└── [Pending configuration]
```

---

## Device Inventory

### 1. Windows Desktop (Primary Workstation)
| Property | Value |
|----------|-------|
| Hostname | DESKTOP-JJ1SUHB |
| OS | Windows (with WSL2 Ubuntu 24.04) |
| GPU | RTX 3090 |
| RAM | 47GB |
| Primary Use | Development, AI inference, audio production |

**Services Running:**
- Ollama (7 models, localhost:11434)
- FAITHH Backend (localhost:5557)
- Docker Desktop (optional)

**Key Software:**
- Windsurf (AI coding)
- Audio production suite (for Tom Cat Sound)
- Claude Desktop

### 2. Gen8 MicroServer (servicebox)
| Property | Value |
|----------|-------|
| Hostname | servicebox |
| Model | HP ProLiant MicroServer Gen8 |
| CPU | Intel Xeon E3-1265L V2 (4C/8T @ 2.5-3.5GHz) |
| RAM | 15GB DDR3 ECC |
| Storage | 915GB available |
| OS | Ubuntu 22.04 LTS |
| Docker | v28.2.2 |

**Network:**
- LAN IP: 192.158.1.243 (DHCP - needs static)
- Tailscale: 192.158.1.243

**Services (12 total):**
| Service | Port | Purpose |
|---------|------|---------|
| ChromaDB | 8000 | RAG database (208 docs) |
| Grafana | 3000 | Monitoring UI |
| Prometheus | 9090 | Metrics collection |
| Node Exporter | 9100 | System metrics |
| Pi-hole | 80/53 | DNS filtering |
| Gitea | 3002 (SSH: 2222) | Git hosting |
| GitLab Runner | - | CI/CD |
| Vaultwarden | 8080 | Password manager |
| Docker Registry | 5000 | Private images |
| Registry UI | 5001 | Registry web UI |
| Uptime Kuma | 3001 | Service monitoring |

### 3. OWC Thunderbolt 3 Dock (NEW)
| Property | Value |
|----------|-------|
| Model | OWC Thunderbolt 3 Dock |
| Status | Pending setup |
| Purpose | Hub for peripherals, displays, network |

**Potential Connections:**
- [ ] Ethernet (to switch)
- [ ] Displays
- [ ] Audio interface (for Tom Cat Sound)
- [ ] USB peripherals

---

## Network Configuration Tasks

### Priority 1: Static IP Assignments

**Devices needing static IPs:**

| Device | Current IP | Proposed Static | MAC Address |
|--------|------------|-----------------|-------------|
| Gen8 | 192.158.1.243 | 192.158.1.10 | [get from Gen8] |
| Windows Desktop | DHCP | 192.158.1.20 | [get from ipconfig] |
| OWC Dock (if ethernet) | DHCP | 192.158.1.30 | [TBD] |

**How to set static IPs:**
1. **Option A - Router DHCP Reservation (Recommended)**
   - Log into router admin
   - Find DHCP settings
   - Add reservation: MAC address → Static IP

2. **Option B - Device-level static**
   - Gen8: Edit `/etc/netplan/` config
   - Windows: Network adapter settings

### Priority 2: DNS Configuration

**Current:**
- Pi-hole running on Gen8 (192.158.1.243:53)
- Not yet network-wide

**To enable network-wide:**
1. Set router's DHCP DNS server to Gen8 IP
2. Or manually configure each device

### Priority 3: Firewall & Security

- [ ] Document open ports
- [ ] Configure UFW on Gen8
- [ ] VPN considerations for remote access

---

## Remote Recording Infrastructure (Future)

### Requirements Research Needed

| Topic | Questions | Research Method |
|-------|-----------|-----------------|
| Latency | What's acceptable for remote recording? (<20ms?) | Web search + audio forums |
| Protocols | Dante, AVB, or IP-based? | Manufacturer docs |
| Hardware | Network audio interfaces? | Product research |
| Software | JackTrip? SonoBus? Source-Connect? | Feature comparison |
| Network | Dedicated VLAN? QoS settings? | Network engineering |

### Potential Architecture
```
Remote Client
    │
    ├── [Internet] ← Latency concern
    │
Home Network (Your Setup)
    │
    ├── OWC Thunderbolt Dock
    │   └── Audio Interface
    │
    └── Windows Desktop
        └── DAW (recording/mixing)
```

### Limitations to Research
- [ ] Internet upload speed requirements
- [ ] Latency compensation techniques
- [ ] Sync/timecode considerations
- [ ] Backup recording strategies
- [ ] Legal considerations for remote sessions

---

## Service Access Quick Reference

### Gen8 Services (192.158.1.243)
| Service | URL | Credentials |
|---------|-----|-------------|
| ChromaDB | :8000/api/v2/heartbeat | None |
| Grafana | :3000 | admin / Grafana2026! |
| Pi-hole | :80/admin | admin / PiHole2026! |
| Vaultwarden | :8080 | IavZyxU3ie2OduLu9cq+u2wO2CNNJ+6I2RUfilhAvMY= |
| Gitea | :3002 | [your account] |
| Prometheus | :9090 | None |
| Uptime Kuma | :3001 | [setup required] |
| Docker Registry | :5000 (UI: :5001) | None |

### Local Services (Windows/WSL)
| Service | URL |
|---------|-----|
| FAITHH Backend | localhost:5557 |
| Ollama | localhost:11434 |

### SSH Access
```bash
# Gen8
ssh -i ~/.ssh/servicebox_ed25519 jonat@192.158.1.243

# Gitea SSH
ssh -T git@192.158.1.243 -p 2222
```

---

## Maintenance Commands

```bash
# Gen8 health check
~/ai-stack/gen8_health_check.sh

# Check all containers
ssh -i ~/.ssh/servicebox_ed25519 jonat@192.158.1.243 "docker ps --format 'table {{.Names}}\t{{.Status}}'"

# ChromaDB document count
curl -s "http://192.158.1.243:8000/api/v1/collections/faithh_knowledge_base" | jq '.id'

# Restart FAITHH backend
cd ~/ai-stack && ./restart_backend.sh
```

---

## Next Steps

1. [ ] Get MAC addresses for static IP setup
2. [ ] Configure router DHCP reservations
3. [ ] Test OWC dock connectivity
4. [ ] Complete Tom Cat Sound taxes (PRIORITY)
5. [ ] Research remote recording requirements
6. [ ] Document tax workflow for future automation

---

**End of Ecosystem Map**
