# KV cache quantization benchmark (llama.cpp)

**Date:** 2026-04-05 (run / capture in agent session)  
**Model:** `qwen25-grounded-gen5-delta:latest` — Qwen2 14.8B, Q4_K_M, GGUF  
**Target hardware:** RTX 3090 24GB, `CUDA_VISIBLE_DEVICES=0`  
**Goal:** Compare VRAM and viability of long context with `--cache-type-k` / `--cache-type-v` (or Python server `--type_k` / `--type_v`) vs default f16 KV.

**Note (2026-04-11):** FAITHH’s documented default grounded tag is **`qwen25-grounded:latest`**. This runbook keeps **`qwen25-grounded-gen5-delta:latest`** where it names the exact GGUF artifact used for these measurements.

**Ollama daily driver:** Same idea via **`OLLAMA_KV_CACHE_TYPE`** + **`OLLAMA_FLASH_ATTENTION`** on the **Ollama server** — see **[`docs/guides/OLLAMA_KV_ENV.md`](../guides/OLLAMA_KV_ENV.md)**.

---

## Operator runbook (CUDA toolkit + CUDA `llama-server`) — 2026-04-06

**Agent status:** `sudo` was not available in the automation session, so **CUDA toolkit was not installed** and **llama.cpp was not rebuilt** here. `nvcc` is still missing; `~/llama.cpp/build` has a partial CMake tree with `CUDAToolkit_NVCC_EXECUTABLE-NOTFOUND`.

**On your machine, run in order:**

1. **Install CUDA Toolkit 12.8 (WSL / Ubuntu 22.04)** — needs sudo:
   ```bash
   cd /home/jonat/ai-stack
   bash scripts/install_cuda_toolkit_wsl2204.sh
   ```
   Then add `PATH` / `LD_LIBRARY_PATH` / `CUDA_HOME` to `~/.bashrc` as printed by the script, open a new shell, and confirm `nvcc --version`.

2. **Build llama.cpp with CUDA (sm_86):**
   ```bash
   bash scripts/build_llama_cpp_cuda.sh
   ```
   Produces `~/llama.cpp/build/bin/llama-server` and symlinks `~/.local/bin/llama-server` (and `llama-cli`).

3. **VRAM / KV benchmark** (does **not** call Ollama `DELETE` — that can remove blobs from disk):
   ```bash
   export CUDA_VISIBLE_DEVICES=0
   OLLAMA_MODEL_REF=qwen25-grounded-gen5-delta:latest bash scripts/run_llama_kv_cache_benchmark.sh
   ```
   Paste the printed **MiB** lines into the results table below (four rows: f16 8K, q4_0 8K, **f16 32K**, q4_0 32K). If any case returns `ERR`, note **OOM** or failure in the table.

4. **Optional:** use `-ngl all` instead of `-ngl 99` if your `llama-server --help` lists `all` for full GPU offload.

### Troubleshooting (WSL2 / llama-server b8683+)

| Symptom | Cause | Fix |
|--------|--------|-----|
| `ggml_cuda_init: failed to initialize CUDA: no CUDA-capable device` | `CUDA_VISIBLE_DEVICES` unset or wrong in **this** shell | Export `CUDA_VISIBLE_DEVICES=0` (or the correct GPU index) before starting `llama-server`; the benchmark script does this by default. |
| `torch.cuda` / PyTorch: “No CUDA GPUs are available” in the same session | Same as above — PyTorch also honors `CUDA_VISIBLE_DEVICES` | Use `CUDA_VISIBLE_DEVICES=0 python3 ...` |
| `main: starting router server, no model will be loaded` | **`params.model.path` is empty** — llama.cpp treats that as router mode | Ensure `-m` / `--model` points at a real file. A **broken shell paste** (two `find` commands merged into one line) can set `GGUF_PATH` to garbage so the path is invalid and the arg is dropped. Use the full blob path or a single clean `find ... \| head -1`. |
| `POST /v1/chat/completions ... 400` while in router mode | No loaded model / routing rules | Load a model (single-model mode with valid `-m`) or pass a valid `"model"` in JSON after loading via router API. |
| `curl: Failed to connect to 127.0.0.1:8090` | Server still loading 14B weights, exited on error, or never bound | Wait longer (30–60s+), or run `scripts/run_llama_kv_cache_benchmark.sh` (polls logs for `server is listening on` vs router). |
| `gguf_init_from_file: failed to open GGUF file ... (No such file or directory)` | Hardcoded path from **another** Ollama install layout | Ollama may store under **`~/.ollama/models/`** (user install) or **`/usr/share/ollama/.ollama/`** (Linux `ollama` service user). **Do not** assume one path. Run `python3 scripts/resolve_ollama_gguf.py` or set **`GGUF_PATH`** / **`OLLAMA_MODELS`**. |
| **`find /mnt/c ...` hangs** | **`/mnt/c` is the whole Windows volume** — full-tree `find` is huge on WSL2 | Use **`bash scripts/quick_find_ollama_blobs.sh`** or a **single** tree: `find /mnt/c/Users/jonat/.ollama/models/blobs -maxdepth 1 -name 'sha256-*' -size +100M`. |

