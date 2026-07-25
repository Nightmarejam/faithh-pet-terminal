#!/usr/bin/env python3
"""
Audit AI Chat Exports
Discovers export files and reports their structure/metadata availability.
"""

import os
import json
from pathlib import Path
from collections import defaultdict

EXPORT_DIRS = [
    Path.home() / "ai-stack" / "AI_Chat_Exports",
    Path.home() / "ai-stack" / "exports",
]

def analyze_json_structure(filepath, sample_depth=2):
    """Analyze JSON file structure without loading entire file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if isinstance(data, list):
            return {
                "type": "array",
                "count": len(data),
                "sample_keys": list(data[0].keys()) if data and isinstance(data[0], dict) else None
            }
        elif isinstance(data, dict):
            return {
                "type": "object",
                "top_keys": list(data.keys())[:10],
                "sample": {k: type(v).__name__ for k, v in list(data.items())[:5]}
            }
    except Exception as e:
        return {"error": str(e)}

def audit_exports():
    results = {
        "directories_found": [],
        "files_by_type": defaultdict(list),
        "platforms_detected": defaultdict(int),
        "total_size_mb": 0,
        "structures": {}
    }

    for export_dir in EXPORT_DIRS:
        if export_dir.exists():
            results["directories_found"].append(str(export_dir))

            for filepath in export_dir.rglob("*"):
                if filepath.is_file():
                    size_mb = filepath.stat().st_size / (1024 * 1024)
                    results["total_size_mb"] += size_mb

                    ext = filepath.suffix.lower()
                    results["files_by_type"][ext].append({
                        "path": str(filepath),
                        "size_mb": round(size_mb, 2)
                    })

                    # Detect platform from filename
                    name_lower = filepath.name.lower()
                    if "claude" in name_lower or "Claude" in str(filepath):
                        results["platforms_detected"]["claude"] += 1
                    elif "chatgpt" in name_lower or "gpt" in name_lower or "Chat_GPT" in str(filepath):
                        results["platforms_detected"]["chatgpt"] += 1
                    elif "grok" in name_lower or "Grok" in str(filepath):
                        results["platforms_detected"]["grok"] += 1

                    # Analyze JSON structure (sample first few important files)
                    if ext == ".json" and len(results["structures"]) < 15:
                        # Prioritize conversations.json files
                        if "conversations" in name_lower or "convos" in name_lower or "memories" in name_lower or "projects" in name_lower:
                            results["structures"][str(filepath.relative_to(Path.home() / "ai-stack"))] = analyze_json_structure(filepath)

    # Print report
    print("=" * 60)
    print("AI CHAT EXPORTS AUDIT")
    print("=" * 60)

    print(f"\nDirectories found: {len(results['directories_found'])}")
    for d in results["directories_found"]:
        print(f"  - {d}")

    print(f"\nTotal size: {results['total_size_mb']:.1f} MB")

    print(f"\nFiles by type:")
    for ext, files in sorted(results["files_by_type"].items()):
        total_size = sum(f['size_mb'] for f in files)
        print(f"  {ext if ext else '(no extension)':20s}: {len(files):4d} files ({total_size:7.1f} MB)")

    print(f"\nPlatforms detected:")
    for platform, count in sorted(results["platforms_detected"].items()):
        print(f"  {platform:15s}: {count:4d} files")

    print(f"\nJSON structures (key files):")
    for name, structure in results["structures"].items():
        print(f"\n  {name}:")
        if "error" in structure:
            print(f"    ERROR: {structure['error']}")
        else:
            print(f"    Type: {structure.get('type', 'unknown')}")
            if structure.get('type') == 'array':
                print(f"    Count: {structure.get('count', 0)}")
                print(f"    Sample keys: {structure.get('sample_keys', [])}")
            elif structure.get('type') == 'object':
                print(f"    Top keys: {structure.get('top_keys', [])}")

    # Save full report
    report_path = Path.home() / "ai-stack" / "docs" / "EXPORT_AUDIT.json"
    with open(report_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nFull report saved to: {report_path}")

    return results

if __name__ == "__main__":
    audit_exports()
