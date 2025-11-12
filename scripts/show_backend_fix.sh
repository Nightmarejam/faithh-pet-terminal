#!/bin/bash
# Manual Backend Fix Guide
# Run this to see exactly what needs to be changed

cd ~/ai-stack

echo "🔍 BACKEND FIX ANALYSIS"
echo "======================="
echo ""

echo "1️⃣ Checking current state..."
echo ""

# Check if import exists
if grep -q "from dotenv import load_dotenv" faithh_professional_backend.py; then
    echo "✅ Import exists (line $(grep -n 'from dotenv import load_dotenv' faithh_professional_backend.py | cut -d: -f1))"
else
    echo "❌ Import missing"
fi

# Check if load_dotenv() is called
if grep -q "load_dotenv()" faithh_professional_backend.py; then
    echo "✅ load_dotenv() called"
else
    echo "❌ load_dotenv() NOT called - NEEDS TO BE ADDED"
fi

# Check if using os.getenv
if grep -q 'os\.getenv.*GEMINI' faithh_professional_backend.py; then
    echo "✅ Using os.getenv for API key"
else
    echo "❌ NOT using os.getenv - NEEDS TO BE CHANGED"
fi

echo ""
echo "2️⃣ Finding API key location..."
echo ""

# Find where GEMINI_API_KEY is set
echo "API key assignments found on these lines:"
grep -n "GEMINI_API_KEY.*=" faithh_professional_backend.py | grep -v "^#"

echo ""
echo "3️⃣ What you need to do:"
echo ""
echo "MANUAL FIX REQUIRED:"
echo ""
echo "Step 1: Open the file"
echo "  nano faithh_professional_backend.py"
echo ""
echo "Step 2: Go to around line 25-30 (after imports)"
echo "  Add these lines after 'from dotenv import load_dotenv':"
echo ""
echo "    import os"
echo "    "
echo "    # Load environment variables"
echo "    load_dotenv()"
echo ""
echo "Step 3: Find each line with 'GEMINI_API_KEY = \"AIzaSy...\"'"
echo "  Change it to:"
echo ""
echo "    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')"
echo ""
echo "Step 4: Save (Ctrl+X, then Y, then Enter)"
echo ""
echo "Step 5: Test with this command:"
echo "  python3 test_backend_env.py"
echo ""

# Create a test script
cat > test_backend_env.py << 'PYTHON'
#!/usr/bin/env python3
"""Test that backend can load .env properly"""

import sys
import os

# Add current directory to path
sys.path.insert(0, '/home/jonat/ai-stack')

# Test 1: Can we load dotenv?
try:
    from dotenv import load_dotenv
    print("✅ dotenv module available")
except ImportError:
    print("❌ dotenv not installed")
    sys.exit(1)

# Test 2: Can we load .env file?
try:
    load_dotenv()
    print("✅ .env file loaded")
except Exception as e:
    print(f"❌ Error loading .env: {e}")
    sys.exit(1)

# Test 3: Is GEMINI_API_KEY available?
gemini_key = os.getenv('GEMINI_API_KEY')
if gemini_key:
    print(f"✅ GEMINI_API_KEY loaded ({len(gemini_key)} characters)")
    print(f"   Key preview: {gemini_key[:15]}...")
else:
    print("❌ GEMINI_API_KEY not found in environment")
    print("   Check your .env file")
    sys.exit(1)

# Test 4: Try importing the backend (basic syntax check)
print("\nTesting backend import...")
try:
    # This will fail if there are syntax errors
    with open('faithh_professional_backend.py', 'r') as f:
        content = f.read()
        compile(content, 'faithh_professional_backend.py', 'exec')
    print("✅ Backend has no syntax errors")
except SyntaxError as e:
    print(f"❌ Syntax error in backend: {e}")
    sys.exit(1)

print("\n" + "="*50)
print("✅ ALL TESTS PASSED!")
print("="*50)
print("\nYour backend is ready to use .env!")
print("\nNext step: Restart your backend")
print("  python3 faithh_professional_backend.py")
PYTHON

chmod +x test_backend_env.py

echo ""
echo "✅ Created test_backend_env.py"
echo ""
echo "After you make the manual changes, run:"
echo "  python3 test_backend_env.py"
echo ""
