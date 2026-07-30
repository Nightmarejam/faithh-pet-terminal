#!/usr/bin/env python3
"""Index the repo's markdown documentation into the live Chroma collection.

Why not scripts/indexing/index_faithh_kb_markdown.py: that one calls
`collection.upsert(ids, documents, metadatas)` with no `embeddings`, which makes the
Chroma *server* embed. The server's default embedder is not BGE. If it produced
768-wide vectors from a different model, they would pass every dimension check while
being semantically incomparable to everything else in the collection — silent
corruption that no guard would catch. So embed client-side, explicitly, with the
same model the backend queries with.

See docs/architecture/EMBEDDINGS.md.

Safety:
  * refuses to write if the embedder's width differs from the collection's
  * deterministic ids (docs_{slug}_{n}) so re-running updates instead of duplicating
  * --dry-run prints what would be written and touches nothing

Usage:
    python scripts/ingest/index_docs.py --dry-run
    python scripts/ingest/index_docs.py
"""
from __future__ import annotations

import argparse
import os
import pathlib
import re
import sys

MODEL = os.environ.get("FAITHH_EMBEDDER_MODEL", "BAAI/bge-base-en-v1.5")
COLLECTION = os.environ.get("CHROMA_COLLECTION", "faithh_knowledge_base_v2")
CHROMA_HOST = os.environ.get("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.environ.get("CHROMA_PORT", "8000"))

# Prose chunking. Bigger than rag_processor's 500-char default: architecture docs
# reason across paragraphs, and 500 chars splits mid-argument, which is how you get
# retrievable fragments that individually say nothing.
CHUNK_CHARS = 1400
OVERLAP = 200
BATCH = 64

ROOTS = ["docs", "."]           # "." picks up top-level AGENTS.md / README.md only
TOP_LEVEL_ONLY = {"AGENTS.md", "README.md", "CLAUDE.md"}
SKIP_DIRS = {"archive", "node_modules", ".git", "__pycache__", "llama.cpp", ".venv", "venv"}


def discover(repo: pathlib.Path) -> list[pathlib.Path]:
    out: list[pathlib.Path] = []
    for p in (repo / "docs").rglob("*.md"):
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        out.append(p)
    for name in TOP_LEVEL_ONLY:
        p = repo / name
        if p.is_file():
            out.append(p)
    return sorted(set(out))


def split_markdown(text: str) -> list[str]:
    """Split on H2 boundaries, then hard-wrap anything still oversized.

    Heading-aware first so a chunk usually corresponds to one section, which keeps
    the retrieved excerpt self-explanatory.
    """
    sections = re.split(r"\n(?=## )", text)
    chunks: list[str] = []
    for sec in sections:
        sec = sec.strip()
        if not sec:
            continue
        if len(sec) <= CHUNK_CHARS:
            chunks.append(sec)
            continue
        start = 0
        while start < len(sec):
            chunks.append(sec[start : start + CHUNK_CHARS])
            start += CHUNK_CHARS - OVERLAP
    return chunks


def slug(rel: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", rel.lower()).strip("_")


# A record describes what was true when it was written; a living document is expected
# to track current state. Both belong in the repo — deleting records loses history —
# but they must not compete equally in retrieval. A PHASE2 completion report was
# getting the same tier-1 boost as EMBEDDINGS.md, so a question about the current
# embedder could be answered from a report about April.
#
# Same rules as scripts/docs/audit_doc_currency.py, which skips records for the same
# reason. Keep the two in sync.
RECORD_NAME = re.compile(
    r"(\d{4}[-_]\d{2}([-_]\d{2})?|PHASE\d|_STATUS|_REPORT|COMPLETION|_ANALYSIS|RELEVANCY)",
    re.I,
)
# A record declares itself in its header, not incidentally in prose. Scanning the whole
# body with a line-anchored pattern misfired: GEN8_POWER_CONSTRAINT.md contains
# a doc whose prose happened to wrap the word "recorded" to the start of a line.
# GEN8_POWER_CONSTRAINT.md hit exactly that, was typed doc_record, lost its
# tier-1 boost, and dropped out of retrieval for the question it answers.
# start of a line, the doc was typed doc_record, lost its tier-1 boost, and dropped out
# of retrieval for the exact question it answers. Header only.
RECORD_HEADER_LINES = 12
RECORD_BODY = re.compile(
    r"^\s*(>?\s*)?\*{0,2}(recorded|snapshot|as of|captured|sample run)\b", re.I | re.M
)


def is_record(rel: str, text: str) -> bool:
    header = "\n".join(text.splitlines()[:RECORD_HEADER_LINES])
    return bool(RECORD_NAME.search(pathlib.Path(rel).name)) or bool(RECORD_BODY.search(header))


def is_reference(rel: str) -> bool:
    """External source material, not FAITHH's own documentation.

    docs/data/ holds imported primary sources — the UN Charter, the Universal
    Declaration of Human Rights, the US Constitution, V-Dem codebooks, third-party
    API manuals. They are worth retrieving, but they are not design decisions about
    this system, and giving them the same authority as an ADR means a question about
    FAITHH's architecture can be answered from the UN Charter.
    """
    return "/data/" in rel or rel.startswith("data/")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--repo", default=str(pathlib.Path(__file__).resolve().parents[2]))
    args = ap.parse_args()

    repo = pathlib.Path(args.repo)
    files = discover(repo)
    if not files:
        print("no markdown found", file=sys.stderr)
        return 1

    records = []
    for f in files:
        rel = f.relative_to(repo).as_posix()
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            print(f"  skip {rel}: {e}")
            continue
        if not text.strip():
            continue
        if is_reference(rel):
            doc_type = "reference_doc"
        elif is_record(rel, text):
            doc_type = "doc_record"
        else:
            doc_type = "architecture_doc"
        for i, chunk in enumerate(split_markdown(text)):
            records.append({
                "id": f"docs_{slug(rel)}_{i}",
                "document": f"# {rel}\n\n{chunk}",
                "metadata": {
                    "source": "repo_docs",
                    "path": rel,
                    "title": f.stem,
                    "chunk_index": i,
                    # architecture_doc = living, carries the tier-1 boost and is
                    # eligible for whole-document expansion.
                    # doc_record      = historical; retrievable, but must not outrank
                    #                   a living document about current state.
                    "document_type": doc_type,
                },
            })

    print(f"{len(files)} files -> {len(records)} chunks")
    for f in files:
        print(f"   {f.relative_to(repo).as_posix()}")

    if args.dry_run:
        print("\n--dry-run: nothing written")
        print("\nsample chunk:")
        print("  " + records[0]["document"][:300].replace("\n", "\n  "))
        return 0

    import chromadb
    from sentence_transformers import SentenceTransformer

    client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    col = client.get_collection(COLLECTION)

    # Refuse on width mismatch, before writing anything.
    pk = col.peek(limit=1)
    pe = pk.get("embeddings")
    col_dim = len(pe[0]) if pe is not None and len(pe) > 0 and pe[0] is not None else None

    device = os.environ.get("FAITHH_EMBED_DEVICE") or "cpu"
    model = SentenceTransformer(MODEL, device=device)
    emb_dim = model.get_sentence_embedding_dimension()
    print(f"\nembedder {MODEL} -> {emb_dim}-dim (device={device})")
    print(f"collection {COLLECTION} -> {col_dim}-dim, {col.count():,} docs")

    if col_dim is not None and col_dim != emb_dim:
        print(
            f"\nREFUSING TO WRITE: {COLLECTION} holds {col_dim}-dim vectors, "
            f"{MODEL} produces {emb_dim}-dim.\n"
            "See docs/architecture/EMBEDDINGS.md",
            file=sys.stderr,
        )
        return 2

    before = col.count()
    for s in range(0, len(records), BATCH):
        part = records[s : s + BATCH]
        embs = model.encode(
            [r["document"] for r in part], batch_size=32, show_progress_bar=False
        ).tolist()
        col.upsert(
            ids=[r["id"] for r in part],
            documents=[r["document"] for r in part],
            metadatas=[r["metadata"] for r in part],
            embeddings=embs,
        )
        print(f"  {min(s + BATCH, len(records))}/{len(records)}", end="\r", flush=True)

    after = col.count()
    print(f"\ncollection {before:,} -> {after:,} (+{after - before:,} new, "
          f"{len(records) - (after - before)} updated in place)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
