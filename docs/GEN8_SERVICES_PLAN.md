# Gen8 MicroServer Services Plan

**Last Updated:** 2025-12-18
**Status:** Parts ordered, awaiting arrival
**Purpose:** Home services box for Pi-hole DNS filtering and Uptime Kuma monitoring

---

## 🎯 Project Overview

The HP ProLiant MicroServer Gen8 is being upgraded to serve as a dedicated home services box. This will handle DNS-level ad blocking and service monitoring without impacting the primary infrastructure.

### Role Definition
- **What it is:** Services box for Pi-hole and monitoring
- **What it's NOT:** Router, NAS, or compute-heavy workloads
- **Why separate:** Keeps critical home services isolated from AI/media infrastructure

---

## 🔧 Hardware Specifications

### Current State
- **Model:** HP ProLiant MicroServer Gen8
- **Status:** OFFLINE - awaiting CPU and RAM upgrades
- **Current Config:** Stock configuration (insufficient for services)

### Ordered Upgrades
| Component | Specification | Purpose |
|-----------|--------------|---------|
| **CPU** | Intel Xeon E3-1265L v2 | Low-power server-grade processor |
| **RAM** | 2x 8GB DDR3-1600 ECC UDIMM | 16GB total (Gen8 max capacity) |
| **Total Cost** | ~$110-130 | Budget-conscious upgrade |

### Why These Specs?
- **Xeon E3-1265L v2:** Server-grade reliability with ECC support, low power draw
- **16GB ECC RAM:** Sufficient for Docker services, error correction for stability
- **ECC Memory:** Critical for 24/7 services box operation

---

## 📦 Planned Services

### Pi-hole (Primary Service)
**Purpose:** Network-wide DNS-level ad blocking

**Deployment:**
```bash
docker run -d \
  --name pihole \
  -p 53:53/tcp -p 53:53/udp \
  -p 80:80 \
  -e TZ="America/Los_Angeles" \
  -e WEBPASSWORD="<secure-password>" \
  --restart=unless-stopped \
  pihole/pihole:latest
```

**Configuration:**
- Assign static IP on home network (e.g., 192.168.1.2)
- Update UDM DHCP settings to point DNS to Pi-hole
- Configure upstream DNS servers (Cloudflare 1.1.1.1 / Google 8.8.8.8)
- Set logging level and blocklists

