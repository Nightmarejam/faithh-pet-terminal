# Network Infrastructure Parity File
**Version**: 1.0  
**Last Updated**: 2025-11-19  
**Status**: Assessment Phase → Implementation Pending  
**Auto-Update**: Via network audit scripts + FAITHH session summaries

---

## 🎯 Goals & Requirements

### Primary Objectives
```yaml
stability: "Eliminate disconnections (current main issue)"
performance: "Support low-latency audio streaming (JackTrip)"
security: "Protect client IP and studio work"
usability: "Maintain family-friendly casting/discovery"
```

### Performance Targets
```yaml
latency: "<20ms local, <50ms to partner's location"
uptime: "99.5% (excluding planned maintenance)"
concurrent_devices: "8-15 typical, 20 max"
bandwidth_allocation:
  streaming: "6-10 Mbps up"
  jacktrip: "3-5 Mbps up" 
  ai_services: "1-2 Mbps up/down"
  overhead: "30% buffer"
```

---

## 📊 Current State Assessment

### Hardware Inventory
```yaml
isp_modem_router:
  model: "Nighthawk C7000v2"
  type: "Modem + Router combo"
  current_mode: "Router mode (causing double-NAT)"
  firmware: "[UNKNOWN - needs check]"
  issue: "First router in chain, conflicts with UniFi"

unifi_dream_machine:
  model: "UniFi Dream Machine (UDM Gen1)"
  firmware: "UniFi OS 4.4.6"
  current_mode: "Router mode (second router = double-NAT)"
  features:
    - Deep Packet Inspection (DPI)
    - Threat Management (IPS/IDS)
    - VLANs
    - Traffic shaping
  performance: "Adequate for 15 devices"

unifi_ap_lr:
  model: "UniFi AP LR (Long Range)"
  connection: "Via 8-port switch"
  current_vlan: "[UNKNOWN - likely same as main]"
  
unifi_switch:
  model: "UniFi 8-port"
  managed: true
  vlans_configured: "[UNKNOWN]"

synology_nas:
  model: "DS220j"
  drives: "1x Seagate IronWolf Pro 16TB"
  services:
    - File storage
    - Attempted Pi-hole (failed - insufficient resources)
  network: "Main network (no VLAN isolation)"
```

### Network Topology (Current - BROKEN)
```
ISP
 ↓
Nighthawk C7000v2 (Router Mode) ← PROBLEM: Creates NAT #1
 ↓
UniFi Dream Machine (Router Mode) ← PROBLEM: Creates NAT #2
 ├─→ UniFi 8-port Switch
 │    └─→ UniFi AP LR
 │    └─→ NAS
 └─→ Direct WiFi clients

ISSUE: Double-NAT causes:
  - Random disconnections
  - Port forwarding failures
  - UPnP conflicts
  - Slower routing decisions
```

### Device Census
```yaml
studio_devices:
  - Windows Desktop (FAITHH AI, streaming, mastering)
  - MacBook Pro M1 (mobile mastering, Constella dev)
  - Partner's M2 Mac Mini (Luna DAW, remote collab)
  - Synology NAS DS220j (client files, backups)
  
family_shared_devices:
  - 3-4 Smart TVs (Fire TV, Roku)
  - 2-3 Streaming sticks (FireStick)
  - 4-5 Phones/tablets
  - 2-3 Game consoles (Xbox, PlayStation, Switch)
  - Misc laptops

smart_home:
  - "[UNKNOWN - needs inventory]"

total_typical: "8-15 concurrent"
total_max: "20 devices"
```

### Current Issues (Ranked by Severity)
```yaml
critical:
  - Random disconnections (affects streaming/recording)
  - Double-NAT (root cause of most issues)
  - No network segmentation (studio + family mixed)

high:
  - YouTube jitter on single TV (bandwidth or AP issue?)
  - No ad blocking (Pi-hole failed on DS220j)
  - Unknown current configuration state

medium:
  - No automated backups of network config
  - No monitoring/alerting for issues
  - WiFi optimization unclear (auto-optimize?)

low:
  - Guest network not configured
  - QoS not tuned for studio work
  - DNS not optimized (using ISP?)
```

