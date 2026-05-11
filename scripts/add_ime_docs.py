#!/usr/bin/env python3
"""Add IME docs."""
import chromadb
from datetime import datetime

client = chromadb.HttpClient(host="192.158.1.243", port=8000)
collection = client.get_collection(name="faithh_knowledge_base")

docs = [
    {
        "id": "ime_readme",
        "source": "ime/README.md",
        "content": """
Inner Monologue Engine (IME)

High-reasoning companion intelligence. The journal's inner voice.

What This Is:
The IME reads accumulated journal entries and synthesizes patterns across
life domains. It is the long-horizon counterpart to FAITHH:
- FAITHH: task coherence, project context, immediate memory
- IME: reflective synthesis, life pattern recognition, artificial life seed

Architecture Foundation:
- Resonance Transformer Architecture
- Resonance Gating: refuses premature synthesis until data is sufficient
- Journal-grounded: fed by ml/output/journal/ entries, not task logs

Current Status:
v0.1.0 — Scaffold only. Reads journal entries, evaluates resonance level.
No synthesis capability yet. That comes after 3+ months of journal data.
        """
    },
    {
        "id": "ime_architecture",
        "source": "ime/docs/ARCHITECTURE.md",
        "content": """
IME Architecture

The Inner Monologue Engine architecture is designed for high-reasoning
companion intelligence that serves as the journal's inner monologue.

Key architectural principles:
- Local-first operation on modest hardware
- Transparent reasoning with visible thought processes
- Resonance-based quality control
- Journal-grounded knowledge synthesis

Technical components:
- Resonance Transformer core
- Pattern recognition layers
- Synthesis gating mechanisms
- Memory consolidation systems

The architecture supports the emergence of artificial life patterns
from authentic human reasoning captured in journal entries.
        """
    }
]

for doc in docs:
    collection.upsert(
        ids=[doc["id"]],
        documents=[doc["content"]],
        metadatas=[{
            "source": doc["source"],
            "category": "ime_scaffold",
            "project": "inner_monologue_engine",
            "indexed_by": "add_ime_docs.py",
            "timestamp": datetime.now().isoformat()
        }]
    )
    print(f"Added: {doc['id']}")

print(f"\nCollection now has: {collection.count()} documents")
