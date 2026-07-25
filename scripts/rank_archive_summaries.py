#!/usr/bin/env python3
"""
Rank synthesized archive summaries and output manual review queue CSV.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


KEYWORDS = {
    "alife": ["alife", "genomic", "experiment", "diversity floor", "strategy escape", "lineage"],
    "governance": ["governance", "constitution", "constitutional", "policy", "charter", "un ", "ostrom"],
    "constella": ["constella", "penumbra", "ucf", "civic tome", "astris", "auctor"],
    "faithh": ["faithh", "retrieval", "index", "rag", "chroma", "embedding"],
}


def score(text: str) -> tuple[float, list[str]]:
    t = text.lower()
    total = 0.0
    tags: list[str] = []
    for topic, kws in KEYWORDS.items():
        hits = sum(1 for k in kws if k in t)
        if hits > 0:
            tags.append(topic)
            total += hits * 2.5
    if len(text) > 400:
        total += 1.0
    return total, tags


def main() -> None:
    parser = argparse.ArgumentParser(description="Rank archive summaries for review")
    parser.add_argument(
        "--input",
        default="/home/jonat/ai-stack/reports/inventory/archive_summaries.jsonl",
    )
    parser.add_argument(
        "--output",
        default="/home/jonat/ai-stack/reports/inventory/archive_review_queue.csv",
    )
    parser.add_argument("--min-score", type=float, default=4.0)
    args = parser.parse_args()

    inp = Path(args.input)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)

    if not inp.exists():
        raise FileNotFoundError(inp)

    rows = []
    for line in inp.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        s, tags = score(rec.get("summary_text", ""))
        if s < args.min_score:
            continue
        target_domain = (
            "alife"
            if "alife" in tags
            else "constella_constitutional"
            if "governance" in tags or "constella" in tags
            else "faithh_core"
        )
        rows.append(
            {
                "conversation_id": rec.get("conversation_id", ""),
                "title": rec.get("title", ""),
                "created_at": rec.get("created_at", ""),
                "source_file": rec.get("source_file", ""),
                "score": f"{s:.2f}",
                "topic_tags": "|".join(tags),
                "include_for_index": "review",
                "target_domain": target_domain,
                "target_source_type": "archive_synthesis",
                "sensitivity": "internal",
            }
        )

    rows.sort(key=lambda r: float(r["score"]), reverse=True)
    fields = list(rows[0].keys()) if rows else [
        "conversation_id",
        "title",
        "created_at",
        "source_file",
        "score",
        "topic_tags",
        "include_for_index",
        "target_domain",
        "target_source_type",
        "sensitivity",
    ]

    with out.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Output: {out}")
    print(f"Rows: {len(rows)}")


if __name__ == "__main__":
    main()
