#!/usr/bin/env python3
"""
FAITHH Scaffolding Integration - Layer 1: Position Awareness
Add this to faithh_professional_backend_fixed.py

This provides persistent structural context that survives between sessions,
helping maintain orientation when switching between projects or returning to work.
"""

from pathlib import Path
from datetime import datetime
import json

# ============================================================
# SCAFFOLDING STATE - PERSISTENT STRUCTURAL AWARENESS
# ============================================================

SCAFFOLDING_FILE = Path.home() / "ai-stack/scaffolding_state.json"

def load_scaffolding():
    """Load scaffolding state from disk"""
    try:
        if SCAFFOLDING_FILE.exists():
            with open(SCAFFOLDING_FILE, 'r') as f:
                return json.load(f)
        return None
    except Exception as e:
        print(f"❌ Error loading scaffolding: {e}")
        return None

def save_scaffolding(scaffolding):
    """Persist scaffolding state to disk"""
    try:
        scaffolding['meta']['last_updated'] = datetime.now().isoformat()
        with open(SCAFFOLDING_FILE, 'w') as f:
            json.dump(scaffolding, f, indent=2)
        print(f"🏗️  Scaffolding saved: {datetime.now().strftime('%H:%M:%S')}")
    except Exception as e:
        print(f"❌ Error saving scaffolding: {e}")

def get_scaffolding_context(query_text=None):
    """
    Build orientation context from scaffolding state.
    This is the "You are HERE" function.
    """
    scaffolding = load_scaffolding()
    if not scaffolding:
        return None
    
    context_parts = []
    
    # Active context - where you are right now
    active = scaffolding.get('active_context', {})
    if active:
        context_parts.append(f"""
=== CURRENT POSITION ===
Project: {active.get('primary_project', 'Unknown').upper()}
Position: {active.get('structural_position', 'Unknown')}
Goal: {active.get('phase_goal', 'Not defined')}

Summary: {active.get('position_summary', '')}
=========================""")
    
    # Recent completions - what's done (with permission to move on)
    completions = scaffolding.get('recent_completions', [])
    if completions:
        latest = completions[0]  # Most recent
        context_parts.append(f"""
=== RECENTLY COMPLETED ===
What: {latest.get('what', '')}
When: {latest.get('when', '')}
Significance: {latest.get('structural_significance', '')}
Permission: {latest.get('permission', '')}
===========================""")
    
    # Open loops - what's in progress
    open_loops = scaffolding.get('open_loops', [])
    active_loops = [l for l in open_loops if l.get('status') != 'completed']
    if active_loops:
        context_parts.append("\n=== OPEN LOOPS ===")
        for loop in active_loops[:3]:  # Top 3
            context_parts.append(f"• {loop.get('item', '')}")
            context_parts.append(f"  Why: {loop.get('why_structural', '')}")
            context_parts.append(f"  Status: {loop.get('status', 'unknown')}")
        context_parts.append("==================")
    
    # Parked tangents - ideas noted but not current priority
    tangents = scaffolding.get('parked_tangents', [])
    if tangents and query_text:
        # Check if query might be about a parked tangent
        query_lower = query_text.lower()
        for tangent in tangents:
            if any(word in query_lower for word in tangent.get('idea', '').lower().split() if len(word) > 4):
                context_parts.append(f"""
=== PARKED TANGENT DETECTED ===
You previously parked: "{tangent.get('idea', '')}"
Why parked: {tangent.get('why_parked', '')}
Revisit when: {tangent.get('revisit_when', '')}

This is noted but not your current structural priority.
================================""")
                break
    
    return "\n".join(context_parts) if context_parts else None

def detect_orientation_need(query_text):
    """
    Detect if query is asking for orientation/position awareness.
    Returns True if scaffolding context should be injected.
    """
    query_lower = query_text.lower()
    
    orientation_patterns = [
        'where was i',
        'where did i leave off',
        'what was i working on',
        'what was i doing',
        'where am i',
        'what\'s the status',
        'what\'s my progress',
        'catch me up',
        'bring me up to speed',
        'what have i done',
        'what\'s been done',
        'what\'s complete',
        'what\'s finished',
        'am i on track',
        'how\'s it going',
        'what should i work on',
        'what\'s next',
        'where should i start',
        'what\'s the priority'
    ]
    
    return any(pattern in query_lower for pattern in orientation_patterns)

