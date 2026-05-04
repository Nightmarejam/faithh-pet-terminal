# Lean LLM — vLLM on faithh, Chroma on Gen8, Anthropic via `.env`

**Lean rule:** Gen8 runs **Docker + Chroma** only for this stack; **all heavy LLM** runs on **faithh** (vLLM first). **Ollama** only if you need **`/api/generate`**, quick local modelfiles, or a vLLM gap.

**Secrets:** `ANTHROPIC_API_KEY` only in **`~/ai-stack/.env`** on the host that runs the chat backend — never git (`chmod 600`).

**Handoffs:** Optional **`~/audit/*.md`** on disk; **not required** in git — seed ops from **`docs/ops/`** + **[RUNBOOK.md](../../RUNBOOK.md)**.

**`FAITHH_FORCE_LOCAL=0` (important):** This does **not** mean “remote vLLM only.” It means: **do not force** `/api/chat` to Ollama-only — use the **route list** in **`configs/model_config.yaml`** (e.g. **`local_webui`** first, then **`ollama`** / **`groq`** as listed). vLLM can still be **`http://127.0.0.1:8000/v1`** on **faithh** (same VM as the backend). The lean part is: **Gen8 does not run that LLM** — faithh does.

---

## 1. Repo + clone check (faithh — where chat runs)

```bash
cd ~/ai-stack && git fetch origin && git status -sb
ls -1 faithh_professional_backend_fixed.py configs/model_config.yaml 2>/dev/null || true
```

If those files are missing, you are on a **slim** clone or old tip — **`git pull origin main`** (see **[GIT_DIVERGENCE.md](GIT_DIVERGENCE.md)**) before tuning LLM.

---

## 2. Anthropic SDK (`ModuleNotFoundError: anthropic`)

After **every** `git pull` that changes **`requirements.txt`**:

```bash
cd ~/ai-stack
grep -n anthropic requirements.txt
./venv/bin/pip install -r requirements.txt
./venv/bin/python -c "import anthropic; print('Anthropic SDK OK')"
```

If **`grep`** shows nothing, you are **before** the commit that added **`anthropic`** — fix git first, then **`pip`**.

**Key in `.env`:**

```bash
ANTHROPIC_API_KEY=sk-ant-api03-...
FAITHH_FORCE_LOCAL=0
chmod 600 ~/ai-stack/.env
```

**Pick `model` for `model_config.yaml`:** with vLLM running:

```bash
./venv/bin/python scripts/ops/print_first_vllm_model_id.py
# other port: ./venv/bin/python scripts/ops/print_first_vllm_model_id.py --url http://127.0.0.1:8010/v1/models
```

Paste the printed **`id`** into **`providers.local_webui.model`** (replace **`REPLACE_WITH_ID_FROM_V1_MODELS`**).

Restart the backend (**`./restart_backend.sh`**). Smoke: **`curl -sS http://127.0.0.1:5557/health | head -c 800`** — when the full backend exposes it, **`providers.anthropic`** (or similar) should reflect the key.

---

## 3. vLLM first (faithh)

1. **Serve vLLM** (e.g. port **8000**). Check: **`curl -sS "http://127.0.0.1:8000/v1/models"`**.
2. **`configs/model_config.yaml`:** set **`providers.local_webui.base_url`** to your **`/v1`** URL (often **`http://127.0.0.1:8000/v1`**). Set **`model`** to an **`id`** from that JSON (replace **`REPLACE_WITH_ID_FROM_V1_MODELS`**).
3. **`~/ai-stack/.env`:** **`FAITHH_FORCE_LOCAL=0`** so YAML routes apply (see note at top).
4. **`restart_backend.sh`** sources **`.env`** then uses **`: "${FAITHH_FORCE_LOCAL:=1}"`** — a literal **`0`** in **`.env`** is preserved.
5. **UI:** **`http://<faithh-LAN-or-TS>:5557/`** (not **`file://`**).

---

## 4. Ollama fallback (faithh only when needed)

Install Ollama on **faithh**; add **`ollama`** into **`routes.auto`** (and other routes) in **`model_config.yaml`** if you want fallback. Keep **`FAITHH_FORCE_LOCAL=0`** unless you intentionally want **Ollama-only** routing.

---

## 5. Gen8 (`servicebox`)

**Chroma** + **`~/services`**. Smoke toward faithh:

```bash
curl -sS "http://<faithh-ip>:8000/v1/models" | head -c 400
```

**Docker / listen:** what matters is **bind** (**`0.0.0.0:8000`** for Chroma so faithh can reach Gen8’s LAN IP). Check: **`docker ps`**, **`ss -tlnp`**.

---

## 6. Git hygiene

- **Routine:** **`git fetch origin && git pull origin main`**
- **`git reset --hard origin/main`:** only when you **intend** to discard all local commits and uncommitted work on that clone.

---

## 7. Related

- **[GEN8_START.md](GEN8_START.md)** — role split.  
- **[MULTI_HOST_AUDIT.md](MULTI_HOST_AUDIT.md)** — which host you are on.
