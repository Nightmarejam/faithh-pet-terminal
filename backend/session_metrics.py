"""
FAITHH session operational telemetry — Chroma collection `faithh_session_metrics`.
Not mixed into RAG / faithh_knowledge_base.
"""

from __future__ import annotations

import json
import logging
import os
import time
from collections import Counter, OrderedDict
from datetime import datetime, timedelta, timezone
from typing import Any

logger = logging.getLogger(__name__)

STALL_THRESHOLD_MS = int(os.environ.get("FAITHH_STALL_THRESHOLD_MS", "30000"))
ACC_MAX = int(os.environ.get("FAITHH_SESSION_ACCUMULATOR_MAX", "500"))

DOMAIN = "faithh"
CAT = "session_metrics"
DOC_TYPE = "operational_telemetry"

_accumulators: OrderedDict[str, dict[str, Any]] = OrderedDict()


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _week_label(d: datetime) -> str:
    iso = d.isocalendar()
    return f"{iso.year}-W{iso.week:02d}"


def _new_accumulator() -> dict[str, Any]:
    return {
        "turns": 0,
        "rag_used_count": 0,
        "system_data_attached_count": 0,
        "stream_used": False,
        "providers_used": [],
        "latencies_ms": [],
        "fallback_count": 0,
        "stall_count": 0,
        "error_count": 0,
    }


def ensure_accumulator(session_id: str) -> None:
    if not session_id:
        return
    if session_id in _accumulators:
        _accumulators.move_to_end(session_id)
        return
    while len(_accumulators) >= ACC_MAX:
        _accumulators.popitem(last=False)
    _accumulators[session_id] = _new_accumulator()


def pop_accumulator(session_id: str) -> dict[str, Any] | None:
    return _accumulators.pop(session_id, None)


def accumulator_size() -> int:
    return len(_accumulators)


def bump_after_turn(
    session_id: str,
    *,
    rag_used: bool,
    system_data_attached_len: int,
    stream_used: bool,
    latency_ms: int,
    provider_slug: str,
    used_fallback: bool,
    stall_threshold_ms: int = STALL_THRESHOLD_MS,
) -> None:
    if not session_id:
        return
    ensure_accumulator(session_id)
    acc = _accumulators[session_id]
    _accumulators.move_to_end(session_id)
    acc["turns"] += 1
    if rag_used:
        acc["rag_used_count"] += 1
    if system_data_attached_len:
        acc["system_data_attached_count"] += 1
    if stream_used:
        acc["stream_used"] = True
    acc["latencies_ms"].append(latency_ms)
    ps = provider_slug.lower().strip()
    if ps and ps not in acc["providers_used"]:
        acc["providers_used"].append(ps)
    if used_fallback:
        acc["fallback_count"] += 1
    if latency_ms > stall_threshold_ms:
        acc["stall_count"] += 1


def note_error(session_id: str) -> None:
    if not session_id:
        return
    ensure_accumulator(session_id)
    acc = _accumulators[session_id]
    _accumulators.move_to_end(session_id)
    acc["error_count"] += 1


def normalize_provider_slug(provider_display: str) -> str:
    n = (provider_display or "").lower()
    if "groq" in n:
        return "groq"
    if "anthropic" in n or "claude" in n:
        return "anthropic"
    if "google" in n or "gemini" in n:
        return "gemini"
    return "ollama"


def bump_from_chat_response(
    session_id: str | None,
    response_data: dict,
    *,
    streamed: bool,
    routing_debug: dict | None,
) -> None:
    if not session_id:
        return
    rd = routing_debug or {}
    llm = rd.get("llm_routing") or {}
    used_fb = bool(llm.get("used_fallback"))
    prov = normalize_provider_slug(str(response_data.get("provider") or "ollama"))
    rt = response_data.get("response_time")
    try:
        latency_ms = int(float(rt) * 1000) if rt is not None else 0
    except (TypeError, ValueError):
        latency_ms = 0
    bump_after_turn(
        session_id,
        rag_used=bool(response_data.get("rag_used")),
        system_data_attached_len=len(response_data.get("system_data_attached") or []),
        stream_used=streamed,
        latency_ms=latency_ms,
        provider_slug=prov,
        used_fallback=used_fb,
    )


