#!/usr/bin/env python3
"""Add resonance gating content as a single chunk."""
import chromadb
from datetime import datetime

client = chromadb.HttpClient(host="192.158.1.243", port=8000)
collection = client.get_collection(name="faithh_knowledge_base")

# Key resonance gating content
content = """
Resonance Gating Architecture

Resonance gating prevents premature synthesis in the Inner Monologue Engine (IME). 
It ensures that synthesis only occurs when sufficient data has accumulated to support 
meaningful pattern recognition.

Key principles:
- Data sufficiency threshold must be met before synthesis
- Quality gates prevent hallucinated connections
- Temporal coherence requires consistent patterns over time
- Resonance levels indicate confidence in synthesis readiness

The resonance gating mechanism serves as the IME's quality control system,
ensuring that artificial life patterns emerge from genuine data relationships
rather than spurious correlations.
"""

collection.upsert(
    ids=["harmony_resonance_gating_summary"],
    documents=[content],
    metadatas=[{
        "source": "projects/constella-framework/harmony/docs/resonance_gating_architecture_note_v1.0.md",
        "category": "ime_architecture",
        "project": "inner_monologue_engine",
        "indexed_by": "add_resonance_gating.py",
        "timestamp": datetime.now().isoformat()
    }]
)

print("Added resonance gating summary")
print(f"Collection now has: {collection.count()} documents")