def detect_tangent(query_text, scaffolding=None):
    """
    Check if the current query might be a tangent from the main goal.
    Returns a gentle reminder if tangent detected.
    """
    if not scaffolding:
        scaffolding = load_scaffolding()
    if not scaffolding:
        return None
    
    query_lower = query_text.lower()
    active = scaffolding.get('active_context', {})
    current_goal = active.get('phase_goal', '')
    
    # Check parked tangents
    for tangent in scaffolding.get('parked_tangents', []):
        tangent_words = [w for w in tangent.get('idea', '').lower().split() if len(w) > 4]
        if any(word in query_lower for word in tangent_words):
            return {
                'is_tangent': True,
                'tangent_idea': tangent.get('idea', ''),
                'why_parked': tangent.get('why_parked', ''),
                'current_goal': current_goal,
                'message': f"This relates to a parked idea: '{tangent.get('idea', '')}'. Current goal is: '{current_goal}'. Want to park this and stay on track?"
            }
    
    return {'is_tangent': False}

def check_completion_signals(project_name=None):
    """
    Check if current work shows completion signals.
    Returns completion status with permission language.
    """
    scaffolding = load_scaffolding()
    if not scaffolding:
        return None
    
    completions = scaffolding.get('recent_completions', [])
    if not completions:
        return None
    
    # Get most recent completion
    latest = completions[0]
    
    return {
        'what_completed': latest.get('what', ''),
        'criteria_met': latest.get('criteria_met', []),
        'what_remains': latest.get('what_remains', ''),
        'permission': latest.get('permission', ''),
        'structural_significance': latest.get('structural_significance', '')
    }

def get_structural_milestones(project_name):
    """
    Get milestone progression for a project.
    Shows: completed → current → next → after_that
    """
    scaffolding = load_scaffolding()
    if not scaffolding:
        return None
    
    milestones = scaffolding.get('project_structural_milestones', {})
    project = milestones.get(project_name.lower(), {})
    
    if not project:
        return None
    
    return {
        'completed': project.get('completed', []),
        'current': project.get('current', 'Unknown'),
        'next': project.get('next', 'Unknown'),
        'after_that': project.get('after_that', 'Unknown')
    }

def update_scaffolding_position(project, position, goal, summary=None):
    """
    Update the current structural position.
    Call this when transitioning between phases.
    """
    scaffolding = load_scaffolding()
    if not scaffolding:
        scaffolding = {'meta': {}, 'active_context': {}}
    
    scaffolding['active_context'] = {
        'primary_project': project,
        'structural_position': position,
        'phase_goal': goal,
        'position_summary': summary or '',
        'entered_phase': datetime.now().strftime('%Y-%m-%d')
    }
    
    save_scaffolding(scaffolding)
    return scaffolding

def mark_completion(what, criteria_met, what_remains, permission, significance):
    """
    Mark something as structurally complete.
    This creates the "permission to move on" signal.
    """
    scaffolding = load_scaffolding()
    if not scaffolding:
        scaffolding = {'meta': {}, 'recent_completions': []}
    
    if 'recent_completions' not in scaffolding:
        scaffolding['recent_completions'] = []
    
    completion = {
        'what': what,
        'when': datetime.now().strftime('%Y-%m-%d'),
        'criteria_met': criteria_met,
        'what_remains': what_remains,
        'permission': permission,
        'structural_significance': significance
    }
    
    # Add to front of list
    scaffolding['recent_completions'].insert(0, completion)
    # Keep last 10
    scaffolding['recent_completions'] = scaffolding['recent_completions'][:10]
    
    save_scaffolding(scaffolding)
    return scaffolding

def park_tangent(idea, why_parked, revisit_when):
    """
    Park an idea for later - acknowledge it without losing it.
    """
    scaffolding = load_scaffolding()
    if not scaffolding:
        scaffolding = {'meta': {}, 'parked_tangents': []}
    
    if 'parked_tangents' not in scaffolding:
        scaffolding['parked_tangents'] = []
    
    tangent = {
        'idea': idea,
        'noted': datetime.now().strftime('%Y-%m-%d'),
        'why_parked': why_parked,
        'revisit_when': revisit_when
    }
    
    scaffolding['parked_tangents'].append(tangent)
    save_scaffolding(scaffolding)
    return scaffolding

def add_open_loop(item, why_structural, suggested_action=None):
    """
    Add an open loop - something in progress that needs attention.
    """
    scaffolding = load_scaffolding()
    if not scaffolding:
        scaffolding = {'meta': {}, 'open_loops': []}
    
    if 'open_loops' not in scaffolding:
        scaffolding['open_loops'] = []
    
    loop = {
        'id': f"loop_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        'item': item,
        'why_structural': why_structural,
        'created': datetime.now().strftime('%Y-%m-%d'),
        'status': 'in_progress',
        'blocked_by': None,
        'suggested_action': suggested_action
    }
    
    scaffolding['open_loops'].append(loop)
    save_scaffolding(scaffolding)
    return scaffolding

