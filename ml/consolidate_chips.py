#!/usr/bin/env python3
"""
Chip Consolidation & Centroid Computation
==========================================
Takes 422 micro-topics from BERTopic and consolidates into ~30-40 macro-chips
with computed centroids for semantic routing.

Steps:
  1. Load micro-chips from chips.json
  2. Pull embeddings from ChromaDB for centroid computation
  3. Group micro-topics into macro-chips via keyword/category rules
  4. Compute centroid embedding per macro-chip
  5. Output consolidated_chips.json for FAITHH backend

Usage:
  ml/venv/bin/python ml/consolidate_chips.py
"""

import json
import os
import re
import sys
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path

# GPU DISABLED for Proxmox VM environment
# os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
# os.environ["CUDA_VISIBLE_DEVICES"] = "1"
os.environ["CUDA_VISIBLE_DEVICES"] = ""  # Force CPU-only

import numpy as np
import chromadb
from sentence_transformers import SentenceTransformer

# ============================================================
# Configuration
# ============================================================

CHROMA_HOST = os.environ.get("CHROMA_HOST", "192.158.1.10")
CHROMA_PORT = int(os.environ.get("CHROMA_PORT", "8000"))
COLLECTION_NAME = "faithh_knowledge_base_v2"

BASE_DIR = Path(__file__).parent.parent
CHIPS_FILE = BASE_DIR / "ml" / "output" / "chips.json"
OUTPUT_FILE = BASE_DIR / "ml" / "output" / "consolidated_chips.json"
REPORT_FILE = BASE_DIR / "ml" / "output" / "consolidation_report.md"

EMBEDDING_MODEL = os.environ.get("FAITHH_EMBEDDER_MODEL", "BAAI/bge-base-en-v1.5")

# ============================================================
# Macro-chip definitions (keyword-based grouping rules)
# ============================================================

