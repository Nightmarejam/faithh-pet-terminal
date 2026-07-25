# KV cache experiments — reproducibility checklist

Use this when running **VRAM benchmarks**, **chat ablations**, or **PolarQuant Python** checks so results stay comparable across machines and commits.

## Before you run

| Field | Why it matters | How to capture |
|--------|----------------|----------------|
| **llama-server build** | Kernels and cache types differ by commit | `llama-server --version` (stored in ablation JSON `environment.llama_server_version_output`) |
| **GGUF identity** | Weight quant ≠ KV quant | `gguf_basename` + `gguf_bytes` in ablation JSON; or `OLLAMA_MODEL_REF` |
| **CUDA / GPU** | VRAM and behavior | `nvidia-smi` first GPU line in `environment.nvidia_smi_gpu_line_0` |
| **`--ctx-size`** | KV size scales linearly | `KV_ABLATION_CTX` in JSON |
| **KV types** | f16 vs q4_0 vs q8_0 | `KV_ABLATION_CACHE_KV` + server flags (`--cache-type-k` / `-v`) |
| **`-ngl` / offload** | CPU vs GPU path | `KV_ABLATION_NGL` |
| **Chat sampling** | Greedy vs stochastic | `temperature`, `max_tokens` in JSON root |
| **Prompt set** | Must match across runs | Default = `scripts/extract_kv_vectors.py` starters; or `--prompt-file` |

## Scripts (this repo)

| Goal | Command | Artifacts |
|------|---------|-----------|
| VRAM table (f16/q4, 8K/32K) | `bash scripts/run_llama_kv_cache_benchmark.sh` | Paste MiB into `KV_CACHE_QUANT_BENCHMARK_20260405.md` |
| Chat quality (f16 vs q4_0) | `bash scripts/run_llama_kv_quality_ablation.sh` | `data/kv_vectors/llama_kv_ablation_f16_*.json`, `*_q4_0_*.json` |
| + q8_0 third leg | `KV_QUALITY_INCLUDE_Q8=1 bash scripts/run_llama_kv_quality_ablation.sh` | + `*_q8_0_*.json`, `compare-multi` summary |
| Diff two runs | `python3 scripts/llama_kv_prompt_ablation.py compare A.json B.json` | stdout table |
| Diff baseline vs many | `python3 scripts/llama_kv_prompt_ablation.py compare-multi base.json a.json b.json` | stdout |
| **8K + 32K matrix + summary** | `KV_QUALITY_TIMEOUT=600 bash scripts/run_llama_kv_ablation_matrix.sh` | `llama_kv_ablation_*_{8192,32768}.json`, `KV_ABLATION_SUMMARY.md`, `ablation_matrix.log` (log gitignored) |
| Auto table over all JSON | `python3 scripts/summarize_kv_ablation_runs.py data/kv_vectors` | stdout; add `--markdown path` to write file |
| PolarQuant toy metrics | `python3 scripts/polar_quant_experiment.py` (after `extract_kv_vectors.py`) | `data/kv_vectors/experiment_a_results.json` |

## What “good enough” measurement means

- **VRAM:** Use **after-load** MiB from the benchmark script **and** note **peak** `nvidia-smi` during a long generation if you care about OOM margins.
- **Quality:** **`temperature=0`** ablation catches **deterministic** drift; real FAITHH traffic may need **manual spot checks** on RAG/tool flows.
- **Latency:** Ablation latencies are **end-to-end HTTP**; use for coarse comparison only.

## Optional: commit captured JSON

When a run is the new **reference** for the team, commit the JSON under `data/kv_vectors/` and add a short **“Captured run”** paragraph in `KV_CACHE_QUANT_BENCHMARK_20260405.md` (see existing section for the llama chat ablation).
