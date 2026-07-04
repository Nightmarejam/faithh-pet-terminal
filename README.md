# FAITHH — Friendly AI Teaching & Helping Hub

A personal AI companion I run on my own homelab — a NetNavi in the Mega Man Battle
Network sense: a small intelligence that lives with you, learns your world, and helps.
Not a product, not hosted; a research build I use and grow.

> One node in a personal AI ecosystem — see the [ecosystem map](https://github.com/Nightmarejam).
> Everything here is **human-directed, AI-assisted, with receipts** (see [PROVENANCE.md](PROVENANCE.md)).

---

## The idea (one concept)

Most assistants answer and forget. FAITHH is built to **perceive, reason, remember, and
(soon) act** — and to be **honest about how sure it is** at every step. That last part is
the whole point: it tags what it knows as `confirmed` (with a receipt), `asserted`, or
`speculative`, and never pretends to certainty it doesn't have.

## How it works — four building blocks

Take them one at a time; each is a layer on the one before.

1. **Perceive** — retrieval (RAG) over a knowledge base of my docs and past sessions.
   It reads before it speaks.
2. **Reason** — "battle chips" and the PULSE engine route a query to the right approach;
   a coherence step checks whether independent signals agree before it trusts a fact.
3. **Remember** — tiered memory (hot session → warm profile → cold vector store), so it
   carries context across days instead of starting cold.
4. **Act** *(in progress)* — an "agency" layer (tools it can run) gated by the honesty
   rule: act on `confirmed`, confirm on `asserted`, **stop and flag** on `speculative`.
   That gate is what keeps an autonomous agent from going rogue.

Underneath all four: **attestation** — the discipline of attaching checkable provenance
to every claim. It's the thing that makes FAITHH a companion you can trust rather than a
confident guesser.

## Read the concepts (deep-dives, newest thinking)

If you want to understand the design one document at a time, in order:

- [docs/ATTESTATION_CONCEPT](docs/ATTESTATION_CONCEPT_2026-07-02.md) — the honesty layer, the core idea
- [docs/CONNECTIVE_ARCHITECTURE](docs/CONNECTIVE_ARCHITECTURE_2026-07-02.md) — how the four blocks connect (the "nervous system")
- [docs/AUTONOMY_DESIGN](docs/AUTONOMY_DESIGN.md) — how it learns to act safely
- [docs/BACKEND_AUDIT](docs/BACKEND_AUDIT_2026-07-02.md) + [docs/CAPABILITY_MAP](docs/CAPABILITY_MAP_2026-07-02.md) + [docs/TARGET_ARCHITECTURE](docs/TARGET_ARCHITECTURE_2026-07-02.md) — the honest state of the code and where it's headed
- [SYSTEMS_MAP.md](SYSTEMS_MAP.md) — the full system map

## Run it

```bash
./restart_backend.sh                 # Flask backend on :5557
curl http://localhost:5557/health    # health check
```

There's also a lightweight offline build — **FAITHH Lite** (`faithh-lite/`) — that runs
on a laptop with just local Ollama, no homelab required. It's the reference for the
smaller devices this is meant to run on eventually.

## Status & scope (honest)

- **Active research build.** The backend is a large Flask app mid-refactor toward the
  modular target in `docs/TARGET_ARCHITECTURE`; the audit docs describe exactly what's
  live, what's orphaned, and what's planned. No inflated claims — the tiers tell you
  what's real.
- **Gen8/NAS knowledge nodes are temporarily offline** (homelab re-auth pending physical
  access). Facts tagged `[VERIFY]` wait on that; nothing gets promoted to `confirmed`
  without the live box answering.
- Not a hosted product; scoped to my setup. Useful as a reference, not turnkey.
- License: MIT.

## Stack

Flask backend · ChromaDB RAG (BGE embeddings) · multi-provider LLM (vLLM local, Groq,
Anthropic, Ollama) · Proxmox homelab with an HP Gen8 knowledge node · a Mega Man Battle
Network-styled web UI.
