#!/usr/bin/env python3
"""
FAITHH PULSE Reflection Engine — Tier 2: Decision Divergence Tracker
=====================================================================
Analyzes each decision in decisions_log.json against current project state
using a local LLM (Ollama) to detect:
  1. Decisions that have drifted from original intent
  2. Decisions whose rationale no longer holds
  3. Rejected alternatives that were actually implemented
  4. Decisions that should be revisited given new context

Uses RTX 3090 via Ollama for LLM inference.

Usage:
    python scripts/decision_divergence.py                  # Full analysis
    python scripts/decision_divergence.py --model llama31-faithh  # Specific model
    python scripts/decision_divergence.py --decision faithh_003   # Single decision
    python scripts/decision_divergence.py --output report  # Save to ml/output/
    python scripts/decision_divergence.py --json           # Machine-readable

Depends on: Ollama running (systemd service, port 11434)
Runtime: ~2-5 minutes for all decisions (depends on model)
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import requests
import chromadb

BASE_DIR = Path(__file__).parent.parent
VLLM_URL = os.environ.get("VLLM_URL", "http://localhost:8000")
CHROMA_HOST = os.environ.get("CHROMA_HOST", "192.158.1.10")
CHROMA_PORT = int(os.environ.get("CHROMA_PORT", "8000"))
COLLECTION_NAME = "faithh_knowledge_base"
DEFAULT_MODEL = "qwen2.5-14b-awq"


def load_decisions() -> list[dict]:
    """Load decisions from decisions_log.json."""
    path = BASE_DIR / "decisions_log.json"
    with open(path) as f:
        data = json.load(f)
    return data.get("decisions", [])


def load_project_state() -> dict:
    """Load current project state."""
    path = BASE_DIR / "project_states.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {}


def load_scaffolding() -> dict:
    """Load scaffolding state."""
    path = BASE_DIR / "scaffolding_state.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {}


def get_related_doc_content(related_docs: list[str], max_chars: int = 3000) -> str:
    """Read content from related docs."""
    content_parts = []
    for doc_path in related_docs:
        full_path = BASE_DIR / doc_path
        if full_path.exists():
            try:
                text = full_path.read_text(encoding="utf-8", errors="replace")
                # Truncate long docs
                if len(text) > 1500:
                    text = text[:1500] + "\n... [truncated]"
                content_parts.append(f"--- {doc_path} ---\n{text}")
            except Exception:
                content_parts.append(f"--- {doc_path} --- [read error]")
        else:
            content_parts.append(f"--- {doc_path} --- [FILE MISSING]")

    combined = "\n\n".join(content_parts)
    if len(combined) > max_chars:
        combined = combined[:max_chars] + "\n... [truncated]"
    return combined


def get_chromadb_context(decision_text: str, n_results: int = 5) -> str:
    """Get relevant context from ChromaDB for a decision."""
    try:
        client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
        collection = client.get_collection(COLLECTION_NAME)

        results = collection.query(
            query_texts=[decision_text],
            n_results=n_results,
            include=["documents", "metadatas"]
        )

        if results["documents"] and results["documents"][0]:
            chunks = []
            for i, doc in enumerate(results["documents"][0]):
                meta = results["metadatas"][0][i] if results["metadatas"] else {}
                source = meta.get("source", "unknown")
                chunks.append(f"[{source}]: {doc[:500]}")
            return "\n\n".join(chunks)
    except Exception as e:
        return f"[ChromaDB unavailable: {e}]"
    return "[No relevant context found]"


def build_analysis_prompt(decision: dict, project_state: dict,
                          scaffolding: dict, related_content: str,
                          rag_context: str) -> str:
    """Build the LLM prompt for decision analysis."""
    alternatives = decision.get("alternatives_considered", [])
    alt_text = "\n".join(
        f"  - {a['option']}: rejected because \"{a['rejected_because']}\""
        if isinstance(a, dict) else f"  - {a}"
        for a in alternatives
    ) if alternatives else "  (none recorded)"

    # Get current milestone for this project
    project = decision.get("project", "faithh")
    milestones = scaffolding.get("project_structural_milestones", {}).get(project, {})
    current_milestone = milestones.get("current", "unknown")
    next_milestone = milestones.get("next", "unknown")

    return f"""You are analyzing a past architectural decision for the FAITHH project system.
Your job is to determine if this decision is still valid, has drifted, or should be revisited.

DECISION ID: {decision.get('id', 'unknown')}
DECISION: {decision.get('decision', '')}
DATE MADE: {decision.get('date', 'unknown')}
PROJECT: {project}
CATEGORY: {decision.get('category', 'unknown')}
STATUS: {decision.get('status', 'unknown')}

ORIGINAL RATIONALE:
{decision.get('rationale', 'none recorded')}

ALTERNATIVES THAT WERE REJECTED:
{alt_text}

EXPECTED IMPACT:
{decision.get('impact', 'none recorded')}

CURRENT PROJECT MILESTONE: {current_milestone}
NEXT MILESTONE: {next_milestone}

