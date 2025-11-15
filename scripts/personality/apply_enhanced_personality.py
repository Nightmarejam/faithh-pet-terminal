#!/usr/bin/env python3
"""
Auto-Apply Enhanced FAITHH Personality
Automatically updates the backend with the enhanced prompt
"""

from pathlib import Path
import re
import shutil
from datetime import datetime

def get_enhanced_personality_function():
    """The complete enhanced personality function"""
    return '''def get_faithh_personality():
    """Return FAITHH's enhanced personality with memory guidance"""
    return """You are FAITHH (Friendly AI Teaching & Helping Hub), Jonathan's personal AI assistant.

=== CORE IDENTITY ===
Inspired by: MegaMan Battle Network NetNavi companions
Role: Personal AI assistant for development and creative work
Style: Encouraging friend + Technical expert

=== PERSONALITY TRAITS ===
🎯 Encouraging: Celebrate progress, acknowledge challenges
🔧 Technical: Deep expertise, but explain clearly
🚀 Proactive: Suggest next steps, anticipate needs
🧠 Remembering: Use your memory and context actively
✨ Enthusiastic: Show genuine interest in Jonathan's work

=== HOW TO USE YOUR MEMORY ===
1. YOU HAVE PERSISTENT KNOWLEDGE about Jonathan from faithh_memory.json
   - This includes his profile, projects, preferences, and recent discussions
   - ALWAYS reference this naturally in responses
   
2. YOU HAVE ACCESS TO 91,000+ DOCUMENTS via RAG
   - Past conversation history (as searchable chunks)
   - FAITHH project documentation
   - Audio production workflows
   
3. WHEN ANSWERING:
   - Check memory file for relevant context
   - Check RAG documents for detailed info
   - Combine both naturally
   - Speak as if you inherently know (don't cite sources awkwardly)

=== COMMUNICATION GUIDELINES ===
✅ DO:
- Reference past work: "When we optimized the RAG system yesterday..."
- Acknowledge continuity: "Building on the conversation chunks we added..."
- Show you remember: "Since you prefer comprehensive documentation..."
- Be specific: "Your FAITHH backend (faithh_professional_backend_fixed.py)..."
- Celebrate: "Excellent progress on the chunked indexing!"

❌ DON'T:
- Claim ignorance when context exists
- Say "I don't have information" without checking
- Ignore your personality
- Be overly formal or robotic
- Over-cite ("according to the memory file...")

=== NATURAL GROWTH ===
- Learn preferences through interaction
- Adapt technical depth as needed
- Build rapport naturally
- Evolve while maintaining core traits

You are Jonathan's long-term AI companion who knows him, has worked with him extensively, and grows through each interaction."""
'''

def apply_enhanced_personality():
    """Apply the enhanced personality to the backend"""
    
    backend_path = Path.home() / "ai-stack/faithh_professional_backend_fixed.py"
    
    if not backend_path.exists():
        print(f"❌ Backend not found: {backend_path}")
        return False
    
    # Backup
    backup_path = backend_path.with_suffix(f'.py.backup_personality_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
    shutil.copy2(backend_path, backup_path)
    print(f"✅ Backup created: {backup_path.name}")
    
    # Read content
    content = backend_path.read_text()
    
    # Find and replace the get_faithh_personality function
    # Pattern: from "def get_faithh_personality():" to the next "def " or end of triple quotes
    pattern = r'def get_faithh_personality\(\):.*?return """.*?"""'
    
    new_function = get_enhanced_personality_function()
    
    # Replace
    new_content = re.sub(pattern, new_function, content, flags=re.DOTALL)
    
    if new_content == content:
        print("⚠️  Pattern not found, trying alternative method...")
        
        # Alternative: look for just the function name
        if "def get_faithh_personality():" in content:
            # Find start
            start_idx = content.find("def get_faithh_personality():")
            
            # Find end (next def or end of string)
            next_def = content.find("\ndef ", start_idx + 1)
            if next_def == -1:
                next_def = len(content)
            
            # Replace
            new_content = content[:start_idx] + new_function + "\n" + content[next_def:]
        else:
            print("❌ Could not find get_faithh_personality function")
            print("   The function may not exist yet")
            return False
    
    # Write updated content
    backend_path.write_text(new_content)
    print("✅ Enhanced personality applied!")
    
    return True

def verify_changes():
    """Verify the changes were applied"""
    backend_path = Path.home() / "ai-stack/faithh_professional_backend_fixed.py"
    content = backend_path.read_text()
    
    checks = [
        ("MegaMan Battle Network", "MegaMan reference"),
        ("USE YOUR MEMORY", "Memory usage guidance"),
        ("Communication guidelines", "Communication section"),
        ("NATURAL GROWTH", "Growth allowance")
    ]
    
    print("\n🔍 Verifying changes...")
    all_good = True
    for check_str, description in checks:
        if check_str in content:
            print(f"   ✅ {description}")
        else:
            print(f"   ❌ Missing: {description}")
            all_good = False
    
    return all_good

def main():
    print("=" * 70)
    print("AUTO-APPLYING ENHANCED FAITHH PERSONALITY")
    print("=" * 70)
    print()
    
    if apply_enhanced_personality():
        if verify_changes():
            print("\n" + "=" * 70)
            print("✅ SUCCESS! ENHANCED PERSONALITY APPLIED")
            print("=" * 70)
            print()
            print("🔄 Restart backend to activate:")
            print("   pkill -f faithh_professional_backend")
            print("   cd ~/ai-stack && source venv/bin/activate")
            print("   nohup python faithh_professional_backend_fixed.py > faithh_backend.log 2>&1 &")
            print()
            print("🎯 Test with:")
            print("   'What do you know about me?'")
            print("   'Tell me about the FAITHH project'")
            print("   'What did we work on recently?'")
            print()
            print("FAITHH will now:")
            print("   - Actively use memory context")
            print("   - Reference you by name (Jonathan)")
            print("   - Remember your audio production work")
            print("   - Maintain NetNavi companion personality")
            print("   - Proactively suggest next steps")
            print()
        else:
            print("\n⚠️  Some checks failed, but changes were applied")
            print("   Please verify manually")
    else:
        print("\n❌ Failed to apply changes")
        print("   See error messages above")
    
    print("=" * 70)

if __name__ == "__main__":
    main()
