#!/usr/bin/env python3

def is_ping_like_prompt(text: str) -> bool:
    """True for trivial probes where we should NOT run chips/RAG or call any model."""
    if text is None:
        return True

    raw = str(text).strip().lower()
    if not raw:
        return True

    # Normalize away punctuation/whitespace so `ping...`, `ping?`, etc. all match.
    norm = "".join(ch for ch in raw if ch.isalnum())

    if norm in {"ping", "pong", "health", "status", "heartbeat", "ready", "ok"}:
        return True

    # Treat anything that *starts* with ping as a probe (pinglike, pingtest, ping123, etc.)
    if norm.startswith("ping"):
        return True

    return False

test_msg = "What were the key findings from Experiment 5 parasitic emergence?"
print(f"Message: {test_msg}")
print(f"Is ping: {is_ping_like_prompt(test_msg)}")
print(f"Has content: {bool(test_msg.strip())}")
