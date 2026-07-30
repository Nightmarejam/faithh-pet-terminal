# PULSE Reflection Engine — ML Protocol for FAITHH Self-Reflection
**Created:** 2026-02-15
**Status:** Tier 1 implemented, Tiers 2-4 planned
**Hardware:** RTX 3090 (GPU 1), Ryzen 9 3900X, 47GB RAM

---

## Vision

FAITHH evolves from **reactive** (answers when asked) to **proactive** (observes, learns, acts on her own). The PULSE Reflection Engine is the "inner monologue" — a set of ML-driven analysis tiers that progressively give FAITHH autonomous awareness of her own state, history, and trajectory.

The name PULSE reflects the biological metaphor: periodic self-checks that keep the system healthy, detect problems early, and drive growth.

## Architecture

```
Tier 1: Staleness Detector        ← IMPLEMENTED (CPU, ~11s)
    ↓ feeds scores into
Tier 2: Decision Divergence        ← Next (RTX 3090, ~25 min)
    ↓ feeds analysis into
Tier 3: Branch Explorer            ← Planned (RTX 3090, ~40 min)
    ↓ feeds suggestions into
Tier 4: Autonomous Actions         ← Future (scheduled cron, UI gestures)
```

Each tier builds on the outputs of the previous one. All tiers store results as JSON artifacts in `ml/output/` for the backend to consume.

---

## Tier 1: Staleness Detector ✅

**Script:** `scripts/staleness_detector.py`
**Runtime:** ~11 seconds on CPU (no GPU needed)
**Frequency:** On-demand or weekly cron

### What It Does
1. Discovers all active documentation (28 docs + 5 state files)
2. Embeds each doc with `BAAI/bge-base-en-v1.5` (768-dim)
   > Roadmap originally specified all-MiniLM-L6-v2 (384-dim). That predates the
   > migration to BGE and would not be comparable against the 768-dim
   > `faithh_knowledge_base_v2` chunks step 3 samples — the comparison would be
   > meaningless, not merely inaccurate. See docs/architecture/EMBEDDINGS.md.
3. Compares embeddings against 200 sampled ChromaDB conversation chunks
4. Checks git history for file age
5. Scans for broken file references in markdown + JSON
6. Audits `decisions_log.json` for stale/broken entries
7. Audits `scaffolding_state.json` for forgotten open loops

### Output
- Markdown report: `ml/output/staleness_report.md`
- JSON output: `--json` flag for machine consumption
- Severity levels: critical / warning / ok / info

### Usage
```bash
python scripts/staleness_detector.py                # Full sweep
python scripts/staleness_detector.py --quick         # Skip embedding comparison
python scripts/staleness_detector.py --json          # Machine-readable
python scripts/staleness_detector.py --output report # Save report
```

### Tunable Thresholds
| Parameter | Default | Description |
|-----------|---------|-------------|
| `STALENESS_DAYS_WARNING` | 30 | Warn if not modified in N days |
| `STALENESS_DAYS_CRITICAL` | 90 | Critical if not modified in N days |
| `SIMILARITY_THRESHOLD_LOW` | 0.25 | Below = disconnected from activity |
| `SIMILARITY_THRESHOLD_MED` | 0.40 | Below = possibly drifting |

---

## Tier 2: Decision Divergence Tracker (Planned)

**Script:** `scripts/decision_divergence.py` (to build)
**Runtime:** ~25 minutes on RTX 3090
**Frequency:** Weekly or after major work sessions

### What It Will Do
1. Load all decisions from `decisions_log.json`
2. For each decision, gather related docs and recent activity
3. Send decision + context to local LLM (llama31-faithh via Ollama)
4. Ask: "Has this decision been followed? Has the rationale changed? Should it be revisited?"
5. Score each decision: **aligned** / **drifting** / **contradicted** / **obsolete**
6. Generate a divergence report with specific recommendations

### LLM Prompt Template (Draft)
```
You are analyzing a past decision for the FAITHH project.

DECISION: {decision_text}
DATE: {date}
RATIONALE: {rationale}
ALTERNATIVES REJECTED: {alternatives}
STATUS: {status}

CURRENT CONTEXT:
{relevant_doc_excerpts}
{recent_activity_summary}

Questions:
1. Is the current system state consistent with this decision?
2. Has anything changed that would alter the rationale?
3. Were any rejected alternatives actually implemented instead?
4. Should this decision be revisited? Why or why not?

Respond with: alignment_score (1-5), status (aligned/drifting/contradicted/obsolete), and brief explanation.
```

