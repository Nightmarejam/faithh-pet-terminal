# alife-core — the Rust port of the ALife sim (in progress)

Ported one piece at a time, each validated bit-for-bit against the Python original
(`../simulation.py`). The strategy decided up front (see homelab DETERMINISM_NOTES):
**bit-identical fossils across Rust ↔ Python ↔ Mac ↔ Gen8**, which requires reproducing
Python's exact RNG rather than using Rust's.

## Port progress
- ✅ **RNG** (`src/rng.rs`) — CPython's Mersenne Twister, bit-exact. `random()` and
  `randrange()` match Python for seeds 42 & 123 including rejection sampling. This is the
  determinism linchpin: without it, nothing downstream can hash-match. **Done & validated.**
- ⬜ **World** — the grid + energy field (next).
- ⬜ **Agent** — genome (bytes), energy (int), step logic.
- ⬜ **Simulation** — the tick loop (the hot path Rust is here for).
- ⬜ **Fossil output** — write the same JSONL the Python fossil tools already read.

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
