#!/usr/bin/env python3
"""
Impact analyzer — given a component ID or name, traces what it affects.
Reads component_map.json, project_status.json, process_registry.json.

Usage:
    python3 scripts/impact_analyzer.py --component api_chat
    python3 scripts/impact_analyzer.py --component llm_route
    python3 scripts/impact_analyzer.py --list
    python3 scripts/impact_analyzer.py --changed-today
    python3 scripts/impact_analyzer.py --component api_chat --json
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
COMPONENT_MAP = BASE / "projects/status/component_map.json"
PROJECT_STATUS = BASE / "projects/status/project_status.json"
PROCESS_REG = BASE / "docs/architecture/process_registry.json"


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    except Exception as e:
        return {"error": str(e)}


def find_component(components, query: str):
    query = query.lower().strip()
    for c in components:
        cid = c.get("id", "").lower()
        cname = (c.get("name") or "").lower()
        if cid == query or query in cid or query in cname:
            return c
    return None


def trace_dependents(components, component_id: str):
    """Find components that list component_id in depends_on (direct)."""
    direct = []
    for c in components:
        if component_id in c.get("depends_on", []):
            direct.append(c["id"])
    indirect = []
    for dep_id in direct:
        for c in components:
            if dep_id in c.get("depends_on", []) and c["id"] not in direct and c["id"] != component_id:
                indirect.append(c["id"])
    return direct, list(dict.fromkeys(indirect))


def trace_dependencies(components, component_id: str):
    comp = find_component(components, component_id)
    if not comp:
        return [], []
    direct = list(comp.get("depends_on", []))
    indirect = []
    for dep in direct:
        dep_comp = find_component(components, dep)
        if dep_comp:
            for d2 in dep_comp.get("depends_on", []):
                if d2 not in direct and d2 not in indirect:
                    indirect.append(d2)
    return direct, indirect


def get_related_gates(project_status, track_ids):
    gates = []
    for track in project_status.get("tracks", []):
        if track["id"] not in track_ids:
            continue
        for gate in track.get("gates", []):
            if gate.get("status") != "completed":
                gates.append(
                    f"{track['id']}-{gate['id']}: {gate.get('title', '')} ({gate.get('status', '')})"
                )
    return gates


def analyze_component(component_id, components, project_status):
    comp = find_component(components, component_id)
    if not comp:
        return {"error": f"Component '{component_id}' not found. Use --list to see options."}

    direct_deps, indirect_deps = trace_dependencies(components, comp["id"])
    direct_consumers, indirect_consumers = trace_dependents(components, comp["id"])
    related_gates = get_related_gates(project_status, comp.get("related_tracks", []))

    consumer_count = len(direct_consumers) + len(indirect_consumers)
    dep_count = len(direct_deps) + len(indirect_deps)
    if consumer_count >= 3 or dep_count >= 4:
        risk = "HIGH — many dependents or dependencies. Test thoroughly."
    elif consumer_count >= 1 or dep_count >= 2:
        risk = "MEDIUM — some dependents. Verify consumers after change."
    else:
        risk = "LOW — few or no dependents. Change is relatively isolated."

    return {
        "component": comp["name"],
        "type": comp["type"],
        "file": comp["file"],
        "last_changed": comp["last_changed"],
        "change_summary": comp["change_summary"],
        "impact": {
            "direct_consumers": direct_consumers,
            "indirect_consumers": indirect_consumers,
            "direct_dependencies": direct_deps,
            "indirect_dependencies": indirect_deps,
        },
        "related_open_gates": related_gates,
        "change_risk": risk,
        "recommendation": _recommend(comp, direct_consumers, direct_deps),
        "change_log": comp.get("change_log", []),
    }


def _recommend(comp, consumers, deps):
    if comp["type"] == "endpoint":
        consumer_list = ", ".join(consumers) if consumers else "none found"
        return (
            f"This is an API endpoint. Dependent components: {consumer_list}. "
            "After any change: (1) restart backend, (2) hard refresh UI, "
            "(3) check browser console for fetch errors, (4) run smoke test."
        )
    if comp["type"] == "function":
        return (
            f"This is a core function. Dependents: {', '.join(consumers) or 'none'}. "
            "After any change: run python3 -m py_compile on the file, "
            "then restart backend and test affected endpoints."
        )
    if comp["type"] == "frontend":
        return (
            "This is frontend code. Hard refresh (Ctrl+Shift+R) required after changes. "
            "Check browser console. Verify API calls still match backend expectations."
        )
    return "Review dependents and test after any change."


def main():
    parser = argparse.ArgumentParser(description="FAITHH Impact Analyzer")
    parser.add_argument("--component", help="Component ID or name to analyze")
    parser.add_argument("--list", action="store_true", help="List all components")
    parser.add_argument("--changed-today", action="store_true", help="Show components changed today")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    cm = load_json(COMPONENT_MAP)
    ps = load_json(PROJECT_STATUS)
    if "error" in cm and not cm.get("components"):
        print(f"WARNING: component map load issue: {cm.get('error')}", file=sys.stderr)
    components = cm.get("components", [])

    if args.list:
        print("\nKnown components:")
        for c in components:
            print(f"  {c['id']:30s} {c['type']:12s} {c['name']}")
        return

    if args.changed_today:
        today = datetime.now().strftime("%Y-%m-%d")
        recent = [c for c in components if str(c.get("last_changed", "")) >= today]
        if not recent:
            print("No components changed today.")
        else:
            print(f"\nComponents changed today ({today}):")
            for c in recent:
                print(f"  {c['id']}: {c['change_summary']}")
        return

    if args.component:
        result = analyze_component(args.component, components, ps)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"\n=== Impact Analysis: {result.get('component', args.component)} ===")
            if "error" in result:
                print(f"ERROR: {result['error']}")
                return
            print(f"File:          {result['file']}")
            print(f"Type:          {result['type']}")
            print(f"Last changed:  {result['last_changed']}")
            print(f"Summary:       {result['change_summary']}")
            print(f"\nRisk level:    {result['change_risk']}")
            print(f"\nDirect consumers:    {result['impact']['direct_consumers'] or ['none']}")
            print(f"Indirect consumers:  {result['impact']['indirect_consumers'] or ['none']}")
            print(f"Direct deps:         {result['impact']['direct_dependencies'] or ['none']}")
            print(f"Indirect deps:       {result['impact']['indirect_dependencies'] or ['none']}")
            if result["related_open_gates"]:
                print("\nRelated open gates:")
                for g in result["related_open_gates"]:
                    print(f"  {g}")
            print(f"\nRecommendation:\n  {result['recommendation']}")
            if result["change_log"]:
                print("\nChange history:")
                for entry in result["change_log"]:
                    print(f"  [{entry['date']}] {entry['what']}")
                    print(f"           why: {entry['why']}")
                    print(f"        impact: {entry['impact']}")
        return

    parser.print_help()


if __name__ == "__main__":
    main()
