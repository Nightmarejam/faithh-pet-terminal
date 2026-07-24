# Technology Ecosystem Inventory
**Created:** 2025-12-05  
**Last Updated:** 2025-12-05  
**Purpose:** Complete hardware tracking, upgrade planning, and ecosystem architecture

---

## 📍 V1: Current State (Ground Truth)

### Windows Desktop - Primary Workstation
**Location:** Home office, 192.168.1.232 (local), 100.115.225.100 (Tailscale)  
**Primary Use:** Audio production, AI development, FAITHH backend, streaming

#### CPU
```yaml
Model: AMD Ryzen 9 3900X
Architecture: Zen 2 (Matisse), 7nm
Cores/Threads: 12C/24T
Base/Boost: 3.8 GHz / 4.65 GHz
Typical Operation: ~4.2 GHz
Cache: 64MB L3 (4x 16MB), 6MB L2, 768KB L1
TDP: 105W (PPT: 142W)
Socket: AM4
Current Temps: 35-46°C (idle/light load)
Status: ✅ Excellent - No upgrade needed
```

**Notes:**
- PBO (Precision Boost Overdrive) enabled
- Strong single-thread and multi-thread performance
- Still relevant in 2025 for AI workloads
- AM4 platform mature and stable

#### Memory
```yaml
Capacity: 64GB (2x 32GB)
Type: DDR4-3200 (PC4-25600)
Model: G.Skill TridentZ Neo F4-3200C16-32GTZN
Timings: CL16
Voltage: 1.2V
Configuration: Dual channel
Status: ✅ Perfect for current workloads
```

**Notes:**
- Sufficient for Ollama, ChromaDB, Docker stack
- No upgrade needed unless running multiple 70B+ models

#### Graphics
**Dual GPU Configuration:**

**GPU 1 (Display/Streaming):**
```yaml
Model: NVIDIA GeForce GTX 1080 Ti
Manufacturer: EVGA Corp.
VRAM: 11GB GDDR5X
CUDA Cores: 3,584
Architecture: Pascal (GP102-350-A1), 16nm
PCIe: x1 @ 8.0 GT/s (PCIe 3.0)
Power Limit: 250W (300W max)
Purpose: Display output, OBS capture
Status: ✅ Working as intended for display
```

**GPU 2 (AI/Compute):**
```yaml
Model: NVIDIA GeForce RTX 3090
Manufacturer: ZOTAC International
VRAM: 24GB GDDR6X
CUDA Cores: 10,496
Tensor Cores: 328
RT Cores: 82
Architecture: Ampere (GA102-300-A1), 8nm
PCIe: x16 @ 2.5 GT/s (⚠️ Running at PCIe 1.0 speed)
Power Limit: 350W (385W max)
Purpose: Ollama inference, ComfyUI, AI training
Status: ⚠️ PCIe bandwidth needs verification
```

**⚠️ Investigation Needed:**
- ✅ **RESOLVED:** RTX 3090 at PCIe Gen3 x16 confirmed via nvidia-smi
- ✅ **RESOLVED:** GTX 1080 Ti at x1 is intentional (display-only, minimal bandwidth needed)
- ✅ **CONFIRMED:** GPU assignment optimal for workload separation

**GPU Assignment (Verified):**
```bash
# From nvidia-smi and Docker configs:
- RTX 3090 (GPU 1): Ollama inference, AI compute (9.4GB VRAM in use)
- GTX 1080 Ti (GPU 0): Display output, OBS capture (~2.5GB VRAM in use)
```

**Workload Separation Working as Designed:**
- Streaming/gaming doesn't interrupt AI inference
- Display on separate GPU prevents VRAM contention
- x1 bandwidth sufficient for display (no 3D rendering bottleneck)

#### Storage
```yaml
System Drive (C:):
  Model: Samsung 970 EVO NVMe
  Capacity: 1TB (930GB formatted)
  Free Space: 355GB (38%)
  Interface: PCIe 4.0 x4 NVMe
  Status: ✅ Healthy

Secondary Drive (E:):
  Type: SSD
  Capacity: 1.81TB
  Free Space: 925GB (51%)
  Status: ✅ Good

External Storage (D:):
  Model: WD My Passport
  Capacity: 931GB
  Free Space: 929GB (100%)
  Status: ✅ Backup ready

Network Storage:
  - Synology DS220J NAS (nas.taileb8c60.ts.net)
  - Multiple 12.6TB volumes mapped
  - Used for: Project backups, audio archives
```

