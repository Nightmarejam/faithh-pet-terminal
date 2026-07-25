#!/usr/bin/env python3
"""
Synthesize archive conversation exports into compact JSONL summaries.

Supported input format:
- directories containing `conversations.json` with list[conversation]
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, UTC
from pathlib import Path


def extract_messages(conv: dict) -> list[dict]:
    for key in ("chat_messages", "messages"):
        value = conv.get(key)
        if isinstance(value, list):
            return value
    return []


def extract_text(msg: dict) -> str:
    # Handle common export variants
    text = msg.get("text")
    if isinstance(text, str):
        return text
    parts = msg.get("parts")
    if isinstance(parts, list):
        return "\n".join(str(p) for p in parts if isinstance(p, str))
    content = msg.get("content")
    if isinstance(content, str):
        return content
    return ""


def summarize_conversation(conv: dict, source_file: Path) -> dict:
    messages = extract_messages(conv)
    user_msgs = []
    assistant_msgs = []
    for m in messages:
        role = str(m.get("sender") or m.get("role") or "").lower()
        txt = extract_text(m).strip()
        if not txt:
            continue
        if "assistant" in role or role == "ai":
            assistant_msgs.append(txt)
        else:
            user_msgs.append(txt)

    title = conv.get("name") or conv.get("title") or "untitled"
    created = conv.get("created_at") or conv.get("createdAt") or ""
    conv_id = conv.get("uuid") or conv.get("id") or f"conv_{abs(hash(title))}"

    lead_user = user_msgs[0][:800] if user_msgs else ""
    lead_assistant = assistant_msgs[0][:800] if assistant_msgs else ""
    tail_user = user_msgs[-1][:400] if user_msgs else ""

    summary_text = (
        f"Conversation: {title}\n"
        f"Created: {created}\n"
        f"Message counts: user={len(user_msgs)} assistant={len(assistant_msgs)}\n\n"
        f"Initial user intent:\n{lead_user}\n\n"
        f"Initial assistant response:\n{lead_assistant}\n\n"
        f"Latest user direction:\n{tail_user}\n"
    ).strip()

    return {
        "conversation_id": str(conv_id),
        "title": str(title),
        "created_at": str(created),
        "source_file": str(source_file),
        "message_count_user": len(user_msgs),
        "message_count_assistant": len(assistant_msgs),
        "summary_text": summary_text,
        "topic_tags": ["unclassified"],
        "quality_score": 0.6,
        "provenance": {
            "export_file": str(source_file),
            "conversation_id": str(conv_id),
        },
        "synthesized_at": datetime.now(UTC).isoformat(),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Synthesize archive conversation exports")
    parser.add_argument(
        "--inputs",
        nargs="+",
        default=["/tmp/claude_export_1", "/tmp/claude_export_2"],
        help="Input directories to scan for conversations.json",
    )
    parser.add_argument(
        "--output",
        default="/home/jonat/ai-stack/reports/inventory/archive_summaries.jsonl",
        help="Output JSONL path",
    )
    args = parser.parse_args()

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    records = []
    for inp in args.inputs:
        root = Path(inp)
        if not root.exists():
            continue
        for conv_file in root.rglob("conversations.json"):
            try:
                payload = json.loads(conv_file.read_text(encoding="utf-8", errors="ignore"))
            except json.JSONDecodeError:
                continue
            if not isinstance(payload, list):
                continue
            for conv in payload:
                if not isinstance(conv, dict):
                    continue
                records.append(summarize_conversation(conv, conv_file))

    with output.open("w", encoding="utf-8") as fh:
        for rec in records:
            fh.write(json.dumps(rec, ensure_ascii=True) + "\n")

    print(f"Output: {output}")
    print(f"Records: {len(records)}")


if __name__ == "__main__":
    main()
