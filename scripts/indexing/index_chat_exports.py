#!/usr/bin/env python3
"""
Multi-provider chat export → faithh_knowledge_base (HTTP Chroma).

Parses Claude / ChatGPT / Grok / Windsurf / Cursor exports, normalizes, chunks,
and upserts with domain=live_conversation, document_type=chat_export.

Chroma runs only on the remote server (Gen8). This script uses chromadb as an HTTP
client (CHROMA_HOST, CHROMA_PORT); it never starts a local Chroma server.

Embeddings run client-side (SentenceTransformer). Pin the GPU with CUDA_VISIBLE_DEVICES
(e.g. 0 for RTX 3090 after nvidia-smi). Override device with CHAT_EXPORTS_EMBED_DEVICE
or --embed-device cpu if CUDA is unavailable.

Align the model with the FAITHH backend: FAITHH_EMBEDDER_MODEL (default all-MiniLM-L6-v2).

Environment: CHROMA_HOST, CHROMA_PORT, CHROMA_COLLECTION, FAITHH_EMBEDDER_MODEL,
CHAT_EXPORTS_EMBED_DEVICE, CHROMA_MAINT_REQUEST_TIMEOUT_S.
"""

from __future__ import annotations

import argparse
import gc
import hashlib
import re
import json
import os
import sys
sys.setrecursionlimit(5000)
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

_SCRIPTS_DIR = Path(__file__).resolve().parents[1]
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

import chromadb  # noqa: E402
from chromadb.config import Settings  # noqa: E402
from chromadb.utils import embedding_functions  # noqa: E402

from chroma_ingest_guard import (  # noqa: E402
    check_post_ingest_growth,
    normalize_source_for_metadata,
    validate_bulk_metadata,
)

# --- Source path constants (repo-relative) ---

CLAUDE_EXPORTS = [
    "AI_Chat_Exports/Claude_Exports/conversations.json",
    "AI_Chat_Exports/01-19-2026 Exports/Claude/conversations.json",
    "AI_Chat_Exports/Claude_Exports/Claude_Mar2026/conversations.json",
]
CLAUDE_PROJECTS = [
    "AI_Chat_Exports/Claude_Exports/projects.json",
    "AI_Chat_Exports/01-19-2026 Exports/Claude/projects.json",
    "AI_Chat_Exports/Claude_Exports/Claude_Mar2026/projects.json",
]
CHATGPT_EXPORTS = [
    "knowledge_base/imports/chatgpt/conversations.json",
    "AI_Chat_Exports/ChatGPT_Mar2026/conversations-000.json",
    "AI_Chat_Exports/ChatGPT_Mar2026/conversations-001.json",
    "AI_Chat_Exports/ChatGPT_Mar2026/conversations-002.json",
]
GROK_EXTRACTED = "AI_Chat_Exports/Grok_Exports/extracted"
WINDSURF_EXPORTS = "AI_Chat_Exports/Windsurf"
CURSOR_EXPORTS = "AI_Chat_Exports/Cursor"

CHUNK_SIZE = 1200
CHUNK_OVERLAP = 150

