#!/usr/bin/env python3
"""
FAITHH PULSE Reflection Engine — Tier 3: Branch Explorer
==========================================================
Mines unexplored ideas from:
  1. Parked tangents in scaffolding_state.json
  2. Rejected alternatives in decisions_log.json
  3. Ideas mentioned in conversations but never acted on (via ChromaDB)
  4. Archived handoff docs with unfinished items

Uses local LLM (Ollama) to evaluate each idea against current state
and rank by potential value + feasibility.

Usage:
    python scripts/branch_explorer.py                    # Full exploration
    python scripts/branch_explorer.py --model llama31-faithh
    python scripts/branch_explorer.py --output branches  # Save to ml/output/
    python scripts/branch_explorer.py --json             # Machine-readable
    python scripts/branch_explorer.py --quick            # Skip LLM (data mining only)

Depends on: Ollama running (systemd service, port 11434)
Runtime: ~2-5 minutes for full analysis
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

import requests
import chromadb

BASE_DIR = Path(__file__).parent.parent
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
CHROMA_HOST = os.environ.get("CHROMA_HOST", "192.158.1.243")
CHROMA_PORT = int(os.environ.get("CHROMA_PORT", "8000"))
COLLECTION_NAME = "faithh_knowledge_base"
DEFAULT_MODEL = "llama31-faithh"


def load_json(filename: str) -> dict:
    """Load a JSON file from BASE_DIR."""
    path = BASE_DIR / filename
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {}


def extract_parked_tangents(scaffolding: dict) -> list[dict]:
    """Extract parked tangents from scaffolding state."""
    tangents = []
    for t in scaffolding.get("parked_tangents", []):
        tangents.append({
            "source": "scaffolding:parked_tangent",
            "idea": t.get("idea", ""),
            "noted": t.get("noted", ""),
            "why_parked": t.get("why_parked", ""),
            "revisit_when": t.get("revisit_when", ""),
            "details": t.get("details", ""),
        })
    return tangents


def extract_rejected_alternatives(decisions: list[dict]) -> list[dict]:
    """Extract rejected alternatives from decisions log."""
    alternatives = []
    for d in decisions:
        for alt in d.get("alternatives_considered", []):
            # Handle both dict and string formats
            if isinstance(alt, dict):
                alternatives.append({
                    "source": f"decision:{d.get('id', 'unknown')}",
                    "idea": alt.get("option", ""),
                    "original_decision": d.get("decision", ""),
                    "rejected_because": alt.get("rejected_because", ""),
                    "decision_date": d.get("date", ""),
                    "decision_status": d.get("status", ""),
                })
            elif isinstance(alt, str):
                alternatives.append({
                    "source": f"decision:{d.get('id', 'unknown')}",
                    "idea": alt,
                    "original_decision": d.get("decision", ""),
                    "rejected_because": "",
                    "decision_date": d.get("date", ""),
                    "decision_status": d.get("status", ""),
                })
    return alternatives


def extract_open_loops(scaffolding: dict) -> list[dict]:
    """Extract incomplete open loops."""
    loops = []
    for loop in scaffolding.get("open_loops", []):
        if loop.get("status") not in ("done", "completed", "solved"):
            loops.append({
                "source": f"scaffolding:open_loop:{loop.get('id', 'unknown')}",
                "idea": loop.get("item", ""),
                "why_structural": loop.get("why_structural", ""),
                "status": loop.get("status", ""),
                "blocked_by": loop.get("blocked_by"),
                "suggested_action": loop.get("suggested_action", ""),
                "created": loop.get("created", ""),
            })
    return loops


def mine_archived_ideas(archive_dir: Path, max_files: int = 20) -> list[dict]:
    """Scan archived handoffs for TODO/next-step items that were never completed."""
    ideas = []
    handoff_dir = archive_dir / "handoffs"
    if not handoff_dir.exists():
        return ideas

    # Patterns that suggest unfinished work
    patterns = [
        r'(?:TODO|NEXT|FUTURE|PLANNED|CONSIDER)[\s:]+(.+)',
        r'- \[ \]\s+(.+)',  # Unchecked checkboxes
        r'(?:should|could|might|want to)\s+(.{20,100})',
    ]

    files = sorted(handoff_dir.glob("*.md"))[:max_files]
    for f in files:
        try:
            content = f.read_text(encoding="utf-8", errors="replace")
            for pattern in patterns[:2]:  # Only use explicit TODO/checkbox patterns
                for match in re.finditer(pattern, content, re.IGNORECASE):
                    idea_text = match.group(1).strip()
                    if len(idea_text) > 15 and len(idea_text) < 200:
                        ideas.append({
                            "source": f"archive:{f.name}",
                            "idea": idea_text,
                            "file": str(f.relative_to(BASE_DIR)),
                        })
        except Exception:
            continue

    return ideas


def mine_chromadb_ideas(n_queries: int = 5) -> list[dict]:
    """Query ChromaDB for conversation topics about future plans/ideas."""
    ideas = []
    query_prompts = [
        "ideas for future development and improvements",
        "things we should explore or investigate later",
        "features planned but not yet built",
        "problems we identified but haven't solved",
        "interesting tangents worth revisiting",
    ]

    try:
        client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
        collection = client.get_collection(COLLECTION_NAME)

        for query in query_prompts[:n_queries]:
            results = collection.query(
                query_texts=[query],
                n_results=3,
                include=["documents", "metadatas"]
            )
            if results["documents"] and results["documents"][0]:
                for i, doc in enumerate(results["documents"][0]):
                    meta = results["metadatas"][0][i] if results["metadatas"] else {}
                    ideas.append({
                        "source": f"chromadb:{meta.get('source', 'conversation')}",
                        "idea": doc[:300],
                        "query_matched": query,
                    })
    except Exception as e:
        print(f"  Warning: ChromaDB unavailable ({e})")

    return ideas


def deduplicate_ideas(ideas: list[dict]) -> list[dict]:
    """Remove near-duplicate ideas based on text similarity."""
    if not ideas:
        return ideas

    seen_texts = set()
    unique = []
    for idea in ideas:
        text = idea.get("idea", "").lower().strip()
        # Simple dedup: skip if first 50 chars match something seen
        key = text[:50]
        if key not in seen_texts and len(text) > 10:
            seen_texts.add(key)
            unique.append(idea)

    return unique


def build_evaluation_prompt(idea: dict, project_state: dict, scaffolding: dict) -> str:
    """Build LLM prompt to evaluate an unexplored idea."""
    # Current milestones for context
    faithh_current = scaffolding.get("project_structural_milestones", {}).get("faithh", {})
    current = faithh_current.get("current", "unknown")
    next_ms = faithh_current.get("next", "unknown")

    source = idea.get("source", "unknown")
    idea_text = idea.get("idea", "")

    extra_context = ""
    if "rejected_because" in idea:
        extra_context = f"\nORIGINALLY REJECTED BECAUSE: {idea['rejected_because']}"
        extra_context += f"\nORIGINAL DECISION: {idea.get('original_decision', '')}"
        extra_context += f"\nDECISION DATE: {idea.get('decision_date', '')}"
    elif "why_parked" in idea:
        extra_context = f"\nWHY PARKED: {idea['why_parked']}"
        extra_context += f"\nREVISIT WHEN: {idea.get('revisit_when', '')}"
    elif "why_structural" in idea:
        extra_context = f"\nWHY STRUCTURAL: {idea['why_structural']}"
        extra_context += f"\nSTATUS: {idea.get('status', '')}"
        if idea.get("blocked_by"):
            extra_context += f"\nBLOCKED BY: {idea['blocked_by']}"

    return f"""You are evaluating an unexplored idea for the FAITHH project system.
