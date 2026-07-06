# ALife — a minimal ecology for studying emergence

**In one line:** strip the rules of a world down to almost nothing — energy, threat, a
gradient, decay — drop in agents with tiny genomes, and watch what evolves. The bet:
*simple rules generate seemingly infinite possibility.*

> Part of a personal AI ecosystem — see the [ecosystem map](https://github.com/Nightmarejam).
> Research-grade sandbox; results are intrinsically valuable independent of applications.
> Human-directed, AI-assisted, with receipts (confirmability tiers throughout).

---

## The idea (one concept)

A rich model of the universe would *confound* emergence — you couldn't tell whether
complex behavior came from evolution or from physics you baked in. So this world is
deliberately **minimal**: a grid where cells hold energy (food), threat (predator waves),
light (a gradient), and a slow thermal drain. Agents are 8-byte genomes (sense / process /
memory / act / regulate). A run "succeeds" when it produces **something the experimenter
did not predict from the rules.**

## What's here

- `simulation.py`, `world.py`, `agent.py`, `ops.py` — the Python sim (works today).
- `experiments/` — exp0 primordial → exp5 parasitic (Red Queen) → exp6-9 (cultural/diversity).
- `alife-core/` — the **Rust port** (fast + bit-exact) — see its README for progress.
- `fossil_run.py` / `fossil_compare.py` — seeded runs → hashed local fossil records
  (cross-location integrity checks; no database needed).
- **Docs (read these for the thinking):**
  - `WORLD_DESIGN_LINEAGE.md` — the design's trail and whether it holds up
  - `SANDBOX_REVIEW.md` — honest audit: real sandbox, results not yet all confirmed
  - `NOMENCLATURE_PIPELINE.md` — how emergent terms become a usable vocabulary/dataset

## Status (honest, tiered)

- **Sandbox & design:** ✅ hold up — sound minimal-emergence complexity science.
- **Rust port:** 🔨 RNG + World + Agent/population all **validated bit-for-bit** vs Python;
  the tick loop (ops + orchestration) is the remaining mechanical piece.
- **Results (anticipation, Red Queen, cultural transmission):** ⚠️ mostly `asserted` —
  they need seeded re-runs at scale to become `confirmed`. That's what the Rust port buys.

## How it connects to FAITHH

Loose coupling by design: **ALife exports a validated vocabulary dataset** (the
nomenclature pipeline), and **FAITHH imports it** into its knowledge base — always
carrying the tiers (concept confirmed in-sim; any human mapping stays speculative). ALife
doesn't live inside FAITHH; it produces a knowledge artifact FAITHH reads.

## Roadmap

1. Finish the Rust tick loop (validated by multi-tick state hash).
2. Run seeded exp5–9 at 50k-tick scale → confirm the asserted results.
3. Nomenclature pipeline → the exported dataset → FAITHH ingestion.
4. Future track: convergence of "cultural universals" across independent populations.
