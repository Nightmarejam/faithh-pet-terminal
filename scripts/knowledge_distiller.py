#!/usr/bin/env python3
"""
FAITHH Knowledge Distiller
============================
Scans all conversation chunks in ChromaDB, groups by conversation,
evaluates each for signal quality using a local LLM, and produces
a structured "Gold Nuggets" report of actionable insights.

Think of it as chip_synthesis for *ideas* instead of topic clusters.

Pipeline:
  1. Pull all chunks from ChromaDB, group by conversation
  2. Build a representative sample per conversation (first + last chunks)
  3. Send each sample to LLM for classification + insight extraction
  4. Filter noise, rank by signal quality
  5. Output insights.json + knowledge_distillation_report.md

Output categories:
  - IDEA:      Novel concept, feature proposal, design direction
  - DECISION:  Architectural choice, technology pick, trade-off resolution
  - PATTERN:   Reusable design pattern, workflow, integration approach
  - INSIGHT:   "Aha moment", realization, principle discovered
  - REFERENCE: Useful factual info worth keeping (config, setup, specs)
  - NOISE:     Routine troubleshooting, transient errors, chit-chat

Usage:
  cd ~/ai-stack
  venv/bin/python scripts/knowledge_distiller.py
  venv/bin/python scripts/knowledge_distiller.py --provider groq --max-conversations 50
  venv/bin/python scripts/knowledge_distiller.py --dry-run
  venv/bin/python scripts/knowledge_distiller.py --skip-evaluated
"""

import argparse
import json
import os
import sys
import time
import re
from datetime import datetime
from pathlib import Path
from collections import defaultdict

import chromadb
import requests

# ============================================================
# Configuration
# ============================================================

CHROMA_HOST = os.environ.get("CHROMA_HOST", "192.158.1.243")
CHROMA_PORT = int(os.environ.get("CHROMA_PORT", "8000"))
COLLECTION_NAME = os.environ.get("CHROMA_COLLECTION", "faithh_knowledge_base")

BASE_DIR = Path(__file__).parent.parent  # ~/ai-stack
OUTPUT_DIR = BASE_DIR / "ml" / "output"
INSIGHTS_FILE = OUTPUT_DIR / "insights.json"
REPORT_FILE = OUTPUT_DIR / "knowledge_distillation_report.md"

# LLM providers
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama31-faithh")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")

# Sampling config
SAMPLE_CHARS = 3000       # Max chars to send per conversation
MIN_CONVERSATION_CHUNKS = 3  # Skip tiny conversations


# ============================================================
# ChromaDB data pull
# ============================================================

def pull_and_group_conversations(host, port, collection_name, batch_size=5000):
    """Pull all chunks from ChromaDB and group by conversation."""
    print(f"📡 Connecting to ChromaDB at {host}:{port}...")

    client = chromadb.HttpClient(host=host, port=port)
    collection = client.get_collection(collection_name)
    total = collection.count()
    print(f"   Collection '{collection_name}': {total:,} documents")

    # Pull all chunks
    all_docs = []
    all_metas = []
    for offset in range(0, total, batch_size):
        batch = collection.get(
            limit=batch_size,
            offset=offset,
            include=["documents", "metadatas"]
        )
        all_docs.extend(batch["documents"])
        all_metas.extend(batch["metadatas"])
        print(f"   Pulled {min(offset + batch_size, total):,}/{total:,}")

    # Group by conversation_id (fall back to source)
    conversations = defaultdict(lambda: {"chunks": [], "meta": None})
    for doc, meta in zip(all_docs, all_metas):
        if not doc or not doc.strip():
            continue
        meta = meta or {}
        cid = meta.get("conversation_id") or meta.get("source", "unknown")
        conversations[cid]["chunks"].append(doc.strip())
        if conversations[cid]["meta"] is None:
            conversations[cid]["meta"] = meta

    # Skip project_docs (already authoritative)
    filtered = {}
    skipped_docs = 0
    for cid, data in conversations.items():
        cat = (data["meta"] or {}).get("category", "")
        src = (data["meta"] or {}).get("source", "")
        if cat == "project_docs" or src.startswith("project_docs:"):
            skipped_docs += 1
            continue
        filtered[cid] = data

    print(f"✅ {len(filtered)} conversations ({skipped_docs} project_docs skipped)")
    return filtered


