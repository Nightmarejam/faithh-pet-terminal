#!/usr/bin/env python3
"""Normalize a ChatGPT export into the Claude export shape.

ChatGPT stores each conversation as a `mapping` — a node graph keyed by id, each
node holding {id, message, parent}. Claude stores a flat `chat_messages` array.
Rather than teach the manifest/classifier/ingest three formats, this converts
ChatGPT to the Claude shape once, so the whole existing pipeline works unchanged.

    python normalize_gpt_export.py D:/faithh-ingest/raw/gpt

Writes `conversations.json` into that directory, which manifest_claude_exports.py
and ingest_claude_exports.py then pick up like any other export folder.

Ordering: nodes are walked from `current_node` back through `parent` pointers,
which follows the conversation branch actually shown in the UI. Regenerated or
abandoned branches are excluded — ChatGPT keeps them in the graph, but they are
not what the user saw, and including them double-counts assistant text (this
export has 12,086 assistant nodes against 6,529 user messages).

Skipped: system/tool authors, hidden nodes, empty parts, and non-text content
types (images, execution output) which carry no useful prose.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

SKIP_ROLES = {"system", "tool"}


def iso(ts) -> str:
    if not ts:
        return ""
    try:
        return datetime.fromtimestamp(float(ts), tz=timezone.utc).isoformat()
    except (TypeError, ValueError, OSError):
        return ""


def node_text(msg: dict) -> str:
    """Join the text parts of a message, ignoring non-text payloads."""
    content = msg.get("content") or {}
    if content.get("content_type") not in (None, "text", "multimodal_text"):
        return ""
    out = []
    for p in content.get("parts") or []:
        if isinstance(p, str):
            out.append(p)
        elif isinstance(p, dict) and isinstance(p.get("text"), str):
            out.append(p["text"])
    return "\n".join(out).strip()


def walk(conv: dict) -> list[dict]:
    """Return messages along the visible branch, oldest first."""
    mapping = conv.get("mapping") or {}
    chain, seen = [], set()
    node_id = conv.get("current_node")
    # Fall back to any leaf if current_node is missing.
    if node_id not in mapping:
        parents = {n.get("parent") for n in mapping.values()}
        node_id = next((k for k in mapping if k not in parents), None)
    while node_id and node_id in mapping and node_id not in seen:
        seen.add(node_id)
        chain.append(mapping[node_id])
        node_id = mapping[node_id].get("parent")
    chain.reverse()

    msgs = []
    for node in chain:
        msg = node.get("message")
        if not msg:
            continue
        role = (msg.get("author") or {}).get("role")
        if role in SKIP_ROLES:
            continue
        meta = msg.get("metadata") or {}
        if meta.get("is_visually_hidden_from_conversation"):
            continue
        text = node_text(msg)
        if not text:
            continue
        msgs.append(
            {
                "sender": "human" if role == "user" else "assistant",
                "text": text,
                "created_at": iso(msg.get("create_time")),
            }
        )
    return msgs


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else r"D:/faithh-ingest/raw/gpt")
    files = sorted(root.glob("conversations-*.json"))
    if not files:
        print(f"no conversations-*.json in {root}", file=sys.stderr)
        return 1

    out, dropped, msg_total = [], 0, 0
    for f in files:
        for conv in json.loads(f.read_text(encoding="utf-8")):
            msgs = walk(conv)
            if not msgs:
                dropped += 1
                continue
            msg_total += len(msgs)
            out.append(
                {
                    "uuid": conv.get("conversation_id") or conv.get("id") or "",
                    "name": conv.get("title") or "Untitled",
                    "created_at": iso(conv.get("create_time")),
                    "updated_at": iso(conv.get("update_time")),
                    "chat_messages": msgs,
                }
            )

    dest = root / "conversations.json"
    dest.write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    print(f"read {len(files)} file(s)")
    print(f"conversations: {len(out)} written, {dropped} dropped (no usable messages)")
    print(f"messages kept: {msg_total:,} (visible branch only)")
    print(f"wrote {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
