#!/usr/bin/env python3
"""Index ALIFE_FINDINGS.md into ChromaDB as a living synthesis document."""
import chromadb

CHROMADB_HOST = "servicebox.taileb8c60.ts.net"
CHROMADB_PORT = 8000
COLLECTION_NAME = "faithh_knowledge_base"

client = chromadb.HttpClient(host=CHROMADB_HOST, port=CHROMADB_PORT)
collection = client.get_collection(COLLECTION_NAME)

with open("/home/jonat/ai-stack/docs/constella_stress_tests/ALIFE_FINDINGS.md") as f:
    full_text = f.read()

# Index as three chunks — patterns, per-experiment findings, and design decisions
documents = [
    {
        "id": "alife_findings_cross_patterns",
        "text": """ALife Experiment Synthesis — Cross-Experiment Patterns (Living Document)

Five consistent patterns emerged across Exps 0–6 that were not designed for:

Pattern 1: Collapse thresholds are ratios, not parameters.
No single parameter value caused collapse. Collapse occurred when the ratio between
two competing rates crossed a threshold: adaptation speed vs counter-strategy
establishment time (Exp 5), overshoot rate vs carrying capacity (Exp 6).
Governance failure parameters are always relational, not absolute.

Pattern 2: Novel strategies emerge in order — extraction before destruction.
Parasitism appeared at tick 57. Toxin at tick 1,840. Low-cost extraction is always
the first-order dysfunction. High-cost destruction is second-order and only emerges
once extraction is normalized. Monitor extraction metrics as early warning.

Pattern 3: Unconditional support at scale removes selection pressure.
98% floor utilization means the floor is not a safety net — it is the system floor
for everyone. Any sufficiently accessible resource will reach full utilization.
Accessibility thresholds must exist. The threshold IS the filter.

Pattern 4: Anticipation emerges from memory + threshold, not intelligence.
8-byte genome, one pattern buffer, one threshold opcode produced 89.2% anticipatory
behavior and 74 stable coexisting rhythms with no communication.
Anticipatory governance capacity comes from recorded history plus clear thresholds.

Pattern 5: Environmental heterogeneity produces functional diversity without design.
Three spatial zones produced three distinct stable strategy distributions without
any niche assignment. Allow heterogeneity, don't enforce uniformity.""",
        "metadata": {
            "domain": "alife",
            "source_type": "synthesis_document",
            "document": "ALIFE_FINDINGS.md",
            "section": "cross_experiment_patterns",
            "experiments_covered": "exp0,exp1,exp3,exp4,exp5,exp6",
            "date": "2026-03-29",
            "quality_score": 0.95
        }
    },
    {
        "id": "alife_findings_key_results",
        "text": """ALife Experiment Key Results — Earned Findings Only (Living Document)

Exp 3 (Anticipation Gap): 89.2% anticipatory shielding, 74 stable rhythmic patterns,
no inter-agent communication. Anticipation from memory + threshold alone.
EARNED: Distributed temporal coordination without signaling. Pattern diversity is stable.

Exp 4 (Harmonic Interference): Spatial cognitive stratification into 3 niches.
Interference zone (highest complexity) produced most sophisticated agents — not fewest.
EARNED: Complexity zones select for capability, not avoidance. Don't simplify complex zones.

Exp 5 (Parasitic Emergence, drain=1.5): Collapsed tick 10,039.
Parasitism tick 57 (gen 2). Toxin tick 1,840 (gen 20). Neither reached critical mass.
EARNED: Extraction is always first-order under stress. The collapse threshold is the ratio
between adaptation speed and counter-strategy establishment time, not the drain rate itself.

Exp 6 (UCF Floor, unconditional): Collapsed tick 7,410 — 2,629 ticks EARLIER than Exp 5.
Floor rider peak: 833/848 agents (98%). Commons pool 60% full at collapse.
EARNED: Unconditional floor caused population overshoot. Carrying capacity, not resource
depletion, was the binding constraint. Intervention accelerated the outcome it was designed
to prevent. UCF without participation gate = perverse intervention effect.

Discarded (noise, not signal):
exp8_cultural_transmission: 16,499 protocols, 0 transmissions. Mechanics not working.
multi_generational: survival_probability ~0 across all organisms. No real selection.
environmental_adaptation: genomic biasing output without functional dynamics.""",
        "metadata": {
            "domain": "alife",
            "source_type": "synthesis_document",
            "document": "ALIFE_FINDINGS.md",
            "section": "key_results",
            "experiments_covered": "exp3,exp4,exp5,exp6",
            "date": "2026-03-29",
            "quality_score": 0.95
        }
    },
    {
        "id": "alife_findings_design_decisions",
        "text": """ALife to Constella — Earned Design Decisions (Living Document)

These Constella design implications are labeled EARNED (not predicted before the run)
vs INTERPRETED (asserted before the run, confirmed by result).

[EARNED] UCF must be conditional, not unconditional.
Source: Exp 6 unconditional floor caused overshoot and earlier collapse.
Decision: UCF eligibility requires minimum participation threshold.
Participants below threshold enter Penumbra zone before losing floor access.
UCF and Penumbra Accord are structurally coupled — not independent mechanisms.

[EARNED] Early warning signal is extraction, not crisis.
Source: Exp 5 parasitism at tick 57, long before any other dysfunction.
Decision: Constella monitoring should track extraction behavior (free-riding,
voice monopolization, attention harvesting) as primary early warning metric.

[EARNED] Civic Tome amendment history IS the anticipatory mechanism.
Source: Exp 3 anticipation from pattern memory + threshold alone.
Decision: The value of the Civic Tome is not symbolic — it is the literal
pattern memory that enables collective anticipatory governance.

[EARNED] Don't specify participation modes — allow environmental heterogeneity.
Source: Exp 4 three stable niches from physical environment structure alone.
Decision: Constella communities in different contexts will naturally develop
different participation modes. Design for heterogeneity, not uniformity.

[INTERPRETED] Governance complexity must scale at most as fast as participant capability.
Source: Exp 5 adaptation speed ratio. Connection is argued, not proven.

[INTERPRETED] Natural carrying capacity emerges from resource density, not membership caps.
Source: Exp 0 logistic growth to ~324 agents. Connection is plausible, not demonstrated.

Next experiment pre-registered hypothesis (Exp 7):
Gate interval of 500–1000 ticks will prevent overshoot without excluding genuinely
stressed agents. Population will stabilize lower than Exp 5 but not collapse.""",
        "metadata": {
            "domain": "constella",
            "source_type": "synthesis_document",
            "document": "ALIFE_FINDINGS.md",
            "section": "design_decisions",
            "constella_principles": "UCF,Penumbra,Civic_Tome,Auctor",
            "date": "2026-03-29",
            "quality_score": 0.95
        }
    }
]

collection.upsert(
    ids=[d["id"] for d in documents],
    documents=[d["text"] for d in documents],
    metadatas=[d["metadata"] for d in documents]
)
print(f"Indexed {len(documents)} ALIFE_FINDINGS sections to ChromaDB")
for d in documents:
    print(f"  {d['id']}")
