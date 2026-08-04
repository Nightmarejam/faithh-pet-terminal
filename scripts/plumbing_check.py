#!/usr/bin/env python3
"""Probe every declared dependency and report where config, docs and reality differ.

Run this before and after changing provider wiring. The point is not "is the app
up" - it is **does what we believe match what is actually listening**. Every check
here exists because the answer was no at least once.

## Why a dedicated probe rather than reading the config

`fingerprint_state.json` is generated, and the copy in the tree is dated
2026-05-17. It already recorded `ollama: unreachable` and `groq_available: false`.
A stale artifact that says something is broken is indistinguishable from a fresh
one that says the same thing, so it cannot tell you whether the break is new.
This probe resolves config the way `backend/config.py` does and then actually
connects.

## The divergences it was written to catch

`ARCHITECTURE.md` lists Ollama on 11434 as ✅ Active and as the primary provider,
and puts ChromaDB on `localhost:8000`. In fact ChromaDB lives on the Gen8 over the
tailnet, `config.yaml` names `groq` as primary with `anthropic` as fallback, and
the only local inference that actually works - vLLM serving qwen2.5-14b on the
3090 - appears nowhere in the document at all.

Collection dimension is checked because it has bitten before: `rag_processor.py`
embeds with BAAI/bge-base-en-v1.5 (768), and pointing that at a 384-dim collection
does not error. Every query is silently rejected, `best_distance` pins at 1.0, and
answers come back fluent and ungrounded - the worst failure shape there is.

## Run this ON THE DEPLOYMENT HOST

The live backend is a bare python process on the Gen8, cwd `/home/jonat/ai-stack`,
listening on 5557 — a second clone of this repo, 35 commits behind origin/main and
carrying its own uncommitted `config.yaml` and `.env`. Running the probe from a
Windows checkout tests that machine's localhost and reports failures that are true
there and false in production. It cost a full round of wrong conclusions here:
"no API keys" and "backend down" were both artifacts of probing the wrong host.

## Ask the app what it did, do not infer it from config

An earlier version of this probe concluded the vLLM was unwired because no module
grepped for `VLLM_HOST`. That was wrong. Routing is declared in
`configs/model_config.yaml` — a `vllm` provider of `type: openai_compatible`,
listed **first** in `routes.auto`, `routes.local`, `routes.code` and
`routes.reasoning` — and the live backend answers with
`provider: "vLLM (RTX 3090)"`. The `.env` `VLLM_*` vars really are read by nobody,
but they are vestigial, not the wiring.

The lesson is the check below: **send a request and read back which provider
served it.** Config greps prove what is declared; only a round trip proves what
runs. Three separate wrong conclusions here came from inferring — reading the
Windows `config.yaml` rather than `configs/model_config.yaml`, grepping env names,
and probing the wrong host.

Exit 0 when nothing diverges, 1 otherwise.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

TIMEOUT = 6
leaks: list[str] = []


def leak(msg: str) -> None:
    leaks.append(msg)
    print(f"  [LEAK] {msg}")


def ok(msg: str) -> None:
    print(f"  [ ok ] {msg}")


def env(*names: str, default: str = "") -> str:
    """Mirror backend/config.py: last alias present wins."""
    val = default
    for n in names:
        v = os.getenv(n)
        if v is not None:
            val = v
    return val


def get(url: str, timeout: int = TIMEOUT):
    req = urllib.request.Request(url, headers={"User-Agent": "faithh-plumbing/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read() or b"null")


def section(t: str) -> None:
    print(f"\n=== {t} ===")


def check_chroma() -> None:
    section("chromadb")
    host = env("CHROMA_HOST", "CHROMADB_HOST", default="servicebox.taileb8c60.ts.net")
    port = env("CHROMA_PORT", "CHROMADB_PORT", default="8000")
    want = env("CHROMA_COLLECTION", default="faithh_knowledge_base_v2")
    base = f"http://{host}:{port}"
    print(f"  resolved {base}  collection={want}")
    if host in ("localhost", "127.0.0.1"):
        leak("CHROMA_HOST resolves to localhost - ARCHITECTURE.md says localhost:8000, "
             "but the instance runs on the Gen8 over the tailnet")
    try:
        get(f"{base}/api/v2/heartbeat")
        ok("heartbeat")
    except Exception as exc:
        leak(f"chromadb unreachable at {base}: {str(exc)[:60]}")
        return
    try:
        cols = get(f"{base}/api/v2/tenants/default_tenant/databases/default_database/collections")
    except Exception as exc:
        leak(f"cannot list collections: {str(exc)[:60]}")
        return
    names = [c.get("name") for c in (cols or [])]
    if want not in names:
        leak(f"configured collection {want!r} does not exist; found {names[:6]}")
        return
    ok(f"collection {want} exists ({len(names)} collections total)")
    # 768 vs 384 is the silent-ungrounded-answers failure. Check, do not assume.
    for c in cols:
        if c.get("name") == want:
            dim = (c.get("configuration_json") or {}).get("hnsw", {}).get("dimension") \
                  or c.get("dimension")
            if dim and int(dim) != 768:
                leak(f"{want} is {dim}-dim; rag_processor embeds at 768 - every "
                     f"query would be rejected with best_distance pinned at 1.0")
            elif dim:
                ok(f"{want} is {dim}-dim, matches the 768-dim embedder")
            else:
                print("  [ ?? ] dimension not exposed by this Chroma version")


def check_ollama() -> None:
    section("ollama (config's local provider)")
    host = env("OLLAMA_HOST", default="http://localhost:11434")
    model = env("OLLAMA_MODEL", "OLLAMA_DEFAULT_MODEL", default="qwen2.5:7b")
    print(f"  resolved {host}  model={model}")
    try:
        tags = get(f"{host.rstrip('/')}/api/tags")
    except Exception as exc:
        # Output stays ASCII on purpose: this runs in a Windows console under
        # cp1252, where a stray checkmark from ARCHITECTURE.md raises
        # UnicodeEncodeError and takes the whole probe down mid-run.
        leak(f"ollama unreachable at {host} ({str(exc)[:44]}) - but ARCHITECTURE.md "
             f"lists it as the PRIMARY provider and 'Active'")
        return
    have = [m.get("name") for m in (tags or {}).get("models", [])]
    ok(f"reachable, {len(have)} model(s)")
    if model not in have:
        leak(f"configured model {model!r} not pulled; have {have[:5]}")


def check_vllm() -> None:
    section("vllm on the 3090")
    base = env("VLLM_BASE_URL", "OPENAI_BASE_URL",
               default="http://desktop-iifeikl.taileb8c60.ts.net:8000/v1")
    print(f"  resolved {base}")
    try:
        d = get(f"{base.rstrip('/')}/models")
    except Exception as exc:
        leak(f"vllm unreachable at {base}: {str(exc)[:60]}")
        return
    ids = [m.get("id") for m in (d or {}).get("data", [])]
    ok(f"serving {ids}")
    # Whether anything ROUTES here is settled by check_routing()'s round trip,
    # not by grepping for env names. This check only proves the endpoint is up.


def check_keys() -> None:
    section("provider keys (presence only, never values)")
    for label, names in (("groq", ("GROQ_API_KEY",)),
                         ("anthropic", ("ANTHROPIC_API_KEY",)),
                         ("gemini", ("GEMINI_API_KEY", "GOOGLE_API_KEY"))):
        v = env(*names)
        if v:
            ok(f"{label}: set ({len(v)} chars)")
        else:
            leak(f"{label}: not set - config.yaml names groq primary and anthropic "
                 f"fallback, so this shell cannot reach either")


def check_routing() -> None:
    """Round-trip the live backend and read back which provider actually served.

    This is the only check here that proves behaviour rather than declaration.
    `configs/model_config.yaml` can name vllm first in every route and still be
    overridden at runtime, and a process started before a config edit runs the old
    file regardless of what is on disk. Ask, do not infer.
    """
    section("live routing (round trip)")
    port = env("BACKEND_PORT", "FAITHH_PORT", default="5557")
    body = json.dumps({"message": "Reply with exactly: PONG",
                       "provider": "vllm"}).encode()
    req = urllib.request.Request(f"http://localhost:{port}/api/chat", data=body,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            d = json.loads(r.read())
    except Exception as exc:
        leak(f"cannot round-trip /api/chat: {str(exc)[:60]}")
        return
    prov, model = d.get("provider"), d.get("model_used")
    ok(f"served by {prov!r} using {model!r}")
    if not prov or "vllm" not in str(prov).lower():
        leak(f"asked for vllm, got {prov!r} - the 3090 is not taking traffic")


def check_backend() -> None:
    section("faithh backend")
    port = env("FAITHH_PORT", default="5557")
    try:
        get(f"http://localhost:{port}/health", timeout=4)
        ok(f"backend healthy on {port}")
    except Exception as exc:
        leak(f"backend not answering on {port}: {str(exc)[:50]}")


def main() -> int:
    print("FAITHH plumbing check - resolved config vs what is actually listening")
    check_chroma()
    check_ollama()
    check_vllm()
    check_keys()
    check_routing()
    check_backend()
    print(f"\n=== verdict ===\n  {len(leaks)} divergence(s)")
    return 1 if leaks else 0


if __name__ == "__main__":
    sys.exit(main())
