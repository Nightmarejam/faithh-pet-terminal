#!/bin/bash
# Apply scaffolding integration to FAITHH backend v3.2
# This adds Layer 1: Position Awareness

echo "🏗️  Applying Scaffolding Integration to FAITHH Backend"
echo "======================================================="
echo ""

cd ~/ai-stack

# Backup current backend
echo "📦 Creating backup..."
cp faithh_professional_backend_fixed.py faithh_professional_backend_fixed.py.bak_pre_scaffolding
echo "   Backed up to: faithh_professional_backend_fixed.py.bak_pre_scaffolding"

# Test scaffolding integration module
echo ""
echo "🧪 Testing scaffolding integration module..."
python3 scaffolding_integration.py
if [ $? -ne 0 ]; then
    echo "❌ Scaffolding integration test failed!"
    exit 1
fi
echo "✅ Scaffolding module tests passed"

# Now patch the backend using Python for precision
echo ""
echo "🔧 Patching backend..."

python3 << 'PATCH_SCRIPT'
import re

# Read the current backend
with open('faithh_professional_backend_fixed.py', 'r') as f:
    content = f.read()

# ============================================================
# PATCH 1: Add scaffolding import and file path
# ============================================================

# Find the MEMORY_FILE line and add SCAFFOLDING_FILE after it
old_memory_section = '''MEMORY_FILE = Path.home() / "ai-stack/faithh_memory.json"
DECISIONS_LOG = Path.home() / "ai-stack/decisions_log.json"
PROJECT_STATES = Path.home() / "ai-stack/project_states.json"'''

new_memory_section = '''MEMORY_FILE = Path.home() / "ai-stack/faithh_memory.json"
DECISIONS_LOG = Path.home() / "ai-stack/decisions_log.json"
PROJECT_STATES = Path.home() / "ai-stack/project_states.json"
SCAFFOLDING_FILE = Path.home() / "ai-stack/scaffolding_state.json"'''

content = content.replace(old_memory_section, new_memory_section)

# ============================================================
# PATCH 2: Add load_scaffolding function after load_project_states
# ============================================================

old_load_states = '''def load_project_states():
    """Load project states"""
    return load_json_file(PROJECT_STATES)'''

new_load_states = '''def load_project_states():
    """Load project states"""
    return load_json_file(PROJECT_STATES)

def load_scaffolding():
    """Load scaffolding state for structural awareness"""
    return load_json_file(SCAFFOLDING_FILE)

def save_scaffolding(scaffolding):
    """Persist scaffolding state to disk"""
    try:
        scaffolding['meta']['last_updated'] = datetime.now().isoformat()
        with open(SCAFFOLDING_FILE, 'w') as f:
            json.dump(scaffolding, f, indent=2)
        print(f"🏗️  Scaffolding saved: {datetime.now().strftime('%H:%M:%S')}")
    except Exception as e:
        print(f"❌ Error saving scaffolding: {e}")'''

content = content.replace(old_load_states, new_load_states)

# ============================================================
# PATCH 3: Add scaffolding intent detection patterns
# ============================================================

# Find the existing intent dict initialization and add scaffolding flags
old_intent_init = '''    intent = {
        'is_self_query': False,
        'is_why_question': False,
        'is_next_action_query': False,
        'is_constella_query': False,
        'patterns_matched': []
    }'''

new_intent_init = '''    intent = {
        'is_self_query': False,
        'is_why_question': False,
        'is_next_action_query': False,
        'is_constella_query': False,
        'needs_orientation': False,
        'is_tangent': False,
        'patterns_matched': []
    }'''

content = content.replace(old_intent_init, new_intent_init)

# ============================================================
# PATCH 4: Add orientation pattern detection after constella detection
# ============================================================

old_constella_check = '''    # Pattern 4: Constella queries (domain-specific)
    constella_keywords = ['constella', 'astris', 'auctor', 'civic tome', 'penumbra',
                          'ucf', 'resonance gap', 'harmonic', 'celestial equilibrium']
    if any(kw in query_lower for kw in constella_keywords):
        intent['is_constella_query'] = True
    
    return intent'''

new_constella_check = '''    # Pattern 4: Constella queries (domain-specific)
    constella_keywords = ['constella', 'astris', 'auctor', 'civic tome', 'penumbra',
                          'ucf', 'resonance gap', 'harmonic', 'celestial equilibrium']
    if any(kw in query_lower for kw in constella_keywords):
        intent['is_constella_query'] = True
    
    # Pattern 5: Orientation queries (scaffolding - where am I?)
    orientation_patterns = [
        r'where (was i|did i leave off|am i)',
        r'what was i (working on|doing)',
        r'catch me up',
        r'bring me up to speed',
        r"what('s| is) (the )?(status|progress)",
        r"what('s| is| have i) (been )?(done|complete|finished)",
        r'am i on track'
    ]
    for pattern in orientation_patterns:
        if re.search(pattern, query_lower):
            intent['needs_orientation'] = True
            intent['patterns_matched'].append(f"orientation: {pattern}")
            break
    
    return intent'''