def build_sample(conversation_data, max_chars=SAMPLE_CHARS):
    """Build a representative text sample from a conversation's chunks."""
    chunks = conversation_data["chunks"]
    meta = conversation_data["meta"] or {}
    title = meta.get("title", meta.get("source", "Untitled"))

    # Take first chunk (sets context) + last chunks (conclusions/decisions)
    if len(chunks) <= 3:
        sample_text = "\n---\n".join(chunks)
    else:
        # First 2 chunks + middle sample + last 2 chunks
        first = chunks[:2]
        middle_idx = len(chunks) // 2
        middle = [chunks[middle_idx]]
        last = chunks[-2:]
        sample_text = "\n---\n".join(first + middle + last)

    # Truncate to max_chars
    if len(sample_text) > max_chars:
        sample_text = sample_text[:max_chars] + "\n[...truncated...]"

    return title, sample_text, len(chunks)


# ============================================================
# LLM evaluation
# ============================================================

EVAL_PROMPT = """You are a strict knowledge curator for the FAITHH project. Your job is to separate GOLD from NOISE. Be harsh — most conversations are NOT documentation-worthy.

PROJECT CONTEXT:
- FAITHH = "Friendly AI That's Teaching, Helping, and a Hub" — an AI assistant with RAG, multi-provider LLM routing, chip-based semantic routing, and a self-monitoring PULSE system
- Harmony Framework = a biomechanical resonance model (head/feet/hands modules, phase flips, yin/yang flows) that maps to AI architecture concepts
- Constella = a civic governance framework (Astris, Auctor, etc.) developed alongside FAITHH
- Tom Cat Sound LLC = the user's audio business
- The user builds things across AI, audio engineering, biomechanics, and civic governance

CONVERSATION TITLE: {title}
CHUNK COUNT: {chunk_count}
---
{sample}
---

Evaluate this conversation STRICTLY. Respond in EXACTLY this JSON format (no markdown, no extra text):
{{
  "category": "<pick exactly ONE: IDEA, DECISION, PATTERN, INSIGHT, REFERENCE, or NOISE>",
  "signal_score": 1-5,
  "documentation_worthy": true/false,
  "title": "short descriptive title",
  "summary": "2-3 sentence summary of the key content",
  "actionable_items": ["specific actionable items, if any"],
  "keywords": ["relevant", "keywords"],
  "faithh_relevant": true/false,
  "domain": "faithh|harmony|constella|business|personal|technical|other"
}}

STRICT SCORING RUBRIC:
  5 = Breakthrough: Novel framework concept, major architectural decision, or original idea that changes project direction. RARE — at most 5% of conversations deserve this.
  4 = High value: Reusable design pattern, important technical decision with rationale, or significant insight worth preserving in documentation.
  3 = Moderate: Useful reference info, implementation details worth noting, or minor insights. Not documentation-worthy on its own.
  2 = Low value: Routine setup, configuration, product research, or troubleshooting that got resolved. Common knowledge.
  1 = Noise: Generic chat, product shopping/comparisons, transient errors, curiosity questions with textbook answers, billing issues.

CATEGORY GUIDE:
- IDEA: Novel concept or feature proposal that doesn't exist yet (e.g., "what if FAITHH designed its own UI based on chip patterns")
- DECISION: Architectural choice WITH rationale (e.g., "chose ChromaDB over Pinecone because X")
- PATTERN: Reusable design pattern or workflow (e.g., "two-tier RAG query with source boosting")
- INSIGHT: Original realization or "aha moment" (e.g., "fascial load can be modeled as a transfer function")
- REFERENCE: Factual info worth keeping (hardware inventory, model benchmarks, business structure)
- NOISE: Everything else. Product comparisons, shopping, routine troubleshooting, general curiosity, generic advice.

NOISE EXAMPLES (score 1-2):
- Comparing MacBook docks or finish nailers = NOISE (score 1)
- "How does gravity work?" with textbook answer = NOISE (score 1)
- iPhone feature comparisons or phone migration steps = NOISE (score 2)
- Fixing a Python import error = NOISE (score 1)
- Car insurance or used car shopping = NOISE (score 1)
- Generic security advice like "use strong passwords" = NOISE (score 2)

documentation_worthy: true ONLY if score >= 4 AND this contains an original idea, architectural decision, or framework insight that should become a permanent document. Most conversations are NOT — routine implementation, product research, and troubleshooting are NEVER doc-worthy even if useful.
faithh_relevant: true ONLY if directly about FAITHH code, architecture, or design philosophy.
domain: pick the SINGLE most relevant domain from: faithh, harmony, constella, business, personal, technical, other.

CRITICAL: Pick exactly ONE category. Do NOT combine them with pipes or slashes. Pick the BEST fit."""