**Storage Notes:**
- C: drive at 62% usage - monitor but not urgent
- Good distribution across drives
- Network storage accessible via Tailscale when remote

#### Motherboard
```yaml
Manufacturer: ASRock
Model: X570 Steel Legend
Chipset: AMD X570
Socket: AM4
PCIe Support: Gen 4.0
BIOS Version: P5.67 (06/24/2025)
Southbridge: AMD X570
LPCIO: Nuvoton NCT6796D-E
Status: ✅ Modern, well-supported
```

**Motherboard Notes:**
- Supports Ryzen 5000 series (5900X, 5950X) if upgrade desired
- PCIe 4.0 for fast NVMe and GPU bandwidth
- Recent BIOS suggests active maintenance
- No immediate upgrade needed

#### Power Supply
```yaml
Manufacturer: FSP Group
Model: PT-1000FM (PT FM Series)
Wattage: 1000W
Efficiency: 80 Plus Platinum
Type: Full Modular, Active PFC
Standards: ATX 12V v2.4, EPS 12V v2.92
Energy Star: Certified
Status: ✅ Excellent - Plenty of headroom
```

**Power Budget:**
- RTX 3090: 350W (385W max)
- GTX 1080 Ti: 250W (300W max)
- Ryzen 9 3900X: 142W (PPT limit)
- System total: ~800W under full load
- PSU capacity: 1000W (20% overhead) ✅

#### Peripherals & Connectivity
```yaml
Monitor: ASUS ROG PG278QR (27", 2560x1440, 165Hz, 2018)
Audio Interfaces: [Document from audio workflow]
iLok: Connected (for audio software licensing)
Network: Tailscale VPN + local 192.168.1.x
Bluetooth: Micro USB dongle
USB Hubs: Multiple (ASMedia, Generic)
Storage Devices: WD external drives connected
```

---

### MacBook Pro M1 - Mobile Workstation
**Location:** Mobile, 192.168.1.132 (local), 100.122.56.106 (Tailscale)  
**Primary Use:** Mastering sessions, Constella development, FAITHH Lite

```yaml
Model: MacBook Pro M1
CPU: Apple M1 (8-core, 4 performance + 4 efficiency)
RAM: Unknown (likely 8GB or 16GB - TODO: verify)
Storage: 500GB
GPU: Integrated M1 (7 or 8-core)
Status: ✅ FAITHH Lite operational
```

**Software:**
- FAITHH Lite (~/faithh/)
- Ollama (llama3.1:8b model)
- WaveLab (audio mastering)
- Luna DAW (when mobile)

**TODO:** 
- Verify exact RAM amount
- Document installed audio plugins
- Confirm WaveLab vs Luna primary workflow

---

### HP ProLiant MicroServer Gen8 - Future Server
**Location:** Currently offline (home storage)  
**Planned Use:** ChromaDB server, Docker host, always-on services

#### Current Specs
```yaml
CPU: Intel Xeon E3-1220L v2
  Cores/Threads: 2C/4T
  Clock: 2.3 GHz
  TDP: 17W (ultra-low power)
  Architecture: Ivy Bridge
  Socket: LGA 1155
  ECC Support: ✅ Yes

RAM: 4GB (1x 4GB single stick)
  Max Supported: 16GB (2x 8GB DDR3 ECC unbuffered)
  Slots: 2 DIMM slots
  Current: Single-channel, severely limiting performance

Storage: 
  Bays: 4x 3.5" hot-swap SATA
  Current: Unknown configuration
  Controller: HP Dynamic Smart Array B120i (RAID 0/1/10)

Form Factor: Ultra-micro tower (~9" cube)
Power: ~25-40W typical
Status: ⚠️ Offline - Deferred due to electricity cost
```

#### Recommended Upgrades (When Budget Allows)
**CPU Upgrade: Xeon E3-1265L v2**
```yaml
Cores/Threads: 4C/8T (2x current!)
Clock: 2.5 GHz base, 3.5 GHz turbo
TDP: 45W (within stock cooling)
Cost: ~$50-60 (eBay, AliExpress)
ROI: ⭐⭐⭐⭐⭐ Excellent - doubles cores for $50
```

