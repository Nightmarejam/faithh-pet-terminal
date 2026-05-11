#!/usr/bin/env python3
"""
FAITHH ChromaDB Audit Script
==============================
Samples chunks from ChromaDB and classifies them as signal vs noise.
Run ONCE before any restructuring to understand what's actually in the database.

Usage:
    python scripts/chroma_audit.py                    # sample 500 chunks, full report
    python scripts/chroma_audit.py --sample 200       # smaller sample
    python scripts/chroma_audit.py --full             # sample all chunks (slow)
    python scripts/chroma_audit.py --export           # save labeled samples to JSON
    python scripts/chroma_audit.py --verbose          # show individual chunk previews

Output:
    - Console report: noise %, signal %, type breakdown, quality distribution
    - docs/archive/chroma_audit_YYYY-MM-DD.json (if --export)
    - Labeled training examples for future ML classifier
"""

import json
import re
import random
import argparse
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict, Counter

BASE_DIR = Path(__file__).parent.parent
CHROMA_HOST = "192.158.1.243"
CHROMA_PORT = 8000
CHROMA_COLLECTION = "faithh_knowledge_base"

# ── Type Detection Patterns ──────────────────────────────────────────────────
# Order matters — first match wins

TYPE_PATTERNS = [
    # System / log noise
    ("health_log",      [
        r"heartbeat", r"nanosecond", r"status.*ok", r"uptime",
        r"cpu.*%", r"memory.*%", r"disk.*%", r"ping",
    ]),
    ("terminal_command", [
        r"^\$\s+\w+", r"^>>>", r"^root@", r"^jonat@",
        r"sudo\s+\w+", r"apt-get", r"pip install",
        r"git (add|commit|push|pull|status|log)",
    ]),
    ("git_log", [
        r"commit [0-9a-f]{7,40}",
        r"Author:.*<.*@",
        r"Date:\s+\w{3}\s+\w{3}",
        r"\+\+\+\s+b/", r"@@\s+-\d+",
    ]),
    ("stack_trace", [
        r"Traceback \(most recent",
        r"File \".*\", line \d+",
        r"^\s+at \w+\.\w+\(",
        r"Error: .* is not defined",
    ]),
    ("json_data", [
        r'^\s*[\{\[]',
        r'"[a-z_]+"\s*:\s*[\"\[\{\d]',
        r'^\s*"[a-z_]+":\s*',
    ]),
    ("metric_data", [
        r"\d+\.\d+\s*(ms|s|MB|GB|%|fps)",
        r"p50|p95|p99",
        r"requests/sec",
        r"avg.*min.*max",
    ]),
    ("log_entry", [
        r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}",
        r"INFO\s*[\|:]", r"DEBUG\s*[\|:]",
        r"WARNING\s*[\|:]", r"ERROR\s*[\|:]",
        r"\[.*\]\s+\w+:",
    ]),
    # Content / signal
    ("decision", [
        r"decided (to|that|we|I)",
        r"rationale:", r"because (we|I|it)",
        r"alternatives considered",
        r"the reason (is|was|for)",
        r"we (chose|picked|selected|went with)",
    ]),
    ("project_discussion", [
        r"(FAITHH|Constella|Tom Cat|FGS|Floating Garden)",
        r"phase \d+", r"next steps?",
        r"working on", r"we need to",
        r"the goal (is|was)",
    ]),
    ("technical_explanation", [
        r"(ChromaDB|embedding|vector|RAG|LLM|model)",
        r"(Flask|Python|WSL|Docker|chromadb)",
        r"(function|class|method|endpoint|API)",
        r"how (it|this|the) works",
    ]),
    ("conversation", [
        r"(you|I|we) (said|mentioned|discussed|talked)",
        r"(sounds good|makes sense|exactly|right)",
        r"(what do you think|can you|could you|help me)",
        r"(jonathan|claude|chatgpt)",
    ]),
    ("document_content", [
        r"^#+\s+\w+",          # markdown headers
        r"\*\*(.*?)\*\*",      # bold text
        r"^\s*-\s+\w+",        # bullet lists
        r"^>\s+\w+",           # blockquotes
    ]),
    ("code_block", [
        r"def \w+\(", r"class \w+",
        r"import \w+", r"from \w+ import",
        r"const |let |var ",
        r"function \w+\(",
    ]),
]

SIGNAL_TYPES = {
    "decision", "project_discussion", "technical_explanation",
    "conversation", "document_content", "code_block"
}

NOISE_TYPES = {
    "health_log", "terminal_command", "git_log", "stack_trace",
    "json_data", "metric_data", "log_entry"
}

