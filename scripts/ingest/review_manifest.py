#!/usr/bin/env python3
"""Review a dry-run manifest without reading raw JSON — Job A, phase 2.

The manifest is 299 records deep; this is the lens for it. Read-only.

    # what is in a mode, and why
    python review_manifest.py m.json --mode troubleshooting
    python review_manifest.py m.json --mode journal --sort chars

    # the ones the classifier declined to label, with what ALMOST matched
    python review_manifest.py m.json --unclassified

    # runbook candidates: troubleshooting that looks like it reached a resolution
    python review_manifest.py m.json --runbook

    # high-signal conversations regardless of label
    python review_manifest.py m.json --nuggets

    # slice by anything
    python review_manifest.py m.json --topic infrastructure --since 2026-04-01
    python review_manifest.py m.json --timeline           # day-by-day coverage

`--near-miss` shows the runner-up scores so you can see which dial to turn:
raise/lower MIN_DENSITY or MIN_HITS in classify.py, or add a phrase to a signal
list. Modes are cheap to add — a new entry in MODE_SIGNALS and a re-run.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

# Signals that a troubleshooting conversation actually RESOLVED — these are the
# ones worth mining into runbook-to-rule-them-all rather than just archiving.
RESOLVED = ("that worked", "fixed", "solved", "working now", "it works", "resolved",
            "perfect", "that did it", "success", "up and running")


def load(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))["records"]


def fmt(r, show_evidence=False, show_scores=False):
    s = r.get("structure") or {}
    line = (f"  {r.get('date') or '????-??-??'}  {r['chunks']:>3}ch {r['chars']//1000:>4}k  "
            f"[{r.get('topic','?'):<14}] {r['title'][:56]}")
    out = [line]
    if show_scores:
        top = sorted((r.get("scores") or {}).items(), key=lambda kv: -kv[1])[:4]
        out.append(f"        modes={','.join(r.get('modes') or ['-'])}  "
                   f"scores={' '.join(f'{k}:{v}' for k, v in top if v)}")
        out.append(f"        human_ratio={s.get('human_ratio')} avg_human_msg={s.get('avg_human_msg')} msgs={s.get('messages')}")
    if show_evidence and r.get("evidence"):
        out.append(f"        why: {', '.join(r['evidence'][:4])}")
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("manifest")
    ap.add_argument("--mode"); ap.add_argument("--topic")
    ap.add_argument("--since"); ap.add_argument("--until")
    ap.add_argument("--unclassified", action="store_true")
    ap.add_argument("--runbook", action="store_true")
    ap.add_argument("--nuggets", action="store_true")
    ap.add_argument("--timeline", action="store_true")
    ap.add_argument("--near-miss", action="store_true")
    ap.add_argument("--sort", choices=["date", "chars", "chunks"], default="date")
    ap.add_argument("--limit", type=int, default=40)
    args = ap.parse_args()

    recs = load(args.manifest)
    sel = recs
    if args.since:
        sel = [r for r in sel if (r.get("date") or "") >= args.since]
    if args.until:
        sel = [r for r in sel if (r.get("date") or "") <= args.until]
    if args.topic:
        sel = [r for r in sel if r.get("topic") == args.topic]
    if args.mode:
        sel = [r for r in sel if args.mode in (r.get("modes") or [])]
    if args.unclassified:
        sel = [r for r in sel if not (r.get("modes") or [])]

    if args.timeline:
        by_day = defaultdict(list)
        for r in sel:
            if r.get("date"):
                by_day[r["date"]].append(r)
        print(f"day-by-day coverage: {len(by_day)} days\n")
        for day in sorted(by_day):
            rs = by_day[day]
            modes = Counter(m for r in rs for m in (r.get("modes") or ["unclassified"]))
            tag = " ".join(f"{m[:5]}:{n}" for m, n in modes.most_common(3))
            print(f"  {day}  {len(rs):>2} conv  {sum(x['chars'] for x in rs)//1000:>4}k  {tag}")
        gaps = 0
        days = sorted(by_day)
        from datetime import date, timedelta
        if days:
            d0 = date.fromisoformat(days[0]); d1 = date.fromisoformat(days[-1])
            gaps = (d1 - d0).days + 1 - len(days)
        print(f"\n  span {days[0]} -> {days[-1]}, {len(days)} active days, {gaps} days with nothing")
        return 0

    if args.runbook:
        # Rank by how much of the conversation IS troubleshooting, not how big it is.
        # Ranking by size put a 662k biology chat with 17 incidental "the error" hits
        # above a 278k GPU-passthrough session with 82 — useless for runbook mining.
        cands = []
        for r in sel:
            modes = r.get("modes") or []
            if "troubleshooting" not in modes:
                continue
            sc = r.get("scores") or {}
            ts = sc.get("troubleshooting", 0)
            runner = max((v for k, v in sc.items() if k != "troubleshooting"), default=0)
            primacy = ts / (runner + 0.01)          # how dominant is the mode
            if modes[0] != "troubleshooting":
                primacy *= 0.35                      # present but not the point
            substance = min(r["chars"] / 100000, 3)  # size helps, but is capped
            cands.append((primacy * 2 + substance, ts, primacy, r))
        cands.sort(key=lambda t: -t[0])
        print(f"RUNBOOK CANDIDATES — ranked by troubleshooting primacy ({len(cands)} total)\n")
        for _, ts, prim, r in cands[: args.limit]:
            print(fmt(r, show_evidence=False))
            print(f"        ts_density={ts}  primacy={prim:.1f}x over next mode  "
                  f"msgs={r.get('structure',{}).get('messages')}")
        strong = [c for c in cands if c[2] >= 1.5]
        print(f"\n  {len(cands)} contain troubleshooting; {len(strong)} have it as the dominant mode")
        print(f"  strong set = {sum(c[3]['chunks'] for c in strong):,} chunks, "
              f"{sum(c[3]['chars'] for c in strong)//1000:,}k chars")
        print("  -> the strong set is the raw material for runbook-to-rule-them-all")
        return 0

    if args.nuggets:
        scored = []
        for r in sel:
            s = r.get("structure") or {}
            hr = s.get("human_ratio") or 0
            avg = s.get("avg_human_msg") or 0
            modes = set(r.get("modes") or [])
            # you wrote a lot, at length, in a reflective or generative mode
            v = (hr * 2) + min(avg / 1000, 3)
            if modes & {"journal", "speculative", "idea"}:
                v += 2
            if r["chars"] > 40000:
                v += 1
            scored.append((v, r))
        scored.sort(key=lambda t: -t[0])
        print("GOLDEN NUGGETS — you wrote a lot, at length, in a generative mode\n")
        for v, r in scored[: args.limit]:
            print(fmt(r, show_evidence=True, show_scores=True))
        return 0

    order = {"date": lambda r: r.get("date") or "", "chars": lambda r: -r["chars"],
             "chunks": lambda r: -r["chunks"]}[args.sort]
    sel = sorted(sel, key=order)

    header = "UNCLASSIFIED" if args.unclassified else (args.mode or args.topic or "ALL").upper()
    print(f"{header} — {len(sel)} conversations "
          f"({sum(r['chunks'] for r in sel):,} chunks, {sum(r['chars'] for r in sel)//1000:,}k chars)\n")
    for r in sel[: args.limit]:
        print(fmt(r, show_evidence=True, show_scores=args.near_miss or args.unclassified))
    if len(sel) > args.limit:
        print(f"\n  ... {len(sel) - args.limit} more (raise --limit)")

    if args.unclassified:
        print("\nnear-miss summary — which mode came closest, and how far off:")
        gaps = Counter()
        for r in sel:
            sc = r.get("scores") or {}
            if sc:
                best, val = max(sc.items(), key=lambda kv: kv[1])
                gaps[f"{best} (best {val})"] += 1
        for k, n in gaps.most_common(10):
            print(f"   {n:>3}x  {k}")
        print("\n  dials: MIN_DENSITY (0.15) / MIN_HITS (2) / DENOM_FLOOR (3.0) in classify.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
