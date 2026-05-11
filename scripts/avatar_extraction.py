#!/usr/bin/env python3
"""
FAITHH User Avatar Extraction — ML Personality Profiling
=========================================================
Analyzes conversation history to build a user personality profile:
  - Communication style (tone, vocabulary, sentence patterns)
  - Interest clusters (weighted by frequency and recency)
  - Decision-making patterns (from decisions_log.json)
  - Time-of-day activity patterns
  - Emotional markers and energy levels

Input:  ChromaDB conversation chunks + decisions_log.json + scaffolding_state.json
Output: ml/output/user_avatar.json — personality profile for FAITHH context injection

Usage:
  python scripts/avatar_extraction.py
  python scripts/avatar_extraction.py --json
  python scripts/avatar_extraction.py --output avatar_report
"""

import argparse
import json
import os
import re
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

import chromadb
import numpy as np
from sentence_transformers import SentenceTransformer

# ============================================================
# Configuration
# ============================================================

BASE_DIR = Path(__file__).parent.parent  # ~/ai-stack
OUTPUT_DIR = BASE_DIR / "ml" / "output"
AVATAR_FILE = OUTPUT_DIR / "user_avatar.json"
REPORT_FILE = OUTPUT_DIR / "avatar_report.md"
DECISIONS_LOG = BASE_DIR / "decisions_log.json"
SCAFFOLDING = BASE_DIR / "scaffolding_state.json"
MEMORY_FILE = BASE_DIR / "faithh_memory.json"

CHROMA_HOST = os.environ.get("CHROMA_HOST", "192.158.1.243")
CHROMA_PORT = int(os.environ.get("CHROMA_PORT", "8000"))
COLLECTION_NAME = os.environ.get("CHROMA_COLLECTION", "faithh_knowledge_base")

EMBEDDING_MODEL = "all-MiniLM-L6-v2"
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama31-faithh:latest")


# ============================================================
# Data Pulling
# ============================================================

def pull_user_chunks(host, port, collection_name, batch_size=5000):
    """Pull conversation chunks from ChromaDB, focusing on user messages."""
    print(f"📡 Connecting to ChromaDB at {host}:{port}...")

    client = chromadb.HttpClient(host=host, port=port)
    client.heartbeat()

    collection = client.get_collection(collection_name)
    total = collection.count()
    print(f"   Collection '{collection_name}': {total:,} documents")

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
        print(f"   Pulled {min(offset + batch_size, total):,}/{total:,} chunks")

    print(f"✅ Pulled {len(all_docs):,} chunks total")
    return all_docs, all_metas


def extract_user_messages(docs, metas):
    """Extract chunks that are likely user-authored content."""
    user_chunks = []
    for doc, meta in zip(docs, metas):
        if not doc or len(doc.strip()) < 30:
            continue
        source = meta.get("source", "").lower() if meta else ""
        # Conversation exports typically contain user messages
        # Filter for conversational content (not pure code or docs)
        if any(kw in source for kw in ["chat", "export", "conversation", "claude", "chatgpt"]):
            user_chunks.append({"text": doc.strip(), "meta": meta or {}})
        # Also include chunks from decision logs, scaffolding — user-authored
        elif any(kw in source for kw in ["decision", "scaffolding", "memory"]):
            user_chunks.append({"text": doc.strip(), "meta": meta or {}})

    print(f"🔍 Extracted {len(user_chunks):,} user-relevant chunks")
    return user_chunks


# ============================================================
# Analysis Functions
# ============================================================

