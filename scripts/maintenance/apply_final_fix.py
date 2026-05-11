#!/usr/bin/env python3
"""
Final Fix: Add claude_conversation_chunk to backend where clause
This is THE fix that will make conversation chunks work!
"""

from pathlib import Path
import re

def apply_final_fix():
    """Add claude_conversation_chunk to the category list"""
    
    backend_path = Path.home() / "ai-stack/faithh_professional_backend_fixed.py"
    
    if not backend_path.exists():
        print(f"❌ Backend not found: {backend_path}")
        return False
    
    content = backend_path.read_text()
    
    # Find the where clause with categories
    old_pattern = r'where=\{"[^"]*or[^"]*": \[\s*\{"category": "documentation"\},\s*\{"category": "parity_file"\},\s*\{"category": "backend_code"\},\s*\{"category": "claude_conversation"\}'
    
    new_clause = '''where={"$or": [
                        {"category": "documentation"},
                        {"category": "parity_file"},
                        {"category": "backend_code"},
                        {"category": "claude_conversation"},
                        {"category": "claude_conversation_chunk"}'''
    
    # Try replacement
    new_content = re.sub(old_pattern, new_clause, content)
    
    if new_content == content:
        # Try a simpler pattern
        old_simple = '"claude_conversation"\n                    \]'
        new_simple = '"claude_conversation",\n                        {"category": "claude_conversation_chunk"}\n                    ]'
        new_content = content.replace(old_simple, new_simple)
    
    if new_content != content:
        # Backup
        backup = backend_path.with_suffix('.py.backup_final')
        backup.write_text(content)
        
        # Apply fix
        backend_path.write_text(new_content)
        
        print("✅ Added claude_conversation_chunk to where clause!")
        print(f"   Backup: {backup.name}")
        return True
    else:
        print("⚠️  Could not find pattern to replace")
        print("\n📝 Manual fix needed:")
        print("   Edit faithh_professional_backend_fixed.py")
        print("   Find: {\"category\": \"claude_conversation\"}")
        print("   Add after it: ,")
        print("                 {\"category\": \"claude_conversation_chunk\"}")
        return False

def main():
    print("=" * 70)
    print("FINAL FIX: Add claude_conversation_chunk Category")
    print("=" * 70)
    print()
    print("This fix adds the missing category to the where clause so")
    print("conversation chunks are actually searched!")
    print()
    
    if apply_final_fix():
        print("\n🔄 Restart backend:")
        print("   pkill -f faithh_professional_backend")
        print("   cd ~/ai-stack && source venv/bin/activate")
        print("   nohup python faithh_professional_backend_fixed.py > faithh_backend.log 2>&1 &")
        print("\n💡 Then test with: 'What did we discuss about FAITHH backend?'")
        print("   Should now return conversation context!")
    
    print()
    print("=" * 70)

if __name__ == "__main__":
    main()
