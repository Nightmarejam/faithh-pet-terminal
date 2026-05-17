#!/usr/bin/env python3
"""
Index ALife experiment JSONs + synthesis markdown into faithh_knowledge_base
using explicit all-MiniLM-L6-v2 (CPU) embeddings.
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Any

os.environ["CUDA_VISIBLE_DEVICES"] = ""

import chromadb

BASE = Path("/home/jonat/ai-stack")
GENOMIC = BASE / "genomic_results"
FINDINGS_MD = BASE / "docs/constella_stress_tests/ALIFE_FINDINGS.md"
TRACK_B_MD = BASE / "docs/constella_stress_tests/TRACK_B_OVERVIEW.md"
EVIDENCE_MAP_MD = (
    BASE / "projects/constella-framework/docs/governance/alife_evidence_mapping.md"
)

CHROMA_HOST = os.getenv("CHROMA_HOST", "192.158.1.10")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8000"))
COLLECTION_NAME = "faithh_knowledge_base"

EXPERIMENT_FILES = [
    ("exp5", "exp5_parasitic_drain15_results.json", "alife_exp5_core"),
    ("exp6", "exp6_ucf_floor_results.json", "alife_exp6_core"),
    ("exp7", "exp7_ucf_gated_results.json", "alife_exp7_core"),
    ("exp8b", "exp8b_strategy_escape_results.json", "alife_exp8b_core"),
    ("exp9", "exp9_diversity_floor_results.json", "alife_exp9_core"),
]

UPSERT_BATCH = 64
EMBED_BATCH = 32


def _fmt_obj(label: str, obj: Any, indent: str = "") -> list[str]:
    out: list[str] = []
    if obj is None:
        return out
    if isinstance(obj, str):
        out.append(f"{indent}{label}: {obj}")
    elif isinstance(obj, (int, float, bool)):
        out.append(f"{indent}{label}: {obj}")
    elif isinstance(obj, dict):
        out.append(f"{indent}{label}:")
        for k, v in obj.items():
            out.extend(_fmt_obj(str(k), v, indent + "  "))
    elif isinstance(obj, list):
        out.append(f"{indent}{label}:")
        for i, item in enumerate(obj[:20]):
            out.extend(_fmt_obj(f"[{i}]", item, indent + "  "))
        if len(obj) > 20:
            out.append(f"{indent}  ... ({len(obj) - 20} more items)")
    else:
        out.append(f"{indent}{label}: {obj!r}")
    return out


def format_experiment_document(exp: str, data: dict[str, Any]) -> str:
    """Build readable text from heterogeneous experiment JSON shapes."""
    lines: list[str] = []

    name = data.get("experiment", f"Experiment {exp}")
    lines.append(f"Experiment: {name}")
    lines.append("")

    # Outcome / code
    outcome_code = data.get("outcome_code")
    if outcome_code is None and "result" in data and isinstance(data["result"], dict):
        outcome_code = data["result"].get("outcome_code")
    if data.get("outcome"):
        lines.append(f"Outcome: {data['outcome']}")
    elif "result" in data and isinstance(data["result"], dict):
        r = data["result"]
        if r.get("collapsed"):
            lines.append(f"Outcome: COLLAPSE (tick {r.get('collapse_tick')})")
        else:
            lines.append("Outcome: No collapse reported in result block")
        if r.get("outcome_code"):
            lines.append(f"Outcome code: {r['outcome_code']}")
    elif data.get("collapsed") is not None:
        lines.append(
            f"Outcome: {'COLLAPSE' if data['collapsed'] else 'SURVIVED'}"
        )
    if outcome_code and "Outcome code:" not in "\n".join(lines):
        lines.append(f"Outcome code: {outcome_code}")

    # Key metrics (pull from top level or nested result)
    src = data
    if "result" in data and isinstance(data["result"], dict):
        src = {**data, **data["result"]}

    fp = src.get("final_population", data.get("final_population"))
    ct = src.get("collapse_tick", data.get("collapse_tick"))
    wc = src.get("wave_count", data.get("wave_count"))
    pk = src.get("predator_kills", data.get("predator_kills"))
    tr = src.get("total_reproductions")
    if tr is None:
        tr = src.get("total_reproduction_events")
    if tr is None:
        tr = data.get("total_reproductions") or data.get(
            "total_reproduction_events"
        )

    lines.append("")
    lines.append("Key metrics:")
    if fp is not None:
        lines.append(f"  Final population: {fp}")
    if ct is not None:
        lines.append(f"  Collapse tick: {ct}")
    else:
        lines.append("  Collapse tick: (none — survived or not applicable)")
    if wc is not None:
        lines.append(f"  Wave count: {wc}")
    if pk is not None:
        lines.append(f"  Predator kills: {pk}")
    if tr is not None:
        lines.append(f"  Total reproductions: {tr}")

    # Constella implications (various keys)
    lines.append("")
    lines.append("Constella implications / mapping:")
    constella_bits: list[str] = []

    if data.get("constella_implications"):
        constella_bits.extend(
            _fmt_obj("constella_implications", data["constella_implications"])
        )
    analysis = data.get("analysis")
    if isinstance(analysis, dict) and analysis.get("constella_mapping"):
        constella_bits.extend(
            _fmt_obj(
                "constella_mapping",
                analysis["constella_mapping"],
            )
        )
    if data.get("constella_design_decision"):
        constella_bits.extend(
            _fmt_obj(
                "constella_design_decision",
                data["constella_design_decision"],
            )
        )
    if data.get("track_b_implications"):
        constella_bits.extend(
            _fmt_obj("track_b_implications", data["track_b_implications"])
        )
    if constella_bits:
        lines.extend(constella_bits)
    else:
        lines.append("  (none present in this JSON)")

    # Decision field(s)
    lines.append("")
    lines.append("Decision:")
    dec = data.get("decision")
    if dec is None and isinstance(data.get("constella_design_decision"), dict):
        dec = data["constella_design_decision"].get("decision")
    if dec:
        if isinstance(dec, str):
            lines.append(f"  {dec}")
        else:
            lines.extend(_fmt_obj("decision", dec, "  "))
    else:
        lines.append("  (none present in this JSON)")

    # Exp 8b: brief condition summary
    if exp == "exp8b" and isinstance(data.get("conditions"), dict):
        lines.append("")
        lines.append("Conditions summary:")
        for ck, cv in data["conditions"].items():
            if not isinstance(cv, dict):
                continue
            lines.append(f"  {ck}:")
            lines.append(
                f"    collapsed={cv.get('collapsed')}, "
                f"collapse_tick={cv.get('collapse_tick')}, "
                f"final_population={cv.get('final_population')}"
            )

    return "\n".join(lines).strip()


def split_findings_by_headers(md: str) -> list[str]:
    """
    Split ALIFE_FINDINGS.md into sections at ## or ### line starts.
    (File uses ### Exp N / ## Section; avoids splitting every ** line.)
    """
    lines = md.splitlines(keepends=True)
    chunks: list[list[str]] = []
    current: list[str] = []
    header_re = re.compile(r"^(##|###)\s+")

    for line in lines:
        if header_re.match(line) and current:
            chunks.append(current)
            current = [line]
        else:
            current.append(line)
    if current:
        chunks.append(current)

    texts = ["".join(c).strip() for c in chunks if "".join(c).strip()]
    return texts


def load_text(path: Path) -> str:
    if not path.is_file():
        print(f"ERROR: missing file {path}", file=sys.stderr)
        sys.exit(1)
    return path.read_text(encoding="utf-8")


def main() -> None:
    from sentence_transformers import SentenceTransformer

    embedder = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")
    client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    col = client.get_collection(COLLECTION_NAME)

    records: list[tuple[str, str, dict[str, Any]]] = []

    # Part 1 — experiment JSONs
    for exp_key, fname, doc_id in EXPERIMENT_FILES:
        path = GENOMIC / fname
        data = json.loads(load_text(path))
        if not isinstance(data, dict):
            print(f"ERROR: {path} root must be object", file=sys.stderr)
            sys.exit(1)
        body = format_experiment_document(exp_key, data)
        meta = {
            "domain": "alife",
            "source_type": "alife_experiment",
            "document_type": "experiment_result",
            "quality_score": 0.95,
            "category": "project_docs",
            "experiment": exp_key,
        }
        records.append((doc_id, body, meta))

    # Part 2 — ALIFE_FINDINGS.md chunks + full
    findings_raw = load_text(FINDINGS_MD)
    sections = split_findings_by_headers(findings_raw)
    for i, sec in enumerate(sections, start=1):
        rid = f"alife_findings_pattern_{i}"
        meta = {
            "domain": "alife",
            "source_type": "synthesis_document",
            "document_type": "finding",
            "quality_score": 0.97,
            "category": "project_docs",
        }
        records.append((rid, sec, meta))

    meta_full = {
        "domain": "alife",
        "source_type": "synthesis_document",
        "document_type": "finding",
        "quality_score": 0.97,
        "category": "project_docs",
    }
    records.append(("alife_findings_full", findings_raw.strip(), meta_full))

    # Part 3 — two overview markdown files
    for doc_id, path in (
        ("alife_track_b_overview", TRACK_B_MD),
        ("alife_evidence_mapping", EVIDENCE_MAP_MD),
    ):
        meta = {
            "domain": "alife",
            "source_type": "synthesis_document",
            "document_type": "overview",
            "quality_score": 0.97,
            "category": "project_docs",
        }
        records.append((doc_id, load_text(path).strip(), meta))

    ids = [r[0] for r in records]
    documents = [r[1] for r in records]
    metadatas = [r[2] for r in records]

    embeddings: list[list[float]] = []
    for i in range(0, len(documents), EMBED_BATCH):
        batch = documents[i : i + EMBED_BATCH]
        emb = embedder.encode(batch, show_progress_bar=False)
        embeddings.extend(emb.tolist())

    for i in range(0, len(ids), UPSERT_BATCH):
        col.upsert(
            ids=ids[i : i + UPSERT_BATCH],
            embeddings=embeddings[i : i + UPSERT_BATCH],
            documents=documents[i : i + UPSERT_BATCH],
            metadatas=metadatas[i : i + UPSERT_BATCH],
        )

    print(f"Upserted {len(ids)} documents into {COLLECTION_NAME}.")

    # Verification (HttpClient count() has no where-filter; use get + len)
    limit = max(col.count(), 1)
    n_alife = len(
        col.get(where={"domain": "alife"}, limit=limit, include=[])["ids"]
    )
    n_exp = len(
        col.get(
            where={
                "$and": [
                    {"domain": {"$eq": "alife"}},
                    {"source_type": {"$eq": "alife_experiment"}},
                ]
            },
            limit=limit,
            include=[],
        )["ids"]
    )
    print(f"Count domain=alife: {n_alife}")
    print(
        f"Count domain=alife AND source_type=alife_experiment: {n_exp}"
    )


if __name__ == "__main__":
    main()
