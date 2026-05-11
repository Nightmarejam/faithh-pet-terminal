# Gen8 ProLiant Setup Checklist

## Hardware (Ordered)
- [x] Gen8 ProLiant MicroServer base
- [ ] Xeon E3-1265L v2 (arriving)
- [ ] 16GB DDR3 ECC (arriving)
- [x] Intel 82576-T4 NIC (owned)

## Initial Setup
- [ ] Install Ubuntu Server 24.04 LTS
- [ ] Configure static IP (e.g., 192.168.1.10)
- [ ] Install Docker + Docker Compose
- [ ] Install Tailscale
- [ ] Configure SSH keys from main PC

## Services to Deploy
- [ ] Pi-hole (DNS filtering)
- [ ] Uptime Kuma (monitoring)
- [ ] ChromaDB (RAG database)
- [ ] Portainer (Docker management UI, optional)

## Network Configuration
- [ ] Set Gen8 as primary DNS in UDM DHCP
- [ ] Add to Uptime Kuma monitoring
- [ ] Test from all devices

## Data Migration
- [ ] Export AI chat conversations (already done)
- [ ] Run re-indexer on Gen8 ChromaDB
- [ ] Update FAITHH backend to point to Gen8:8000
- [ ] Verify RAG queries work

## Post-Setup
- [ ] Document final IP addresses
- [ ] Update ~/dev-mode.sh with Gen8 endpoints
- [ ] Test gaming-mode.sh still works
- [ ] Run RAG quality test (target: 85%+)