def _rag_block_from_signal(
    sig: dict,
    *,
    threshold: float,
    collection_size: int,
    stale_seconds: float,
) -> dict[str, Any]:
    ts = sig.get("ts")
    age: int | None = None
    if isinstance(ts, (int, float)):
        age = int(max(0, time.time() - float(ts)))
    ran = bool(sig.get("ran"))
    stale = age is None or age > stale_seconds or not ran
    best_distance = sig.get("best_distance")
    bd_f: float | None
    if best_distance is None:
        bd_f = None
    else:
        try:
            bd_f = float(best_distance)
        except (TypeError, ValueError):
            bd_f = None
    if stale:
        return {
            "best_distance": bd_f,
            "low_confidence": True,
            "threshold": threshold,
            "collection_size": collection_size,
            "signal_age_seconds": age if age is not None else -1,
        }
    lc = bool(sig.get("low_confidence")) if bd_f is not None else True
    return {
        "best_distance": bd_f,
        "low_confidence": lc,
        "threshold": threshold,
        "collection_size": collection_size,
        "signal_age_seconds": int(age) if age is not None else 0,
    }


def _outcome_from_accumulator(acc: dict[str, Any] | None) -> dict[str, Any]:
    if not acc:
        return {
            "turns": 0,
            "rag_used_count": 0,
            "system_data_attached_count": 0,
            "stream_used": False,
            "providers_used": [],
            "avg_latency_ms": 0.0,
            "max_latency_ms": 0.0,
            "fallback_count": 0,
            "stall_count": 0,
            "error_count": 0,
        }
    lat = acc.get("latencies_ms") or []
    avg = float(sum(lat) / len(lat)) if lat else 0.0
    mx = float(max(lat)) if lat else 0.0
    return {
        "turns": int(acc.get("turns", 0)),
        "rag_used_count": int(acc.get("rag_used_count", 0)),
        "system_data_attached_count": int(acc.get("system_data_attached_count", 0)),
        "stream_used": bool(acc.get("stream_used")),
        "providers_used": list(acc.get("providers_used") or []),
        "avg_latency_ms": avg,
        "max_latency_ms": mx,
        "fallback_count": int(acc.get("fallback_count", 0)),
        "stall_count": int(acc.get("stall_count", 0)),
        "error_count": int(acc.get("error_count", 0)),
    }


def _flags_from_open_and_outcome(
    open_flags: dict[str, Any],
    outcome: dict[str, Any],
    llm_state: dict[str, Any],
    chroma_unreachable_at_open: bool,
) -> dict[str, Any]:
    return {
        "rag_low_confidence": bool(open_flags.get("rag_low_confidence")),
        "provider_fallback": outcome.get("fallback_count", 0) > 0,
        "stall_detected": outcome.get("stall_count", 0) > 0,
        "chroma_unreachable": bool(chroma_unreachable_at_open),
        "ollama_unreachable": not bool(llm_state.get("ollama_reachable")),
        "error_count": int(outcome.get("error_count", 0)),
    }