def close_open_loop(loop_id_or_item):
    """
    Close an open loop - mark it as completed.
    """
    scaffolding = load_scaffolding()
    if not scaffolding or 'open_loops' not in scaffolding:
        return None
    
    for loop in scaffolding['open_loops']:
        if loop.get('id') == loop_id_or_item or loop.get('item') == loop_id_or_item:
            loop['status'] = 'completed'
            loop['completed_date'] = datetime.now().strftime('%Y-%m-%d')
            save_scaffolding(scaffolding)
            return scaffolding
    
    return None


# ============================================================
# INTEGRATION WITH EXISTING INTENT DETECTION
# ============================================================

def enhanced_detect_query_intent(query_text, existing_intent):
    """
    Enhance existing intent detection with scaffolding awareness.
    Call this after the original detect_query_intent().
    """
    # Add scaffolding-specific intent flags
    existing_intent['needs_orientation'] = detect_orientation_need(query_text)
    existing_intent['tangent_check'] = detect_tangent(query_text)
    
    if existing_intent['needs_orientation']:
        existing_intent['patterns_matched'].append('scaffolding: orientation_need')
    
    if existing_intent['tangent_check'] and existing_intent['tangent_check'].get('is_tangent'):
        existing_intent['patterns_matched'].append('scaffolding: tangent_detected')
    
    return existing_intent


def build_scaffolding_enhanced_context(query_text, intent, existing_context):
    """
    Add scaffolding context to existing integrated context.
    Call this in build_integrated_context() after other integrations.
    """
    context_parts = [existing_context] if existing_context else []
    
    # Add scaffolding context if orientation is needed
    if intent.get('needs_orientation') or intent.get('is_next_action_query'):
        scaffolding_context = get_scaffolding_context(query_text)
        if scaffolding_context:
            context_parts.append(scaffolding_context)
            print("   🏗️  Added scaffolding context (orientation)")
    
    # Add tangent warning if detected
    tangent_info = intent.get('tangent_check', {})
    if tangent_info.get('is_tangent'):
        tangent_context = f"""
=== TANGENT ALERT ===
You're asking about: {tangent_info.get('tangent_idea', '')}
This was parked because: {tangent_info.get('why_parked', '')}
Current goal: {tangent_info.get('current_goal', '')}

Consider: Is this actually important right now, or should we stay on track?
====================="""
        context_parts.append(tangent_context)
        print("   ⚠️  Added tangent warning")
    
    return "\n\n".join(context_parts) if context_parts else ""


# ============================================================
# ORIENTATION RESPONSE HELPERS
# ============================================================

def format_orientation_response():
    """
    Generate a full orientation response for "where was I?" type queries.
    """
    scaffolding = load_scaffolding()
    if not scaffolding:
        return "I don't have scaffolding state yet. Let's establish where you are."
    
    active = scaffolding.get('active_context', {})
    completions = scaffolding.get('recent_completions', [])
    loops = scaffolding.get('open_loops', [])
    
    response_parts = []
    
    # Current position
    response_parts.append(f"**Current Position**: {active.get('structural_position', 'Unknown')}")
    response_parts.append(f"**Goal**: {active.get('phase_goal', 'Not defined')}")
    
    if active.get('position_summary'):
        response_parts.append(f"\n{active.get('position_summary')}")
    
    # Recent completion
    if completions:
        latest = completions[0]
        response_parts.append(f"\n**Just Completed**: {latest.get('what', '')}")
        response_parts.append(f"*{latest.get('permission', '')}*")
    
    # Open loops
    active_loops = [l for l in loops if l.get('status') != 'completed']
    if active_loops:
        response_parts.append("\n**Open Loops**:")
        for loop in active_loops[:3]:
            response_parts.append(f"- {loop.get('item', '')}")
    
    return "\n".join(response_parts)


# ============================================================
# EXAMPLE USAGE (for testing)
# ============================================================

if __name__ == "__main__":
    print("Testing scaffolding integration...")
    
    # Test loading
    scaffolding = load_scaffolding()
    if scaffolding:
        print(f"✅ Loaded scaffolding state")
        print(f"   Project: {scaffolding.get('active_context', {}).get('primary_project', 'Unknown')}")
        print(f"   Position: {scaffolding.get('active_context', {}).get('structural_position', 'Unknown')}")
    else:
        print("⚠️  No scaffolding state found")
    
    # Test orientation detection
    test_queries = [
        "Where was I?",
        "What should I work on?",
        "What's the Astris decay formula?",
        "Let's set up Mac FAITHH"  # This should trigger tangent detection
    ]
    
    print("\nTesting query detection:")
    for query in test_queries:
        needs_orientation = detect_orientation_need(query)
        tangent = detect_tangent(query)
        print(f"  '{query[:40]}...'")
        print(f"    Orientation: {needs_orientation}, Tangent: {tangent.get('is_tangent', False)}")
    
    print("\n✅ Scaffolding integration ready for backend!")
