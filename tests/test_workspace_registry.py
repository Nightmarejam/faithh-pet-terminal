"""GET /api/workspace/registry — Canvas service registry (live backend)."""

import json

import pytest
import requests

BASE_URL = "http://localhost:5557"


def _backend_available():
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=3)
        return r.status_code == 200
    except Exception:
        return False


skipif_no_backend = pytest.mark.skipif(
    not _backend_available(),
    reason="FAITHH backend not running on localhost:5557",
)


@skipif_no_backend
def test_workspace_registry_live():
    r = requests.get(f"{BASE_URL}/api/workspace/registry", timeout=15)
    if r.status_code == 404:
        pytest.skip("Backend running without GET /api/workspace/registry — restart after pulling Canvas Phase 3")
    assert r.status_code == 200
    data = r.json()
    assert data.get("success") is True
    assert "services" in data
    assert "navigation" in data
    for key in ("chat", "rag", "genomic", "pulse", "diagnostics"):
        assert key in data["services"]
    assert data["services"]["chat"].get("active") is True
    assert data["services"]["diagnostics"].get("href") == "/cockpit"
    nav = data["navigation"]
    assert isinstance(nav, list) and len(nav) >= 1
    assert any(n.get("target_page") == "chatPage" for n in nav)
