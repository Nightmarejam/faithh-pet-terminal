#!/bin/bash
# FAITHH Git Recovery Script
# Run this in your ai-stack directory

echo "=========================================="
echo "🔍 FAITHH Git History & Recovery"
echo "=========================================="
echo ""

# Check if Git is initialized
if [ -d .git ]; then
    echo "✅ Git repository found!"
    echo ""
    
    echo "📜 Commit History (last 10):"
    echo "-----------------------------"
    git log --oneline --graph --all -10
    echo ""
    
    echo "📊 Current Status:"
    echo "------------------"
    git status --short
    echo ""
    
    echo "🔎 Changes to faithh_pet_v3.html:"
    echo "-----------------------------------"
    git log --oneline --all -- faithh_pet_v3.html | head -5
    echo ""
    
    echo "💾 Available versions of faithh_pet_v3.html:"
    echo "---------------------------------------------"
    git log --pretty=format:"%h - %ar - %s" -- faithh_pet_v3.html | head -5
    echo ""
    echo ""
    
    # Check for uncommitted changes
    if git diff --quiet faithh_pet_v3.html; then
        echo "✓ No uncommitted changes to faithh_pet_v3.html"
    else
        echo "⚠️  Uncommitted changes detected:"
        git diff --stat faithh_pet_v3.html
        echo ""
        echo "To see full diff:"
        echo "  git diff faithh_pet_v3.html"
    fi
    echo ""
    
    # Show recovery options
    echo "🔧 RECOVERY OPTIONS:"
    echo "===================="
    echo ""
    echo "1. See what changed in last commit:"
    echo "   git diff HEAD~1 faithh_pet_v3.html"
    echo ""
    echo "2. Restore from 1 commit ago:"
    echo "   git checkout HEAD~1 -- faithh_pet_v3.html"
    echo ""
    echo "3. Restore from specific commit (use hash from log above):"
    echo "   git checkout <commit-hash> -- faithh_pet_v3.html"
    echo ""
    echo "4. Discard all uncommitted changes:"
    echo "   git checkout -- faithh_pet_v3.html"
    echo ""
    echo "5. Create a new branch to test fixes:"
    echo "   git checkout -b fix-ui-testing"
    echo ""
    
else
    echo "❌ No Git repository found!"
    echo ""
    echo "Would you like to:"
    echo "1. Initialize Git now (preserves current state)"
    echo "2. Check VS Code local history instead"
    echo ""
    echo "To initialize Git:"
    echo "  git init"
    echo "  git add ."
    echo "  git commit -m 'Current state backup'"
    echo ""
fi

echo "=========================================="
echo "📁 File Backup Status:"
echo "=========================================="
echo ""
echo "Backups of faithh_pet_v3.html:"
ls -lht faithh_pet_v3.html* 2>/dev/null | head -10
echo ""

# Check for the specific working version before patches
echo "🔍 Checking for working version markers..."
echo ""
if grep -q "for (const \[service, status\] of Object.entries(data.services))" faithh_pet_v3.html 2>/dev/null; then
    echo "⚠️  FOUND: Original broken loop (status variable)"
    echo "This is the version that needs fixing"
elif grep -q "for (const \[service, info\] of Object.entries(data.services))" faithh_pet_v3.html 2>/dev/null; then
    echo "✅ FOUND: Patched loop (info variable)"
    echo "Checking if innerHTML is correct..."
    if grep -q "statusItem.innerHTML.*status-name.*status-value" faithh_pet_v3.html 2>/dev/null; then
        echo "✅ innerHTML present"
    else
        echo "❌ innerHTML missing or broken"
    fi
fi

echo ""
echo "=========================================="
echo "🎯 QUICK FIX OPTIONS:"
echo "=========================================="
echo ""
echo "A. If you have Git history:"
echo "   ./restore_from_git.sh"
echo ""
echo "B. If no Git history:"
echo "   ./restore_from_backup.sh"
echo ""
echo "C. Manual fix (5 min):"
echo "   nano faithh_pet_v3.html"
echo "   Search for: Object.entries(data.services)"
echo "   Apply fix from RECOVERY_GUIDE.md"
echo ""
