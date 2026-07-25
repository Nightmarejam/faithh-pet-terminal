# IDEA VAULT

## Pulse Ops Guardian (future)

### Purpose
Make Pulse a lightweight ops/status AI: surface collector health, backend/Ollama/Chroma heartbeat, and suggest safe actions. No auto-restarts; human-approved fixes only.

### Status JSON for Pulse
- Endpoint: `GET /api/context/collectors/status`
- Shape:
  ```json
  {
    "success": true,
    "aggregated_at": "<iso>",
    "issues": [],
    "summary": {
      "git": {"collected_at": "<iso>", "success": true, "version": "1.0", "error": null},
      "file_changes": {"collected_at": "<iso>", "success": true, "version": "1.0", "error": null},
      "health": {"collected_at": "<iso>", "success": true, "version": "1.0", "error": null},
      "terminal": {"collected_at": "<iso>", "success": true, "version": "1.0", "error": null}
    }
  }
  ```
- Companion endpoints: `GET /api/context/collectors` (full data), `GET /api/status` (service health).

### UI/Chip concept
- Pulse chip pulls status JSON every few minutes.
- Badges: green (fresh & success), yellow (stale), red (failure).
- Suggested actions: display text; optional “heal” button to POST a safe runner (not yet implemented).
- HTML view: small read-only dashboard calling the same JSON (no terminal actions).

### Future security/defense ideas
- Watch unexpected outbound calls/new listening ports (extend health collector).
- Git integrity signals: diff summary since baseline; alert on new executables in sensitive dirs.
- Sandbox toggle: disable risky actions unless approved; Pulse prompts user.

### Near-term tasks (if prioritized)
- Add HTML status view.
- Add POST `/api/context/collectors/run` to re-run a collector safely (whitelist args).
- Wire Pulse chip to consume status JSON and show badges.

### Model/GPU check (2026-01-16)
- Chat API with `model="qwen3-faithh:latest"` returns `model_used: qwen3-faithh:latest`, provider `Alibaba (via Ollama)`, response_time ~19s.
- `nvidia-smi --query-compute-apps` shows the Ollama PID on both GPUs (bus 09:00.0 and 0E:00.0), so CUDA_VISIBLE_DEVICES=1 isolation is not effective yet.
- Mitigation to try: confirm `/etc/systemd/system/ollama.service.d/override.conf` with `CUDA_VISIBLE_DEVICES=1`, add `OLLAMA_GPU=1` if supported, daemon-reload + restart Ollama, re-check `nvidia-smi` during a Qwen request.

### WSL GPU Isolation Limitation (2026-01-16)
**Finding:** In WSL, Ollama still shows the PID on both GPUs despite:
- Setting `CUDA_VISIBLE_DEVICES` and `NVIDIA_VISIBLE_DEVICES` to the 3090 UUID and index 1.
- Using systemd DevicePolicy/DeviceAllow to restrict to /dev/nvidia1.
**Result:** With strict DevicePolicy, Ollama fell back to CPU (no nvidia-smi entries, ~60s). With env-only, Ollama runs (~19s) but nvidia-smi lists the PID on both bus IDs (09:00.0 and 0E:00.0).
**Conclusion:** WSL appears to expose both GPUs regardless of CUDA_VISIBLE_DEVICES. Accept dual-GPU visibility; timely responses (~19s for Qwen) indicate the 3090 is doing the heavy lifting; the 1080 Ti appears idle or minimally used.

### Current Optimal Config for This Environment
- **Ollama systemd override** (`/etc/systemd/system/ollama.service.d/override.conf`):
  ```
  [Service]
  Environment="CUDA_DEVICE_ORDER=PCI_BUS_ID"
  Environment="CUDA_VISIBLE_DEVICES=1"
  Environment="NVIDIA_VISIBLE_DEVICES=1"
  Environment="OLLAMA_GPU=1"
  Environment="OLLAMA_NUM_PARALLEL=2"
  Environment="OLLAMA_MAX_LOADED_MODELS=2"
  Environment="OLLAMA_KEEP_ALIVE=24h"
  ```
- **Embedder:** Force SentenceTransformer to CPU to avoid CUDA kernel image errors (`device="cpu"`).
- **Backend:** `faithh_professional_backend_fixed.py` on port 5557; RAG stable (7/7 tests pass).
- **Collectors:** Cron fixed with absolute paths and cwd; status page at `/collectors/status`.
- **UI:** Shows model/provider per response; header link to collectors status.
- **Performance:** Qwen3-faithh:latest ~19s; Llama31-faithh:latest faster; RAG search ~0.14s.
- **Notes:** GPU isolation may work in native Linux but not WSL; dual visibility is acceptable given performance.


---

### Handoff Document Architecture (2026-01-30)
**Problem:** Multiple handoff/status documents exist across projects (HANDOFF.md, STATUS_TRACKER.md, Session_Summary.md, various dated STATUS files). When a new AI session starts, it's unclear which document has the most accurate/current information. Documents get stale, duplicate, or conflict.

