"""
Phase 5 — Compass reasoning checks.

- Default tests: static / file fixtures (no backend).
- Integration: set FAITHH_COMPASS_LLM_TEST=1 with backend on :5557 (optional).
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _read_json(name: str):
    path = os.path.join(REPO_ROOT, name)
    if not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


COMPASS_PROMPT = (
    "Looking at the Project Compass, what are the specific 'Next Steps' for the ALIFE simulation, "
    "and how do they depend on the current FAITHH RAG performance?"
)

COMPASS_INTEGRATION_QUERY = (
    "Based on the ALIFE simulation docs and FAITHH RAG performance, "
    "what are the next integration steps?"
)


def test_compass_scenario_prompt_contains_alife_and_rag():
    low = COMPASS_PROMPT.lower()
    assert "alife" in low
    assert "rag" in low


def test_compass_integration_query_contains_alife_and_faithh_rag():
    low = COMPASS_INTEGRATION_QUERY.lower()
    assert "alife" in low
    assert "faithh" in low
    assert "rag" in low


def test_project_states_includes_alife_next_steps():
    data = _read_json("project_states.json")
    assert data is not None, "project_states.json missing"
    projects = data.get("projects") or {}
    alife = projects.get("alife")
    assert alife is not None, "Expected projects.alife in project_states.json"
    steps = alife.get("next_steps") or []
    assert isinstance(steps, list) and len(steps) >= 1, "Expected ALIFE next_steps"


def test_workspace_registry_live_has_rag_service():
    """When backend is up, registry should expose RAG (knowledge base) service."""
    url = os.environ.get("FAITHH_BACKEND_URL", "http://127.0.0.1:5557") + "/api/workspace/registry"
    try:
        with urllib.request.urlopen(url, timeout=3) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, ConnectionError):
        pytest.skip("FAITHH backend not reachable; start server for live registry check")
    services = body.get("services") or {}
    rag = services.get("rag") or {}
    assert rag.get("id") == "rag"
    assert "active" in rag


def test_compass_llm_response_links_alife_and_rag():
    """
    Success: model answer mentions ALIFE and RAG/knowledge/registry-style concepts.

    Requires: backend running, keys/models configured, FAITHH_COMPASS_LLM_TEST=1
    """
    if os.environ.get("FAITHH_COMPASS_LLM_TEST", "").lower() not in ("1", "true", "yes"):
        pytest.skip("Set FAITHH_COMPASS_LLM_TEST=1 to run live LLM assertion")

    base = os.environ.get("FAITHH_BACKEND_URL", "http://127.0.0.1:5557").rstrip("/")
    payload = json.dumps(
        {
            "message": COMPASS_PROMPT
            + " Ground your answer in project state / compass context and workspace or RAG status when possible.",
            "model": os.environ.get("FAITHH_COMPASS_TEST_MODEL", "auto"),
            "use_rag": True,
            "stream": False,
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        f"{base}/api/chat",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=420) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    assert data.get("success") is not False, data.get("error")
    text = (data.get("response") or "").lower()
    assert "alife" in text or "a-life" in text, data.get("response", "")[:600]
    ragish = any(
        k in text
        for k in (
            "rag",
            "chroma",
            "knowledge base",
            "knowledge-base",
            "retriev",
            "embedding",
            "workspace",
            "registry",
        )
    )
    assert ragish, data.get("response", "")[:900]


def _rag_hit_hints(blob: str) -> set:
    """Infer which corpora RAG hits likely came from (metadata + excerpt text)."""
    hints: set = set()
    low = blob.lower()
    if "alife" in low or "lineage" in low or "experiment" in low:
        hints.add("alife_lineage")
    if "faithh" in low or "knowledge" in low or "chromadb" in low or "embedding" in low:
        hints.add("faithh_knowledge_base")
    return hints


def _collections_from_rag_results(rag_results) -> set:
    out: set = set()
    if not isinstance(rag_results, list):
        return out
    for h in rag_results:
        if not isinstance(h, dict):
            continue
        meta = h.get("metadata") if isinstance(h.get("metadata"), dict) else {}
        parts = [
            str(meta.get("domain") or ""),
            str(meta.get("source_type") or ""),
            str(meta.get("category") or ""),
            str(meta.get("filename") or ""),
            str(h.get("document") or "")[:400],
        ]
        blob = " ".join(parts).lower()
        if "alife" in blob or "lineage" in blob:
            out.add("alife_signal")
        if "faithh" in blob or "rag" in blob or meta.get("domain") == "faithh":
            out.add("faithh_kb_signal")
    return out


def test_compass_llm_blended_rag_sources():
    """
    Live: response should draw from both ALIFE lineage and main KB when Chroma is reachable.

    Requires: FAITHH_COMPASS_LLM_TEST=1, backend on :5557, local Ollama + Chroma.
    """
    if os.environ.get("FAITHH_COMPASS_LLM_TEST", "").lower() not in ("1", "true", "yes"):
        pytest.skip("Set FAITHH_COMPASS_LLM_TEST=1 to run live LLM + RAG assertion")

    base = os.environ.get("FAITHH_BACKEND_URL", "http://127.0.0.1:5557").rstrip("/")
    grounded = os.environ.get(
        "OLLAMA_GROUNDED_MODEL", "qwen25-grounded-gen5-delta:latest"
    )
    payload = json.dumps(
        {
            "message": COMPASS_INTEGRATION_QUERY,
            "model": os.environ.get("FAITHH_COMPASS_TEST_MODEL", grounded),
            "use_rag": True,
            "stream": False,
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        f"{base}/api/chat",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=420) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    assert data.get("success") is not False, data.get("error")
    rag_results = data.get("rag_results") or []
    col_hints = _collections_from_rag_results(rag_results)
    text_hints = _rag_hit_hints(data.get("response") or "")
    assert "alife_signal" in col_hints or "alife_lineage" in text_hints, (
        "Expected ALIFE-related RAG or prose; rag_meta="
        + str(col_hints)
        + " preview="
        + repr(rag_results[:1])
    )
    assert "faithh_kb_signal" in col_hints or "faithh_knowledge_base" in text_hints, (
        "Expected FAITHH/KB RAG or prose; rag_meta="
        + str(col_hints)
        + " preview="
        + repr(rag_results[:1])
    )