MACRO_CHIPS = {
    "faithh_core": {
        "label": "FAITHH Core System",
        "description": "FAITHH backend, chip system, PULSE, memory architecture",
        "match_keywords": ["robocopy", "mir", "backup_parallel", "dryrun", "resonance", "resonant", "earth", "energy", "ilo", "iso", "spp", "boot", "usb", "fgsjson", "floating_gardens_soundworks", "reverb", "wav", "llc", "cpa", "synology", "macvlan", "pi hole", "traefik", "8080", "llama_cpp", "cuda", "torch", "pytorch", "binaries", "5557", "backend", "faithh_professional_backend_fixed", "jonat ai", "ubuntu bash", 
            "faithh", "pulse", "chip", "backend", "rag", "memory", "scaffold",
            "context", "session", "awareness", "stars", "journal", "rating",
            "resonance", "level", "tier", "compass", "orientation",
            "faithh_professional_backend", "faithh_professional_backend_fixed", "5557", "integration", "intent", "jonat ai", "ubuntu bash",
        ],
        "match_categories": ["faithh"],
    },
    "constella_governance": {
        "label": "Constella Framework",
        "description": "Civic governance, Astris/Auctor tokens, Celestial Equilibrium",
        "match_keywords": [
            "constella", "astris", "auctor", "civic", "celestial", "equilibrium",
            "governance", "penumbra", "vault", "genesis", "doctrine", "harmony",
            "ucf", "resonance gap", "eden", "consensus", "review v1", "merit", "omf", "bounty", "fund",
        ],
        "match_categories": ["constella"],
    },
    "infrastructure_docker": {
        "label": "Infrastructure & Docker",
        "description": "Docker, containers, networking, proxmox, VM infrastructure",
        "match_keywords": ["docker", "pihole", "traefik", "container", "volume1", "compose", "synology", "macvlan", "pi hole", "8080"],
        "match_categories": ["infrastructure"],
    },
    "hardware_setup": {
        "label": "Hardware & System Config",
        "description": "CPU, GPU, BIOS, boot, USB, hardware configuration",
        "match_keywords": [
            "mhz", "voltage", "cpu", "bios", "dram", "gpu", "vram",
            "1080", "3090", "rtx", "boot", "usb", "iso", "ilo", "spp",
            "thunderbolt", "dock", "cable", "owc", "nvme", "pcie", "ilo", "iso", "spp",
        ],
    },
    "audio_business": {
        "label": "Audio & Music Business",
        "description": "Tom Cat Sound, audio gear, reverb, music business, LLC",
        "match_keywords": ["operational_pillars", "tax", "cpa", "inventory", "fgs", "floating_gardens", "soundworks", "wav", "reverb"],
        "match_categories": ["audio"],
    },
    "llm_ai_tools": {
        "label": "LLM & AI Tools",
        "description": "LLM models, AI tools, Groq, Anthropic, Ollama, vLLM, fine-tuning",
        "match_keywords": ["llama", "ollama", "groq", "gemini", "provider", "model", "cuda", "torch", "pytorch", "llama_cpp", "cpp"],
    },
    "chromadb_indexing": {
        "label": "ChromaDB & RAG Indexing",
        "description": "ChromaDB, embeddings, conversation indexing, search",
        "match_keywords": [
            "chromadb", "collection", "embedding", "indexing", "conversations",
            "exports", "grok", "claude", "chunks", "reindex", "jsonl",
            "inbox", "create_time", "chatgpt", "chat gpt", "get_message_dict", "schema org", "json schema", "content type", "type application",
        ],
    },
    "coding_dotnet": {
        "label": "Desktop App Development",
        "description": ".NET/WPF/XAML development, FAITHH Desktop app",
        "match_keywords": [
            "xaml", "cs", "csproj", "dotnet", "wpf", "stackpanel",
            "staticresource", "setter", "grid", "mainwindow",
            "resourcedictionary", "faithh desktop", "border", "rgba",
        ],
    },
    "coding_powershell": {
        "label": "PowerShell & Windows Scripts",
        "description": "PowerShell scripts, scheduled tasks, backup, robocopy",
        "match_keywords": [
            "robocopy", "mt", "scheduledtask", "taskname", "ps1", "dryrun",
            "backup", "logfile", "add content", "shortcut", "ico",
            "publish", "env userprofile",
        ],
    },
    "server_gen8": {
        "label": "Gen8 Server & Homelab",
        "description": "Gen8 MicroServer, iLO, server deployment, monitoring",
        "match_keywords": [
            "gen8", "ilo", "spp", "microserver", "xeon", "ecc",
            "tailscale", "ssh", "service", "systemctl",
        ],
    },
    "file_management": {
        "label": "File Management & Backup",
        "description": "File operations, backup, rsync, robocopy, storage management",
        "match_keywords": ["archive", "canonical", "cleanup", "migrate", "tar", "robocopy", "mir", "mt", "backup_parallel"],
    },
    "personal_health": {
        "label": "Health & Wellness",
        "description": "Physical health, jaw/tension, body awareness",
        "match_keywords": [
            "tongue", "jaw", "tension", "neck", "cranial", "feet",
            "head", "diagram", "body", "muscle", "stretch",
        ],
    },
    "philosophy_universe": {
        "label": "Philosophy & Universe",
        "description": "Philosophy, universe, consciousness, identity, meaning",
        "match_keywords": ["universe", "earth", "energy", "sun", "consciousness", "resonance", "resonant"],
    },
    "git_version_control": {
        "label": "Git & Version Control",
        "description": "Git operations, GitHub, PRs, branch management",
        "match_keywords": [
            "pr", "gh", "merge", "branch", "protection", "git",
            "commit", "push", "gitea",
        ],
    },
    "networking_security": {
        "label": "Networking & Security",
        "description": "Network config, ports, firewall, connectivity",
        "match_keywords": [
            "port", "netconnection", "firewall", "ssl", "certificate", "vlan", "vlans", "authenticator", "bitwarden", "tcp6", "listen",
            "ssh", "proxy", "tunnel", "socket",
        ],
    },
}


def load_micro_chips():
    """Load micro-chip definitions from BERTopic output."""
    with open(CHIPS_FILE) as f:
        data = json.load(f)
    return data["chips"], data["pipeline"]


def assign_macro_chip(micro_chip):
    """
    Assign a micro-chip to a macro-chip based on keyword matching.
    Returns (macro_chip_id, confidence_score).
    """
    best_match = None
    best_score = 0

    micro_keywords = set(k.lower() for k in micro_chip.get("keywords", []))
    micro_cats = set(micro_chip.get("categories", {}).keys())
    micro_name = micro_chip.get("name", "").lower()

    for macro_id, macro_def in MACRO_CHIPS.items():
        score = 0
        match_kw = set(k.lower() for k in macro_def.get("match_keywords", []))
        match_cats = set(macro_def.get("match_categories", []))

        # Keyword overlap (check both keywords list and chip name)
        for mk in match_kw:
            if any(mk in kw for kw in micro_keywords):
                score += 2
            if mk in micro_name:
                score += 1

        # Category overlap
        if match_cats & micro_cats:
            score += 3

        if score > best_score:
            best_score = score
            best_match = macro_id

    return best_match, best_score