def build_session_open_document(
    session_id: str,
    *,
    workspace_registry: dict,
    rag_signal: dict,
    rag_threshold: float,
    rag_stale_seconds: float,
    primary_provider: str,
    ollama_model: str,
    kv_cache_type: str,
    ollama_reachable: bool,
    chroma_connected: bool,
    collection_size: int,
) -> dict[str, Any]:
    now = _utc_now()
    sm = workspace_registry.get("services") or {}
    rag_svc = sm.get("rag") or {}
    services_active = {
        "chat": bool((sm.get("chat") or {}).get("active", True)),
        "rag": bool(rag_svc.get("active")),
        "genomic": bool((sm.get("genomic") or {}).get("active")),
        "pulse": bool((sm.get("pulse") or {}).get("active")),
        "ollama": bool(ollama_reachable),
    }
    rag_block = _rag_block_from_signal(
        rag_signal,
        threshold=rag_threshold,
        collection_size=collection_size,
        stale_seconds=rag_stale_seconds,
    )
    llm_state = {
        "primary_provider": str(primary_provider or "ollama").lower(),
        "ollama_model": str(ollama_model or ""),
        "kv_cache_type": str(kv_cache_type or ""),
        "ollama_reachable": bool(ollama_reachable),
    }
    meta_date = now.date().isoformat()
    meta_week = _week_label(now)
    open_flags = {
        "rag_low_confidence": bool(rag_block.get("low_confidence")),
        "provider_fallback": False,
        "stall_detected": False,
        "chroma_unreachable": not bool(chroma_connected),
        "ollama_unreachable": not bool(ollama_reachable),
        "error_count": 0,
    }
    doc = {
        "id": session_id,
        "timestamp_open": now.isoformat(),
        "timestamp_close": None,
        "duration_seconds": None,
        "services_active": services_active,
        "rag_signal": rag_block,
        "llm_state": llm_state,
        "session_outcome": {
            "turns": 0,
            "rag_used_count": 0,
            "system_data_attached_count": 0,
            "stream_used": False,
            "providers_used": [],
            "avg_latency_ms": 0.0,
            "max_latency_ms": 0.0,
            "fallback_count": 0,
            "stall_count": 0,
        },
        "flags": open_flags,
        "metadata": {
            "domain": DOMAIN,
            "category": CAT,
            "document_type": DOC_TYPE,
            "date": meta_date,
            "week": meta_week,
        },
    }
    return doc


def _chroma_metadata_for_doc(doc: dict[str, Any], closed: int) -> dict[str, Any]:
    md = doc.get("metadata") or {}
    return {
        "domain": str(md.get("domain", DOMAIN)),
        "category": str(md.get("category", CAT)),
        "document_type": str(md.get("document_type", DOC_TYPE)),
        "date": str(md.get("date", "")),
        "week": str(md.get("week", "")),
        "session_id": str(doc.get("id", "")),
        "closed": int(closed),
    }


def record_session_open(
    metrics_collection,
    session_id: str,
    *,
    workspace_registry: dict,
    rag_signal: dict,
    rag_threshold: float,
    rag_stale_seconds: float,
    primary_provider: str,
    ollama_model: str,
    kv_cache_type: str,
    ollama_reachable: bool,
    chroma_connected: bool,
    collection_size: int,
) -> None:
    if metrics_collection is None or not session_id:
        return
    doc = build_session_open_document(
        session_id,
        workspace_registry=workspace_registry,
        rag_signal=rag_signal,
        rag_threshold=rag_threshold,
        rag_stale_seconds=rag_stale_seconds,
        primary_provider=primary_provider,
        ollama_model=ollama_model,
        kv_cache_type=kv_cache_type,
        ollama_reachable=ollama_reachable,
        chroma_connected=chroma_connected,
        collection_size=collection_size,
    )
    ensure_accumulator(session_id)
    try:
        metrics_collection.upsert(
            ids=[session_id],
            documents=[json.dumps(doc, default=str)],
            metadatas=[_chroma_metadata_for_doc(doc, 0)],
        )
    except Exception as e:
        logger.warning("record_session_open failed: %s", e)
        raise


