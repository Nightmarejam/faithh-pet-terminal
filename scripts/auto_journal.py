#!/usr/bin/env python3
"""
FAITHH Auto-Journal Generator
==============================
Generates daily journal entries from real activity data:
  - Git commits and file changes
  - PULSE reflection report summaries
  - Collector snapshots (health, files, git)
  - Decision log changes
  - Scaffolding state diffs

Output: ml/output/journal/YYYY-MM-DD.md — daily journal entry
        ml/output/journal/index.json — journal index for quick lookup

Usage:
  python scripts/auto_journal.py                   # Generate today's journal
  python scripts/auto_journal.py --date 2026-02-14 # Generate for specific date
  python scripts/auto_journal.py --week            # Generate last 7 days
  python scripts/auto_journal.py --json            # Output JSON to stdout
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent  # ~/ai-stack
OUTPUT_DIR = BASE_DIR / "ml" / "output" / "journal"
PULSE_DIR = BASE_DIR / "ml" / "output"
LOGS_DIR = BASE_DIR / "logs"
DECISIONS_LOG = BASE_DIR / "decisions_log.json"
SCAFFOLDING = BASE_DIR / "scaffolding_state.json"
WORK_LOG = BASE_DIR / "work_log.json"

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama31-faithh:latest")

# ChromaDB config
CHROMA_HOST = os.environ.get("CHROMA_HOST", "192.158.1.243")
CHROMA_PORT = int(os.environ.get("CHROMA_PORT", "8000"))
COLLECTION_NAME = "faithh_knowledge_base"


# ============================================================
# Data Collection
# ============================================================

def get_conversations_for_date(date_str):
    """Query ChromaDB for conversations indexed on a specific date.
    
    Note: The 'timestamp' field is the INDEX date, not the original conversation date.
    Original conversation dates aren't stored in ChromaDB metadata.
    This function returns conversations that were indexed on the given date.
    """
    try:
        import chromadb
        client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
        collection = client.get_collection(COLLECTION_NAME)
        
        # Get a sample and filter by index timestamp
        # This works for recent dates when conversations were indexed
        results = collection.get(
            limit=1000,
            include=["metadatas"]
        )
        
        conversations = []
        seen_titles = set()
        
        metas = results.get("metadatas", [])
        
        for meta in metas:
            timestamp = meta.get("timestamp", "")
            # Check if timestamp starts with the target date
            if not timestamp.startswith(date_str):
                continue
                
            title = meta.get("title", "")
            platform = meta.get("platform", "unknown")
            
            if title and title not in seen_titles:
                seen_titles.add(title)
                conversations.append({
                    "title": title,
                    "source": platform,
                    "preview": ""  # Skip preview to reduce memory
                })
        
        return {
            "count": len(conversations),
            "conversations": conversations[:10],  # Top 10
            "note": "Shows conversations indexed on this date, not original conversation dates"
        }
    except Exception as e:
        return {"error": str(e), "count": 0, "conversations": []}


def get_git_activity(date_str):
    """Get git commits and file changes for a specific date."""
    try:
        # Commits on this date
        result = subprocess.run(
            ["git", "log", "--oneline", "--after", f"{date_str} 00:00",
             "--before", f"{date_str} 23:59", "--format=%h %s"],
            cwd=BASE_DIR, capture_output=True, text=True, timeout=10,
        )
        commits = [line.strip() for line in result.stdout.strip().split("\n") if line.strip()]

        # Files changed
        result2 = subprocess.run(
            ["git", "log", "--after", f"{date_str} 00:00",
             "--before", f"{date_str} 23:59", "--name-only", "--format="],
            cwd=BASE_DIR, capture_output=True, text=True, timeout=10,
        )
        files = list(set(line.strip() for line in result2.stdout.strip().split("\n") if line.strip()))

        # Diff stats
        result3 = subprocess.run(
            ["git", "log", "--after", f"{date_str} 00:00",
             "--before", f"{date_str} 23:59", "--shortstat", "--format="],
            cwd=BASE_DIR, capture_output=True, text=True, timeout=10,
        )
        stats_lines = [l.strip() for l in result3.stdout.strip().split("\n") if l.strip()]

        return {
            "commits": commits,
            "commit_count": len(commits),
            "files_changed": files[:30],  # Cap to avoid huge lists
            "files_changed_count": len(files),
            "stats": stats_lines,
        }
    except Exception as e:
        return {"error": str(e), "commits": [], "commit_count": 0}


def get_pulse_reports(date_str):
    """Check if PULSE reports were generated on this date."""
    reports = {}
    for name, fname in [("staleness", "staleness_report.md"),
                         ("divergence", "divergence_report.md"),
                         ("branches", "branch_report.md")]:
        path = PULSE_DIR / fname
        if path.exists():
            mtime = datetime.fromtimestamp(path.stat().st_mtime)
            if mtime.strftime("%Y-%m-%d") == date_str:
                # Read first few lines for summary
                content = path.read_text(encoding="utf-8")
                # Extract summary section
                summary_lines = []
                in_summary = False
                for line in content.split("\n")[:30]:
                    if "## Summary" in line or "## Overview" in line:
                        in_summary = True
                        continue
                    if in_summary:
                        if line.startswith("## "):
                            break
                        if line.strip():
                            summary_lines.append(line.strip())
                reports[name] = {
                    "generated": mtime.isoformat(),
                    "summary": summary_lines[:5],
                }
    return reports


def get_collector_activity(date_str):
    """Check collector log for activity on this date."""
    log_path = LOGS_DIR / "collectors.log"
    if not log_path.exists():
        return {"note": "No collector log found"}

    try:
        lines = log_path.read_text(encoding="utf-8", errors="replace").split("\n")
        day_lines = [l for l in lines if date_str in l]
        return {
            "entries": len(day_lines),
            "sample": day_lines[:5] if day_lines else [],
        }
    except Exception as e:
        return {"error": str(e)}


def get_work_log_entries(date_str):
    """Get work log entries for the date."""
    if not WORK_LOG.exists():
        return []
    try:
        with open(WORK_LOG) as f:
            data = json.load(f)
        entries = data.get("entries", [])
        return [e for e in entries if e.get("date", "").startswith(date_str)]
    except Exception:
        return []


def get_decisions_for_date(date_str):
    """Check if any decisions were logged on this date."""
    if not DECISIONS_LOG.exists():
        return []
    try:
        with open(DECISIONS_LOG) as f:
            data = json.load(f)
        decisions = data.get("decisions", [])
        return [d for d in decisions if d.get("date", "").startswith(date_str)]
    except Exception:
        return []


# ============================================================
# Journal Generation
# ============================================================

def generate_journal_entry(date_str, include_conversations=True):
    """Generate a complete journal entry for a given date."""
    print(f"📓 Generating journal for {date_str}...")

    git = get_git_activity(date_str)
    pulse = get_pulse_reports(date_str)
    collectors = get_collector_activity(date_str)
    work_entries = get_work_log_entries(date_str)
    decisions = get_decisions_for_date(date_str)
    
    # Get conversations from ChromaDB
    conversations = {}
    if include_conversations:
        print(f"   💬 Querying conversations for {date_str}...")
        conversations = get_conversations_for_date(date_str)
        if conversations.get("count", 0) > 0:
            print(f"   ✅ Found {conversations['count']} conversations")

    # Determine activity level (now includes conversation count)
    commit_count = git.get("commit_count", 0)
    conv_count = conversations.get("count", 0)
    total_activity = commit_count + conv_count
    
    if total_activity >= 10:
        activity_level = "🔥 Very Active"
    elif total_activity >= 5:
        activity_level = "⚡ Active"
    elif total_activity >= 1:
        activity_level = "📝 Light"
    else:
        activity_level = "😴 Quiet"

    entry = {
        "date": date_str,
        "activity_level": activity_level,
        "git": git,
        "conversations": conversations,
        "pulse_reports": pulse,
        "collector_activity": collectors,
        "work_log": work_entries,
        "decisions": [{"id": d.get("id"), "title": d.get("title", d.get("decision", ""))} for d in decisions],
        "generated_at": datetime.now().isoformat(),
    }

    return entry


def synthesize_summary(entry, model=None):
    """Use local LLM to write a human-readable journal summary."""
    import requests

    model = model or OLLAMA_MODEL
    git = entry.get("git", {})
    commits = git.get("commits", [])
    pulse = entry.get("pulse_reports", {})
    decisions = entry.get("decisions", [])
    convos = entry.get("conversations", {})

    commit_str = "\n".join(f"  - {c}" for c in commits[:10]) if commits else "  No commits"
    pulse_str = "\n".join(f"  - {name}: {', '.join(r.get('summary', []))}" for name, r in pulse.items()) if pulse else "  No PULSE reports"
    decision_str = "\n".join(f"  - {d['id']}: {d['title']}" for d in decisions) if decisions else "  No new decisions"
    convo_str = "\n".join(f"  - {c.get('title', 'Untitled')} [{c.get('source', '')}]" for c in convos.get("conversations", [])[:5]) if convos.get("count", 0) > 0 else "  No conversations indexed"

    prompt = f"""Write a brief, personal daily journal entry (3-5 sentences) for a developer working on an AI assistant called FAITHH.