**Resolve GGUF path on *your* machine:**

```bash
python3 scripts/resolve_ollama_gguf.py qwen25-grounded-gen5-delta:latest
# or another tag:  python3 scripts/resolve_ollama_gguf.py mymodel:latest
```

On **WSL2 with Ollama running on Windows**, blobs usually live under **`/mnt/c/Users/<you>/.ollama`** (or sometimes **`.../AppData/Local/Ollama`**). The resolver checks those paths automatically; if discovery is slow, set **`OLLAMA_MODELS`** to the folder that contains **`models/blobs`** and **`models/manifests`**.

If resolution still fails, the script calls **`GET $OLLAMA_HOST/api/tags`** (default `http://127.0.0.1:11434`) and prints **which model names the daemon actually has**. Use the **exact** name from that list (e.g. **`qwen25-grounded-gen5-delta:latest`** vs **`qwen25-grounded:latest`**) or set **`OLLAMA_MODEL_REF`** / **`GGUF_PATH`** accordingly.

Then:

```bash
export CUDA_VISIBLE_DEVICES=0
GGUF="$(python3 scripts/resolve_ollama_gguf.py)"
~/llama.cpp/build/bin/llama-server -m "$GGUF" --port 8090 --host 127.0.0.1 --ctx-size 8192 -ngl all
```

The benchmark script calls this resolver automatically if **`GGUF_PATH`** is unset (override with **`OLLAMA_MODEL_REF`** if you use a different model name).

---

## Measured results (operator — fill after scripts)

**Captured:** 2026-04-06 — RTX 3090 24GB, `llama-server` b8683, `-ngl all`, `qwen25-grounded-gen5-delta:latest` GGUF via Ollama blob resolver. **Four-case** `scripts/run_llama_kv_cache_benchmark.sh` (includes **f16 @ 32K**).

| Step | VRAM used (MiB) after load | Notes |
|------|----------------------------|--------|
| f16 KV, 8K ctx | 10452 | Default KV; baseline |
| q4_0 KV, 8K ctx | 9360 | ~1.1 GiB lower than f16 at same ctx |
| f16 KV, 32K ctx | 15060 | **No OOM** on 24GB; ~4.4 GiB more VRAM than q4_0 @ 32K (KV precision cost at long ctx) |
| q4_0 KV, 32K ctx | 10666 | No OOM; **~4394 MiB** less VRAM than f16 @ 32K at same ctx |

**CUDA toolkit package:** `cuda-toolkit-12-8` (see install script).  
**Build:** `~/llama.cpp/build/bin/llama-server` with `GGML_CUDA=ON`, `CMAKE_CUDA_ARCHITECTURES=86`.

### Weights vs KV cache (terminology)

The GGUF is **weight-quantized** (Q4_K_M for the ~14B parameters). The benchmark varied **KV cache** storage only (`--cache-type-k` / `--cache-type-v`): **f16** vs **q4_0** for keys and values. It did **not** load an FP16-weights model. **f16 KV** is therefore not “the full unquantized model”—it is FP16 storage for the attention cache at a fixed weight quant.

---

## Production profiles and runtime choice (2026-04-06)

### Primary runtime: Ollama vs `llama-server`