TTL_MAP = {
    "health_log": 7, "terminal_command": 7, "log_entry": 14,
    "metric_data": 14, "git_log": 30, "stack_trace": 30,
    "json_data": 30, "code_block": 365, "document_content": 365,
    "technical_explanation": 730, "project_discussion": 730,
    "conversation": 730, "decision": 9999,
}

COLLECTION_MAP = {
    "decision":               "faithh_decisions",
    "project_discussion":     "faithh_conversations",
    "conversation":           "faithh_conversations",
    "technical_explanation":  "faithh_documents",
    "document_content":       "faithh_documents",
    "code_block":             "faithh_documents",
    "health_log":             "faithh_system_logs",
    "terminal_command":       "faithh_system_logs",
    "git_log":                "faithh_system_logs",
    "log_entry":              "faithh_system_logs",
    "metric_data":            "faithh_system_logs",
    "stack_trace":            "faithh_system_logs",
    "json_data":              "faithh_ephemeral",
}


# ── Classifier ───────────────────────────────────────────────────────────────

def detect_type(text: str) -> str:
    """Rule-based type detection. Returns type string."""
    for type_name, patterns in TYPE_PATTERNS:
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE | re.MULTILINE):
                return type_name
    return "unknown"


def score_quality(text: str, detected_type: str) -> float:
    """
    Heuristic quality score 0.0 - 1.0.
    This function will be replaced by ML classifier in Phase 2.
    """
    score = 0.5  # neutral start

    # Length check
    length = len(text.strip())
    if length < 50:
        score -= 0.4
    elif length < 150:
        score -= 0.1
    elif length > 300:
        score += 0.1

    # Alpha ratio (real text vs symbols/numbers)
    alpha_ratio = sum(c.isalpha() for c in text) / max(length, 1)
    if alpha_ratio < 0.4:
        score -= 0.3
    elif alpha_ratio > 0.65:
        score += 0.1

    # Timestamp density (log indicator)
    ts_matches = len(re.findall(
        r'\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}', text
    ))
    if ts_matches > 2:
        score -= 0.2 * min(ts_matches, 3)

    # Signal keywords
    signal_words = [
        'decided', 'because', 'rationale', 'working on',
        'goal', 'phase', 'next', 'need to', 'want to',
        'the reason', 'we chose', 'makes sense'
    ]
    hits = sum(1 for w in signal_words if w in text.lower())
    score += hits * 0.05

    # Noise keywords
    noise_words = [
        'heartbeat', 'nanosecond', 'cpu%', 'ping',
        'traceback', '0.000', 'null', 'undefined'
    ]
    hits = sum(1 for w in noise_words if w in text.lower())
    score -= hits * 0.1

    # Type-based adjustment
    if detected_type in SIGNAL_TYPES:
        score += 0.15
    elif detected_type in NOISE_TYPES:
        score -= 0.2

    return round(max(0.0, min(1.0, score)), 3)


def classify_chunk(text: str, metadata: dict) -> dict:
    """Full classification of a single chunk."""
    detected_type = detect_type(text)
    quality = score_quality(text, detected_type)
    is_signal = detected_type in SIGNAL_TYPES or (
        detected_type == "unknown" and quality > 0.5
    )
    return {
        "detected_type":       detected_type,
        "quality_score":       quality,
        "is_signal":           is_signal,
        "suggested_collection": COLLECTION_MAP.get(detected_type, "faithh_unclassified"),
        "suggested_ttl_days":  TTL_MAP.get(detected_type, 90),
        "preview":             text[:120].replace("\n", " ").strip(),
    }


# ── Sampling ─────────────────────────────────────────────────────────────────

def fetch_sample(collection, n: int, verbose: bool = False) -> list:
    """Fetch n random chunks from ChromaDB."""
    total = collection.count()
    if verbose:
        print(f"  Collection has {total:,} chunks. Sampling {n}...")

    # ChromaDB doesn't have random sampling — we use offset tricks
    # Get chunks in batches with random offsets
    results = []
    batch_size = min(100, n)
    offsets_used = set()

    attempts = 0
    while len(results) < n and attempts < n * 3:
        offset = random.randint(0, max(0, total - batch_size))
        if offset in offsets_used:
            attempts += 1
            continue
        offsets_used.add(offset)

        try:
            batch = collection.get(
                limit=batch_size,
                offset=offset,
                include=["documents", "metadatas"]
            )
            docs = batch.get("documents", []) or []
            metas = batch.get("metadatas", []) or []
            ids = batch.get("ids", []) or []

            for doc, meta, doc_id in zip(docs, metas, ids):
                if doc and len(results) < n:
                    results.append({
                        "id": doc_id,
                        "text": doc,
                        "metadata": meta or {}
                    })
        except Exception as e:
            if verbose:
                print(f"  Batch error at offset {offset}: {e}")
        attempts += 1

    return results