FAITHH is a personal AI companion with RAG, ML chips, and a reflection engine.
Current milestone: {current}
Next milestone: {next_ms}

SOURCE: {source}
IDEA: {idea_text}
{extra_context}

Evaluate this idea:
1. RELEVANCE (1-5): How relevant is this to current project goals?
2. FEASIBILITY (1-5): How feasible with current hardware (RTX 3090, Ryzen 9, 47GB RAM)?
3. VALUE (1-5): How much value would this add if implemented?
4. TIMING: Is now the right time? (yes/not_yet/missed_window)
5. RECOMMENDATION: One sentence — explore, park, or discard?

Respond ONLY with this JSON:
{{
  "relevance": <1-5>,
  "feasibility": <1-5>,
  "value": <1-5>,
  "timing": "<yes|not_yet|missed_window>",
  "recommendation": "<one sentence>",
  "reasoning": "<1-2 sentences>"
}}"""


def query_ollama(prompt: str, model: str, timeout: int = 120) -> str:
    """Send prompt to Ollama and get response."""
    try:
        resp = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "num_predict": 400,
                }
            },
            timeout=timeout
        )
        resp.raise_for_status()
        return resp.json().get("response", "")
    except requests.exceptions.ConnectionError:
        return '{"error": "Ollama not running"}'
    except Exception as e:
        return f'{{"error": "{str(e)}"}}'


def parse_llm_response(raw: str) -> dict:
    """Parse the LLM's JSON response."""
    raw = raw.strip()
    if "```json" in raw:
        raw = raw.split("```json")[1].split("```")[0].strip()
    elif "```" in raw:
        raw = raw.split("```")[1].split("```")[0].strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start >= 0 and end > start:
            try:
                return json.loads(raw[start:end])
            except json.JSONDecodeError:
                pass
    return {
        "relevance": 0, "feasibility": 0, "value": 0,
        "timing": "unknown", "recommendation": "Parse error",
        "reasoning": f"Raw: {raw[:200]}",
    }


