#!/usr/bin/env python3
"""
generate_context.py - Generate unified AI context injection document

Reads from source-of-truth files and produces:
1. CONTEXT.md - Universal AI injection document
2. Optionally: Framing snapshot (immutable timestamp)

Usage:
    python scripts/generate_context.py                    # Generate CONTEXT.md only
    python scripts/generate_context.py --snapshot         # Also create framing snapshot
    python scripts/generate_context.py --output custom.md # Custom output path
    python scripts/generate_context.py --dry-run          # Preview without writing

Sources:
    - project_states.json (auto-updating technical state)
    - faithh_memory.json (AI self-awareness, user profile)
    - decisions_log.json (decision history with rationale)
    - scaffolding_state.json (session continuity)
    - faithh_knowledge_graph.yaml (entities, relationships)
"""

import json
import yaml
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Paths
AI_STACK = Path.home() / "ai-stack"
SOURCES = {
    "project_states": AI_STACK / "project_states.json",
    "faithh_memory": AI_STACK / "faithh_memory.json",
    "decisions_log": AI_STACK / "decisions_log.json",
    "scaffolding": AI_STACK / "scaffolding_state.json",
    "knowledge_graph": AI_STACK / "faithh_knowledge_graph.yaml",
    "life_map": AI_STACK / "LIFE_MAP.md",
}
TEMPLATE_PATH = AI_STACK / "templates" / "CONTEXT_TEMPLATE.md"
OUTPUT_PATH = AI_STACK / "CONTEXT.md"
SNAPSHOTS_DIR = AI_STACK / "snapshots" / "framing"


def load_json(path: Path) -> Optional[Dict]:
    """Load JSON file, return None if not found."""
    try:
        return json.loads(path.read_text())
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"⚠️  Could not load {path.name}: {e}")
        return None


def load_yaml(path: Path) -> Optional[Dict]:
    """Load YAML file, return None if not found.
    
    Handles multi-document YAML by merging all documents.
    """
    try:
        content = path.read_text()
        # Handle multi-document YAML (merged into single dict)
        docs = list(yaml.safe_load_all(content))
        if not docs:
            return None
        # Merge all documents into one dict
        result = {}
        for doc in docs:
            if isinstance(doc, dict):
                result.update(doc)
        return result
    except (FileNotFoundError, yaml.YAMLError) as e:
        print(f"⚠️  Could not load {path.name}: {e}")
        return None


def extract_project_state(data: Dict) -> Dict[str, Any]:
    """Extract relevant fields from project_states.json."""
    if not data:
        return {}
    
    projects = data.get("projects", {})
    faithh = projects.get("FAITHH", {})
    tomcat = projects.get("tomcat_sound", {})
    constella = projects.get("constella_harmony", {})
    
    return {
        "state_date": data.get("last_updated", "unknown"),
        "faithh_phase": faithh.get("phase", "unknown"),
        "faithh_status": faithh.get("phase_status", "unknown"),
        "faithh_recent": ", ".join(faithh.get("next_steps", [])[:2]) or "See project_states.json",
        "chroma_url": faithh.get("infrastructure", {}).get("database", "unknown"),
        "chunk_count": faithh.get("infrastructure", {}).get("chunks_indexed", "unknown"),
        "conversation_count": faithh.get("infrastructure", {}).get("breakdown", {}).get("total_conversations", "unknown"),
        "tomcat_phase": tomcat.get("phase", "Operations"),
        "tomcat_status": tomcat.get("status", "active"),
        "tomcat_recent": ", ".join(tomcat.get("recent_work", [])[:2]) if tomcat.get("recent_work") else "Ongoing operations",
        "constella_phase": constella.get("phase", "Documentation"),
        "constella_status": constella.get("phase_status", "in_progress"),
        "constella_version": constella.get("integration_status", {}).get("documentation", "See project"),
        "constella_recent": ", ".join(constella.get("next_steps", [])[:2]) if constella.get("next_steps") else "Documentation work",
    }


