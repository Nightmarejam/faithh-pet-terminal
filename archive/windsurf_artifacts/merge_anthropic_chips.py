#!/usr/bin/env python3
"""
Merge Anthropic optimization chips into existing ML chips
"""

import json
from pathlib import Path

def merge_chips():
    """Merge new Anthropic chips into existing chips.json"""
    
    # Load existing chips
    chips_file = Path("ml/output/chips.json")
    with open(chips_file, 'r') as f:
        existing_data = json.load(f)
    
    # Load new Anthropic chips
    anthropic_file = Path("ml/output/anthropic_optimization_chips.json")
    with open(anthropic_file, 'r') as f:
        anthropic_chips = json.load(f)
    
    # Convert new chips to match existing format
    converted_chips = []
    for chip in anthropic_chips:
        converted_chip = {
            "id": chip["id"],
            "name": chip["title"],
            "keywords": chip.get("applicable_to", []),
            "representative_excerpts": [chip["content"]],
            "activation_keywords": chip.get("applicable_to", []),
            "type": chip["type"],
            "category": chip["category"],
            "project": chip["project"],
            "date": chip["date"],
            "impact": chip.get("impact", "medium"),
            "actionable": chip.get("actionable", False),
            "rank": len(existing_data["chips"]) + len(converted_chips)
        }
        
        # Add type-specific fields
        if chip["type"] == "decision":
            converted_chip["alternatives"] = chip.get("alternatives", [])
        elif chip["type"] == "pattern":
            converted_chip["code_example"] = chip.get("code_example", "")
            converted_chip["config_example"] = chip.get("config_example", "")
            converted_chip["reusable"] = chip.get("reusable", False)
        
        converted_chips.append(converted_chip)
    
    # Merge chips
    existing_data["chips"].extend(converted_chips)
    
    # Update metadata
    existing_data["anthropic_optimization"] = {
        "added": len(converted_chips),
        "date": "2026-03-28",
        "project": "anthropic_api_optimization"
    }
    
    # Save merged chips
    with open(chips_file, 'w') as f:
        json.dump(existing_data, f, indent=2)
    
    print(f"✅ Merged {len(converted_chips)} Anthropic optimization chips")
    print(f"✅ Total chips: {len(existing_data['chips'])}")
    print(f"✅ Updated {chips_file}")

if __name__ == "__main__":
    merge_chips()
