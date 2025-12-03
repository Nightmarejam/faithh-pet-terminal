#!/bin/bash
# Upgrade FAITHH backend to v3.2-integrated
# This script safely backs up the old backend and activates the new one

cd ~/ai-stack

echo "=================================================="
echo "🔧 FAITHH Backend Upgrade to v3.2-integrated"
echo "=================================================="
echo ""

# Step 1: Backup current backend
echo "📦 Step 1: Backing up current backend..."
BACKUP_FILE="faithh_professional_backend_fixed.py.backup_$(date +%Y%m%d_%H%M%S)"
cp faithh_professional_backend_fixed.py "$BACKUP_FILE"
echo "   ✅ Backed up to: $BACKUP_FILE"
echo ""

# Step 2: Replace with integrated version
echo "🔄 Step 2: Installing integrated backend..."
cp faithh_backend_integrated.py faithh_professional_backend_fixed.py
echo "   ✅ faithh_professional_backend_fixed.py updated"
echo ""

# Step 3: Verify
echo "🔍 Step 3: Verifying installation..."
if grep -q "v3.2" faithh_professional_backend_fixed.py; then
    echo "   ✅ Version 3.2-integrated confirmed!"
else
    echo "   ❌ Warning: Version check failed"
    echo "   Restoring backup..."
    cp "$BACKUP_FILE" faithh_professional_backend_fixed.py
    echo "   ✅ Restored from backup"
    exit 1
fi
echo ""

# Step 4: Kill old backend
echo "🛑 Step 4: Stopping old backend..."
pkill -f "faithh_professional_backend" || echo "   (No backend was running)"
sleep 2
echo ""

# Step 5: Start new backend
echo "🚀 Step 5: Starting integrated backend..."
python faithh_professional_backend_fixed.py &
BACKEND_PID=$!
echo "   ✅ Backend started (PID: $BACKEND_PID)"
sleep 3
echo ""

# Step 6: Test
echo "🧪 Step 6: Testing integrations..."
curl -s http://localhost:5557/api/test_integrations | python3 -m json.tool
echo ""

echo "=================================================="
echo "✅ UPGRADE COMPLETE!"
echo "=================================================="
echo ""
echo "New features:"
echo "  ✅ Self-awareness boost (detects queries about FAITHH)"
echo "  ✅ Decision citation (answers 'why' questions)"
echo "  ✅ Project state awareness (knows current phase)"
echo "  ✅ Smart intent detection"
echo ""
echo "Test the improvements:"
echo "  1. Ask: 'What is FAITHH meant to be?'"
echo "  2. Ask: 'Why did we choose ChromaDB?'"
echo "  3. Ask: 'What should I work on next for FAITHH?'"
echo ""
echo "UI: http://localhost:5557"
echo "=================================================="
