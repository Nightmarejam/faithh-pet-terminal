#!/usr/bin/env python3
"""
Fix smart_rag_query to handle where parameter
"""

from pathlib import Path
import re

def fix_smart_rag_query():
    """Update smart_rag_query to accept and ignore the where parameter"""
    
    backend_path = Path.home() / "ai-stack/faithh_professional_backend_fixed.py"
    content = backend_path.read_text()
    
    # Find the old smart_rag_query
    old_function_pattern = r'def smart_rag_query\(query_text, n_results=10\):'
    
    # New function with where parameter support
    new_function = '''def smart_rag_query(query_text, n_results=10, where=None):
    """
    Intelligent RAG query that prioritizes conversation chunks for dev queries
    Note: where parameter is accepted but overridden by smart logic
    """'''
    
    # Replace function signature
    content = re.sub(old_function_pattern, new_function, content)
    
    # Save
    backend_path.write_text(content)
    print("✅ Updated smart_rag_query to accept where parameter")
    
    return True

if __name__ == "__main__":
    print("=" * 70)
    print("FIXING smart_rag_query PARAMETER ISSUE")
    print("=" * 70)
    print()
    
    if fix_smart_rag_query():
        print("\n🔄 Restart backend to apply fix:")
        print("   pkill -f faithh_professional_backend")
        print("   cd ~/ai-stack && source venv/bin/activate")
        print("   nohup python faithh_professional_backend_fixed.py > faithh_backend.log 2>&1 &")
    
    print()
    print("=" * 70)