**RAM Upgrade: 2x 8GB DDR3 ECC**
```yaml
Cost: ~$60-80 (used server memory)
Total: 16GB (4x current)
ROI: ⭐⭐⭐⭐ Very good - essential for Docker/ChromaDB
```

**Total Upgrade Cost: ~$110-130**
- Transforms into capable Docker/ChromaDB server  
- Still low power (~40-50W vs 17W current)
- Can run Ollama (slow but functional)
- **CRITICAL:** 4GB RAM is unusable for Docker - RAM upgrade is mandatory, not optional
- **DO BOTH AT ONCE:** Buying RAM in two stages costs more and risks compatibility issues

**Decision:** Deferred until cash flow improves. Current Windows host sufficient.

---

### Synology DS220J NAS
**Location:** nas.taileb8c60.ts.net (local), Tailscale-accessible  
**Primary Use:** File storage, backups, project archives

```yaml
Model: DS220J
CPU: Realtek RTD1296 (ARM quad-core, 1.4 GHz)
RAM: 512MB (not upgradeable)
Bays: 2x 3.5" SATA
OS: DSM (Synology DiskStation Manager)
Capacity: [Document actual drive configuration]
Status: ✅ Reachable and operational
```

**Use Cases:**
- Audio project backups
- Document archives
- Docker image registry (potential)
- Tailscale exit node (potential)

**TODO:** Document actual storage configuration and usage

---

### Partner's Remote System (South Dakota)
**Location:** Remote via Tailscale  
**Use:** Audio collaboration, Luna DAW

```yaml
Model: Mac Mini M2
Owner: Business partner
Purpose: Remote audio session collaboration
Connectivity: Tailscale VPN
Status: Available for collaboration
```

**Collaboration Tools:**
- JackTrip (network audio)
- SonoBus (alternative network audio)
- Luna DAW projects shared via cloud

---

## 🔌 Network Architecture

### Current Topology
```
┌─────────────────────────────────────────────────────────┐
│                 TAILSCALE NETWORK                        │
│            (100.x.x.x private addresses)                 │
│         Encrypted WireGuard tunnel, global access        │
│                                                          │
│  ┌──────────────────┐         ┌──────────────────┐     │
│  │  Windows Desktop │◄───────►│  MacBook Pro M1  │     │
│  │  192.168.1.232   │Tailscale│  192.168.1.132   │     │
│  │  100.115.225.100 │         │  100.122.56.106  │     │
│  │                  │         │                  │     │
│  │  FAITHH Full     │         │  FAITHH Lite     │     │
│  │  93,609+ docs    │         │  Local Ollama    │     │
│  │  ChromaDB        │         │  3 context files │     │
│  │  RTX 3090 + 1080Ti│        │  Audio mastering │     │
│  └──────────────────┘         └──────────────────┘     │
│                                                          │
│  ┌──────────────────┐         ┌──────────────────┐     │
│  │  Synology NAS    │         │  ProLiant Gen8   │     │
│  │  DS220J          │         │  (Offline)       │     │
│  │  nas.taileb8c60.ts.net    │         │                  │     │
│  │                  │         │  Xeon E3-1220L   │     │
│  │  File storage    │         │  4GB RAM         │     │
│  │  Reachable ✅    │         │  Future server   │     │
│  └──────────────────┘         └──────────────────┘     │
│                                                          │
│  ┌──────────────────┐                                   │
│  │  Mac Mini M2     │                                   │
│  │  (Partner - SD)  │                                   │
│  │  [Tailscale IP]  │                                   │
│  │                  │                                   │
│  │  Luna DAW        │                                   │
│  │  Audio collab    │                                   │
│  └──────────────────┘                                   │
│                                                          │
└─────────────────────────────────────────────────────────┘

Local Network: 192.168.1.x
(Intentionally non-standard for security obfuscation)
```

### Network Features
- **Tailscale VPN:** All devices connected, accessible anywhere
- **Security:** Non-standard local subnet (192.168.1.x)
- **Phone Access:** Via Tailscale to Windows host (API endpoints)
- **Remote Collaboration:** Partner Mac Mini accessible via Tailscale

---

## 📊 Workload Analysis

