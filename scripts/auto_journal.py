#!/usr/bin/env python3
"""
Auto-Journal Entry Generator for FAITHH
Analyzes conversation and generates resonance journal entries automatically
"""

import json
import re
from datetime import datetime
from pathlib import Path

def analyze_conversation(conversation_file):
    """
    Analyzes a FAITHH conversation and generates journal entry
    
    Args:
        conversation_file: Path to conversation JSON or text file
    
    Returns:
        dict: Structured journal entry
    """
    
    # This is a template - actual implementation would parse conversation
    # For now, showing the structure
    
    entry = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "morning_check": {
            "need_today": "Detected from first messages or manual input",
            "can_faithh_help": "Auto-detected or manual",
            "topic": "Auto-categorized (Constella/FAITHH/Audio/etc)"
        },
        "questions_analyzed": [],
        "evening_check": {
            "did_faithh_help": True,  # If any questions answered
            "what_worked": [],
            "what_missing": [],
            "would_use_again": True  # If avg rating >= 3
        },
        "auto_generated": True,
        "manual_review_needed": False
    }
    
    return entry

def auto_rate_response(question, response, context_retrieved):
    """
    Automatically rates a FAITHH response
    
    Criteria:
    - 5 stars: Made connections, asked follow-ups, helped thinking
    - 4 stars: Comprehensive answer with context
    - 3 stars: Correct but surface-level
    - 2 stars: Partial answer, missing key info
    - 1 star: Wrong or couldn't answer
    """
    
    rating = 3  # Default: correct but basic
    reasons = []
    
    # Check for connection-making (Level 2)
    if any(phrase in response.lower() for phrase in [
        "connect", "relate", "similar to", "reminds me of",
        "this is like", "in the same way"
    ]):
        rating += 1
        reasons.append("Made connections across concepts")
    
    # Check for follow-up questions (engagement)
    if "?" in response and any(phrase in response.lower() for phrase in [
        "would you like", "shall we", "want to explore", "tell me more"
    ]):
        rating += 0.5
        reasons.append("Asked follow-up questions")
    
    # Check for context usage
    if context_retrieved and len(context_retrieved) > 0:
        rating += 0.5
        reasons.append("Retrieved relevant context")
    
    # Check for actionable guidance
    if any(phrase in response.lower() for phrase in [
        "next step", "suggest", "recommend", "might consider",
        "focus on", "start with"
    ]):
        rating += 0.5
        reasons.append("Provided guidance")
    
    # Check for missing depth indicators
    if len(response.split()) < 50:
        rating -= 1
        reasons.append("Brief response, may lack depth")
    
    # Check for "I don't know" patterns
    if any(phrase in response.lower() for phrase in [
        "i don't have", "i can't", "i'm not sure",
        "unfortunately", "i don't know"
    ]):
        rating = max(1, rating - 2)
        reasons.append("Couldn't fully answer")
    
    # Clamp to 0-5 range
    rating = max(0, min(5, int(rating)))
    
    return {
        "rating": rating,
        "reasons": reasons
    }

def generate_journal_markdown(entry):
    """Converts structured entry to resonance_journal.md format"""
    
    md = f"\n### 📅 {entry['date']}\n\n"
    
    # Morning check
    md += "**Morning Check**:\n"
    md += f"- **Need today**: {entry['morning_check']['need_today']}\n"
    md += f"- **Can FAITHH help?**: {entry['morning_check']['can_faithh_help']}\n"
    md += f"- **Topic**: {entry['morning_check']['topic']}\n\n"
    
    # Evening check
    md += "**Evening Check**:\n"
    md += f"- **Did FAITHH help?**: {'Yes' if entry['evening_check']['did_faithh_help'] else 'No'}\n"
    
    if entry['evening_check']['what_worked']:
        md += "- **What worked**: \n"
        for item in entry['evening_check']['what_worked']:
            md += f"  - {item}\n"
    
    if entry['evening_check']['what_missing']:
        md += "- **What's missing**: \n"
        for item in entry['evening_check']['what_missing']:
            md += f"  - {item}\n"
    
    md += f"- **Would use again for this?**: {'Yes' if entry['evening_check']['would_use_again'] else 'No'}\n\n"
    
    # Notes
    if 'notes' in entry and entry['notes']:
        md += f"**Notes**: {entry['notes']}\n"
    
    if entry.get('auto_generated'):
        md += "\n*[Auto-generated entry - review and edit as needed]*\n"
    
    return md

# Simple CLI interface
if __name__ == "__main__":
    import sys
    
    print("🤖 FAITHH Auto-Journal Generator")
    print("=" * 60)
    
    # Example usage - would integrate with actual conversation data
    print("\nThis is a template. To use:")
    print("1. FAITHH logs conversations to a file")
    print("2. Run this script at end of day")
    print("3. It analyzes conversations and generates entry")
    print("4. Entry is appended to resonance_journal.md")
    print("5. You review and edit if needed")
    
    print("\n📋 Example generated entry:")
    
    example_entry = {
        "date": "2025-11-26",
        "morning_check": {
            "need_today": "Test FAITHH's context understanding",
            "can_faithh_help": "Yes",
            "topic": "Constella"
        },
        "evening_check": {
            "did_faithh_help": True,
            "what_worked": [
                "Astris formula (4 stars) - accurate, clear",
                "Resonance→audio connection (5 stars!) - insightful",
                "Penumbra Accord (4 stars) - comprehensive"
            ],
            "what_missing": [
                "Level 3 synthesis weak (3 stars) - gave tasks not vision",
                "Missing 'why' behind 2% decay rate"
            ],
            "would_use_again": True
        },
        "notes": "First real testing. FAITHH good at connections, needs big-picture work.",
        "auto_generated": True
    }
    
    print(generate_journal_markdown(example_entry))
    
    print("\n" + "=" * 60)
    print("Next step: Integrate with FAITHH backend")
    print("  - Add /api/journal endpoint")
    print("  - Log all Q&A with timestamps")
    print("  - Auto-generate entries at EOD")