| Path | Use when | KV quantization flags | Context |
|------|----------|----------------------|---------|
| **Ollama** | FAITHH’s usual local path ([`backend/llm_providers.py`](../../backend/llm_providers.py)), `ollama run`, lowest moving parts | Internal defaults only (no Modelfile `cache-type` knob) | Set with **`PARAMETER num_ctx`** in the model’s Modelfile (this benchmark used gen5-delta: [`ml/grounding_finetune/output/qwen25-grounded-gen5-delta/gguf_gguf/Modelfile`](../../ml/grounding_finetune/output/qwen25-grounded-gen5-delta/gguf_gguf/Modelfile) — **4096** at capture) |
| **`llama-server`** | Benchmarks, OpenAI-compatible `/v1`, explicit VRAM tuning | **Yes** — e.g. `--cache-type-k q4_0 --cache-type-v q4_0` | **`--ctx-size`** (e.g. 8192, 32768) |

**Decision:** Keep **Ollama** as the **primary** FAITHH runtime for normal UI/chat. Use **`llama-server`** when you need **KV cache quantization** or **context larger** than the Modelfile allows without recreating the Ollama image (you can also raise `num_ctx` in the Modelfile and `ollama create` again—still no per-layer KV type control).

### Recommended profiles (RTX 3090 24GB, same Q4_K_M GGUF)

| Profile | Runtime | KV | Context | VRAM after load (measured) | When to use |
|---------|---------|-----|---------|----------------------------|-------------|
| **A — Default batch / headroom** | `llama-server` | q4_0 / q4_0 | 8192 | ~9360 MiB | Best margin on 24GB; preferred for scripts and non-UI inference |
| **B — Long context (VRAM-efficient)** | `llama-server` | q4_0 / q4_0 | 32768 | ~10666 MiB | Long documents / large RAG; leaves most headroom on 24GB |
| **B2 — Long context (f16 KV)** | `llama-server` | f16 (omit `--cache-type-*`) | 32768 | ~15060 MiB | Same 32K slot as B but **~4.4 GiB** more VRAM; use if q4_0 KV quality is unacceptable |
| **C — KV quality-first** | `llama-server` | f16 (omit cache-type or explicit f16) | 8192 | ~10452 MiB | If q4_0 KV hurts behavior on your tasks |
| **D — FAITHH UI** | Ollama | default | 4096 (Modelfile) | *TBD — sample under load* | Matches current gen5-delta Modelfile; simplest day-to-day |

Example **profile A** (resolve GGUF same as benchmark):

```bash
export CUDA_VISIBLE_DEVICES=0
MODEL="$(python3 scripts/resolve_ollama_gguf.py qwen25-grounded-gen5-delta:latest)"
~/llama.cpp/build/bin/llama-server -m "$MODEL" --host 127.0.0.1 --port 8081 \
  -ngl all --ctx-size 8192 --cache-type-k q4_0 --cache-type-v q4_0
```

Example **profile B**: same as above with `--ctx-size 32768`. **Profile B2:** same port/host/GGUF but `--ctx-size 32768` and **omit** `--cache-type-k` / `--cache-type-v` (f16 KV).

### VRAM headroom and stress verification

1. **Do not tune to the last MiB.** Keep **~2–4 GiB** below the first OOM you see in stress tests, or **~10–15%** of total VRAM free after load—whichever is larger—for spikes during generation and desktop/display.
2. **Verify under real prompts:** while running your longest typical user + assistant turn, watch `nvidia-smi` (e.g. `watch -n1 nvidia-smi`) and note **peak** `memory.used`, not only the idle-after-load number from the benchmark.
3. If **q4_0** KV causes odd long-context behavior, try **`q8_0`** for K/V if `llama-server --help` lists it on your build (middle ground vs f16 KV).
4. **f16 KV at 32K (completed on this hardware):** **did not OOM** — ~**15060 MiB** after load vs ~**10666 MiB** for q4_0 @ 32K. On other GPUs or builds, the script still catches failure as `ERR` in the summary line.

---

## Findings from this environment (automated run)

