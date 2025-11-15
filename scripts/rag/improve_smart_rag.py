#!/usr/bin/env python3
"""
Improved smart_rag_query that works with backend's where clauses
"""

from pathlib import Path
import re

def create_improved_smart_rag_query():
    """Create an improved smart_rag_query function"""
    
    improved_function = '''def smart_rag_query(query_text, n_results=10, where=None):
    """
    Intelligent RAG query that prioritizes conversation chunks for dev queries
    Integrates with backend's category filtering
    """
    try:
        # Keywords that indicate a development/technical query
        dev_keywords = ['discuss', 'talk', 'said', 'conversation', 'we', 'our',
                       'plan', 'setup', 'configure', 'implement', 'build', 
                       'create', 'did we', 'what was', 'how did', 'tell me about',
                       'what did', 'what were', 'talked about']
        
        query_lower = query_text.lower()
        is_dev_query = any(keyword in query_lower for keyword in dev_keywords)
        
        print(f"🔍 Query: '{query_text[:60]}...'")
        print(f"   Dev query: {is_dev_query}")
        
        # For dev queries, prioritize conversation chunks
        if is_dev_query:
            try:
                # Try conversation chunks FIRST
                conv_results = collection.query(
                    query_texts=[query_text],
                    n_results=n_results,
                    where={"category": "claude_conversation_chunk"}
                )
                
                # Check if we got good matches
                if (conv_results['distances'] and 
                    conv_results['distances'][0] and 
                    len(conv_results['distances'][0]) > 0 and
                    conv_results['distances'][0][0] < 0.7):
                    print(f"   ✅ Using conversation chunks (best: {conv_results['distances'][0][0]:.3f})")
                    return conv_results
                else:
                    print(f"   ⚠️  Conversation chunks not good enough, trying mixed search")
            except Exception as e:
                print(f"   ⚠️  Conversation chunk query failed: {e}")
        
        # Fall back to the backend's where clause or broader search
        if where:
            # Backend provided a where clause, use it
            print(f"   📚 Using backend's where clause")
            return collection.query(
                query_texts=[query_text],
                n_results=n_results,
                where=where
            )
        else:
            # No where clause, do mixed category search
            categories = ["claude_conversation_chunk", "claude_conversation", 
                         "documentation", "code", "parity", "conversation"]
            print(f"   📚 Using mixed category search")
            try:
                return collection.query(
                    query_texts=[query_text],
                    n_results=n_results,
                    where={"category": {"$in": categories}}
                )
            except:
                # Ultimate fallback - no filtering
                print(f"   🔍 Using unfiltered search")
                return collection.query(
                    query_texts=[query_text],
                    n_results=n_results
                )
        
    except Exception as e:
        print(f"❌ Error in smart RAG query: {e}")
        # Ultimate fallback
        return collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
'''
    
    return improved_function

def apply_improved_function():
    """Apply the improved function to the backend"""
    
    backend_path = Path.home() / "ai-stack/faithh_professional_backend_fixed.py"
    content = backend_path.read_text()
    
    # Find and replace the old smart_rag_query function
    # Pattern: from "def smart_rag_query" to the next "def " or "@app.route"
    pattern = r'def smart_rag_query\(.*?\):\s*""".*?""".*?(?=\ndef |@app\.route)'
    
    replacement = create_improved_smart_rag_query()
    
    new_content = re.sub(pattern, replacement + '\n', content, flags=re.DOTALL)
    
    # Check if replacement worked
    if new_content != content:
        # Backup first
        backup_path = backend_path.with_suffix('.py.backup2')
        backup_path.write_text(content)
        
        # Write new version
        backend_path.write_text(new_content)
        
        print("✅ Improved smart_rag_query applied!")
        print(f"   Backup: {backup_path.name}")
        return True
    else:
        print("⚠️  Pattern didn't match, manual replacement needed")
        
        # Save the improved function to a file
        patch_path = Path.home() / "ai-stack/docs/patches/improved_smart_rag_query.py"
        patch_path.write_text(create_improved_smart_rag_query())
        print(f"   Improved function saved to: {patch_path}")
        return False

def main():
    print("=" * 70)
    print("IMPROVING smart_rag_query FUNCTION")
    print("=" * 70)
    print()
    print("This will:")
    print("  1. Detect dev queries (discuss, we, our, what did, etc.)")
    print("  2. Try conversation chunks FIRST for dev queries")
    print("  3. Fall back to backend's where clause if needed")
    print("  4. Add debug logging to see what's happening")
    print()
    
    if apply_improved_function():
        print("\n🔄 Restart backend to apply:")
        print("   pkill -f faithh_professional_backend")
        print("   cd ~/ai-stack && source venv/bin/activate")
        print("   nohup python faithh_professional_backend_fixed.py > faithh_backend.log 2>&1 &")
        print("\n   Then check logs: tail -f ~/ai-stack/faithh_backend.log")
    
    print()
    print("=" * 70)

if __name__ == "__main__":
    main()
