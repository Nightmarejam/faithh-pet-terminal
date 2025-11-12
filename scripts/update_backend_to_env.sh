#!/bin/bash
# Update Backend to Use .env
# This script modifies faithh_professional_backend.py to load API key from .env

cd /home/jonat/ai-stack

echo "🔧 Updating Backend to Use .env"
echo "================================"
echo ""

# Step 1: Check if python-dotenv is installed
echo "1️⃣  Checking python-dotenv..."
if pip list | grep -q python-dotenv; then
    echo "✅ python-dotenv is installed"
else
    echo "⚠️  Installing python-dotenv..."
    pip install python-dotenv
    echo "✅ python-dotenv installed"
fi
echo ""

# Step 2: Create a Python script to update the backend
echo "2️⃣  Creating backend updater..."

cat > update_backend_env.py << 'PYTHON_SCRIPT'
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

PYTHON_SCRIPT

chmod +x update_backend_env.py

echo "✅ Updater script created"
echo ""

# Step 3: Run the updater
echo "3️⃣  Running backend updater..."
python3 update_backend_env.py

echo ""

# Step 4: Verify the changes
echo "4️⃣  Verifying changes..."
echo ""

echo "Checking for dotenv import:"
if grep -q "from dotenv import load_dotenv" faithh_professional_backend.py; then
    echo "  ✅ dotenv imported"
else
    echo "  ⚠️  dotenv import not found"
fi

echo "Checking for load_dotenv() call:"
if grep -q "load_dotenv()" faithh_professional_backend.py; then
    echo "  ✅ load_dotenv() called"
else
    echo "  ⚠️  load_dotenv() call not found"
fi

echo "Checking for os.getenv usage:"
if grep -q "os.getenv.*GEMINI" faithh_professional_backend.py; then
    echo "  ✅ Using os.getenv for API key"
else
    echo "  ⚠️  Not using os.getenv"
fi

echo ""

# Step 5: Test the configuration
echo "5️⃣  Testing configuration..."
cat > test_env_loading.py << 'PYTHON_TEST'
#!/usr/bin/env python3
"""Test that .env loads correctly"""

from dotenv import load_dotenv
import os

load_dotenv()

gemini_key = os.getenv('GEMINI_API_KEY')

if gemini_key:
    print("✅ GEMINI_API_KEY loaded successfully")
    print(f"   Key length: {len(gemini_key)} characters")
    print(f"   Key starts with: {gemini_key[:10]}...")
else:
    print("❌ GEMINI_API_KEY not found in .env")
    print("   Please check your .env file")

print("")
print("Other environment variables:")
for key in ['OLLAMA_HOST', 'BACKEND_PORT', 'ENVIRONMENT']:
    value = os.getenv(key)
    if value:
        print(f"  ✅ {key} = {value}")
    else:
        print(f"  ⚠️  {key} not set")

PYTHON_TEST

python3 test_env_loading.py

echo ""

# Final summary
echo "════════════════════════════════════════"
echo "✨ Backend Update Complete!"
echo "════════════════════════════════════════"
echo ""
echo "What changed:"
echo "  1. Added: from dotenv import load_dotenv"
echo "  2. Added: load_dotenv() call"
echo "  3. Updated: API key to use os.getenv()"
echo ""
echo "Next steps:"
echo "  1. Review the changes: nano faithh_professional_backend.py"
echo "  2. Restart your backend"
echo "  3. Test that it works"
echo "  4. If issues, restore from: faithh_professional_backend.py.original"
echo ""
echo "To restart backend:"
echo "  - Press Ctrl+C in backend terminal"
echo "  - Run: python3 faithh_professional_backend.py"
echo ""
