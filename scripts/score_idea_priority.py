#!/usr/bin/env python3
"""
Score idea cards into NOW / NEXT / ARCHIVE buckets.

Usage:
  # Single card
  python3 scripts/score_idea_priority.py --input path/to/idea.json --format text

  # Batch cards (top-level {"cards": [...]})
  python3 scripts/score_idea_priority.py --input docs/data/current_priority_layout.json --format text
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


DEFAULT_WEIGHTS = {
    "strategic_alignment": 1.4,
    "urgency": 1.1,
    "effort_inverse": 1.0,
    "evidence_strength": 1.1,
    "energy_match": 0.9,
}


def clamp_score(value: int) -> int:
    return max(0, min(5, int(value)))


def bucket_for_score(score: float) -> str:
    if score >= 18:
        return "NOW"
    if score >= 12:
        return "NEXT"
    return "ARCHIVE"


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def weighted_score(card: dict, weights: dict[str, float]) -> dict:
    factors = card.get("factors", {})
    normalized = {k: clamp_score(factors.get(k, 0)) for k in weights}

    component_scores = {
        name: normalized[name] * weights[name]
        for name in weights
    }
    total = round(sum(component_scores.values()), 2)
    bucket = bucket_for_score(total)

    return {
        "id": card.get("id", ""),
        "title": card.get("title", ""),
        "domain": card.get("domain", ""),
        "project": card.get("project", ""),
        "factors": normalized,
        "weights": weights,
        "components": component_scores,
        "total_score": total,
        "bucket": bucket,
    }


def render_text(result: dict) -> str:
    domain_line = ""
    if result.get("domain") or result.get("project"):
        domain_line = f" [{result.get('domain', '')}/{result.get('project', '')}]".rstrip("/")
    lines = [
        f"Idea: {result['title']} ({result['id']}){domain_line}",
        f"Bucket: {result['bucket']}",
        f"Total score: {result['total_score']}",
        "",
        "Components:",
    ]
    for name, score in result["components"].items():
        lines.append(f"- {name}: {score:.2f} (factor={result['factors'][name]})")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Score idea card priority.")
    parser.add_argument(
        "--input",
        required=True,
        help="Path to JSON card file (see docs/data/idea_priority_schema.json).",
    )
    parser.add_argument(
        "--format",
        choices=["json", "text"],
        default="json",
        help="Output format (default: json).",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=0,
        help="For batch input, show only top N cards (0 = all).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    card_path = Path(args.input).expanduser().resolve()

    if not card_path.exists():
        raise SystemExit(f"Input file not found: {card_path}")

    card = load_json(card_path)

    # Single-card mode
    if isinstance(card, dict) and "factors" in card:
        result = weighted_score(card, DEFAULT_WEIGHTS)
        if args.format == "text":
            print(render_text(result))
        else:
            print(json.dumps(result, indent=2))
        return 0

    # Batch mode: {"cards": [ ... ]}
    if isinstance(card, dict) and isinstance(card.get("cards"), list):
        results = [weighted_score(c, DEFAULT_WEIGHTS) for c in card["cards"]]
        results.sort(key=lambda x: x["total_score"], reverse=True)

        if args.top and args.top > 0:
            results = results[: args.top]

        if args.format == "text":
            print("Priority Ranking")
            print("================")
            for idx, r in enumerate(results, start=1):
                print(f"{idx}. {r['title']} ({r['id']})")
                if r.get("domain") or r.get("project"):
                    print(f"   Domain/Project: {r.get('domain', '')} / {r.get('project', '')}")
                print(f"   Bucket: {r['bucket']} | Score: {r['total_score']}")
            bucket_counts = {
                "NOW": sum(1 for r in results if r["bucket"] == "NOW"),
                "NEXT": sum(1 for r in results if r["bucket"] == "NEXT"),
                "ARCHIVE": sum(1 for r in results if r["bucket"] == "ARCHIVE"),
            }
            print("")
            print(f"Buckets -> NOW: {bucket_counts['NOW']}, NEXT: {bucket_counts['NEXT']}, ARCHIVE: {bucket_counts['ARCHIVE']}")
        else:
            print(json.dumps({"results": results}, indent=2))
        return 0

    raise SystemExit(
        "Input format not recognized. Provide either a single card with 'factors' "
        "or a batch object with top-level 'cards'."
    )


if __name__ == "__main__":
    raise SystemExit(main())
