#!/usr/bin/env python3
"""Dry-run manifest for Claude conversation exports — Job A, phase 1.

WRITES NOTHING to ChromaDB. Parses the exports exactly the way the real ingest
would, generates the same deterministic chunk IDs, asks Chroma which already
exist, classifies each conversation, and reports what *would* be ingested.

    python scripts/ingest/manifest_claude_exports.py D:/faithh-ingest/raw
    python scripts/ingest/manifest_claude_exports.py <dir> --json out.json --since 2026-06-01

Compatibility notes (both shapes appear in real exports):
  * scripts/conversation_parsers.py ClaudeParser reads msg["text"] (flat)
  * scripts/chunk_claude_chats.py   reads msg["content"][] blocks
  This reads both and prefers whichever is non-empty.

Chunking mirrors chunk_claude_chats.py: groups of CHUNK_SIZE messages, chunks
under MIN_CHUNK_CHARS dropped, id = claude_chunk_{conv_uuid}_{n}.
Target collection is faithh_knowledge_base_v2 (768-dim/BGE) — the old
`documents_768` name in chunk_claude_chats.py refers to this same collection
before it was renamed. See AGENTS.md for the dimension rule.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from classify import classify  # noqa: E402

CHUNK_SIZE = 5
ID_PREFIX = "claude_chunk"   # override via --id-prefix
MIN_CHUNK_CHARS = 200
COLLECTION = "faithh_knowledge_base_v2"
CHROMA = "http://servicebox.taileb8c60.ts.net:8000"
BASE = "/api/v2/tenants/default_tenant/databases/default_database/collections"

# Classification lives in classify.py (v2: topic and mode as separate axes).


# --- parsing ------------------------------------------------------------------
def message_text(msg: dict) -> str:
    """Read either the flat `text` field or the `content[]` block array."""
    flat = (msg.get("text") or "").strip()
    if flat:
        return flat
    parts = []
    for block in msg.get("content") or []:
        if isinstance(block, dict) and block.get("type") == "text":
            parts.append(block.get("text") or "")
    return "\n".join(parts).strip()


def parse_dt(ts):
    if not ts:
        return None
    try:
        return datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
    except ValueError:
        return None


def chunk_conversation(conv: dict) -> list[dict]:
    """Mirror chunk_claude_chats.chunk_conversation, tolerant of both shapes."""
    name = conv.get("name") or "Untitled Conversation"
    created = conv.get("created_at") or ""
    msgs = conv.get("chat_messages") or []
    out = []
    for i in range(0, len(msgs), CHUNK_SIZE):
        group = msgs[i : i + CHUNK_SIZE]
        body = f"# {name} (Part {i // CHUNK_SIZE + 1})\n\nCreated: {created}\nMessages in chunk: {len(group)}\n\n---\n\n"
        for m in group:
            t = message_text(m)
            if t:
                body += f"**{(m.get('sender') or 'unknown').upper()}**:\n{t}\n\n"
        if len(body) > MIN_CHUNK_CHARS:
            out.append({"chunk_num": i // CHUNK_SIZE, "text": body, "messages": len(group)})
    return out


# --- chroma (read-only) -------------------------------------------------------
def chroma_existing_ids(ids: list[str]) -> set[str]:
    """Ask Chroma which of these chunk IDs already exist. Read-only."""
    try:
        with urllib.request.urlopen(f"{CHROMA}{BASE}", timeout=20) as r:
            cols = json.load(r)
    except Exception as e:  # noqa: BLE001
        print(f"  ! could not reach Chroma ({e}) — skipping dedupe check", file=sys.stderr)
        return set()
    cid = next((c["id"] for c in cols if c.get("name") == COLLECTION), None)
    if not cid:
        print(f"  ! collection {COLLECTION} not found — skipping dedupe check", file=sys.stderr)
        return set()
    found: set[str] = set()
    for i in range(0, len(ids), 500):
        batch = ids[i : i + 500]
        req = urllib.request.Request(
            f"{CHROMA}{BASE}/{cid}/get",
            data=json.dumps({"ids": batch, "include": []}).encode(),
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                found.update(json.load(r).get("ids") or [])
        except Exception as e:  # noqa: BLE001
            print(f"  ! dedupe batch failed ({e})", file=sys.stderr)
            break
    return found


# --- main ---------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("root", help="directory containing extracted export folders")
    ap.add_argument("--json", dest="json_out", help="write the machine-readable manifest here")
    ap.add_argument("--since", help="only include conversations created on/after YYYY-MM-DD")
    ap.add_argument("--no-dedupe", action="store_true", help="skip the Chroma existence check")
    ap.add_argument("--id-prefix", default=ID_PREFIX, help="chunk id prefix (must match the ingest run)")
    args = ap.parse_args()

    since = datetime.fromisoformat(args.since).date() if args.since else None
    files = sorted(Path(args.root).rglob("conversations.json"))
    if not files:
        print(f"no conversations.json under {args.root}", file=sys.stderr)
        return 1

    records, all_ids = [], []
    for f in files:
        source = f.parent.name
        convs = json.loads(f.read_text(encoding="utf-8"))
        print(f"reading {source}: {len(convs)} conversations")
        for conv in convs:
            dt = parse_dt(conv.get("created_at"))
            if since and (not dt or dt.date() < since):
                continue
            chunks = chunk_conversation(conv)
            if not chunks:
                continue
            full = "\n".join(c["text"] for c in chunks)
            msgs = [
                {"sender": m.get("sender"), "text": message_text(m)}
                for m in (conv.get("chat_messages") or [])
            ]
            res = classify(conv.get("name") or "", msgs)
            label = res.primary_mode
            scores = res.mode_scores
            uuid = conv.get("uuid") or "nouuid"
            ids = [f"{args.id_prefix}_{uuid}_{c['chunk_num']}" for c in chunks]
            all_ids += ids
            records.append(
                {
                    "source": source,
                    "uuid": uuid,
                    "title": (conv.get("name") or "Untitled")[:90],
                    "date": dt.date().isoformat() if dt else None,
                    "messages": len(conv.get("chat_messages") or []),
                    "chunks": len(chunks),
                    "chars": len(full),
                    "label": label,
                    "scores": scores,
                    "topic": res.topic,
                    "modes": res.modes,
                    "structure": res.structure,
                    "evidence": res.evidence,
                    "ids": ids,
                }
            )

    existing = set() if args.no_dedupe else chroma_existing_ids(all_ids)
    for r in records:
        r["new_chunks"] = sum(1 for i in r["ids"] if i not in existing)
        r["dup_chunks"] = r["chunks"] - r["new_chunks"]

    # ---- report ----
    tot_chunks = sum(r["chunks"] for r in records)
    tot_new = sum(r["new_chunks"] for r in records)
    tot_chars = sum(r["chars"] for r in records)
    by_label = Counter(r["label"] for r in records)
    chunks_by_label = defaultdict(int)
    for r in records:
        chunks_by_label[r["label"]] += r["new_chunks"]
    days = sorted({r["date"] for r in records if r["date"]})

    print("\n" + "=" * 74)
    print("DRY-RUN MANIFEST — nothing has been written")
    print("=" * 74)
    print(f"conversations in scope : {len(records):,}")
    print(f"chunks generated       : {tot_chunks:,}")
    print(f"  already in Chroma    : {tot_chunks - tot_new:,}")
    print(f"  NEW (would ingest)   : {tot_new:,}")
    print(f"text volume            : {tot_chars:,} chars (~{tot_chars // 4:,} tokens)")
    if days:
        print(f"date span              : {days[0]} -> {days[-1]}  ({len(days)} distinct days)")

    by_topic = Counter(r.get("topic", "?") for r in records)
    print("\nTOPIC — what it is about (single label):")
    for label, n in by_topic.most_common():
        print(f"  {label:<16} {n:>4}")

    mode_counts = Counter()
    for r in records:
        for m in r.get("modes") or ["unclassified"]:
            mode_counts[m] += 1
    print("\nMODE — how it is written (multi-label, conversations may appear twice):")
    for label, n in mode_counts.most_common():
        print(f"  {label:<16} {n:>4}")

    print("\nprimary mode / new chunks:")
    for label, n in by_label.most_common():
        print(f"  {label:<16} {n:>4}  /  {chunks_by_label[label]:>5}")

    print("\nsample per primary mode (with evidence):")
    for label in by_label:
        picks = [r for r in records if r["label"] == label][:3]
        print(f"  [{label}]")
        for p in picks:
            print(f"     {p['date']}  {p['chunks']:>3}ch  topic={p.get('topic','?'):<15} {p['title'][:52]}")
            if p.get("evidence"):
                print(f"        why: {', '.join(p['evidence'][:3])}")

    journals = [r for r in records if "journal" in (r.get("modes") or [])]
    if journals:
        print(f"\njournal-mode conversations: {len(journals)}  across {len({j['date'] for j in journals})} days")
        for j in sorted(journals, key=lambda r: r["chars"], reverse=True)[:5]:
            s = j.get("structure", {})
            print(f"   {j['date']}  human_ratio={s.get('human_ratio')}  avg_msg={s.get('avg_human_msg')}  {j['title'][:50]}")

    if tot_new == 0 and tot_chunks:
        print("\n>> everything in scope is already indexed; nothing new to ingest.")
    else:
        biggest = sorted(records, key=lambda r: r["new_chunks"], reverse=True)[:5]
        print("\nlargest new contributions:")
        for r in biggest:
            print(f"  {r['new_chunks']:>4} new chunks  {r['date']}  [{r['label']}]  {r['title']}")

    if args.json_out:
        Path(args.json_out).write_text(
            json.dumps(
                {
                    "generated": datetime.now().isoformat(timespec="seconds"),
                    "collection": COLLECTION,
                    "chunk_size": CHUNK_SIZE,
                    "totals": {
                        "conversations": len(records),
                        "chunks": tot_chunks,
                        "new_chunks": tot_new,
                        "chars": tot_chars,
                    },
                    "records": records,
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        print(f"\nmanifest written: {args.json_out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
