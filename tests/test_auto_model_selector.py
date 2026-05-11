"""Pytest coverage for auto model selection (aligned with /api/chat auto mode)."""

import pytest

from backend.llm_providers import get_optimal_model_for_query, normalize_assistant_text


def test_normalize_assistant_text_list_blocks():
    assert normalize_assistant_text([{"type": "text", "text": "Hello"}]) == "Hello"
    assert normalize_assistant_text(None) == ""
    assert normalize_assistant_text({"content": "x"}) == "x"


@pytest.mark.parametrize(
    "query,exp_provider,exp_model_substr",
    [
        ("hello there", "ollama", "grounded"),
        (
            "why does the quantum eraser experiment produce interference patterns",
            "ollama",
            "deepseek",
        ),
        ("what does my faithh_memory.json contain", "ollama", "grounded"),
        ("according to my documentation the API", "ollama", "grounded"),
    ],
)
def test_get_optimal_model_for_query(query, exp_provider, exp_model_substr):
    p, m = get_optimal_model_for_query(query)
    assert p == exp_provider
    assert exp_model_substr in m.lower()


def test_creative_routes_to_gemini():
    p, m = get_optimal_model_for_query("imagine a perfect world where AI helps everyone")
    assert p == "gemini"
    assert "gemini" in m.lower()
