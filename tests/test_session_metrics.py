#!/usr/bin/env python3
"""Unit tests for FAITHH session metrics layer (no live Chroma required)."""

from __future__ import annotations

import json
from unittest.mock import Mock

import pytest

import backend.session_metrics as sm


def test_session_open_schema_valid():
    wr = {
        "services": {
            "chat": {"active": True},
            "rag": {"active": True},
            "genomic": {"active": False},
            "pulse": {"active": True, "ollama_reachable": True},
        }
    }
    sig = {"ts": __import__("time").time(), "ran": True, "best_distance": 0.4, "low_confidence": False, "hit_count": 3}
    doc = sm.build_session_open_document(
        "session_test_open",
        workspace_registry=wr,
        rag_signal=sig,
        rag_threshold=0.55,
        rag_stale_seconds=900.0,
        primary_provider="ollama",
        ollama_model="m:latest",
        kv_cache_type="q8_0",
        ollama_reachable=True,
        chroma_connected=True,
        collection_size=1200,
    )
    assert doc["id"] == "session_test_open"
    assert doc["timestamp_close"] is None
    assert doc["duration_seconds"] is None
    assert doc["services_active"]["chat"] is True
    assert doc["rag_signal"]["collection_size"] == 1200
    assert doc["session_outcome"]["turns"] == 0
    assert doc["metadata"]["category"] == "session_metrics"
    assert doc["metadata"]["document_type"] == "operational_telemetry"


def test_session_close_merges_outcome():
    coll = Mock()
    open_doc = sm.build_session_open_document(
        "session_close_test",
        workspace_registry={"services": {"chat": {"active": True}, "rag": {"active": True}, "genomic": {"active": False}, "pulse": {"active": True}}},
        rag_signal={"ran": False},
        rag_threshold=0.55,
        rag_stale_seconds=900.0,
        primary_provider="ollama",
        ollama_model="x:latest",
        kv_cache_type="f16",
        ollama_reachable=True,
        chroma_connected=True,
        collection_size=10,
    )
    coll.get.return_value = {"documents": [json.dumps(open_doc)]}

    outcome = {
        "turns": 2,
        "rag_used_count": 1,
        "system_data_attached_count": 1,
        "stream_used": True,
        "providers_used": ["ollama", "groq"],
        "avg_latency_ms": 1500.0,
        "max_latency_ms": 2000.0,
        "fallback_count": 1,
        "stall_count": 0,
        "error_count": 0,
    }
    sm.record_session_close(coll, "session_close_test", outcome)
    coll.upsert.assert_called_once()
    args, kwargs = coll.upsert.call_args
    updated = json.loads(kwargs["documents"][0])
    assert updated["session_outcome"]["turns"] == 2
    assert updated["session_outcome"]["avg_latency_ms"] == 1500.0
    assert updated["timestamp_close"] is not None
    assert updated["duration_seconds"] is not None
    assert updated["flags"]["provider_fallback"] is True


def test_accumulator_lru_eviction(monkeypatch):
    monkeypatch.setattr(sm, "ACC_MAX", 3)
    sm._accumulators.clear()
    for i in range(4):
        sm.ensure_accumulator(f"s{i}")
    assert "s0" not in sm._accumulators
    assert sm.accumulator_size() == 3


def test_metrics_summary_endpoint_shape():
    synthetic = [
        {
            "timestamp_open": "2026-04-08T12:00:00+00:00",
            "rag_signal": {"best_distance": 0.5},
            "session_outcome": {"turns": 2, "avg_latency_ms": 1000, "fallback_count": 0, "stall_count": 0, "rag_used_count": 1},
            "flags": {"rag_low_confidence": False},
            "metadata": {"date": "2026-04-08", "category": "session_metrics"},
        },
        {
            "timestamp_open": "2026-04-09T12:00:00+00:00",
            "rag_signal": {"best_distance": 0.9},
            "session_outcome": {"turns": 1, "avg_latency_ms": 2000, "fallback_count": 1, "stall_count": 1, "rag_used_count": 0},
            "flags": {"rag_low_confidence": True},
            "metadata": {"date": "2026-04-09", "category": "session_metrics"},
        },
    ]
    summary = sm.compute_summary_from_parsed_sessions(synthetic, window_days=7, limit=100)
    assert summary["sessions_total"] == 2
    assert "avg_latency_ms" in summary
    assert "trend" in summary
    assert "provider_distribution" in summary
    assert "health_score" in summary


def test_health_score_range():
    assert 0.0 <= sm.health_score_from_rates(1.0, 1.0, 1.0) <= 100.0
    assert sm.health_score_from_rates(0.0, 0.0, 0.0) == 100.0
    mid = sm.health_score_from_rates(0.25, 0.1, 0.2)
    assert 0.0 <= mid <= 100.0
    # (1-0.1)*40 + (1-0.2)*35 + (1-0.25)*25 = 36 + 28 + 18.75
    assert abs(mid - 82.75) < 0.01


def test_flush_endpoint_requires_dev_mode(monkeypatch):
    """flush-session returns 403 when not localhost and FAITHH_DEV_MODE unset."""
    monkeypatch.delenv("FAITHH_DEV_MODE", raising=False)
    import faithh_professional_backend_fixed as backend

    app = backend.app
    with app.test_client() as c:
        resp = c.post(
            "/api/metrics/flush-session",
            json={"session_id": "test"},
            environ_base={"REMOTE_ADDR": "10.0.0.1"},
        )
        assert resp.status_code == 403