Date: {entry['date']}
Activity level: {entry['activity_level']}

Git commits ({git.get('commit_count', 0)}):
{commit_str}

Files changed: {git.get('files_changed_count', 0)}

Conversations ({convos.get('count', 0)} topics discussed):
{convo_str}

PULSE Reflection Reports:
{pulse_str}

Decisions logged:
{decision_str}

Write a concise journal entry summarizing the day's work. Use first person. Be specific about what was accomplished."""

    try:
        resp = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json={"model": model, "prompt": prompt, "stream": False,
                  "options": {"temperature": 0.7, "num_predict": 300}},
            timeout=90,
        )
        resp.raise_for_status()
        return resp.json().get("response", "").strip()
    except Exception as e:
        print(f"⚠️ LLM synthesis failed: {e}")
        return None


def render_markdown(entry, summary=None):
    """Render journal entry as markdown."""
    lines = [
        f"# 📓 Journal — {entry['date']}",
        f"**Activity:** {entry['activity_level']}",
        f"**Generated:** {entry['generated_at'][:16]}",
        "",
    ]

    if summary:
        lines.extend(["## Summary", summary, ""])

    git = entry.get("git", {})
    if git.get("commit_count", 0) > 0:
        lines.append(f"## Git ({git['commit_count']} commits, {git.get('files_changed_count', 0)} files)")
        for c in git.get("commits", [])[:15]:
            lines.append(f"- `{c}`")
        if git.get("stats"):
            lines.append(f"\n*{'; '.join(git['stats'][:3])}*")
        lines.append("")

    # Conversations from ChromaDB
    convos = entry.get("conversations", {})
    if convos.get("count", 0) > 0:
        lines.append(f"## Conversations ({convos['count']} topics)")
        for c in convos.get("conversations", [])[:10]:
            source = c.get("source", "")
            source_badge = f"[{source}]" if source else ""
            lines.append(f"- **{c.get('title', 'Untitled')}** {source_badge}")
            if c.get("preview"):
                lines.append(f"  > {c['preview'][:100]}...")
        lines.append("")

    pulse = entry.get("pulse_reports", {})
    if pulse:
        lines.append("## PULSE Reports Generated")
        for name, report in pulse.items():
            lines.append(f"- **{name}**: {', '.join(report.get('summary', ['generated']))}")
        lines.append("")

    decisions = entry.get("decisions", [])
    if decisions:
        lines.append("## Decisions Logged")
        for d in decisions:
            lines.append(f"- **{d['id']}**: {d['title']}")
        lines.append("")

    work = entry.get("work_log", [])
    if work:
        lines.append("## Work Log")
        for w in work:
            lines.append(f"- {w.get('description', w.get('task', 'work'))}")
        lines.append("")

    lines.append("---")
    lines.append("*Auto-generated by FAITHH Auto-Journal*")

    return "\n".join(lines)