### Current Bottlenecks & Performance
**✅ Working Well:**
- AI inference (RTX 3090 handles 8B-30B models smoothly)
- Multi-tasking (12C/24T handles Docker + audio + AI)
- Storage speed (NVMe provides fast boot and app loading)
- Network connectivity (Tailscale seamless across devices)

**⚠️ Potential Issues:**
- RTX 3090 PCIe bandwidth (showing Gen1 speed - needs testing)
- C: drive space declining (62% used, will need monitoring)
- ProLiant offline (could handle ChromaDB, freeing Windows resources)

**🎯 Current Workload Distribution:**
| Workload | Device | Performance |
|----------|--------|-------------|
| FAITHH Backend (Full) | Windows Desktop | ✅ Excellent |
| FAITHH Lite | MacBook | ✅ Good (~2s response) |
| Ollama Inference (8-30B) | Windows (RTX 3090) | ✅ Excellent |
| ChromaDB (93K+ docs) | Windows | ✅ Good |
| Audio Production | Windows or Mac | ✅ Excellent |
| File Storage | NAS | ✅ Working |
| Docker Stack | Windows (WSL2) | ✅ Working |

### Identified Needs
1. **70B+ Model Inference:** Currently impossible on single RTX 3090
   - Options: Quantization, dedicated inference device, cloud API
   - **Assessment:** Not urgent - 30B models handle coding tasks well
2. **Phone Access:** Need API endpoint on Windows or ProLiant
3. **Always-On Services:** ProLiant ideal for ChromaDB when activated
4. **Remote Audio:** Network audio tools (JackTrip, SonoBus) working

### Computational Capability Assessment

**Model Performance on RTX 3090 (24GB VRAM):**

| Model Size | Quantization | Response Time | VRAM Usage | Status |
|------------|--------------|---------------|------------|--------|
| 7-8B | Full (FP16) | 2-5s | ~8-10GB | ✅ Excellent |
| 14B | Full (FP16) | 5-10s | ~16-18GB | ✅ Very Good |
| 30B | Q4 (4-bit) | 10-20s | ~18-22GB | ✅ Good |
| 70B | Q2-Q3 (2-3 bit) | 30-60s+ | ~22-24GB | ⚠️ Slow but usable |
| 70B | Q4+ | N/A | Exceeds VRAM | ❌ Impossible |

**Workload Suitability:**

| Task | Recommended Model | Current Capability |
|------|-------------------|-------------------|
| FAITHH queries | llama3.1-8b | ✅ Excellent (2-5s) |
| Code completion | qwen2.5-coder-7b | ✅ Excellent (2-5s) |
| Code refactoring | qwen2.5-coder-32b (Q4) | ✅ Good (10-20s) |
| Architecture design | qwen2.5-32b (Q4) | ✅ Good (10-20s) |
| Audio production | N/A | ✅ Not GPU-limited |
| Document analysis | llama3.1-8b | ✅ Excellent |
| Novel algorithm dev | 70B+ (cloud or future) | ⚠️ Slow with Q2/Q3 |

**Verdict for "Foreseeable Future":**
- ✅ Current setup handles 95% of coding tasks well
- ✅ 30B quantized models (Qwen 2.5 Coder 32B) are excellent for development
- ✅ No urgent need for 70B unless doing cutting-edge research
- ✅ Can always fall back to cloud APIs (Claude, ChatGPT) for rare 70B+ needs

**Recommendation:** Your RTX 3090 setup is sufficient. Focus budget on ProLiant activation or storage rather than GPU upgrades.

---

## 🎯 Optimization Candidates

### Tier 1: High ROI / Low Cost (Immediate Opportunities)

#### 1. Verify RTX 3090 PCIe Bandwidth ⚡
**Cost:** Free  
**Effort:** 15 minutes  
**Impact:** ⭐⭐⭐⭐⭐

**Action Items:**
- Run GPU stress test while monitoring PCIe speed
- Check BIOS PCIe settings (ensure Gen4 enabled)
- Verify slot assignment (should be in primary x16 slot)
- Expected result: 16 GT/s (PCIe 4.0), not 2.5 GT/s

**Commands:**
```bash
# Check current PCIe stats
nvidia-smi -q | grep -i pcie

# Or use GPU-Z bandwidth test under load
```

#### 2. Document PSU Specifications 📋
**Cost:** Free  
**Effort:** 5 minutes  
**Impact:** ⭐⭐⭐