RELATED DOCUMENTS (current content):
{related_content}

RECENT RELEVANT ACTIVITY FROM KNOWLEDGE BASE:
{rag_context}

Based on the above, answer these questions concisely:

1. ALIGNMENT (1-5 scale): Is the current system state consistent with this decision?
   1=completely contradicted, 3=partially drifted, 5=fully aligned

2. RATIONALE_VALID (yes/partially/no): Does the original rationale still hold?

3. ALTERNATIVES_CHECK: Were any rejected alternatives actually implemented or should they now be reconsidered?

4. STATUS: What is the true current status? (aligned/drifting/contradicted/obsolete/evolved)

5. RECOMMENDATION: One sentence — should this decision be reaffirmed, updated, or replaced?

Respond in this exact JSON format:
{{
  "alignment_score": <1-5>,
  "rationale_valid": "<yes|partially|no>",
  "alternatives_note": "<brief note or null>",
  "status": "<aligned|drifting|contradicted|obsolete|evolved>",
  "recommendation": "<one sentence>",
  "reasoning": "<2-3 sentence explanation>"
}}

Respond ONLY with the JSON object, no other text."""


def query_ollama(prompt: str, model: str, timeout: int = 120) -> str:
    """Query vLLM (OpenAI-compatible) instead of Ollama."""
    try:
        resp = requests.post(
            f"{VLLM_URL}/v1/chat/completions",
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
                "max_tokens": 500,
            },
            timeout=timeout,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
    except requests.exceptions.ConnectionError:
        return '{"error": "vLLM not running — check: ps aux | grep vllm"}'
    except requests.exceptions.Timeout:
        return '{"error": "vLLM timeout"}'

def parse_llm_response(raw: str) -> dict:
    """Parse the LLM's JSON response, handling common formatting issues."""
    # Try to extract JSON from the response
    raw = raw.strip()

    # Handle markdown code blocks
    if "```json" in raw:
        raw = raw.split("```json")[1].split("```")[0].strip()
    elif "```" in raw:
        raw = raw.split("```")[1].split("```")[0].strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Try to find JSON object in response
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start >= 0 and end > start:
            try:
                return json.loads(raw[start:end])
            except json.JSONDecodeError:
                pass

    return {
        "alignment_score": 0,
        "rationale_valid": "unknown",
        "alternatives_note": None,
        "status": "parse_error",
        "recommendation": "Could not parse LLM response",
        "reasoning": f"Raw response: {raw[:200]}",
    }


