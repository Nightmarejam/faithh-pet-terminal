#!/bin/bash
# Master Monday Script - Runs all Monday tasks in sequence

set -e  # Exit on error

echo ""
echo "╔════════════════════════════════════════════════════╗"
echo "║   FAITHH Monday Master Script                      ║"
echo "║   Automated Week 1 Monday Completion               ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""

cd /home/jonat/ai-stack

# Check that scripts exist
SCRIPTS=(
    "monday_completion.sh"
    "update_backend_to_env.sh"
    "final_monday_cleanup.sh"
)

echo "Checking for required scripts..."
for script in "${SCRIPTS[@]}"; do
    if [ ! -f "$script" ]; then
        echo "❌ Missing: $script"
        echo "Please ensure all scripts are in ~/ai-stack/"
        exit 1
    fi
    chmod +x "$script"
done
echo "✅ All scripts found"
echo ""

# ============================================================
# Phase 1: Initial Setup
# ============================================================
echo "═══════════════════════════════════════════════════"
echo "PHASE 1: Initial Setup & Configuration"
echo "═══════════════════════════════════════════════════"
echo ""

./monday_completion.sh

echo ""
read -p "⏸️  Phase 1 complete. Press Enter to continue to Phase 2..." 

# ============================================================
# Phase 2: Backend Update
# ============================================================
echo ""
echo "═══════════════════════════════════════════════════"
echo "PHASE 2: Backend Update (Use .env)"
echo "═══════════════════════════════════════════════════"
echo ""
echo "⚠️  IMPORTANT: This will modify faithh_professional_backend.py"
echo "A backup will be created first."
echo ""

read -p "Update backend to use .env? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    ./update_backend_to_env.sh
    echo ""
    echo "✅ Backend updated!"
    echo "⚠️  You'll need to restart your backend after this script completes"
else
    echo "⏭️  Skipped backend update"
    echo "You can run it later: ./update_backend_to_env.sh"
fi

echo ""
read -p "⏸️  Phase 2 complete. Press Enter to continue to Phase 3..."

# ============================================================
# Phase 3: Final Cleanup
# ============================================================
echo ""
echo "═══════════════════════════════════════════════════"
echo "PHASE 3: Final Cleanup & Summary"
echo "═══════════════════════════════════════════════════"
echo ""

./final_monday_cleanup.sh

# ============================================================
# Complete!
# ============================================================
echo ""
echo "╔════════════════════════════════════════════════════╗"
echo "║                                                    ║"
echo "║         🎉 MONDAY COMPLETE! 🎉                    ║"
echo "║                                                    ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""
echo "📖 Next Steps:"
echo ""
echo "1. READ: MONDAY_COMPLETE_SUMMARY.md"
echo "   cat MONDAY_COMPLETE_SUMMARY.md"
echo ""
echo "2. VERIFY: Your .env file has the Gemini API key"
echo "   cat .env | grep GEMINI_API_KEY"
echo ""
echo "3. RESTART: Your backend (if it's currently running)"
echo "   - Press Ctrl+C in backend terminal"
echo "   - Run: python3 faithh_professional_backend.py"
echo ""
echo "4. TEST: Send a message in your UI to confirm it works"
echo ""
echo "5. REVIEW: Tuesday's checklist when ready"
echo "   cat WEEK1_CHECKLIST.md"
echo ""
echo "════════════════════════════════════════════════════"
echo ""
echo "Time to rest! Great work today! 🚀"
echo ""
