"""Unit tests for GET /api/health/gpu-hint payload builder (no Flask server required)."""

import pytest

from backend.llm_providers import build_gpu_hint_payload


@pytest.fixture
def gpu_env(monkeypatch):
    monkeypatch.setenv("CUDA_DEVICE_ORDER", "PCI_BUS_ID")
    monkeypatch.setenv("FAITHH_CUDA_PHYSICAL_DEVICE", "1")
    monkeypatch.setenv("FAITHH_STRICT_LLM_GPU", "1")
    monkeypatch.setenv("CUDA_VISIBLE_DEVICES", "1")
    yield


def test_gpu_hint_match(gpu_env):
    p = build_gpu_hint_payload()
    assert p["alignment"] == "MATCH"
    assert p["faithh_cuda_physical_device"] == "1"
    assert p["cuda_visible_devices"] == "1"
    assert p["strict_gpu_policy"] is True
    assert "ollama_note" in p
    assert "3090" in (p.get("ui_primary_gpu") or "")


def test_gpu_hint_mismatch(monkeypatch):
    monkeypatch.setenv("CUDA_DEVICE_ORDER", "PCI_BUS_ID")
    monkeypatch.setenv("FAITHH_CUDA_PHYSICAL_DEVICE", "1")
    monkeypatch.setenv("FAITHH_STRICT_LLM_GPU", "1")
    monkeypatch.setenv("CUDA_VISIBLE_DEVICES", "0")
    p = build_gpu_hint_payload()
    assert p["alignment"] == "MISMATCH"
    assert "WSL" in p["message"] or "FAITHH_CUDA" in p["message"]


def test_gpu_hint_respects_physical_override(monkeypatch):
    monkeypatch.setenv("CUDA_DEVICE_ORDER", "PCI_BUS_ID")
    monkeypatch.setenv("FAITHH_CUDA_PHYSICAL_DEVICE", "0")
    monkeypatch.setenv("FAITHH_STRICT_LLM_GPU", "1")
    monkeypatch.setenv("CUDA_VISIBLE_DEVICES", "0")
    p = build_gpu_hint_payload()
    assert p["alignment"] == "MATCH"
    assert p["faithh_cuda_physical_device"] == "0"
