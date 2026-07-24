#!/usr/bin/env python3
"""
FAITHH Conversation Tagger + Canvas Pipeline
=============================================
Runs against faithh_knowledge_base_v2. For each conversation in the Claude
export, assigns:
  - category: coding | hypothesis | learning | system | civic | personal | misc
  - novelty_score: 0.0-1.0 (keyword + structural signal, no model needed)
  - canvas_tag: big_picture | active | background | archive

Writes two outputs:
  1. Updates metadata in v2 collection (upserts category/novelty/canvas_tag)
  2. ~/ai-stack/docs/CANVAS.md — living markdown canvas of big_picture items

Usage:
  cd ~/ai-stack
  source venv/bin/activate
  python3 scripts/faithh_conversation_tagger.py [--dry-run] [--reset]

  --dry-run   print classifications without writing to chroma or disk
  --reset     re-tag all conversations (default: only untagged)
"""

from __future__ import annotations
import argparse
import json
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

# ── config ────────────────────────────────────────────────────────────────────
CHROMA_HOST = "servicebox.taileb8c60.ts.net"
CHROMA_PORT = 8000
COLLECTION  = "faithh_knowledge_base_v2"
EXPORT_FILE = Path.home() / "ai-stack/knowledge_base/imports/claude/conversations.json"
CANVAS_OUT  = Path.home() / "ai-stack/docs/CANVAS.md"
BATCH_SIZE  = 100

# ── category keyword signals ──────────────────────────────────────────────────
CATEGORY_SIGNALS: dict[str, list[str]] = {
    "coding": [
        "python", "bash", "script", "vllm", "docker", "git", "api", "function",
        "error", "traceback", "install", "npm", "cuda", "gpu", "server", "port",
        "endpoint", "chromadb", "ollama", "tmux", "cron", "systemd", "nginx",
        "proxmox", "vm", "ssh", "deploy", "backend", "frontend", "debug",
    ],
    "hypothesis": [
        "theory", "hypothesis", "quantum", "field", "energy", "frequency",
        "impedance", "dna", "genome", "fibonacci", "toroid", "resonance",
        "consciousness", "pattern", "symmetry", "breaking", "emerge", "universe",
        "gradient", "tensegrity", "fascia", "connective", "alife", "simulation",
    ],
    "learning": [
        "explain", "how does", "what is", "understand", "learning", "study",
        "research", "paper", "concept", "definition", "tutorial", "guide",
        "example", "difference between", "compare", "overview",
    ],
    "civic": [
        "constella", "governance", "voting", "ucf", "astris", "auctor",
        "policy", "civic", "community", "oxnard", "constitution", "penumbra",
        "token", "consensus", "proof of life", "faithh", "pet device",
        "cooperative", "land", "floatgarden", "tomcat",
    ],
    "system": [
        "mining", "kas", "etc", "hashrate", "miner", "pool", "nas", "proxmox",
        "grafana", "prometheus", "sensor", "telemetry", "backup", "storage",
        "network", "unifi", "pihole", "vaultwarden", "samba",
    ],
    "personal": [
        "adhd", "health", "food", "grocery", "sleep", "anxiety", "therapy",
        "relationship", "family", "money", "budget", "insurance", "rent",
        "communication", "feeling", "emotion", "life", "goals",
    ],
}

# ── novelty signals ───────────────────────────────────────────────────────────
HIGH_NOVELTY_SIGNALS = [
    "proof of life", "pet device", "riscv", "risc-v", "holoc", "holyc",
    "visionfive", "joule anchor", "astris", "auctor", "alife", "megaman",
    "battle network", "constella", "tensegrity", "toroidal", "fibonacci boundary",
    "emergent rate", "clearance tier", "behavioral entropy",
]

CANVAS_TOPICS = [
    "constella", "faithh", "proof of life", "pet device", "joule anchor",
    "holoc", "holyc", "risc-v", "riscv", "alife", "battle network",
    "megaman", "governance", "ucf", "astris", "auctor", "tensegrity",
    "connective tissue", "toroid", "fibonacci", "emergent", "canvas",
    "visionfive", "behavioral entropy",
]

# ── helpers ───────────────────────────────────────────────────────────────────

def extract_text(conv: dict) -> str:
    """Flatten all message text from a conversation."""
    parts = []
    for msg in conv.get("chat_messages", []):
        text = msg.get("text", "") or ""
        if isinstance(text, list):
            text = " ".join(
                b.get("text", "") for b in text if isinstance(b, dict)
            )
        parts.append(str(text))
    return " ".join(parts).lower()


def classify_category(text: str, title: str) -> str:
    combined = (title + " " + text[:4000]).lower()
    scores: dict[str, int] = defaultdict(int)
    for cat, keywords in CATEGORY_SIGNALS.items():
        for kw in keywords:
            if kw in combined:
                scores[cat] += 1
    if not scores:
        return "misc"
    return max(scores, key=lambda k: scores[k])


def novelty_score(text: str, title: str, msg_count: int) -> float:
    combined = (title + " " + text[:6000]).lower()
    hits = sum(1 for sig in HIGH_NOVELTY_SIGNALS if sig in combined)
    # length bonus: longer convos more likely to have original development
    length_bonus = min(msg_count / 100.0, 0.3)
    raw = min(hits / max(len(HIGH_NOVELTY_SIGNALS) * 0.15, 1), 0.7) + length_bonus
    return round(min(raw, 1.0), 3)


