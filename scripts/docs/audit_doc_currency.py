#!/usr/bin/env python3
"""Audit the documents that receive the tier-1 retrieval boost for stale claims.

Why this exists: improving retrieval raised the cost of stale documentation. While
retrieval was broken a wrong document was harmless — nothing could find it. Now that
docs/ carries the authoritative-tier boost, gets reassembled whole, and is cited by
name, a confidently wrong document outranks the one that corrects it. Three documents
asserted a 384-dim embedder, which is the configuration that produces
`best_distance: 1.0` on every query — they described the bug as if it were the design.

Age is not the signal here: 243 of 244 boosted docs are under 90 days old. What
matters is whether a document asserts something we have since verified false.

Each rule below is a fact that changed, with the evidence for what is true now.
Add a rule whenever a verified fact changes — that is what keeps this useful.

Usage:
    python scripts/docs/audit_doc_currency.py
    python scripts/docs/audit_doc_currency.py --severity high
"""
from __future__ import annotations

import argparse
import pathlib
import re
import subprocess
import sys
from collections import defaultdict

REPO = pathlib.Path(__file__).resolve().parents[2]

# Documents allowed to mention a term because they explain its history. Keyed by rule
# id so an exemption is narrow rather than blanket.
ALLOW: dict[str, set[str]] = {
    "embedder-384": {
        "AGENTS.md",
        "docs/architecture/SYSTEM_TRANSPARENCY_IMPLEMENTATION_CHECKLIST.md",
        "docs/architecture/EMBEDDINGS.md",
        "docs/architecture/VECTOR_STORE_REVIEW.md",
        "docs/consolidated/SYSTEM_OVERVIEW.md",
        "docs/architecture/SYSTEM_OVERVIEW.md",
        "docs/guides/QUICKSTART.md",
    },
    "legacy-collection": {
        "AGENTS.md",
        "docs/FAITHH_STACK_RUNBOOK.md",      # labels it "legacy" correctly
        "docs/ENVIRONMENT_SPEC.md",          # documents both, correctly
        "docs/architecture/ACTIVE_INDEXING_PIPELINE.md",
        "docs/architecture/INFRASTRUCTURE.md",
        "docs/architecture/EMBEDDINGS.md",
        "docs/architecture/VECTOR_STORE_REVIEW.md",
        "docs/consolidated/SYSTEM_OVERVIEW.md",
        "docs/architecture/SYSTEM_OVERVIEW.md",
        "docs/guides/QUICKSTART.md",
    },
    "alife-live": {
        "docs/architecture/VECTOR_STORE_REVIEW.md",
        "docs/consolidated/SYSTEM_OVERVIEW.md",
    },
    "ollama-default": {
        "docs/consolidated/SYSTEM_OVERVIEW.md",
        "docs/architecture/GEN8_POWER_CONSTRAINT.md",
        "docs/architecture/FAITHH_REDESIGN.md",
        "docs/architecture/EMBEDDINGS.md",
    },
    "dead-subnet": set(),
    "retired-groq-model": set(),
    "consolidated-context-docs": {"docs/consolidated/SYSTEM_OVERVIEW.md"},
    "dead-category-field": {"docs/architecture/EMBEDDINGS.md"},
}

RULES = [
    {
        "id": "embedder-384",
        "severity": "high",
        "pattern": re.compile(r"all-MiniLM-L6-v2|384[- ]dim", re.I),
        "why": "Live embedder is BAAI/bge-base-en-v1.5 (768-dim). A 384-dim embedder "
               "against faithh_knowledge_base_v2 yields best_distance 1.0 on every query.",
        "ref": "docs/architecture/EMBEDDINGS.md",
    },
    {
        "id": "legacy-collection",
        "severity": "high",
        # faithh_knowledge_base NOT followed by _v2
        "pattern": re.compile(r"faithh_knowledge_base(?!_v2)\b"),
        "why": "Primary collection is faithh_knowledge_base_v2. The unsuffixed one is "
               "legacy 384-dim and not comparable with the live query embedder.",
        "ref": "docs/architecture/EMBEDDINGS.md",
    },
    {
        "id": "dead-subnet",
        "severity": "high",
        "pattern": re.compile(r"192\.158\.\d+\.\d+"),
        "why": "192.158.* was a typo for 192.168.* and was never routable. Any literal "
               "using it is dead by definition. Prefer MagicDNS names.",
        "ref": "AGENTS.md",
    },
    {
        "id": "alife-live",
        "severity": "medium",
        "pattern": re.compile(r"alife_lineage"),
        "why": "alife_lineage was exported to SQLite and deleted from Chroma on "
               "2026-07-30. Queries against it now fail.",
        "ref": "docs/architecture/VECTOR_STORE_REVIEW.md",
    },
    {
        "id": "ollama-default",
        "severity": "medium",
        "pattern": re.compile(r"ollama", re.I),
        "why": "Nothing serves :11434 on the Gen8; local inference is vLLM on the RTX "
               "3090. Check whether this document presents Ollama as active.",
        "ref": "docs/architecture/GEN8_POWER_CONSTRAINT.md",
    },
    {
        "id": "retired-groq-model",
        "severity": "medium",
        "pattern": re.compile(r"qwen/qwen3-32b"),
        "why": "Retired by Groq; returns 404. Verified against the live model list "
               "2026-07-28.",
        "ref": "configs/model_config.yaml",
    },
    {
        "id": "consolidated-context-docs",
        "severity": "low",
        "pattern": re.compile(r"\b(CONTEXT|MASTER_CONTEXT|CURSOR_CONTEXT)\.md\b"),
        "why": "Consolidated into AGENTS.md, the single live context file.",
        "ref": "AGENTS.md",
    },
    {
        "id": "dead-category-field",
        "severity": "low",
        "pattern": re.compile(r"category['\"]?\s*[:=]\s*['\"]?project_docs"),
        "why": "category is set on zero documents; the authoritative tier keys on "
               "document_type == 'architecture_doc'.",
        "ref": "docs/architecture/EMBEDDINGS.md",
    },
]