def format_report(results: list[dict], elapsed: float) -> str:
    """Format the divergence report as markdown."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        "# FAITHH Decision Divergence Report",
        f"**Generated:** {now}",
        f"**Analysis time:** {elapsed:.1f}s",
        f"**Decisions analyzed:** {len(results)}",
        "",
    ]

    # Summary
    status_counts = {}
    for r in results:
        s = r.get("analysis", {}).get("status", "unknown")
        status_counts[s] = status_counts.get(s, 0) + 1

    lines.append("## Summary")
    for status, count in sorted(status_counts.items()):
        icon = {"aligned": "✅", "drifting": "🟡", "contradicted": "🔴",
                "obsolete": "⚫", "evolved": "🔵"}.get(status, "❓")
        lines.append(f"- {icon} **{status}:** {count}")
    lines.append("")

    # Detail table
    lines.append("## Decision Analysis")
    lines.append("")

    for r in results:
        d = r["decision"]
        a = r.get("analysis", {})
        score = a.get("alignment_score", "?")
        status = a.get("status", "unknown")
        icon = {"aligned": "✅", "drifting": "🟡", "contradicted": "🔴",
                "obsolete": "⚫", "evolved": "🔵"}.get(status, "❓")

        lines.append(f"### {icon} {d['id']}: {d.get('decision', '')}")
        lines.append(f"- **Date:** {d.get('date', '?')} | **Project:** {d.get('project', '?')} | **Alignment:** {score}/5")
        lines.append(f"- **Status:** {status} | **Rationale valid:** {a.get('rationale_valid', '?')}")

        alt_note = a.get("alternatives_note")
        if alt_note and alt_note != "null" and alt_note.lower() != "none":
            lines.append(f"- **Alternatives note:** {alt_note}")

        lines.append(f"- **Recommendation:** {a.get('recommendation', 'N/A')}")
        lines.append(f"- **Reasoning:** {a.get('reasoning', 'N/A')}")
        lines.append("")

    # Action items
    action_items = [r for r in results
                    if r.get("analysis", {}).get("status") in ("drifting", "contradicted", "obsolete")]
    if action_items:
        lines.append("## Action Items")
        lines.append("")
        for r in action_items:
            d = r["decision"]
            a = r["analysis"]
            lines.append(f"- [ ] **{d['id']}** ({a['status']}): {a.get('recommendation', 'Review needed')}")
        lines.append("")

    lines.append("---")
    lines.append("*Generated by FAITHH PULSE Reflection Engine — Tier 2 Decision Divergence Tracker*")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="FAITHH Decision Divergence Tracker (Tier 2)")
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL,
                        help=f"Ollama model to use (default: {DEFAULT_MODEL})")
    parser.add_argument("--decision", type=str, default=None,
                        help="Analyze a single decision by ID")
    parser.add_argument("--json", action="store_true",
                        help="Output machine-readable JSON")
    parser.add_argument("--output", type=str, default=None,
                        help="Save report to ml/output/<name>.md")
    parser.add_argument("--timeout", type=int, default=120,
                        help="Timeout per LLM call in seconds (default: 120)")
    args = parser.parse_args()

    start = time.time()
    print("=" * 60)
    print("FAITHH PULSE Reflection Engine — Tier 2: Decision Divergence")
    print("=" * 60)

    # 1. Load data
    print("\n[1/4] Loading decisions and project state...")
    decisions = load_decisions()
    project_state = load_project_state()
    scaffolding = load_scaffolding()
    print(f"  {len(decisions)} decisions loaded")

    if args.decision:
        decisions = [d for d in decisions if d.get("id") == args.decision]
        if not decisions:
            print(f"  Error: Decision '{args.decision}' not found")
            sys.exit(1)
        print(f"  Filtering to: {args.decision}")

    # 2. Check Ollama connectivity
    print(f"\n[2/4] Checking vLLM ({args.model})...")
    try:
        resp = requests.get(f"{VLLM_URL}/v1/models", timeout=5)
        models = [m["name"] for m in resp.json().get("models", [])]
        if not any(args.model in m for m in models):
            print(f"  Warning: Model '{args.model}' not found. Available: {models}")
            print(f"  Will attempt anyway (Ollama may auto-pull)...")
        else:
            print(f"  Model '{args.model}' available")
    except Exception as e:
        print(f"  Error: Cannot reach Ollama at {OLLAMA_URL}: {e}")
        print("  vLLM not running — check tmux session")
        sys.exit(1)

    # 3. Connect to ChromaDB
    print("\n[3/4] Connecting to ChromaDB for context...")
    try:
        chroma_client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
        collection = chroma_client.get_collection(COLLECTION_NAME)
        print(f"  Collection: {COLLECTION_NAME} ({collection.count():,} docs)")
    except Exception as e:
        print(f"  Warning: ChromaDB unavailable ({e}), will skip RAG context")

    # 4. Analyze each decision
    print(f"\n[4/4] Analyzing {len(decisions)} decisions with {args.model}...")
    results = []

    for i, decision in enumerate(decisions):
        d_id = decision.get("id", "unknown")
        d_text = decision.get("decision", "")
        d_status = decision.get("status", "")
        
        # Skip superseded decisions - they're no longer active
        if d_status == "superseded" or "superseded" in d_status.lower():
            print(f"\n  [{i+1}/{len(decisions)}] {d_id}: SKIPPED (superseded by {decision.get('superseded_by', 'unknown')})")
            continue
            
        print(f"\n  [{i+1}/{len(decisions)}] {d_id}: {d_text[:60]}...")

        # Gather context
        related_docs = decision.get("related_docs", [])
        related_content = get_related_doc_content(related_docs)
        rag_context = get_chromadb_context(f"{d_text} {decision.get('rationale', '')}")

        # Build prompt
        prompt = build_analysis_prompt(decision, project_state, scaffolding,
                                       related_content, rag_context)

        # Query LLM
        t0 = time.time()
        raw_response = query_ollama(prompt, args.model, timeout=args.timeout)
        llm_time = time.time() - t0

        analysis = parse_llm_response(raw_response)
        status = analysis.get("status", "unknown")
        score = analysis.get("alignment_score", "?")
        icon = {"aligned": "✅", "drifting": "🟡", "contradicted": "🔴",
                "obsolete": "⚫", "evolved": "🔵"}.get(status, "❓")

        print(f"    {icon} {status} (alignment: {score}/5, {llm_time:.1f}s)")

        results.append({
            "decision": decision,
            "analysis": analysis,
            "llm_time_seconds": round(llm_time, 1),
        })

    elapsed = time.time() - start

    # Output
    if args.json:
        output = {
            "generated": datetime.now().isoformat(),
            "model": args.model,
            "analysis_time_seconds": round(elapsed, 1),
            "results": results,
        }
        print(json.dumps(output, indent=2))
    else:
        report = format_report(results, elapsed)
        print(f"\n{'=' * 60}")
        print(report)

        if args.output:
            output_path = BASE_DIR / "ml" / "output" / f"{args.output}.md"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(report)
            print(f"\nReport saved to: {output_path}")

    # Summary
    aligned = sum(1 for r in results if r["analysis"].get("status") == "aligned")
    drifting = sum(1 for r in results if r["analysis"].get("status") in ("drifting", "contradicted", "obsolete"))
    print(f"\n{'=' * 60}")
    print(f"Analysis complete in {elapsed:.1f}s")
    print(f"  {aligned} aligned, {drifting} need attention, {len(results) - aligned - drifting} other")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
