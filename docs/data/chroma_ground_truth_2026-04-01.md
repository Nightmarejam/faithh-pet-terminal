# ChromaDB Ground Truth — 2026-04-01

## Live counts (Gen8 — servicebox.taileb8c60.ts.net:8000)

  faithh_knowledge_base: 806,109
  alife_lineage:          50,450
  TOTAL:                 856,559

## Resolution of prior discrepancy

All document counts are on Gen8. Local Docker Chroma was empty and
unused — container and volume removed. Two stale embedded SQLite
files from January 2026 initial setup deleted:
- faithh_rag/chroma.sqlite3 (238MB, Jan 6)
- chroma_db/ directory (160KB + tier1/, Jan 6)

## Architecture confirmed

FAITHH backend `.env` points to `http://servicebox.taileb8c60.ts.net:8000` (Gen8 LAN).
Local Docker Chroma container removed. No competing local instances remain.

## Status

Safe to proceed with indexing: YES
Single source of truth: Gen8 ChromaDB