---

## 🔍 Pre-Implementation Assessment

### Step 1: SSH Audit (30 minutes)
```bash
# Connect to UniFi Dream Machine
ssh root@192.168.1.1
# Default password: printed on device or set during setup

# Check current firmware
ubnt-systool info | grep "Version"

# Check active VLANs
show vlan

# Check DHCP leases (see all connected devices)
show dhcp leases

# Check current NAT/routing
show nat rules
ip route show

# Check WiFi config
show wireless

# Save output to file for review
ubnt-systool info > /tmp/udm_info.txt
show vlan > /tmp/vlan_config.txt
show dhcp leases > /tmp/current_devices.txt

# Exit and download these files via SCP
```

### Step 2: Speed Test from Multiple Devices
```yaml
test_locations:
  - Windows Desktop (wired)
  - MacBook Pro M1 (WiFi 5GHz)
  - Family room TV (WiFi 2.4GHz)
  - Phone near AP (WiFi 5GHz)

metrics_to_record:
  - Download speed
  - Upload speed
  - Ping to gateway (192.168.1.1)
  - Ping to ISP (8.8.8.8)
  - Jitter

baseline_expected:
  download: "450-600 Mbps"
  upload: "40-50 Mbps"
  ping_gateway: "<5ms"
  ping_internet: "<20ms"
```

### Step 3: Document Current Port Forwards
```bash
# In UniFi Controller:
Settings → Routing & Firewall → Port Forwarding
# Screenshot or document ALL current forwards
# (Will need to recreate after reset)
```

### Step 4: Backup Everything
```bash
# UniFi Controller Backup:
Settings → System → Backup → Download Backup

# Store at: ~/ai-stack/network-backups/unifi_backup_[DATE].unf

# Document current WiFi passwords, device IPs, etc.
```

---

## ✅ Decision Matrix: Fix vs. Fresh Start

### Option A: Fix Current Config (Conservative)
```yaml
time_required: "2-4 hours"
risk: "Low (can revert)"
downtime: "Minimal (<30 mins)"

steps:
  1. Put Nighthawk in bridge mode (fixes double-NAT)
  2. Optimize UniFi WiFi settings
  3. Create Studio VLAN (optional)
  4. Document final state

pros:
  - Keeps working config as baseline
  - Can test incrementally
  - Easier rollback

cons:
  - May miss hidden misconfigurations
  - Accumulated cruft remains
  - Unknown what past "custom configs" do
```

### Option B: Fresh Start (Recommended)
```yaml
time_required: "3-6 hours"
risk: "Medium (must reconfigure everything)"
downtime: "1-2 hours"

steps:
  1. Backup current config
  2. Document all device IPs, port forwards, WiFi names
  3. Factory reset UDM
  4. Put Nighthawk in bridge mode
  5. Configure from scratch following this parity file
  6. Test each feature as you enable it

pros:
  - Known good baseline
  - No hidden issues
  - Documented every setting
  - Parity file matches reality 100%

cons:
  - More initial work
  - Family experiences downtime
  - Must reconfigure everything

recommendation: "Option B (Fresh Start)"
reason: "You mentioned 'I don't know whether [custom configs] are the right choice' - fresh start gives clarity"
```

### Decision Criteria
```yaml
choose_fresh_start_if:
  - You can schedule 2-3 hour maintenance window
  - Current unknowns are causing anxiety
  - Want 100% documented baseline
  - Willing to reconfigure all devices

choose_fix_current_if:
  - Can't afford extended downtime
  - Most things work well enough
  - Just need double-NAT fixed
  - Want minimal disruption
```

---

## 🏗️ Target Architecture (Clean Slate)