_IMAGE_SUFFIXES = frozenset({".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".ico"})
_SKIP_NAME_PARTS = ("zone.identifier", "user.json", "sora.json")


@dataclass
class NormalizedConversation:
    conversation_id: str
    title: str
    provider: str
    export_date: str
    messages: list[dict[str, str]] = field(default_factory=list)
    project_name: str = ""


def _repo_path(rel: str) -> Path:
    return (_REPO_ROOT / rel).resolve()


def _file_export_date(path: Path) -> str:
    try:
        ts = path.stat().st_mtime
        return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d")
    except OSError:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _parse_claude_message_text(msg: dict) -> str:
    t = msg.get("text")
    if isinstance(t, str) and t.strip():
        return t.strip()
    content = msg.get("content")
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, dict):
                tx = block.get("text")
                if isinstance(tx, str) and tx.strip():
                    parts.append(tx.strip())
        if parts:
            return "\n".join(parts)
    return ""


def parse_claude_conversations(path: str) -> list[NormalizedConversation]:
    p = _repo_path(path)
    if not p.is_file():
        return []
    with p.open(encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        return []
    out: list[NormalizedConversation] = []
    exp_file = _file_export_date(p)
    for item in data:
        if not isinstance(item, dict):
            continue
        cid = str(item.get("uuid") or "")
        if not cid:
            continue
        title = (item.get("name") or "").strip() or "Untitled"
        updated = item.get("updated_at") or item.get("created_at") or ""
        export_date = str(updated)[:10] if len(str(updated)) >= 10 else exp_file
        messages: list[dict[str, str]] = []
        for m in item.get("chat_messages") or []:
            if not isinstance(m, dict):
                continue
            body = _parse_claude_message_text(m)
            if not body:
                continue
            sender = (m.get("sender") or "").lower()
            role = "user" if sender == "human" else "assistant" if sender == "assistant" else sender or "unknown"
            ts = str(m.get("created_at") or "")
            messages.append({"role": role, "content": body, "timestamp": ts})
        if messages:
            out.append(
                NormalizedConversation(
                    conversation_id=cid,
                    title=title,
                    provider="claude",
                    export_date=export_date,
                    messages=messages,
                    project_name="",
                )
            )
    return out


def parse_claude_projects(path: str) -> list[NormalizedConversation]:
    p = _repo_path(path)
    if not p.is_file():
        return []
    with p.open(encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        return []
    out: list[NormalizedConversation] = []
    exp_file = _file_export_date(p)
    for item in data:
        if not isinstance(item, dict):
            continue
        proj = (item.get("name") or "").strip() or "Untitled Project"
        for doc in item.get("docs") or []:
            if not isinstance(doc, dict):
                continue
            du = str(doc.get("uuid") or "")
            if not du:
                continue
            content = doc.get("content")
            if not isinstance(content, str) or not content.strip():
                continue
            fn = (doc.get("filename") or "untitled").strip()
            ts = str(doc.get("created_at") or "")
            export_date = ts[:10] if len(ts) >= 10 else exp_file
            out.append(
                NormalizedConversation(
                    conversation_id=du,
                    title=fn,
                    provider="claude_project",
                    export_date=export_date,
                    messages=[{"role": "document", "content": content.strip(), "timestamp": ts}],
                    project_name=proj,
                )
            )
    return out


def _chatgpt_message_text(msg: dict) -> tuple[str, str, str]:
    author = msg.get("author") or {}
    role = (author.get("role") or "").lower()
    content = msg.get("content") or {}
    parts = content.get("parts") if isinstance(content, dict) else None
    if not isinstance(parts, list) or not parts:
        return "", "", ""
    texts = []
    for part in parts:
        if isinstance(part, str) and part.strip():
            texts.append(part)
    text = "".join(texts).strip()
    ct = msg.get("create_time")
    ts = str(ct) if ct is not None else ""
    return role, text, ts


def _chatgpt_ordered_messages(mapping: dict[str, Any]) -> list[dict[str, str]]:
    if not mapping:
        return []

    roots = []
    for nid, node in mapping.items():
        if not isinstance(node, dict):
            continue
        if node.get("parent") is None:
            roots.append(str(nid))

    out: list[dict[str, str]] = []
    visited: set[str] = set()

    def visit(nid: str) -> None:
        if nid in visited or nid not in mapping:
            return
        visited.add(nid)
        node = mapping[nid]
        if not isinstance(node, dict):
            return
        msg = node.get("message")
        if isinstance(msg, dict):
            role, text, ts = _chatgpt_message_text(msg)
            if role in ("user", "assistant") and text:
                out.append({"role": role, "content": text, "timestamp": ts})
        for ch in node.get("children") or []:
            if isinstance(ch, str) and ch:
                visit(ch)

    for r in roots:
        visit(r)
    return out


def parse_chatgpt_conversations(paths: list[str]) -> list[NormalizedConversation]:
    by_id: dict[str, NormalizedConversation] = {}
    for rel in paths:
        p = _repo_path(rel)
        if not p.is_file():
            continue
        exp_file = _file_export_date(p)
        with p.open(encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            continue
        for item in data:
            if not isinstance(item, dict):
                continue
            cid = str(item.get("conversation_id") or item.get("id") or "")
            if not cid:
                continue
            title = (item.get("title") or "").strip() or "Untitled"
            mapping = item.get("mapping")
            if not isinstance(mapping, dict):
                continue
            messages = _chatgpt_ordered_messages(mapping)
            if not messages:
                continue
            ct = item.get("create_time")
            export_date = exp_file
            if isinstance(ct, (int, float)):
                export_date = datetime.fromtimestamp(float(ct), tz=timezone.utc).strftime("%Y-%m-%d")
            by_id[cid] = NormalizedConversation(
                conversation_id=cid,
                title=title,
                provider="chatgpt",
                export_date=export_date,
                messages=messages,
                project_name="",
            )
    return list(by_id.values())


def _is_probably_utf8_text(raw: bytes) -> bool:
    if not raw or raw.startswith(b"\x00"):
        return False
    if len(raw) > 4 and raw[:4] in (b"\x89PNG", b"\xff\xd8\xff"):
        return False
    try:
        raw.decode("utf-8")
        return True
    except UnicodeDecodeError:
        return False


def _grok_content_files(extracted_dir: Path) -> list[Path]:
    base = extracted_dir / "ttl" / "30d" / "export_data"
    if not base.is_dir():
        return []
    files: list[Path] = []
    for user_dir in base.iterdir():
        if not user_dir.is_dir():
            continue
        asset = user_dir / "prod-mc-asset-server"
        if not asset.is_dir():
            continue
        for conv_dir in asset.iterdir():
            if not conv_dir.is_dir():
                continue
            cf = conv_dir / "content"
            if cf.is_file():
                files.append(cf)
    return sorted(files)


def dry_run_grok_peek(extracted_dir: str, n: int = 3, preview: int = 200) -> None:
    root = _repo_path(extracted_dir)
    all_cf = _grok_content_files(root)
    paths = all_cf[:n]
    if not paths:
        print(f"[dry-run-grok] No content files under {extracted_dir!r}")
        return
    print(f"[dry-run-grok] total content files: {len(all_cf)}; previewing {len(paths)}")
    for i, cf in enumerate(paths):
        raw = cf.read_bytes()[: 8192 * 4]
        ok = _is_probably_utf8_text(raw)
        label = "utf-8-text" if ok else "binary/non-utf8"
        snippet = ""
        if ok:
            snippet = raw.decode("utf-8", errors="replace")[:preview].replace("\n", "\\n")
        print(f"  [{i}] {cf.relative_to(_REPO_ROOT)} ({label}): {snippet!r}")


def parse_grok_conversations(extracted_dir: str) -> list[NormalizedConversation]:
    root = _repo_path(extracted_dir)
    files = _grok_content_files(root)
    out: list[NormalizedConversation] = []
    exp_file = _file_export_date(root) if root.exists() else datetime.now(timezone.utc).strftime("%Y-%m-%d")
    for cf in files:
        raw = cf.read_bytes()
        if not _is_probably_utf8_text(raw):
            continue
        text = raw.decode("utf-8", errors="strict").strip()
        if len(text) < 10:
            continue
        conv_uuid = cf.parent.name
        out.append(
            NormalizedConversation(
                conversation_id=conv_uuid,
                title=conv_uuid,
                provider="grok",
                export_date=exp_file,
                messages=[{"role": "document", "content": text, "timestamp": exp_file}],
                project_name="",
            )
        )
    return out


def _should_skip_path(p: Path) -> bool:
    name_lower = p.name.lower()
    if "zone.identifier" in name_lower:
        return True
    for part in _SKIP_NAME_PARTS:
        if part in name_lower and p.suffix.lower() == ".json":
            return True
    if p.suffix.lower() in _IMAGE_SUFFIXES:
        return True
    parts = {x.lower() for x in p.parts}
    if "venv" in parts or "__pycache__" in parts or ".git" in parts:
        return True
    return False


def parse_markdown_exports(paths: list[str], provider: str) -> list[NormalizedConversation]:
    out: list[NormalizedConversation] = []
    for rel in paths:
        p = _repo_path(rel)
        if not p.is_file() or p.suffix.lower() not in (".md", ".markdown"):
            continue
        if _should_skip_path(p):
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        if not text.strip():
            continue
        rel_str = str(p.relative_to(_REPO_ROOT))
        h = hashlib.sha256(rel_str.encode()).hexdigest()[:12]
        title = p.stem
        mtime = datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc).isoformat()
        export_date = _file_export_date(p)
        out.append(
            NormalizedConversation(
                conversation_id=h,
                title=title,
                provider=provider,
                export_date=export_date,
                messages=[{"role": "document", "content": text.strip(), "timestamp": mtime}],
                project_name="",
            )
        )
    return out


def collect_markdown_dir(rel_dir: str, provider: str) -> list[NormalizedConversation]:
    d = _repo_path(rel_dir)
    if not d.is_dir():
        return []
    paths = []
    for p in sorted(d.glob("*.md")):
        if _should_skip_path(p):
            continue
        try:
            rel = str(p.relative_to(_REPO_ROOT))
        except ValueError:
            continue
        paths.append(rel)
    return parse_markdown_exports(paths, provider)



def _is_low_quality(content: str) -> bool:
    """Quality gate — returns True if chunk should not be indexed."""
    if len(content) < 150:
        return True
    urls = re.findall(r'https?://\S+', content)
    url_chars = sum(len(u) for u in urls)
    if url_chars / len(content) > 0.5:
        return True
    file_refs = re.findall(r'\S+\.(png|jpg|jpeg|gif|pdf|zip)\b', content, re.IGNORECASE)
    if len(file_refs) > 5 and url_chars / max(len(content), 1) > 0.3:
        return True
    return False


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    text = text.strip()
    if not text:
        return []
    if len(text) <= chunk_size:
        return [text]
    chunks: list[str] = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + chunk_size, n)
        if end < n:
            for sep in ("\n\n", "\n", ". ", " "):
                boundary = text.rfind(sep, start + overlap, end)
                if boundary > start + overlap:
                    end = boundary + len(sep)
                    break
        chunks.append(text[start:end])
        if end >= n:
            break
        start = max(end - overlap, start + 1)
    return chunks


def stable_chunk_id(conv: NormalizedConversation, msg_index: int, chunk_index: int, text: str) -> str:
    h = hashlib.sha256(
        f"{conv.provider}|{conv.conversation_id}|{msg_index}|{chunk_index}|{text[:200]}".encode()
    ).hexdigest()[:16]
    safe_prov = "".join(c if c.isalnum() or c in "-_" else "_" for c in conv.provider[:20])
    safe_cid = "".join(c if c.isalnum() or c in "-_" else "_" for c in conv.conversation_id[:36])
    return f"chatexp_{safe_prov}_{safe_cid}_{msg_index}_{chunk_index}_{h}"


def chunk_conversation(conv: NormalizedConversation) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    title_safe = (conv.title or "untitled")[:60]
    base_source = f"{conv.provider}/{title_safe}"
    for mi, msg in enumerate(conv.messages):
        content = (msg.get("content") or "").strip()
        role = msg.get("role") or "unknown"
        ts = msg.get("timestamp") or ""
        if _is_low_quality(content):
            continue
        for ci, piece in enumerate(chunk_text(content)):
            meta = {
                "domain": "live_conversation",
                "category": "chat_export",
                "source": base_source,
                "provider": conv.provider,
                "conversation_id": conv.conversation_id,
                "conversation_title": conv.title[:500] if conv.title else "",
                "role": role,
                "project_name": conv.project_name or "",
                "export_date": conv.export_date,
                "document_type": "chat_export",
                "message_index": mi,
                "chunk_index": ci,
            }
            bad = validate_bulk_metadata(meta, keys=("domain", "category", "source"))
            if bad:
                raise SystemExit(f"chunk metadata missing {bad}")
            cid = stable_chunk_id(conv, mi, ci, piece)
            out.append({"id": cid, "text": piece, "metadata": meta})
    return out


def _default_embed_device() -> str:
    d = (os.environ.get("CHAT_EXPORTS_EMBED_DEVICE") or "cuda").strip().lower()
    return d if d in ("cuda", "cpu") else "cuda"


def _make_embedding_function(args: argparse.Namespace):
    """Local SentenceTransformer embedder; vectors are sent to remote Chroma (Gen8)."""
    model = os.environ.get("FAITHH_EMBEDDER_MODEL", "all-MiniLM-L6-v2").strip()
    return embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=model,
        device=args.embed_device,
    )


def _parse_chroma_host_port() -> tuple[str, int]:
    raw = (os.environ.get("CHROMA_HOST") or "").strip()
    if not raw:
        legacy = (os.environ.get("CHROMADB_HOST") or "").strip()
        if legacy:
            p = os.environ.get("CHROMADB_PORT") or os.environ.get("CHROMA_PORT") or "8000"
            raw = legacy if "://" in legacy else f"http://{legacy}:{p}"
        else:
            raw = "127.0.0.1"
    if raw.startswith("http://") or raw.startswith("https://"):
        u = urlparse(raw)
        host = u.hostname or "localhost"
        port = int(os.environ.get("CHROMA_PORT", u.port or 8000))
        return host, port
    if ":" in raw and raw.count(":") == 1:
        h, _, p = raw.partition(":")
        return h, int(os.environ.get("CHROMA_PORT", p))
    return raw, int(os.environ.get("CHROMA_PORT", "8000"))


def _load_repo_dotenv() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    env_path = _REPO_ROOT / ".env"
    if env_path.is_file():
        load_dotenv(env_path, override=False)


def fetch_existing_conversation_ids(collection, *, page_size: int = 2000) -> set[str]:
    existing: set[str] = set()
    offset = 0
    while True:
        try:
            page = collection.get(
                where={"document_type": "chat_export"},
                include=["metadatas"],
                limit=page_size,
                offset=offset,
            )
        except Exception:
            break
        metas = page.get("metadatas") or []
        ids = page.get("ids") or []
        if not ids:
            break
        for m in metas:
            if isinstance(m, dict):
                cid = m.get("conversation_id")
                if cid:
                    existing.add(str(cid))
        if len(ids) < page_size:
            break
        offset += page_size
    return existing


def iter_conversations(provider: str | None, *, all_providers: bool):
    """
    Generator — yields one NormalizedConversation at a time.
    Never holds the full corpus in memory simultaneously.
    Calls gc.collect() between providers to release parsed JSON.
    """

    def _yield_claude():
        for rel in CLAUDE_EXPORTS:
            yield from parse_claude_conversations(rel)
            gc.collect()
        for rel in CLAUDE_PROJECTS:
            yield from parse_claude_projects(rel)
            gc.collect()

    def _yield_chatgpt():
        for rel in CHATGPT_EXPORTS:
            yield from parse_chatgpt_conversations([rel])
            gc.collect()

    def _yield_grok():
        yield from parse_grok_conversations(GROK_EXTRACTED)
        gc.collect()

    def _yield_md():
        yield from collect_markdown_dir(WINDSURF_EXPORTS, "windsurf")
        gc.collect()
        yield from collect_markdown_dir(CURSOR_EXPORTS, "cursor")
        gc.collect()

    if all_providers or provider is None:
        yield from _yield_claude()
        yield from _yield_chatgpt()
        yield from _yield_grok()
        yield from _yield_md()
        return

    p = provider.lower().strip()
    if p == "claude":
        yield from _yield_claude()
    elif p == "chatgpt":
        yield from _yield_chatgpt()
    elif p == "grok":
        yield from _yield_grok()
    elif p == "windsurf":
        yield from collect_markdown_dir(WINDSURF_EXPORTS, "windsurf")
    elif p == "cursor":
        yield from collect_markdown_dir(CURSOR_EXPORTS, "cursor")
    else:
        raise SystemExit(f"Unknown --provider {provider!r}")


def main() -> None:
    _load_repo_dotenv()
    ap = argparse.ArgumentParser(description="Index multi-provider chat exports into faithh_knowledge_base")
    ap.add_argument("--dry-run", action="store_true", help="Count only; no Chroma writes")
    ap.add_argument("--dry-run-grok", action="store_true", help="Print Grok content samples; no indexing")
    ap.add_argument("--all", action="store_true", help="All providers")
    ap.add_argument("--provider", help="claude|chatgpt|grok|windsurf|cursor")
    ap.add_argument("--skip-existing", action="store_true", help="Skip chunks whose conversation_id exists")
    ap.add_argument("--batch-size", type=int, default=100, help="Upsert batch size (default 100)")
    ap.add_argument("--collection", default=os.environ.get("CHROMA_COLLECTION", "faithh_knowledge_base"))
    ap.add_argument("--force", action="store_true", help="Allow >3× collection growth (chroma_ingest_guard)")
    ap.add_argument(
        "--embed-device",
        choices=("cuda", "cpu"),
        default=_default_embed_device(),
        help="SentenceTransformer device for client-side embeddings (env CHAT_EXPORTS_EMBED_DEVICE default: cuda)",
    )
    args = ap.parse_args()

    if args.dry_run_grok:
        dry_run_grok_peek(GROK_EXTRACTED)
        if not (args.dry_run or args.all or args.provider):
            return

    if not args.dry_run:
        if not args.all and not args.provider:
            ap.error("Indexing requires --all or --provider (use --dry-run to count only)")

    if args.provider:
        all_p = False
        prov: str | None = args.provider
    else:
        all_p = True
        prov = None

    indexed_at = datetime.now(timezone.utc).isoformat()
    script_name = Path(__file__).name

    def iter_chunks():
        """Yield chunks one at a time without holding the full corpus."""
        for c in iter_conversations(prov, all_providers=all_p):
            for row in chunk_conversation(c):
                row["metadata"]["indexed_at"] = indexed_at
                row["metadata"]["indexed_by"] = script_name
                row["metadata"]["source"] = normalize_source_for_metadata(
                    row["metadata"]["source"], _REPO_ROOT
                )
                yield row
        gc.collect()

    if args.dry_run:
        total = sum(1 for _ in iter_chunks())
        print(f"Chunks (>=50 char messages): {total}")
        print("--dry-run: no Chroma operations performed")
        return

    if args.dry_run_grok and not args.all and args.provider != "grok":
        return

    host, port = _parse_chroma_host_port()
    timeout_s = int(os.environ.get("CHROMA_MAINT_REQUEST_TIMEOUT_S", "120"))
    client = chromadb.HttpClient(
        host=host,
        port=port,
        settings=Settings(
            anonymized_telemetry=False,
            chroma_query_request_timeout_seconds=timeout_s,
            chroma_sysdb_request_timeout_seconds=max(timeout_s, 60),
        ),
    )
    ef = _make_embedding_function(args)
    model_id = os.environ.get("FAITHH_EMBEDDER_MODEL", "all-MiniLM-L6-v2").strip()
    print(f"Client-side embeddings: model={model_id!r} device={args.embed_device!r} → {host}:{port}")

    collection = client.get_or_create_collection(
        name=args.collection.strip(),
        embedding_function=ef,
        metadata={"dimension": 768},
    )
    pre_count = collection.count()

    skip_ids: set[str] = set()
    if args.skip_existing:
        skip_ids = fetch_existing_conversation_ids(collection)
        print(f"skip-existing: {len(skip_ids)} conversation_id(s) already in collection")

    bs = max(1, int(args.batch_size))
    batch: list[dict[str, Any]] = []
    total_upsert = 0
    total_seen = 0
    total_skipped = 0

    def flush_batch() -> None:
        nonlocal total_upsert
        if not batch:
            return
        # Deduplicate within batch (ChatGPT shards can overlap)
        seen: set[str] = set()
        deduped = [r for r in batch if not seen.__contains__(r["id"]) and not seen.add(r["id"])]
        collection.upsert(
            ids=[r["id"] for r in deduped],
            documents=[r["text"] for r in deduped],
            metadatas=[r["metadata"] for r in deduped],
        )
        total_upsert += len(batch)
        print(
            f"   > Upserted {total_upsert} rows so far "
            f"(batch={len(batch)}, skipped={total_skipped})",
            end="\r",
            flush=True,
        )
        batch.clear()

    for row in iter_chunks():
        total_seen += 1
        cid_meta = row["metadata"].get("conversation_id")
        if args.skip_existing and cid_meta and str(cid_meta) in skip_ids:
            total_skipped += 1
            continue
        batch.append(row)
        if len(batch) >= bs:
            flush_batch()

    flush_batch()

    print()
    post_count = collection.count()
    print(
        f"Chunks seen: {total_seen}  Skipped: {total_skipped}  "
        f"Upserted: {total_upsert}  "
        f"Collection: {pre_count:,} -> {post_count:,}"
    )

    try:
        check_post_ingest_growth(
            pre_count,
            post_count,
            multiplier=3.0,
            force=args.force,
            label=f"{args.collection} (index_chat_exports)",
        )
    except SystemExit as exc:
        print(str(exc), file=sys.stderr)
        raise


if __name__ == "__main__":
    main()
