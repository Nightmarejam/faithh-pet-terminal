#!/usr/bin/env python3
"""Shared synthesis core for RunBook seeding scripts."""

from __future__ import annotations

import json
import re
from datetime import datetime, UTC
from typing import Any


def slugify(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value or "seed"


def normalize_tags(query: str, metadatas: list[dict[str, Any]]) -> list[str]:
    tags: set[str] = set()
    for word in re.findall(r"[a-zA-Z0-9_]+", query.lower()):
        if len(word) >= 4:
            tags.add(word)
    for md in metadatas:
        for key in ("category", "domain", "source_type", "document_type", "experiment"):
            val = md.get(key)
            if isinstance(val, str) and val:
                tags.add(slugify(val))
    cleaned = [t for t in sorted(tags) if t]
    return cleaned[:8] if cleaned else ["seeded", "runbook"]


def query_collections(
    client: Any,
    query: str,
    collection_names: list[str],
    max_chunks: int,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for name in collection_names:
        try:
            col = client.get_collection(name)
        except Exception:
            continue
        res = col.query(query_texts=[query], n_results=max_chunks)
        ids = (res.get("ids") or [[]])[0]
        docs = (res.get("documents") or [[]])[0]
        mets = (res.get("metadatas") or [[]])[0]
        dists = (res.get("distances") or [[]])[0]
        for idx, doc_id in enumerate(ids):
            md = mets[idx] if idx < len(mets) and isinstance(mets[idx], dict) else {}
            doc = docs[idx] if idx < len(docs) and isinstance(docs[idx], str) else ""
            dist = dists[idx] if idx < len(dists) and isinstance(dists[idx], (int, float)) else None
            score = 1.0 / (1.0 + float(dist)) if isinstance(dist, (int, float)) else 0.0
            rows.append(
                {
                    "collection": name,
                    "document_id": str(doc_id),
                    "score": round(score, 6),
                    "distance": float(dist) if isinstance(dist, (int, float)) else None,
                    "excerpt": doc[:360].strip(),
                    "metadata": md,
                }
            )
    rows.sort(key=lambda r: r["score"], reverse=True)
    return rows[:max_chunks]


def suggest_steps(query: str, evidence: list[dict[str, Any]]) -> list[str]:
    base = [
        "Clarify intent and success criteria for this runbook objective.",
        "Validate prerequisites and environment readiness before execution.",
        "Execute the core workflow in a reproducible, logged sequence.",
        "Run verification checks and collect quantitative outcomes.",
        "Record outcomes and update run history with artifacts and deviations.",
    ]
    if "alife" in query.lower():
        base[2] = "Execute ALife generation workflow with explicit parameters and report capture."
        base[3] = "Verify Chroma count delta and compare quality metrics against baseline."
    if evidence:
        top = evidence[0]
        col = top.get("collection", "collection")
        base.insert(1, f"Pull high-signal context from `{col}` semantic search results.")
    return base[:6]


def build_seed(query: str, evidence: list[dict[str, Any]]) -> dict[str, Any]:
    now = datetime.now(UTC)
    date = now.strftime("%Y-%m-%d")
    slug = slugify(query)[:56]
    seed_id = f"runbook-seed-{slug}"
    tags = normalize_tags(query, [e.get("metadata", {}) for e in evidence])
    title = " ".join(word.capitalize() for word in query.strip().split()) + " (seeded draft)"
    steps = suggest_steps(query, evidence)
    prereqs = [
        "Required data sources are reachable (ChromaDB or local artifacts).",
        "Execution environment and dependencies are available.",
        "Operator has access to write run history artifacts.",
    ]
    verification = [
        "Execution completes without blocking errors.",
        "At least one measurable output artifact is produced.",
        "Observed metrics are recorded in run history notes.",
    ]

    return {
        "version": "v0.1",
        "generated_at": now.isoformat(),
        "query": query,
        "seed_id": seed_id,
        "title": title,
        "intent": f"Seed a reproducible runbook flow for: {query}.",
        "tags": tags,
        "prerequisites": prereqs,
        "suggested_steps": steps,
        "verification_checks": verification,
        "known_failure_modes": [
            "Inputs are unavailable or stale.",
            "Environment mismatch causes script or command failure.",
            "Metrics artifact is produced but missing required fields.",
        ],
        "notes": [
            "This is a seeded draft; refine language and ordering before promotion.",
            "Use run history updates to harden this from draft to verified.",
        ],
        "source_evidence": evidence,
        "runbook_frontmatter_suggestion": {
            "id": f"{date}-{slug}",
            "title": title.replace(" (seeded draft)", ""),
            "tags": tags[:5],
            "status": "draft",
            "replicated_by": [],
            "sandbox_ref": "",
            "created": date,
            "last_verified": date,
            "constella": True,
        },
        "future_stacking": {
            "suggested_prereq_ids": [],
            "suggested_next_ids": [],
            "learning_objective_tags": tags[:4],
        },
    }


def validate_seed(seed: dict[str, Any]) -> dict[str, Any]:
    required = [
        "version",
        "generated_at",
        "query",
        "seed_id",
        "title",
        "intent",
        "tags",
        "prerequisites",
        "suggested_steps",
        "verification_checks",
        "source_evidence",
        "runbook_frontmatter_suggestion",
        "future_stacking",
    ]
    issues: list[str] = []
    missing = [k for k in required if k not in seed]
    if missing:
        issues.append(f"Missing required fields: {', '.join(missing)}")
    evidence_ok = isinstance(seed.get("source_evidence"), list) and len(seed["source_evidence"]) > 0
    if not evidence_ok:
        issues.append("source_evidence must be non-empty")
    steps = seed.get("suggested_steps", [])
    step_count_ok = isinstance(steps, list) and 3 <= len(steps) <= 12
    if not step_count_ok:
        issues.append("suggested_steps must contain between 3 and 12 items")

    validation = {
        "required_fields_ok": len(missing) == 0,
        "source_evidence_non_empty": evidence_ok,
        "step_count_ok": step_count_ok,
        "issues": issues,
    }
    seed["validation"] = validation
    return validation


def seed_to_markdown(seed: dict[str, Any]) -> str:
    fm = seed["runbook_frontmatter_suggestion"]
    lines = [
        "---",
        f"id: {fm['id']}",
        f"title: \"{fm['title']}\"",
        "tags:",
    ]
    for t in fm["tags"]:
        lines.append(f"  - {t}")
    lines.extend(
        [
            f"status: {fm['status']}",
            "replicated_by: []",
            "sandbox_ref: \"\"",
            f"created: {fm['created']}",
            f"last_verified: {fm['last_verified']}",
            f"constella: {str(fm['constella']).lower()}",
            "---",
            "",
            "## Intent",
            "",
            seed["intent"],
            "",
            "## Prerequisites",
            "",
        ]
    )
    for p in seed["prerequisites"]:
        lines.append(f"- {p}")
    lines.extend(["", "## Steps", ""])
    for i, s in enumerate(seed["suggested_steps"], start=1):
        lines.append(f"{i}. {s}")
    lines.extend(["", "## Verification", ""])
    for v in seed["verification_checks"]:
        lines.append(f"- {v}")
    lines.extend(["", "## Run history", "", "- YYYY-MM-DD — outcome: partial — artifacts: TBD — notes: seeded draft"])
    lines.extend(["", "## Known failure modes", ""])
    for k in seed["known_failure_modes"]:
        lines.append(f"- {k}")
    lines.extend(["", "## Notes", ""])
    for n in seed["notes"]:
        lines.append(f"- {n}")
    lines.extend(["", "## Source evidence (seed)", ""])
    for e in seed["source_evidence"]:
        lines.append(f"- `{e['collection']}/{e['document_id']}` score={e['score']}: {e['excerpt']}")
    return "\n".join(lines) + "\n"


def write_seed_outputs(seed: dict[str, Any], json_path: Path, md_path: Path) -> None:
    json_path.write_text(json.dumps(seed, indent=2), encoding="utf-8")
    md_path.write_text(seed_to_markdown(seed), encoding="utf-8")
