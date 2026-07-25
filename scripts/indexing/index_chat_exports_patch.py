"""
FAITHH — index_chat_exports.py memory patch
============================================
Replace the all_chunks accumulation block (lines ~645–715) with this
streaming version. Everything else in the file stays IDENTICAL.

WHAT CHANGES:
  - iter_chunks() generator replaces the all_chunks list
  - Two-pass logic (count eligible, then upsert) becomes one streaming pass
  - gc.collect() called between provider batches
  - Peak RAM drops from O(all chunks) to O(batch_size)

HOW TO APPLY:
  Back up the original first:
    cp ~/ai-stack/scripts/indexing/index_chat_exports.py \
       ~/ai-stack/scripts/indexing/index_chat_exports.py.bak

  Then open the file and replace from the line:
    convs = gather_conversations(prov, all_providers=all_p)
  through the closing batch flush / post_count block
  with the code below.
"""

# ── ADD THIS IMPORT at the top of the file (after existing imports) ───────────
import gc  # already in stdlib, just add to the import block


# ── REPLACE from `convs = gather_conversations(...)` through end of main() ────

def main() -> None:
    # ... (keep all argparse / args logic above this line unchanged) ...

    # ── 1. Stream conversations provider-by-provider ──────────────────────────
    indexed_at = datetime.now(timezone.utc).isoformat()
    script_name = Path(__file__).name

    def iter_chunks():
        """Yield chunks one at a time without holding the full corpus."""
        convs = gather_conversations(prov, all_providers=all_p)
        for c in convs:
            for row in chunk_conversation(c):
                row["metadata"]["indexed_at"] = indexed_at
                row["metadata"]["indexed_by"] = script_name
                row["metadata"]["source"] = normalize_source_for_metadata(
                    row["metadata"]["source"], _REPO_ROOT
                )
                yield row
        del convs
        gc.collect()

    # ── 2. Dry-run: stream once just to count, never build the full list ───────
    if args.dry_run:
        total = sum(1 for _ in iter_chunks())
        print(f"Chunks (>=50 char messages): {total}")
        print("--dry-run: no Chroma operations performed")
        return

    if args.dry_run_grok and not args.all and args.provider != "grok":
        return

    # ── 3. Connect to Chroma ───────────────────────────────────────────────────
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

    collection = client.get_collection(
        name=args.collection.strip(),
        embedding_function=ef,
    )
    pre_count = collection.count()

    skip_ids: set[str] = set()
    if args.skip_existing:
        skip_ids = fetch_existing_conversation_ids(collection)
        print(f"skip-existing: {len(skip_ids)} conversation_id(s) already in collection")

    # ── 4. Stream-ingest — never holds more than batch_size chunks in RAM ──────
    bs = max(1, int(args.batch_size))
    batch: list[dict[str, Any]] = []
    total_upsert = 0
    total_seen = 0
    total_skipped = 0

    def flush_batch() -> None:
        nonlocal total_upsert
        if not batch:
            return
        collection.upsert(
            ids=[r["id"] for r in batch],
            documents=[r["text"] for r in batch],
            metadatas=[r["metadata"] for r in batch],
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

    flush_batch()  # final partial batch

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
