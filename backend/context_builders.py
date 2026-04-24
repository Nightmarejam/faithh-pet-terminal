"""
FAITHH Backend — Context Builders
Functions that assemble context from various sources (memory, decisions, projects, scaffolding).
Extracted from faithh_professional_backend_fixed.py for modularity.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from backend.data_loaders import (
    load_memory, load_decisions, load_project_states, load_scaffolding
)


def get_self_awareness_context():
    """Extract self-awareness section from memory"""
    memory = load_memory()
    if 'self_awareness' in memory:
        sa = memory['self_awareness']
        context = f"""
=== FAITHH SELF-AWARENESS ===
Identity: {sa.get('identity', 'FAITHH')}
Purpose: {sa.get('purpose', 'AI assistant')}
What I am: {sa.get('what_i_am', '')}
What I am NOT: {sa.get('what_i_am_not', '')}
Hero workflow: {sa.get('hero_workflow', '')}
Current capability: {sa.get('current_capability', '')}
Target capability: {sa.get('target_capability', '')}
==============================
"""
        return context.strip()
    return None


def get_constella_awareness_context():
    """Extract Constella awareness section from memory"""
    memory = load_memory()
    if 'constella_awareness' in memory:
        ca = memory['constella_awareness']
        context = f"""
=== CONSTELLA FRAMEWORK AWARENESS ===
What it is: {ca.get('what_it_is', '')}
What it is NOT: {ca.get('what_it_is_NOT', '')}
Core philosophy: {ca.get('core_philosophy', '')}

Key Components:
  Tokens:
    - Astris: {ca.get('key_components', {}).get('tokens', {}).get('Astris', '')}
    - Auctor: {ca.get('key_components', {}).get('tokens', {}).get('Auctor', '')}
  
  Governance:
    - Penumbra Accord: {ca.get('key_components', {}).get('governance_mechanisms', {}).get('Penumbra_Accord', '')}
    - UCF: {ca.get('key_components', {}).get('governance_mechanisms', {}).get('UCF', '')}
    - Civic Tome: {ca.get('key_components', {}).get('governance_mechanisms', {}).get('Civic_Tome', '')}
  
  Evidence Framework: {ca.get('key_components', {}).get('evidence_framework', '')}

Connection to FAITHH: {ca.get('connection_to_faithh', '')}
Current Status: {ca.get('current_status', '')}

CRITICAL: {ca.get('when_asked_about_constella', '')}
======================================
"""
        return context.strip()
    return None


def search_decisions_log(query_text):
    """Search decisions log for relevant decisions"""
    decisions = load_decisions()
    if not decisions or 'decisions' not in decisions:
        return None
    
    query_lower = query_text.lower()
    relevant_decisions = []
    
    for decision in decisions['decisions']:
        decision_text = f"{decision.get('decision', '')} {decision.get('rationale', '')}".lower()
        if any(word in decision_text for word in query_lower.split() if len(word) > 3):
            relevant_decisions.append(decision)
    
    if not relevant_decisions:
        return None
    
    context = "\n=== RELEVANT DECISIONS ===\n"
    for dec in relevant_decisions[:3]:
        context += f"\nDecision: {dec.get('decision', '')}\n"
        context += f"Date: {dec.get('date', '')}\n"
        context += f"Rationale: {dec.get('rationale', '')}\n"
        if 'alternatives_considered' in dec:
            context += "Alternatives considered:\n"
            for alt in dec['alternatives_considered']:
                context += f"  - {alt.get('option', '')}: Rejected because {alt.get('rejected_because', '')}\n"
        context += f"Impact: {dec.get('impact', '')}\n"
        context += "---\n"
    context += "=========================\n"
    
    return context.strip()


def get_project_state_context(project_name=None):
    """Get current state for a project or all projects"""
    states = load_project_states()
    if not states or 'projects' not in states:
        return None
    
    projects = states['projects']
    
    def find_project(name):
        name_lower = name.lower()
        for key, proj in projects.items():
            if key.lower() == name_lower or name_lower in proj.get('name', '').lower():
                return proj
        return None
    
    if project_name:
        project = find_project(project_name)
        if project:
            context = f"""
=== {project.get('name', project_name)} STATE ===
Phase: {project.get('phase', 'Unknown')}
Status: {project.get('phase_status', project.get('status', 'Unknown'))}
Summary: {project.get('summary', '')}

