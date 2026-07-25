#!/usr/bin/env python3
"""
Build NAS classification queue from full inventory.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def _path_segments_lower(path: str) -> list[str]:
    return [s for s in path.lower().split("/") if s]


def classify_domain_group(path: str) -> str:
    p = path.lower()
    # Business first so explicit business roots are not overridden by a "personal" segment elsewhere.
    if any(k in p for k in ("/tomcat sound llc/", "/business/", "cpa_package", "tax_filing")):
        return "business"
    if "personal" in _path_segments_lower(path):
        return "personal"
    if any(k in p for k in ("/volume1/ai/", "/volume1/projects/", "/volume1/raw_ingest/", "/volume1/archive/")):
        return "shared"
    return "unknown"


def classify_ingestion_scope(path: str) -> tuple[str, float]:
    p = path.lower()
    gov_hits = sum(
        1
        for k in (
            "govern",
            "constit",
            "charter",
            "policy",
            "civic",
            "ostrom",
            "rights",
            "united_nations",
        )
        if k in p
    )
    alife_hits = sum(
        1
        for k in ("alife", "genom", "lineage", "experiment", "exp_", "exp-", "diversity_floor", "strategy_escape")
        if k in p
    )
    constella_hits = sum(1 for k in ("constella", "penumbra", "ucf", "astris", "auctor", "civic_tome") if k in p)

    if gov_hits >= max(alife_hits, constella_hits) and gov_hits > 0:
        return "governance", gov_hits * 1.5
    if alife_hits >= max(gov_hits, constella_hits) and alife_hits > 0:
        return "alife", alife_hits * 1.5
    if constella_hits > 0:
        return "constella", constella_hits * 1.5
    return "exclude", 0.0


def classify_sensitivity(path: str, domain_group: str) -> str:
    p = path.lower()
    if domain_group == "personal":
        return "private"
    if any(k in p for k in ("tax", "invoice", "receipt", "insurance", "ssn", "bank", "payroll")):
        return "private"
    if any(k in p for k in ("legal", "policy", "constitution", "charter", "governance", "alife", "constella")):
        return "internal"
    return "internal"


def _sanitize_relative_relpath(rel: str) -> str:
    """Collapse . / .. and drop empty parts; never allow escaping above the target root."""
    parts: list[str] = []
    for part in Path(rel).as_posix().split("/"):
        if not part or part == ".":
            continue
        if part == "..":
            if parts:
                parts.pop()
            continue
        parts.append(part)
    return "/".join(parts)


def _volume1_tail_relative(path: str) -> str:
    """Path under /volume1/ preserving case; empty if not under /volume1/."""
    posix = Path(path).as_posix()
    marker = "/volume1/"
    idx = posix.lower().find(marker)
    if idx == -1:
        return ""
    tail = posix[idx + len(marker) :]
    return _sanitize_relative_relpath(tail)


def _strip_leading_personal_segment(rel: str) -> str:
    """Avoid Personal/... duplication when staging under Personal/_review."""
    parts = rel.split("/")
    if parts and parts[0].lower() == "personal":
        return "/".join(parts[1:])
    return rel


def move_target(path: str, ingestion_scope: str, domain_group: str) -> str:
    rel = _volume1_tail_relative(path)
    if not rel:
        rel = _sanitize_relative_relpath(Path(path).name)
    if domain_group == "personal":
        under_review = _strip_leading_personal_segment(rel)
        return f"/volume1/Personal/_review/{under_review}"
    if ingestion_scope == "governance":
        return f"/volume1/projects/governance_corpus/{rel}"
    if ingestion_scope == "alife":
        return f"/volume1/projects/alife_corpus/{rel}"
    if ingestion_scope == "constella":
        return f"/volume1/projects/constella_corpus/{rel}"
    return f"/volume1/projects/shared_reference/{rel}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Build NAS classification queue")
    parser.add_argument(
        "--input",
        default="/home/jonat/ai-stack/reports/inventory/nas_full_inventory.csv",
    )
    parser.add_argument(
        "--output",
        default="/home/jonat/ai-stack/reports/inventory/nas_classification_queue.csv",
    )
    parser.add_argument("--auto-approve-score", type=float, default=3.0)
    args = parser.parse_args()

    inp = Path(args.input)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    if not inp.exists():
        raise FileNotFoundError(inp)

    rows = list(csv.DictReader(inp.open("r", encoding="utf-8")))
    out_rows = []
    for row in rows:
        path = row.get("path", "")
        dg = classify_domain_group(path)
        scope, score = classify_ingestion_scope(path)
        sens = classify_sensitivity(path, dg)
        target = move_target(path, scope, dg)
        status = (
            "approved"
            if dg != "personal" and scope in {"governance", "alife", "constella"} and sens != "private" and score >= args.auto_approve_score
            else "pending"
        )
        if dg == "personal":
            status = "blocked"

        out_rows.append(
            {
                **row,
                "domain_group": dg,
                "ingestion_scope": scope,
                "sensitivity": sens,
                "move_target": target,
                "review_status": status,
                "score": f"{score:.2f}",
            }
        )

    fields = [
        "path",
        "size_bytes",
        "modified_at_utc",
        "extension",
        "source_host",
        "domain_group",
        "ingestion_scope",
        "sensitivity",
        "move_target",
        "review_status",
        "score",
    ]
    with out.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(out_rows)

    print(f"Output: {out}")
    print(f"Rows: {len(out_rows)}")
    approved = sum(1 for r in out_rows if r["review_status"] == "approved")
    blocked = sum(1 for r in out_rows if r["review_status"] == "blocked")
    print(f"Approved: {approved}  Blocked: {blocked}")


if __name__ == "__main__":
    main()
