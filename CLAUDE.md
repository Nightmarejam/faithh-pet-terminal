# FAITHH Local Stack (Claude Code)

You are running on **qwen3-coder-30b-a3b-awq** via vLLM with a **49K** context window (may increase if `start_vllm.sh` reports a higher `max_model_len`).

## Constraints

- Claude Code sends the full tool schema on every request (~27–30K tokens). Multi-turn sessions fill quickly.
- Route: Claude Code → `http://localhost:5558` (cc_proxy) → vLLM `:8000`. Do not point `ANTHROPIC_BASE_URL` at `:8000` or `:5557`.
- FAITHH PET backend is **:5557** only; it is not the Claude Code API path.

## Workflow

- Keep responses concise. Prefer targeted edits over full-file rewrites.
- After **2–3 tool-heavy turns**, run **`/compact`** to summarize and reset context.
- For large doc updates (e.g. SYSTEMS_MAP), use a **fresh session** or compact before the write turn.
- In Claude Code: `/model` → **Sonnet** → `claude-sonnet-4-6`.

## If you see context errors

- Proxy may return HTTP 413 with a clear message — run `/compact` or start a new `claude` session.
- Verify: `echo $ANTHROPIC_BASE_URL` → `http://localhost:5558`