def analyze_vocabulary(chunks, top_n=100):
    """Analyze vocabulary patterns from user chunks."""
    # Common stopwords to exclude
    stopwords = set(
        "the a an is are was were be been being have has had do does did will "
        "would could should may might shall can need dare to of in for on with "
        "at by from as into through during before after above below between out "
        "up down about over again further then once here there when where why "
        "how all each every both few more most other some such no nor not only "
        "own same so than too very just don t s m re ve ll d it its he she they "
        "we you i me him her them us my your his their our this that these those "
        "what which who whom and but or if while because until although since "
        "also still already even though yet however like get got make made thing "
        "things really actually basically going go know think want said one two "
        "well much many way much right now new something anything".split()
    )

    word_freq = Counter()
    bigram_freq = Counter()
    sentence_lengths = []

    for chunk in chunks:
        text = chunk["text"].lower()
        # Clean text
        text = re.sub(r'[^a-z\s\'-]', ' ', text)
        words = [w for w in text.split() if len(w) > 2 and w not in stopwords]

        word_freq.update(words)

        # Bigrams
        for i in range(len(words) - 1):
            bigram_freq[f"{words[i]} {words[i+1]}"] += 1

        # Sentence lengths
        sentences = re.split(r'[.!?]+', chunk["text"])
        for s in sentences:
            wc = len(s.split())
            if 3 < wc < 100:
                sentence_lengths.append(wc)

    avg_sentence_len = np.mean(sentence_lengths) if sentence_lengths else 0
    std_sentence_len = np.std(sentence_lengths) if sentence_lengths else 0

    return {
        "top_words": dict(word_freq.most_common(top_n)),
        "top_bigrams": dict(bigram_freq.most_common(50)),
        "avg_sentence_length": round(float(avg_sentence_len), 1),
        "sentence_length_std": round(float(std_sentence_len), 1),
        "vocabulary_size": len(word_freq),
        "total_words": sum(word_freq.values()),
    }


def analyze_interests(chunks, embedder):
    """Cluster user interests using embeddings."""
    # Define interest probes — topics we want to detect affinity for
    interest_probes = {
        "software_engineering": "coding programming software development debugging APIs",
        "ai_ml": "artificial intelligence machine learning neural networks embeddings models",
        "infrastructure": "servers docker containers kubernetes deployment devops networking",
        "music_audio": "music audio recording production sound engineering mixing",
        "business": "business revenue taxes LLC partnerships financial planning",
        "philosophy": "philosophy consciousness meaning purpose existence ethics",
        "biology_nature": "biology nature ecology regenerative farming homesteading animals",
        "hardware": "hardware GPUs CPUs RAM NAS servers building computers",
        "security": "security encryption authentication access control privacy",
        "creative_design": "design UI UX visual creative art pixel retro gaming",
        "personal_growth": "learning growth discipline habits mindset productivity wellbeing",
        "systems_thinking": "systems architecture patterns integration modular design",
    }

    print("🧠 Analyzing interest clusters...")

    # Embed probes
    probe_texts = list(interest_probes.values())
    probe_labels = list(interest_probes.keys())
    probe_embeddings = embedder.encode(probe_texts, normalize_embeddings=True)

    # Sample chunks for efficiency (max 2000)
    sample = chunks[:2000] if len(chunks) > 2000 else chunks
    chunk_texts = [c["text"][:500] for c in sample]  # Truncate long chunks

    # Embed chunks in batches
    batch_size = 256
    all_scores = {label: [] for label in probe_labels}

    for i in range(0, len(chunk_texts), batch_size):
        batch = chunk_texts[i:i + batch_size]
        batch_embeddings = embedder.encode(batch, normalize_embeddings=True)

        # Cosine similarity against each probe
        similarities = np.dot(batch_embeddings, probe_embeddings.T)

        for j, label in enumerate(probe_labels):
            all_scores[label].extend(similarities[:, j].tolist())

    # Compute interest scores
    interest_scores = {}
    for label in probe_labels:
        scores = all_scores[label]
        # Use mean of top 5% as the affinity score (avoids noise from unrelated chunks)
        top_k = max(1, int(len(scores) * 0.05))
        sorted_scores = sorted(scores, reverse=True)[:top_k]
        interest_scores[label] = {
            "affinity": round(float(np.mean(sorted_scores)), 3),
            "peak": round(float(max(scores)), 3),
            "mentions_above_threshold": sum(1 for s in scores if s > 0.4),
        }

    # Sort by affinity
    ranked = sorted(interest_scores.items(), key=lambda x: x[1]["affinity"], reverse=True)
    return {label: data for label, data in ranked}