### Network Design
```
ISP (Xfinity)
 ↓
Nighthawk C7000v2 (BRIDGE MODE) ← Modem only, no routing
 ↓
UniFi Dream Machine (ROUTER) ← Single source of truth
 ├─→ UniFi 8-port Switch (Managed)
 │    ├─→ UniFi AP LR (WiFi extension)
 │    ├─→ NAS (Wired, VLAN 1 + 10 access)
 │    └─→ Windows Desktop (Wired, VLAN 10)
 │
 └─→ WiFi Clients
      ├─→ Main Network (VLAN 1) - Family devices
      └─→ Studio Network (VLAN 10) - Work devices
```

### VLAN Strategy
```yaml
vlan_1_main:
  name: "Family"
  subnet: "192.168.1.0/24"
  dhcp_pool: "192.168.1.100-200"
  devices:
    - Smart TVs
    - Streaming sticks
    - Family phones/tablets
    - Game consoles
    - Guest devices
  internet: "Full access"
  inter_vlan: "Can access NAS on read-only share"

vlan_10_studio:
  name: "Studio"
  subnet: "192.168.10.0/24"
  dhcp_pool: "192.168.10.50-100"
  devices:
    - Windows Desktop (static: 192.168.10.10)
    - MacBook Pro M1 (static: 192.168.10.11)
    - M2 Mac Mini (static: 192.168.10.12)
  internet: "Full access + QoS priority"
  inter_vlan: "Can access NAS full control"

nas_placement:
  primary_vlan: 1 (Family)
  accessible_from: [1, 10]
  static_ip: "192.168.1.5"
  reason: "Acts as media server for family, work storage for studio"

future_vlan_20_iot:
  name: "IoT"
  subnet: "192.168.20.0/24"
  purpose: "Smart home devices (when added)"
  internet: "Restricted (no inter-VLAN access)"
  status: "Not implemented yet"
```

### WiFi Configuration
```yaml
ssid_main:
  name: "[Your current WiFi name]"
  password: "[Your current password]"
  vlan: 1
  bands: ["2.4GHz", "5GHz"]
  security: "WPA3 (fallback WPA2)"

ssid_studio:
  name: "[Your WiFi name]-Studio"
  password: "[Different secure password]"
  vlan: 10
  bands: ["5GHz only"]
  security: "WPA3"
  note: "Only for studio devices, better isolation"

wifi_optimization:
  auto_optimize: false  # Causes disconnections
  2.4GHz:
    channel: "1, 6, or 11" # Manual selection, avoid auto
    channel_width: "20MHz" # Better stability
    tx_power: "Medium" # Avoid interference
  
  5GHz:
    channel: "36, 40, 44, 48" # DFS channels if clear
    channel_width: "80MHz" # Balance speed/stability
    tx_power: "High" # Less interference on 5GHz

  advanced:
    minimum_rssi: "-80dBm" # Kick weak clients to AP
    band_steering: "Prefer 5GHz"
    fast_roaming: true # 802.11r for AP handoff
```

---

## 🔧 Implementation Procedure

### Phase 1: Preparation (Do This First)
```bash
# Create network-backups directory
mkdir -p ~/ai-stack/network-backups

# Backup UniFi config
# (Download from Settings → System → Backup)
cp ~/Downloads/unifi_backup*.unf ~/ai-stack/network-backups/

# Document current setup
cat > ~/ai-stack/network-backups/current_state.txt << 'EOF'
Date: [DATE]

WiFi Names:
- Main: [name]
- Password: [password]

Port Forwards:
- [list any you remember]

Static IPs:
- NAS: [current IP]
- Desktop: [current IP]

Issues to Fix:
- Random disconnections
- Double-NAT
- [others]
EOF

# Speed test baseline
speedtest-cli > ~/ai-stack/network-backups/speed_before.txt
```