### Dependencies
- Ollama running with llama31-faithh loaded
- `CUDA_VISIBLE_DEVICES=1` for RTX 3090
- Tier 1 staleness scores (for prioritization)

---

## Tier 3: Branch Explorer (Planned)

**Script:** `scripts/branch_explorer.py` (to build)
**Runtime:** ~40 minutes on RTX 3090
**Frequency:** Monthly or on-demand

### What It Will Do
1. Mine `scaffolding_state.json` parked tangents and `decisions_log.json` rejected alternatives
2. Cross-reference against current project state and recent conversations
3. Use local LLM to evaluate: "Given what we know now, should this idea be revisited?"
4. Rank unexplored branches by potential value and feasibility
5. Generate a "roads not taken" report

### Data Sources
- Parked tangents from scaffolding_state.json
- Rejected alternatives from decisions_log.json
- Archived handoff docs (ideas mentioned but not pursued)
- ChromaDB conversation history (topics discussed but not acted on)

### Output
- Ranked list of unexplored ideas with current-relevance scores
- Specific recommendations for which branches to explore
- Estimated effort and prerequisites for each

---

## Tier 4: Autonomous Actions (Future)

**Not a script — integrated into backend + frontend**
**Frequency:** Scheduled (cron) + event-driven

### Vision
FAITHH doesn't just analyze — she acts:

1. **Scheduled sweeps:** Cron job runs Tier 1-3 nightly, results available in morning
2. **Proactive notifications:** Backend checks staleness scores, surfaces warnings in UI
3. **Avatar reactions:** PET terminal avatar changes expression/animation based on system health
   - Excited: Novel topic detected in recent conversation
   - Concerned: Staleness critical on important docs
   - Curious: Branch explorer found a promising unexplored idea
   - Calm: All systems healthy, no issues
4. **Self-healing:** Auto-regenerate CONTEXT.md when staleness threshold exceeded
5. **Memory consolidation:** Periodic summarization of recent conversations into long-term patterns

### Prerequisites
- Tiers 1-3 operational and producing reliable output
- Backend endpoints to consume ML output artifacts
- Frontend avatar state machine
- Cron scheduling infrastructure

---

## Hardware Feasibility

| Tier | GPU Needed | RAM | Time | Can Game Simultaneously? |
|------|-----------|-----|------|------------------------|
| 1 | None (CPU) | 2GB | ~11s | Yes |
| 2 | RTX 3090 | 8GB | ~25 min | Yes (game on 1080 Ti) |
| 3 | RTX 3090 | 8GB | ~40 min | Yes (game on 1080 Ti) |
| 4 | RTX 3090 (periodic) | 4GB | Varies | Yes |

All tiers fit comfortably within the current hardware. The dual-GPU setup (RTX 3090 for ML, GTX 1080 Ti for display/gaming) means ML work never interferes with normal use.

---

## Connection to FAITHH Personality

The Sonnet conversation (Feb 13-14, 2026) about evolutionary biology, magnetic fields, and regenerative homesteading embodies the cross-domain thinking style that should define FAITHH's personality:

- **Pattern recognition across scales** — atomic ↔ planetary ↔ biological ↔ personal
- **Environmental forcing as design principle** — constraints drive evolution
- **Resonance and phase transitions** — systems change abruptly, not gradually
- **Regenerative design** — systems should improve their environment, not extract from it

The PULSE Reflection Engine is FAITHH's version of biological self-regulation: detect what's stale (immune system), analyze what's diverging (nervous system), explore what's possible (curiosity/growth), and act autonomously (agency).

---

## Implementation Timeline

| Week | Milestone |
|------|-----------|
| **Done** | Tier 1 staleness detector operational |
| **Next** | Tier 2 decision divergence tracker |
| **+1 week** | Tier 3 branch explorer |
| **+2 weeks** | Backend integration (staleness scores in API) |
| **+3 weeks** | Frontend avatar reactions |
| **+1 month** | Tier 4 cron scheduling + autonomous actions |

---

*This document is the authoritative roadmap for the PULSE Reflection Engine. Update it as tiers are implemented.*