**Why:** Need to verify power capacity before considering upgrades.

#### 3. Storage Cleanup & Organization 🗂️
**Cost:** Free  
**Effort:** 1-2 hours  
**Impact:** ⭐⭐⭐

**Current Status:** C: drive at 62% (355GB free of 930GB)  
**Action:** Review and archive unused files to E: or NAS

---

### Tier 2: Capability Expansion (Medium Priority)

#### 1. ProLiant Server Activation 🖥️
**Cost:** $110-130 (CPU + RAM upgrade)  
**Timeline:** When cash flow allows  
**Impact:** ⭐⭐⭐⭐

**Upgrade Plan:**
- Xeon E3-1265L v2 CPU (~$50-60)
- 2x 8GB DDR3 ECC RAM (~$60-80)
- Ubuntu Server 24.04 LTS
- Docker + ChromaDB + lightweight services

**Benefits:**
- Offload ChromaDB from Windows (free up resources)
- Always-on API endpoint for phone access
- Low power consumption (~40-50W vs Windows ~300W+)
- Central knowledge base server

**Decision Gate:** Wait for FGS income to stabilize

#### 2. Dedicated 70B LLM Inference Device 🤖
**Cost:** $500-1500 (highly variable)  
**Timeline:** Research phase  
**Impact:** ⭐⭐⭐⭐

**Options to Research:**
- High-RAM mini-PC (96GB+ RAM for CPU inference)
- Used enterprise GPU (A6000, A100 if prices drop)
- Groq LPU box (if available for purchase)
- Cloud API alternative (calculate vs ownership cost)

