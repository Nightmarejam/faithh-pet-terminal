# RUNBOOK — lean homelab + FAITHH (pointer)

**Start here:** [docs/ops/LEAN_LLM_VLLM_FIRST.md](docs/ops/LEAN_LLM_VLLM_FIRST.md) — vLLM on faithh, Chroma on Gen8, Anthropic **`pip` + `.env`**, **`FAITHH_FORCE_LOCAL`**, Ollama optional.

**Gen8 vs faithh:** [docs/ops/GEN8_START.md](docs/ops/GEN8_START.md) · **Audits:** [docs/ops/MULTI_HOST_AUDIT.md](docs/ops/MULTI_HOST_AUDIT.md) · **Git:** [docs/ops/GIT_DIVERGENCE.md](docs/ops/GIT_DIVERGENCE.md)

**Handoffs:** Optional **`~/audit/*.md`** — do not require committing handoff markdown to run the stack; keep secrets in **`.env`** only (`chmod 600`).

For full port tables and connectivity, see in-repo ops docs under **`docs/ops/`** (inventory, Gen8 network map, faithh ↔ Gen8) when present on your **`origin/main`** tip.