**Questions to Resolve:**
1. Should handoffs be referenced at all, or are they more noise than signal?
2. Should old handoffs be archived (moved to `99_archives/`) after each session?
3. Are they disposable (delete after the next session confirms it's caught up)?
4. Should we scan for historical content and consolidate into a structured log?

**Potential Solutions:**
- **Single Source of Truth:** One `HANDOFF.md` per project, always overwritten (not versioned). Previous content archived automatically.
- **Append-Only Log:** Instead of full documents, append timestamped entries to a `SESSION_LOG.md`. AI scans recent entries, not whole docs.
- **Structured JSON:** Machine-readable status (like `tomcat_sound_status.json`) that's easier to parse than markdown. Human-readable summary auto-generated from it.
- **Hybrid:** JSON for machine state + brief markdown summary for human review. Archive policy: keep last 3-5 sessions, older ones compressed to one-liners in a history section.

**Key Insight:** The goal is "minimum viable context" — enough for a new session to pick up where the last left off, without wading through stale or conflicting docs.

**Next Step:** Prototype the append-only log approach on one project (e.g., tomcat-sound) and evaluate after 3-5 sessions.

---

## Distilled Ideas (Knowledge Distiller — Feb 2026)

*Extracted from 32,873 ChromaDB conversation chunks via deepseek-r1:32b. Scored ⭐4-5 as documentation-worthy.*

### ⭐5 Personalized Chip Synthesis System

Proposes a system where FAITHH learns and generates personalized "battle chips" based on user behavior patterns. Chip creation would be triggered by detecting recurring query patterns, novel topic clusters, or user-defined bookmarks.

**Key concepts:**
- Automatic chip generation from conversation pattern detection
- Privacy-aware personalization boundaries
- Chip evolution over time (chips get stronger as patterns solidify)
- User-curated vs auto-generated chip distinction

**Actions:** Design chip synthesis triggers, define pattern detection thresholds, implement privacy controls.

### ⭐5 Oha Agloki Consciousness Model

A novel state machine model for an AI engine with a structured cycle through various consciousness states. Defines specific transitions and validations between states, modeling awareness as an emergent property of state cycling.

**Key concepts:**
- Consciousness as cyclic state machine (not linear)
- State transitions with validation gates
- Potential integration with FAITHH's chip routing for "awareness" of its own processing

**Actions:** Document the full state machine diagram, explore integration with PULSE self-reflection system.

### ⭐4 Consciousness Architecture Model

Framework for understanding consciousness through resonance, geometry, and feedback loops. Organized into layers: gravitational coherence, probability processing, and emergent awareness. Connects to the Harmony Framework's resonance concepts.

### ⭐4 Brain Function as Layered System Model

Three-layer model of brain function: physical mechanisms → neural integration → symbolic/affective processing. Proposes biomechanical resonance and quantum processing analogies. Could inform FAITHH's own multi-layer processing architecture.

### ⭐4 Body Mapping Controller Framework

Maps the human body as a gaming controller or engine transmission, with the head as control hub. Sensory inputs and motor outputs modeled as controller axes and buttons. Ties into Harmony Framework's head/feet/hands module structure.

### ⭐4 Sacred Geometry in Biomechanical Modeling

Applies golden ratio, Fibonacci sequence, and other sacred geometry principles to understand human biomechanics and energy flow. Proposes a framework for mapping body proportions to resonance frequencies.

### ⭐4 Earth as Standing Waves

Geological resonance model treating Earth's structure as standing wave patterns. Connects plate tectonics, mantle convection, and geological features to wave mechanics. Analogous to Harmony Framework's phase flip concepts at planetary scale.

### ⭐4 Yin Yang Superposition Model

Applies superposition principles to biomechanics, modeling opposing forces (flexion/extension, sympathetic/parasympathetic) as quantum-like superposition states rather than binary toggles. Informs Harmony Framework's yin/yang flow concepts.

### ⭐4 Jurassic-Inspired Failsafe Agriculture

Uses Jurassic-era plant resilience (high CO₂-adapted species) as blueprint for failsafe agricultural strategy. Proposes seed storage partnerships (Svalbard-style) and research into ancient plant genetics for climate adaptation.

### ⭐4 Cymatics and Life Formation

Cymatics patterns (standing wave geometries in vibrated media) appear in biological formation processes — cell division, tissue folding, organ development. Proposes that life itself may follow cymatics-like resonance patterns at multiple scales, from cellular to geological.

**Connection:** Bridges Harmony Framework's resonance concepts with developmental biology. Relates to Earth as Standing Waves concept at macro scale.

### ⭐4 Keratin-Melanin Interaction Insights

Novel observation that keratin and melanin protein interactions exhibit resonance-like behavior — their structural relationships in hair, skin, and nails follow frequency-dependent patterns rather than simple chemical bonding. Suggests biological structures optimize for electromagnetic and mechanical resonance.

### ⭐4 AI Supercharging Techniques

Advanced techniques for enhancing AI systems: graph RAG, multi-agent orchestration, multimodal data integration, hierarchical memory systems. Structured approach for iterative improvement of FAITHH's retrieval and reasoning capabilities.

### ⭐4 Neural Studio Design Concept

Studio design inspired by brainwave states: acoustic zones tuned to alpha, beta, theta, and delta frequencies. Branding as a "resonant brain" environment for Tom Cat Sound LLC.

### ⭐4 Legal Doctrines of Self-Preservation

Framework integrating legal doctrines (self-defense, necessity) with psychological principles of panic and stress response. Explores how legal structures can be redesigned to account for human behavioral patterns under duress.

### ⭐4 Purpose Constellation Framework

Personal development framework that maps purpose through intrinsic drivers arranged as a constellation. Journaling prompts for self-reflection, exploring core values and flow states as navigation points.