Next Steps:
"""
            for step in project.get('next_steps', [])[:5]:
                context += f"  - {step}\n"
            
            recent = project.get('recent_work', project.get('recent_completions', []))
            if recent:
                context += "\nRecent Work:\n"
                for item in recent[:3]:
                    context += f"  - {item}\n"
            
            context += "================================\n"
            return context.strip()
    
    # Return overview of all projects
    last_updated = states.get('last_updated', 'unknown')
    context = f"\n=== ALL PROJECTS OVERVIEW (as of {last_updated}) ===\n"
    for proj_key, project in projects.items():
        context += f"\n{project.get('name', proj_key)}:\n"
        context += f"  Phase: {project.get('phase', 'Unknown')}\n"
        context += f"  Status: {project.get('phase_status', project.get('status', 'Unknown'))}\n"
        next_steps = project.get('next_steps', [])
        if next_steps:
            context += f"  Top priority: {next_steps[0]}\n"
    context += "============================\n"
    
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
    
    active = scaffolding.get('active_context', {})
    if active:
        context_parts.append(f"""
=== CURRENT STRUCTURAL POSITION ===
Project: {active.get('primary_project', 'Unknown').upper()}
Position: {active.get('structural_position', 'Unknown')}
Goal: {active.get('phase_goal', 'Not defined')}

