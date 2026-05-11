#!/usr/bin/env python3
"""
FAITHH Knowledge Graph Document Generator
Generates human-readable markdown from the YAML knowledge graph.

Usage:
    python generate_docs.py knowledge_graph.yaml --output ./docs/
"""

import yaml
import argparse
from pathlib import Path
from datetime import datetime


def load_knowledge_graph(path: str) -> dict:
    """Load and parse the YAML knowledge graph."""
    with open(path, 'r') as f:
        # Handle multiple YAML documents in one file
        docs = list(yaml.safe_load_all(f))
    
    # Merge all documents into one dict
    merged = {}
    for doc in docs:
        if doc:
            merged.update(doc)
    return merged


def generate_roadmap(kg: dict) -> str:
    """Generate ROADMAP.md from knowledge graph."""
    faithh = kg.get('entities', {}).get('faithh', {})
    
    lines = [
        "# FAITHH Development Roadmap",
        f"\n*Auto-generated from knowledge graph on {datetime.now().strftime('%Y-%m-%d')}*\n",
        "---\n",
        
        "## Current State\n",
    ]
    
    # Architecture components
    arch = faithh.get('architecture', {}).get('components', {})
    for comp_name, comp_data in arch.items():
        status = comp_data.get('status', 'unknown')
        status_emoji = "✅" if status == "operational" else "🔄" if status == "development" else "❌"
        lines.append(f"### {comp_name.replace('_', ' ').title()} {status_emoji}\n")
        lines.append(f"**Status:** {status}\n")
        
        if 'database' in comp_data:
            lines.append(f"- Database: {comp_data['database']}")
        if 'documents_indexed' in comp_data:
            lines.append(f"- Documents Indexed: {comp_data['documents_indexed']:,}")
        if 'behavior' in comp_data:
            lines.append(f"- Behavior: {comp_data['behavior']}")
        if 'gpu' in comp_data:
            lines.append(f"- GPU: {comp_data['gpu']}")
        if 'performance' in comp_data:
            lines.append(f"- Performance: {comp_data['performance']}")
        
        lines.append("")
    
    # Known Issues
    lines.append("---\n")
    lines.append("## Known Issues\n")
    
    for comp_name, comp_data in arch.items():
        issues = comp_data.get('known_issues', [])
        if issues:
            lines.append(f"### {comp_name.replace('_', ' ').title()}\n")
            for issue in issues:
                lines.append(f"- ⚠️ {issue}")
            lines.append("")
    
    # Proposed Solutions
    lines.append("---\n")
    lines.append("## Proposed Solutions\n")
    
    for comp_name, comp_data in arch.items():
        solutions = comp_data.get('proposed_solutions', [])
        if solutions:
            lines.append(f"### {comp_name.replace('_', ' ').title()}\n")
            for solution in solutions:
                lines.append(f"- 💡 {solution}")
            lines.append("")
    
    # Development Priorities
    lines.append("---\n")
    lines.append("## Development Priorities\n")
    
    priorities = faithh.get('development_priorities', {})
    for level in ['high', 'medium', 'low']:
        items = priorities.get(level, [])
        if items:
            emoji = "🔴" if level == "high" else "🟡" if level == "medium" else "🟢"
            lines.append(f"### {emoji} {level.title()} Priority\n")
            for item in items:
                lines.append(f"- {item}")
            lines.append("")
    
    # Decisions Log
    lines.append("---\n")
    lines.append("## Recent Decisions\n")
    
    decisions = faithh.get('decisions_log', [])
    for decision in decisions:
        lines.append(f"### {decision.get('date', 'Unknown date')}\n")
        lines.append(f"**Decision:** {decision.get('decision', 'N/A')}\n")
        lines.append(f"**Reasoning:** {decision.get('reasoning', 'N/A')}\n")
    
    return '\n'.join(lines)


