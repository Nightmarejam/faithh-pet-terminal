#!/usr/bin/env python3
"""Index Experiment 5: The Parasitic Emergence results into ChromaDB.
Adds key findings and design documents to faithh_knowledge_base collection.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
import chromadb

# Connect to ChromaDB
try:
    client = chromadb.HttpClient(host='servicebox.taileb8c60.ts.net', port=8000)
    collection = client.get_collection('faithh_knowledge_base')
    print(f"[INDEX] Connected to ChromaDB at servicebox.taileb8c60.ts.net:8000")
    print(f"[INDEX] Collection 'faithh_knowledge_base': {collection.count()} documents")
except Exception as e:
    print(f"[ERROR] Failed to connect to ChromaDB: {e}")
    sys.exit(1)

# Documents to index
documents = [
    {
        "id": "exp5_parasitic_design",
        "content": """Experiment 5: The Parasitic Emergence — Three-Phase Offensive Evolution

Biological Insight:
Real offensive capability doesn't start with venom. It starts with resource theft.
The progression is: parasitism → system hijacking → chemical warfare.

Phase A — Energy Parasitism (ACT_SIGNAL repurposed):
- ACT_SIGNAL (0x05, cost 2/tick) drains PARASITE_DRAIN_RATE energy/tick from each adjacent agent
- Cheap, immediate fitness advantage without predator interaction
- Question: Do parasitic agents emerge and spread? How does population respond?

Phase B — Threat Redirection (system hijacking):
- Parasitic agents redirect PARASITE_REDIRECT_FRACTION of wave damage to adjacent non-parasites
- Uses neighbors as meat shields — co-opting existing defenses
- Question: Does population develop counter-strategies?

Phase C — Toxin Production (chemical warfare):
- ACT_TOXIN (0x06, cost 5/tick) provides damage reduction immune to predator adaptation
- Only viable after parasitic infrastructure established (energy surplus)
- Question: Does full offensive stack emerge?

Key Parameters:
- PARASITE_DRAIN_RATE: 3 energy/tick per victim (tuned in later runs)
- PARASITE_REDIRECT_FRACTION: 0.3 (30% damage redirected)
- PARASITE_REDIRECT_TICK: 5000 (when threat redirection activates)
- TOXIN_UNLOCK_TICK: 15000 (when ACT_TOXIN becomes available)

Success Criteria:
- PARASITISM_EMERGES: ACT_SIGNAL agents spread
- ARMS_RACE: Victims evolve counter-strategies
- HIJACKING_EMERGES: Parasites redirect wave damage
- TOXIN_EMERGES: Full offensive stack established
- ECOSYSTEM: Multiple strategies coexist

Comparison with Direct Toxin (failed approach):
- Direct toxin: 5 energy/tick, immediate cost, no intermediate benefit
- Parasitism: 2 energy/tick, cheap energy theft, creates population dynamics
- Result: Parasitism produces real boom-bust cycles; direct toxin never establishes

Date: 2026-03-25
Experiment: 5
Status: Complete — FULL_OFFENSIVE_STACK achieved""",
        "metadata": {
            "document_type": "experiment_design",
            "experiment": 5,
            "title": "Experiment 5: The Parasitic Emergence",
            "date": "2026-03-25",
            "status": "complete",
            "outcome": "full_offensive_stack",
            "tags": "alife,experiment,parasitism,offensive_evolution,boom_bust"
        }
    },
    {
        "id": "exp5_parasitic_results",
        "content": """Experiment 5 Results: The Parasitic Emergence (10K tick diagnostic)

Key Findings:
1. Parasitism emerged naturally at tick 1377 (generation 12) with adaptation only at 0.20
   - Parasite appeared while Shield still 80% effective (anticipatory emergence)
   - First offensive agent survived multiple generations (unlike direct toxin noise)

2. Classic boom-bust dynamics observed:
   - Parasites surged to 240 agents (30% of population) by tick 5000
   - Complete crash to 0 by tick 6000 — overexploitation of hosts
   - 262 parasitic kills, 350 redirect events — mechanics working
   - Lotka-Volterra predator-prey cycle in simulation

3. Three-phase progression partially demonstrated:
   - Phase A (0-5000): Parasitism established, grew to 30%
   - Phase B (5000+): Threat redirection activated, parasites crashed
   - Phase C: Toxin agent appeared at tick 9000 but no full stack yet

4. Comparison with direct toxin approach:
   - Direct toxin: First agent tick 44, gen 1 (random), 0 kills, never established
   - Parasitic: First agent tick 1377, gen 12 (selection), 262 kills, real lineage
   - Parasitic framing objectively better for emergent offensive behavior

Population Dynamics:
- Start: 327 defenders, 0 parasites
- Peak: 565 defenders, 240 parasites (30%)
- End: 513 defenders, 1 parasite, 1 toxin
- Shield effectiveness: 100% → 0% (adaptation 0.00 → 1.50)
- Outcome: FULL_OFFENSIVE_STACK (both parasite and toxin lineages present)

Technical Notes:
- Parasitic drain at 3 energy/tick too aggressive → host depletion in ~80 ticks
- Suggested tuning: PARASITE_DRAIN_RATE = 1-2 for sustainable oscillation
- Redirect mechanic functional (350 events) but needs host population management
- Adaptive predator continued adapting (1.50) even after parasite crash

