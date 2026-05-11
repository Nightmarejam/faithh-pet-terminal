#!/usr/bin/env python3
"""
Update faithh_professional_backend.py to use .env for API key
"""

import re
import sys

def update_backend():
    """Update the backend file to use .env"""
    
    # Read the current backend
    with open('faithh_professional_backend.py', 'r') as f:
        content = f.read()
    
    # Backup original
    with open('faithh_professional_backend.py.original', 'w') as f:
        f.write(content)
    
    # Check if already using dotenv
    if 'from dotenv import load_dotenv' in content:
        print("✅ Backend already imports dotenv")
        uses_dotenv = True
    else:
        print("➕ Adding dotenv import...")
        uses_dotenv = False
    
    # Find the imports section
    lines = content.split('\n')
    new_lines = []
    imports_added = False
    dotenv_loaded = False
    
    for i, line in enumerate(lines):
        # Add dotenv import after other imports
        if not imports_added and line.startswith('import ') and not uses_dotenv:
            new_lines.append(line)
            # Look ahead to find end of imports
            if i + 1 < len(lines) and not lines[i + 1].startswith(('import ', 'from ')):
                new_lines.append('from dotenv import load_dotenv')
                new_lines.append('import os')
                imports_added = True
                continue
        
        # Add load_dotenv() after imports, before any other code
        if not dotenv_loaded and not line.startswith(('import ', 'from ', '#', '')) and line.strip():
            if 'load_dotenv()' not in content:
                new_lines.append('')
                new_lines.append('# Load environment variables')
                new_lines.append('load_dotenv()')
                new_lines.append('')
                dotenv_loaded = True
        
        # Replace hardcoded API key with environment variable
        if 'AIzaSy' in line and 'GEMINI_API_KEY' not in line:
            print(f"⚠️  Found hardcoded API key on line {i+1}")
            # Replace with env variable
            line = re.sub(
                r'["\']AIzaSy[^"\']*["\']',
                'os.getenv("GEMINI_API_KEY")',
                line
            )
            print(f"✅ Replaced with os.getenv('GEMINI_API_KEY')")
        
        # Update any existing GEMINI_API_KEY that doesn't use os.getenv
        if 'GEMINI_API_KEY' in line and 'os.getenv' not in line and '=' in line:
            if not line.strip().startswith('#'):
                print(f"⚠️  Found GEMINI_API_KEY assignment on line {i+1}")
                line = re.sub(
                    r'GEMINI_API_KEY\s*=\s*["\'][^"\']*["\']',
                    'GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")',
                    line
                )
                print(f"✅ Updated to use os.getenv()")
        
        new_lines.append(line)
    
    # Write updated content
    updated_content = '\n'.join(new_lines)
    
    with open('faithh_professional_backend.py', 'w') as f:
        f.write(updated_content)
    
    print("")
    print("✅ Backend updated successfully!")
    print("📄 Original backed up to: faithh_professional_backend.py.original")
    print("")
    print("🔍 Verification:")
    print("  - Check that 'from dotenv import load_dotenv' is imported")
    print("  - Check that 'load_dotenv()' is called early")
    print("  - Check that os.getenv('GEMINI_API_KEY') is used")
    print("")

if __name__ == '__main__':
    try:
        update_backend()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

