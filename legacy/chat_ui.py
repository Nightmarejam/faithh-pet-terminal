#!/usr/bin/env python3
"""
FAITHH Streamlit Chat UI
Beautiful chat interface with RAG + Tools
"""
import streamlit as st
import requests
import json
from datetime import datetime
from typing import Dict, Any

# Page configuration
st.set_page_config(
    page_title="FAITHH Chat",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .source-card {
        background: #f0f2f6;
        padding: 0.5rem;
        border-radius: 0.3rem;
        margin: 0.3rem 0;
    }
    .tool-badge {
        background: #4CAF50;
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 0.3rem;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

# API Configuration
API_URL = "http://localhost:5556"

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'api_status' not in st.session_state:
    st.session_state.api_status = None


# Helper functions
def check_api_status():
    """Check if API is available"""
    try:
        response = requests.get(f"{API_URL}/api/status", timeout=2)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def send_message(message: str, use_rag: bool, use_tools: bool) -> Dict[str, Any]:
    """Send message to unified API"""
    try:
        response = requests.post(
            f"{API_URL}/api/chat",
            json={
                'message': message,
                'use_rag': use_rag,
                'use_tools': use_tools
            },
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
        return {'error': f'API error: {response.status_code}'}
    except Exception as e:
        return {'error': str(e)}

def get_rag_stats():
    """Get RAG database stats"""
    try:
        response = requests.get(f"{API_URL}/api/rag/stats", timeout=2)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

# ============= SIDEBAR =============

with st.sidebar:
    st.title("⚙️ Settings")
    
    # Check API status
    status = check_api_status()
    if status:
        st.success("✅ API Connected")
        st.session_state.api_status = status
        
        # Show services status
        with st.expander("📊 Services", expanded=False):
            services = status.get('services', {})
            for service, state in services.items():
                icon = "✅" if state == "online" else "❌"
                st.write(f"{icon} {service.title()}: {state}")
        
        # RAG Stats
        rag_stats = get_rag_stats()
        if rag_stats and 'document_count' in rag_stats:
            st.metric("📚 RAG Documents", f"{rag_stats['document_count']:,}")
    else:
        st.error("❌ API Offline")
        st.caption(f"Make sure API is running on {API_URL}")
    
    st.divider()
    
    # Settings
    st.subheader("Chat Settings")
    use_rag = st.toggle("Enable RAG", value=True, help="Auto-search documents")
    use_tools = st.toggle("Enable Tools", value=True, help="Allow tool execution")
    
    # Show auto-detection
    if use_rag:
        st.caption("🔍 RAG will auto-activate for relevant queries")
    if use_tools:
        st.caption("🔧 Tools will be suggested when needed")
    
    st.divider()
    
    # Stats
    st.subheader("📈 Session Stats")
    st.metric("Messages", len(st.session_state.messages))
    
    # Clear chat
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ============= MAIN CHAT INTERFACE =============

st.title("💬 FAITHH Chat")
st.caption("AI Assistant with RAG + Tools | Battle Chip System")

# Display chat messages
for message in st.session_state.messages:
    role = message["role"]
    
    with st.chat_message(role):
        # Show message content
        st.markdown(message["content"])
        
        # Show RAG sources if present
        if message.get("rag_sources"):
            with st.expander(f"📚 {len(message['rag_sources'])} Sources Used", expanded=False):
                for i, source in enumerate(message['rag_sources'], 1):
                    st.markdown(f"""
                    <div class="source-card">
                        <strong>Source {i}</strong> (Score: {source.get('score', 0):.2f})<br/>
                        {source['content'][:200]}...
                    </div>
                    """, unsafe_allow_html=True)
        
        # Show tool usage if present
        if message.get("tool_results"):
            st.markdown("🔧 **Tools:** " + ", ".join(message['tool_results']))


# Chat input
if prompt := st.chat_input("Ask anything... (RAG will auto-activate for memory queries)"):
    # Check API availability
    if not st.session_state.api_status:
        st.error("⚠️ API is offline. Please start the API server first.")
        st.code("cd ~/ai-stack && source venv/bin/activate && python3 faithh_unified_api.py")
        st.stop()
    
    # Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
        "timestamp": datetime.now().isoformat()
    })
    
    # Display user message immediately
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response_data = send_message(prompt, use_rag, use_tools)
            
            if 'error' in response_data:
                st.error(f"❌ Error: {response_data['error']}")
            else:
                # Display response
                st.markdown(response_data.get('response', 'No response'))
                
                # Show RAG usage
                if response_data.get('used_rag') and response_data.get('rag_sources'):
                    with st.expander(f"📚 {len(response_data['rag_sources'])} Sources Used"):
                        for i, source in enumerate(response_data['rag_sources'], 1):
                            score = source.get('score', 0)
                            st.markdown(f"""
                            <div class="source-card">
                                <strong>Source {i}</strong> (Relevance: {score:.1%})<br/>
                                {source['content']}
                            </div>
                            """, unsafe_allow_html=True)
                
                # Show tool detection
                if response_data.get('tool_results'):
                    st.info("🔧 Tools detected: " + ", ".join(response_data['tool_results']))
                
                # Add assistant message to history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response_data.get('response', ''),
                    "rag_sources": response_data.get('rag_sources', []),
                    "tool_results": response_data.get('tool_results', []),
                    "used_rag": response_data.get('used_rag', False),
                    "used_tools": response_data.get('used_tools', False),
                    "timestamp": datetime.now().isoformat()
                })

# Show helpful hints if no messages yet
if len(st.session_state.messages) == 0:
    st.info("👋 **Welcome to FAITHH Chat!**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 💡 Try asking:")
        st.markdown("""
        - "What did we discuss about Docker?"
        - "Read my config.yaml file"
        - "List files in /tmp"
        - "Run command: echo hello"
        """)
    
    with col2:
        st.markdown("### ✨ Features:")
        st.markdown("""
        - 🤖 **Gemini AI** - Smart responses
        - 📚 **RAG Search** - Remember past conversations
        - 🔧 **Tools** - Execute real commands
        - ⚡ **Real-time** - Instant responses
        """)
    
    # Quick start guide
    with st.expander("📖 Quick Start Guide"):
        st.markdown("""
        **RAG (Memory) Queries:**
        - Use words like "remember", "discussed", "mentioned"
        - Example: "What did I say about deployment?"
        
        **Tool Execution:**
        - Mention file operations: "read", "write", "list"
        - Mention commands: "run", "execute"
        - Example: "Read the README file"
        
        **Settings:**
        - Toggle RAG/Tools in sidebar
        - View system status and stats
        - Clear chat history when needed
        """)

# Footer
st.divider()
st.caption("💬 FAITHH Chat v1.0 | Unified API with RAG + Tools | 🎮 Battle Chip System")