# ── Reporting ─────────────────────────────────────────────────────────────────

COLORS = {
    "green":  "\033[92m",
    "yellow": "\033[93m",
    "red":    "\033[91m",
    "cyan":   "\033[96m",
    "dim":    "\033[2m",
    "bold":   "\033[1m",
    "reset":  "\033[0m",
}

def c(text, color): return f"{COLORS[color]}{text}{COLORS['reset']}"


def print_audit_report(results: list, total_chunks: int, sample_size: int, verbose: bool):
    now = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')

    type_counts    = Counter(r["classification"]["detected_type"] for r in results)
    signal_count   = sum(1 for r in results if r["classification"]["is_signal"])
    noise_count    = sample_size - signal_count
    signal_pct     = round(signal_count / sample_size * 100)
    noise_pct      = 100 - signal_pct
    avg_quality    = round(sum(r["classification"]["quality_score"] for r in results) / sample_size, 3)
    collection_dist = Counter(r["classification"]["suggested_collection"] for r in results)

    # Extrapolate to full collection
    est_signal = round(total_chunks * signal_pct / 100)
    est_noise  = total_chunks - est_signal

    print(f"\n{'='*62}")
    print(f"  {c('FAITHH ChromaDB Audit Report', 'bold')}")
    print(f"  {now}")
    print(f"  Sample: {sample_size:,} of {total_chunks:,} total chunks")
    print(f"{'='*62}\n")

    # Signal vs noise headline
    signal_bar = "█" * (signal_pct // 5)
    noise_bar  = "░" * ((100 - signal_pct) // 5)
    color = "green" if signal_pct >= 70 else "yellow" if signal_pct >= 50 else "red"
    print(f"  {c('SIGNAL vs NOISE', 'bold')}")
    print(f"  {c(signal_bar, color)}{c(noise_bar, 'dim')}  "
          f"{c(f'{signal_pct}% signal', color)} / {c(f'{noise_pct}% noise', 'red')}")
    print(f"  Avg quality score: {c(str(avg_quality), color)}")
    print(f"\n  Extrapolated from {sample_size:,} sample → {total_chunks:,} total:")
    print(f"  {c(f'~{est_signal:,} signal chunks', 'green')}  "
          f"/ {c(f'~{est_noise:,} noise chunks', 'red')}\n")

    # Type breakdown
    print(f"  {c('TYPE BREAKDOWN', 'bold')}")
    for type_name, count in type_counts.most_common():
        pct = round(count / sample_size * 100)
        bar = "█" * max(1, pct // 3)
        is_noise = type_name in NOISE_TYPES
        color = "red" if is_noise else "green" if type_name in SIGNAL_TYPES else "yellow"
        tag = c("[NOISE]", "red") if is_noise else c("[SIGNAL]", "green") if type_name in SIGNAL_TYPES else c("[?]", "yellow")
        print(f"  {tag} {type_name:<25} {c(bar, color)} {count:>4} ({pct}%)")

    # Collection routing projection
    print(f"\n  {c('PROJECTED COLLECTION DISTRIBUTION', 'bold')}")
    for coll, count in collection_dist.most_common():
        pct = round(count / sample_size * 100)
        est = round(total_chunks * pct / 100)
        print(f"  {coll:<35} ~{est:>6,} chunks ({pct}%)")

    # Unknown chunks (need manual review)
    unknown = [r for r in results if r["classification"]["detected_type"] == "unknown"]
    if unknown:
        print(f"\n  {c(f'UNCLASSIFIED: {len(unknown)} chunks need review', 'yellow')}")
        if verbose:
            for r in unknown[:5]:
                print(f"  {c('»', 'dim')} {r['classification']['preview']}")

    # Recommendations
    print(f"\n  {c('RECOMMENDATIONS', 'bold')}")
    if signal_pct >= 75:
        print(f"  {c('✓', 'green')} Database is mostly signal. Metadata tagging is sufficient for now.")
        print(f"    Add TTL sweep for noise chunks — estimated {est_noise:,} to eventually prune.")
    elif signal_pct >= 50:
        print(f"  {c('⚠', 'yellow')} Significant noise present. Metadata tagging + collection split recommended.")
        print(f"    Priority: quarantine {est_noise:,} noise chunks, prevent future accumulation.")
    else:
        print(f"  {c('✗', 'red')} HIGH NOISE. Collection split is urgent.")
        print(f"    ~{est_noise:,} chunks are degrading RAG search quality right now.")
        print(f"    Recommend immediate reindex with gating rules.")

    # TTL analysis
    ttl_short = sum(1 for r in results if r["classification"]["suggested_ttl_days"] <= 30)
    ttl_pct = round(ttl_short / sample_size * 100)
    est_pruneable = round(total_chunks * ttl_pct / 100)
    print(f"\n  {c('TTL ANALYSIS', 'bold')}")
    print(f"  {ttl_pct}% of chunks have TTL ≤ 30 days → ~{est_pruneable:,} chunks pruneable now")
    print(f"  A nightly TTL sweep would keep database at ~{total_chunks - est_pruneable:,} chunks")

    if verbose:
        print(f"\n  {c('SAMPLE PREVIEWS (signal)', 'bold')}")
        signal_examples = [r for r in results if r["classification"]["is_signal"]][:5]
        for r in signal_examples:
            q = r["classification"]["quality_score"]
            t = r["classification"]["detected_type"]
            print(f"  [{c(str(q), 'green')}] {c(t, 'cyan')}: {r['classification']['preview'][:80]}")

        print(f"\n  {c('SAMPLE PREVIEWS (noise)', 'bold')}")
        noise_examples = [r for r in results if not r["classification"]["is_signal"]][:5]
        for r in noise_examples:
            q = r["classification"]["quality_score"]
            t = r["classification"]["detected_type"]
            print(f"  [{c(str(q), 'red')}] {c(t, 'yellow')}: {r['classification']['preview'][:80]}")

    print(f"\n{'='*62}\n")


# ── Export ────────────────────────────────────────────────────────────────────

def export_results(results: list, total_chunks: int, sample_size: int):
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    out_dir = BASE_DIR / "docs" / "archive"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"chroma_audit_{today}.json"

    type_counts = Counter(r["classification"]["detected_type"] for r in results)
    signal_count = sum(1 for r in results if r["classification"]["is_signal"])

    export = {
        "audit_date":    today,
        "total_chunks":  total_chunks,
        "sample_size":   sample_size,
        "signal_pct":    round(signal_count / sample_size * 100),
        "noise_pct":     round((sample_size - signal_count) / sample_size * 100),
        "avg_quality":   round(sum(r["classification"]["quality_score"] for r in results) / sample_size, 3),
        "type_distribution": dict(type_counts.most_common()),
        "collection_projection": dict(
            Counter(r["classification"]["suggested_collection"] for r in results).most_common()
        ),
        # Labeled samples — training data for future ML classifier
        "labeled_samples": [
            {
                "id":       r["id"],
                "text":     r["text"][:500],
                "label":    r["classification"]["detected_type"],
                "is_signal": r["classification"]["is_signal"],
                "quality":  r["classification"]["quality_score"],
                "suggested_collection": r["classification"]["suggested_collection"],
                "suggested_ttl_days":   r["classification"]["suggested_ttl_days"],
            }
            for r in results
        ],
        "_note": "labeled_samples can be used as training data for ML classifier (Phase 2)"
    }

    out_file.write_text(json.dumps(export, indent=2))
    print(f"  Exported to: {out_file}")
    print(f"  {len(results)} labeled samples saved (future ML training data)")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="FAITHH ChromaDB Audit")
    parser.add_argument("--sample",  type=int, default=500, help="Number of chunks to sample")
    parser.add_argument("--full",    action="store_true",   help="Sample all chunks (slow)")
    parser.add_argument("--export",  action="store_true",   help="Export labeled samples to JSON")
    parser.add_argument("--verbose", action="store_true",   help="Show chunk previews")
    args = parser.parse_args()

    print(f"\n  Connecting to ChromaDB at {CHROMA_HOST}:{CHROMA_PORT}...")
    try:
        import chromadb
        client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
        collection = client.get_collection(CHROMA_COLLECTION)
        total = collection.count()
        print(f"  Connected. {total:,} chunks in {CHROMA_COLLECTION}")
    except Exception as e:
        print(f"  ERROR: Could not connect to ChromaDB: {e}")
        return

    sample_size = total if args.full else min(args.sample, total)

    print(f"  Sampling {sample_size:,} chunks...")
    raw_samples = fetch_sample(collection, sample_size, args.verbose)

    print(f"  Classifying {len(raw_samples):,} chunks...")
    results = []
    for chunk in raw_samples:
        classification = classify_chunk(chunk["text"], chunk["metadata"])
        results.append({**chunk, "classification": classification})

    print_audit_report(results, total, len(results), args.verbose)

    if args.export:
        export_results(results, total, len(results))


if __name__ == "__main__":
    main()