def analyze_communication_style(chunks):
    """Detect communication style markers."""
    total = len(chunks)
    if total == 0:
        return {}

    markers = {
        "uses_technical_jargon": 0,
        "uses_emojis": 0,
        "uses_markdown": 0,
        "asks_questions": 0,
        "gives_instructions": 0,
        "expresses_uncertainty": 0,
        "expresses_excitement": 0,
        "uses_analogies": 0,
        "references_prior_work": 0,
        "thinks_in_systems": 0,
    }

    patterns = {
        "uses_technical_jargon": r'\b(api|docker|gpu|cuda|llm|rag|embeddings?|chromadb|endpoint|backend|frontend|venv|systemd|cron)\b',
        "uses_emojis": r'[✅❌⚠️🚀💡🔍🧠📡🎯🔧💻🤖🌟]|:\)|:\(|<3',
        "uses_markdown": r'```|#{1,3}\s|\*\*.*\*\*|__.*__|`[^`]+`',
        "asks_questions": r'\?',
        "gives_instructions": r'\b(should|must|need to|let\'s|go ahead|make sure|set up|configure|create|build|implement)\b',
        "expresses_uncertainty": r'\b(maybe|perhaps|not sure|might|could be|possibly|wondering|hmm)\b',
        "expresses_excitement": r'\b(awesome|great|love|amazing|perfect|excellent|fantastic|incredible)\b|!{2,}',
        "uses_analogies": r'\b(like a|similar to|think of it as|imagine|metaphor|analogy|reminds me of)\b',
        "references_prior_work": r'\b(last session|previously|we already|earlier|before we|last time|remember when)\b',
        "thinks_in_systems": r'\b(architecture|pipeline|workflow|integration|modular|component|layer|tier|system)\b',
    }

    for chunk in chunks:
        text = chunk["text"]
        for marker, pattern in patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                markers[marker] += 1

    # Normalize to percentages
    style = {}
    for marker, count in markers.items():
        pct = round((count / total) * 100, 1)
        style[marker] = {"count": count, "pct": pct}

    return style


def analyze_time_patterns(metas):
    """Analyze time-of-day activity patterns from metadata timestamps."""
    hour_counts = Counter()
    day_counts = Counter()
    month_counts = Counter()

    for meta in metas:
        if not meta:
            continue
        # Try various timestamp fields
        ts = meta.get("timestamp") or meta.get("date") or meta.get("created_at", "")
        if not ts:
            continue
        try:
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            hour_counts[dt.hour] += 1
            day_counts[dt.strftime("%A")] += 1
            month_counts[dt.strftime("%Y-%m")] += 1
        except (ValueError, AttributeError):
            continue

    if not hour_counts:
        return {"note": "No timestamp data available in metadata"}

    peak_hour = hour_counts.most_common(1)[0] if hour_counts else (0, 0)
    peak_day = day_counts.most_common(1)[0] if day_counts else ("Unknown", 0)

    return {
        "peak_hour": peak_hour[0],
        "peak_day": peak_day[0],
        "hourly_distribution": dict(sorted(hour_counts.items())),
        "daily_distribution": dict(day_counts.most_common()),
        "monthly_activity": dict(sorted(month_counts.items())),
    }


def analyze_decision_patterns():
    """Analyze decision-making patterns from decisions_log.json."""
    if not DECISIONS_LOG.exists():
        return {"note": "decisions_log.json not found"}

    try:
        with open(DECISIONS_LOG) as f:
            data = json.load(f)
    except Exception as e:
        return {"error": str(e)}

    decisions = data.get("decisions", [])
    if not decisions:
        return {"note": "No decisions found"}

    # Analyze patterns
    categories = Counter()
    alternatives_count = []
    has_rationale = 0
    statuses = Counter()

    for d in decisions:
        categories[d.get("category", "uncategorized")] += 1
        alts = d.get("alternatives_considered", [])
        alternatives_count.append(len(alts))
        if d.get("rationale"):
            has_rationale += 1
        statuses[d.get("status", "unknown")] += 1

    return {
        "total_decisions": len(decisions),
        "categories": dict(categories.most_common()),
        "avg_alternatives_considered": round(float(np.mean(alternatives_count)), 1) if alternatives_count else 0,
        "rationale_rate": round(has_rationale / len(decisions) * 100, 1) if decisions else 0,
        "statuses": dict(statuses),
        "decision_thoroughness": "high" if np.mean(alternatives_count) >= 2 else "moderate" if np.mean(alternatives_count) >= 1 else "low",
    }


