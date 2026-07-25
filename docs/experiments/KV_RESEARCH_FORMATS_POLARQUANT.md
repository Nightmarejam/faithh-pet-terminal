# Research KV formats (e.g. PolarQuant) vs llama.cpp today

**Purpose:** Answer “do I need kernel changes to use Google-style / PolarQuant KV?” and record **where this repo stands** after the Python experiments.

---

## Short answers

| Approach | In `llama-server` today? | Kernel / C++ work? |
|----------|-------------------------|-------------------|
| **f16 / q8_0 / q4_0** KV (`--cache-type-k` / `-v`) | **Yes** | **No** (already in llama.cpp + GGML) |
| **PolarQuant** (packed polar angles + radii, ~4× vs fp16 KV) | **No** | **Yes — substantial** |

There is **no flag** like `--cache-type-k polar` in stock llama.cpp. PolarQuant is a **different representation** of key vectors than scalar int8/int4 quant.

---

## What PolarQuant is (conceptually)

From the paper / reference write-ups (e.g. *PolarQuant: Quantizing KV Caches with Polar Transformation*, Chen et al., arXiv:2502.02617) and the CUDA walkthrough in `vendor/polar_quant/README.md`:

1. **Random rotation** of each key vector (fixed matrix, dimension e.g. 128).
2. **Recursive polar pairing** (multiple levels) → angles + a small set of **radii**.
3. **Quantize angles** with **codebooks** matched to the **known angle distributions** after rotation.
4. **Pack** into a small record (~62 bytes / 128-d key in the tutorial layout).

Inference wants either:

- **Decode** packed → fp16/fp32 K, then usual attention, or  
- **Fused kernel:** compute **Q·K** (or part of attention) **directly from packed form** without full decode (what the B200 tutorial optimizes).

Both paths require **custom GPU (or highly tuned CPU) code**, not just a new `q*_0` block quant on existing KV buffers.

---

## What would have to change in llama.cpp (high level)

This is **not** a small patch; think **fork + sustained work**:

1. **New KV storage type** in GGML / backend (layout, alignment, `ggml_type`-like handling or parallel path).
2. **Encode path** when writing K (after projection): rotation → polar → quantize → pack. (Could start CPU-side; production usually wants GPU.)
3. **Attention read path:** either dequant to fp16 for existing `flash_attn` / CUDA matmuls, or **replace** the dot-product path with a **PolarQuant-aware kernel** per head dim / layout.
4. **`llama-server` CLI** and API: new cache type names, buffer sizing, possibly V-cache policy (PolarQuant write-ups often focus on **K**; V may stay q8/f16 unless you extend the method).
5. **Validation:** parity / perplexity vs f16 KV, same as you did for q8_0 — but against a **new** stack.

**Reference CUDA:** `vendor/polar_quant/` — tutorial kernels, **not** a llama.cpp plugin. Treat as spec + math validation, not a drop-in library.

---

## Where **this repo** stands

| Artifact | Meaning |
|----------|---------|
| `scripts/polar_quant_experiment.py` + `experiment_a_results.json` | **Offline** quality vs a block-q4 *toy* on HF K vectors; **~4×** nominal packing matches paper layout; does **not** prove llama attention behavior. |
| `scripts/extract_kv_vectors.py` | Realistic **Qwen2-shaped** K/V samples for analysis. |
| Chat ablation + `KV_ABLATION_SUMMARY.md` | **Shippable today:** **f16 / q4_0 / q8_0** KV in real `llama-server`. |
| `vendor/polar_quant` | Upstream **CUDA teaching** repo; clone for reading / future porting only. |

**Conclusion:** To “use PolarQuant” in production inference you are looking at **llama.cpp (or another engine) fork + CUDA/GGML integration**, not configuration. Until then, the **highest-value usable knob** for KV is **`q8_0`** (or f16 / q4_0) on **`llama-server`**.

---

## If you pursue integration later (checklist)

- [ ] Confirm target **head_dim** (128) and **GQA** layout match your kernels.  
- [ ] Decide: **K-only** PolarQuant first, V stays q8/f16.  
- [ ] Prototype **decode-to-f16** path before fused Q·K (easier correctness).  
- [ ] Run the same **chat ablation** + **VRAM** scripts against the fork.  
- [ ] Track upstream llama.cpp KV / flash-attn changes (merge cost).

---

## Related docs

- `docs/experiments/KV_CACHE_QUANT_BENCHMARK_20260405.md` — measured VRAM + chat ablation + choosing f16/q8/q4.  
- `docs/experiments/KV_EXPERIMENT_REPRO_CHECKLIST.md` — how to re-run comparisons fairly.