| Item | Result |
|------|--------|
| **Ollama model path** | **Install-dependent:** blobs live under `$OLLAMA_MODELS`, or `~/.ollama/models/`, or `/usr/share/ollama/.ollama/models/` when the daemon runs as user `ollama`. |
| **GGUF blob for this model** | Use `scripts/resolve_ollama_gguf.py` to read the manifest and print the weights path (supports optional `from` field in the manifest layer). |
| **`~/.local/bin/llama-server`** | Present but **CPU-only** build: log shows `no usable GPU found, --gpu-layers option will be ignored`. |
| **`llama-cpp-python` in venv** | `pip install ... --extra-index-url .../whl/cu128` resolved to **PyPI CPU wheels** (no `libggml-cuda.so` under `site-packages/llama_cpp/lib/`). `llama_supports_gpu_offload()` → **False**. `pip download --only-binary=:all:` against the cu128 index found **no wheel** for this platform (Python 3.12 / manylinux combo). |
| **Torch CUDA** | `torch.cuda.is_available()` → True, device name RTX 3090 — driver works; llama.cpp stack still needs a **CUDA-enabled** llama build. |
| **`sudo systemctl stop ollama`** | **Not available** in agent shell (password required). Stop Ollama manually before GPU-exclusive llama-server tests. |
| **Ollama `/api/generate` VRAM** | During short runs, `nvidia-smi` reported ~**123 MiB** used / **~24204 MiB** free (GPU essentially idle in those samples). Treat as **inconclusive** for “model resident on GPU” without a loaded-model probe (e.g. load then sample `nvidia-smi` before unload). |

**Conclusion (agent sandbox):** KV VRAM A/B was **not completed** in that environment (no CUDA `llama-server` in-path). **Operator run 2026-04-06** on RTX 3090 **did** complete the **four-case** benchmark (including **f16 @ 32K**); see **Measured results** and **Production profiles** above. **C8 / `llama_server` in `component_map`** can move from “deferred” once you adopt a local OpenAI-compatible endpoint intentionally (optional `llm_providers` wiring remains a product choice).

---

## Results table (fill on your machine)

| Test | KV type | Ctx size | VRAM used (MiB) | VRAM free (MiB) | Notes |
|------|---------|----------|-----------------|-----------------|-------|
| Ollama baseline | f16 (default) | 4096 (Modelfile `num_ctx`) | *TBD* | *TBD* | After model load, before huge prompt |
| Ollama long prompt | f16 (default) | 4096 | *TBD* | *TBD* | After ~few-k token prompt |
| llama-server | f16 | 8192 | 10452 | ~14124 | Native binary: default KV (f16); after load, before long prompt |
| llama-server | q4_0 / q4_0 | 8192 | 9360 | ~15216 | `--cache-type-k q4_0 --cache-type-v q4_0` |
| llama-server | f16 | 32768 | 15060 | ~9516 | No OOM; **full KV precision** at 32K ctx; ~4.4 GiB heavier than q4_0 @ 32K |
| llama-server | q4_0 / q4_0 | 32768 | 10666 | ~13910 | **32K viable** on 24GB with this Q4_K_M 14B + full offload |

---

## Commands that match upstream APIs

### Native `llama-server` (hyphen flags)

```bash
MODEL="$(python3 scripts/resolve_ollama_gguf.py qwen25-grounded-gen5-delta:latest)"
CUDA_VISIBLE_DEVICES=0 llama-server \
  -m "$MODEL" \
  --n-gpu-layers all \
  --ctx-size 8192 \
  --cache-type-k q4_0 \
  --cache-type-v q4_0 \
  --port 8081 \
  --host 0.0.0.0
```

### Python `llama_cpp.server` (underscore / argparse names)

```bash
CUDA_VISIBLE_DEVICES=0 python3 -m llama_cpp.server \
  --model "$MODEL" \
  --n_gpu_layers -1 \
  --n_ctx 8192 \
  --type_k q4_0 \
  --type_v q4_0 \
  --port 8081 \
  --host 0.0.0.0
```

Verify GPU before benchmarking:

```bash
python3 -c "from llama_cpp import llama_cpp as L; print('gpu_offload', L.llama_supports_gpu_offload())"
# Expect True after a proper CUDA build
ls "$(python3 -c 'import llama_cpp, pathlib; print(pathlib.Path(llama_cpp.__file__).parent)')"/lib/*cuda* 2>/dev/null
```

### Getting a CUDA-enabled build

1. **Match CUDA wheel** to your Python version (cp312 may have no prebuilt CUDA wheel on abetlen’s index — try **Python 3.11** venv or build from source).
2. **Source build:**  
   `CMAKE_ARGS="-DGGML_CUDA=on" pip install llama-cpp-python[server] --force-reinstall --no-cache-dir`  
   (requires CUDA toolkit / nvcc aligned with driver.)