content = content.replace(old_constella_check, new_constella_check)

# ============================================================
# PATCH 5: Add get_scaffolding_context function after get_project_state_context
# ============================================================

# Find end of get_project_state_context and add scaffolding function
old_project_state_end = '''    context += "============================\\n"
    
    return context.strip()


def smart_rag_query'''

new_project_state_end = '''    context += "============================\\n"
    
    return context.strip()


def get_scaffolding_context(query_text=None):
    """
    Build orientation context from scaffolding state.
    This is the "You are HERE" function for persistent structural awareness.
    """
    scaffolding = load_scaffolding()
    if not scaffolding:
        return None
    
    context_parts = []
    
    # Active context - where you are right now
    active = scaffolding.get('active_context', {})
    if active:
        context_parts.append(f"""
=== CURRENT STRUCTURAL POSITION ===
Project: {active.get('primary_project', 'Unknown').upper()}
Position: {active.get('structural_position', 'Unknown')}
Goal: {active.get('phase_goal', 'Not defined')}

Summary: {active.get('position_summary', '')}
====================================""")
    
    # Recent completions - what's done (with permission to move on)
    completions = scaffolding.get('recent_completions', [])
    if completions:
        latest = completions[0]
        context_parts.append(f"""
=== RECENTLY COMPLETED ===
What: {latest.get('what', '')}
When: {latest.get('when', '')}
Significance: {latest.get('structural_significance', '')}
What remains: {latest.get('what_remains', '')}
Permission: {latest.get('permission', '')}
===========================""")
    
    # Open loops - what's in progress
    open_loops = scaffolding.get('open_loops', [])
    active_loops = [l for l in open_loops if l.get('status') != 'completed']
    if active_loops:
        context_parts.append("\\n=== OPEN LOOPS ===")
        for loop in active_loops[:3]:
            context_parts.append(f"• {loop.get('item', '')}")
            context_parts.append(f"  Why structural: {loop.get('why_structural', '')}")
            context_parts.append(f"  Status: {loop.get('status', 'unknown')}")
            if loop.get('suggested_action'):
                context_parts.append(f"  Suggested: {loop.get('suggested_action', '')}")
        context_parts.append("==================")
    
    # Parked tangents - check if query relates to a parked idea
    tangents = scaffolding.get('parked_tangents', [])
    if tangents and query_text:
        query_lower = query_text.lower()
        for tangent in tangents:
            tangent_words = [w for w in tangent.get('idea', '').lower().split() if len(w) > 4]
            if any(word in query_lower for word in tangent_words):
                context_parts.append(f"""
=== PARKED TANGENT DETECTED ===
You previously parked: "{tangent.get('idea', '')}"
Why parked: {tangent.get('why_parked', '')}
Revisit when: {tangent.get('revisit_when', '')}

This is noted but not your current structural priority. Consider if this is important right now or should stay parked.
================================""")
                break
    
    # Project milestones - show progression
    milestones = scaffolding.get('project_structural_milestones', {})
    primary_project = active.get('primary_project', '').lower()
    if primary_project in milestones:
        proj_milestones = milestones[primary_project]
        context_parts.append(f"""
=== {primary_project.upper()} MILESTONE PROGRESSION ===
Completed: {', '.join(proj_milestones.get('completed', [])[-3:])}
Current: {proj_milestones.get('current', 'Unknown')}
Next: {proj_milestones.get('next', 'Unknown')}
After that: {proj_milestones.get('after_that', 'Unknown')}
=============================================""")
    
    return "\\n".join(context_parts) if context_parts else None


def smart_rag_query'''

content = content.replace(old_project_state_end, new_project_state_end)

# ============================================================
# PATCH 6: Add scaffolding to build_integrated_context
# ============================================================

old_rag_section = '''    # Integration 4: RAG (if not a pure self-query)
    rag_results = []
    if use_rag and CHROMA_CONNECTED and not intent['is_self_query']:'''

new_rag_section = '''    # Integration 4: Scaffolding (structural orientation)
    if intent.get('needs_orientation') or intent.get('is_next_action_query'):
        scaffolding_context = get_scaffolding_context(query_text)
        if scaffolding_context:
            context_parts.append(scaffolding_context)
            print("   🏗️  Added scaffolding context (orientation)")
    
    # Integration 5: RAG (if not a pure self-query)
    rag_results = []
    if use_rag and CHROMA_CONNECTED and not intent['is_self_query']:'''

content = content.replace(old_rag_section, new_rag_section)

# ============================================================
# PATCH 7: Add scaffolding to status endpoint
# ============================================================

