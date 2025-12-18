# Archived Projects Reference
**Last Updated:** 2025-12-18
**Purpose:** Preserve context for inactive projects

---

## Overview

This document maintains historical context for projects that were previously tracked in `project_states.json` but are no longer in active development. These projects remain part of the broader ecosystem but are not currently the focus of development work.

The current `project_states.json` intentionally focuses on **active development projects** (FAITHH Phase 2, Gen8 services) to maintain accuracy and avoid stale tracking data.

---

## Constella Framework

### Status
- **Phase:** Documentation & Governance
- **Last Active:** 2025-11-26
- **Current State:** On hold, documentation phase complete

### Vision Statement
Proof-before-scale civic OS for resilient siting, healthy homes, and fair governance. Judge systems by how they treat those with weakest resonance.

### Why It Matters
Current civic systems create dissonance. Constella provides governance framework that respects dignity and enables renewal through harmonic alignment.

### Key Accomplishments
- Framework v1.2 master completed
- Hard review integration (token mechanics, governance edge cases)
- 1,904 Constella docs indexed into FAITHH RAG with priority
- Governance specifications drafted for pilot programs

### Resources
- **Primary Documentation:** See `constella-framework/` directory
- **FAITHH Integration:** `docs/CONSTELLA_MASTER_REFERENCE.md`
- **RAG Index:** 1,904 documents indexed with priority weighting

### Next Milestone (When Resumed)
Complete governance edge cases and pilot program designs before scaling.

### Success Criteria
Communities can pilot governance structures that demonstrably improve civic health before scaling.

---

## Audio Production (Floating Garden Soundworks / Tom Cat Sound LLC)

### Status
- **Phase:** Primary Income Focus
- **Last Active:** 2025-11-20
- **Current State:** Operational, income-generating

### Vision Statement
Boutique audio mastering and remote collaboration services. High-fidelity production with global reach through innovative remote workflows.

### Why It Matters
**Primary income source.** Everything else depends on this being sustainable.

### Current Priorities
- Find and serve paying clients
- Complete partner Tailscale setup for remote collaboration
- Define service packages with pricing
- Create portfolio/samples

### Tools & Setup
- **Mastering:** WaveLab 11.2 on Windows desktop
- **Interface:** UAD Volt 1
- **Monitoring:** Sonarworks reference correction
- **Remote Collaboration:** SonoBus/JackTrip with partner's M2 Mac Mini + Luna DAW
- **NAS Storage:** Tom Cat Productions at `/volume1/Audio/tomcat/`

### Partner Information
- **Name:** Thomas
- **Location:** South Dakota
- **Equipment:** M2 Mac Mini, Luna DAW
- **Network:** Tailscale mesh connection (pending final setup)

### Next Milestone
Establish sustainable client pipeline with 2-3 active clients per month and repeat business.

### Success Criteria
- 2-3 active clients per month
- Repeat business from existing clients
- Remote workflow proven with South Dakota partner

---

## Infrastructure

### Status
- **Phase:** Production Ready
- **Last Active:** 2025-12-07
- **Current State:** All critical infrastructure operational

### Phase Description
NAS organized, Tailscale connected, documentation complete. FAITHH Full and FAITHH Lite both operational.

### Devices
| Device | Role | Status | Notes |
|--------|------|--------|-------|
| **Windows Desktop** | FAITHH Full, AI inference, primary workstation | ✅ Operational | Ryzen 9 3900X, 48GB RAM, RTX 3090 + GTX 1080 Ti |
| **MacBook Pro** | FAITHH Lite, mobile mastering, Constella dev | ✅ Operational | Tailscale IP: 100.122.56.106 |
| **DS220j NAS** | File storage only | ✅ Organized | 3.6TB organized, 794GB freed (2025-12-06) |
| **ProLiant Gen8** | Future services box | 🔄 Upgrading | See `docs/GEN8_SERVICES_PLAN.md` |
| **Phone** | Tailscale access to Windows FAITHH | ✅ Connected | Mobile access |
| **Partner Mac Mini** | Remote collaboration (Thomas) | ⏳ Pending | Tailscale setup in progress |