def evaluate_with_ollama(title, sample, chunk_count):
    """Evaluate a conversation using local Ollama LLM."""
    prompt = EVAL_PROMPT.format(title=title, sample=sample, chunk_count=chunk_count)
    # Larger models (32B+) need more time and tokens for reasoning
    is_large = any(tag in OLLAMA_MODEL for tag in ["32b", "70b", "14b", "deepseek"])
    timeout = 180 if is_large else 60
    num_predict = 2000 if is_large else 500
    try:
        r = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.1, "num_predict": num_predict}
            },
            timeout=timeout
        )
        r.raise_for_status()
        return _parse_llm_response(r.json().get("response", ""))
    except Exception as e:
        return {"error": str(e)}


def evaluate_with_groq(title, sample, chunk_count, max_retries=3):
    """Evaluate a conversation using Groq API with retry + backoff."""
    prompt = EVAL_PROMPT.format(title=title, sample=sample, chunk_count=chunk_count)
    for attempt in range(max_retries):
        try:
            r = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": GROQ_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1,
                    "max_tokens": 500
                },
                timeout=30
            )
            if r.status_code == 429:
                wait = min(2 ** (attempt + 1), 30)  # 2s, 4s, 8s...
                time.sleep(wait)
                continue
            r.raise_for_status()
            content = r.json()["choices"][0]["message"]["content"]
            return _parse_llm_response(content)
        except requests.exceptions.HTTPError as e:
            if "429" in str(e) and attempt < max_retries - 1:
                time.sleep(min(2 ** (attempt + 1), 30))
                continue
            return {"error": str(e)}
        except Exception as e:
            return {"error": str(e)}
    return {"error": "Max retries exceeded (rate limited)"}


def _parse_llm_response(text):
    """Parse LLM JSON response, handling common formatting issues."""
    text = text.strip()

    # Strip <think>...</think> blocks from reasoning models (e.g., deepseek-r1)
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()

    # Strip markdown code fences if present
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)

    # Try direct JSON parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try to find JSON object in text
    match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    return {"error": f"Failed to parse LLM response", "raw": text[:200]}


def _normalize_result(result):
    """Post-process LLM result to fix common issues like compound categories."""
    if "error" in result:
        return result

    # Fix compound categories (e.g., "IDEA|DECISION" -> take first)
    cat = result.get("category", "NOISE")
    if "|" in cat or "/" in cat:
        parts = [p.strip() for p in cat.replace("/", "|").split("|")]
        valid = [p for p in parts if p in ("IDEA", "DECISION", "PATTERN", "INSIGHT", "REFERENCE", "NOISE")]
        result["category"] = valid[0] if valid else "NOISE"

    # Normalize domain (allow compound, just clean up)
    domain = result.get("domain", "other")
    if "|" in domain:
        result["domain"] = domain.split("|")[0].strip()

    # Ensure signal_score is int
    try:
        result["signal_score"] = int(result.get("signal_score", 1))
    except (ValueError, TypeError):
        result["signal_score"] = 1

    # Enforce doc-worthy only for score >= 4 and non-noise
    if result.get("signal_score", 1) < 4 or result.get("category") == "NOISE":
        result["documentation_worthy"] = False

    return result