### Phase 2: Nighthawk Bridge Mode (30 min)
```yaml
step_1:
  action: "Access Nighthawk admin"
  url: "http://192.168.0.1 or http://192.168.1.1"
  credentials: "admin / [password on router sticker]"

step_2:
  action: "Navigate to bridge mode"
  path: "Advanced → Administration → Router Mode"
  option: "Enable Bridge Mode"
  warning: "This will disable WiFi on Nighthawk"

step_3:
  action: "Reboot and verify"
  test: "Can no longer access 192.168.0.1"
  result: "Nighthawk now just a modem"
```

### Phase 3: UniFi Fresh Setup (2-3 hours)
```yaml
step_1_factory_reset:
  action: "Reset UDM to factory defaults"
  method: "Hold reset button 10 seconds while powered on"
  result: "All settings erased, fresh start"

step_2_initial_setup:
  connect: "Ethernet cable to UDM LAN port"
  url: "http://192.168.1.1"
  wizard:
    - Set device name: "UDM-Studio"
    - Create admin account
    - Enable automatic updates
    - Enable cloud access (optional)

step_3_network_creation:
  main_network:
    name: "Family"
    vlan_id: 1
    subnet: "192.168.1.1/24"
    dhcp: "192.168.1.100-200"
    ipv6: "Disabled (unless ISP supports)"
  
  studio_network:
    name: "Studio"
    vlan_id: 10
    subnet: "192.168.10.1/24"
    dhcp: "192.168.10.50-100"
    purpose: "Work devices only"

step_4_wifi_setup:
  main_ssid:
    name: "[Your WiFi Name]"
    password: "[Strong password]"
    vlan: 1
    security: "WPA2/WPA3"
  
  studio_ssid:
    name: "[Your WiFi Name]-Studio"
    password: "[Different password]"
    vlan: 10
    security: "WPA3"
    5ghz_only: true

step_5_optimize_wifi:
  disable:
    - Auto-optimize channels
    - Auto TX power
  
  set_manually:
    2.4ghz_channel: "6" # Or run WiFi analyzer first
    2.4ghz_width: "20MHz"
    5ghz_channel: "40"
    5ghz_width: "80MHz"

step_6_security:
  enable:
    - Deep Packet Inspection (DPI)
    - Threat Management → IPS (Intrusion Prevention)
    - "Block malware/phishing sites"
  
  dns:
    primary: "1.1.1.1" # Cloudflare
    secondary: "1.0.0.1"
    # OR use Quad9: 9.9.9.9 / 149.112.112.112

step_7_qos:
  enable: true
  priority_high:
    - Studio VLAN (192.168.10.0/24)
    - UDP 4464 (JackTrip)
    - Custom: "Low latency audio"

step_8_firewall_rules:
  studio_to_nas:
    name: "Studio access NAS"
    from: "192.168.10.0/24"
    to: "192.168.1.5"
    ports: "445,548,5000,5001"
    action: "Allow"
  
  family_to_nas:
    name: "Family read NAS"
    from: "192.168.1.0/24"
    to: "192.168.1.5"
    ports: "445,548,5000"
    action: "Allow"
```

### Phase 4: Device Reconnection (1 hour)
```yaml
priority_order:
  1. Studio devices (ensure they work first)
  2. NAS (test file access)
  3. Family devices (reconnect to main WiFi)

studio_static_ips:
  windows_desktop:
    ip: "192.168.10.10"
    method: "DHCP reservation by MAC"
  
  macbook_m1:
    ip: "192.168.10.11"
    method: "DHCP reservation by MAC"
  
  m2_mini:
    ip: "192.168.10.12"
    method: "DHCP reservation by MAC"

nas_config:
  ip: "192.168.1.5"
  method: "DHCP reservation by MAC"
  note: "In Synology: Control Panel → Network → VLAN → Add VLAN 10 interface"
```