Summary: {active.get('position_summary', '')}
===================================""")
    
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
    
    open_loops = scaffolding.get('open_loops', [])
    active_loops = [l for l in open_loops if l.get('status') != 'completed']
    if active_loops:
        context_parts.append("\n=== OPEN LOOPS ===")
        for loop in active_loops[:3]:
            context_parts.append(f"• {loop.get('item', '')}")
            context_parts.append(f"  Why structural: {loop.get('why_structural', '')}")
            context_parts.append(f"  Status: {loop.get('status', 'unknown')}")
            if loop.get('suggested_action'):
                context_parts.append(f"  Suggested: {loop.get('suggested_action', '')}")
        context_parts.append("==================")
    
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
    
    return "\n".join(context_parts) if context_parts else None


def update_recent_topics(memory, query, response_preview):
    """Add conversation to recent topics"""
    if "conversation_context" not in memory:
        memory["conversation_context"] = {"recent_topics": []}
    
    if "recent_topics" not in memory["conversation_context"]:
        memory["conversation_context"]["recent_topics"] = []
    
    topic = {
        "timestamp": datetime.now().isoformat(),
        "query": query[:100],
        "response_preview": response_preview[:100],
        "date": datetime.now().strftime("%Y-%m-%d")
    }
    
    recent = memory["conversation_context"]["recent_topics"]
    recent.insert(0, topic)
    memory["conversation_context"]["recent_topics"] = recent[:50]
    
    return memory


def format_memory_context(memory):
    """Format memory into context string"""
    context_parts = []
    
    if "user_profile" in memory:
        profile = memory["user_profile"]
        context_parts.append(f"USER: {profile.get('name', 'User')}")
        if "role" in profile:
            context_parts.append(f"ROLE: {profile['role']}")
    
    if "ongoing_projects" in memory and "FAITHH" in memory["ongoing_projects"]:
        faithh = memory["ongoing_projects"]["FAITHH"]
        context_parts.append(f"\nCURRENT PROJECT: {faithh.get('description', 'FAITHH AI system')}")
        if "current_focus" in faithh:
            context_parts.append("CURRENT FOCUS:")
            for focus in faithh["current_focus"][:3]:
                context_parts.append(f"  - {focus}")
    
    if "conversation_context" in memory and "recent_topics" in memory["conversation_context"]:
        recent = memory["conversation_context"]["recent_topics"][:5]
        if recent:
            context_parts.append("\nRECENT DISCUSSIONS:")
            for topic in recent:
                date = topic.get("date", "unknown")
                query = topic.get("query", "")[:60]
                context_parts.append(f"  [{date}] {query}...")
    
    return "\n".join(context_parts)


def _get_recent_git_changes(base_dir):
    """
    Get recent git commit history so FAITHH can accurately answer
    'what changed recently?' questions instead of fabricating activity.
    """
    import subprocess
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "--no-decorate", "-10"],
            cwd=base_dir,
            capture_output=True, text=True, timeout=5
        )
        if result.returncode != 0 or not result.stdout.strip():
            return None

        lines = ["=== RECENT CHANGES (git log) ==="]
        for line in result.stdout.strip().split("\n"):
            lines.append(f"  {line}")

        # Also get files changed in the most recent commit
        diff_result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD~1", "HEAD"],
            cwd=base_dir,
            capture_output=True, text=True, timeout=5
        )
        if diff_result.returncode == 0 and diff_result.stdout.strip():
            changed = diff_result.stdout.strip().split("\n")
            lines.append(f"Files changed in latest commit: {', '.join(changed[:15])}")

        lines.append("When asked about recent changes, ONLY cite commits listed above. Do NOT invent commit descriptions or changes.")
        return "\n".join(lines)
    except Exception:
        return None


def get_project_structure_snapshot():
    """
    Generate a live snapshot of the current project structure.
    Injected into every prompt so FAITHH always knows what files exist RIGHT NOW.
    Prevents hallucinating references to deleted/nonexistent files.
    Lists files 2 levels deep so the model can see actual file names in subdirectories.
    """
    import os
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ALLOWED_EXTS = {'.py', '.html', '.md', '.json', '.yaml', '.yml', '.sh', '.txt', '.conf'}

    # Key files at root
    root_files = []
    for f in sorted(os.listdir(base)):
        full = os.path.join(base, f)
        if os.path.isfile(full) and not f.startswith('.'):
            ext = os.path.splitext(f)[1]
            if ext in ALLOWED_EXTS:
                root_files.append(f)

    # Key directories — list files up to 2 levels deep
    dir_summaries = {}
    for d in ['backend', 'scripts', 'docs', 'ml', 'tests']:
        dpath = os.path.join(base, d)
        if not os.path.isdir(dpath):
            continue
        items = []
        for item in sorted(os.listdir(dpath)):
            if item.startswith('.') or item.startswith('__'):
                continue
            item_path = os.path.join(dpath, item)
            if os.path.isfile(item_path):
                items.append(item)
            elif os.path.isdir(item_path) and item != 'archive':
                # List files inside subdirectory (level 2)
                sub_files = []
                try:
                    for sf in sorted(os.listdir(item_path)):
                        if os.path.isfile(os.path.join(item_path, sf)) and not sf.startswith('.'):
                            sub_files.append(sf)
                except OSError:
                    pass
                if sub_files:
                    items.append(f"{item}/ [{', '.join(sub_files[:10])}]")
                else:
                    items.append(f"{item}/")
        dir_summaries[d] = items[:20]

    # Build concise snapshot — git log FIRST (primacy bias: LLMs attend more to the start)
    lines = []

    # Git log at the top so the model sees recent changes first
    recent = _get_recent_git_changes(base)
    if recent:
        lines.append(recent)
        lines.append("")

    lines.append("=== CURRENT PROJECT STRUCTURE (LIVE) ===")
    lines.append("⚠️ GROUNDING RULE: Only reference files listed below. If not listed, it does NOT exist.")
    lines.append("")
    lines.append("Root: " + ", ".join(root_files))
    for d, items in dir_summaries.items():
        lines.append(f"{d}/: " + ", ".join(items))
    lines.append("============================================")

    return "\n".join(lines)


def get_faithh_personality():
    """Return FAITHH's enhanced personality"""
    return """You are FAITHH (Friendly AI Teaching & Helping Hub), Jonathan's personal AI assistant.

=== ⚠️ ACCURACY RULES — READ FIRST, OBEY ALWAYS ===
These rules override ALL other instructions. Violating them produces harmful misinformation.

1. RECENT CHANGES: When asked "what changed recently" or "last update", look for the "RECENT CHANGES (git log)" section in your context. It lists actual git commits with their messages and files changed. Quote those commits directly. If the commits don't match what the user expects (e.g., they ask about RAG but the commits are about documentation), be honest: describe what the commits ACTUALLY say. Never invent commits, sprints, or changes that aren't in the git log.

2. FILE REFERENCES: Only mention files listed in the CURRENT PROJECT STRUCTURE snapshot. The snapshot lists every relevant file — if a file isn't there, it doesn't exist.

3. NEVER FABRICATE: Do not invent feature names, metrics, scores, config entries, decision log entries, test results, or descriptions of work that was done. If you don't have specific evidence, say so honestly.

4. ACCURACY > COMPLETENESS: A short, accurate answer is always better than a long, fabricated one. Say "I'm not sure about the specifics" rather than making something up.

5. WHAT "RECENTLY CHANGED" MEANS: The git log shows exact commit messages and files changed. Quote those directly. Do NOT describe what you think might have been done to a file — only describe what the commit messages explicitly say.

=== CORE IDENTITY ===
Inspired by: MegaMan Battle Network NetNavi companions
Role: Personal AI assistant and thought partner
Style: Encouraging friend + Technical expert

=== PERSONALITY TRAITS ===
🎯 Encouraging: Celebrate progress, acknowledge challenges
🔧 Technical: Deep expertise, but explain clearly
🚀 Proactive: Suggest next steps, anticipate needs
🧠 Remembering: Use context from your chips actively
✨ Enthusiastic: Show genuine interest in Jonathan's work

=== HOW TO USE CONTEXT PROVIDED ===
1. You are given context from multiple sources:
   - Project structure + git log (what files exist and what recently changed)
   - Self-awareness section (when asked about yourself)
   - Decisions log (when asked "why" questions)
   - Project states (when asked about next steps)
   - Knowledge base (RAG from conversation history)
   
2. When context is provided, integrate it naturally:
   - Don't say "According to the context..." — just answer
   - Be specific and cite actual decisions/rationale when available
   - BUT: never embellish or add details beyond what the context provides
   
3. When answering about recent work:
   - Check the git log FIRST — it is the authoritative source
   - Quote commit messages directly rather than paraphrasing
   - List the actual files changed, not guesses about what might have changed

=== COMMUNICATION STYLE ===
✅ DO:
- Be specific: cite file names from the structure snapshot
- Be honest: "Based on the last commit..." or "I can see from the git log..."
- Celebrate real progress based on actual commit history
- Connect past conversations to current questions when RAG provides evidence

❌ DON'T:
- Invent descriptions of what was "recently done" to files
- Fabricate sprint names, entry numbers, or metric values
- Describe code changes you cannot verify from context
- Add "(just updated)" annotations unless the git log confirms it
- Claim ignorance when context IS provided

=== SPECIAL BEHAVIORS ===
When asked about yourself (FAITHH):
- Reference your purpose clearly
- Be honest about current capabilities vs target

When asked "why" questions:
- Cite actual documented decisions if available
- Explain the rationale behind choices

When asked "what's next":
- Reference current project phase from scaffolding/project states
- Suggest next steps based on current state

You are Jonathan's long-term AI companion who grows through each interaction. Your value comes from being TRUSTWORTHY and ACCURATE, not from appearing to know everything."""


