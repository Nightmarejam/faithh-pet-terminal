# Jonathan's Project Context
<!-- 
  AUTO-GENERATED FILE - Do not edit directly
  Generated: 2026-05-26T00:04:26.036392
  Generator: scripts/generate_context.py
  Sources: project_states.json, faithh_memory.json, decisions_log.json, 
           LIFE_MAP.md, faithh_knowledge_graph.yaml, scaffolding_state.json
-->

---
generated: "2026-05-26T00:04:26.036392"
version: "1.0"
generator: "generate_context.py"
token_estimate: 0
---

## Who I Am

**Name:** Jonathan  
**Role:** Audio Producer & AI Developer  
**Core Challenge:** Maintaining project coherence when attention shifts between multiple long-term projects (ADHD)  
**What I Need:** Systems that remember "why" when I lose sight of it

### Work Context
- **Business:** Tom Cat Sound LLC (dba Floating Garden Soundworks) — boutique audio production
- **Partner:** Thomas Charles Gilson (remote engineer, South Dakota)
- **Tools:** Luna DAW, WaveLab 11.2, UAD Volt 1, PreSonus Studio 1810c, SonoBus

### Philosophy
**Celestial Equilibrium** — resonance, harmonic alignment, dignity  
**Driving Question:** *"How do we build systems that actually serve people well?"*

---

## Current State (2026-04-12)

### FAITHH
- **Phase:** Phase 4 Active
- **Status:** operational
- **Infrastructure:** Backend on WSL2 (localhost:5557), ChromaDB on Gen8 (ChromaDB on Gen8 (192.158.1.10:8000))
- **Knowledge Base:** 53976 chunks indexed (306 conversations)
- **Recent:** Complete Phase 3: Test RAG performance with 37K chunks, Complete Phase 3: Run end-to-end integration tests with qwen25-grounded

### Tom Cat Sound
- **Phase:** Operations & Growth
- **Status:** active
- **Recent:** 2024 tax package COMPLETED — CPA_PACKAGE_2024/ (Jan 26, 2026), NAS setup for partner access — /mnt/z/Business/TomCatSound_LLC/2024_Tax_Filing/

### Constella Framework
- **Phase:** Phase 1 Integration
- **Status:** in_progress
- **Version:** in_progress
- **Recent:** Complete Phase 1 integration per guide, Build example applications

---

## Project Graph

### Entities
Knowledge graph not available

### Relationships
Knowledge graph not available

### The Unifying Thread
All projects answer the same question: *"How do we build systems that actually serve people well?"*
- **FAITHH** — serves Jonathan by maintaining coherence across attention shifts
- **Constella** — serves communities through governance that respects dignity
- **FGS/Audio** — serves artists through high-fidelity production and fair collaboration

---

## Active Focus

### Current Position
FAITHH backend v4.0-pulse; canonical Flask on :5557 (faithh_professional_backend_fixed.py). Coherence Arbiter Phase 1–3 UI path. PULSE operational. ChromaDB on Gen8: faithh_knowledge_base ~54k chunks (see fingerprint_state.json); faithh_uncertainty_surface for migrated noise; session metrics in faithh_session_metrics (not RAG). Default chat model: qwen25-faithh-v3:latest (config.yaml). Ollama stop/num_predict caps in backend/llm_providers.py; KB index quality gate in _finalize_response.

### Open Loops
- **coherence-arbiter-phase3-expansion**: Expand Coherence Arbiter Phase 3: Additional claim types and adaptive thresholding (ready_for_implementation)
- **claude-cli-mcp-integration-issue**: Investigate and resolve Claude CLI MCP Method Not Found errors (-32601) (known_issue_documented)
- **form-1065-filing**: File Form 1065 for Tom Cat Sound LLC (pending_cpa)
- **faithh-memory-staleness**: Establish protocol for keeping source files fresh (solved)

### Parked Ideas (Not Now)
- Mac lightweight FAITHH setup — *Useful but not structural — current system works from any device via Tailscale*
- User avatar from chat history (ML personality extraction) — *Exciting but depends on chip synthesis pipeline being built first*
- RAG temporal weighting and knowledge synthesis — *Important architecture question but ML routing may solve this naturally*
- Auto-journal generation — *Could be built on top of chip synthesis — chips detect topics, journal summarizes*