def canvas_tag(text: str, title: str, score: float, category: str) -> str:
    combined = (title + " " + text[:4000]).lower()
    is_canvas = any(topic in combined for topic in CANVAS_TOPICS)
    if is_canvas and score >= 0.3:
        return "big_picture"
    if score >= 0.2 or category in ("coding", "civic", "hypothesis"):
        return "active"
    if score >= 0.1:
        return "background"
    return "archive"


def build_canvas_md(canvas_items: list[dict]) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        f"# FAITHH canvas",
        f"",
        f"*last updated {now} — {len(canvas_items)} big picture items*",
        f"",
        f"This is the living map of threads that matter. Auto-generated from",
        f"conversation history. Edit tags in ChromaDB or re-run the tagger.",
        f"",
    ]

    by_cat: dict[str, list] = defaultdict(list)
    for item in sorted(canvas_items, key=lambda x: -x["novelty_score"]):
        by_cat[item["category"]].append(item)

    cat_order = ["civic", "hypothesis", "coding", "system", "learning", "personal", "misc"]
    for cat in cat_order:
        items = by_cat.get(cat, [])
        if not items:
            continue
        lines.append(f"## {cat}")
        lines.append("")
        for item in items:
            score_bar = "█" * int(item["novelty_score"] * 10) + "░" * (10 - int(item["novelty_score"] * 10))
            date = item.get("created_at", "")[:10]
            lines.append(f"- **{item['title']}**")
            lines.append(f"  `{score_bar}` novelty {item['novelty_score']:.2f} · {date} · {item['msg_count']} msgs")
            lines.append("")
        lines.append("")

    return "\n".join(lines)


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--reset", action="store_true",
                        help="re-tag all conversations, not just untagged")
    args = parser.parse_args()

    import chromadb
    client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    col = client.get_collection(COLLECTION)

    print(f"Loading export: {EXPORT_FILE}")
    with open(EXPORT_FILE) as f:
        conversations = json.load(f)
    print(f"  {len(conversations)} conversations")

    # find which conv_ids are already tagged (have category set)
    already_tagged: set[str] = set()
    if not args.reset:
        check = col.get(
            where={"source": "claude"},
            include=["metadatas"],
            limit=50000,
        )
        for meta in check["metadatas"]:
            if meta.get("category") and meta["category"] != "":
                already_tagged.add(meta.get("conversation_id", ""))
        print(f"  {len(already_tagged)} conversations already tagged (use --reset to retag)")

    canvas_items: list[dict] = []
    tagged = 0
    skipped = 0
    updates: dict[str, dict] = {}  # chunk_id -> metadata patch

    for conv in conversations:
        uuid = conv.get("uuid", "")
        title = conv.get("name", "") or conv.get("title", "untitled")
        created = conv.get("created_at", "")
        msgs = conv.get("chat_messages", [])
        msg_count = len(msgs)

        if uuid in already_tagged and not args.reset:
            skipped += 1
            continue

        text = extract_text(conv)
        if len(text) < 50:
            skipped += 1
            continue

        cat  = classify_category(text, title)
        nov  = novelty_score(text, title, msg_count)
        ctag = canvas_tag(text, title, nov, cat)

        if args.dry_run:
            print(f"  [{cat:12s}] [{ctag:12s}] nov={nov:.2f} msgs={msg_count:3d}  {title[:70]}")
        else:
            # collect chunk ids for this conversation to patch metadata
            res = col.get(
                where={"conversation_id": uuid},
                include=["metadatas"],
            )
            for i, cid in enumerate(res["ids"]):
                meta = res["metadatas"][i].copy()
                meta["category"]     = cat
                meta["novelty_score"] = str(nov)
                meta["canvas_tag"]   = ctag
                updates[cid] = meta

        if ctag == "big_picture":
            canvas_items.append({
                "title": title,
                "category": cat,
                "novelty_score": nov,
                "canvas_tag": ctag,
                "created_at": created,
                "msg_count": msg_count,
            })

        tagged += 1

    # flush updates in batches
    if not args.dry_run and updates:
        ids   = list(updates.keys())
        metas = [updates[i] for i in ids]
        print(f"\nWriting {len(ids)} chunk metadata updates to ChromaDB...")
        for start in range(0, len(ids), BATCH_SIZE):
            batch_ids   = ids[start:start+BATCH_SIZE]
            batch_metas = metas[start:start+BATCH_SIZE]
            # fetch existing docs for these ids
            existing = col.get(ids=batch_ids, include=["documents", "embeddings"])
            col.upsert(
                ids=batch_ids,
                documents=existing["documents"],
                metadatas=batch_metas,
                embeddings=existing["embeddings"],
            )
            print(f"  batch {start//BATCH_SIZE + 1}/{(len(ids)-1)//BATCH_SIZE + 1} done")

    # write canvas
    if canvas_items and not args.dry_run:
        CANVAS_OUT.parent.mkdir(parents=True, exist_ok=True)
        canvas_md = build_canvas_md(canvas_items)
        CANVAS_OUT.write_text(canvas_md)
        print(f"\nCanvas written: {CANVAS_OUT}")
        print(f"  {len(canvas_items)} big_picture items")

    print(f"\nDone. tagged={tagged} skipped={skipped}")
    if canvas_items:
        print(f"Canvas items ({len(canvas_items)}):")
        for item in sorted(canvas_items, key=lambda x: -x["novelty_score"])[:15]:
            print(f"  {item['novelty_score']:.2f}  {item['title'][:65]}")


if __name__ == "__main__":
    main()
