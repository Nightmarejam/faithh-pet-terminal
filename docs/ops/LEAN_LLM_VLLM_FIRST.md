# Lean LLM — vLLM on faithh, Chroma on Gen8, Anthropic via `.env`

**Lean rule:** Gen8 runs **Docker + Chroma** only for this stack; **all heavy LLM** runs on **faithh** (vLLM first). **Ollama** only if you need **`/api/generate`** or quick local pulls.

**Secrets:** `ANTHROPIC_API_KEY` only in **`~/ai-stack/.env`** on the host that runs the chat backend — never git.

**Handoffs:** Optional `~/audit/*.md` on disk; **not required** in git — seed ops from **`docs/ops/`** + **`RUNBOOK.md`**.

---

## 1. Repo + clone check (faithh)

```bash
cd ~/ai-stack && git fetch origin && git status -sb
ls -1 faithh_professional_backend_fixed.py configs/model_config.yaml 2>/dev/null || true
```

If the entrypoint or **`configs/model_config.yaml`** is missing, this clone is incomplete for full chat — fix remotes / branch, then **`git pull`**.

---

## 2. Anthropic SDK + key (faithh)

```bash
cd ~/ai-stack && ./venv/bin/pip install -r requirements.txt
./venv/bin/python -c "import anthropic; print('Anthropic SDK OK')"
```

Edit **`~/ai-stack/.env`**:

```bash
ANTHROPIC_API_KEY=sk-ant-api03-...
chmod 600 ~/ai-stack/.env
```

Restart backend (**`./restart_backend.sh`** or your process manager). Smoke: **`curl -sS http://127.0.0.1:5557/health | head -c 800`** — expect **`providers`** / **`anthropic`** truthy when the full backend exposes that field.

---

## 3. vLLM-first routing

1. **Run vLLM** on faithh (default listen often **`:8000`**).

2. **Prove it:**

   ```bash
   curl -sS -m 10 "http://127.0.0.1:8000/v1/models" | head -c 1200
   ```

3. **`configs/model_config.yaml`** → **`providers.local_webui`:**

   - **`base_url`:** `http://127.0.0.1:8000/v1` (or another port; must end with **`/v1`**).
   - **`model`:** exact **`id`** from that JSON.

4. **`.env`:** **`FAITHH_FORCE_LOCAL=0`**  
   This does **not** mean “vLLM on another machine” by itself — it means **use the route order in `model_config.yaml`** (e.g. **`local_webui`** before **`ollama`**). vLLM can still be **`127.0.0.1`** on faithh. **`FAITHH_FORCE_LOCAL=1`** forces **Ollama-only** route lists in the backend.

5. **`./restart_backend.sh`**

6. **UI:** `http://<faithh-LAN-ip>:5557/` from your workstation (not `file://`, not laptop `localhost`).

---

## 4. Gen8 (servicebox)

- **Chroma** + **`~/services`** Docker — no vLLM/Ollama for FAITHH here.
- faithh **`.env`**: **`CHROMA_HOST`** / **`CHROMA_PORT`** → Gen8 LAN or Tailscale.

---

## 5. Ollama fallback

Install **`ollama serve`** on faithh if needed; keep **`ollama`** in **`model_config.yaml`** routes after **`local_webui`** for fallbacks.

---

## 6. Related

- **`GIT_DIVERGENCE.md`** — if `main` and `origin/main` diverge again after resets.  
- **`GEN8_START.md`** — role split.  
- **`MULTI_HOST_AUDIT.md`** — which host you are on.
