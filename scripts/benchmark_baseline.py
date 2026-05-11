#!/usr/bin/env python3
"""
CLI baseline benchmark: same intent + integrated context path as /api/chat (no Flask/HTTP).

Logs one JSON line to logs/performance.log with request_source: "baseline_cli" so you can
compare rag_ms / llm_ms / total_ms against API and UI rows.

Usage (from repo root):
  venv/bin/python scripts/benchmark_baseline.py
  venv/bin/python scripts/benchmark_baseline.py --context-only
  venv/bin/python scripts/benchmark_baseline.py --message "Your query here"

Note: Imports faithh_professional_backend_fixed (one-time Chroma/embedder init). Do not run
dozens of parallel copies; use for occasional baselines.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def _append_performance_log(row: dict) -> None:
    log_dir = REPO_ROOT / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    path = log_dir / "performance.log"
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, default=str) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="FAITHH CLI performance baseline (no Flask).")
    parser.add_argument(
        "--message",
        "-m",
        default="How does ALIFE integrate with FAITHH RAG?",
        help="Query text (default: ALIFE + KB style)",
    )
    parser.add_argument(
        "--context-only",
        action="store_true",
        help="Measure build_integrated_context only; skip Ollama /api/generate",
    )
    parser.add_argument(
        "--grounded",
        action="store_true",
        help="Force OLLAMA_GROUNDED_MODEL (skip cloud/complex routing from get_optimal_model_for_query)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=int(os.environ.get("OLLAMA_READ_TIMEOUT", "300")),
        help="Ollama HTTP timeout seconds (when not --context-only)",
    )
    args = parser.parse_args()

    os.chdir(REPO_ROOT)
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))

    try:
        from dotenv import load_dotenv

        env_file = REPO_ROOT / ".env"
        if env_file.is_file():
            load_dotenv(env_file, override=True)
    except ImportError:
        pass

    # Heavy import: initializes Chroma client, embedder hooks, etc.
    import faithh_professional_backend_fixed as fb  # noqa: E402

    from backend.context_builders import get_faithh_personality  # noqa: E402
    from backend.intent_detection import detect_query_intent  # noqa: E402
    from backend.llm_providers import call_ollama_chat, get_optimal_model_for_query  # noqa: E402

    message = (args.message or "").strip()
    if not message:
        print("Empty message", file=sys.stderr)
        return 2

    req_id = f"baseline_cli_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    wall0 = time.perf_counter()

    intent = detect_query_intent(message)
    if args.grounded:
        provider, model = "ollama", os.environ.get(
            "OLLAMA_GROUNDED_MODEL", "qwen25-grounded-gen5-delta:latest"
        )
    else:
        provider, model = get_optimal_model_for_query(message, intent, None)
        if provider != "ollama":
            provider = "ollama"
            model = os.environ.get("OLLAMA_GROUNDED_MODEL", model)

    pipe0 = time.perf_counter()
    (
        context,
        _rag_results,
        _integrations,
        _advance,
        _coh,
        _const,
        _parallel_chip_summary,
    ) = fb.build_integrated_context(message, intent, use_rag=True, session_id=None)
    t_rag_end = time.perf_counter()

    rag_ms = round((t_rag_end - pipe0) * 1000, 2)
    llm_ms = 0.0
    post_ms = 0.0
    reply_preview = ""

    if not args.context_only:
        t_llm0 = time.perf_counter()
        personality = get_faithh_personality()
        prompt = f"{personality}\n\n{context}\n\nUser: {message}"
        base_url = os.environ.get("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
        try:
            text, _usage, _raw = call_ollama_chat(
                base_url,
                model,
                prompt,
                temperature=0.2,
                timeout_s=args.timeout,
                num_ctx=None,
            )
            reply_preview = (text or "")[:200]
        except Exception as exc:
            reply_preview = f"<error: {exc}>"
        t_llm_end = time.perf_counter()
        llm_ms = round((t_llm_end - t_llm0) * 1000, 2)
        post_ms = round((time.perf_counter() - t_llm_end) * 1000, 2)
    else:
        t_llm_end = t_rag_end

    t_done = time.perf_counter()
    total_ms = round((t_done - wall0) * 1000, 2)

    row = {
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
        "rag_ms": rag_ms,
        "llm_ms": llm_ms,
        "post_ms": post_ms,
        "total_ms": total_ms,
        "provider": provider,
        "model": model,
        "query_preview": message[:120],
        "request_id": req_id,
        "cached": False,
        "streamed": False,
        "request_source": "baseline_cli",
        "baseline_context_only": bool(args.context_only),
        "baseline_force_grounded": bool(args.grounded),
        "reply_preview": reply_preview,
    }

    # Optional VRAM sample (same idea as Flask path)
    try:
        import subprocess

        r = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=memory.used,memory.total",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if r.returncode == 0 and (r.stdout or "").strip():
            parts = [p.strip() for p in r.stdout.strip().splitlines()[0].split(",")]
            if len(parts) >= 2:
                row["vram_used_mib"] = int(float(parts[0]))
                row["vram_total_mib"] = int(float(parts[1]))
    except (OSError, ValueError, subprocess.TimeoutExpired, IndexError):
        pass

    _append_performance_log(row)
    print(json.dumps(row, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
