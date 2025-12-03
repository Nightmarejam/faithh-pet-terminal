# FAITHH Parity File Index
**Last Updated**: 2025-11-25  
**Purpose**: Master index of all parity files tracking physical/real-world state

---

## Current Parity Files

### Audio Production
- **[audio_workspace.md](audio_workspace.md)** - VoiceMeeter routing, hardware inventory, workflow checklists
  - Covers: UAD Volt 1, PreSonus 1810c, Blue Yeti, WaveLab, OBS
  - Workflows: Streaming, Mastering, Remote Collaboration

### Network Infrastructure  
- **[network_infrastructure.md](network_infrastructure.md)** - Network topology, VLAN strategy, optimization procedures
  - Covers: UDM, Nighthawk (bridge mode), UniFi AP, Switch, NAS
  - Status: Double-NAT fix documented, implementation pending

---

## Planned Additions

- [ ] `dev_environment.md` - WSL2, Docker, GPU configs, Python environments
- [ ] `streaming_setup.md` - OBS scenes, encoding settings (currently in audio_workspace)
- [ ] `mastering_workflow.md` - WaveLab templates, file schemas

---

## Update Protocol

1. **After hardware changes**: Update relevant parity file within 24 hours
2. **After workflow changes**: Update checklists immediately  
3. **Weekly review**: Verify index matches actual files
4. **Auto-update**: FAITHH session summaries can suggest parity updates

---

## File Locations

| File | Git Tracked | Contains Secrets |
|------|-------------|------------------|
| audio_workspace.md | ✅ Yes | ❌ No |
| network_infrastructure.md | ✅ Yes | ❌ No (templates only) |
| ../network-backups/* | ❌ No | ✅ Yes (actual IPs, passwords) |

---

*This index maintained by Jonathan + FAITHH system*