def consolidate(micro_chips):
    """Assign all micro-chips to macro-chips."""
    assignments = defaultdict(list)
    unassigned = []

    for chip in micro_chips:
        macro_id, score = assign_macro_chip(chip)
        if macro_id and score >= 2:
            assignments[macro_id].append(chip)
        else:
            unassigned.append(chip)

    return assignments, unassigned


def compute_centroids(assignments, embedding_model):
    """Compute centroid embedding for each macro-chip using representative keywords."""
    centroids = {}

    for macro_id, micro_chips in assignments.items():
        # Collect all unique keywords from constituent micro-chips
        all_keywords = []
        for chip in micro_chips:
            all_keywords.extend(chip.get("keywords", [])[:5])

        # Also include the macro-chip description
        macro_def = MACRO_CHIPS[macro_id]
        text_for_centroid = macro_def["description"] + ". " + ", ".join(set(all_keywords))

        # Embed the combined text
        embedding = embedding_model.encode(text_for_centroid, normalize_embeddings=True)
        centroids[macro_id] = embedding.tolist()

    return centroids


def build_consolidated_output(assignments, unassigned, centroids, pipeline_info):
    """Build final consolidated chips JSON."""
    consolidated = []

    for macro_id, micro_chips in assignments.items():
        macro_def = MACRO_CHIPS[macro_id]
        total_docs = sum(c["doc_count"] for c in micro_chips)

        # Merge categories across micro-chips
        merged_cats = defaultdict(int)
        for chip in micro_chips:
            for cat, count in chip.get("categories", {}).items():
                merged_cats[cat] += count

        # Collect all keywords, ranked by frequency
        keyword_freq = defaultdict(float)
        for chip in micro_chips:
            for kw, score in chip.get("keyword_scores", {}).items():
                keyword_freq[kw] += score * chip["doc_count"]

        top_keywords = sorted(keyword_freq.items(), key=lambda x: -x[1])[:15]

        # Get best representative excerpts (from largest micro-chips)
        sorted_micros = sorted(micro_chips, key=lambda c: -c["doc_count"])
        excerpts = []
        for mc in sorted_micros[:3]:
            excerpts.extend(mc.get("representative_excerpts", [])[:1])

        chip_def = {
            "id": macro_id,
            "label": macro_def["label"],
            "description": macro_def["description"],
            "doc_count": total_docs,
            "micro_topic_count": len(micro_chips),
            "categories": dict(merged_cats),
            "top_keywords": [kw for kw, _ in top_keywords],
            "keyword_scores": {kw: round(score, 4) for kw, score in top_keywords},
            "activation_keywords": [kw for kw, _ in top_keywords[:8]],
            "centroid": centroids.get(macro_id, []),
            "representative_excerpts": excerpts[:3],
            "micro_topic_ids": [c["topic_id"] for c in micro_chips],
        }
        consolidated.append(chip_def)

    # Sort by doc count
    consolidated.sort(key=lambda c: -c["doc_count"])
    for i, chip in enumerate(consolidated):
        chip["rank"] = i + 1

    return consolidated


