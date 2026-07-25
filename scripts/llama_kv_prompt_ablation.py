#!/usr/bin/env python3
"""
Send fixed prompts to llama-server (OpenAI-compatible /v1) and record latency + outputs.

Pairs with scripts/run_llama_kv_quality_ablation.sh: f16 vs q4_0 (optional q8_0).
Subcommands: run (writes JSON + optional environment metadata), compare, compare-multi.

Prompts match scripts/extract_kv_vectors.py (PolarQuant KV experiment alignment).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Same sentence starters as extract_kv_vectors.py
DEFAULT_PROMPTS = [
    "The avatar transitions between operational states by",
    "In distributed systems, context compression allows",
    "The recursive polar transform converts cartesian coordinates",
    "When multiple agent states must coexist in memory,",
    "Quantization error accumulates across transformer layers when",
]


def _get_json(url: str, timeout: float) -> dict[str, Any]:
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def _post_json(url: str, body: dict, timeout: float) -> dict[str, Any]:
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def first_model_id(base_v1: str, timeout: float) -> str:
    d = _get_json(f"{base_v1.rstrip('/')}/models", timeout)
    data = d.get("data") or []
    if not data:
        raise RuntimeError(f"No models at {base_v1}/models: {d!r}")
    mid = (data[0].get("id") or "").strip()
    if not mid:
        raise RuntimeError(f"Empty model id in /v1/models: {d!r}")
    return mid


def run_prompts(
    base_v1: str,
    prompts: list[str],
    max_tokens: int,
    temperature: float,
    timeout: float,
) -> list[dict[str, Any]]:
    mid = first_model_id(base_v1, timeout)
    out: list[dict[str, Any]] = []
    chat_url = f"{base_v1.rstrip('/')}/chat/completions"

    for i, user_text in enumerate(prompts):
        body = {
            "model": mid,
            "messages": [{"role": "user", "content": user_text}],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        t0 = time.perf_counter()
        try:
            d = _post_json(chat_url, body, timeout=timeout)
        except urllib.error.HTTPError as e:
            err_body = e.read().decode(errors="replace")[:2000]
            raise RuntimeError(f"HTTP {e.code} for prompt {i}: {err_body}") from e
        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        choice0 = (d.get("choices") or [{}])[0]
        msg = choice0.get("message") or {}
        content = msg.get("content")
        if content is None:
            content = ""
        elif not isinstance(content, str):
            content = json.dumps(content)

        usage = d.get("usage") or {}
        rec = {
            "prompt_index": i,
            "user_message": user_text,
            "latency_ms": round(elapsed_ms, 2),
            "model": mid,
            "content": content,
            "content_sha256": hashlib.sha256(content.encode()).hexdigest()[:16],
            "finish_reason": choice0.get("finish_reason"),
            "prompt_tokens": usage.get("prompt_tokens"),
            "completion_tokens": usage.get("completion_tokens"),
            "total_tokens": usage.get("total_tokens"),
        }
        out.append(rec)
    return out


def collect_environment_metadata() -> dict[str, Any]:
    """
    Best-effort context for reproducibility (operator machine + llama build).
    Shell should export: GGUF_PATH, KV_ABLATION_CTX, KV_ABLATION_CACHE_KV, KV_ABLATION_NGL, LLAMA_SERVER.
    """
    m: dict[str, Any] = {
        "platform": platform.platform(),
        "python_version": platform.python_version(),
    }
    for key in (
        "CUDA_VISIBLE_DEVICES",
        "OLLAMA_MODEL_REF",
        "KV_ABLATION_CTX",
        "KV_ABLATION_CACHE_KV",
        "KV_ABLATION_NGL",
    ):
        v = os.environ.get(key)
        if v:
            m[key.lower()] = v
    gp = os.environ.get("GGUF_PATH")
    if gp:
        p = Path(gp)
        m["gguf_basename"] = p.name
        try:
            m["gguf_bytes"] = p.stat().st_size
        except OSError:
            pass
    nv = shutil.which("nvidia-smi")
    if nv:
        try:
            proc = subprocess.run(
                [nv, "--query-gpu=name,driver_version,memory.total", "--format=csv,noheader"],
                capture_output=True,
                text=True,
                timeout=12,
                check=False,
            )
            if proc.stdout:
                line0 = proc.stdout.strip().split("\n")[0].strip()
                if line0:
                    m["nvidia_smi_gpu_line_0"] = line0
        except Exception as e:
            m["nvidia_smi_error"] = str(e)
    for cand in (
        os.environ.get("LLAMA_SERVER"),
        shutil.which("llama-server"),
        str(Path.home() / "llama.cpp/build/bin/llama-server"),
    ):
        if cand and Path(cand).is_file():
            try:
                proc = subprocess.run(
                    [cand, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=8,
                    check=False,
                )
                txt = (proc.stdout or "") + (proc.stderr or "")
                m["llama_server_path"] = cand
                m["llama_server_version_output"] = txt.strip()[:1200]
            except Exception as e:
                m["llama_server_version_error"] = str(e)
            break
    return m


def cmd_run(args: argparse.Namespace) -> int:
    if args.prompt_file:
        text = Path(args.prompt_file).read_text(encoding="utf-8")
        prompts = [ln.strip() for ln in text.splitlines() if ln.strip()]
    else:
        prompts = list(DEFAULT_PROMPTS)

    try:
        rows = run_prompts(
            args.base_url,
            prompts,
            max_tokens=args.max_tokens,
            temperature=args.temperature,
            timeout=args.timeout,
        )
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    payload: dict[str, Any] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "label": args.label,
        "base_url": args.base_url,
        "max_tokens": args.max_tokens,
        "temperature": args.temperature,
        "n_prompts": len(rows),
        "results": rows,
    }
    if not args.no_environment:
        payload["environment"] = collect_environment_metadata()
    out_path = Path(args.out).expanduser()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {out_path} ({len(rows)} completions)")
    return 0


def cmd_compare(args: argparse.Namespace) -> int:
    a = json.loads(Path(args.left).read_text(encoding="utf-8"))
    b = json.loads(Path(args.right).read_text(encoding="utf-8"))
    ra = a.get("results") or []
    rb = b.get("results") or []
    if len(ra) != len(rb):
        print(f"Mismatch: {len(ra)} vs {len(rb)} rows", file=sys.stderr)
        return 1

    print(f"Compare: {args.left}\n     vs {args.right}\n")
    print(f"{'#':>2} {'ms A':>8} {'ms B':>8} {'Δms':>8}  match  sha A      sha B")
    for i, (x, y) in enumerate(zip(ra, rb)):
        la = x.get("latency_ms", 0)
        lb = y.get("latency_ms", 0)
        same = x.get("content") == y.get("content")
        print(
            f"{i:2d} {la:8.1f} {lb:8.1f} {lb - la:8.1f}  "
            f"{'Y' if same else 'N'}  {x.get('content_sha256','')} {y.get('content_sha256','')}"
        )
    return 0


def cmd_compare_multi(args: argparse.Namespace) -> int:
    paths = [Path(p) for p in args.paths]
    if len(paths) < 2:
        print("Need baseline JSON plus at least one other (e.g. f16 q4 q8).", file=sys.stderr)
        return 1
    datas = [json.loads(p.read_text(encoding="utf-8")) for p in paths]
    labels = [str(d.get("label") or p.stem).strip() for d, p in zip(datas, paths)]
    rows0 = datas[0].get("results") or []
    for j in range(1, len(datas)):
        rj = datas[j].get("results") or []
        if len(rj) != len(rows0):
            print(f"Row count mismatch: {paths[0]} ({len(rows0)}) vs {paths[j]} ({len(rj)})", file=sys.stderr)
            return 1

    print("Compare-multi: first file = baseline; m = exact same assistant text as baseline.\n")
    head = f"{'#':>2}  {'lat_ms ' + labels[0][:24]:>30}"
    for lab in labels[1:]:
        head += f"  {'lat_ms ' + lab[:20]:>28}  m"
    print(head)
    for i, base in enumerate(rows0):
        row = f"{i:2d}  {float(base.get('latency_ms', 0)):8.1f}".ljust(34)
        for j in range(1, len(datas)):
            o = datas[j]["results"][i]
            same = base.get("content") == o.get("content")
            row += f"  {float(o.get('latency_ms', 0)):8.1f}  {'Y' if same else 'N'}      "
        print(row.rstrip())
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="llama-server KV quality prompt ablation")
    sub = p.add_subparsers(dest="cmd", required=True)

    pr = sub.add_parser("run", help="Send prompts and write JSON")
    pr.add_argument(
        "--base-url",
        default="http://127.0.0.1:8090/v1",
        help="OpenAI-compatible base including /v1",
    )
    pr.add_argument(
        "--out",
        type=Path,
        default=Path("data/kv_vectors/llama_kv_ablation.json"),
        help="Output JSON path",
    )
    pr.add_argument("--label", default="", help="Tag stored in JSON metadata")
    pr.add_argument("--max-tokens", type=int, default=256)
    pr.add_argument("--temperature", type=float, default=0.0)
    pr.add_argument("--timeout", type=float, default=180.0)
    pr.add_argument(
        "--prompt-file",
        default="",
        help="Newline-separated user messages (default: extract_kv_vectors starters)",
    )
    pr.add_argument(
        "--no-environment",
        action="store_true",
        help="Omit environment/repro metadata block in JSON",
    )
    pr.set_defaults(func=cmd_run)

    pc = sub.add_parser("compare", help="Diff two run JSONs (latency + exact text match)")
    pc.add_argument("left")
    pc.add_argument("right")
    pc.set_defaults(func=cmd_compare)

    pm = sub.add_parser(
        "compare-multi",
        help="Baseline JSON first, then others; prints latency + Y/N match vs baseline text",
    )
    pm.add_argument("paths", nargs="+", metavar="JSON")
    pm.set_defaults(func=cmd_compare_multi)

    args = p.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
