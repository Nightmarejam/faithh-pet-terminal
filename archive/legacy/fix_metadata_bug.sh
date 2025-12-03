#!/bin/bash
# Quick patch for ChromaDB metadata bug
# Converts intent dict to string before indexing

cd ~/ai-stack

echo "🔧 Patching metadata indexing bug..."

# Create backup
cp faithh_professional_backend_fixed.py faithh_professional_backend_fixed.py.bak_metadata

# Fix: Convert intent dict to string in metadata
# Line ~717 and ~750 - change 'intent': intent to 'intent_summary': str(intent['patterns_matched'])

sed -i "s/'intent': intent/'intent_summary': ','.join(intent.get('patterns_matched', []))/" faithh_professional_backend_fixed.py

echo "✅ Patch applied!"
echo ""
echo "Restarting backend..."
pkill -f "faithh_professional_backend"
sleep 2
python faithh_professional_backend_fixed.py &

echo ""
echo "✅ Backend restarted with fix!"
echo "The indexing error should be gone now."