**Benefits:**
- Ad blocking at DNS level (all devices benefit)
- Faster browsing (blocked requests don't load)
- Privacy protection from tracking domains
- Custom local DNS records for home services

### Uptime Kuma (Secondary Service)
**Purpose:** Service availability monitoring

**Deployment:**
```bash
docker run -d \
  --name uptime-kuma \
  -p 3001:3001 \
  -v uptime-kuma:/app/data \
  --restart=unless-stopped \
  louislam/uptime-kuma:1
```

**Monitoring Targets:**
- FAITHH backend (100.115.225.100:5557)
- ChromaDB (localhost:8000)
- text-gen-webui (localhost:7861)
- Synology NAS (192.168.1.x)
- UDM Pro router
- External uptime (e.g., personal website)

**Alerting:**
- Configure notification channels (email, Discord, etc.)
- Set check intervals (60s for critical, 5min for non-critical)
- Define maintenance windows

---

## 🚀 Installation Plan

### Phase 1: Hardware Upgrade
**When:** Upon part arrival
**Steps:**
1. Power down Gen8 completely
2. Remove side panel
3. Install Xeon E3-1265L v2 CPU (replace existing)
4. Install 2x 8GB DDR3 ECC modules
5. Verify all connections, reseat if needed
6. Power on, enter BIOS/iLO to verify recognition
7. Update iLO firmware if needed

### Phase 2: OS Installation
**OS Choice:** Ubuntu Server 24.04 LTS
**Why Ubuntu Server:**
- Lightweight (no GUI overhead)
- Excellent Docker support
- 5-year LTS support
- Familiar for troubleshooting

**Installation Steps:**
1. Download Ubuntu Server 24.04 ISO
2. Create bootable USB via Rufus/Etcher
3. Boot Gen8 from USB
4. Install Ubuntu Server:
   - Hostname: `gen8-services`
   - User: `jonat`
   - Install OpenSSH server
   - No additional snaps during install
5. First boot configuration:
   ```bash
   sudo apt update && sudo apt upgrade -y
   sudo apt install docker.io docker-compose -y
   sudo usermod -aG docker jonat
   sudo systemctl enable docker
   ```

### Phase 3: Network Configuration
**Static IP Assignment:**
1. Assign static IP via UDM DHCP reservation (e.g., 192.168.1.2)
2. Or configure netplan:
   ```yaml
   # /etc/netplan/00-installer-config.yaml
   network:
     version: 2
     ethernets:
       eno1:
         dhcp4: no
         addresses: [192.168.1.2/24]
         gateway4: 192.168.1.1
         nameservers:
           addresses: [1.1.1.1, 8.8.8.8]
   ```
3. Apply: `sudo netplan apply`

### Phase 4: Service Deployment
**Deploy Pi-hole:**
1. Run Docker command above
2. Access web UI: `http://192.168.1.2/admin`
3. Configure blocklists (default + StevenBlack/hosts)
4. Test DNS resolution: `nslookup google.com 192.168.1.2`

**Deploy Uptime Kuma:**
1. Run Docker command above
2. Access web UI: `http://192.168.1.2:3001`
3. Create admin account
4. Add monitoring targets
5. Configure notifications

### Phase 5: DNS Switchover
**Critical Step - Do During Maintenance Window:**
1. Log into UDM Pro
2. Navigate to Network Settings → Networks → Default
3. Change DHCP DNS Server to Gen8 IP (192.168.1.2)
4. **Keep fallback DNS:** Set secondary DNS to 1.1.1.1
5. Apply changes
6. Renew DHCP leases on test devices
7. Verify ad blocking: `nslookup ads.google.com` (should return Pi-hole IP)

---

## ⚠️ Important Considerations

### Power Management
- Gen8 is always-on device
- Estimated power draw: 25-40W with Xeon E3-1265L v2
- Consider UPS backup for DNS reliability

### Backup Strategy
Pi-hole config backup:
```bash
docker exec pihole pihole -a -t
# Save teleporter backup to NAS weekly
```

Uptime Kuma backup:
```bash
docker exec uptime-kuma npm run backup
# Volume is persistent at /app/data
```

### Failover Planning
**If Gen8 goes offline:**
- Secondary DNS (1.1.1.1) will take over automatically
- Internet works, but no ad blocking
- Uptime monitoring alerts will fail (acceptable)

**Recovery:**
- Boot Gen8
- Docker containers auto-restart (unless-stopped)
- Services resume within ~2 minutes

### Security Hardening
```bash
# UFW firewall rules
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 53/tcp    # DNS
sudo ufw allow 53/udp    # DNS
sudo ufw allow 80/tcp    # Pi-hole web UI
sudo ufw allow 3001/tcp  # Uptime Kuma web UI
sudo ufw enable

# Disable password SSH (key-only)
sudo sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo systemctl restart sshd
```

---

## 📋 Next Steps (When Parts Arrive)

### Pre-Install Checklist
- [ ] Download Ubuntu Server 24.04 ISO
- [ ] Create bootable USB
- [ ] Verify Gen8 iLO access (optional but useful)
- [ ] Document current network DNS settings
- [ ] Choose static IP for Gen8 (outside DHCP range)

### Install Day Checklist
- [ ] Hardware upgrade (CPU + RAM)
- [ ] BIOS verification
- [ ] Ubuntu Server installation
- [ ] Docker installation
- [ ] Static IP configuration
- [ ] Deploy Pi-hole container
- [ ] Deploy Uptime Kuma container
- [ ] Test DNS resolution locally
- [ ] Configure Pi-hole blocklists
- [ ] Add Uptime Kuma monitors
- [ ] **CRITICAL:** Update UDM DHCP DNS settings
- [ ] Test from multiple devices
- [ ] Document final IP/credentials in password manager

### Post-Install Monitoring
- Monitor Gen8 resource usage (htop, docker stats)
- Check Pi-hole query logs for issues
- Verify Uptime Kuma alerting works
- Test failover (temporarily stop Pi-hole, confirm fallback DNS works)

---

## 🔗 Integration with Existing Infrastructure

### Network Diagram
```
Internet
    ↓
UDM Pro (192.168.1.1)
    ↓
├── Gen8 MicroServer (192.168.1.2) - Pi-hole + Uptime Kuma
├── Windows Desktop (192.168.1.x) - FAITHH Full
├── MacBook Pro (Tailscale) - FAITHH Lite
├── Synology NAS (192.168.1.x) - Storage
└── Devices → DNS via Pi-hole
```

### Service Dependencies
- **Pi-hole:** Independent (no dependencies on FAITHH/NAS)
- **Uptime Kuma:** Monitors FAITHH/NAS but doesn't depend on them
- **FAITHH:** Unaffected by Gen8 (uses Google DNS or Cloudflare)

### Why This Separation Matters
- DNS/monitoring can stay up even if AI stack goes down
- AI workloads don't interfere with critical home services
- Clear separation of concerns

---

## 📊 Success Criteria

### Phase Complete When:
- [ ] Gen8 boots reliably with new hardware
- [ ] Pi-hole blocks ads on all home devices
- [ ] Uptime Kuma monitors are green and alerting works
- [ ] DNS failover tested and working
- [ ] No performance issues on home network
- [ ] Documentation updated with final IPs/credentials

### Long-Term Validation:
- Gen8 runs continuously for 30 days without intervention
- Pi-hole query logs show expected blocking rates (~25-40%)
- Uptime Kuma catches at least one real outage
- No complaints about network speed/reliability

---

## 💡 Future Enhancements (Optional)

### When Budget Allows:
- **Unbound:** Recursive DNS server (more privacy than Cloudflare)
- **Grafana:** Visualize Pi-hole stats and Uptime Kuma metrics
- **Wireguard:** VPN access to home network (use Pi-hole remotely)
- **Homer Dashboard:** Unified UI for all home services

### Storage Expansion:
- Gen8 has 4x 3.5" drive bays (currently unused)
- Could add small SSD for faster Docker performance
- Could add drives for local backups

---

## 🎓 References

### Documentation
- [Pi-hole Docker Hub](https://hub.docker.com/r/pihole/pihole)
- [Uptime Kuma GitHub](https://github.com/louislam/uptime-kuma)
- [Ubuntu Server 24.04 Guide](https://ubuntu.com/server/docs)
- [Gen8 Specs (HP)](https://support.hpe.com/hpesc/public/docDisplay?docId=c03793258)

### Related Docs
- `~/ai-stack/project_states.json` - Project tracking
- `~/ai-stack/docs/GPT_PROJECT_CONTEXT.md` - FAITHH context
- `~/ai-stack/docs/MASTER_CONTEXT.md` - Infrastructure overview

---

**Status:** Awaiting parts arrival. Ready to execute install plan once hardware upgrades complete.