3. **Or** build `llama-server` from the repo’s `llama.cpp` with `GGML_CUDA=ON` and use that binary.

---

## Key questions (after you have GPU numbers)

- Does **q4_0** KV allow **32K** where **f16** KV OOMs? — **On RTX 3090 24GB, neither OOMs at load:** f16 @ 32K ~**15060 MiB**, q4_0 @ 32K ~**10666 MiB** (~**4.4 GiB** KV savings with q4_0). OOM could still happen on smaller GPUs or under peak generation — use `nvidia-smi` peaks.
- Is quality acceptable for FAITHH-style tasks? — **Validate per profile** under real prompts; fall back to profile C or q8 KV if needed.
- Practical max context before OOM with weights + activations + KV? — **Use peak `nvidia-smi`** during max prompt + generation, not load-only numbers.

## Decision checklist

- [x] **Primary runtime:** Ollama for default FAITHH UI (**profile D**); **`llama-server`** for KV-tuned or long-context work (**profiles A–C**, **B** vs **B2** at 32K).
- [x] **Default batch / server profile:** **A** (q4_0 KV, 8K ctx); **B** (q4_0 32K) or **B2** (f16 32K) for long docs by VRAM vs KV-quality tradeoff; **C** if q4_0 hurts at 8K only.
- [x] **Headroom:** verify peaks under real workloads; target **2–4 GiB** (or **10–15%** VRAM) slack; try **q8_0** K/V before f16 KV if q4_0 is problematic.
- [ ] Optional: add OpenAI-compatible local provider in `backend/llm_providers.py` pointing at `llama-server` — only if product needs unified routing.

## Next steps (if benchmark succeeds)

- Optional provider in `backend/llm_providers.py` for OpenAI-compatible `http://127.0.0.1:8081/v1`.  
- Gate: e.g. T1-C8 — track in `projects/status/project_status.json` when results exist.

---

## Experiment A — PolarQuant vs q4_0 quality comparison (2026-04-07)

**Goal:** Check whether a **paper-aligned PolarQuant** layout (random rotation → 4-level polar tree → Lloyd codebooks on known angle PDFs → **8×fp16 radii** + packed angle indices, **~62 bytes/vector**, **~4.13×** vs fp16) delivers **better reconstruction / attention proxy error** than a simple **per-block q4-style** baseline at a **similar** bit budget (~4 bpw).

**Method (pure Python, no llama.cpp hooks):**

- **KV source:** `scripts/extract_kv_vectors.py` — Hugging Face **`Qwen/Qwen2-1.5B`**, `past_key_values` from layers **5, 12, 20**, five short prompts → **240** flattened K rows, **head_dim 128** (same family as Qwen2 ~15B; not identical weights).
- **PolarQuant:** Reimplements the **4-level / 120-angle** scheme described in `vendor/polar_quant/README.md` (reference repo is **CUDA-only**; no Python module). Codebooks: level 0 **16** bins (4 bits), levels 1–3 **4** bins each (2 bits); radii stored as **fp16 round-trip**.
- **Baseline:** Block-wise absmax normalization, **4-bit** symmetric levels (32-wide blocks), comparable to “q4_0 class” scalar quantization (not bit-identical to GGML).

**Metrics (mean over 240 vectors, CPU):**

| Metric | PolarQuant (nominal layout) | Block q4-style |
|--------|----------------------------:|---------------:|
| Relative L2 reconstruction error | **0.180** | **0.126** |
| Dot-product proxy — mean \|Δ\| vs random unit queries (10/query) | **0.198** | **0.132** |

*Numbers from `experiment_a_results.json` after a **CUDA** `polar_quant_experiment.py` run; a CPU run can shift the dot-proxy by ~0.01 (non-deterministic matmul / order).*

**Compression / capacity (nominal, d=128):**

| Item | Value |
|------|------:|
| fp16 vector | 2048 bits (256 B) |
| Polar record (368 angle bits + 8×fp16 radii) | **496 bits (~62 B)** → **4.13×** vs fp16 |
| Block q4 @ 4 bpw | 512 bits (64 B) → **4.00×** vs fp16 |

**32K context KV scaling (48 layers, 8 KV heads, 128 head_dim, K+V, same geometry as handoff):**