---

## Key Decisions

### Complete Phase 4 Security, Performance, and AI Optimization Implementation for Single-User Deployment (2026-03-26)
**Project:** faithh | **Status:** unknown

Successfully implement Phase 4 core systems including security middleware, connection monitoring, response caching, performance tracking, and local AI optimization. Optimize for single-user deployment while maintaining family deployment readiness. Rate limiting disabled for personal use but architecture supports re-enabling for family sharing.

### Never load SentenceTransformer in WSL scripts — use ChromaDB default embedding or route through backend (2026-03-01)
**Project:** infrastructure | **Status:** implemented

Loading SentenceTransformer (all-MiniLM-L6-v2) in a WSL script triggers PyTorch CUDA initialization against the GTX 1080 Ti (sm_61 architecture). This causes catastrophic WSL memory pressure and crashes the entire WSL instance. The backend already has the model loaded lazily on CPU — use that instead. ChromaDB also supports default embedding functions that sidestep the issue entirely.

### Configure Claude Desktop with MCP filesystem server for direct FAITHH project access (2026-02-23)
**Project:** faithh | **Status:** unknown

Enable Claude Desktop to read FAITHH project files directly without manual context pasting. This bridges Claude Desktop (Windows) to the FAITHH project (WSL2) using MCP filesystem server, making the living workspace truly accessible from Jonathan's primary Claude interface.

### Implement Phase 2 anchor validation for ground truth claim verification (2026-02-23)
**Project:** faithh | **Status:** implemented_phase2

Add ground truth validation of canonical state file claims against actual system behavior. This provides reality-check validation for the Coherence Arbiter's semantic convergence measurements, ensuring that documented claims reflect actual system capabilities.

### Phase 3 Coherence Arbiter: UI surfacing, anchor expansion, behavior hints, tests (2026-02-23)
**Project:** faithh | **Status:** implemented

Surface coherence in the UI so users see when FAITHH is operating from strong vs weak ground; expand anchor validation with conservative checks; add advisory low-coherence hints without changing model output; protect behavior with tests.


---

## What Matters Now

### The Core Tension
You keep building infrastructure for coherence (FAITHH) instead of using what you have to generate income (FGS). This makes sense because FAITHH solves the coherence problem... but it creates a loop.

### Possible Paths
**Path A:** Income First (FGS focus)\n**Path B:** FAITHH Investment (tool completion)\n**Path C:** Parallel Tracks (40% FGS / 30% FAITHH / 20% Permaculture / 10% Constella)

### The Compass Question
Stop building the compass and start using it. FAITHH at current state is functional. The question isn't whether it's perfect — it's whether you're consulting it when you get lost.

---

## For AI Assistants

### How to Use This Document
1. Read the "Who I Am" section to understand context and preferences
2. Check "Current State" for what's actually deployed/working
3. Reference "Project Graph" to understand how things connect
4. Check "Active Focus" before suggesting work — respect open loops and parked items
5. Review "Key Decisions" before proposing changes — understand why things are the way they are

### Communication Preferences
- Technical but accessible explanations
- Comprehensive documentation (ADHD accommodation)
- Milestone-based planning, not calendar-based
- Show the "why" alongside the "what"
- MegaMan Battle Network aesthetic for FAITHH UI

### What NOT to Do
- Don't suggest reorganizing everything from scratch
- Don't ignore existing decisions without understanding the rationale
- Don't propose calendar-based schedules
- Don't confuse "faith" (religious concept) with "FAITHH" (this AI system)
- Don't confuse Constella (civic governance framework) with software frameworks

---

## Quick Reference

### Key URLs
- FAITHH Backend: http://localhost:5557
- ChromaDB: http://192.158.1.243:8000
- Grafana: http://192.158.1.243:3000
- Gitea: http://192.158.1.243:3002

### Key Files
- `project_states.json` — machine-readable state (source of truth)
- `faithh_memory.json` — AI self-awareness and user profile
- `decisions_log.json` — decision history with rationale
- `LIFE_MAP.md` — strategic framing and philosophy
- `MASTER_CONTEXT.md` — technical overview

### SSH Access
```bash
ssh -i ~/.ssh/servicebox_ed25519 jonat@192.158.1.243
```

---

<!-- End of generated context -->
