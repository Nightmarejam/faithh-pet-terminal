"""
Fusion weights for Phase 2 perf metrics only.

Kept separate from faithh_professional_backend_fixed.py so the helper is always
importable early (avoids any ordering/closure edge cases around /api/chat metrics).
Mirrors backend.parallel_chip_engine.DEFAULT_CHIP_WEIGHTS without importing it.
"""

from __future__ import annotations

_CHIP_WEIGHTS_FOR_METRICS: dict[str, float] = {
    "rag_search": 1.0,
    "rag_search_fallback": 1.0,
    "scaffolding": 0.9,
    "decision_logs": 0.85,
    "decisions": 0.85,
    "project_state": 0.8,
    "project": 0.8,
    "constella": 0.75,
    "conversation_history": 0.6,
    "self_awareness": 0.5,
    "life_map": 0.55,
    "project_structure": 0.5,
    "structure": 0.5,
    "filesystem": 0.4,
}


def get_chip_weights(integrations_used):
    # Logic for Humans: Phase 2 perf rows store one float per activated integration; unknown labels default to 1.0.
    """Map integration names (from context assembly) to fusion weights for metrics only."""
    if not integrations_used:
        return {}
    out: dict[str, float] = {}
    for name in integrations_used:
        key = str(name)
        out[key] = float(_CHIP_WEIGHTS_FOR_METRICS.get(key, 1.0))
    return out
