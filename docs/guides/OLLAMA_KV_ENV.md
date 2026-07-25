# Ollama: KV cache quantization (`OLLAMA_KV_CACHE_TYPE`)

**Goal:** Cut KV VRAM (often ~half with `q8_0` vs default `f16`) on long context — same **weight** GGUF (e.g. Q4_K_M), only the **attention cache** changes precision.

**Critical:** These variables apply to the **Ollama server process**, not the FAITHH Python backend. Setting them in **`.env`** used by `restart_backend.sh` **does not** change Ollama unless that same environment is inherited by **`ollama serve`** (it usually is not).

---

## Supported values

| Value | KV VRAM (typical) | Notes |
|-------|-------------------|--------|
| `f16` | Baseline (largest) | Default if unset. |
| `q8_0` | ~½ of f16 KV | Good default when you need **32K+** headroom on a **24 GB** GPU. |
| `q4_0` | ~¼ of f16 KV | More aggressive; validate on your tasks (edge prompts can drift). |

Global: one setting for **all** models on that Ollama instance.

---

## Flash Attention

On many setups, **`OLLAMA_FLASH_ATTENTION=1`** is required for KV quantization to actually apply. If you set `OLLAMA_KV_CACHE_TYPE=q8_0` but logs still show `type_k = 'f16'`, enable flash attention and restart Ollama.

```bash
export OLLAMA_FLASH_ATTENTION=1
export OLLAMA_KV_CACHE_TYPE=q8_0
```

---

## WSL2 (manual `ollama serve` in a shell)

1. Add to **`~/.bashrc`** (or run before starting Ollama in that terminal):

   ```bash
   export OLLAMA_FLASH_ATTENTION=1
   export OLLAMA_KV_CACHE_TYPE=q8_0
   ```

2. **Restart Ollama** so it inherits the env (stop the old process, then start again from a shell where the exports are active):

   ```bash
   pkill -f '[o]llama serve' 2>/dev/null || true
   # wait until nothing listens on 11434, then:
   ollama serve
   ```

3. **Verify** after loading a model (e.g. `ollama run qwen25-grounded:latest` once):

   - Server logs should show **`type_k` / `type_v`** as **`q8_0`** (not **`f16`**).
   - Or compare **`nvidia-smi`** memory for the same model at **`num_ctx` 32768** before vs after.

---

## Linux systemd (`ollama` package)

Override the service environment (path may vary):

```ini
# /etc/systemd/system/ollama.service.d/override.conf
[Service]
Environment="OLLAMA_FLASH_ATTENTION=1"
Environment="OLLAMA_KV_CACHE_TYPE=q8_0"
```

Then:

```bash
sudo systemctl daemon-reload
sudo systemctl restart ollama
```

Confirm with `systemctl show ollama -p Environment` or logs on next model load.

---

## Windows (Ollama app / service)

Ollama must see the variables **before** the service starts.

- **User install:** System **Environment Variables** (User or System) → add `OLLAMA_FLASH_ATTENTION` = `1`, `OLLAMA_KV_CACHE_TYPE` = `q8_0` → reboot or restart **Ollama** from the tray / Services.
- **WSL calling Windows Ollama:** Set vars on **Windows** where the Ollama service runs; WSL `.bashrc` alone does not affect the Windows daemon.

---

## FAITHH / Pulse

After Ollama is on `q8_0` KV:

1. Use **Pulse** or UI to set **Ollama context** (e.g. **32768**) if your Modelfile / app allows.
2. Run a **long** grounded prompt and watch **`nvidia-smi`** peaks.

FAITHH **`OLLAMA_HOST`** in `.env` only points the **client** at Ollama; it does not set Ollama’s KV type.

---

## Troubleshooting

| Symptom | Likely cause |
|---------|----------------|
| Logs still show `type_k = 'f16'` | Flash attention off; old Ollama build; or model/arch doesn’t support KV quant for that path. |
| Variable “does nothing” | Set on **FAITHH** only — must be on **Ollama** process. |
| Windows: WSL `.env` didn’t help | Ollama runs on **Windows** — set env there. |

**Ground truth:** Ollama / llama.cpp **startup logs** for the loaded model, not assumptions.

---

## Related repo docs

- `docs/experiments/KV_CACHE_QUANT_BENCHMARK_20260405.md` — VRAM table + `llama-server` `--cache-type-*` experiments (same physics as Ollama; different knobs).
- `docs/experiments/KV_RESEARCH_FORMATS_POLARQUANT.md` — PolarQuant ≠ Ollama env; fork territory.
