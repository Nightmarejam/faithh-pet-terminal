"""
Shared metadata predicates for date/category spike cohorts (e.g. 2026-03-31 project_docs).

Used by sample_spike_data.py and purge_spike_data.py.
"""

from __future__ import annotations


def spike_date_string(meta: dict | None) -> str:
    """Best-effort timestamp string for spike matching (prefix compare on YYYY-MM-DD)."""
    if not meta:
        return ""
    return str(
        meta.get("indexed_at")
        or meta.get("created_at")
        or meta.get("timestamp")
        or meta.get("mtime")
        or meta.get("updated_at")
        or meta.get("ts")
        or ""
    )


def matches_spike_cohort(
    meta: dict | None,
    *,
    date_prefix: str,
    category_substring: str,
) -> bool:
    if not meta:
        return False
    d = spike_date_string(meta)
    if not str(d).startswith(date_prefix):
        return False
    cat = (meta.get("category") or meta.get("document_type") or "").lower()
    return category_substring.lower() in cat
