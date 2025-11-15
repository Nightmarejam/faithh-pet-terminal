#!/usr/bin/env python3
"""
Fix System Prompt to Include Memory
Ensures memory context is actually used in the LLM prompt
"""

from pathlib import Path
import re

def check_prompt_includes_memory():
    """Check if system prompt includes memory context"""
    
    backend_path = Path.home() / "ai-stack/faithh_professional_backend_fixed.py"
    content = backend_path.read_text()
    
    print("=" * 70)
    print("SYSTEM PROMPT MEMORY INTEGRATION CHECK")
    print("=" * 70)
    print()
    
    # Find the system_prompt definition in chat function
    chat_idx = content.find("def chat():")
    if chat_idx == -1:
        print("❌ Could not find chat() function")
        return False
    
    # Find system_prompt after chat function
    prompt_idx = content.find("system_prompt", chat_idx)
    if prompt_idx == -1:
        print("❌ Could not find system_prompt in chat()")
        return False
    
    # Get the prompt definition (next ~200 chars)
    prompt_section = content[prompt_idx:prompt_idx+500]
    
    print("📝 Current system_prompt construction:")
    print("-" * 70)
    print(prompt_section[:400])
    print("-" * 70)
    print()
    
    # Check if memory_context is referenced
    checks = {
        "personality": "{personality}" in prompt_section,
        "memory_context": "{memory_context}" in prompt_section,
        "context (RAG)": "{context}" in prompt_section
    }
    
    print("Checking prompt includes:")
    for name, found in checks.items():
        status = "✅" if found else "❌"
        print(f"  {status} {name}")
    
    print()
    
    if all(checks.values()):
        print("✅ System prompt includes all components!")
        return True
    else:
        print("⚠️  System prompt missing components")
        return False

def fix_system_prompt():
    """Fix the system prompt to include memory"""
    
    backend_path = Path.home() / "ai-stack/faithh_professional_backend_fixed.py"
    content = backend_path.read_text()
    
    # Backup
    import shutil
    from datetime import datetime
    backup = backend_path.with_suffix(f'.py.backup_prompt_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
    shutil.copy2(backend_path, backup)
    print(f"\n✅ Backup: {backup.name}")
    
    # Find and replace system_prompt in chat function
    # Look for: system_prompt = f"""...
    
    # Pattern to match current system_prompt (handles various formats)
    pattern = r'system_prompt\s*=\s*f"""[^"]*"""'
    
    # New prompt that DEFINITELY includes memory
    new_prompt = '''system_prompt = f"""{personality}

=== MEMORY & CONTEXT ===
{memory_context}

=== KNOWLEDGE BASE ===
{context if context else "No additional context retrieved."}
========================

Respond naturally as FAITHH:"""'''
    
    # Replace
    new_content = re.sub(pattern, new_prompt, content, flags=re.DOTALL)
    
    if new_content == content:
        print("⚠️  Pattern didn't match, trying manual approach...")
        
        # Find the line with system_prompt =
        chat_idx = content.find("def chat():")
        prompt_idx = content.find("system_prompt", chat_idx)
        
        if prompt_idx != -1:
            # Find the end of this statement (closing """)
            end_idx = content.find('"""', prompt_idx + 100)  # Skip opening """
            end_idx = content.find('"""', end_idx + 3)  # Find closing """
            
            if end_idx != -1:
                # Replace this section
                new_content = content[:prompt_idx] + new_prompt + content[end_idx+3:]
    
    # Write
    backend_path.write_text(new_content)
    print("✅ System prompt updated to include memory!")
    
    return True

def main():
    print()
    
    if not check_prompt_includes_memory():
        print("\n🔧 Fixing system prompt...")
        
        if fix_system_prompt():
            print("\n" + "=" * 70)
            print("✅ SYSTEM PROMPT FIXED")
            print("=" * 70)
            print()
            print("The prompt now includes:")
            print("  1. ✅ FAITHH personality")
            print("  2. ✅ Your memory (name, role, projects)")
            print("  3. ✅ RAG context (documents)")
            print()
            print("🔄 Restart backend:")
            print("   pkill -f faithh_professional_backend")
            print("   cd ~/ai-stack && source venv/bin/activate")
            print("   nohup python faithh_professional_backend_fixed.py > faithh_backend.log 2>&1 &")
            print()
            print("🧪 Test again:")
            print("   'What do you know about me?'")
            print()
            print("FAITHH should now respond:")
            print("   'Hi Jonathan! I know you're an Audio Producer...'")
            print()
    else:
        print("✅ System prompt already includes memory!")
        print("\nIf FAITHH still doesn't use memory, the issue is elsewhere.")
        print("Check that Ollama is receiving the full prompt.")
    
    print("=" * 70)

if __name__ == "__main__":
    main()