def get_system_fingerprint_context(include_full=False):
    """
    Load and format system fingerprint for LLM context injection.
    
    Args:
        include_full: If True, include full static fingerprint. If False, just dynamic state.
    
    Returns:
        Formatted fingerprint context string for prompt injection.
    """
    base_dir = Path(__file__).parent.parent
    fingerprint_state_path = base_dir / "fingerprint_state.json"
    fingerprint_static_path = base_dir / "SYSTEM_FINGERPRINT.md"
    
    context_parts = []
    
    # Load dynamic state
    dynamic_state = None
    if fingerprint_state_path.exists():
        try:
            with open(fingerprint_state_path, 'r') as f:
                dynamic_state = json.load(f)
        except Exception:
            pass
    
    if dynamic_state:
        # Build concise state summary
        health = dynamic_state.get("health", {})
        backend_status = health.get("backend", {}).get("status", "unknown")
        chromadb_docs = health.get("backend", {}).get("chromadb_docs", 0)
        ollama_models = health.get("ollama", {}).get("models", [])
        
        active_model = dynamic_state.get("active_model", {})
        default_model = active_model.get("default", "unknown")
        reasoning_model = active_model.get("reasoning", "unknown")
        
        projects = dynamic_state.get("projects", {}).get("projects", {})
        project_summary = ", ".join([
            f"{p.get('name', k)}: {p.get('status', 'unknown')}"
            for k, p in list(projects.items())[:3]
        ])
        
        open_loops = dynamic_state.get("open_loops", [])
        current_focus = next((l for l in open_loops if l.get("id") == "current_focus"), None)
        
        context_parts.append(f"""
=== SYSTEM FINGERPRINT (Live State) ===
Generated: {dynamic_state.get('generated_at', 'unknown')}
Overall Status: {dynamic_state.get('overall_status', 'unknown')}

Health:
  Backend: {backend_status} (ChromaDB: {chromadb_docs} docs)
  Ollama Models: {', '.join(ollama_models[:3])}

Active Models:
  Default: {default_model}
  Reasoning: {reasoning_model}

Projects: {project_summary}
""")
        
        if current_focus:
            context_parts.append(f"Current Focus: {current_focus.get('description', '')[:100]}")
        
        context_parts.append("========================================")
    
    # Optionally include static fingerprint (truncated)
    if include_full and fingerprint_static_path.exists():
        try:
            with open(fingerprint_static_path, 'r') as f:
                static_content = f.read()
            # Include key sections only (first 2000 chars)
            context_parts.append("\n=== SYSTEM IDENTITY (from SYSTEM_FINGERPRINT.md) ===")
            context_parts.append(static_content[:2000])
            context_parts.append("... [truncated for context window]")
        except Exception:
            pass
    
    return "\n".join(context_parts) if context_parts else None


def refresh_fingerprint_state():
    """
    Regenerate fingerprint_state.json by calling the generator script.
    Called periodically or on-demand to keep state fresh.
    """
    import subprocess
    base_dir = Path(__file__).parent.parent
    script_path = base_dir / "scripts" / "generate_fingerprint.py"
    
    if not script_path.exists():
        return False
    
    try:
        result = subprocess.run(
            ["python3", str(script_path)],
            cwd=str(base_dir),
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode == 0
    except Exception:
        return False
