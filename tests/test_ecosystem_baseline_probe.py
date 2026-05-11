"""Tests for scripts/ecosystem_baseline_probe.py (mocked HTTP; no live backend)."""
from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from scripts.ecosystem_baseline_probe import (
    extract_llm_latency_ms,
    run_probe,
    summarize_health_for_probe,
    summarize_plc_for_probe,
)


def test_extract_llm_latency_ms():
    assert extract_llm_latency_ms({}) is None
    assert extract_llm_latency_ms({"routing_debug": {}}) is None
    assert (
        extract_llm_latency_ms(
            {"routing_debug": {"llm_routing": {"latency_ms": 298.5}}}
        )
        == 298.5
    )


def test_summarize_plc_for_probe():
    plc = {
        "current_state": "idle",
        "recent_component_changes": [{"id": "x"}],
        "faithh_status": {
            "version": "v4",
            "current_model": {"name": "m", "provider": "Groq"},
            "services": {
                "chromadb": {"reachable": True, "documents": 100, "host": "http://h:8000"},
                "ollama": {"reachable": True, "count": 2},
            },
        },
    }
    s = summarize_plc_for_probe(plc)
    assert s["faithh_version"] == "v4"
    assert s["current_model"]["name"] == "m"
    assert s["chromadb"]["documents"] == 100
    assert s["recent_component_changes_count"] == 1


def test_summarize_health_for_probe():
    h = {
        "overall_health": {"status": "healthy", "issues": []},
        "services": {
            "connection_monitor": {
                "monitoring_active": True,
                "overall_status": "healthy",
                "required_unhealthy_services": 0,
            }
        },
    }
    s = summarize_health_for_probe(h)
    assert s["overall_status"] == "healthy"
    assert s["required_unhealthy_services"] == 0


def _resp(code: int, data: dict) -> MagicMock:
    r = MagicMock()
    r.status_code = code
    r.ok = 200 <= code < 300
    r.json.return_value = data
    r.text = json.dumps(data)
    return r


@patch("scripts.ecosystem_baseline_probe.requests.Session")
def test_run_probe_pass_minimal(mock_session_cls):
    sess = MagicMock()
    mock_session_cls.return_value = sess

    plc_body = {
        "current_state": "idle",
        "faithh_status": {"version": "4.0-pulse"},
        "recent_component_changes": [],
    }
    health_body = {
        "overall_health": {"status": "healthy", "issues": []},
        "services": {"connection_monitor": {"monitoring_active": True, "overall_status": "healthy"}},
    }
    sess.get.side_effect = [
        _resp(200, plc_body),
        _resp(200, health_body),
    ]
    sess.post.side_effect = [
        _resp(200, {"success": True, "response": "pong", "response_time": 0.0, "request_id": "r0"}),
        _resp(
            200,
            {
                "success": True,
                "response": "4",
                "response_time": 0.42,
                "model_used": "x",
                "provider": "Groq",
                "request_id": "r1",
                "routing_debug": {"llm_routing": {"latency_ms": 200.0}},
            },
        ),
    ]

    report = run_probe(
        base_url="http://127.0.0.1:5557",
        with_rag=False,
        skip_llm=False,
        timeout_plc=5.0,
        timeout_health=5.0,
        timeout_chat=60.0,
        max_wall_ping_ms=99999.0,
        max_wall_llm_ms=99999.0,
        max_wall_rag_ms=99999.0,
        strict_health=False,
        llm_message="test",
    )

    assert report["pass"] is True
    assert report["failures"] == []
    assert report["steps"]["chat_ping"]["response_time_server"] == 0.0
    assert report["steps"]["chat_baseline_llm"]["llm_routing_latency_ms"] == 200.0
    assert report["steps"]["chat_with_rag"]["skipped"] is True
    assert sess.get.call_count == 2
    assert sess.post.call_count == 2


@patch("scripts.ecosystem_baseline_probe.requests.Session")
def test_run_probe_strict_health_fails(mock_session_cls):
    sess = MagicMock()
    mock_session_cls.return_value = sess

    plc_body = {"faithh_status": {"version": "v1"}, "recent_component_changes": []}
    health_body = {"overall_health": {"status": "degraded", "issues": ["x"]}, "services": {}}
    sess.get.side_effect = [_resp(200, plc_body), _resp(200, health_body)]
    sess.post.side_effect = [
        _resp(200, {"success": True, "response": "pong", "response_time": 0.0}),
        _resp(200, {"success": True, "response": "ok", "response_time": 0.1}),
    ]

    report = run_probe(
        base_url="http://127.0.0.1:5557",
        with_rag=False,
        skip_llm=False,
        timeout_plc=5.0,
        timeout_health=5.0,
        timeout_chat=60.0,
        max_wall_ping_ms=99999.0,
        max_wall_llm_ms=99999.0,
        max_wall_rag_ms=99999.0,
        strict_health=True,
        llm_message="x",
    )

    assert report["pass"] is False
    assert any("overall_health" in f for f in report["failures"])