Date: 2026-03-25
Experiment: 5
Ticks: 10000
Status: Complete — FULL_OFFENSIVE_STACK""",
        "metadata": {
            "document_type": "experiment_results",
            "experiment": 5,
            "title": "Experiment 5 Results: Parasitic Emergence",
            "date": "2026-03-25",
            "ticks": 10000,
            "status": "complete",
            "outcome": "full_offensive_stack",
            "tags": "alife,experiment,results,parasitism,boom_bust,population_dynamics"
        }
    },
    {
        "id": "alife_roadmap_summary",
        "content": """ALife Project Roadmap Summary — Full Vision

Project Purpose:
Build artificial life simulation exploring emergent intent — specifically when agent behavior transitions from reactive to anticipatory. Generates structured behavioral data for FAITHH's cognitive development.

Architecture:
- Gen8 MicroServer: Simulation engine (always on)
- DS220j NAS: File serving, lightweight PULSE watcher
- Windows Desktop: FAITHH deep analysis (when on)
- Data flow: Gen8 → ChromaDB → DS220j → Desktop (when available)

Experiment Ladder (Completed):
- Exp 0: Primordial Soup ✅ — Population stabilizes at ~324 agents
- Exp 1: Pressure Test ✅ — Shield trait rises 10%→100% under predator pressure
- Exp 2: Stripe Test ✅ — Dual-purpose trait dominates, environment defends complexity
- Exp 3: Anticipation Gap ✅ — Negative gaps observed, intent emergence confirmed
- Exp 4: Harmonic Interference ✅ — Red Queen dynamics, PROC_BEAT vs PROC_PREDICT
- Exp 5: Parasitic Emergence ✅ — Three-phase offensive evolution, boom-bust cycles

Key Technical Decisions:
- Process-action coupling (P0→A0, P1→A1) enables anticipation
- Wave propagation at finite speed C=0.8 col/tick creates natural variance
- Parasitic progression: energy theft → threat redirection → toxin production
- Variable-length genomes (Exp 5+) for trait complexity

FAITHH Integration Layers:
1. External Observer (current): Queries alife_lineage collection
2. Peripheral Awareness (next): PULSE sweeps include ALIFE data
3. Self-Application (goal): Apply intent scoring framework to herself

Specialist Avatar Architecture:
- IRIS (Infrastructure), VAULT (Security), MEMO (Data), LEDGER (Business)
- Physics Navi (wave mechanics, thermodynamics)
- Training pipeline: domain-filtered data → fine-tune → evaluate
- Avatar states derived from PULSE observation, not manual programming

Growth Stack:
Current: External LLM + JSONs + ChromaDB = FAITHH
6 months: Fine-tuned small model + richer context = specialized FAITHH
Eventually: Personal model (1-3B) + self-updating context = novel intelligence

Open Questions:
- Variable-length genome implementation timing
- Physics Navi development for wave interference
- Gen8 GPU (Tesla P4) for always-on embeddings
- TempleOS port (Phase 2) readiness
- Training data threshold for specialist fine-tuning

Date: 2026-03-25
Status: Phase 1 active, Experiments 0-5 complete""",
        "metadata": {
            "document_type": "roadmap",
            "project": "alife",
            "title": "ALife Project Roadmap Summary",
            "date": "2026-03-25",
            "status": "phase1_active",
            "experiments_complete": 5,
            "tags": "alife,roadmap,architecture,experiments,faithh_integration"
        }
    },
    {
        "id": "model_comparison_finding",
        "content": """FAITHH Model Comparison: Exp 5 Analysis

Context:
Query about Experiment 5 parasitic emergence results (10K tick run). Two models auto-selected for comparison.

Models Tested:
- llama3.3 (70B): Auto-selected for "complex reasoning"
- qwen25-grounded: User-selected grounded model

Findings:
Both models performed poorly due to lack of indexed Exp 5 data:
- Both hit RAG Fallback (no ChromaDB documents on Exp 5)
- Coherence: low for both responses
- Neither model understood redirect mechanic (350 events occurred)
- Both missed self-starvation mechanism details

Model Performance:
llama3.3 (70B):
- Better narrative flow, exploratory tone
- Correctly identified overexploitation cause
- Missed adaptation→shield effectiveness relationship
- No mention of threat redirection mechanic

qwen25-grounded:
- More cautious, admitted confusion about adaptation
- Explicitly asked "does higher adaptation make shields worse?"
- Better on host depletion concept
- Still missed redirect mechanic entirely

Root Cause:
Exp 5 parasitic results not indexed into faithh_knowledge_base collection.
Without grounding data, both models rely on general reasoning rather than specific context.

Resolution:
Index Exp 5 results + ALIFE_ROADMAP.md to ChromaDB.
Grounded model should outperform on mechanical questions with proper context.
The 70B model may be better for narrative synthesis once data is available.

Date: 2026-03-25
Context: Exp 5 parasitic emergence analysis
Finding: Grounded models need indexed data to demonstrate advantage""",
        "metadata": {
            "document_type": "analysis",
            "topic": "model_comparison",
            "title": "FAITHH Model Comparison: Exp 5 Analysis",
            "date": "2026-03-25",
            "context": "exp5_parasitic_emergence",
            "finding": "grounded_models_need_indexed_data",
            "tags": "faithh,model_comparison,grounding,rag_fallback"
        }
    }
]

# Index documents
for doc in documents:
    try:
        collection.add(
            documents=[doc["content"]],
            metadatas=[doc["metadata"]],
            ids=[doc["id"]]
        )
        print(f"[INDEX] Added: {doc['id']}")
    except Exception as e:
        print(f"[ERROR] Failed to add {doc['id']}: {e}")

print(f"\n[INDEX] Complete. Collection now has {collection.count()} documents")