# ============================================================
# Report generation
# ============================================================

def generate_report(all_results, insights, stats, elapsed):
    """Generate the knowledge distillation markdown report.
    
    Args:
        all_results: ALL evaluated items (including noise)
        insights: Only the items that passed the signal filter
        stats: Pipeline statistics dict
        elapsed: Duration in seconds
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Group ALL results by category (for stats)
    by_category = defaultdict(list)
    for ins in all_results:
        by_category[ins.get("category", "NOISE")].append(ins)

    # Group insights by domain
    by_domain = defaultdict(list)
    for ins in insights:
        by_domain[ins.get("domain", "other")].append(ins)

    # Documentation-worthy items
    doc_worthy = [i for i in insights if i.get("documentation_worthy")]
    doc_worthy.sort(key=lambda x: x.get("signal_score", 0), reverse=True)

    lines = [
        "# FAITHH Knowledge Distillation Report",
        f"**Generated:** {now}  ",
        f"**Duration:** {elapsed:.0f}s  ",
        f"**Conversations Analyzed:** {stats['total_evaluated']}  ",
        f"**Documentation-Worthy:** {len(doc_worthy)}  ",
        f"**Total Insights (score ≥ {stats.get('min_signal', 3)}):** {len(insights)}  ",
        f"**Noise Filtered:** {stats['noise_count']}  ",
        "",
        "## Score Distribution",
        "",
        "| Category | Count | Avg Score | Doc-Worthy | FAITHH |",
        "|----------|-------|-----------|------------|--------|",
    ]

    category_order = ["IDEA", "DECISION", "PATTERN", "INSIGHT", "REFERENCE", "NOISE"]
    for cat in category_order:
        items = by_category.get(cat, [])
        if not items:
            continue
        avg = sum(i.get("signal_score", 0) for i in items) / len(items)
        dw = sum(1 for i in items if i.get("documentation_worthy"))
        faithh_count = sum(1 for i in items if i.get("faithh_relevant"))
        lines.append(f"| {cat} | {len(items)} | {avg:.1f} | {dw} | {faithh_count} |")

    # Domain breakdown
    if by_domain:
        lines.extend(["", "## Domain Breakdown", ""])
        domain_labels = {
            "faithh": "🤖 FAITHH", "harmony": "🎵 Harmony Framework",
            "constella": "🏛️ Constella", "business": "💼 Business",
            "personal": "👤 Personal", "technical": "⚙️ Technical", "other": "📦 Other"
        }
        for domain in ["faithh", "harmony", "constella", "business", "technical", "personal", "other"]:
            items = by_domain.get(domain, [])
            if items:
                label = domain_labels.get(domain, domain)
                lines.append(f"- **{label}:** {len(items)} insights")

    # === DOCUMENTATION-WORTHY (the main section) ===
    if doc_worthy:
        lines.extend([
            "",
            "---",
            "",
            "## 🏆 Documentation-Worthy Insights",
            "",
            "*These conversations contain insights valuable enough to become permanent project documentation.*",
            "",
        ])
        for i, ins in enumerate(doc_worthy, 1):
            domain_tag = ins.get("domain", "other").upper()
            lines.append(f"### {i}. {ins.get('title', 'Untitled')} [{ins['category']}] ⭐{ins.get('signal_score', 0)} `{domain_tag}`")
            lines.append(f"**Source:** {ins.get('original_title', 'Unknown')}  ")
            lines.append(f"**Chunks:** {ins.get('chunk_count', 0)}  ")
            lines.append("")
            lines.append(ins.get("summary", "No summary available."))
            lines.append("")
            actions = ins.get("actionable_items", [])
            if actions:
                lines.append("**Actionable Items:**")
                for a in actions:
                    lines.append(f"- {a}")
                lines.append("")
            kw = ins.get("keywords", [])
            if kw:
                lines.append(f"**Keywords:** {', '.join(kw)}")
                lines.append("")

    # === CATEGORY SUMMARIES (compact) ===
    for cat_key, cat_label, cat_emoji in [
        ("IDEA", "Ideas", "💡"), ("DECISION", "Decisions", "⚖️"),
        ("PATTERN", "Patterns", "🔧"), ("INSIGHT", "Insights", "🧠"),
        ("REFERENCE", "References", "📚"),
    ]:
        cat_items = [i for i in insights if i.get("category") == cat_key and not i.get("documentation_worthy")]
        if cat_items:
            lines.extend(["", f"## {cat_emoji} {cat_label} (Notable, not doc-worthy)", ""])
            for ins in cat_items[:20]:
                score = ins.get("signal_score", 0)
                domain = ins.get("domain", "")
                lines.append(f"- **{ins.get('title', 'Untitled')}** (⭐{score}, {domain}) — {ins.get('summary', '')[:150]}")

    # === NOISE SUMMARY ===
    noise_items = by_category.get("NOISE", [])
    if noise_items:
        lines.extend([
            "",
            "## �️ Filtered Noise (not included in insights)",
            "",
            f"*{len(noise_items)} conversations classified as noise.*",
            "",
        ])
        for ins in noise_items[:15]:
            score = ins.get("signal_score", 0)
            lines.append(f"- ⭐{score} {ins.get('title', 'Untitled')[:80]}")
        if len(noise_items) > 15:
            lines.append(f"- *...and {len(noise_items) - 15} more*")

    # Stats
    lines.extend([
        "",
        "---",
        "",
        "## 📊 Pipeline Statistics",
        "",
        f"- Total conversations in ChromaDB: {stats['total_conversations']}",
        f"- Conversations evaluated: {stats['total_evaluated']}",
        f"- Skipped (too small): {stats['skipped_small']}",
        f"- Documentation-worthy: {len(doc_worthy)}",
        f"- Insights (score ≥ {stats.get('min_signal', 3)}): {len(insights)}",
        f"- Noise filtered: {stats['noise_count']}",
        f"- LLM errors: {stats['error_count']}",
        f"- LLM provider: {stats['provider']}",
        f"- Duration: {elapsed:.0f}s",
    ])

    return "\n".join(lines)


# ============================================================
# Main pipeline
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="FAITHH Knowledge Distiller")
    parser.add_argument("--provider", choices=["ollama", "groq"], default="groq",
                        help="LLM provider (default: groq)")
    parser.add_argument("--model", type=str, default=None,
                        help="Override LLM model name (e.g., deepseek-r1:32b for Ollama)")
    parser.add_argument("--max-conversations", type=int, default=0,
                        help="Max conversations to evaluate (0=all)")
    parser.add_argument("--min-chunks", type=int, default=MIN_CONVERSATION_CHUNKS,
                        help=f"Min chunks per conversation (default: {MIN_CONVERSATION_CHUNKS})")
    parser.add_argument("--min-signal", type=int, default=3,
                        help="Min signal score to include in report (default: 3)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Pull data and show stats without LLM evaluation")
    parser.add_argument("--skip-evaluated", action="store_true",
                        help="Skip conversations already in insights.json")
    args = parser.parse_args()

    # Apply model override
    global OLLAMA_MODEL, GROQ_MODEL
    if args.model:
        if args.provider == "ollama":
            OLLAMA_MODEL = args.model
        else:
            GROQ_MODEL = args.model

    # Validate provider
    if args.provider == "groq" and not GROQ_API_KEY:
        print("⚠️  GROQ_API_KEY not set. Falling back to ollama.")
        args.provider = "ollama"

    if args.provider == "ollama":
        try:
            r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
            models = [m["name"] for m in r.json().get("models", [])]
            if OLLAMA_MODEL not in models and f"{OLLAMA_MODEL}:latest" not in models:
                print(f"⚠️  Model '{OLLAMA_MODEL}' not found in Ollama. Available: {models}")
                sys.exit(1)
        except Exception as e:
            print(f"❌ Cannot reach Ollama at {OLLAMA_URL}: {e}")
            sys.exit(1)

    evaluate_fn = evaluate_with_groq if args.provider == "groq" else evaluate_with_ollama

    print("=" * 60)
    print("FAITHH KNOWLEDGE DISTILLER")
    print("=" * 60)
    print(f"Provider: {args.provider} ({GROQ_MODEL if args.provider == 'groq' else OLLAMA_MODEL})")

    start_time = time.time()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Step 1: Pull and group conversations
    print("\n📦 Step 1: Pull conversation data from ChromaDB")
    conversations = pull_and_group_conversations(CHROMA_HOST, CHROMA_PORT, COLLECTION_NAME)

    # Filter by min chunk count
    eligible = {
        cid: data for cid, data in conversations.items()
        if len(data["chunks"]) >= args.min_chunks
    }
    skipped_small = len(conversations) - len(eligible)
    print(f"   Eligible: {len(eligible)} (skipped {skipped_small} with < {args.min_chunks} chunks)")

    # Load existing insights if --skip-evaluated
    existing_ids = set()
    if args.skip_evaluated and INSIGHTS_FILE.exists():
        try:
            existing = json.loads(INSIGHTS_FILE.read_text())
            existing_ids = {i.get("conversation_id") for i in existing.get("insights", [])}
            print(f"   Skipping {len(existing_ids)} already-evaluated conversations")
        except Exception:
            pass

    if args.dry_run:
        print(f"\n📊 Dry run summary:")
        print(f"   Conversations to evaluate: {len(eligible) - len(existing_ids)}")
        # Show size distribution
        sizes = sorted([len(d["chunks"]) for d in eligible.values()], reverse=True)
        print(f"   Chunk distribution: max={sizes[0]}, median={sizes[len(sizes)//2]}, min={sizes[-1]}")
        # Show source breakdown
        platforms = defaultdict(int)
        for data in eligible.values():
            plat = (data["meta"] or {}).get("platform", "unknown")
            platforms[plat] += 1
        print(f"   Platforms: {dict(platforms)}")
        # Estimate time
        n = len(eligible) - len(existing_ids)
        est_sec = n * (1.0 if args.provider == "groq" else 3.0)
        print(f"   Estimated time ({args.provider}): ~{est_sec/60:.0f} minutes")
        return

    # Step 2: Evaluate each conversation
    print(f"\n🧠 Step 2: Evaluating {len(eligible) - len(existing_ids)} conversations...")
    all_results = []  # ALL evaluated items (including noise)
    insights = []     # Only items passing the signal filter
    error_count = 0
    noise_count = 0

    to_evaluate = [
        (cid, data) for cid, data in eligible.items()
        if cid not in existing_ids
    ]

    if args.max_conversations > 0:
        to_evaluate = to_evaluate[:args.max_conversations]

    for i, (cid, data) in enumerate(to_evaluate, 1):
        title, sample, chunk_count = build_sample(data)

        if i % 10 == 0 or i == 1:
            elapsed_so_far = time.time() - start_time
            rate = i / max(elapsed_so_far, 1)
            remaining = (len(to_evaluate) - i) / max(rate, 0.01)
            print(f"   [{i}/{len(to_evaluate)}] ~{remaining:.0f}s remaining...")

        result = _normalize_result(evaluate_fn(title, sample, chunk_count))

        if "error" in result:
            error_count += 1
            if error_count <= 3:
                print(f"   ⚠️  Error on '{title[:50]}': {result['error'][:80]}")
            if error_count == 3:
                print(f"   (suppressing further error messages)")
            continue

        # Enrich with metadata
        result["conversation_id"] = cid
        result["original_title"] = title
        result["chunk_count"] = chunk_count
        result["platform"] = (data["meta"] or {}).get("platform", "unknown")
        result["timestamp"] = (data["meta"] or {}).get("timestamp", "")
        result["evaluated_at"] = datetime.now().isoformat()

        all_results.append(result)

        cat = result.get("category", "NOISE")
        score = result.get("signal_score", 1)

        if cat == "NOISE" or score < args.min_signal:
            noise_count += 1
        else:
            insights.append(result)

        # Rate limit for Groq (free tier is strict)
        if args.provider == "groq":
            time.sleep(2.0)

    elapsed = time.time() - start_time

    # Sort by signal score
    insights.sort(key=lambda x: x.get("signal_score", 0), reverse=True)
    all_results.sort(key=lambda x: x.get("signal_score", 0), reverse=True)

    print(f"\n✅ Evaluation complete: {len(insights)} insights, {noise_count} noise, {error_count} errors")

    doc_worthy = [i for i in insights if i.get("documentation_worthy")]
    print(f"   Documentation-worthy: {len(doc_worthy)}")

    # Step 3: Save outputs
    print("\n💾 Step 3: Save outputs")

    output = {
        "version": "2.0",
        "generated": datetime.now().isoformat(),
        "pipeline": {
            "provider": args.provider,
            "model": GROQ_MODEL if args.provider == "groq" else OLLAMA_MODEL,
            "conversations_evaluated": len(to_evaluate),
            "insights_extracted": len(insights),
            "documentation_worthy": len(doc_worthy),
            "noise_filtered": noise_count,
            "errors": error_count,
            "min_signal": args.min_signal,
            "elapsed_seconds": round(elapsed, 1),
        },
        "insights": insights,
        "noise": [r for r in all_results if r.get("category") == "NOISE" or r.get("signal_score", 1) < args.min_signal],
    }

    with open(INSIGHTS_FILE, "w") as f:
        json.dump(output, f, indent=2)
    print(f"   📄 Insights: {INSIGHTS_FILE}")

    stats = {
        "total_conversations": len(conversations),
        "total_evaluated": len(to_evaluate),
        "skipped_small": skipped_small,
        "total_insights": len(insights),
        "noise_count": noise_count,
        "error_count": error_count,
        "min_signal": args.min_signal,
        "provider": f"{args.provider} ({GROQ_MODEL if args.provider == 'groq' else OLLAMA_MODEL})",
    }

    report = generate_report(all_results, insights, stats, elapsed)
    with open(REPORT_FILE, "w") as f:
        f.write(report)
    print(f"   📋 Report: {REPORT_FILE}")

    # Summary
    print(f"\n{'=' * 60}")
    print(f"✅ KNOWLEDGE DISTILLATION COMPLETE")
    print(f"{'=' * 60}")
    print(f"   Conversations evaluated: {len(to_evaluate)}")
    print(f"   Documentation-worthy: {len(doc_worthy)}")
    print(f"   Insights (score ≥ {args.min_signal}): {len(insights)}")
    print(f"   Noise filtered: {noise_count}")
    print(f"   Duration: {elapsed:.0f}s")

    if doc_worthy:
        print(f"\n   🏆 Documentation-Worthy:")
        for ins in doc_worthy[:10]:
            domain = ins.get("domain", "?")
            print(f"     ⭐{ins.get('signal_score',0)} [{ins['category']}/{domain}] {ins.get('title', 'Untitled')}")

    print(f"\n   Review: {REPORT_FILE}")
    print(f"   Data:   {INSIGHTS_FILE}")


if __name__ == "__main__":
    main()
