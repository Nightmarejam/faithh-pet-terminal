
# Backend RAG Query Optimization Patch
# Add this to faithh_professional_backend_fixed.py after the query_rag function

def smart_rag_query(query_text, n_results=10):
    """
    Intelligent RAG query that prioritizes conversation chunks for dev queries
    """
    try:
        # Keywords that indicate a development/technical query
        dev_keywords = ['discuss', 'talk', 'said', 'conversation', 'we', 'plan', 
                       'setup', 'configure', 'implement', 'build', 'create']
        
        is_dev_query = any(keyword in query_text.lower() for keyword in dev_keywords)
        
        if is_dev_query:
            # Try conversation chunks first
            conv_results = collection.query(
                query_texts=[query_text],
                n_results=n_results,
                where={"category": "claude_conversation_chunk"}
            )
            
            # If we got good matches (distance < 0.7), use them
            if conv_results['distances'][0] and conv_results['distances'][0][0] < 0.7:
                return conv_results
        
        # Fall back to broader search with mixed categories
        categories = ["claude_conversation_chunk", "documentation", "code", "parity"]
        results = collection.query(
            query_texts=[query_text],
            n_results=n_results,
            where={"category": {"$in": categories}}
        )
        
        return results
        
    except Exception as e:
        print(f"Error in smart RAG query: {e}")
        # Ultimate fallback - no filtering
        return collection.query(
            query_texts=[query_text],
            n_results=n_results
        )

# Replace the /api/chat endpoint RAG query with:
# results = smart_rag_query(message, n_results=10)
