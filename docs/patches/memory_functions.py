
# ============================================================
# PERSISTENT MEMORY SYSTEM
# ============================================================

import json
from datetime import datetime

MEMORY_FILE = Path.home() / "ai-stack/faithh_memory.json"

def load_memory():
    """Load persistent memory from disk"""
    try:
        if MEMORY_FILE.exists():
            with open(MEMORY_FILE, 'r') as f:
                return json.load(f)
        else:
            print("⚠️  Memory file not found, using defaults")
            return {"user_profile": {"name": "User"}}
    except Exception as e:
        print(f"❌ Error loading memory: {e}")
        return {"user_profile": {"name": "User"}}

def save_memory(memory):
    """Persist memory to disk"""
    try:
        memory["last_updated"] = datetime.now().isoformat()
        with open(MEMORY_FILE, 'w') as f:
            json.dump(memory, f, indent=2)
        print(f"💾 Memory saved: {datetime.now().strftime('%H:%M:%S')}")
    except Exception as e:
        print(f"❌ Error saving memory: {e}")

def update_recent_topics(memory, query, response_preview):
    """Add conversation to recent topics"""
    if "conversation_context" not in memory:
        memory["conversation_context"] = {"recent_topics": []}
    
    if "recent_topics" not in memory["conversation_context"]:
        memory["conversation_context"]["recent_topics"] = []
    
    # Add new topic
    topic = {
        "timestamp": datetime.now().isoformat(),
        "query": query[:100],
        "response_preview": response_preview[:100],
        "date": datetime.now().strftime("%Y-%m-%d")
    }
    
    recent = memory["conversation_context"]["recent_topics"]
    recent.insert(0, topic)
    
    # Keep only last 50 topics
    memory["conversation_context"]["recent_topics"] = recent[:50]
    
    return memory

def format_memory_context(memory):
    """Format memory into context string for system prompt"""
    
    context_parts = []
    
    # User profile
    if "user_profile" in memory:
        profile = memory["user_profile"]
        context_parts.append(f"USER: {profile.get('name', 'User')}")
        if "role" in profile:
            context_parts.append(f"ROLE: {profile['role']}")
    
    # Current project focus
    if "ongoing_projects" in memory and "FAITHH" in memory["ongoing_projects"]:
        faithh = memory["ongoing_projects"]["FAITHH"]
        context_parts.append(f"\nCURRENT PROJECT: {faithh.get('description', 'FAITHH AI system')}")
        if "current_focus" in faithh:
            context_parts.append("CURRENT FOCUS:")
            for focus in faithh["current_focus"][:3]:
                context_parts.append(f"  - {focus}")
    
    # Recent conversation topics
    if "conversation_context" in memory and "recent_topics" in memory["conversation_context"]:
        recent = memory["conversation_context"]["recent_topics"][:5]
        if recent:
            context_parts.append("\nRECENT DISCUSSIONS:")
            for topic in recent:
                date = topic.get("date", "unknown")
                query = topic.get("query", "")[:60]
                context_parts.append(f"  [{date}] {query}...")
    
    # Unresolved issues
    if "conversation_context" in memory and "unresolved_issues" in memory["conversation_context"]:
        issues = memory["conversation_context"]["unresolved_issues"]
        if issues:
            context_parts.append("\nUNRESOLVED ISSUES:")
            for issue in issues[:3]:
                context_parts.append(f"  - {issue.get('issue', 'Unknown')}")
    
    return "\n".join(context_parts)

def get_faithh_personality():
    """Return FAITHH's core personality prompt"""
    return """You are FAITHH (Friendly AI Teaching & Helping Hub), a personal AI assistant inspired by the NetNavi characters from MegaMan Battle Network.

PERSONALITY TRAITS:
- Encouraging and helpful, like a trusted companion
- Technical but accessible - explain complex topics clearly
- Proactive in suggesting next steps
- Remember past conversations and maintain continuity
- Enthusiastic about progress and milestones

COMMUNICATION STYLE:
- Reference past discussions naturally (use context provided)
- Be specific with technical details when needed
- Acknowledge Jonathan's ADHD - provide clear structure
- Celebrate wins and progress
- When uncertain, say so and offer to investigate

CORE KNOWLEDGE:
You have access to a comprehensive RAG system with 91,000+ documents including:
- FAITHH project documentation and code
- Past conversation history (as semantic chunks)
- Audio production workflows and tools
- AI/ML development context

Always check the provided context first before answering. If context is relevant, reference it naturally."""

