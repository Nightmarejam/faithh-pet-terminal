#!/usr/bin/env python3
"""
Apply Backend RAG Optimizer Patch
Adds smart query logic to prioritize conversation chunks
"""

import re
from pathlib import Path
import shutil
from datetime import datetime

def find_backend_file():
    """Find the active backend file"""
    ai_stack = Path.home() / "ai-stack"
    
    # Look for backend files
    candidates = list(ai_stack.glob("*backend*.py"))
    
    if not candidates:
        print("❌ No backend files found!")
        return None
    
    # Prefer "fixed" version
    for candidate in candidates:
        if "fixed" in candidate.name:
            return candidate
    
    return candidates[0]

def backup_file(filepath):
    """Create backup before modifying"""
    backup_path = filepath.with_suffix(f'.py.backup.{datetime.now().strftime("%Y%m%d_%H%M%S")}')
    shutil.copy2(filepath, backup_path)
    print(f"✅ Backup created: {backup_path.name}")
    return backup_path

def apply_patch(backend_path):
    """Apply the RAG optimizer patch"""
    
    # Read current backend
    content = backend_path.read_text()
    
    # Check if already patched
    if "smart_rag_query" in content:
        print("⏭️  Backend already patched!")
        return False
    
    # Find the location to insert the new function (after imports, before routes)
    # Look for the @app.route or def query_rag pattern
    
    smart_query_function = '''
def smart_rag_query(query_text, n_results=10):
    """
    Intelligent RAG query that prioritizes conversation chunks for dev queries
    """
    try:
        # Keywords that indicate a development/technical query
        dev_keywords = ['discuss', 'talk', 'said', 'conversation', 'we', 'our',
                       'plan', 'setup', 'configure', 'implement', 'build', 
                       'create', 'did we', 'what was', 'how did', 'tell me about']
        
        query_lower = query_text.lower()
        is_dev_query = any(keyword in query_lower for keyword in dev_keywords)
        
        if is_dev_query:
            # Try conversation chunks first
            try:
                conv_results = collection.query(
                    query_texts=[query_text],
                    n_results=n_results,
                    where={"category": "claude_conversation_chunk"}
                )
                
                # If we got good matches (distance < 0.75), use them
                if (conv_results['distances'] and 
                    conv_results['distances'][0] and 
                    conv_results['distances'][0][0] < 0.75):
                    print(f"🎯 Using conversation chunks (best: {conv_results['distances'][0][0]:.3f})")
                    return conv_results
            except Exception as e:
                print(f"⚠️  Conversation chunk query failed: {e}")
        
        # Fall back to broader search with mixed categories
        categories = ["claude_conversation_chunk", "documentation", "code", "parity", "conversation"]
        try:
            results = collection.query(
                query_texts=[query_text],
                n_results=n_results,
                where={"category": {"$in": categories}}
            )
            print(f"📚 Using mixed category search")
            return results
        except:
            pass
        
        # Ultimate fallback - no filtering
        print(f"🔍 Using unfiltered search")
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
    
    # Find where to insert (before first @app.route)
    route_match = re.search(r'(@app\.route)', content)
    if route_match:
        insert_pos = route_match.start()
        new_content = content[:insert_pos] + smart_query_function + "\n" + content[insert_pos:]
    else:
        print("⚠️  Could not find @app.route, appending to end")
        new_content = content + "\n" + smart_query_function
    
    # Now replace the RAG query call in /api/chat
    # Look for: collection.query(query_texts=[message]
    # Replace with: smart_rag_query(message
    
    old_pattern = r'collection\.query\(\s*query_texts=\[message\],?\s*n_results=(\d+)'
    new_pattern = r'smart_rag_query(message, n_results=\1'
    
    new_content = re.sub(old_pattern, new_pattern, new_content)
    
    # Also replace any: results = collection.query(
    old_pattern2 = r'results\s*=\s*collection\.query\(\s*query_texts=\[([^\]]+)\],?\s*n_results=(\d+)'
    new_pattern2 = r'results = smart_rag_query(\1, n_results=\2'
    
    new_content = re.sub(old_pattern2, new_pattern2, new_content)
    
    # Write patched version
    backend_path.write_text(new_content)
    
    return True

def main():
    print("=" * 70)
    print("BACKEND RAG OPTIMIZER PATCHER")
    print("=" * 70)
    print()
    
    # Find backend
    backend_path = find_backend_file()
    if not backend_path:
        return
    
    print(f"📝 Found backend: {backend_path.name}\n")
    
    # Backup
    backup_path = backup_file(backend_path)
    
    # Apply patch
    print("\n🔧 Applying RAG optimizer patch...")
    
    if apply_patch(backend_path):
        print("✅ Patch applied successfully!")
        print("\n📋 Changes made:")
        print("   1. Added smart_rag_query() function")
        print("   2. Prioritizes conversation chunks for dev queries")
        print("   3. Falls back to mixed search if needed")
        print("   4. Updated /api/chat to use smart query")
        
        print("\n🔄 Restart backend to apply changes:")
        print("   pkill -f faithh_professional_backend")
        print("   cd ~/ai-stack && source venv/bin/activate")
        print(f"   nohup python {backend_path.name} > faithh_backend.log 2>&1 &")
    else:
        print("   (No changes needed)")
    
    print("\n💡 To restore from backup:")
    print(f"   cp {backup_path.name} {backend_path.name}")
    print()
    print("=" * 70)

if __name__ == "__main__":
    main()
