# Next Steps Action Plan
**Created:** 2025-12-05  
**Session:** Sonnet Hardware Inventory + Tailscale Setup

---

## 🎯 Immediate Actions (Do Now)

### 1. Verify MacBook RAM ⏱️ 2 minutes

**On your MacBook, run:**
```bash
# Quick check
system_profiler SPHardwareDataType | grep Memory

# Or use the full script
chmod +x ~/Downloads/mac_system_info.sh
~/Downloads/mac_system_info.sh
```

**Expected output:**
- Memory: 8GB or 16GB
- Update hardware_inventory.md with actual amount

---

### 2. Get Partner on Tailscale ⏱️ 10 minutes (his time)

**Action:**
1. Send him this guide: [tailscale_partner_setup.md](computer:///mnt/user-data/outputs/tailscale_partner_setup.md)
2. Have him install Tailscale on Mac Mini M2
3. Get his Tailscale IP (100.x.x.x)
4. Test connection: `ping [his_IP]`

**Benefits:**
- ✅ Secure audio collaboration (JackTrip/SonoBus)
- ✅ File sharing for Luna DAW projects
- ✅ Remote troubleshooting if needed

**Follow-up test:**
```bash
# From your Mac or Windows
ping [PARTNER_TAILSCALE_IP]

# Test JackTrip over Tailscale (after he's connected)
```

---

### 3. Test Phone API Access ⏱️ 15 minutes

**Steps:**
1. Install Tailscale on your phone
   - iOS: App Store → "Tailscale"
   - Android: Play Store → "Tailscale"

2. Log in with same account as desktop

3. Test in phone browser: `http://100.115.225.100:5557`

4. Try a FAITHH query

**Full guide:** [phone_api_access_guide.md](computer:///mnt/user-data/outputs/phone_api_access_guide.md)

**Success criteria:**
- ✅ Can browse to FAITHH from phone
- ✅ Queries return in <10 seconds
- ✅ Works on cellular (not just WiFi)

---

## 📅 Near-Term Actions (This Week)

### 4. Add NAS to Tailscale ⏱️ 20 minutes

**When:** After phone access is working  
**Guide:** [nas_tailscale_setup.md](computer:///mnt/user-data/outputs/nas_tailscale_setup.md)

**Steps:**
1. Open Package Center on DS220J
2. Install Tailscale package
3. Log in with your account
4. Note new 100.x.x.x IP for NAS
5. Test file access from Mac/Windows

**Benefits:**
- Remote file access without port forwarding
- Secure backup destination
- Share files with partner

---

### 5. Update dev_environment.md

**Changes needed:**
```bash
# Edit ~/ai-stack/parity/dev_environment.md

Updates:
- PSU: FSP PT-1000FM (1000W Platinum)
- GPU PCIe: Confirmed Gen3 x16 (RTX 3090), x1 (1080 Ti - intentional)
- RAM: Confirmed 2x 32GB G.Skill TridentZ Neo
- ChromaDB docs: 93,629 (not 91,604)
- Tailscale IPs: 100.115.225.100 (Windows), 100.122.56.106 (Mac)
- Add: Elgato 4K X, Stream Decks documented
```

---

### 6. Document Audio Interfaces

**TODO:** Add to hardware_inventory.md:
- Audio interface model(s)
- Sample rates supported
- Inputs/outputs
- Driver versions
- Connection type (USB, Thunderbolt, etc.)

**Where to add:** Under "Peripherals & Connectivity" section

---

## 🔮 Future Actions (When Time Allows)

### 7. Storage Cleanup (Optional)

**Current status:** C: drive at 62% (355GB free)  
**Trigger point:** When drops below 200GB free

**Actions:**
- Review large files/folders
- Move old projects to E: drive or NAS
- Clean Docker images/containers

### 8. Light OBS Setup for Gaming (Later)

**Equipment:** Elgato 4K X + GTX 1080 Ti (display GPU)  
**Plan:** Lightweight streaming setup, doesn't interfere with AI work

**Deferred because:** FGS audio work is priority

---

## 📊 Success Metrics

After completing immediate actions, you should have:

- ✅ Partner on Tailscale (secure audio collaboration)
- ✅ Phone access to full FAITHH (93K docs anywhere)
- ✅ MacBook specs documented (RAM amount confirmed)
- ✅ Complete hardware inventory
- ✅ NAS accessible remotely (optional but useful)

---

## 🚨 Blockers/Dependencies

**None currently!** All immediate actions are ready to execute.

**Optional dependencies:**
- ProLiant activation: Wait for cash flow (~$110-130)
- 70B inference: No urgency (30B sufficient)
- Streaming setup: Defer until FGS income stable

---

## 📞 Questions to Ask Partner

When getting him on Tailscale:

1. What's your Mac Mini M2 Tailscale IP? (100.x.x.x)
2. Can you ping my Windows? (100.115.225.100)
3. Ready to test JackTrip over Tailscale?
4. Want access to shared NAS folders? (requires NAS on Tailscale first)

---

## 📝 Files Created This Session

All guides ready to use:
- [tailscale_partner_setup.md](computer:///mnt/user-data/outputs/tailscale_partner_setup.md) - Send to partner
- [phone_api_access_guide.md](computer:///mnt/user-data/outputs/phone_api_access_guide.md) - For testing phone
- [nas_tailscale_setup.md](computer:///mnt/user-data/outputs/nas_tailscale_setup.md) - For NAS setup
- [mac_system_info.sh](computer:///mnt/user-data/outputs/mac_system_info.sh) - Run on MacBook
- [hardware_inventory.md](computer:///mnt/user-data/outputs/hardware_inventory.md) - Complete hardware docs

---

**Priority Order:**
1. MacBook RAM verification (2 min)
2. Partner on Tailscale (10 min his time)
3. Phone API test (15 min)
4. NAS Tailscale (20 min, optional)

**Estimated total time:** ~45 minutes active work  
**Impact:** Massive improvement in remote workflow flexibility

---

**Status:** ✅ Ready to execute  
**Next session focus:** After these are done, can tackle ProLiant planning or streaming setup