def extract_scaffolding(data: Dict) -> Dict[str, str]:
    """Extract relevant fields from scaffolding_state.json."""
    if not data:
        return {
            "current_position": "Not available - check scaffolding_state.json",
            "open_loops": "Not available",
            "parked_tangents": "Not available",
        }
    
    active = data.get("active_context", {})
    
    # Format open loops
    loops = data.get("open_loops", [])
    if loops:
        loop_text = "\n".join([f"- **{l.get('id', 'unknown')}**: {l.get('item', '')} ({l.get('status', 'unknown')})" for l in loops[:5]])
    else:
        loop_text = "No open loops recorded"
    
    # Format parked tangents
    parked = data.get("parked_tangents", [])
    if parked:
        parked_text = "\n".join([f"- {p.get('idea', '')} — *{p.get('why_parked', '')}*" for p in parked[:5]])
    else:
        parked_text = "No parked tangents"
    
    return {
        "current_position": active.get("position_summary", "Not specified"),
        "open_loops": loop_text,
        "parked_tangents": parked_text,
    }


def extract_decisions(data: Dict, limit: int = 5) -> str:
    """Extract recent decisions from decisions_log.json."""
    if not data:
        return "No decisions log available"
    
    decisions = data.get("decisions", [])
    if not decisions:
        return "No decisions recorded"
    
    # Sort by date descending, take most recent
    sorted_decisions = sorted(decisions, key=lambda d: d.get("date", ""), reverse=True)[:limit]
    
    lines = []
    for d in sorted_decisions:
        lines.append(f"### {d.get('decision', 'Untitled')} ({d.get('date', 'unknown')})")
        lines.append(f"**Project:** {d.get('project', 'unknown')} | **Status:** {d.get('status', 'unknown')}")
        lines.append(f"\n{d.get('rationale', 'No rationale recorded')}\n")
    
    return "\n".join(lines)


def extract_entities(data: Dict) -> str:
    """Extract entities section from knowledge graph."""
    if not data:
        return "Knowledge graph not available"
    
    entities = data.get("entities", {})
    if not entities:
        return "No entities defined"
    
    lines = []
    for name, entity in entities.items():
        etype = entity.get("type", "unknown")
        if etype == "person":
            role = entity.get("role", "")
            lines.append(f"- **{name}** (person): {role}")
        elif etype == "business":
            legal = entity.get("legal_name", name)
            dba = entity.get("dba", "")
            lines.append(f"- **{legal}** (business): dba {dba}" if dba else f"- **{legal}** (business)")
        elif etype == "ai_system":
            purpose = entity.get("purpose", {}).get("primary", "")
            lines.append(f"- **{entity.get('full_name', name)}** (AI system): {purpose}")
        elif etype == "framework":
            purpose = entity.get("purpose", {}).get("primary", "")
            lines.append(f"- **{entity.get('full_name', name)}** (framework): {purpose}")
    
    return "\n".join(lines) if lines else "No entities extracted"


def extract_relationships(data: Dict) -> str:
    """Extract relationships section from knowledge graph."""
    if not data:
        return "Knowledge graph not available"
    
    relationships = data.get("relationships", [])
    if not relationships:
        return "No relationships defined"
    
    lines = []
    for rel in relationships:
        from_entity = rel.get("from", "unknown")
        to_entity = rel.get("to", "unknown")
        rel_type = rel.get("type", "relates-to")
        desc = rel.get("description", "")
        
        # Handle list of entities
        if isinstance(from_entity, list):
            from_entity = ", ".join(from_entity)
        if isinstance(to_entity, list):
            to_entity = ", ".join(to_entity)
        
        lines.append(f"- {from_entity} **{rel_type}** {to_entity}: {desc}")
    
    return "\n".join(lines) if lines else "No relationships extracted"


def estimate_tokens(text: str) -> int:
    """Rough token estimate (words * 1.3)."""
    return int(len(text.split()) * 1.3)