# ============================================================
# LLM Personality Synthesis
# ============================================================

def synthesize_personality(vocab, interests, style, decisions, model=None):
    """Use local LLM to synthesize a personality summary from the data."""
    import requests

    model = model or OLLAMA_MODEL

    # Build analysis context
    top_interests = list(interests.items())[:6]
    interest_str = "\n".join(f"  - {name}: affinity={data['affinity']}, peak={data['peak']}" for name, data in top_interests)

    top_style = sorted(style.items(), key=lambda x: x[1]["pct"], reverse=True)[:6]
    style_str = "\n".join(f"  - {name}: {data['pct']}% of chunks" for name, data in top_style)

    top_words = list(vocab.get("top_words", {}).items())[:20]
    words_str = ", ".join(f"{w}({c})" for w, c in top_words)

    prompt = f"""Analyze this user profile data and write a concise personality summary (3-4 paragraphs).
Focus on: who this person is, how they think, what drives them, and their communication style.
Write in third person. Be specific and insightful, not generic.

INTEREST CLUSTERS (ranked by affinity):
{interest_str}

COMMUNICATION STYLE:
{style_str}

VOCABULARY (top words): {words_str}
Average sentence length: {vocab.get('avg_sentence_length', 0)} words
Vocabulary size: {vocab.get('vocabulary_size', 0)} unique words

DECISION PATTERNS:
  Total decisions logged: {decisions.get('total_decisions', 0)}
  Avg alternatives considered: {decisions.get('avg_alternatives_considered', 0)}
  Thoroughness: {decisions.get('decision_thoroughness', 'unknown')}
  Top categories: {decisions.get('categories', {})}

Write the personality summary now:"""

    try:
        resp = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json={"model": model, "prompt": prompt, "stream": False,
                  "options": {"temperature": 0.7, "num_predict": 600}},
            timeout=120,
        )
        resp.raise_for_status()
        return resp.json().get("response", "").strip()
    except Exception as e:
        print(f"⚠️ LLM synthesis failed: {e}")
        return None


# ============================================================
# Output
# ============================================================

def build_avatar(vocab, interests, style, time_patterns, decisions, personality_summary):
    """Assemble the full user avatar profile."""
    avatar = {
        "meta": {
            "version": "1.0",
            "generated_at": datetime.now().isoformat(),
            "generator": "scripts/avatar_extraction.py",
            "chunks_analyzed": vocab.get("total_words", 0),
        },
        "personality_summary": personality_summary,
        "interests": interests,
        "communication_style": style,
        "vocabulary": {
            "avg_sentence_length": vocab.get("avg_sentence_length"),
            "sentence_length_std": vocab.get("sentence_length_std"),
            "vocabulary_size": vocab.get("vocabulary_size"),
            "top_words": dict(list(vocab.get("top_words", {}).items())[:30]),
            "top_bigrams": dict(list(vocab.get("top_bigrams", {}).items())[:20]),
        },
        "time_patterns": time_patterns,
        "decision_patterns": decisions,
    }
    return avatar


def generate_report(avatar):
    """Generate a markdown report."""
    lines = [
        "# FAITHH User Avatar Report",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
    ]

    if avatar.get("personality_summary"):
        lines.extend(["## Personality Summary", avatar["personality_summary"], ""])

    lines.append("## Interest Clusters (ranked)")
    for name, data in avatar.get("interests", {}).items():
        bar = "█" * int(data["affinity"] * 20)
        lines.append(f"- **{name}**: {data['affinity']:.3f} {bar}")
    lines.append("")

    lines.append("## Communication Style")
    for name, data in sorted(avatar.get("communication_style", {}).items(),
                              key=lambda x: x[1]["pct"], reverse=True):
        lines.append(f"- **{name}**: {data['pct']}% ({data['count']} chunks)")
    lines.append("")

    v = avatar.get("vocabulary", {})
    lines.extend([
        "## Vocabulary",
        f"- **Unique words:** {v.get('vocabulary_size', 0):,}",
        f"- **Avg sentence length:** {v.get('avg_sentence_length', 0)} words (±{v.get('sentence_length_std', 0)})",
        f"- **Top words:** {', '.join(list(v.get('top_words', {}).keys())[:15])}",
        "",
    ])

    d = avatar.get("decision_patterns", {})
    if d.get("total_decisions"):
        lines.extend([
            "## Decision Patterns",
            f"- **Total decisions:** {d['total_decisions']}",
            f"- **Avg alternatives considered:** {d.get('avg_alternatives_considered', 0)}",
            f"- **Thoroughness:** {d.get('decision_thoroughness', 'unknown')}",
            f"- **Categories:** {d.get('categories', {})}",
            "",
        ])

    return "\n".join(lines)