### Network Infrastructure
- **Tailscale Mesh:** 6 devices connected across locations
- **Windows Desktop IP:** 100.115.225.100 (FAITHH Full)
- **MacBook Pro IP:** 100.122.56.106 (FAITHH Lite)

### NAS Structure
| Share | Size | Contents |
|-------|------|----------|
| Personal | 1.4TB | Videos, photos, docs, private files |
| Audio | 152GB | Tom Cat Productions, stems, backups |
| Backups | 1012GB | Windows host, legacy backups |
| AI | 177GB | Learning Portal, datasets |
| Archive | ~30GB | ISOs, old software |
| Inbox_Sorted | 66GB | Needs manual sorting |

### FAITHH Infrastructure Status
**Windows Full:**
- Status: Production ready
- Documents: 93,629 indexed in ChromaDB
- Models: llama3.1-8b, qwen2.5-coder:7b, qwen2.5-7b
- Integrations: self-awareness, constella, decisions, scaffolding, project_states

**MacBook Lite:**
- Status: Operational
- Model: llama3.1:8b
- Context Files: life_map, constella, audio
- Response Time: ~2 seconds

### Next Milestone
ProLiant Gen8 activation when $130 budget available (CPU + RAM upgrades).

### Upgrade Details
- **CPU:** Intel Xeon E3-1265L v2 ($50-60)
- **RAM:** 2x 8GB DDR3 ECC ($60-80)
- **Total:** $110-130
- **Purpose:** Pi-hole DNS filtering + Uptime Kuma monitoring

---

## Cross-Project Themes

### Resonance and Harmony
All projects involve creating or maintaining harmony:
- **Civic:** Constella governance framework
- **Sonic:** Audio mastering and production
- **Personal Workflow:** FAITHH as thought partner

### Celestial Equilibrium
Unifying philosophy across projects - resonance gap, harmonic alignment, the human standard.

### Proof Before Scale
Both Constella and FAITHH follow this principle - validate core functionality before expanding.

### Affordable But Mighty
High ROI upgrades, repurpose hardware efficiently, budget-conscious decisions.

---

## Time Allocation (Previous Balance)

When all projects were active, the recommended time allocation was:

| Project | Allocation | Rationale |
|---------|------------|-----------|
| Audio Client Work | 60% | PRIMARY INCOME FOCUS |
| FAITHH Maintenance | 20% | Daily usage, not building |
| Constella Development | 10% | Documentation when inspired |
| Infrastructure | 10% | Maintenance only |

**Current Focus:** With Constella on hold and infrastructure stable, time is reallocated to FAITHH Phase 2 completion and Gen8 services buildout while maintaining audio production as primary income.

---

## Why These Projects Are Archived

### Intent
These projects are **not abandoned** - they are **paused** or **operational but not in active development**.

### Rationale for Archival
1. **Accuracy Over Comprehensiveness:** Better to have accurate tracking of 2 active projects than outdated tracking of 5 projects with stale dates.
2. **Focus on Development Work:** `project_states.json` now tracks projects requiring active coding/implementation.
3. **Context Preservation:** This document preserves historical context without cluttering active project tracking.

### When to Un-Archive
Move projects back to `project_states.json` when:
- Active development resumes (Constella pilot prep)
- Significant infrastructure changes occur (Gen8 complete, new services added)
- Audio production workflow requires software development (DAW plugins, automation)

---

## Related Documentation

- **Active Projects:** See `project_states.json` for FAITHH and Gen8 services
- **Constella Framework:** Full documentation in `constella-framework/` directory
- **FAITHH Context:** See `docs/MASTER_CONTEXT.md` and `docs/HARMONY_CONTEXT.md`
- **Infrastructure Plans:** See `docs/GEN8_SERVICES_PLAN.md` for upcoming services box

---

**Maintenance Note:** Update this document when project status changes significantly or when context needs refreshing for RAG queries.