def generate_context(dry_run: bool = False) -> str:
    """Generate the CONTEXT.md content."""
    
    print("📚 Loading source files...")
    
    # Load all sources
    project_states = load_json(SOURCES["project_states"])
    faithh_memory = load_json(SOURCES["faithh_memory"])
    decisions_log = load_json(SOURCES["decisions_log"])
    scaffolding = load_json(SOURCES["scaffolding"])
    knowledge_graph = load_yaml(SOURCES["knowledge_graph"])
    
    print("🔧 Extracting data...")
    
    # Extract data from each source
    state_data = extract_project_state(project_states)
    scaffolding_data = extract_scaffolding(scaffolding)
    decisions_text = extract_decisions(decisions_log)
    entities_text = extract_entities(knowledge_graph)
    relationships_text = extract_relationships(knowledge_graph)
    
    # Build template variables
    now = datetime.now().isoformat()
    
    variables = {
        "generated_at": now,
        **state_data,
        **scaffolding_data,
        "decisions_section": decisions_text,
        "entities_section": entities_text,
        "relationships_section": relationships_text,
        # Static/semi-static content from LIFE_MAP (could parse but keeping simple)
        "core_tension": "You keep building infrastructure for coherence (FAITHH) instead of using what you have to generate income (FGS). This makes sense because FAITHH solves the coherence problem... but it creates a loop.",
        "paths_summary": "**Path A:** Income First (FGS focus)\\n**Path B:** FAITHH Investment (tool completion)\\n**Path C:** Parallel Tracks (40% FGS / 30% FAITHH / 20% Permaculture / 10% Constella)",
        "compass_question": "Stop building the compass and start using it. FAITHH at current state is functional. The question isn't whether it's perfect — it's whether you're consulting it when you get lost.",
        "token_estimate": 0,  # Will update after generation
    }
    
    print("📝 Loading template...")
    
    # Load template
    try:
        template = TEMPLATE_PATH.read_text()
    except FileNotFoundError:
        print(f"❌ Template not found at {TEMPLATE_PATH}")
        print("   Creating from inline template...")
        template = create_inline_template()
    
    print("🔄 Filling template...")
    
    # Fill template (simple string replacement)
    content = template
    for key, value in variables.items():
        placeholder = "{" + key + "}"
        if isinstance(value, (int, float)):
            value = str(value)
        content = content.replace(placeholder, str(value) if value else "N/A")
    
    # Update token estimate
    token_est = estimate_tokens(content)
    content = content.replace("{token_estimate}", str(token_est))
    
    print(f"✅ Generated {len(content)} characters (~{token_est} tokens)")
    
    return content


def create_inline_template() -> str:
    """Fallback inline template if file not found."""
    return """# Jonathan's Project Context
<!-- Generated: {generated_at} -->

## Who I Am
Jonathan - Audio Producer & AI Developer
Core Challenge: Maintaining project coherence when attention shifts (ADHD)

## Current State ({state_date})
- FAITHH: {faithh_phase} ({faithh_status})
- Tom Cat Sound: {tomcat_phase} ({tomcat_status})
- Constella: {constella_phase} ({constella_status})

## Active Focus
{current_position}

## Open Loops
{open_loops}

## Key Decisions
{decisions_section}

---
Token estimate: {token_estimate}
"""


def create_framing_snapshot(content: str) -> Path:
    """Create an immutable framing snapshot."""
    date_str = datetime.now().strftime("%Y-%m-%d")
    snapshot_path = SNAPSHOTS_DIR / f"{date_str}.md"
    
    # Add snapshot header
    header = f"""# Framing Snapshot: {date_str}
<!-- IMMUTABLE: Do not edit after creation -->
<!-- Created: {datetime.now().isoformat()} -->

---

"""
    
    snapshot_content = header + content
    
    # Check if already exists today
    if snapshot_path.exists():
        # Add time suffix
        time_str = datetime.now().strftime("%H%M")
        snapshot_path = SNAPSHOTS_DIR / f"{date_str}_{time_str}.md"
    
    snapshot_path.write_text(snapshot_content)
    return snapshot_path


def main():
    parser = argparse.ArgumentParser(description="Generate unified AI context document")
    parser.add_argument("--output", "-o", type=Path, default=OUTPUT_PATH,
                        help="Output path for CONTEXT.md")
    parser.add_argument("--snapshot", "-s", action="store_true",
                        help="Also create a framing snapshot")
    parser.add_argument("--dry-run", "-n", action="store_true",
                        help="Preview output without writing files")
    args = parser.parse_args()
    
    print("=" * 60)
    print("CONTEXT GENERATOR")
    print("=" * 60)
    
    # Generate content
    content = generate_context(dry_run=args.dry_run)
    
    if args.dry_run:
        print("\n--- DRY RUN OUTPUT ---\n")
        print(content[:2000])
        print("\n... (truncated) ...")
        return
    
    # Write main output
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(content)
    print(f"\n📄 Written: {args.output}")
    
    # Create snapshot if requested
    if args.snapshot:
        snapshot_path = create_framing_snapshot(content)
        print(f"📸 Snapshot: {snapshot_path}")
    
    print("\n✅ Done!")


if __name__ == "__main__":
    main()
