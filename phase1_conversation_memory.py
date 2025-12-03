#!/usr/bin/env python3
"""
PHASE 1: CONVERSATION MEMORY CODE
Complete implementation for session-based multi-turn conversations

This file contains all the code needed to add conversation memory to FAITHH.
Integrate into faithh_professional_backend_fixed.py following the guide.
"""

# ============================================================
# SECTION 1: Conversation Memory Data Structures & Functions
# Add after: CURRENT_MODEL = {"name": "unknown", ...}
# ============================================================

conversation_sessions = {}
SESSION_TIMEOUT = 3600  # 1 hour in seconds

def cleanup_old_sessions():
    """Remove sessions older than timeout"""
    from datetime import datetime
    now = datetime.now()
    to_remove = []
    for session_id, session in conversation_sessions.items():
        last_activity = datetime.fromisoformat(session["last_activity"])
        if (now - last_activity).total_seconds() > SESSION_TIMEOUT:
            to_remove.append(session_id)
    
    for session_id in to_remove:
        del conversation_sessions[session_id]
        print(f"🧹 Cleaned up session: {session_id}")

def get_or_create_session(session_id):
    """Get existing session or create new one"""
    from datetime import datetime
    if not session_id:
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    if session_id not in conversation_sessions:
        conversation_sessions[session_id] = {
            "started": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat(),
            "history": []
        }
        print(f"🆕 Created session: {session_id}")
    else:
        conversation_sessions[session_id]["last_activity"] = datetime.now().isoformat()
    
    # Cleanup old sessions periodically
    if len(conversation_sessions) > 50:
        cleanup_old_sessions()
    
    return session_id

def add_to_conversation_history(session_id, user_msg, assistant_msg, intent=None):
    """Add exchange to session history"""
    from datetime import datetime
    if session_id not in conversation_sessions:
        return
    
    conversation_sessions[session_id]["history"].append({
        "timestamp": datetime.now().isoformat(),
        "user": user_msg,
        "assistant": assistant_msg,
        "intent": intent or {}
    })
    
    # Keep only last 10 exchanges (configurable)
    if len(conversation_sessions[session_id]["history"]) > 10:
        conversation_sessions[session_id]["history"] = conversation_sessions[session_id]["history"][-10:]

def format_conversation_history(history, last_n=5):
    """Format conversation history for context"""
    if not history:
        return None
    
    recent = history[-last_n:]
    formatted = []
    
    for exchange in recent:
        formatted.append(f"User: {exchange['user']}")
        # Truncate long responses but keep enough for context
        assistant_text = exchange['assistant']
        if len(assistant_text) > 500:
            assistant_text = assistant_text[:500] + "..."
        formatted.append(f"Assistant: {assistant_text}")
        formatted.append("")
    
    return "\n".join(formatted)


# ============================================================
# SECTION 2: Modified build_integrated_context
# This REPLACES your existing build_integrated_context function
# ============================================================

