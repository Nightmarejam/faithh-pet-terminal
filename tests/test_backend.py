#!/usr/bin/env python3
"""
Backend endpoint tests for FAITHH
Requires backend running on localhost:5557
"""

import pytest
import requests
import json

BASE_URL = "http://localhost:5557"


def _backend_available():
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=3)
        return r.status_code == 200
    except Exception:
        return False


skipif_no_backend = pytest.mark.skipif(
    not _backend_available(),
    reason="FAITHH backend not running on localhost:5557"
)


@skipif_no_backend
def test_health_endpoint():
    r = requests.get(f"{BASE_URL}/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "healthy"


@skipif_no_backend
def test_plc_state_endpoint():
    r = requests.get(f"{BASE_URL}/api/plc/state")
    assert r.status_code == 200
    data = r.json()
    assert "current_state" in data
    assert "faithh_status" in data
    fs = data["faithh_status"]
    assert fs.get("success") is not False
    assert "services" in fs


@skipif_no_backend
def test_api_status_legacy_alias():
    """Thin alias; ecosystem clients should use /api/plc/state."""
    r = requests.get(f"{BASE_URL}/api/status")
    assert r.status_code == 200
    data = r.json()
    assert "services" in data


@skipif_no_backend
def test_models_endpoint():
    r = requests.get(f"{BASE_URL}/api/models")
    assert r.status_code == 200
    data = r.json()
    assert "models" in data
    assert len(data["models"]) > 0


@skipif_no_backend
def test_pulse_state_endpoint():
    r = requests.get(f"{BASE_URL}/api/pulse/state")
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    assert "avatar" in data
    assert "mood" in data["avatar"]


@skipif_no_backend
def test_journal_endpoint():
    r = requests.get(f"{BASE_URL}/api/journal")
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True


@skipif_no_backend
def test_manifest_json():
    r = requests.get(f"{BASE_URL}/manifest.json")
    assert r.status_code == 200
    data = r.json()
    assert data["short_name"] == "FAITHH"


@skipif_no_backend
def test_chat_endpoint():
    r = requests.post(f"{BASE_URL}/api/chat", json={
        "message": "ping",
        "model": "gemini"
    }, timeout=60)
    assert r.status_code == 200
    data = r.json()
    assert "response" in data or "error" in data