def update_index(date_str, entry):
    """Update the journal index file."""
    index_path = OUTPUT_DIR / "index.json"
    try:
        index = json.loads(index_path.read_text()) if index_path.exists() else {"entries": []}
    except Exception:
        index = {"entries": []}

    # Remove existing entry for this date
    index["entries"] = [e for e in index["entries"] if e.get("date") != date_str]

    index["entries"].append({
        "date": date_str,
        "activity_level": entry.get("activity_level", ""),
        "commit_count": entry.get("git", {}).get("commit_count", 0),
        "pulse_reports": list(entry.get("pulse_reports", {}).keys()),
        "decisions": len(entry.get("decisions", [])),
    })

    # Sort by date descending
    index["entries"].sort(key=lambda x: x["date"], reverse=True)
    index["last_updated"] = datetime.now().isoformat()

    with open(index_path, "w") as f:
        json.dump(index, f, indent=2)


# ============================================================
# Main
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="FAITHH Auto-Journal Generator")
    parser.add_argument("--date", type=str, help="Date to generate for (YYYY-MM-DD)")
    parser.add_argument("--week", action="store_true", help="Generate last 7 days")
    parser.add_argument("--json", action="store_true", help="Output JSON to stdout")
    parser.add_argument("--skip-llm", action="store_true", help="Skip LLM summary synthesis")
    parser.add_argument("--model", type=str, default=OLLAMA_MODEL, help="Ollama model")
    args = parser.parse_args()

    start = time.time()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Determine dates to process
    if args.week:
        dates = [(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
    elif args.date:
        dates = [args.date]
    else:
        dates = [datetime.now().strftime("%Y-%m-%d")]

    all_entries = []

    for date_str in dates:
        entry = generate_journal_entry(date_str)

        # LLM summary
        summary = None
        if not args.skip_llm and entry.get("git", {}).get("commit_count", 0) > 0:
            print(f"🤖 Synthesizing summary for {date_str}...")
            summary = synthesize_summary(entry, args.model)

        # Render and save
        md = render_markdown(entry, summary)
        md_path = OUTPUT_DIR / f"{date_str}.md"
        with open(md_path, "w") as f:
            f.write(md)
        print(f"💾 Saved: {md_path.relative_to(BASE_DIR)}")

        # Also save structured JSON
        json_path = OUTPUT_DIR / f"{date_str}.json"
        entry["summary"] = summary
        with open(json_path, "w") as f:
            json.dump(entry, f, indent=2)

        update_index(date_str, entry)
        all_entries.append(entry)

    elapsed = round(time.time() - start, 1)

    if args.json:
        print(json.dumps(all_entries if len(all_entries) > 1 else all_entries[0], indent=2))
    else:
        print(f"\n⏱️  Completed in {elapsed}s — {len(dates)} journal(s) generated")
        for entry in all_entries:
            git = entry.get("git", {})
            print(f"  {entry['date']}: {entry['activity_level']} ({git.get('commit_count', 0)} commits)")


if __name__ == "__main__":
    main()