def apply_session_metrics_close(
    metrics_collection,
    session_id: str,
    merged: dict[str, Any],
) -> bool:
    """
    Merge outcome into the existing open session row and mark closed in Chroma.
    Returns True if a document was updated.
    """
    if metrics_collection is None or not session_id:
        return False
    try:
        res = metrics_collection.get(ids=[session_id], include=["documents"])
    except Exception as e:
        logger.warning("apply_session_metrics_close get failed: %s", e)
        return False
    docs = res.get("documents") or []
    if not docs or not docs[0]:
        return False
    try:
        doc = json.loads(docs[0])
    except Exception:
        return False
    t_open_s = doc.get("timestamp_open")
    t_close = _utc_now()
    duration = None
    if t_open_s:
        try:
            t0 = datetime.fromisoformat(str(t_open_s).replace("Z", "+00:00"))
            if t0.tzinfo is None:
                t0 = t0.replace(tzinfo=timezone.utc)
            duration = int((t_close - t0).total_seconds())
        except Exception:
            duration = None
    doc["timestamp_close"] = t_close.isoformat()
    doc["duration_seconds"] = duration
    doc["session_outcome"] = {
        "turns": int(merged.get("turns", 0)),
        "rag_used_count": int(merged.get("rag_used_count", 0)),
        "system_data_attached_count": int(merged.get("system_data_attached_count", 0)),
        "stream_used": bool(merged.get("stream_used")),
        "providers_used": list(merged.get("providers_used") or []),
        "avg_latency_ms": float(merged.get("avg_latency_ms", 0.0)),
        "max_latency_ms": float(merged.get("max_latency_ms", 0.0)),
        "fallback_count": int(merged.get("fallback_count", 0)),
        "stall_count": int(merged.get("stall_count", 0)),
    }
    doc["flags"] = _flags_from_open_and_outcome(
        doc.get("flags") or {},
        merged,
        doc.get("llm_state") or {},
        bool((doc.get("flags") or {}).get("chroma_unreachable")),
    )
    doc["flags"]["error_count"] = int(merged.get("error_count", 0))
    try:
        metrics_collection.upsert(
            ids=[session_id],
            documents=[json.dumps(doc, default=str)],
            metadatas=[_chroma_metadata_for_doc(doc, 1)],
        )
    except Exception as e:
        logger.warning("apply_session_metrics_close upsert failed: %s", e)
        return False
    return True


def record_session_close(
    metrics_collection,
    session_id: str,
    outcome: dict[str, Any] | None = None,
) -> None:
    acc = pop_accumulator(session_id)
    merged = outcome if outcome is not None else _outcome_from_accumulator(acc)
    apply_session_metrics_close(metrics_collection, session_id, merged)


def flush_session_metrics(metrics_collection, session_id: str) -> tuple[dict[str, Any], bool]:
    """
    Pop in-memory accumulator and write closed session row to Chroma.
    Returns (outcome_dict, chroma_updated).
    """
    acc = pop_accumulator(session_id)
    merged = _outcome_from_accumulator(acc)
    ok = apply_session_metrics_close(metrics_collection, session_id, merged)
    return merged, ok


def fetch_session_documents(
    metrics_collection,
    days: int,
    limit: int,
) -> list[dict[str, Any]]:
    if metrics_collection is None:
        return []
    cutoff = (_utc_now() - timedelta(days=max(1, days))).date().isoformat()
    # Chroma metadata filters do not support $gte on string dates; fetch recent slice and filter in Python.
    try:
        res = metrics_collection.get(
            limit=min(2000, max(500, limit * 50)),
            include=["documents", "metadatas"],
        )
    except Exception as e2:
        logger.warning("session metrics chroma get failed: %s", e2)
        return []
    out: list[dict[str, Any]] = []
    for doc_s in res.get("documents") or []:
        if not doc_s:
            continue
        try:
            d = json.loads(doc_s)
        except Exception:
            continue
        md_in = d.get("metadata") or {}
        if md_in.get("category") != CAT and md_in.get("document_type") != DOC_TYPE:
            continue
        try:
            d_date = (d.get("metadata") or {}).get("date") or d.get("timestamp_open", "")[:10]
            if d_date < cutoff:
                continue
        except Exception:
            pass
        out.append(d)
    out.sort(key=lambda x: str(x.get("timestamp_open") or ""), reverse=True)
    return out[: max(1, limit)]