| KV storage | MiB per state (estimate) | Simultaneous states (VRAM KV budget ~16120 MiB after ~8148 MiB weights + ~307 MiB buffer) |
|------------|--------------------------:|------------------------------------------------------------------------------------------------:|
| f16 | 6144 | ~2.6 |
| Polar (4.13×) | ~1488 | ~10.8 |
| q4_0 class (4×) | ~1536 | ~10.5 |

**Artifacts (tracked):** `data/kv_vectors/experiment_a_results.json`, `data/kv_vectors/extraction_meta.json`, `scripts/extract_kv_vectors.py`, `scripts/polar_quant_experiment.py`. **Local only (regenerate):** `K_qwen2_sample.pt` / `V_qwen2_sample.pt` from `python3 scripts/extract_kv_vectors.py` — not required in git.

**Recommendation:** The **~4× compression ratio** from the PolarQuant **record layout** matches the published **62-byte** story. In this **naive encode→decode** Python test on **rotated Qwen2 K vectors**, **block q4-style quantization achieved lower L2 and lower dot error** than this PolarQuant pipeline at a **similar** bit budget. **Kernel integration** (fused **Q·K** from packed polar without full dequant, tuned codebooks, or training-time alignment) may still be worthwhile for **throughput and memory**, but **do not assume** PolarQuant beats simple int4 block KV on **reconstruction quality** without measuring end-to-end attention / perplexity on your stack.

### llama-server: same prompts, f16 vs q4_0 KV (deployability check)

**Repro fields:** See [`KV_EXPERIMENT_REPRO_CHECKLIST.md`](KV_EXPERIMENT_REPRO_CHECKLIST.md) for what to record. New ablation JSON files include an **`environment`** object (GPU line, `llama-server --version`, GGUF basename, `KV_ABLATION_*`).

**Scripts:**

- `scripts/run_llama_kv_quality_ablation.sh` — starts **`llama-server`** for **f16** then **q4_0** KV (default **8K** ctx). Optional third leg: **`KV_QUALITY_INCLUDE_Q8=1`** → **`q8_0`** K/V, then **`compare-multi`** vs f16. Writes JSON under `data/kv_vectors/`.
- `scripts/llama_kv_prompt_ablation.py` — `run` (chat completions), **`compare`** (two files), **`compare-multi`** (baseline first, then N profiles). Default prompts match **`scripts/extract_kv_vectors.py`**. **`temperature=0`**. Use **`--no-environment`** to omit the repro block.

**Run (after CUDA `llama-server` is built; same env as KV VRAM benchmark):**

```bash
cd /home/jonat/ai-stack
export CUDA_VISIBLE_DEVICES=0
# Optional: export OLLAMA_MODEL_REF=...  or  GGUF_PATH=/path/to/model.gguf
bash scripts/run_llama_kv_quality_ablation.sh
```

**Outputs:** `data/kv_vectors/llama_kv_ablation_f16_8192.json`, `llama_kv_ablation_q4_0_8192.json`, and (with **`KV_QUALITY_INCLUDE_Q8=1`**) `llama_kv_ablation_q8_0_8192.json`.

**Port 8090 busy:** If you see `couldn't bind HTTP server socket`, another `llama-server` (or tool) is still listening. Stop it (`pkill -f '[l]lama-server'`) or run with **`PORT=8091`** (scripts preflight-check and exit with the same hint).

**Optional:** `KV_QUALITY_CTX=32768` for long context. **`KV_QUALITY_INCLUDE_Q8=1`** adds `llama_kv_ablation_q8_0_${CTX}.json` and a three-way summary. `KV_QUALITY_MAX_TOKENS`, `KV_QUALITY_TIMEOUT` tune generation (use **~600s** timeout for slow 32K loads).

**Multi-context matrix (8K + 32K):** `bash scripts/run_llama_kv_ablation_matrix.sh` runs the three-way ablation for **`8192`** and **`32768`** by default (`KV_MATRIX_CONTEXTS` overrides). Logs to `data/kv_vectors/ablation_matrix.log` (gitignored). Then runs **`scripts/summarize_kv_ablation_runs.py`**, which writes **`data/kv_vectors/KV_ABLATION_SUMMARY.md`** — match rates and mean latency vs f16 per ctx. If **f16 @ 32K OOMs**, that leg is recorded as FAIL and the script continues (set **`KV_MATRIX_STOP_ON_ERROR=1`** to abort).

