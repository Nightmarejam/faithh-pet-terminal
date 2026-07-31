#!/usr/bin/env python3
"""Find hardcoded Chroma collection names and check each against the live instance.

Answers "how would I even spot this?" — the class of bug that produced a whole
day of debugging on 2026-07-31:

  * `get_collection("faithh_knowledge_base")` — real collection, but **384-dim**,
    while every embedder in this repo is BGE-768. Chroma rejects the query, the
    caller's `except` swallows it, and the feature silently degrades.
  * `get_or_create_collection("documents")` — no such collection anywhere, and
    get_or_create would happily CREATE one with Chroma's default 384-dim embedder,
    then get BGE vectors written into it.
  * `get_collection("alife_lineage")` — documented for months; does not exist.
  * `get_collection(collections[0].name)` — whichever Chroma lists first. Adding a
    sixth collection silently redirects live retrieval.

Static grep alone cannot catch these: the name looks fine in source. The check has
to ask the running instance what actually exists and at what dimension.

Exit 0 clean, 1 problems found, 2 could not reach Chroma.

Usage:
  python3 scripts/check_collections.py                 # scan repo root
  python3 scripts/check_collections.py --host servicebox.taileb8c60.ts.net
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request

EXPECTED_DIM = 768   # every embedder in this repo is BGE-base-en-v1.5

# get_collection("x") / get_or_create_collection(name="x") with a *literal* name.
LITERAL = re.compile(
    r"""get(?:_or_create)?_collection\(\s*(?:name\s*=\s*)?['"]([A-Za-z0-9_\-]+)['"]""")
# The "whichever is first" antipattern — no literal to check, but always wrong.
POSITIONAL = re.compile(r"collections\[\s*0\s*\]\s*\.\s*name")

SKIP_DIRS = {".git", "archive", "legacy", "node_modules", ".venv", "venv",
             "__pycache__", "chroma_db"}


def _prose_spans(text: str) -> list[tuple[int, int]]:
    """Character ranges of comments and string literals — i.e. not real code.

    Falls back to "nothing is prose" on a syntax error, which errs toward
    reporting rather than silently skipping a file.
    """
    import io
    import tokenize

    spans: list[tuple[int, int]] = []
    # Offset of the start of each 1-indexed line, for converting (row, col).
    starts = [0]
    for line in text.splitlines(keepends=True):
        starts.append(starts[-1] + len(line))

    def off(rc: tuple[int, int]) -> int:
        row, col = rc
        return starts[row - 1] + col if row - 1 < len(starts) else len(text)

    try:
        for tok in tokenize.generate_tokens(io.StringIO(text).readline):
            if tok.type in (tokenize.COMMENT, tokenize.STRING):
                spans.append((off(tok.start), off(tok.end)))
    except (tokenize.TokenError, IndentationError, SyntaxError):
        return []
    return spans


def live_collections(host: str, port: int) -> dict[str, int | None]:
    url = (f"http://{host}:{port}/api/v2/tenants/default_tenant"
           f"/databases/default_database/collections")
    with urllib.request.urlopen(url, timeout=15) as r:
        return {c["name"]: c.get("dimension") for c in json.loads(r.read())}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.path.join(os.path.dirname(__file__), ".."))
    ap.add_argument("--host", default=os.environ.get("CHROMA_HOST", "localhost"))
    ap.add_argument("--port", type=int, default=int(os.environ.get("CHROMA_PORT", "8000")))
    args = ap.parse_args()

    host = args.host.replace("http://", "").replace("https://", "").split(":")[0]

    try:
        live = live_collections(host, args.port)
    except (urllib.error.URLError, OSError, ValueError) as exc:
        print(f"CANNOT CHECK: Chroma unreachable at {host}:{args.port} — {exc}")
        return 2

    print(f"live collections on {host}:{args.port}")
    for n, d in sorted(live.items()):
        flag = "" if d in (None, EXPECTED_DIM) else f"  <-- {d}d, not {EXPECTED_DIM}d"
        print(f"   {n:34} {str(d):>6}{flag}")
    print()

    # Live serving paths vs one-off utilities. Both are reported, but a stale
    # reference in a 2026-03 backfill script is not the same emergency as one in
    # the request path, and lumping them together buries the ones that matter.
    def is_live(rel: str) -> bool:
        head = rel.replace("\\", "/").split("/")[0]
        return head in ("backend",) or "/" not in rel.replace("\\", "/")

    live_problems: list[str] = []
    util_problems: list[str] = []
    self_path = os.path.abspath(__file__)

    for dp, dirs, files in os.walk(os.path.abspath(args.root)):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fn in files:
            if not fn.endswith(".py"):
                continue
            path = os.path.join(dp, fn)
            if os.path.abspath(path) == self_path:
                continue      # this file's own docstring is full of examples
            rel = os.path.relpath(path, os.path.abspath(args.root))
            problems = live_problems if is_live(rel) else util_problems
            try:
                text = open(path, encoding="utf-8", errors="replace").read()
            except OSError:
                continue

            # Skip matches inside comments and string literals. Necessary because
            # every fix for these bugs quotes the bad call while explaining it —
            # without this the lint reports its own documentation as defects.
            # tokenize rather than a '#' heuristic, so docstrings are covered too.
            ignored = _prose_spans(text)

            def commented(pos: int) -> bool:
                return any(a <= pos < b for a, b in ignored)

            for m in LITERAL.finditer(text):
                if commented(m.start()):
                    continue
                name = m.group(1)
                line = text[:m.start()].count("\n") + 1
                if name not in live:
                    problems.append(f"{rel}:{line}  {name!r} does not exist")
                elif live[name] not in (None, EXPECTED_DIM):
                    problems.append(
                        f"{rel}:{line}  {name!r} is {live[name]}d, embedder is {EXPECTED_DIM}d")

            for m in POSITIONAL.finditer(text):
                if commented(m.start()):
                    continue
                line = text[:m.start()].count("\n") + 1
                problems.append(
                    f"{rel}:{line}  collections[0].name — arbitrary; adding a "
                    f"collection changes which one this hits")

    if live_problems:
        print(f"LIVE SERVING PATHS — {len(live_problems)} problem(s):\n")
        for p in live_problems:
            print("  " + p)
        print()
    if util_problems:
        print(f"one-off scripts / ml utilities — {len(util_problems)} problem(s)")
        print("  (historical backfills; stale but not in the request path)\n")
        for p in util_problems:
            print("  " + p)
        print()

    if live_problems:
        return 1
    if util_problems:
        print("Live paths are clean. Utility scripts still carry stale names.")
        return 0
    print("OK — every hardcoded collection exists at the expected dimension.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
