#!/usr/bin/env python3
"""
Aggregate llama_kv_ablation_*.json by context size and KV profile.

For each ctx that has an f16 baseline, reports exact text match rate vs f16
and mean latency (and mean Δ vs f16) for q4_0 and q8_0 when present.

Usage:
  python3 scripts/summarize_kv_ablation_runs.py [data/kv_vectors]
  python3 scripts/summarize_kv_ablation_runs.py --markdown docs/experiments/KV_ABLATION_SUMMARY.md
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

FNAME_RE = re.compile(r"^llama_kv_ablation_(f16|q4_0|q8_0)_(\d+)\.json$")


def load_json(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def collect(root: Path) -> dict[str, dict[str, Path]]:
    by_ctx: dict[str, dict[str, Path]] = defaultdict(dict)
    for p in sorted(root.glob("llama_kv_ablation_*.json")):
        m = FNAME_RE.match(p.name)
        if not m:
            continue
        prof, ctx = m.group(1), m.group(2)
        by_ctx[ctx][prof] = p
    return dict(by_ctx)


def analyze_ctx(ctx: str, profs: dict[str, Path]) -> list[str]:
    lines: list[str] = []
    if "f16" not in profs:
        lines.append(f"ctx **{ctx}**: no f16 baseline JSON — skipped.")
        return lines
    base = load_json(profs["f16"])
    br = base.get("results") or []
    n = len(br)
    if n == 0:
        lines.append(f"ctx **{ctx}**: empty f16 results.")
        return lines

    mean_f16 = sum(float(x.get("latency_ms", 0)) for x in br) / n
    lines.append(f"### Context {ctx}")
    lines.append("")
    lines.append("| profile | exact match vs f16 | mean latency (ms) | mean Δ latency vs f16 |")
    lines.append("|---------|-------------------:|------------------:|------------------------:|")

    order = ["f16", "q4_0", "q8_0"]
    stats: dict[str, tuple[int, int, float]] = {}
    for prof in order:
        if prof not in profs:
            continue
        d = load_json(profs[prof])
        r = d.get("results") or []
        if len(r) != n:
            lines.append(f"| {prof} | (row count mismatch) | — | — |")
            continue
        if prof == "f16":
            matches = n
        else:
            matches = sum(1 for i in range(n) if br[i].get("content") == r[i].get("content"))
        lats = [float(x.get("latency_ms", 0)) for x in r]
        mean_lat = sum(lats) / len(lats)
        delta = mean_lat - mean_f16
        lines.append(f"| {prof} | {matches}/{n} | {mean_lat:.1f} | {delta:+.1f} |")
        stats[prof] = (matches, n, mean_lat)

    lines.append("")
    # Short heuristic (exact-match is strict; operator still spot-checks replies)
    q4m = stats.get("q4_0", (0, n, 0))[0]
    q8m = stats.get("q8_0", (0, n, 0))[0]
    if "q4_0" in stats and "q8_0" in stats:
        if q8m > q4m:
            lines.append(
                f"**Heuristic:** At ctx {ctx}, **q8_0** matches f16 on more prompts than **q4_0** "
                f"({q8m} vs {q4m} / {n}). Prefer **q8_0** if VRAM allows — see VRAM table for MiB."
            )
        elif q4m > q8m:
            lines.append(
                f"**Heuristic:** At ctx {ctx}, **q4_0** wins on exact-match count ({q4m} vs {q8m} / {n}) — "
                "unusual; re-run or check JSON. Still validate behavior (q4 can refuse on edge prompts)."
            )
        else:
            lines.append(
                f"**Heuristic:** Same exact-match count ({q4m}/{n}) for q4_0 vs q8_0 at ctx {ctx}. "
                "Prefer **q8_0** if spot-checks look closer to f16; else **q4_0** for maximum KV savings."
            )
    elif "q4_0" in stats:
        lines.append(
            f"**Heuristic:** Only q4_0 vs f16 at ctx {ctx}. If match rate is 0/{n}, treat as "
            "**quality-unverified** — read completions; consider q8_0 or f16 for production."
        )
    lines.append("")
    return lines


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "directory",
        nargs="?",
        type=Path,
        default=Path("data/kv_vectors"),
        help="Directory containing llama_kv_ablation_*.json",
    )
    ap.add_argument(
        "--markdown",
        type=Path,
        default=None,
        help="Write full markdown report to this path",
    )
    args = ap.parse_args()
    root = args.directory
    if not root.is_dir():
        print(f"Not a directory: {root}", file=sys.stderr)
        return 1

    by_ctx = collect(root)
    if not by_ctx:
        print(f"No llama_kv_ablation_*.json under {root}", file=sys.stderr)
        return 1

    md: list[str] = [
        "# KV chat ablation — auto summary",
        "",
        "Exact **match vs f16** = identical assistant string at `temperature=0` (strict).",
        "See `KV_CACHE_QUANT_BENCHMARK_20260405.md` for qualitative notes (e.g. prompt 0).",
        "",
    ]

    for ctx in sorted(by_ctx.keys(), key=int):
        md.extend(analyze_ctx(ctx, by_ctx[ctx]))

    out = "\n".join(md)
    print(out)
    if args.markdown:
        args.markdown.parent.mkdir(parents=True, exist_ok=True)
        args.markdown.write_text(out + "\n", encoding="utf-8")
        print(f"\nWrote {args.markdown}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
