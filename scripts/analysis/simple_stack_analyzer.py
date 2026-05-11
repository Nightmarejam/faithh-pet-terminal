#!/usr/bin/env python3
"""
Simple AI-Stack Analyzer
Quick analysis without complex processing
"""

import os
import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime

def analyze_ai_stack():
    """Simple analysis of ai-stack directory"""
    root_path = Path("/home/jonat/ai-stack")
    
    print("Starting AI-Stack Analysis...")
    print("=" * 50)
    
    # Basic file scan
    files_by_type = defaultdict(int)
    files_by_category = defaultdict(list)
    total_size = 0
    
    categories = {
        "core_system": ["faithh_professional_backend", "faithh_pet", "config.yaml", "requirements.txt"],
        "phase7": ["phase7_", "sonnet_", "day", "app/services"],
        "documentation": [".md", "docs/"],
        "scripts": ["scripts/", ".sh"],
        "tests": ["tests/", "test_"],
        "data": ["data/", ".json", ".csv"],
        "legacy": ["old", "deprecated", "backup", "temp"],
        "experimental": ["experiment", "prototype", "ml/"]
    }
    
    for file_path in root_path.rglob("*"):
        if file_path.is_file():
            try:
                size = file_path.stat().st_size
                total_size += size
                relative_path = str(file_path.relative_to(root_path))
                
                # Categorize file
                category = "other"
                for cat_name, patterns in categories.items():
                    for pattern in patterns:
                        if pattern in relative_path.lower():
                            category = cat_name
                            break
                    if category != "other":
                        break
                
                files_by_category[category].append({
                    "path": relative_path,
                    "size": size,
                    "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                })
                
                # Count by type
                ext = file_path.suffix.lower()
                files_by_type[ext] += 1
                
            except Exception as e:
                print(f"Error scanning {file_path}: {e}")
    
    # Generate summary
    print(f"Total Files: {sum(len(files) for files in files_by_category.values())}")
    print(f"Total Size: {format_size(total_size)}")
    print()
    
    print("Files by Category:")
    for category, files in files_by_category.items():
        print(f"  {category}: {len(files)} files")
        if len(files) <= 5:  # Show details for small categories
            for file_info in files:
                print(f"    - {file_info['path']} ({format_size(file_info['size'])})")
        else:
            print(f"    (Top 5 largest files)")
            sorted_files = sorted(files, key=lambda x: x['size'], reverse=True)[:5]
            for file_info in sorted_files:
                print(f"    - {file_info['path']} ({format_size(file_info['size'])})")
    print()
    
    print("Files by Type:")
    for ext, count in sorted(files_by_type.items()):
        if ext:
            print(f"  {ext or 'no extension'}: {count} files")
    print()
    
    # Cleanup recommendations
    print("Cleanup Recommendations:")
    print("  KEEP ORGANIZED:")
    for category in ["core_system", "phase7", "documentation", "scripts", "tests", "data"]:
        files = files_by_category.get(category, [])
        if files:
            print(f"    {category}: {len(files)} files")
    
    print("  EVALUATE:")
    for category in ["experimental"]:
        files = files_by_category.get(category, [])
        if files:
            print(f"    {category}: {len(files)} files")
    
    print("  ARCHIVE OR DELETE:")
    for category in ["legacy", "other"]:
        files = files_by_category.get(category, [])
        if files:
            print(f"    {category}: {len(files)} files")
    
    # Save results
    results = {
        "scan_summary": {
            "total_files": sum(len(files) for files in files_by_category.values()),
            "total_size": total_size,
            "categories": {cat: len(files) for cat, files in files_by_category.items()},
            "file_types": dict(files_by_type)
        },
        "files_by_category": {cat: files for cat, files in files_by_category.items()}
    }
    
    with open("/home/jonat/ai-stack/simple_analysis_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\nResults saved to: simple_analysis_results.json")
    print("=" * 50)

def format_size(size_bytes):
    """Format file size"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f}{unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f}TB"

if __name__ == "__main__":
    analyze_ai_stack()