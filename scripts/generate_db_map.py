#!/usr/bin/env python3
"""
Paged metadata-only census of a Chroma collection for faithh_knowledge_base.

Produces a Markdown report: domain/category/path/date aggregates, bloat top 10,
temporal heatmap, and a rolling-history canary (live conversation samples).

Environment: CHROMA_HOST, CHROMA_PORT, CHROMA_COLLECTION (same as FAITHH backend).
Optional: CHROMA_MAINT_BATCH_SIZE (default 10000), CHROMA_MAINT_REQUEST_TIMEOUT_S (default 120).

Examples:
  python scripts/generate_db_map.py
  python scripts/generate_db_map.py --output docs/DATABASE_MAP_2026-04-07.md
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import re
import math
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import chromadb
from chromadb.config import Settings


def _load_repo_dotenv() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    root = Path(__file__).resolve().parents[1]
    env_path = root / ".env"
    if env_path.is_file():
        load_dotenv(env_path, override=False)


def _chroma_host_raw() -> str:
    h = (os.environ.get("CHROMA_HOST") or "").strip()
    if h:
        return h
    legacy = (os.environ.get("CHROMADB_HOST") or "").strip()
    if legacy:
        p = os.environ.get("CHROMADB_PORT") or os.environ.get("CHROMA_PORT") or "8000"
        if "://" in legacy:
            return legacy
        return f"http://{legacy}:{p}"
    return "localhost"


def _parse_chroma_host_port() -> tuple[str, int]:
    raw = _chroma_host_raw()
    if raw.startswith("http://") or raw.startswith("https://"):
        u = urlparse(raw)
        host = u.hostname or "localhost"
        port = int(os.environ.get("CHROMA_PORT", u.port or 8000))
        return host, port
    if ":" in raw and raw.count(":") == 1:
        h, _, p = raw.partition(":")
        return h, int(os.environ.get("CHROMA_PORT", p))
    return raw, int(os.environ.get("CHROMA_PORT", "8000"))


def _chroma_client(host: str, port: int) -> chromadb.ClientAPI:
    timeout_s = int(os.environ.get("CHROMA_MAINT_REQUEST_TIMEOUT_S", "120"))
    settings = Settings(
        anonymized_telemetry=False,
        chroma_query_request_timeout_seconds=timeout_s,
        chroma_sysdb_request_timeout_seconds=max(timeout_s, 60),
    )
    return chromadb.HttpClient(host=host, port=port, settings=settings)


def _norm_meta(meta: dict | None) -> dict:
    if not meta:
        return {}
    out: dict[str, str] = {}
    for k in sorted(meta.keys(), key=lambda x: str(x)):
        v = meta.get(k)
        out[str(k)] = "" if v is None else str(v)
    return out


def _meta_fingerprint(meta: dict | None) -> str:
    blob = json.dumps(_norm_meta(meta), sort_keys=True, ensure_ascii=False).encode("utf-8", errors="ignore")
    return hashlib.sha256(blob).hexdigest()


def _infer_domain(meta: dict | None) -> str:
    m = meta or {}
    proj = str(m.get("project") or "").lower()
    blob = " ".join(
        str(m.get(k) or "")
        for k in ("project", "source", "filename", "path", "title", "doc_key")
    ).lower()
    if "alife" in blob:
        return "alife"
    if "constella" in blob or "inner_monologue_engine" in proj:
        return "constella"
    if "faithh" in blob or proj == "faithh":
        return "faithh"
    if proj in ("legal_tax_db",):
        return "faithh"
    return "unknown"


def _infer_category_bucket(meta: dict | None) -> str:
    m = meta or {}
    t = str(m.get("type") or "").lower().strip()
    c = str(m.get("category") or "").lower().strip()
    st = str(m.get("source_type") or "").lower().strip()
    fn = str(m.get("filename") or "").lower()

    if t == "live_conversation" or c in ("live_chat", "live_conversation"):
        return "live_conversation"
    if "log" in c or st == "logs" or fn.endswith(".log"):
        return "logs"
    if st in ("source_code", "code") or c in ("source_code", "code"):
        return "source_code"
    if c in ("ime_architecture", "ime_scaffold", "project_docs"):
        return c
    if c:
        return c
    if st:
        return st
    if any(fn.endswith(ext) for ext in (".py", ".ts", ".tsx", ".js", ".rb", ".go", ".rs")):
        return "source_code"
    return "other"


def _path_prefix(meta: dict | None) -> str:
    m = meta or {}
    for key in ("source", "filename", "path"):
        s = str(m.get(key) or "").strip()
        if not s:
            continue
        s = s.replace("\\", "/")
        if "/" in s:
            return s.rsplit("/", 1)[0] or "/"
        return f"(file-only) {s[:120]}"
    return "(no path)"


def _display_file_key(meta: dict | None) -> str:
    m = meta or {}
    fn = m.get("filename")
    if fn:
        return str(fn)
    src = m.get("source")
    if src:
        return str(src)
    return "(no filename)"


def _is_live_conversation(meta: dict | None) -> bool:
    m = meta or {}
    t = str(m.get("type") or "").lower().strip()
    c = str(m.get("category") or "").lower().strip()
    return t == "live_conversation" or c in ("live_chat", "live_conversation")


def _parse_created_day(meta: dict | None) -> str | None:
    m = meta or {}
    for key in ("created_at", "indexed_at", "timestamp", "mtime", "updated_at", "ts", "download_date"):
        v = m.get(key)
        if v is None:
            continue
        s = str(v).strip()
        iso = re.match(r"(\d{4}-\d{2}-\d{2})", s)
        if iso:
            return iso.group(1)
    return None


def _pct(n: int, total: int) -> str:
    if total <= 0:
        return "0.0"
    return f"{100.0 * n / total:.1f}"


def _peak_dated_day(day_counts: Counter[str]) -> tuple[str | None, int]:
    dated = {d: c for d, c in day_counts.items() if d and d != "(no date)"}
    if not dated:
        return None, 0
    peak = max(dated, key=lambda k: dated[k])
    return peak, dated[peak]


def _heatmap_lines(day_counts: Counter[str], width: int = 50) -> list[str]:
    lines: list[str] = []
    dated = {d: c for d, c in day_counts.items() if d and not d.startswith("(")}
    if not dated:
        return ["_(No dated metadata found; check keys created_at / indexed_at / timestamp / mtime.)_"]
    log_scaled = {d: math.log1p(c) for d, c in dated.items()}
    mx = max(log_scaled.values())
    for day in sorted(dated.keys()):
        c = dated[day]
        bar = int(width * log_scaled[day] / mx) if mx else 0
        lines.append(f"| {day} | `{'█' * bar}{'·' * (width - bar)}` | {c:,} |")
    undated = day_counts.get("(no date)", 0)
    if undated:
        lines.append(f"| (no date) | — | {undated:,} |")
    return lines


def _pass1_scan(
    coll,
    batch_size: int,
    total: int,
) -> tuple[
    Counter[str],
    Counter[str],
    Counter[str],
    Counter[str],
    set[str],
    Counter[str],
    str | None,
    int,
]:
    domain_c: Counter[str] = Counter()
    category_c: Counter[str] = Counter()
    prefix_c: Counter[str] = Counter()
    day_c: Counter[str] = Counter()
    fp_set: set[str] = set()
    lc_by_file: Counter[str] = Counter()

    offset = 0
    scanned = 0
    top_lc_file: str | None = None
    top_lc_count = 0

    while offset < total:
        page = coll.get(limit=batch_size, offset=offset, include=["metadatas"])
        ids = page.get("ids") or []
        if not ids:
            break
        metas = page.get("metadatas") or []

        for i, _doc_id in enumerate(ids):
            raw = metas[i] if i < len(metas) else None
            meta = raw if isinstance(raw, dict) else None

            domain_c[_infer_domain(meta)] += 1
            category_c[_infer_category_bucket(meta)] += 1
            prefix_c[_path_prefix(meta)] += 1
            fp_set.add(_meta_fingerprint(meta))
            day = _parse_created_day(meta)
            day_c[day if day else "(no date)"] += 1

            if _is_live_conversation(meta):
                fk = _display_file_key(meta)
                lc_by_file[fk] += 1
                if lc_by_file[fk] > top_lc_count:
                    top_lc_count = lc_by_file[fk]
                    top_lc_file = fk

        scanned += len(ids)
        print(
            f"[Progress] {scanned:,} / {total:,} metadata rows scanned...",
            flush=True,
        )
        offset += batch_size

    return domain_c, category_c, prefix_c, day_c, fp_set, lc_by_file, top_lc_file, top_lc_count


def _pass2_reservoir_sample_ids(
    coll,
    batch_size: int,
    total: int,
    target_file_key: str,
    k: int,
    rng: random.Random,
) -> list[str]:
    sample: list[str] = []
    seen_matching = 0
    offset = 0

    while offset < total:
        page = coll.get(limit=batch_size, offset=offset, include=["metadatas"])
        ids = page.get("ids") or []
        if not ids:
            break
        metas = page.get("metadatas") or []

        for i, doc_id in enumerate(ids):
            raw = metas[i] if i < len(metas) else None
            meta = raw if isinstance(raw, dict) else None
            if not _is_live_conversation(meta):
                continue
            if _display_file_key(meta) != target_file_key:
                continue
            seen_matching += 1
            sid = str(doc_id)
            if len(sample) < k:
                sample.append(sid)
            else:
                j = rng.randint(1, seen_matching)
                if j <= k:
                    sample[j - 1] = sid

        offset += batch_size

    return sample


def _fetch_doc_snippets(coll, ids: list[str], prefix_len: int = 50) -> list[str]:
    if not ids:
        return []
    res = coll.get(ids=ids, include=["documents"])
    out: list[str] = []
    rids = res.get("ids") or []
    rdocs = res.get("documents") or []
    by_id = {str(rids[j]): rdocs[j] if j < len(rdocs) else None for j in range(len(rids))}
    for i in ids:
        doc = by_id.get(str(i))
        text = doc if isinstance(doc, str) else ""
        one = text.replace("\n", " ").replace("\r", " ").strip()
        out.append(one[:prefix_len] + ("…" if len(one) > prefix_len else ""))
    return out


def _bloat_top10(prefix_c: Counter[str], category_c: Counter[str]) -> list[tuple[str, int]]:
    merged: list[tuple[str, int]] = []
    for p, c in prefix_c.items():
        merged.append((f"path: {p}", c))
    for cat, c in category_c.items():
        merged.append((f"category: {cat}", c))
    merged.sort(key=lambda x: (-x[1], x[0]))
    seen: set[str] = set()
    out: list[tuple[str, int]] = []
    for label, c in merged:
        if label in seen:
            continue
        seen.add(label)
        out.append((label, c))
        if len(out) >= 10:
            break
    return out


def _write_report(
    path: Path,
    *,
    collection: str,
    host: str,
    port: int,
    total: int,
    unique_meta_fp: int,
    domain_c: Counter[str],
    category_c: Counter[str],
    prefix_c: Counter[str],
    day_c: Counter[str],
    bloat: list[tuple[str, int]],
    canary_file: str | None,
    canary_count: int,
    canary_snippets: list[str],
    generated_at: str,
) -> None:
    peak_day, peak_count = _peak_dated_day(day_c)
    peak_line = f"| **Spike day** (max dated volume) | **{peak_day}** — **{peak_count:,}** records |"
    if not peak_day:
        peak_line = "| **Spike day** (max dated volume) | _(none)_ |"

    lines: list[str] = [
        f"# ChromaDB census — `{collection}`",
        "",
        f"_Generated: {generated_at} (UTC) · Host `{host}:{port}` · Script `scripts/generate_db_map.py`_",
        "",
        "## Executive summary",
        "",
        f"| Metric | Value |",
        f"|--------|------:|",
        f"| Total records | {total:,} |",
        f"| Unique metadata fingerprints (SHA-256 of canonical JSON) | {unique_meta_fp:,} |",
        peak_line,
        "",
        "_Fingerprints change if any metadata field differs; they approximate “distinct chunk identities” without reading document bodies or embeddings._",
        "",
        "## Domain distribution",
        "",
        "| Domain | Count | % of total |",
        "|--------|------:|-----------:|",
    ]
    for dom in ("alife", "faithh", "constella", "unknown"):
        n = domain_c.get(dom, 0)
        lines.append(f"| {dom} | {n:,} | {_pct(n, total)} |")
    lines.extend(
        [
            "",
            "## Category distribution",
            "",
            "| Category (bucket) | Count | % of total |",
            "|-------------------|------:|-----------:|",
        ]
    )
    for cat, n in category_c.most_common():
        lines.append(f"| {cat} | {n:,} | {_pct(n, total)} |")
    lines.extend(
        [
            "",
            "## Top 50 directory prefixes (path noise radar)",
            "",
            "| Rank | Prefix | Count | % of total |",
            "|-----:|--------|------:|-----------:|",
        ]
    )
    for rank, (pref, n) in enumerate(prefix_c.most_common(50), start=1):
        lines.append(f"| {rank} | `{pref[:200]}` | {n:,} | {_pct(n, total)} |")
    lines.extend(
        [
            "",
            '## The "Bloat" top 10',
            "",
            "Largest contributors by **path prefix** or **category bucket** (merged, de-duplicated by label).",
            "",
            "| Rank | Label | Count | % of total |",
            "|-----:|-------|------:|-----------:|",
        ]
    )
    for rank, (label, n) in enumerate(bloat, start=1):
        lines.append(f"| {rank} | {label} | {n:,} | {_pct(n, total)} |")
    lines.extend(
        [
            "",
            "## Temporal heatmap (by `created_at`-style metadata)",
            "",
            "Uses first `YYYY-MM-DD` found on keys: `created_at`, `indexed_at`, `timestamp`, `mtime`, `updated_at`, `ts`, `download_date`.",
            "",
            "_Bar width uses `log1p(count)` scaled to the hottest day so mid-volume days stay visible next to spikes._",
            "",
            "| Day | Volume (scaled) | Count |",
            "|-----|-----------------|------:|",
        ]
    )
    lines.extend(_heatmap_lines(day_c))
    lines.extend(
        [
            "",
            "## Rolling history canary (`live_conversation`)",
            "",
        ]
    )
    if not canary_file or canary_count == 0:
        lines.append("_No `live_conversation` / `live_chat` rows found, or no file key to sample._")
    else:
        lines.extend(
            [
                f"- **Highest-count file key** (within live conversation bucket): `{canary_file}`",
                f"- **Rows for that key:** {canary_count:,}",
                "",
                "First **50 characters** of **5 pseudo-random** records (document fetch; metadata-only scan does not include bodies):",
                "",
            ]
        )
        for i, snip in enumerate(canary_snippets, start=1):
            lines.append(f"{i}. `{snip}`")
        lines.extend(
            [
                "",
                "_If snippets are near-identical, you may be re-indexing the same chat repeatedly; if IDs/timestamps march (N, N+1, …), check auto-index cadence and dedupe._",
            ]
        )
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    _load_repo_dotenv()
    ap = argparse.ArgumentParser(description="Chroma metadata census → Markdown map.")
    ap.add_argument(
        "--collection",
        default=os.environ.get("CHROMA_COLLECTION", "faithh_knowledge_base"),
        help="Chroma collection name",
    )
    ap.add_argument(
        "--output",
        type=Path,
        default=Path("docs/DATABASE_MAP_2026-04-07.md"),
        help="Markdown output path",
    )
    ap.add_argument(
        "--batch-size",
        type=int,
        default=int(os.environ.get("CHROMA_MAINT_BATCH_SIZE", "10000")),
        help="Paged get limit (default 10000)",
    )
    ap.add_argument("--seed", type=int, default=None, help="RNG seed for canary sampling (optional)")
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="Connect and scan only the first batch of rows; print sample aggregates; do not write a report.",
    )
    args = ap.parse_args()

    batch_size = max(1, args.batch_size)
    rng = random.Random(args.seed)

    host, port = _parse_chroma_host_port()
    client = _chroma_client(host, port)
    coll = client.get_collection(name=args.collection)
    total = coll.count()
    scan_total = min(batch_size, total) if args.dry_run else total

    domain_c, category_c, prefix_c, day_c, fp_set, _lc_by_file, top_lc_file, top_lc_count = _pass1_scan(
        coll, batch_size, scan_total
    )

    if args.dry_run:
        lc_rows = sum(1 for k in category_c if "live" in k.lower() or k == "live_conversation")
        print(
            f"Dry-run OK: collection={args.collection} host={host}:{port} "
            f"db_total={total:,} rows_scanned={scan_total:,}",
            flush=True,
        )
        print(f"Unique metadata fingerprints (sample): {len(fp_set):,}", flush=True)
        print("Top domains:", domain_c.most_common(10), flush=True)
        print("Top category buckets:", category_c.most_common(12), flush=True)
        if top_lc_file:
            print(f"Live-conversation canary file key (partial scan): {top_lc_file} count~{top_lc_count}", flush=True)
        return 0

    bloat = _bloat_top10(prefix_c, category_c)

    canary_snippets: list[str] = []
    if top_lc_file and top_lc_count > 0:
        sample_ids = _pass2_reservoir_sample_ids(
            coll, batch_size, total, top_lc_file, k=5, rng=rng
        )
        canary_snippets = _fetch_doc_snippets(coll, sample_ids)

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    _write_report(
        args.output.resolve(),
        collection=args.collection,
        host=host,
        port=port,
        total=total,
        unique_meta_fp=len(fp_set),
        domain_c=domain_c,
        category_c=category_c,
        prefix_c=prefix_c,
        day_c=day_c,
        bloat=bloat,
        canary_file=top_lc_file,
        canary_count=top_lc_count,
        canary_snippets=canary_snippets,
        generated_at=generated_at,
    )

    print(f"Wrote {args.output.resolve()}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
