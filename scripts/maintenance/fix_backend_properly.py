#!/usr/bin/env python3
"""
Reliable Backend Fixer - Properly updates faithh_professional_backend.py
"""

import re
import os

def fix_backend():
    """Fix the backend to use .env properly"""
    
    filepath = 'faithh_professional_backend.py'
    
    print("🔧 Backend Fix Script")
    print("=" * 50)
    print()
    
    # Read the file
    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"❌ Error: {filepath} not found")
        print("   Make sure you're in ~/ai-stack directory")
        return False
    
    # Backup
    backup_file = f"{filepath}.prefixbackup"
    with open(backup_file, 'w') as f:
        f.writelines(lines)
    print(f"✅ Backup created: {backup_file}")
    print()
    
    # Track changes
    changes_made = []
    new_lines = []
    
    # Flags
    has_os_import = False
    has_dotenv_import = False
    has_load_dotenv_call = False
    last_import_line = 0
    
    # Pass 1: Analyze the file
    for i, line in enumerate(lines):
        if 'import os' in line and not line.strip().startswith('#'):
            has_os_import = True
        if 'from dotenv import load_dotenv' in line:
            has_dotenv_import = True
        if line.startswith(('import ', 'from ')) and not line.strip().startswith('#'):
            last_import_line = i
        if 'load_dotenv()' in line:
            has_load_dotenv_call = True
    
    print("📊 Current State:")
    print(f"  • has 'import os': {has_os_import}")
    print(f"  • has 'from dotenv import load_dotenv': {has_dotenv_import}")
    print(f"  • has 'load_dotenv()' call: {has_load_dotenv_call}")
    print(f"  • last import on line: {last_import_line + 1}")
    print()
    
    # Pass 2: Make changes
    load_dotenv_added = False
    
    for i, line in enumerate(lines):
        # Add load_dotenv() call after imports
        if not has_load_dotenv_call and not load_dotenv_added:
            # Found first non-import, non-comment, non-blank line after imports
            if (i > last_import_line and 
                line.strip() and 
                not line.strip().startswith('#') and
                not line.startswith(('import ', 'from '))):
                
                new_lines.append('\n')
                new_lines.append('# Load environment variables\n')
                new_lines.append('load_dotenv()\n')
                new_lines.append('\n')
                load_dotenv_added = True
                changes_made.append(f"Added load_dotenv() call before line {i+1}")
        
        # Replace hardcoded API keys with os.getenv()
        if 'GEMINI_API_KEY' in line and '=' in line and 'AIzaSy' in line:
            # Found hardcoded key
            indent = len(line) - len(line.lstrip())
            new_line = ' ' * indent + 'GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")\n'
            new_lines.append(new_line)
            changes_made.append(f"Line {i+1}: Replaced hardcoded key with os.getenv()")
            continue
        
        # Also catch assignments that might be different
        if re.match(r'^\s*GEMINI_API_KEY\s*=\s*["\']', line) and 'os.getenv' not in line:
            indent = len(line) - len(line.lstrip())
            new_line = ' ' * indent + 'GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")\n'
            new_lines.append(new_line)
            changes_made.append(f"Line {i+1}: Replaced key assignment with os.getenv()")
            continue
        
        # Keep the line as-is
        new_lines.append(line)
    
    # Check if we need to add os import
    if not has_os_import:
        # Find where to add it (after other imports)
        for i, line in enumerate(new_lines):
            if 'from dotenv import load_dotenv' in line:
                new_lines.insert(i + 1, 'import os\n')
                changes_made.append(f"Added 'import os' after line {i+1}")
                break
    
    # Write the fixed file
    with open(filepath, 'w') as f:
        f.writelines(new_lines)
    
    print("✅ Changes Made:")
    if changes_made:
        for change in changes_made:
            print(f"  • {change}")
    else:
        print("  • No changes needed - file already correct!")
    
    print()
    print("=" * 50)
    print("✅ Backend updated successfully!")
    print("=" * 50)
    print()
    print("📋 Next Steps:")
    print("  1. Review changes (optional):")
    print(f"     diff {backup_file} {filepath}")
    print()
    print("  2. Test the configuration:")
    print("     python3 test_backend_env.py")
    print()
    print("  3. Restart your backend:")
    print("     python3 faithh_professional_backend.py")
    print()
    
    return True

if __name__ == '__main__':
    import sys
    
    # Check we're in the right directory
    if not os.path.exists('faithh_professional_backend.py'):
        print("❌ Error: faithh_professional_backend.py not found")
        print("   Make sure you're in ~/ai-stack directory")
        print()
        print("Run: cd ~/ai-stack")
        sys.exit(1)
    
    success = fix_backend()
    sys.exit(0 if success else 1)