def generate_report(consolidated, unassigned, micro_chips, elapsed):
    """Generate consolidation report."""
    total_assigned = sum(c["doc_count"] for c in consolidated)
    total_unassigned_docs = sum(c["doc_count"] for c in unassigned)
    total_micro = len(micro_chips)
    assigned_micro = total_micro - len(unassigned)

    lines = [
        "# Chip Consolidation Report",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ",
        f"**Duration:** {elapsed:.1f}s  ",
        f"**Input:** {total_micro} micro-topics  ",
        f"**Output:** {len(consolidated)} macro-chips  ",
        f"**Assigned:** {assigned_micro} micro-topics ({total_assigned:,} docs)  ",
        f"**Unassigned:** {len(unassigned)} micro-topics ({total_unassigned_docs:,} docs)  ",
        "",
        "## Macro-Chips",
        "",
        "| Rank | Chip | Docs | Micro-Topics | Top Keywords |",
        "|------|------|------|-------------|-------------|",
    ]

    for chip in consolidated:
        kw = ", ".join(chip["top_keywords"][:5])
        lines.append(
            f"| {chip['rank']} | **{chip['label']}** | {chip['doc_count']:,} | "
            f"{chip['micro_topic_count']} | {kw} |"
        )

    lines.extend([
        "",
        "## Unassigned Micro-Topics (Top 20)",
        "",
        "| Topic ID | Name | Docs | Keywords |",
        "|----------|------|------|----------|",
    ])

    for chip in sorted(unassigned, key=lambda c: -c["doc_count"])[:20]:
        kw = ", ".join(chip["keywords"][:4])
        lines.append(f"| {chip['topic_id']} | {chip['name']} | {chip['doc_count']} | {kw} |")

    lines.extend([
        "",
        "## Integration",
        "",
        "Each macro-chip has a centroid embedding (768-dim) for semantic routing:",
        "1. When a query arrives, embed it with all-MiniLM-L6-v2",
        "2. Compute cosine similarity against each chip centroid",
        "3. Activate chips above threshold (e.g., > 0.35)",
        "4. Inject activated chip's context into the LLM prompt",
    ])

    return "\n".join(lines)


def main():
    print("=" * 60)
    print("CHIP CONSOLIDATION & CENTROID COMPUTATION")
    print("=" * 60)

    start_time = time.time()
    Path(OUTPUT_FILE).parent.mkdir(parents=True, exist_ok=True)

    # Step 1: Load micro-chips
    print("\n📦 Step 1: Load micro-chip definitions")
    micro_chips, pipeline_info = load_micro_chips()
    print(f"   Loaded {len(micro_chips)} micro-chips")

    # Step 2: Consolidate
    print("\n🔬 Step 2: Assign micro-chips to macro-chips")
    assignments, unassigned = consolidate(micro_chips)
    print(f"   Macro-chips with assignments: {len(assignments)}")
    assigned_count = sum(len(v) for v in assignments.values())
    print(f"   Micro-chips assigned: {assigned_count}")
    print(f"   Micro-chips unassigned: {len(unassigned)}")

    for macro_id, chips in sorted(assignments.items(), key=lambda x: -sum(c["doc_count"] for c in x[1])):
        total = sum(c["doc_count"] for c in chips)
        print(f"     {macro_id:25s}: {len(chips):3d} micro-topics, {total:5d} docs")

    # Step 3: Compute centroids
    print("\n🧠 Step 3: Compute centroid embeddings")
    model = SentenceTransformer(EMBEDDING_MODEL, device="cpu")
    centroids = compute_centroids(assignments, model)
    print(f"   Computed {len(centroids)} centroids (768-dim each)")

    # Step 4: Build output
    print("\n💾 Step 4: Build consolidated output")
    consolidated = build_consolidated_output(assignments, unassigned, centroids, pipeline_info)

    output_data = {
        "version": "1.0",
        "generated": datetime.now().isoformat(),
        "embedding_model": EMBEDDING_MODEL,
        "embedding_dim": 768,
        "macro_chip_count": len(consolidated),
        "total_docs_covered": sum(c["doc_count"] for c in consolidated),
        "unassigned_micro_topics": len(unassigned),
        "chips": consolidated,
    }

    with open(OUTPUT_FILE, "w") as f:
        json.dump(output_data, f, indent=2)
    print(f"   📄 {OUTPUT_FILE}")

    elapsed = time.time() - start_time
    report = generate_report(consolidated, unassigned, micro_chips, elapsed)
    with open(REPORT_FILE, "w") as f:
        f.write(report)
    print(f"   📋 {REPORT_FILE}")

    # Summary
    print(f"\n{'=' * 60}")
    print(f"✅ CONSOLIDATION COMPLETE")
    print(f"{'=' * 60}")
    print(f"   {len(consolidated)} macro-chips with centroids")
    for chip in consolidated[:10]:
        print(f"     {chip['rank']:2d}. {chip['label']:30s} ({chip['doc_count']:,} docs, {chip['micro_topic_count']} sub-topics)")
    print(f"\n   Duration: {elapsed:.1f}s")


if __name__ == "__main__":
    main()
