#!/usr/bin/env python3
"""
Rank inventory rows into governance/ALife/Constella indexing candidates.

Input:
  reports/inventory/combined_inventory.csv

Output:
  reports/inventory/index_candidates_governance_alife.csv
"""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


GOVERNANCE_KEYWORDS = (
    "governance",
    "constitution",
    "constitutional",
    "policy",
    "charter",
    "bylaws",
    "civic",
    "commons",
    "ostrom",
    "un ",
    "human rights",
    "participation",
    "institution",
)

ALIFE_KEYWORDS = (
    "alife",
    "artificial life",
    "genomic",
    "lineage",
    "experiment",
    "predator",
    "diversity floor",
    "strategy escape",
    "ucf",
    "penumbra",
    "gamer",
)

CONSTELLA_KEYWORDS = (
    "constella",
    "civic_tome",
    "penumbra_accord",
    "astris",
    "auctor",
    "ucf",
)

EXTENSION_BONUS = {
    ".md": 4.0,
    ".txt": 2.0,
    ".json": 2.5,
    ".yaml": 2.0,
    ".yml": 2.0,
    ".csv": 1.0,
    ".pdf": 1.5,
}

ALLOWED_EXTENSIONS = {".md", ".txt", ".json", ".yaml", ".yml", ".csv", ".pdf"}

EXCLUDE_SUBSTRINGS = (
    "cinebench",
    "invoice",
    "receipt",
    "tax_filing",
    "cpa_package",
    "insurance_policy",
    "bitwarden_export",
    "expired_example_cookies",
)


def score_row(path: str, extension: str) -> tuple[float, str]:
    lower = path.lower()
    score = 0.0
    label = "other"

    if any(x in lower for x in EXCLUDE_SUBSTRINGS):
        return 0.0, "other"

    if extension and extension.lower() not in ALLOWED_EXTENSIONS:
        return 0.0, "other"

    gov_hits = sum(1 for k in GOVERNANCE_KEYWORDS if k in lower)
    alife_hits = sum(1 for k in ALIFE_KEYWORDS if k in lower)
    constella_hits = sum(1 for k in CONSTELLA_KEYWORDS if k in lower)
    exp_n_hits = len(re.findall(r"\bexp\s*[_-]?\s*[0-9]{1,2}[a-z]?\b", lower))

    score += EXTENSION_BONUS.get(extension.lower(), 0.0)
    score += gov_hits * 3.0
    score += alife_hits * 3.0
    score += constella_hits * 2.5
    score += exp_n_hits * 2.5

    if "archive" in lower or "backup" in lower:
        score -= 1.0

    if gov_hits > 0 and gov_hits >= alife_hits:
        label = "governance"
    elif alife_hits > 0 or exp_n_hits > 0:
        label = "alife"
    elif constella_hits > 0:
        label = "governance"

    return score, label


def target_metadata(label: str, path: str) -> tuple[str, str]:
    lower = path.lower()
    if label == "alife":
        if lower.endswith(".json"):
            return "alife", "alife_experiment"
        return "alife", "synthesis_document"
    # governance / constella
    if "constella" in lower:
        return "constella_constitutional", "synthesis_document"
    return "constella_constitutional", "synthesis_document"


def main() -> None:
    parser = argparse.ArgumentParser(description="Mine governance/ALife index candidates from inventory CSV")
    parser.add_argument(
        "--input",
        default="reports/inventory/combined_inventory.csv",
        help="Input combined inventory CSV",
    )
    parser.add_argument(
        "--output",
        default="reports/inventory/index_candidates_governance_alife.csv",
        help="Output candidate CSV",
    )
    parser.add_argument("--min-score", type=float, default=5.0, help="Minimum score threshold")
    parser.add_argument("--limit", type=int, default=5000, help="Maximum candidates to emit")
    args = parser.parse_args()

    input_csv = Path(args.input)
    output_csv = Path(args.output)
    output_csv.parent.mkdir(parents=True, exist_ok=True)

    if not input_csv.exists():
        raise FileNotFoundError(f"Input CSV not found: {input_csv}")

    candidates = []
    with input_csv.open("r", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            path = row.get("path", "")
            ext = row.get("extension", "")
            score, label = score_row(path, ext)
            if label not in ("governance", "alife") or score < args.min_score:
                continue

            target_domain, target_source_type = target_metadata(label, path)
            candidates.append(
                {
                    "path": path,
                    "size_bytes": row.get("size_bytes", ""),
                    "modified_at_utc": row.get("modified_at_utc", ""),
                    "extension": ext,
                    "source_host": row.get("source_host", ""),
                    "domain_guess": label,
                    "score": f"{score:.2f}",
                    "include_for_index": "review",
                    "target_domain": target_domain,
                    "target_source_type": target_source_type,
                    "sensitivity": "internal",
                }
            )

    candidates.sort(key=lambda r: float(r["score"]), reverse=True)
    candidates = candidates[: args.limit]

    fields = [
        "path",
        "size_bytes",
        "modified_at_utc",
        "extension",
        "source_host",
        "domain_guess",
        "score",
        "include_for_index",
        "target_domain",
        "target_source_type",
        "sensitivity",
    ]
    with output_csv.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(candidates)

    print(f"Candidates written: {output_csv}")
    print(f"Count: {len(candidates)}")
    if candidates:
        print("Top candidate:", candidates[0]["path"], "score=", candidates[0]["score"])


if __name__ == "__main__":
    main()
