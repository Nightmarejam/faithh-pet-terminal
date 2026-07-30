#!/usr/bin/env python3
"""Export alife_lineage from Chroma into SQLite.

Why: alife_lineage is 339,900 rows of per-agent-per-tick simulation telemetry —
72% of the whole vector store. The documents are templated renderings of the
numbers ("Band2 agent B_00 pop=B tick=11: signal=0.49 resources=1.37 ..."), so
embedding them discards the numbers and keeps a sentence that looks like 339,899
other sentences. Cosine similarity cannot discriminate; the real questions are
`fitness > 0.8`, `generation = 10`, `GROUP BY noise_amp` — filters and aggregates.

This is non-destructive. It only reads from Chroma. Deleting the collection is a
separate, deliberate step, and should only happen after `--verify` passes.

Schema note: the metadata is heterogeneous (agent events carry genome/energy
fields, population snapshots carry aggregates, only 1.8% carry flag_reason), so a
wide table would be mostly NULL. Core queryable fields become real indexed
columns; everything else lands in a JSON column, queryable via json_extract().

Usage:
    python scripts/alife/export_to_sqlite.py --out data/alife_lineage.sqlite
    python scripts/alife/export_to_sqlite.py --out data/alife_lineage.sqlite --verify
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import sqlite3
import sys

BATCH = 5000
COLLECTION = os.environ.get("ALIFE_COLLECTION", "alife_lineage")

# Promoted to real columns because these are what you filter and group by.
CORE = [
    ("chroma_id", "TEXT"),
    ("event_type", "TEXT"),
    ("experiment", "TEXT"),
    ("tick", "INTEGER"),
    ("generation", "INTEGER"),
    ("agent_id", "TEXT"),
    ("parent_id", "TEXT"),
    ("population", "TEXT"),
    ("flagged", "INTEGER"),
    ("fitness", "REAL"),
    ("resources", "REAL"),
    ("noise_amp", "REAL"),
]

DDL = f"""
CREATE TABLE IF NOT EXISTS lineage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    {', '.join(f'{n} {t}' for n, t in CORE)},
    document TEXT,
    meta TEXT              -- full original metadata as JSON
);
CREATE INDEX IF NOT EXISTS ix_event      ON lineage(event_type);
CREATE INDEX IF NOT EXISTS ix_experiment ON lineage(experiment);
CREATE INDEX IF NOT EXISTS ix_generation ON lineage(generation);
CREATE INDEX IF NOT EXISTS ix_agent      ON lineage(agent_id);
CREATE INDEX IF NOT EXISTS ix_flagged    ON lineage(flagged);
CREATE INDEX IF NOT EXISTS ix_exp_gen    ON lineage(experiment, generation);
"""


def connect_chroma():
    import chromadb

    host = os.environ.get("CHROMA_HOST", "localhost")
    port = int(os.environ.get("CHROMA_PORT", "8000"))
    return chromadb.HttpClient(host=host, port=port)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, help="SQLite file to write")
    ap.add_argument("--verify", action="store_true",
                    help="after export, compare row count to Chroma and print a summary")
    ap.add_argument("--limit", type=int, default=0, help="stop after N rows (smoke test)")
    args = ap.parse_args()

    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    client = connect_chroma()
    col = client.get_collection(COLLECTION)
    total = col.count()
    print(f"{COLLECTION}: {total:,} documents in Chroma")

    db = sqlite3.connect(out)
    db.executescript(DDL)
    # Durability is irrelevant for a rebuildable export; this is much faster.
    db.execute("PRAGMA journal_mode=OFF")
    db.execute("PRAGMA synchronous=OFF")

    existing = db.execute("SELECT COUNT(*) FROM lineage").fetchone()[0]
    if existing:
        print(f"table already holds {existing:,} rows — clearing for a clean export")
        db.execute("DELETE FROM lineage")
        db.commit()

    cols = [n for n, _ in CORE] + ["document", "meta"]
    sql = f"INSERT INTO lineage ({','.join(cols)}) VALUES ({','.join('?' * len(cols))})"

    written = 0
    offset = 0
    while True:
        batch = col.get(limit=BATCH, offset=offset, include=["documents", "metadatas"])
        ids = batch.get("ids") or []
        if not ids:
            break
        docs = batch.get("documents") or []
        metas = batch.get("metadatas") or []
        rows = []
        for i, cid in enumerate(ids):
            m = metas[i] if i < len(metas) and metas[i] else {}
            doc = docs[i] if i < len(docs) else None
            row = [cid]
            for name, _ in CORE[1:]:
                v = m.get(name)
                if name == "flagged":
                    v = int(bool(v)) if v is not None else None
                elif name in ("experiment", "population", "agent_id", "parent_id") and v is not None:
                    v = str(v)
                row.append(v)
            row.append(doc)
            row.append(json.dumps(m, sort_keys=True, default=str))
            rows.append(row)
        db.executemany(sql, rows)
        db.commit()
        written += len(rows)
        offset += BATCH
        print(f"  {written:,}/{total:,}", end="\r", flush=True)
        if args.limit and written >= args.limit:
            print(f"\nstopping at --limit {args.limit}")
            break
        if written >= total:
            break

    print(f"\nwrote {written:,} rows to {out}  ({out.stat().st_size / 1e6:.1f} MB)")

    if args.verify:
        n = db.execute("SELECT COUNT(*) FROM lineage").fetchone()[0]
        match = "MATCH" if n == total else "MISMATCH"
        print(f"\nverify: sqlite={n:,}  chroma={total:,}  -> {match}")
        print("\nrows by event_type:")
        for et, cnt in db.execute(
            "SELECT COALESCE(event_type,'(none)'), COUNT(*) FROM lineage "
            "GROUP BY 1 ORDER BY 2 DESC"
        ):
            print(f"   {et:<26}{cnt:>9,}")
        print("\nanalytically interesting (snapshots + flags):")
        keep = db.execute(
            "SELECT COUNT(*) FROM lineage WHERE event_type LIKE '%snapshot%' "
            "OR event_type LIKE 'flag%' OR flagged=1"
        ).fetchone()[0]
        print(f"   {keep:,} rows  ({100 * keep / max(1, n):.2f}%)")
        print("\nexample query the vector store could never answer well:")
        for r in db.execute(
            "SELECT experiment, generation, ROUND(AVG(fitness),4) AS mean_fitness, COUNT(*) n "
            "FROM lineage WHERE fitness IS NOT NULL "
            "GROUP BY experiment, generation ORDER BY generation LIMIT 8"
        ):
            print("  ", r)
        if n != total:
            return 1

    db.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