SEV_ORDER = {"high": 0, "medium": 1, "low": 2}

# A dated filename marks a point-in-time snapshot, per the documentation convention in
# AGENTS.md §8: plain names for living docs, dates in filenames for snapshots. A
# snapshot describing the collection as it was in April is correct, not stale — it is
# a record. Only living documents are expected to track current state.
SNAPSHOT_NAME = re.compile(r"\d{4}[-_]\d{2}([-_]\d{2})?")
# Likewise, a document whose body is explicitly a dated record.
SNAPSHOT_BODY = re.compile(
    r"^\s*(>?\s*)?\*{0,2}(recorded|snapshot|as of|captured|sample run)\b", re.I | re.M
)


def is_snapshot(rel: str, text: str) -> bool:
    return bool(SNAPSHOT_NAME.search(pathlib.Path(rel).name)) or bool(
        SNAPSHOT_BODY.search(text[:1500])
    )


def boosted_docs() -> list[pathlib.Path]:
    """Same corpus scripts/ingest/index_docs.py indexes as architecture_doc."""
    out: list[pathlib.Path] = []
    for p in (REPO / "docs").rglob("*.md"):
        parts = set(p.parts)
        if parts & {"archive", "node_modules", ".git", "__pycache__"}:
            continue
        if "/data/" in p.as_posix():
            continue
        out.append(p)
    for name in ("AGENTS.md", "README.md", "CLAUDE.md"):
        f = REPO / name
        if f.is_file():
            out.append(f)
    return sorted(set(out))


def last_commit(rel: str) -> str:
    r = subprocess.run(
        ["git", "log", "-1", "--format=%ad", "--date=short", "--", rel],
        cwd=REPO, capture_output=True, text=True,
    )
    return r.stdout.strip() or "untracked"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--severity", choices=["high", "medium", "low"], default="low",
                    help="minimum severity to report (default: low = everything)")
    args = ap.parse_args()
    floor = SEV_ORDER[args.severity]

    findings: dict[str, list[tuple[dict, int, str]]] = defaultdict(list)
    docs = boosted_docs()

    skipped_snapshots = 0
    for p in docs:
        rel = p.relative_to(REPO).as_posix()
        try:
            body = p.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        if is_snapshot(rel, body):
            skipped_snapshots += 1
            continue
        lines = body.splitlines()
        for rule in RULES:
            if SEV_ORDER[rule["severity"]] > floor:
                continue
            if rel in ALLOW.get(rule["id"], set()):
                continue
            for n, line in enumerate(lines, 1):
                if rule["pattern"].search(line):
                    findings[rel].append((rule, n, line.strip()[:110]))
                    break  # one hit per rule per file is enough to flag it

    print(f"tier-1 boosted documents scanned: {len(docs)}")
    print(f"dated snapshots skipped (records, not live docs): {skipped_snapshots}")
    print(f"documents with stale claims:      {len(findings)}\n")

    if not findings:
        print("no stale claims found")
        return 0

    def worst(rel: str) -> tuple[int, int]:
        rules = [f[0] for f in findings[rel]]
        return (min(SEV_ORDER[r["severity"]] for r in rules), -len(rules))

    for rel in sorted(findings, key=worst):
        print(f"{rel}   (last commit {last_commit(rel)})")
        for rule, n, text in sorted(findings[rel], key=lambda f: SEV_ORDER[f[0]["severity"]]):
            print(f"   [{rule['severity']:<6}] {rule['id']}  line {n}")
            print(f"            {text}")
            print(f"            -> {rule['why']}")
        print()

    high = sum(1 for r in findings for f in findings[r] if f[0]["severity"] == "high")
    print(f"high-severity findings: {high}")
    return 1 if high else 0


if __name__ == "__main__":
    sys.exit(main())