### Phase 5: Testing & Validation (1 hour)
```bash
# Test 1: Speed test from studio devices
speedtest-cli  # Should match ISP speeds

# Test 2: Ping stability
ping -c 100 192.168.10.1  # Should be <5ms, no drops

# Test 3: Inter-VLAN (studio → NAS)
ping 192.168.1.5  # Should work

# Test 4: Family casting
# Open YouTube on phone → Cast to TV
# Should discover devices and work

# Test 5: Gaming/streaming
# Play game, stream OBS
# Monitor for disconnections

# Test 6: JackTrip (when ready)
# Connect to partner
# Measure latency
```

---

## 📊 Ongoing Maintenance

### Daily Monitoring (Automated)
```bash
# Create monitoring script
cat > ~/ai-stack/scripts/network/daily_check.sh << 'EOF'
#!/bin/bash
# Network health check
DATE=$(date +%Y-%m-%d)
LOG=~/ai-stack/network-backups/health_${DATE}.log

echo "=== Network Health Check ===" > $LOG
echo "Date: $(date)" >> $LOG

# Ping gateway
ping -c 10 192.168.1.1 | tail -1 >> $LOG

# Speed test (weekly)
if [ $(date +%u) -eq 1 ]; then
  speedtest-cli >> $LOG
fi

# Check for disconnections in UniFi
# (Requires UniFi API access - future enhancement)

echo "Check complete" >> $LOG
EOF

chmod +x ~/ai-stack/scripts/network/daily_check.sh

# Add to cron (runs at 3am)
# crontab -e
# 0 3 * * * ~/ai-stack/scripts/network/daily_check.sh
```

### Weekly Review (Manual)
```yaml
tasks:
  - Check UniFi Controller for alerts
  - Review disconnection logs
  - Verify backup configs are current
  - Update this parity file if changes made

duration: "15 minutes"
```

### Monthly Deep Check
```yaml
tasks:
  - Run full speed tests from all locations
  - Check for firmware updates
  - Review QoS effectiveness
  - Audit connected devices (remove unknowns)
  - Test failover (what happens if UDM reboots?)

duration: "1 hour"
```

---

## 🚨 Troubleshooting Guide

### Issue: Disconnections Return
```yaml
check:
  1. Auto-optimize re-enabled? (Settings → WiFi → Optimize)
  2. Channel interference? (Run WiFi analyzer app)
  3. Too many devices on 2.4GHz? (Check client list)
  4. AP firmware outdated?

solution:
  - Manually set channels again
  - Enable band steering (push to 5GHz)
  - Add second AP if needed
```

### Issue: Slow Speeds on Studio VLAN
```yaml
check:
  1. QoS enabled?
  2. Speed test from wired device
  3. Check switch port speeds (should be 1Gbps)

solution:
  - Verify studio VLAN has QoS priority
  - Check cable quality (Cat 5e minimum)
```

### Issue: Can't Access NAS from Studio
```yaml
check:
  1. Firewall rule exists?
  2. NAS has VLAN 10 interface?
  3. Ping works? (ping 192.168.1.5)

solution:
  - Re-create firewall rule
  - Add VLAN interface in Synology
  - Check NAS firewall settings
```

---

## 📝 Next Actions

### This Week
- [ ] Run SSH audit (save outputs)
- [ ] Document all current port forwards
- [ ] Backup UniFi config
- [ ] Schedule maintenance window with family
- [ ] Decide: Fix current or fresh start?

### Implementation Day
- [ ] Follow Phase 1-5 procedure
- [ ] Test each phase before proceeding
- [ ] Update parity file with actual IPs/settings
- [ ] Create network diagram (draw.io or similar)

### Post-Implementation
- [ ] Set up automated monitoring
- [ ] Document lessons learned
- [ ] Add to FAITHH auto-index
- [ ] Share config with partner (for their network)

---

**Last Manual Update**: 2025-11-19  
**Next Review**: After implementation  
**Maintained By**: Jonathan + FAITHH auto-updates