old_integration_status = '''    # Integration status
    services['integrations'] = {
        'memory': MEMORY_FILE.exists(),
        'decisions_log': DECISIONS_LOG.exists(),
        'project_states': PROJECT_STATES.exists()
    }'''

new_integration_status = '''    # Integration status
    services['integrations'] = {
        'memory': MEMORY_FILE.exists(),
        'decisions_log': DECISIONS_LOG.exists(),
        'project_states': PROJECT_STATES.exists(),
        'scaffolding': SCAFFOLDING_FILE.exists()
    }'''

content = content.replace(old_integration_status, new_integration_status)

# ============================================================
# PATCH 8: Update version string
# ============================================================

content = content.replace('v3.2-integrated', 'v3.3-scaffolding')
content = content.replace('FAITHH PROFESSIONAL BACKEND v3.2 - INTEGRATED', 'FAITHH PROFESSIONAL BACKEND v3.3 - SCAFFOLDING')

# ============================================================
# PATCH 9: Add scaffolding to startup message
# ============================================================

old_startup = '''    print(f"✅ Self-awareness boost (faithh_memory.json)")
    print(f"✅ Decision citation (decisions_log.json)")
    print(f"✅ Project state awareness (project_states.json)")
    print(f"✅ Smart intent detection")
    print(f"✅ Integrated context building")'''

new_startup = '''    print(f"✅ Self-awareness boost (faithh_memory.json)")
    print(f"✅ Decision citation (decisions_log.json)")
    print(f"✅ Project state awareness (project_states.json)")
    print(f"✅ Scaffolding awareness (scaffolding_state.json)")
    print(f"✅ Smart intent detection")
    print(f"✅ Integrated context building")'''

content = content.replace(old_startup, new_startup)

# ============================================================
# PATCH 10: Add scaffolding to health endpoint
# ============================================================

old_health_features = '''        'features': [
            'chat', 'rag', 'upload',
            'self_awareness_boost', 'decision_citation', 'project_state_awareness',
            'intent_detection', 'smart_context_building'
        ]'''

new_health_features = '''        'features': [
            'chat', 'rag', 'upload',
            'self_awareness_boost', 'decision_citation', 'project_state_awareness',
            'scaffolding_awareness', 'orientation_detection',
            'intent_detection', 'smart_context_building'
        ]'''

content = content.replace(old_health_features, new_health_features)

# Write the patched backend
with open('faithh_professional_backend_fixed.py', 'w') as f:
    f.write(content)

print("✅ Backend patched successfully!")
print("   Added: SCAFFOLDING_FILE path")
print("   Added: load_scaffolding() function")
print("   Added: save_scaffolding() function") 
print("   Added: needs_orientation intent flag")
print("   Added: orientation pattern detection")
print("   Added: get_scaffolding_context() function")
print("   Added: Scaffolding integration in build_integrated_context()")
print("   Added: Scaffolding to status endpoint")
print("   Updated: Version to v3.3-scaffolding")
PATCH_SCRIPT

if [ $? -ne 0 ]; then
    echo "❌ Backend patch failed!"
    echo "Restoring backup..."
    cp faithh_professional_backend_fixed.py.bak_pre_scaffolding faithh_professional_backend_fixed.py
    exit 1
fi

echo ""
echo "🔄 Restarting backend..."
./stop_backend.sh 2>/dev/null || pkill -f "faithh_professional_backend" 2>/dev/null
sleep 2
./restart_backend.sh 2>/dev/null || python faithh_professional_backend_fixed.py &

sleep 3

echo ""
echo "🧪 Testing scaffolding integration..."
curl -s http://localhost:5557/api/status | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    integrations = data.get('services', {}).get('integrations', {})
    scaffolding = integrations.get('scaffolding', False)
    version = data.get('version', 'unknown')
    print(f'   Version: {version}')
    print(f'   Scaffolding file detected: {scaffolding}')
    if scaffolding and 'scaffolding' in version:
        print('✅ Scaffolding integration successful!')
    else:
        print('⚠️  Scaffolding may not be fully integrated')
except Exception as e:
    print(f'❌ Error checking status: {e}')
"

echo ""
echo "======================================================="
echo "🏗️  SCAFFOLDING INTEGRATION COMPLETE"
echo "======================================================="
echo ""
echo "What's new in v3.3-scaffolding:"
echo "  • Position awareness - FAITHH knows where you are structurally"
echo "  • Completion recognition - Permission to move on when done"
echo "  • Open loops tracking - What's in progress"
echo "  • Parked tangents - Ideas noted but not current priority"
echo "  • Milestone progression - What's done → current → next"
echo ""
echo "Test queries to try:"
echo "  • 'Where was I?'"
echo "  • 'What should I work on?'"
echo "  • 'What's my progress?'"
echo "  • 'Am I on track?'"
echo ""
echo "Scaffolding state file: ~/ai-stack/scaffolding_state.json"
echo "======================================================="
