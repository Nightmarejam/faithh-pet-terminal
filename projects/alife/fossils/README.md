# Fossil records — local, no database, comparable across locations

Answer to "do I need a database on the Mac?": **no.** Each run writes a local JSON
fossil with a SHA-256 fingerprint. Compare two locations by hash.

## The cross-location integrity check (Mac vs Gen8)
```bash
# On the Mac:
python3 fossil_run.py 5 --seed 42 --ticks 50000     # writes fossils/exp5_seed42.json

# Later, on Gen8, run the SAME seed, copy its fossil here, then:
python3 fossil_compare.py fossils/exp5_seed42.json gen8_exp5_seed42.json
#   IDENTICAL  → deterministic + both stores agree (integrity confirmed)
#   DIVERGED   → drills into which fields differ (code drift / non-determinism / discrepancy)
```

## Verified working (2026-07)
- Seeding fix makes exp5 **deterministic**: two same-seed runs → identical hash. This was
  the missing prerequisite — before, unseeded runs diverged by chance, so no comparison
  was even valid.
- Fossil = the experiment's summary results dict (wave/kill/emergence counts + timing).
  Enough for the divergence check. The FULL generational lineage (every birth/genome)
  still lives in the `alife_lineage` ChromaDB on Gen8 — review that separately when back.

## Note on scale
Short runs (hundreds of ticks) don't show Red Queen emergence — expected. The real
parasitic/arms-race dynamics need the full ~50k-tick runs. The harness saves results
so a long run's outcome is actually captured (the old scripts didn't — hence empty files).

*.json fossils here are regenerable outputs (gitignored); commit only reference baselines.
