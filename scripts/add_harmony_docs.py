#!/usr/bin/env python3
"""Add key harmony docs summaries."""
import chromadb
from datetime import datetime

client = chromadb.HttpClient(host="192.158.1.243", port=8000)
collection = client.get_collection(name="faithh_knowledge_base")

docs = [
    {
        "id": "harmony_resonance_transformer",
        "source": "projects/constella-framework/harmony/docs/resonance_transformer_architecture_spec_v1.0.0.md",
        "content": """
Resonance Transformer Architecture

The Resonance Transformer is a specialized architecture for the Inner Monologue Engine
that enables pattern recognition across temporal scales while maintaining coherence.

Key features:
- Multi-scale temporal attention mechanisms
- Resonance-based memory consolidation
- Adaptive pattern synthesis
- Cross-domain coherence detection

The architecture supports the IME's ability to identify meaningful patterns
in journal entries and synthesize them into coherent insights.
        """
    },
    {
        "id": "harmony_ai_bridge",
        "source": "projects/constella-framework/harmony/docs/harmony_ai_bridge_v1.0.0.md",
        "content": """
Harmony AI Bridge

The Harmony AI Bridge provides the interface between FAITHH (task coherence)
and the IME (reflective synthesis).

Bridge functions:
- Context transfer between systems
- Coherence validation across domains
- Memory consolidation pathways
- Synthesis triggering mechanisms

The bridge ensures that task-oriented insights from FAITHH inform
the IME's reflective synthesis while maintaining system boundaries.
        """
    },
    {
        "id": "harmony_framework",
        "source": "projects/constella-framework/harmony/docs/harmony_framework_complete_v4.0.0.md",
        "content": """
Harmony Framework Complete v4.0.0

The Harmony Framework provides a comprehensive system for multi-modal creativity,
coherence detection, and real-time feedback.

Core components:
- Coherence sensing algorithms
- Multi-modal integration layers
- Real-time feedback systems
- Documentation framework

The framework serves as the foundation for the Constella project's
governance and creative applications.
        """
    }
]

for doc in docs:
    collection.upsert(
        ids=[doc["id"]],
        documents=[doc["content"]],
        metadatas=[{
            "source": doc["source"],
            "category": "ime_architecture",
            "project": "inner_monologue_engine",
            "indexed_by": "add_harmony_docs.py",
            "timestamp": datetime.now().isoformat()
        }]
    )
    print(f"Added: {doc['id']}")

print(f"\nCollection now has: {collection.count()} documents")