# ============================================================
# Main
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="FAITHH User Avatar Extraction")
    parser.add_argument("--json", action="store_true", help="Output JSON to stdout")
    parser.add_argument("--output", type=str, help="Output filename prefix (saved to ml/output/)")
    parser.add_argument("--skip-llm", action="store_true", help="Skip LLM personality synthesis")
    parser.add_argument("--model", type=str, default=OLLAMA_MODEL, help="Ollama model for synthesis")
    args = parser.parse_args()

    start = time.time()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Pull chunks
    docs, metas = pull_user_chunks(CHROMA_HOST, CHROMA_PORT, COLLECTION_NAME)

    # 2. Extract user-relevant chunks
    user_chunks = extract_user_messages(docs, metas)
    if len(user_chunks) < 10:
        print("⚠️ Very few user chunks found. Using all chunks for analysis.")
        user_chunks = [{"text": d, "meta": m or {}} for d, m in zip(docs, metas) if d and len(d) > 30]

    # 3. Load embedder
    print("🧠 Loading embedder...")
    embedder = SentenceTransformer(EMBEDDING_MODEL, device="cpu")

    # 4. Run analyses
    print("\n📊 Analyzing vocabulary...")
    vocab = analyze_vocabulary(user_chunks)
    print(f"   {vocab['vocabulary_size']:,} unique words, avg sentence: {vocab['avg_sentence_length']} words")

    print("📊 Analyzing interests...")
    interests = analyze_interests(user_chunks, embedder)
    top3 = list(interests.keys())[:3]
    print(f"   Top interests: {', '.join(top3)}")

    print("📊 Analyzing communication style...")
    style = analyze_communication_style(user_chunks)

    print("📊 Analyzing time patterns...")
    time_patterns = analyze_time_patterns([c.get("meta", {}) for c in user_chunks])

    print("📊 Analyzing decision patterns...")
    decisions = analyze_decision_patterns()

    # 5. LLM personality synthesis
    personality_summary = None
    if not args.skip_llm:
        print("\n🤖 Synthesizing personality with LLM...")
        personality_summary = synthesize_personality(vocab, interests, style, decisions, args.model)
        if personality_summary:
            print(f"   Generated {len(personality_summary)} char summary")
        else:
            print("   Skipped (LLM unavailable)")

    # 6. Build avatar
    avatar = build_avatar(vocab, interests, style, time_patterns, decisions, personality_summary)
    elapsed = round(time.time() - start, 1)
    avatar["meta"]["elapsed_seconds"] = elapsed

    # 7. Save outputs
    avatar_path = AVATAR_FILE
    report_path = REPORT_FILE

    if args.output:
        avatar_path = OUTPUT_DIR / f"{args.output}.json"
        report_path = OUTPUT_DIR / f"{args.output}.md"

    with open(avatar_path, "w") as f:
        json.dump(avatar, f, indent=2)
    print(f"\n💾 Avatar saved: {avatar_path.relative_to(BASE_DIR)}")

    report = generate_report(avatar)
    with open(report_path, "w") as f:
        f.write(report)
    print(f"💾 Report saved: {report_path.relative_to(BASE_DIR)}")

    if args.json:
        print(json.dumps(avatar, indent=2))
    else:
        print(f"\n⏱️  Completed in {elapsed}s")
        print(f"📊 Chunks analyzed: {len(user_chunks):,}")
        print(f"🧠 Top interests: {', '.join(top3)}")
        if personality_summary:
            print(f"\n--- Personality Summary ---\n{personality_summary[:500]}")

    return avatar


if __name__ == "__main__":
    main()
