#!/usr/bin/env python3
"""Test coherence sensor integration"""
import pytest
import requests

BASE_URL = "http://localhost:5557"


def _backend_available():
    try:
        return requests.get(f"{BASE_URL}/health", timeout=3).status_code == 200
    except Exception:
        return False


skipif_no_backend = pytest.mark.skipif(
    not _backend_available(),
    reason="FAITHH backend not running"
)


@skipif_no_backend
def test_chat_returns_response():
    """Chat endpoint returns a valid response with RAG."""
    r = requests.post(f"{BASE_URL}/api/chat", json={
        "message": "What are the four mechanisms in the Harmony-AI Bridge?",
        "model": "gemini",
        "use_rag": True
    }, timeout=60)
    # Accept 200 or 502/503 (provider temporarily unavailable)
    if r.status_code in (502, 503):
        pytest.skip("LLM provider temporarily unavailable")
    assert r.status_code == 200
    data = r.json()
    assert "response" in data
    assert len(data["response"]) > 0


@skipif_no_backend
def test_rag_used_when_enabled():
    """RAG flag is honored when use_rag=True."""
    r = requests.post(f"{BASE_URL}/api/chat", json={
        "message": "Tell me about FAITHH project structure",
        "model": "gemini",
        "use_rag": True
    }, timeout=60)
    if r.status_code in (502, 503):
        pytest.skip("LLM provider temporarily unavailable")
    assert r.status_code == 200
    data = r.json()
    # rag_used may be True or integrations_used may include rag
    assert data.get("rag_used") or "rag" in str(data.get("integrations_used", [])).lower()
