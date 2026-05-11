# FAITHH Infrastructure System Map

Source of truth: `infrastructure/SYSTEM_MAP.json` (schema in `infrastructure/SYSTEM_MAP.schema.json`).

## Units

### WSL2 Ubuntu (ai-stack)
- Role: primary-dev
- Hostname: DESKTOP-JJ1SUHB
- OS: Ubuntu (WSL2), kernel 6.6.87.2-microsoft-standard-WSL2
- Addresses: LAN 192.158.1.232, Tailscale 100.115.225.100
- GPUs: GTX 1080 Ti (11GB), RTX 3090 (24GB)
- Services: FAITHH backend, Ollama (native)
- Notes: Ollama runs native; ChromaDB is on Gen8

### Gen8 MicroServer (servicebox)
- Role: data-services
- Address: Tailscale 192.158.1.243
- CPU/RAM: Xeon E3-1220L V2, 3.8GB RAM
- Services: ChromaDB, Pi-hole, Uptime Kuma
- Notes: No GPU available

### Synology NAS
- Role: storage
- Notes: On LAN + Tailscale (add IPs + model)

### UniFi Dream Machine (Gen 1)
- Role: network-gateway
- Notes: UniFi controller + router (add LAN IP)

### UniFi Switch 8 (US-8)
- Role: network-switch
- Notes: Managed by UniFi controller (add LAN IP)

### Windows Host (DESKTOP-JJ1SUHB)
- Role: workstation
- Notes: Hosts WSL2 and GPU hardware

### Cloud Services
- Role: external
- Services: Groq API, Claude.ai

## Services

- FAITHH Backend (`/api/chat`, `/api/status`, `/api/compass`, `/api/pulse/*`, `/health`) on port 5557
- Ollama (native) on port 11434
- ChromaDB (Gen8) on port 8000
- Pi-hole on ports 53/80
- Uptime Kuma on port 3001
- Synology DSM (add URL + ports)
- UniFi Network Controller (UDM Gen 1)
- UniFi Switch (US-8)

## Connections

- WSL2 -> Gen8 (Tailscale): ChromaDB API on port 8000
- WSL2 -> Cloud: HTTPS API calls
- Windows -> WSL2: host integration
- UDM -> US-8: managed switch
- UDM -> Synology NAS: LAN path
- WSL2 -> Synology NAS: Tailscale access

## How to Refresh

1. Run `python3 scripts/collect_system_state.py`
2. Update `SYSTEM_MAP.json` with new hardware/service details
3. Keep this markdown in sync or generate a new one