**Interpretation:** Identical **`content_sha256`** rows mean outputs matched exactly at `temperature=0`; divergences flag KV-quality sensitivity for your GGUF. Latency rows are **end-to-end request** time (not isolated decode).

### Choosing KV settings (combine VRAM + chat ablation)

1. **VRAM ceiling:** Use the measured table above (f16 / q4_0 at 8K and 32K) so you know whether **32K** fits with **f16** KV on your GPU.
2. **Greedy text parity:** Run the matrix (or single `KV_QUALITY_CTX`) and read **`KV_ABLATION_SUMMARY.md`** plus qualitative notes below (e.g. prompt 0: **q4_0** can refuse; **q8_0** often stays “on task” with different wording).
3. **Emerging defaults for this stack (Qwen2 ~15B Q4_K_M weights, RTX 3090):**
   - **Quality-first / RAG-critical:** **`--cache-type-k` / `-v` omitted** (f16 KV), **8K** unless you need 32K and VRAM allows.
   - **VRAM constrained, still need sensible answers:** try **`q8_0`** K/V first; re-run your **real** FAITHH prompts before locking in.
   - **Max KV savings:** **`q4_0`** only if task checks pass — do **not** assume parity with f16 at `temperature=0`.
4. **PolarQuant / “Google-style” packed KV:** **Not** available as a `llama-server` flag. Using it in real inference means **forking llama.cpp (or similar) and adding new KV types + CUDA paths** — see **[`KV_RESEARCH_FORMATS_POLARQUANT.md`](KV_RESEARCH_FORMATS_POLARQUANT.md)** for what that entails and where this repo’s Python experiment fits.

Re-run the matrix when you change **GGUF**, **llama-server build**, or **CUDA driver**.

### Captured run — f16 vs q4_0 KV (chat ablation, in-repo)

**Checked in:** `data/kv_vectors/llama_kv_ablation_f16_8192.json`, `llama_kv_ablation_q4_0_8192.json`, `llama_kv_ablation_q8_0_8192.json`. Each file includes an **`environment`** block (platform, `llama-server --version`, GGUF basename, `KV_ABLATION_*`).

| Field | Value |
|-------|--------|
| **When** | `generated_at` in each JSON (2026-04-07 UTC, three-way run) |
| **Hardware** | RTX 3090 24GB, `CUDA_VISIBLE_DEVICES=0`, WSL2 |
| **Server** | `llama-server` build 8683 (`d0a6dfeb2`), `-ngl all`, `--ctx-size 8192`, `127.0.0.1:8090` |
| **Weights** | `qwen25-grounded-gen5-delta:latest` GGUF (Ollama blob `sha256-98ebf1f55fe7…`, ~8.4 GiB) |
| **Chat** | `temperature=0`, `max_tokens=256`, five prompts aligned with `scripts/extract_kv_vectors.py` |
| **Third leg** | `KV_QUALITY_INCLUDE_Q8=1 bash scripts/run_llama_kv_quality_ablation.sh` |

**`compare-multi` summary (baseline = f16 KV; m = exact same assistant text as f16):**

| # | ms f16 | ms q4_0 | m | ms q8_0 | m |
|---|-------:|--------:|:--|--------:|:--|
| 0 | 3245.0 | 1424.1 | N | 3292.7 | N |
| 1 | 3521.9 | 3752.3 | N | 3761.8 | N |
| 2 | 3592.4 | 3760.5 | N | 3780.7 | N |
| 3 | 3678.5 | 2731.3 | N | 3785.0 | N |
| 4 | 3532.2 | 3922.3 | N | 3810.2 | N |

**Prompt 0 (qualitative):** **q4_0 KV** produced a “instruction incomplete / please clarify” style reply vs **f16**’s full structured answer (strong behavioral gap). **q8_0 KV** still differs from f16 on exact text (**m = N**) but stays in the same **helpful completion** regime (numbered transition steps), i.e. a **phrasing / sampling-path** drift rather than refusal. **Neither q4_0 nor q8_0** matched f16 greedily on these five at `temperature=0`; validate per product whether q8 is an acceptable compromise vs VRAM.

---

## Ollama restart / FAITHH

After experiments: `sudo systemctl start ollama` (or your usual method). Confirm `curl http://127.0.0.1:5557/api/health`.
