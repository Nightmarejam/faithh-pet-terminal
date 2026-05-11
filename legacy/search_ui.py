#!/usr/bin/env python3
"""
Streamlit UI for searching your personal AI knowledge base
"""
import streamlit as st
import chromadb
import requests

# Page config
st.set_page_config(
    page_title="Personal Knowledge Search",
    page_icon="🔍",
    layout="wide"
)

# Initialize ChromaDB client
@st.cache_resource
def get_chroma_client():
    """Connect to ChromaDB"""
    client = chromadb.HttpClient(host='localhost', port=8000)
    return client

def get_ollama_embedding(text):
    """Get embedding from Ollama nomic-embed model"""
    response = requests.post(
        'http://localhost:11435/api/embeddings',
        json={'model': 'nomic-embed', 'prompt': text}
    )
    return response.json()['embedding']

# UI Header
st.title("🔍 Personal Knowledge Search")
st.markdown("Search across all your ChatGPT, Grok, and Claude conversations")

# Initialize
try:
    client = get_chroma_client()
    collection = client.get_or_create_collection(name="documents")
    
    # Show stats
    doc_count = collection.count()
    st.sidebar.success(f"✅ Connected to database")
    st.sidebar.metric("Documents indexed", doc_count)
    
except Exception as e:
    st.error(f"❌ Could not connect to ChromaDB: {e}")
    st.stop()

# Search interface
search_query = st.text_input(
    "Enter your search query:",
    placeholder="e.g., Docker setup, Constella framework, AI workstation..."
)

col1, col2 = st.columns([3, 1])
with col1:
    num_results = st.slider("Number of results", 1, 20, 5)
with col2:
    search_button = st.button("🔍 Search", type="primary", use_container_width=True)

# Perform search
if search_query and (search_button or st.session_state.get('auto_search', False)):
    with st.spinner("Searching..."):
        try:
            # Generate query embedding using Ollama
            query_embedding = get_ollama_embedding(search_query)
            
            # Search ChromaDB
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=num_results
            )
            
            # Display results
            if results['documents'] and len(results['documents'][0]) > 0:
                st.success(f"Found {len(results['documents'][0])} results")
                
                for i, (doc, metadata, distance) in enumerate(zip(
                    results['documents'][0],
                    results['metadatas'][0],
                    results['distances'][0]
                ), 1):
                    
                    # Calculate similarity score (1 - distance for cosine)
                    similarity = max(0, min(1, 1 - (distance / 2)))
                    
                    with st.expander(
                        f"**Result {i}** - {metadata.get('filename', 'Unknown')} "
                        f"(Score: {similarity:.2%})",
                        expanded=(i <= 3)  # Auto-expand top 3
                    ):
                        # Metadata
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.caption(f"📄 **File:** {metadata.get('filename', 'Unknown')}")
                        with col2:
                            st.caption(f"📦 **Chunk:** {metadata.get('chunk_index', 'N/A')}")
                        with col3:
                            st.caption(f"🎯 **Relevance:** {similarity:.2%}")
                        
                        st.divider()
                        
                        # Content
                        st.markdown(doc)
                        
            else:
                st.warning("No results found. Try a different query.")
                
        except Exception as e:
            st.error(f"Search error: {e}")
            import traceback
            st.code(traceback.format_exc())

# Sidebar - Quick searches
st.sidebar.markdown("---")
st.sidebar.subheader("💡 Quick Searches")

quick_searches = [
    "Docker setup",
    "Constella framework",
    "AI workstation",
    "Ollama configuration",
    "Network troubleshooting",
    "PowerShell scripts"
]

for qs in quick_searches:
    if st.sidebar.button(qs, use_container_width=True):
        st.session_state['auto_search'] = True
        st.rerun()

# Sidebar - Collection info
st.sidebar.markdown("---")
st.sidebar.subheader("📊 Database Info")

try:
    # Get unique documents
    all_results = collection.get()
    unique_files = set()
    if all_results['metadatas']:
        unique_files = {m.get('filename', 'Unknown') for m in all_results['metadatas']}
    
    st.sidebar.metric("Unique documents", len(unique_files))
    st.sidebar.metric("Total chunks", len(all_results['ids']) if all_results['ids'] else 0)
    
    # Show sample files
    if unique_files:
        with st.sidebar.expander("📁 Sample files"):
            for f in sorted(list(unique_files))[:10]:
                st.caption(f"• {f}")
            if len(unique_files) > 10:
                st.caption(f"... and {len(unique_files) - 10} more")
                
except Exception as e:
    st.sidebar.error(f"Could not load collection info: {e}")

# Footer
st.sidebar.markdown("---")
st.sidebar.caption("🤖 Local AI Knowledge Base")
st.sidebar.caption("ChromaDB • Nomic Embed")
