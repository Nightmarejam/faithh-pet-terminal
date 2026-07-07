# alife-core — the Rust port of the ALife sim (in progress)

Ported one piece at a time, each validated bit-for-bit against the Python original
(`../simulation.py`). The strategy decided up front (see homelab DETERMINISM_NOTES):
**bit-identical fossils across Rust ↔ Python ↔ Mac ↔ Gen8**, which requires reproducing
Python's exact RNG rather than using Rust's.

## Port progress
- ✅ **RNG** (`src/rng.rs`) — CPython's Mersenne Twister, bit-exact. `random()` and
  `randrange()` match Python for seeds 42 & 123 including rejection sampling. This is the
  determinism linchpin: without it, nothing downstream can hash-match. **Done & validated.**
- ✅ **World** — grid + energy field + sources + regen. **VALIDATED** bit-for-bit:
  Rust & Python both hash `76aae69c71538657` for seed 42 (345,600 init draws + 20 sources
  match exactly). Port spec — the exact RNG order that
  must match Python (verified 2026-07):**
  1. seed set FIRST, then World() built → init is deterministic (good).
  2. Grid row-major (y outer, x inner). Each Cell consumes IN ORDER:
     `energy = 50 + randbelow(101)`, then `light = 100 + randbelow(101)`. → 480×360×2
     = 345,600 randbelow calls.
  3. Then energy sources: 20× ( randbelow(480), randbelow(360) ) = 40 calls.
  4. `initialize_light_gradient` is NOT called by the base sim — random cell values stand.
  Validate: hash the energy grid after init; Rust hash must equal Python's.
- ✅ **Agent + population** — genome, energy, spawn. **VALIDATED**: seed 42 →
  `2c9aa438ca75cf3f` both langs (full chain seed→World→50 agents matches bit-for-bit).
  Remaining: the per-tick genome *execution* logic (sense/act/reproduce/mutate).
- ✅ **Simulation (tick loop)** — **DONE & VALIDATED bit-for-bit.** Full port: all 40
  ops, _execute_genome orchestration, reproduction, mutation, death. Rust==Python at
  ticks 1/10/50/100 (pop grows 61→64→117→177 identically). **~70× faster** (500 ticks:
  Rust 0.28s vs Python 19.7s). Root-cause bug found & fixed via staged hashing:
  MEMORY_ENABLED=false forces MEM_NONE (memory clears each tick).

- ✅ **Fossil output** — DONE. `run <seed> <ticks> fossil` writes fossils/*.json; Rust
  fossil hash == Python (a2bb005395f79766 @ seed42/100t). **PORT COMPLETE — bit-exact, ~70× faster.**

## Validate the RNG yourself
```bash
cargo run --release            # prints values + asserts they match Python
# compare against:
python3 -c "import random; random.seed(42); print([random.random() for _ in range(6)])"
```

## Why RNG first
The whole point of the port is fossils that hash-match across languages and machines.
The RNG is the one component where a single wrong draw cascades into total divergence, so
it had to be exact and it had to be first. It is. Everything else (integer energy, byte
genomes, discrete mutation) is naturally cross-platform reproducible — so the hard part of
determinism is now behind us.
