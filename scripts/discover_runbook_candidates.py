#!/usr/bin/env python3
"""
Mine faithh_knowledge_base for conversation chunks that look like completed runs;
score, print ranked candidates, and optionally append runbook_candidate entries to
doc_update_queue in project_states.json.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import chromadb
from chromadb.config import Settings

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
PROJECT_STATES_PATH = REPO_ROOT / "project_states.json"

# Default Chroma target matches faithh_professional_backend_fixed.py (Gen8 LAN / canonical fallback).
_DEFAULT_CHROMA_HOST = "192.158.1.243"
_DEFAULT_CHROMA_PORT = 8000
DEFAULT_COLLECTION = "faithh_knowledge_base"


def default_chroma_host_port() -> tuple[str, int]:
    """Resolve host:port from CHROMA_URL, then CHROMA_HOST / CHROMA_PORT (same as canonical backend)."""
    port = int(os.environ.get("CHROMA_PORT", str(_DEFAULT_CHROMA_PORT)))
    chroma_url = (os.environ.get("CHROMA_URL") or "").strip()
    if chroma_url:
        try:
            parsed = urlparse(chroma_url)
            if parsed.hostname:
                return parsed.hostname, int(parsed.port or port)
        except Exception:
            pass
    host = (os.environ.get("CHROMA_HOST") or _DEFAULT_CHROMA_HOST).strip() or _DEFAULT_CHROMA_HOST
    if host.startswith("http://") or host.startswith("https://"):
        parsed = urlparse(host)
        h = parsed.hostname or _DEFAULT_CHROMA_HOST
        return h, int(parsed.port or port)
    if ":" in host and host.count(":") == 1:
        h, _, ps = host.partition(":")
        try:
            return h.strip(), int(ps)
        except ValueError:
            return host, port
    return host, port

COMPLETION_QUERIES = [
    "confirmed working baseline",
    "run complete results",
    "experiment complete findings",
    "gate passed validated",
    "successfully deployed",
    "fixed and verified",
    "session close confirmed",
]

TITLE_SIGNAL_PATTERNS = (
    r"complete",
    r"deploy",
    r"validated",
    r"confirmed",
    r"baseline",
    r"working",
    r"resolved",
    r"synthesis",
    r"\bfix",
    r"\bfixed",
    r"\bfixing",
)

EXPORT_CUTOFF = date(2026, 1, 1)


def open_knowledge_collection(client: chromadb.HttpClient, collection_name: str):
    """
    faithh_knowledge_base uses SentenceTransformer (all-MiniLM-L6-v2) embeddings.
    The HTTP client must reconstruct a compatible embedding function for query_texts.
    """
    model = (os.environ.get("FAITHH_EMBEDDER_MODEL") or "all-MiniLM-L6-v2").strip()
    try:
        from chromadb.utils import embedding_functions as ef

        emb = ef.SentenceTransformerEmbeddingFunction(model_name=model, device="cpu")
        return client.get_collection(name=collection_name, embedding_function=emb)
    except ImportError as e:
        raise SystemExit(
            "discover_runbook_candidates: need sentence-transformers to query this collection.\n"
            "Install: pip install sentence-transformers\n"
            f"(ImportError: {e})"
        ) from e


@dataclass
class ChunkHit:
    distance: float
    metadata: dict
    document: str

    @property
    def conversation_title(self) -> str:
        return str(self.metadata.get("conversation_title") or "").strip()

    @property
    def conversation_id(self) -> str:
        return str(self.metadata.get("conversation_id") or "").strip()


@dataclass
class ConversationAggregate:
    dedupe_key: str
    title: str
    conversation_id: str
    best_distance: float
    has_assistant: bool
    provider: str
    export_date_raw: str
    chunks: list[ChunkHit] = field(default_factory=list)


def slugify(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value or "untitled"


def parse_export_date(raw: str | None) -> date | None:
    if raw is None:
        return None
    s = str(raw).strip()
    if not s:
        return None
    if s.isdigit():
        try:
            ts = int(s)
            if ts > 1_000_000_000_000:
                ts //= 1000
            return datetime.fromtimestamp(ts, tz=timezone.utc).date()
        except (ValueError, OSError):
            return None
    if "T" in s:
        s = s.split("T", 1)[0]
    try:
        return date.fromisoformat(s[:10])
    except ValueError:
        return None


def title_signal_bonus(title: str) -> bool:
    if not title:
        return False
    t = title.lower()
    return any(re.search(p, t) for p in TITLE_SIGNAL_PATTERNS)


def score_conversation(agg: ConversationAggregate) -> tuple[int, list[str]]:
    reasons: list[str] = []
    s = 0
    if agg.has_assistant:
        s += 2
        reasons.append("+2 assistant role in hit chunks")
    if title_signal_bonus(agg.title):
        s += 2
        reasons.append("+2 title signal (complete/fix/deploy/...)")
    prov = (agg.provider or "").lower()
    if prov == "claude":
        s += 1
        reasons.append("+1 provider=claude")
    elif "claude" in prov:
        s += 1
        reasons.append("+1 provider mentions claude")
    ed = parse_export_date(agg.export_date_raw)
    if ed is not None and ed >= EXPORT_CUTOFF:
        s += 1
        reasons.append(f"+1 export_date>={EXPORT_CUTOFF.isoformat()}")
    return s, reasons


def runbook_uri_slug(title: str, conversation_id: str) -> str:
    base = slugify(title or "untitled")
    suffix = re.sub(r"[^a-zA-Z0-9]", "", conversation_id)[:8] or "noid"
    return f"runbook://{base}-{suffix.lower()}"


def suggested_query_text(agg: ConversationAggregate) -> str:
    t = agg.title.strip() if agg.title else ""
    if not t:
        t = agg.conversation_id or "conversation"
    tail = " documented procedure outcomes verification"
    q = f"{t}{tail}"
    return q[:500]


def collect_hits(
    client: chromadb.HttpClient,
    collection_name: str,
    n_per_query: int,
) -> list[ChunkHit]:
    col = open_knowledge_collection(client, collection_name)
    total = col.count()
    n = min(n_per_query, max(1, total))
    hits: list[ChunkHit] = []
    for q in COMPLETION_QUERIES:
        try:
            res = col.query(
                query_texts=[q],
                n_results=n,
                include=["distances", "metadatas", "documents"],
            )
        except Exception as e:
            print(f"warning: query failed ({q!r}): {e}", file=sys.stderr)
            continue
        ids_row = (res.get("ids") or [[]])[0]
        dists = (res.get("distances") or [[]])[0]
        mets = (res.get("metadatas") or [[]])[0]
        docs = (res.get("documents") or [[]])[0]
        for i, _id in enumerate(ids_row):
            md = mets[i] if i < len(mets) and isinstance(mets[i], dict) else {}
            dist = dists[i] if i < len(dists) else None
            doc = docs[i] if i < len(docs) and isinstance(docs[i], str) else ""
            if not isinstance(dist, (int, float)):
                continue
            hits.append(ChunkHit(distance=float(dist), metadata=md, document=doc))
    return hits


def aggregate_by_conversation_title(hits: list[ChunkHit]) -> list[ConversationAggregate]:
    buckets: dict[str, list[ChunkHit]] = {}
    for h in hits:
        title = h.conversation_title
        cid = h.conversation_id
        key = title.lower() if title else (cid or h.metadata.get("source") or str(id(h)))
        buckets.setdefault(key, []).append(h)

    out: list[ConversationAggregate] = []
    for key, group in buckets.items():
        group.sort(key=lambda x: x.distance)
        rep = group[0]
        title = rep.conversation_title or "(untitled)"
        cid = rep.conversation_id
        has_assistant = any(
            str(x.metadata.get("role") or "").lower() == "assistant" for x in group
        )
        out.append(
            ConversationAggregate(
                dedupe_key=key,
                title=title,
                conversation_id=cid,
                best_distance=group[0].distance,
                has_assistant=has_assistant,
                provider=str(rep.metadata.get("provider") or ""),
                export_date_raw=str(rep.metadata.get("export_date") or ""),
                chunks=group,
            )
        )
    return out


def load_queued_runbook_conversation_ids() -> set[str]:
    if not PROJECT_STATES_PATH.is_file():
        return set()
    with open(PROJECT_STATES_PATH, encoding="utf-8") as f:
        data = json.load(f)
    q = data.get("doc_update_queue") or []
    seen: set[str] = set()
    for e in q:
        if not isinstance(e, dict):
            continue
        if e.get("entry_type") != "runbook_candidate":
            continue
        cid = str(e.get("conversation_id") or "").strip()
        if cid:
            seen.add(cid)
    return seen


def append_queue_entries(entries: list[dict]) -> None:
    with open(PROJECT_STATES_PATH, encoding="utf-8") as f:
        data = json.load(f)
    q = data.get("doc_update_queue")
    if q is None:
        q = []
        data["doc_update_queue"] = q
    if not isinstance(q, list):
        raise SystemExit("doc_update_queue must be a list in project_states.json")
    q.extend(entries)
    with open(PROJECT_STATES_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def parse_args() -> argparse.Namespace:
    def_host, def_port = default_chroma_host_port()
    p = argparse.ArgumentParser(description="Discover runbook seed candidates from Chroma conversation search")
    p.add_argument(
        "--host",
        default=def_host,
        help=(
            f"Chroma HTTP host (default from CHROMA_URL / CHROMA_HOST, else {_DEFAULT_CHROMA_HOST})"
        ),
    )
    p.add_argument(
        "--port",
        type=int,
        default=def_port,
        help=f"Chroma HTTP port (default CHROMA_PORT or {_DEFAULT_CHROMA_PORT})",
    )
    p.add_argument("--collection", default=DEFAULT_COLLECTION, help="Collection name")
    p.add_argument("--min-score", type=int, default=3, help="Minimum score to treat as candidate (default 3)")
    p.add_argument("--dry-run", action="store_true", help="Print only; do not write project_states.json")
    p.add_argument(
        "--seed-top",
        type=int,
        default=0,
        metavar="N",
        help="After writing, run runbook_seed_from_search.py for top N candidates (0=off)",
    )
    p.add_argument(
        "--top-print",
        type=int,
        default=0,
        metavar="N",
        help="Only print detail for first N candidates (0=all)",
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()
    timeout_s = int(os.environ.get("CHROMA_MAINT_REQUEST_TIMEOUT_S", "120"))
    settings = Settings(
        anonymized_telemetry=False,
        chroma_query_request_timeout_seconds=timeout_s,
        chroma_sysdb_request_timeout_seconds=max(timeout_s, 60),
    )
    try:
        client = chromadb.HttpClient(host=args.host, port=args.port, settings=settings)
    except Exception as e:
        print(f"error: Chroma client ({args.host}:{args.port}): {e}", file=sys.stderr)
        return 1

    hits = collect_hits(client, args.collection, 6)
    aggregates = aggregate_by_conversation_title(hits)

    scored: list[tuple[ConversationAggregate, int, list[str]]] = []
    for agg in aggregates:
        sc, rsn = score_conversation(agg)
        scored.append((agg, sc, rsn))

    scored.sort(key=lambda x: (-x[1], x[0].best_distance, x[0].title.lower()))

    queued_ids = load_queued_runbook_conversation_ids()

    candidates: list[tuple[ConversationAggregate, int, list[str]]] = []
    for agg, sc, rsn in scored:
        if sc < args.min_score:
            continue
        if not agg.conversation_id:
            continue
        candidates.append((agg, sc, rsn))

    print(
        f"Chroma {args.host}:{args.port}  collection={args.collection}  "
        f"raw_hits={len(hits)}  conversations={len(aggregates)}  "
        f"candidates(>={args.min_score})={len(candidates)}  "
        f"already_queued_runbook_ids={len(queued_ids)}"
    )
    print()

    planned_writes: list[dict] = []
    new_for_seed: list[tuple[ConversationAggregate, int, list[str]]] = []

    for rank, (agg, sc, rsn) in enumerate(candidates, start=1):
        path_uri = runbook_uri_slug(agg.title, agg.conversation_id)
        skip_queue = agg.conversation_id in queued_ids
        added_today = date.today().isoformat()
        reason = (
            f"Conversation '{agg.title}' looks like a completed run — candidate for runbook seeding"
        )
        entry = {
            "path": path_uri,
            "tier": "reference",
            "reason": reason,
            "triggered_by": "discover_runbook_candidates",
            "added": added_today,
            "status": "pending",
            "completed": None,
            "entry_type": "runbook_candidate",
            "conversation_title": agg.title,
            "conversation_id": agg.conversation_id,
            "suggested_query": suggested_query_text(agg),
        }

        do_print = args.top_print <= 0 or rank <= args.top_print
        if do_print:
            print(f"{'=' * 72}")
            print(f"Rank {rank}  score={sc}  distance_best={agg.best_distance:.4f}")
            print(f"  title: {agg.title}")
            print(f"  conversation_id: {agg.conversation_id}")
            print(f"  path: {path_uri}")
            print(f"  suggested_query: {entry['suggested_query']}")
            print(f"  scoring: {', '.join(rsn)}")
            print(f"  queue: {'SKIP (already runbook_candidate id)' if skip_queue else 'NEW'}")

        if not skip_queue:
            planned_writes.append(entry)
            if not args.dry_run:
                queued_ids.add(agg.conversation_id)
                new_for_seed.append((agg, sc, rsn))

    if args.top_print > 0 and len(candidates) > args.top_print:
        print()
        print(f"... ({len(candidates) - args.top_print} more candidates not printed; use --top-print 0 for all)")

    if not candidates:
        print("No candidates met --min-score (after filters).")
        return 0

    print()
    print(
        f"Summary: {len(candidates)} candidate(s) ranked; "
        f"{len(planned_writes)} would be queued (new conversation_ids); "
        f"{'writing' if not args.dry_run else 'dry-run — not writing'}."
    )

    if args.dry_run:
        print("Dry-run: no changes to project_states.json")
    elif planned_writes:
        append_queue_entries(planned_writes)
        print(f"Appended {len(planned_writes)} runbook_candidate entr(y/ies) to doc_update_queue.")

    if args.seed_top > 0:
        if args.dry_run:
            print("--seed-top ignored in --dry-run")
        elif not new_for_seed:
            print("--seed-top: no newly written candidates to seed")
        else:
            top = sorted(new_for_seed, key=lambda x: -x[1])[: args.seed_top]
            seed_script = REPO_ROOT / "scripts" / "runbook_seed_from_search.py"
            if not seed_script.is_file():
                print(f"warning: missing {seed_script}", file=sys.stderr)
                return 1
            for agg, sc, _ in top:
                sq = suggested_query_text(agg)
                cmd = [
                    sys.executable,
                    str(seed_script),
                    "--query",
                    sq,
                    "--host",
                    args.host,
                    "--port",
                    str(args.port),
                ]
                print(f"seed-top: running: {' '.join(cmd[:4])} ... --query {sq[:48]}...")
                r = subprocess.run(cmd, cwd=str(REPO_ROOT))
                if r.returncode != 0:
                    print(f"warning: runbook_seed_from_search exited {r.returncode}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