def generate_project_map(kg: dict) -> str:
    """Generate PROJECT_MAP.md from knowledge graph."""
    entities = kg.get('entities', {})
    relationships = kg.get('relationships', [])
    
    lines = [
        "# Project Constellation Map",
        f"\n*Auto-generated from knowledge graph on {datetime.now().strftime('%Y-%m-%d')}*\n",
        "---\n",
        
        "## The Operator\n",
    ]
    
    # Jonathan
    jonathan = entities.get('jonathan', {})
    lines.append(f"**{jonathan.get('role', 'Unknown')}**\n")
    
    philosophy = jonathan.get('philosophy', {})
    if philosophy:
        lines.append(f"> *\"{philosophy.get('core', '')}\"*\n")
        lines.append(f"> Driving Question: {philosophy.get('driving_question', '')}\n")
    
    challenges = jonathan.get('challenges', [])
    if challenges:
        lines.append("**Challenges:**")
        for c in challenges:
            lines.append(f"- {c}")
        lines.append("")
    
    # Projects
    lines.append("---\n")
    lines.append("## Projects\n")
    
    # Tom Cat Sound
    tcs = entities.get('tom_cat_sound', {})
    if tcs:
        lines.append("### 🎵 Tom Cat Sound LLC\n")
        lines.append(f"**DBA:** {tcs.get('dba', 'N/A')}\n")
        lines.append(f"**Status:** {tcs.get('status', 'unknown')}\n")
        lines.append(f"**Formed:** {tcs.get('formed', 'N/A')}\n")
        
        revenue = tcs.get('revenue_streams', [])
        if revenue:
            total = sum(r.get('total_revenue', 0) for r in revenue)
            lines.append(f"\n**Total Revenue:** ${total:,}\n")
            for r in revenue:
                lines.append(f"- {r['name']}: ${r.get('total_revenue', 0):,}")
        lines.append("")
    
    # FAITHH
    faithh = entities.get('faithh', {})
    if faithh:
        lines.append("### 🤖 FAITHH\n")
        lines.append(f"**Full Name:** {faithh.get('full_name', 'N/A')}\n")
        lines.append(f"**Status:** {faithh.get('status', 'unknown')}\n")
        
        purpose = faithh.get('purpose', {})
        if purpose:
            lines.append(f"\n**Purpose:** {purpose.get('primary', 'N/A')}\n")
            lines.append(f"> *\"{purpose.get('philosophy', '')}\"*\n")
        lines.append("")
    
    # Constella
    constella = entities.get('constella', {})
    if constella:
        lines.append("### 🌐 Constella Framework\n")
        lines.append(f"**Version:** {constella.get('version', 'N/A')}\n")
        lines.append(f"**Status:** {constella.get('status', 'unknown')}\n")
        
        purpose = constella.get('purpose', {})
        if purpose:
            lines.append(f"\n**Purpose:** {purpose.get('primary', 'N/A')}\n")
        
        apps = constella.get('potential_applications', [])
        if apps:
            lines.append("\n**Potential Applications:**")
            for app in apps:
                lines.append(f"- {app}")
        lines.append("")
    
    # Relationships
    lines.append("---\n")
    lines.append("## How They Connect\n")
    
    for rel in relationships:
        from_entity = rel.get('from', 'unknown')
        to_entity = rel.get('to', 'unknown')
        rel_type = rel.get('type', 'relates_to')
        description = rel.get('description', '')
        
        # Handle list of entities
        if isinstance(from_entity, list):
            from_entity = ' + '.join(from_entity)
        
        lines.append(f"**{from_entity}** → *{rel_type}* → **{to_entity}**")
        if description:
            lines.append(f"  - {description}")
        lines.append("")
    
    # Unified Vision
    lines.append("---\n")
    lines.append("## Unified Vision\n")
    lines.append("All three projects answer the same fundamental question:\n")
    lines.append(f"> **\"{jonathan.get('philosophy', {}).get('driving_question', 'How do we build systems that serve people well?')}\"**\n")
    lines.append("""
- **Tom Cat Sound** answers it through *fair, artist-first business practices*
- **FAITHH** answers it through *AI that maintains human context and coherence*  
- **Constella** answers it through *governance systems that preserve dignity*
""")
    
    return '\n'.join(lines)


def generate_indexing_spec(kg: dict) -> str:
    """Generate INDEXING_SPEC.md for the auto-indexer."""
    rules = kg.get('indexing_rules', {})
    
    lines = [
        "# FAITHH Auto-Indexer Specification",
        f"\n*Auto-generated from knowledge graph on {datetime.now().strftime('%Y-%m-%d')}*\n",
        "---\n",
        
        "## Tiered Storage System\n",
    ]
    
    tiers = rules.get('tiers', {})
    for tier_name, tier_data in tiers.items():
        lines.append(f"### {tier_name.replace('_', ' ').title()}\n")
        lines.append(f"**Description:** {tier_data.get('description', 'N/A')}\n")
        lines.append(f"**Storage:** {tier_data.get('storage', 'N/A')}\n")
        lines.append(f"**Retention:** {tier_data.get('retention', 'N/A')}\n")
        
        criteria = tier_data.get('criteria', [])
        if criteria:
            lines.append("\n**Criteria:**")
            for c in criteria:
                lines.append(f"- {c}")
        lines.append("")
    
    # Negative examples
    neg = rules.get('negative_examples', {})
    if neg:
        lines.append("---\n")
        lines.append("## Negative Examples Archive\n")
        lines.append(f"**Description:** {neg.get('description', 'N/A')}\n")
        lines.append(f"**Storage:** {neg.get('storage', 'N/A')}\n")
        lines.append(f"**Purpose:** {neg.get('purpose', 'N/A')}\n")
        
        criteria = neg.get('criteria', [])
        if criteria:
            lines.append("\n**Criteria:**")
            for c in criteria:
                lines.append(f"- {c}")
        lines.append("")
    
    # Quality signals
    signals = rules.get('quality_signals', {})
    if signals:
        lines.append("---\n")
        lines.append("## Quality Signals\n")
        
        positive = signals.get('positive', [])
        if positive:
            lines.append("### ✅ Positive Signals (Index)\n")
            for sig in positive:
                if isinstance(sig, dict):
                    for k, v in sig.items():
                        lines.append(f"- **{k}:** {v}")
                else:
                    lines.append(f"- {sig}")
            lines.append("")
        
        negative = signals.get('negative', [])
        if negative:
            lines.append("### ❌ Negative Signals (Archive/Discard)\n")
            for sig in negative:
                if isinstance(sig, dict):
                    for k, v in sig.items():
                        lines.append(f"- **{k}:** {v}")
                else:
                    lines.append(f"- {sig}")
            lines.append("")
    
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='Generate docs from FAITHH knowledge graph')
    parser.add_argument('input', help='Path to knowledge graph YAML file')
    parser.add_argument('--output', '-o', default='./docs', help='Output directory for generated docs')
    args = parser.parse_args()
    
    # Load knowledge graph
    print(f"Loading knowledge graph from {args.input}...")
    kg = load_knowledge_graph(args.input)
    
    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate documents
    docs = [
        ('ROADMAP.md', generate_roadmap(kg)),
        ('PROJECT_MAP.md', generate_project_map(kg)),
        ('INDEXING_SPEC.md', generate_indexing_spec(kg)),
    ]
    
    for filename, content in docs:
        output_path = output_dir / filename
        with open(output_path, 'w') as f:
            f.write(content)
        print(f"Generated: {output_path}")
    
    print("\nDone! Generated documents:")
    for filename, _ in docs:
        print(f"  - {output_dir / filename}")


if __name__ == '__main__':
    main()
