# KV chat ablation — auto summary

Exact **match vs f16** = identical assistant string at `temperature=0` (strict).
See `KV_CACHE_QUANT_BENCHMARK_20260405.md` for qualitative notes (e.g. prompt 0).

### Context 8192

| profile | exact match vs f16 | mean latency (ms) | mean Δ latency vs f16 |
|---------|-------------------:|------------------:|------------------------:|
| f16 | 5/5 | 3484.6 | +0.0 |
| q4_0 | 0/5 | 3094.6 | -390.0 |
| q8_0 | 0/5 | 3701.9 | +217.3 |

**Heuristic:** Same exact-match count (0/5) for q4_0 vs q8_0 at ctx 8192. Prefer **q8_0** if spot-checks look closer to f16; else **q4_0** for maximum KV savings.

### Context 32768

| profile | exact match vs f16 | mean latency (ms) | mean Δ latency vs f16 |
|---------|-------------------:|------------------:|------------------------:|
| f16 | 5/5 | 3487.1 | +0.0 |
| q4_0 | 0/5 | 3110.1 | -377.0 |
| q8_0 | 0/5 | 3710.1 | +223.0 |

**Heuristic:** Same exact-match count (0/5) for q4_0 vs q8_0 at ctx 32768. Prefer **q8_0** if spot-checks look closer to f16; else **q4_0** for maximum KV savings.