def _split_halves(sessions: list[dict[str, Any]]) -> tuple[list, list]:
    if len(sessions) < 4:
        return sessions, sessions
    mid = len(sessions) // 2
    # sessions sorted desc by time — first half = older window, second = newer
    older = sessions[mid:]
    newer = sessions[:mid]
    return older, newer


def _mean(xs: list[float]) -> float:
    return float(sum(xs) / len(xs)) if xs else 0.0


def _trend_direction(before: float, after: float, *, lower_is_better: bool) -> str:
    if before <= 0 and after <= 0:
        return "stable"
    ref = max(abs(before), abs(after), 1.0)
    if abs(after - before) < 0.05 * ref:
        return "stable"
    if lower_is_better:
        return "improving" if after < before else "degrading"
    return "improving" if after > before else "degrading"


def compute_summary_from_parsed_sessions(
    sessions: list[dict[str, Any]],
    *,
    window_days: int,
    limit: int,
) -> dict[str, Any]:
    n = len(sessions)
    if n == 0:
        return {
            "window_days": window_days,
            "limit": limit,
            "sessions_total": 0,
            "sessions_with_rag": 0,
            "sessions_with_fallback": 0,
            "sessions_with_stall": 0,
            "avg_latency_ms": 0,
            "avg_turns_per_session": 0.0,
            "rag_low_confidence_rate": 0.0,
            "provider_distribution": {},
            "top_flags": [],
            "trend": {
                "latency_direction": "stable",
                "fallback_direction": "stable",
                "rag_quality_direction": "stable",
            },
            "health_score": 100.0,
            "daily_buckets": [],
        }

    with_rag = sum(
        1
        for s in sessions
        if (s.get("session_outcome") or {}).get("rag_used_count", 0) > 0
    )
    with_fb = sum(1 for s in sessions if (s.get("session_outcome") or {}).get("fallback_count", 0) > 0)
    with_stall = sum(1 for s in sessions if (s.get("session_outcome") or {}).get("stall_count", 0) > 0)
    latencies = [
        float((s.get("session_outcome") or {}).get("avg_latency_ms") or 0)
        for s in sessions
        if (s.get("session_outcome") or {}).get("turns", 0) > 0
    ]
    avg_lat = int(_mean(latencies)) if latencies else 0
    turns = [(s.get("session_outcome") or {}).get("turns", 0) for s in sessions]
    avg_turns = _mean([float(t) for t in turns])
    rag_lc = sum(1 for s in sessions if (s.get("flags") or {}).get("rag_low_confidence"))
    rag_lc_rate = rag_lc / n if n else 0.0
    fb_rate = with_fb / n if n else 0.0
    stall_rate = with_stall / n if n else 0.0

    prov_c: Counter[str] = Counter()
    for s in sessions:
        for p in (s.get("session_outcome") or {}).get("providers_used") or []:
            prov_c[str(p).lower()] += 1

    flag_counts: Counter[str] = Counter()
    for s in sessions:
        fl = s.get("flags") or {}
        for k, v in fl.items():
            if k == "error_count":
                continue
            if v:
                flag_counts[k] += 1
        ec = int(fl.get("error_count") or 0)
        if ec > 0:
            flag_counts["error_count"] += 1

    top_flags = [k for k, _ in flag_counts.most_common(8)]

    older, newer = _split_halves(sessions)
    lat_o = _mean(
        [
            float((s.get("session_outcome") or {}).get("avg_latency_ms") or 0)
            for s in older
            if (s.get("session_outcome") or {}).get("turns", 0) > 0
        ]
    )
    lat_n = _mean(
        [
            float((s.get("session_outcome") or {}).get("avg_latency_ms") or 0)
            for s in newer
            if (s.get("session_outcome") or {}).get("turns", 0) > 0
        ]
    )
    fb_o = (
        sum(1 for s in older if (s.get("session_outcome") or {}).get("fallback_count", 0) > 0) / len(older)
        if older
        else 0.0
    )
    fb_n = (
        sum(1 for s in newer if (s.get("session_outcome") or {}).get("fallback_count", 0) > 0) / len(newer)
        if newer
        else 0.0
    )
    rag_o = _mean(
        [
            float((s.get("rag_signal") or {}).get("best_distance") or 1.0)
            for s in older
            if (s.get("rag_signal") or {}).get("best_distance") is not None
        ]
    )
    rag_n = _mean(
        [
            float((s.get("rag_signal") or {}).get("best_distance") or 1.0)
            for s in newer
            if (s.get("rag_signal") or {}).get("best_distance") is not None
        ]
    )
    if not any(
        (s.get("rag_signal") or {}).get("best_distance") is not None for s in older
    ):
        rag_o = 0.0
    if not any(
        (s.get("rag_signal") or {}).get("best_distance") is not None for s in newer
    ):
        rag_n = 0.0

    trend = {
        "latency_direction": _trend_direction(lat_o, lat_n, lower_is_better=True),
        "fallback_direction": _trend_direction(fb_o, fb_n, lower_is_better=True),
        "rag_quality_direction": _trend_direction(rag_o, rag_n, lower_is_better=True),
    }

    health = (1 - fb_rate) * 40 + (1 - stall_rate) * 30 + (1 - rag_lc_rate) * 30
    health = max(0.0, min(100.0, health))

    # Daily buckets for sparklines (by timestamp_open date)
    by_day: dict[str, list[dict[str, Any]]] = {}
    for s in sessions:
        ts = str(s.get("timestamp_open") or "")
        day = ts[:10] if len(ts) >= 10 else "unknown"
        by_day.setdefault(day, []).append(s)
    daily_buckets = []
    for day in sorted(by_day.keys()):
        grp = by_day[day]
        gn = len(grp)
        lats = [
            float((x.get("session_outcome") or {}).get("avg_latency_ms") or 0)
            for x in grp
            if (x.get("session_outcome") or {}).get("turns", 0) > 0
        ]
        rlc = sum(1 for x in grp if (x.get("flags") or {}).get("rag_low_confidence"))
        fbc = sum(1 for x in grp if (x.get("session_outcome") or {}).get("fallback_count", 0) > 0)
        daily_buckets.append(
            {
                "date": day,
                "avg_latency_ms": int(_mean(lats)) if lats else 0,
                "rag_low_confidence_rate": round(rlc / gn, 4) if gn else 0.0,
                "fallback_count": fbc,
            }
        )

    return {
        "window_days": window_days,
        "limit": limit,
        "sessions_total": n,
        "sessions_with_rag": with_rag,
        "sessions_with_fallback": with_fb,
        "sessions_with_stall": with_stall,
        "avg_latency_ms": avg_lat,
        "avg_turns_per_session": round(avg_turns, 2),
        "rag_low_confidence_rate": round(rag_lc_rate, 4),
        "provider_distribution": dict(prov_c),
        "top_flags": top_flags,
        "trend": trend,
        "health_score": round(health, 1),
        "daily_buckets": daily_buckets,
    }


def health_score_from_rates(fallback_rate: float, stall_rate: float, rag_lc_rate: float) -> float:
    # Stall/latency primary; RAG quality secondary; provider fallback tertiary.
    s = (1 - stall_rate) * 40 + (1 - rag_lc_rate) * 35 + (1 - fallback_rate) * 25
    return max(0.0, min(100.0, s))


def flag_combination_key(s: dict[str, Any]) -> str:
    fl = s.get("flags") or {}
    parts = []
    for k in sorted(fl.keys()):
        if k == "error_count":
            if int(fl.get("error_count") or 0) > 0:
                parts.append("error_count")
            continue
        if fl.get(k):
            parts.append(k)
    return " + ".join(parts) if parts else "(none)"

