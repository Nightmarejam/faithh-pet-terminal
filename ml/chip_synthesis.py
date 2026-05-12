#!/usr/bin/env python3
"""
FAITHH Chip Synthesis Pipeline
================================
Auto-discovers topic chips from conversation history using BERTopic.

Input:  ChromaDB collection (32,499 chunks from 306 conversations)
Output: chips.json — topic chip definitions for FAITHH semantic routing

Architecture:
  1. Pull chunks from ChromaDB
  2. Embed with sentence-transformers (GPU-accelerated)
  3. Reduce dimensions with UMAP
  4. Cluster with HDBSCAN
  5. Extract topic labels with BERTopic
  6. Export chip definitions

Usage:
  cd ~/ai-stack
  ml/venv/bin/python ml/chip_synthesis.py
  ml/venv/bin/python ml/chip_synthesis.py --min-topic-size 30
  ml/venv/bin/python ml/chip_synthesis.py --visualize
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# Target RTX 3090 (GPU 1) — GTX 1080 Ti (GPU 0) lacks sm_70+ support
os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"] = "1"

import numpy as np
import chromadb
from sentence_transformers import SentenceTransformer
from bertopic import BERTopic
from umap import UMAP
from hdbscan import HDBSCAN
from sklearn.feature_extraction.text import CountVectorizer

# ============================================================
# Configuration
# ============================================================

CHROMA_HOST = os.environ.get("CHROMA_HOST", "192.158.1.243")
CHROMA_PORT = int(os.environ.get("CHROMA_PORT", "8000"))
COLLECTION_NAME = os.environ.get("CHROMA_COLLECTION", "faithh_knowledge_base")

# Output paths
BASE_DIR = Path(__file__).parent.parent  # ~/ai-stack
OUTPUT_DIR = BASE_DIR / "ml" / "output"
CHIPS_FILE = OUTPUT_DIR / "chips.json"
REPORT_FILE = OUTPUT_DIR / "synthesis_report.md"

# Model config
EMBEDDING_MODEL = "BAAI/bge-base-en-v1.5"  # Match ChromaDB collection (768-dim)
DEVICE = "cpu"  # CPU-only (Proxmox VM, no GPU passthrough)


def pull_chunks(host, port, collection_name, batch_size=5000):
    """Pull all chunks from ChromaDB."""
    print(f"📡 Connecting to ChromaDB at {host}:{port}...")
    
    client = chromadb.HttpClient(host=host, port=port)
    heartbeat = client.heartbeat()
    print(f"   Heartbeat: {heartbeat}")
    
    collection = client.get_collection(collection_name)
    total = collection.count()
    print(f"   Collection '{collection_name}': {total:,} documents")
    
    all_docs = []
    all_metas = []
    all_ids = []
    
    for offset in range(0, total, batch_size):
        batch = collection.get(
            limit=batch_size,
            offset=offset,
            include=["documents", "metadatas"]
        )
        all_docs.extend(batch["documents"])
        all_metas.extend(batch["metadatas"])
        all_ids.extend(batch["ids"])
        print(f"   Pulled {min(offset + batch_size, total):,}/{total:,} chunks")
    
    print(f"✅ Pulled {len(all_docs):,} chunks total")
    return all_docs, all_metas, all_ids


def filter_chunks(docs, metas, ids, min_length=50):
    """Filter out very short or empty chunks."""
    filtered_docs = []
    filtered_metas = []
    filtered_ids = []
    
    for doc, meta, doc_id in zip(docs, metas, ids):
        if doc and len(doc.strip()) >= min_length:
            filtered_docs.append(doc.strip())
            filtered_metas.append(meta)
            filtered_ids.append(doc_id)
    
    removed = len(docs) - len(filtered_docs)
    print(f"🔧 Filtered: {len(filtered_docs):,} kept, {removed:,} removed (< {min_length} chars)")
    return filtered_docs, filtered_metas, filtered_ids


def build_topic_model(min_topic_size=20, n_neighbors=15, n_components=5, random_state=42):
    """Build BERTopic model with configured components."""
    
    # UMAP for dimensionality reduction
    umap_model = UMAP(
        n_neighbors=n_neighbors,
        n_components=n_components,
        min_dist=0.0,
        metric="cosine",
        random_state=random_state,
    )
    
    # HDBSCAN for clustering
    hdbscan_model = HDBSCAN(
        min_cluster_size=min_topic_size,
        min_samples=5,
        metric="euclidean",
        prediction_data=True,
    )
    
    # Vectorizer for topic representation
    vectorizer = CountVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        min_df=3,
        max_df=0.95,
    )
    
    # Embedding model (same as ChromaDB for consistency)
    embedding_model = SentenceTransformer(EMBEDDING_MODEL, device=DEVICE)
    
    topic_model = BERTopic(
        embedding_model=embedding_model,
        umap_model=umap_model,
        hdbscan_model=hdbscan_model,
        vectorizer_model=vectorizer,
        top_n_words=10,
        verbose=True,
        calculate_probabilities=False,  # Faster
    )
    
    return topic_model, embedding_model


def synthesize_chips(topic_model, docs, metas, ids, topics):
    """Convert BERTopic topics into FAITHH chip definitions."""
    
    topic_info = topic_model.get_topic_info()
    chips = []
    
    for _, row in topic_info.iterrows():
        topic_id = row["Topic"]
        if topic_id == -1:  # Skip outlier topic
            continue
        
        count = row["Count"]
        name = row["Name"]
        
        # Get top words for this topic
        topic_words = topic_model.get_topic(topic_id)
        keywords = [word for word, score in topic_words[:10]]
        keyword_scores = {word: round(float(score), 4) for word, score in topic_words[:10]}
        
        # Get representative docs
        repr_docs = topic_model.get_representative_docs(topic_id)
        
        # Analyze metadata for this topic's docs
        topic_indices = [i for i, t in enumerate(topics) if t == topic_id]
        topic_metas = [metas[i] for i in topic_indices]
        
        # Count categories
        categories = {}
        for m in topic_metas:
            cat = m.get("category", "unknown") if m else "unknown"
            categories[cat] = categories.get(cat, 0) + 1
        
        # Build chip definition
        chip = {
            "id": f"topic_{topic_id:03d}",
            "topic_id": topic_id,
            "name": _clean_topic_name(keywords[:3]),
            "bertopic_name": name,
            "keywords": keywords,
            "keyword_scores": keyword_scores,
            "doc_count": count,
            "categories": categories,
            "representative_excerpts": [d[:300] for d in (repr_docs or [])[:3]],
            "activation_keywords": keywords[:5],  # Top 5 for semantic routing
        }
        chips.append(chip)
    
    # Sort by doc count (most prominent topics first)
    chips.sort(key=lambda c: c["doc_count"], reverse=True)
    
    # Add rank
    for i, chip in enumerate(chips):
        chip["rank"] = i + 1
    
    return chips


def _clean_topic_name(top_words):
    """Create a human-readable chip name from top keywords."""
    # Join top 3 words, title case
    name = " / ".join(w.replace("_", " ").title() for w in top_words[:3])
    return name


def generate_report(chips, topic_model, docs, topics, elapsed_seconds):
    """Generate a Markdown report of the synthesis results."""
    
    total_docs = len(docs)
    outlier_count = sum(1 for t in topics if t == -1)
    clustered_count = total_docs - outlier_count
    
    lines = [
        "# Chip Synthesis Report",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ",
        f"**Pipeline Duration:** {elapsed_seconds:.1f}s  ",
        f"**Documents Processed:** {total_docs:,}  ",
        f"**Clustered:** {clustered_count:,} ({clustered_count/total_docs*100:.1f}%)  ",
        f"**Outliers:** {outlier_count:,} ({outlier_count/total_docs*100:.1f}%)  ",
        f"**Topics Discovered:** {len(chips)}  ",
        "",
        "## Discovered Chips",
        "",
        "| Rank | Chip Name | Docs | Top Keywords |",
        "|------|-----------|------|-------------|",
    ]
    
    for chip in chips[:30]:  # Top 30
        kw = ", ".join(chip["keywords"][:5])
        lines.append(f"| {chip['rank']} | {chip['name']} | {chip['doc_count']} | {kw} |")
    
    if len(chips) > 30:
        lines.append(f"| ... | *{len(chips) - 30} more topics* | | |")
    
    lines.extend([
        "",
        "## Integration Notes",
        "",
        "These chips can be loaded by FAITHH for semantic routing:",
        "- Place `chips.json` in `~/ai-stack/ml/output/`",
        "- Backend reads chip definitions at startup",
        "- Query embeddings are compared against chip centroids",
        "- Matching chips inject their representative context",
        "",
        "## Next Steps",
        "",
        "- [ ] Review chips for quality — merge or split as needed",
        "- [ ] Compute chip centroids for semantic routing",
        "- [ ] Integrate chip activation into FAITHH backend",
        "- [ ] Set up periodic re-synthesis as new conversations are indexed",
    ])
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="FAITHH Chip Synthesis Pipeline")
    parser.add_argument("--min-topic-size", type=int, default=20,
                        help="Minimum docs per topic (default: 20)")
    parser.add_argument("--min-chunk-length", type=int, default=50,
                        help="Minimum chunk character length (default: 50)")
    parser.add_argument("--n-neighbors", type=int, default=15,
                        help="UMAP n_neighbors (default: 15)")
    parser.add_argument("--n-components", type=int, default=5,
                        help="UMAP dimensions (default: 5)")
    parser.add_argument("--visualize", action="store_true",
                        help="Generate topic visualization HTML")
    parser.add_argument("--dry-run", action="store_true",
                        help="Pull data and show stats without running ML")
    args = parser.parse_args()
    
    print("=" * 60)
    print("FAITHH CHIP SYNTHESIS PIPELINE")
    print("=" * 60)
    
    start_time = time.time()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Step 1: Pull data from ChromaDB
    print("\n📦 Step 1: Pull conversation chunks from ChromaDB")
    docs, metas, ids = pull_chunks(CHROMA_HOST, CHROMA_PORT, COLLECTION_NAME)
    
    # Step 2: Filter
    print("\n🔧 Step 2: Filter chunks")
    docs, metas, ids = filter_chunks(docs, metas, ids, min_length=args.min_chunk_length)
    
    if args.dry_run:
        print(f"\n📊 Dry run complete. {len(docs):,} docs ready for synthesis.")
        # Show category breakdown
        cats = {}
        for m in metas:
            cat = m.get("category", "unknown") if m else "unknown"
            cats[cat] = cats.get(cat, 0) + 1
        print("\nCategory breakdown:")
        for cat, count in sorted(cats.items(), key=lambda x: -x[1]):
            print(f"  {cat}: {count:,}")
        return
    
    # Step 3: Build and fit topic model
    print(f"\n🧠 Step 3: Running BERTopic (min_topic_size={args.min_topic_size})")
    print(f"   Embedding model: {EMBEDDING_MODEL} on {DEVICE}")
    print(f"   UMAP: n_neighbors={args.n_neighbors}, n_components={args.n_components}")
    
    topic_model, embedding_model = build_topic_model(
        min_topic_size=args.min_topic_size,
        n_neighbors=args.n_neighbors,
        n_components=args.n_components,
    )
    
    topics, probs = topic_model.fit_transform(docs)
    
    topic_info = topic_model.get_topic_info()
    n_topics = len(topic_info) - 1  # Exclude outlier topic -1
    outlier_count = sum(1 for t in topics if t == -1)
    
    print(f"\n✅ Discovered {n_topics} topics")
    print(f"   Clustered: {len(docs) - outlier_count:,} docs")
    print(f"   Outliers:  {outlier_count:,} docs")
    
    # Step 4: Synthesize chips
    print("\n🔬 Step 4: Synthesize chip definitions")
    chips = synthesize_chips(topic_model, docs, metas, ids, topics)
    print(f"   Generated {len(chips)} chip definitions")
    
    # Step 5: Save outputs
    print("\n💾 Step 5: Save outputs")
    
    chip_output = {
        "version": "1.0",
        "generated": datetime.now().isoformat(),
        "pipeline": {
            "embedding_model": EMBEDDING_MODEL,
            "min_topic_size": args.min_topic_size,
            "n_neighbors": args.n_neighbors,
            "n_components": args.n_components,
            "input_docs": len(docs),
            "topics_discovered": n_topics,
            "outlier_count": outlier_count,
        },
        "chips": chips,
    }
    
    with open(CHIPS_FILE, "w") as f:
        json.dump(chip_output, f, indent=2)
    print(f"   📄 Chips: {CHIPS_FILE}")
    
    elapsed = time.time() - start_time
    report = generate_report(chips, topic_model, docs, topics, elapsed)
    with open(REPORT_FILE, "w") as f:
        f.write(report)
    print(f"   📋 Report: {REPORT_FILE}")
    
    # Optional visualization
    if args.visualize:
        try:
            viz_file = OUTPUT_DIR / "topic_visualization.html"
            fig = topic_model.visualize_topics()
            fig.write_html(str(viz_file))
            print(f"   📊 Visualization: {viz_file}")
        except Exception as e:
            print(f"   ⚠️ Visualization failed: {e}")
    
    # Step 6: Summary
    print(f"\n{'=' * 60}")
    print(f"✅ CHIP SYNTHESIS COMPLETE")
    print(f"{'=' * 60}")
    print(f"   Topics: {n_topics}")
    print(f"   Duration: {elapsed:.1f}s")
    print(f"   Top 5 chips:")
    for chip in chips[:5]:
        print(f"     {chip['rank']}. {chip['name']} ({chip['doc_count']} docs)")
    print(f"\n   Next: Review chips.json, then integrate into FAITHH backend")


if __name__ == "__main__":
    main()