def format_report(evaluated: list[dict], raw_counts: dict, elapsed: float) -> str:
    """Format the branch exploration report."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines = [
        "# FAITHH Branch Exploration Report",
        f"**Generated:** {now}",
        f"**Analysis time:** {elapsed:.1f}s",
        "",
        "## Data Mining Summary",
        f"- **Parked tangents:** {raw_counts.get('parked', 0)}",
        f"- **Rejected alternatives:** {raw_counts.get('rejected', 0)}",
        f"- **Open loops:** {raw_counts.get('loops', 0)}",
        f"- **Archived TODOs:** {raw_counts.get('archived', 0)}",
        f"- **ChromaDB ideas:** {raw_counts.get('chromadb', 0)}",
        f"- **After dedup:** {raw_counts.get('deduped', 0)}",
        f"- **LLM-evaluated:** {len(evaluated)}",
        "",
    ]

    # Sort by composite score (relevance + feasibility + value)
    for item in evaluated:
        e = item.get("eval", {})
        item["_score"] = (e.get("relevance", 0) + e.get("feasibility", 0) + e.get("value", 0))

    evaluated.sort(key=lambda x: x["_score"], reverse=True)

    # Top recommendations
    explore_now = [e for e in evaluated if e.get("eval", {}).get("timing") == "yes"]
    park = [e for e in evaluated if e.get("eval", {}).get("timing") == "not_yet"]
    discard = [e for e in evaluated if e.get("eval", {}).get("timing") == "missed_window"]

    if explore_now:
        lines.append("## 🟢 Explore Now")
        lines.append("")
        for item in explore_now:
            e = item["eval"]
            lines.append(f"### {item['idea']['idea'][:80]}")
            lines.append(f"- **Source:** {item['idea']['source']}")
            lines.append(f"- **Score:** R={e.get('relevance','?')} F={e.get('feasibility','?')} V={e.get('value','?')} (total: {item['_score']})")
            lines.append(f"- **Recommendation:** {e.get('recommendation', 'N/A')}")
            lines.append(f"- **Reasoning:** {e.get('reasoning', 'N/A')}")
            lines.append("")

    if park:
        lines.append("## 🟡 Park for Later")
        lines.append("")
        for item in park:
            e = item["eval"]
            lines.append(f"- **{item['idea']['idea'][:80]}** (score: {item['_score']}) — {e.get('recommendation', '')}")
        lines.append("")

    if discard:
        lines.append("## ⚫ Missed Window / Discard")
        lines.append("")
        for item in discard:
            e = item["eval"]
            lines.append(f"- **{item['idea']['idea'][:80]}** — {e.get('recommendation', '')}")
        lines.append("")

    # Uncategorized
    other = [e for e in evaluated if e.get("eval", {}).get("timing") not in ("yes", "not_yet", "missed_window")]
    if other:
        lines.append("## ❓ Needs Review")
        lines.append("")
        for item in other:
            e = item["eval"]
            lines.append(f"- **{item['idea']['idea'][:80]}** (score: {item['_score']}) — {e.get('recommendation', '')}")
        lines.append("")

    lines.append("---")
    lines.append("*Generated by FAITHH PULSE Reflection Engine — Tier 3 Branch Explorer*")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="FAITHH Branch Explorer (Tier 3)")
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output", type=str, default=None)
    parser.add_argument("--quick", action="store_true",
                        help="Data mining only, skip LLM evaluation")
    parser.add_argument("--max-eval", type=int, default=25,
                        help="Max ideas to evaluate with LLM (default: 25)")
    parser.add_argument("--timeout", type=int, default=120)
    args = parser.parse_args()

    start = time.time()
    print("=" * 60)
    print("FAITHH PULSE Reflection Engine — Tier 3: Branch Explorer")
    print("=" * 60)

    # 1. Load data sources
    print("\n[1/4] Loading data sources...")
    scaffolding = load_json("scaffolding_state.json")
    decisions = load_json("decisions_log.json").get("decisions", [])
    project_state = load_json("project_states.json")

    # 2. Mine ideas from all sources
    print("\n[2/4] Mining unexplored ideas...")

    parked = extract_parked_tangents(scaffolding)
    print(f"  Parked tangents: {len(parked)}")

    rejected = extract_rejected_alternatives(decisions)
    print(f"  Rejected alternatives: {len(rejected)}")

    loops = extract_open_loops(scaffolding)
    print(f"  Open loops: {len(loops)}")

    archived = mine_archived_ideas(BASE_DIR / "docs" / "archive")
    print(f"  Archived TODOs: {len(archived)}")

    chromadb_ideas = mine_chromadb_ideas()
    print(f"  ChromaDB ideas: {len(chromadb_ideas)}")

    # Combine and deduplicate
    all_ideas = parked + rejected + loops + archived + chromadb_ideas
    all_ideas = deduplicate_ideas(all_ideas)
    print(f"  After dedup: {len(all_ideas)} unique ideas")

    raw_counts = {
        "parked": len(parked),
        "rejected": len(rejected),
        "loops": len(loops),
        "archived": len(archived),
        "chromadb": len(chromadb_ideas),
        "deduped": len(all_ideas),
    }

    if args.quick:
        print("\n[3/4] Skipping LLM evaluation (--quick mode)")
        print("\n[4/4] Mined ideas:")
        for i, idea in enumerate(all_ideas):
            print(f"  [{i+1}] [{idea['source']}] {idea['idea'][:80]}")

        elapsed = time.time() - start
        if args.json:
            print(json.dumps({"ideas": all_ideas, "counts": raw_counts}, indent=2))
        print(f"\nDone in {elapsed:.1f}s — {len(all_ideas)} ideas mined")
        return

    # 3. Evaluate with LLM
    print(f"\n[3/4] Evaluating top {min(args.max_eval, len(all_ideas))} ideas with {args.model}...")

    # Prioritize: parked tangents and open loops first, then others
    priority_order = []
    for idea in all_ideas:
        if "parked_tangent" in idea.get("source", "") or "open_loop" in idea.get("source", ""):
            priority_order.insert(0, idea)
        else:
            priority_order.append(idea)

    evaluated = []
    eval_count = min(args.max_eval, len(priority_order))

    for i, idea in enumerate(priority_order[:eval_count]):
        idea_text = idea.get("idea", "")[:60]
        print(f"\n  [{i+1}/{eval_count}] {idea['source']}: {idea_text}...")

        prompt = build_evaluation_prompt(idea, project_state, scaffolding)
        t0 = time.time()
        raw = query_ollama(prompt, args.model, timeout=args.timeout)
        llm_time = time.time() - t0

        evaluation = parse_llm_response(raw)
        timing = evaluation.get("timing", "?")
        score = evaluation.get("relevance", 0) + evaluation.get("feasibility", 0) + evaluation.get("value", 0)
        icon = {"yes": "🟢", "not_yet": "🟡", "missed_window": "⚫"}.get(timing, "❓")

        print(f"    {icon} {timing} (score: {score}/15, {llm_time:.1f}s)")

        evaluated.append({
            "idea": idea,
            "eval": evaluation,
            "llm_time": round(llm_time, 1),
        })

    elapsed = time.time() - start

    # 4. Output
    print(f"\n[4/4] Generating report...")

    if args.json:
        output = {
            "generated": datetime.now().isoformat(),
            "model": args.model,
            "elapsed_seconds": round(elapsed, 1),
            "counts": raw_counts,
            "evaluated": evaluated,
        }
        print(json.dumps(output, indent=2))
    else:
        report = format_report(evaluated, raw_counts, elapsed)
        print(f"\n{'=' * 60}")
        print(report)

        if args.output:
            output_path = BASE_DIR / "ml" / "output" / f"{args.output}.md"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(report)
            print(f"\nReport saved to: {output_path}")

    explore = sum(1 for e in evaluated if e.get("eval", {}).get("timing") == "yes")
    park = sum(1 for e in evaluated if e.get("eval", {}).get("timing") == "not_yet")
    print(f"\n{'=' * 60}")
    print(f"Exploration complete in {elapsed:.1f}s")
    print(f"  {explore} explore now, {park} park, {len(evaluated) - explore - park} other")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