**Use Case:** Running qwen-72b, llama-70b for coding tasks  
**Decision Gate:** Define specific need first (what requires 70B that 30B can't do?)

#### 3. Storage Expansion 💾
**Cost:** $80-150 (2TB NVMe)  
**Timeline:** When C: drive approaches 80% full  
**Impact:** ⭐⭐⭐

**Current:** C: at 62%, trending up slowly  
**Trigger:** Drop below 200GB free space  
**Option:** Add 2TB NVMe to second M.2 slot (if available on mobo)

---

### Tier 3: Future Scaling (Low Priority / Exploratory)

#### 1. CPU/Motherboard Upgrade Path 🔄
**Cost:** $400-800 (CPU only or CPU+Mobo)  
**Timeline:** 2026+ or if 3900X fails  
**Impact:** ⭐⭐ (Current CPU still excellent)

**Potential Paths:**
- **Stay AM4:** Ryzen 9 5900X/5950X (~$200-300 used)
  - Keep existing RAM, motherboard
  - 10-15% single-thread improvement
  - **ROI:** ⭐⭐ Low - marginal gains
  
- **Upgrade to AM5:** Ryzen 9 7900X/7950X + mobo + DDR5
  - Cost: ~$600-800 total
  - Requires new RAM (DDR5)
  - 25-40% improvement
  - **ROI:** ⭐⭐⭐ Medium - only if workload demands it

**Current Assessment:** 3900X remains excellent for AI + audio work. Defer indefinitely unless:
- Workload requirements change dramatically
- Current system fails
- Massive price drops make AM5 compelling

**Price Watch:** Monitor used 5950X prices (currently ~$300)

#### 2. RAM Upgrade (Windows) 💾
**Cost:** $200-300 (64GB → 128GB DDR4)  
**Timeline:** Only if needed  
**Impact:** ⭐ (Current 64GB sufficient)

**Decision:** Not needed unless:
- Running multiple 30B+ models simultaneously
- Heavy video editing/rendering added to workflow
- Docker memory pressure observed

#### 3. Multi-User FAITHH Network 👥
**Cost:** TBD (infrastructure + development time)  
**Timeline:** Phase 3+ (after FAITHH v1.0)  
**Impact:** ⭐⭐⭐⭐ (Long-term vision)

**Concept:** Family members get FAITHH Lite instances:
- Individual conversation history (private)
- Shared knowledge scaffolding (Constella awareness)
- Central ChromaDB on ProLiant
- Accessible via Tailscale when away from home

**Deferred because:** Need stable FAITHH v1.0 first

---

## 💰 Budget & Price Tracking

### Immediate (< $150)
| Item | Estimated Cost | Priority | Status |
|------|---------------|----------|--------|
| RTX 3090 PCIe Fix | $0 (BIOS setting) | 🔥 High | TODO |
| Storage Cleanup | $0 | ⭐ Medium | TODO |
| PSU Documentation | $0 | ⭐ Medium | TODO |

### Near-Term ($150-$500)
| Item | Estimated Cost | Priority | Watch Price |
|------|---------------|----------|-------------|
| ProLiant CPU (E3-1265L v2) | $50-60 | 🔥 High | eBay, Ali |
| ProLiant RAM (16GB DDR3 ECC) | $60-80 | 🔥 High | eBay |
| 2TB NVMe (if needed) | $80-150 | ⭐ Low | Sales |

### Long-Term ($500+)
| Item | Estimated Cost | Priority | Notes |
|------|---------------|----------|-------|
| 70B Inference Device | $500-1500 | ⭐ Medium | Research needed |
| CPU Upgrade (5950X) | $200-300 | ⭐ Low | Only if 3900X fails |
| AM5 Platform | $600-800 | ⭐ Very Low | 2026+ or never |

### Market Watch
**Volatile Components (track for opportunistic buys):**
- Used server CPUs (Xeon, EPYC)
- Enterprise GPUs (A6000, A100) - check quarterly
- High-capacity RAM (DDR4/DDR5 pricing fluctuates)
- ProLiant Gen8 units (prices rising due to homelab popularity)

---

## 🔮 Future State Vision

### Target Architecture (When Constraints Lifted)

```
┌─────────────────────────────────────────────────────────┐
│                    FAITHH ECOSYSTEM                      │
│              (Distributed AI + Knowledge Graph)          │
│                                                          │
│  ┌──────────────────┐         ┌──────────────────┐     │
│  │  Windows Desktop │         │  MacBook Pro M1  │     │
│  │  (Workstation)   │◄───────►│  (Mobile)        │     │
│  │                  │         │                  │     │
│  │  • Heavy AI      │         │  • FAITHH Lite   │     │
│  │  • Audio prod    │         │  • Mastering     │     │
│  │  • Dev work      │         │  • Constella     │     │
│  └────────┬─────────┘         └──────────────────┘     │
│           │                                              │
│           │ Queries ┌──────────────────┐                │
│           └────────►│  ProLiant Gen8   │                │
│                     │  (Central Server)│                │
│  ┌──────────────────┤                  │                │
│  │  Phone (API)     │  • ChromaDB      │                │
│  │                  │  • Ollama (light)│                │
│  └──────────────────┤  • Docker host   │                │
│                     │  • API endpoint  │                │
│           ┌─────────┤  • Always-on     │                │
│           │         └──────────────────┘                │
│  ┌────────▼───────┐         ┌──────────────────┐       │
│  │  70B Inference │         │  Family Devices  │       │
│  │  Device (TBD)  │         │  (Future)        │       │
│  │                │         │                  │       │
│  │  • Coding help │         │  • FAITHH Lite   │       │
│  │  • Heavy NLP   │         │  • Shared KB     │       │
│  └────────────────┘         └──────────────────┘       │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Phase Roadmap

**Phase 1: Current State Optimization (Now - Q1 2025)**
- ✅ FAITHH Lite on Mac operational
- ✅ Tailscale network connected
- 🔲 Fix RTX 3090 PCIe bandwidth
- 🔲 Document all specifications
- 🔲 Test Mac ↔ Windows FAITHH via Tailscale

**Phase 2: Central Infrastructure (Q2-Q3 2025)**
- 🔲 Activate ProLiant (CPU + RAM upgrade)
- 🔲 Migrate ChromaDB to ProLiant
- 🔲 Set up always-on API for phone access
- 🔲 Implement hybrid mode (FAITHH Lite queries ProLiant)
- 🔲 Establish backup/sync strategy

**Phase 3: Capability Expansion (Q4 2025+)**
- 🔲 Research 70B inference options
- 🔲 Implement observation layer (auto-documentation)
- 🔲 Prototype Family FAITHH network
- 🔲 Explore world-state knowledge integration
- 🔲 Revenue generation via FAITHH consulting

---

## 🔄 Migration Path

### Phone Access Implementation

**Option A: Windows Host (Immediate)**
```
Phone (Tailscale) → Windows (100.115.225.100:5557)
                  → FAITHH Backend API
                  → Full 93K+ doc ChromaDB
```

**Pros:** Works today, full feature set  
**Cons:** Windows must be on, higher power consumption

**Option B: ProLiant Server (Future)**
```
Phone (Tailscale) → ProLiant (100.x.x.x:5557)
                  → FAITHH Lite API
                  → ChromaDB (migrated from Windows)
                  → Ollama (basic models)
```

**Pros:** Always-on, low power, dedicated  
**Cons:** Requires ProLiant upgrade first

**Migration Strategy:**
1. Start with Windows host (Phase 1)
2. Build ProLiant in parallel (Phase 2)
3. Test ProLiant API + ChromaDB
4. Switch phone to ProLiant when stable
5. Keep Windows FAITHH for heavy workloads

---

## 🤔 Decision Log

### CPU/Motherboard Upgrade: DEFERRED
**Reasoning:**
- Ryzen 9 3900X still excellent (12C/24T, 4.2+ GHz)
- No workload currently constrained by CPU
- Marginal gains don't justify $200-800 investment
- Better to allocate budget to ProLiant or 70B device

**Reconsider if:**
- Compiling/training time becomes bottleneck
- Massive price drops on 5950X or AM5
- Current system fails

---

### RAM Upgrade (Windows): DEFERRED
**Reasoning:**
- 64GB handling all current workloads
- No memory pressure observed
- Better ROI from ProLiant 16GB than Windows 128GB

**Reconsider if:**
- Running multiple 30B+ models simultaneously
- Docker memory alerts observed
- Video editing added to workflow

---

### ProLiant Activation: DEFERRED (COST)
**Reasoning:**
- Excellent ROI ($110-130 for 4C/8T + 16GB)
- Electricity cost concern (~$3-5/mo @ 40W)
- Cash flow from FGS not yet stable

**Proceed when:**
- Monthly FGS income covers operational costs
- Need for always-on services increases
- Phone access becomes essential

---

### 70B Inference Device: RESEARCH PHASE
**Questions to Answer:**
1. What tasks specifically need 70B over 30B?
2. How often would I use it (daily vs occasional)?
3. Is CPU inference (96GB RAM mini-PC) viable?
4. What's break-even vs cloud API costs?

**Decision Gate:** Define specific use case first

---

## 📋 TODO List

### Immediate (This Week)
- [x] Test RTX 3090 PCIe bandwidth under load - **VERIFIED: Gen3 x16 working**
- [x] Verify Docker GPU assignments - **CONFIRMED: Optimal workload separation**
- [x] Document PSU model and wattage - **DONE: FSP PT-1000FM**
- [x] Test Mac → Windows FAITHH via Tailscale - **SUCCESS: 93,629 docs accessible**
- [ ] Verify MacBook RAM amount
- [ ] Get partner on Tailscale for audio collaboration

### Short-Term (This Month)
- [ ] Storage audit and cleanup (target 50% free on C:)
- [ ] Document audio interface specifications
- [ ] Update dev_environment.md with corrections
- [ ] Test phone API access to Windows FAITHH via Tailscale
- [ ] Verify ProLiant storage configuration (drive count/sizes)
- [ ] Add NAS to Tailscale network

### Long-Term (Q1-Q2 2025)
- [ ] Research 70B inference options and costs (LOW PRIORITY - 30B sufficient)
- [ ] Price watch: ProLiant CPU/RAM when budget allows ($110-130 total)
- [ ] Monitor RTX 3090 VRAM usage patterns during heavy workloads
- [ ] Evaluate world-state knowledge integration strategy

---

## 🔍 Review Checkpoints

### For Opus Review:
- ✅ Verify all Windows specs accurate
- ✅ Check ProLiant upgrade analysis math
- ✅ Validate network topology diagram
- ✅ Review upgrade priority reasoning
- ✅ Confirm "affordable but mighty" philosophy alignment

### For Jonathan:
- Does dual-GPU configuration match your use case?
- Is the PCIe bandwidth issue a real problem or expected?
- Any missing hardware (monitors, audio interfaces, etc.)?
- Does upgrade priority ranking feel right?
- Any planned purchases I should add to tracking?

---

**Status:** ✅ V1 Complete - Ready for Testing and Refinement  
**Next Update:** After RTX 3090 PCIe verification and Tailscale connectivity tests