def build_integrated_context(query_text, intent, use_rag=True, session_id=None):
    """
    Build context from all available sources based on query intent
    NOW WITH CONVERSATION MEMORY! (Phase 1)
    """
    context_parts = []
    
    # Integration 0: Conversation History (NEW - PHASE 1!)
    if session_id and session_id in conversation_sessions:
        history = conversation_sessions[session_id]["history"]
        if history:
            history_text = format_conversation_history(history, last_n=5)
            if history_text:
                context_parts.append(f"""
=== RECENT CONVERSATION ===
{history_text}
============================
""")
                print(f"   💬 Added conversation history ({len(history)} exchanges)")
    
    # Integration 1: Self-Awareness Boost
    if intent['is_self_query']:
        self_context = get_self_awareness_context()
        if self_context:
            context_parts.append(self_context)
            print("   ✅ Added self-awareness context")
    
    # Integration 1b: Constella Awareness Boost
    if intent['is_constella_query']:
        constella_context = get_constella_awareness_context()
        if constella_context:
            context_parts.append(constella_context)
            print("   ✅ Added Constella awareness context")
    
    # Integration 2: Decision Citation
    if intent['is_why_question']:
        decisions_context = search_decisions_log(query_text)
        if decisions_context:
            context_parts.append(decisions_context)
            print("   ✅ Added decisions log context")
    
    # Integration 3: Project State Awareness
    if intent['is_next_action_query']:
        # Try to identify which project from query
        project_name = None
        if 'faithh' in query_text.lower():
            project_name = 'faithh'
        elif 'constella' in query_text.lower():
            project_name = 'constella'
        
        state_context = get_project_state_context(project_name)
        if state_context:
            context_parts.append(state_context)
            print("   ✅ Added project state context")
    
    # Integration 4: Scaffolding (structural orientation)
    if intent.get('needs_orientation') or intent.get('is_next_action_query'):
        scaffolding_context = get_scaffolding_context(query_text)
        if scaffolding_context:
            context_parts.append(scaffolding_context)
            print("   🏗️  Added scaffolding context (orientation)")
    
    # Integration 5: RAG (if not a pure self-query)
    rag_results = []
    if use_rag and CHROMA_CONNECTED and not intent['is_self_query']:
        # Skip RAG for pure orientation queries - scaffolding has the answer
        if intent.get('needs_orientation') and not intent.get('is_constella_query'):
            print("   ⭐ Skipping RAG for orientation query - using scaffolding")
        else:
            try:
                results = smart_rag_query(query_text, n_results=5, intent=intent)
                
                if results and results['documents'] and results['documents'][0]:
                    rag_context = "\n=== KNOWLEDGE BASE ===\n"
                    for i, doc in enumerate(results['documents'][0][:3]):
                        rag_context += f"{i+1}. {doc[:1000]}...\n\n"
                        rag_results.append(doc[:500])
                    rag_context += "=====================\n"
                    context_parts.append(rag_context.strip())
                    print(f"   ✅ Added RAG context ({len(results['documents'][0])} results)")
            except Exception as e:
                print(f"   ⚠️  RAG query failed: {e}")
    
    # Combine all context
    full_context = "\n\n".join(context_parts) if context_parts else ""
    
    return full_context, rag_results


# ============================================================
# SECTION 3: Modified /api/chat endpoint
# Add these changes to your existing chat() function
# ============================================================

# CHANGES TO MAKE IN chat() FUNCTION:

# 1. After: use_rag = data.get('use_rag', True)
#    ADD:
#        session_id = data.get('session_id', None)
#        session_id = get_or_create_session(session_id)

# 2. After: print(f"📨 Query: {message[:80]}...")
#    ADD:
#        print(f"💬 Session: {session_id}")

# 3. Change this line:
#    OLD: context, rag_results = build_integrated_context(message, intent, use_rag)
#    NEW: context, rag_results = build_integrated_context(message, intent, use_rag, session_id)

# 4. Before EACH return jsonify({...}), ADD:
#        add_to_conversation_history(session_id, message, assistant_response, intent)
#    Where assistant_response is:
#    - response.text (for Gemini)
#    - result.get('response', '') (for Ollama)

# 5. In EACH return jsonify({...}), ADD these fields:
#        'session_id': session_id,
#        'conversation_depth': len(conversation_sessions.get(session_id, {}).get('history', []))


# ============================================================
# SECTION 4: New Session Management Endpoints
# Add these before: if __name__ == '__main__':
# ============================================================

@app.route('/api/session/new', methods=['POST'])
def new_session():
    """Create a new conversation session"""
    session_id = get_or_create_session(None)
    return jsonify({
        'success': True,
        'session_id': session_id,
        'message': 'New conversation session created'
    })

@app.route('/api/session/<session_id>', methods=['GET'])
def get_session(session_id):
    """Get session history"""
    if session_id not in conversation_sessions:
        return jsonify({
            'success': False,
            'error': 'Session not found'
        }), 404
    
    session = conversation_sessions[session_id]
    return jsonify({
        'success': True,
        'session_id': session_id,
        'started': session['started'],
        'last_activity': session['last_activity'],
        'exchanges': len(session['history']),
        'history': session['history']
    })

@app.route('/api/session/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    """Delete a conversation session"""
    if session_id in conversation_sessions:
        del conversation_sessions[session_id]
        return jsonify({
            'success': True,
            'message': f'Session {session_id} deleted'
        })
    return jsonify({
        'success': False,
        'error': 'Session not found'
    }), 404

@app.route('/api/sessions', methods=['GET'])
def list_sessions():
    """List all active sessions"""
    sessions_info = []
    for sid, session in conversation_sessions.items():
        sessions_info.append({
            'session_id': sid,
            'started': session['started'],
            'last_activity': session['last_activity'],
            'exchanges': len(session['history'])
        })
    
    return jsonify({
        'success': True,
        'count': len(sessions_info),
        'sessions': sessions_info
    })
