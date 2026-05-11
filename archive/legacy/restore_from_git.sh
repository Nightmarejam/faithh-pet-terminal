#!/bin/bash
# Restore faithh_pet_v3.html from Git history
# Run this after checking git log to find the working version

echo "🔄 Git Restoration Script"
echo "=========================="
echo ""

if [ ! -d .git ]; then
    echo "❌ No Git repository found!"
    echo "Run check_git_history.sh first"
    exit 1
fi

# Backup current version
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
echo "📦 Backing up current version..."
cp faithh_pet_v3.html "faithh_pet_v3.html.before_restore_${TIMESTAMP}"
echo "✅ Saved to: faithh_pet_v3.html.before_restore_${TIMESTAMP}"
echo ""

# Show recent commits
echo "📜 Recent commits for faithh_pet_v3.html:"
echo "-----------------------------------------"
git log --oneline -5 -- faithh_pet_v3.html
echo ""

# Ask which commit to restore from
echo "Enter the commit hash to restore from (or 'HEAD~1' for previous):"
echo "Or press Enter to restore from HEAD (last committed version):"
read -r COMMIT_HASH

if [ -z "$COMMIT_HASH" ]; then
    COMMIT_HASH="HEAD"
fi

echo ""
echo "🔄 Restoring from: $COMMIT_HASH"
echo ""

# Show what will change
echo "Preview of changes:"
git diff "$COMMIT_HASH" -- faithh_pet_v3.html | head -30
echo ""
echo "... (showing first 30 lines of diff)"
echo ""

read -p "Proceed with restoration? (y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    git checkout "$COMMIT_HASH" -- faithh_pet_v3.html
    echo ""
    echo "✅ File restored from $COMMIT_HASH"
    echo ""
    echo "🧪 Testing the restored file..."
    
    # Quick validation
    if grep -q "Object.entries(data.services)" faithh_pet_v3.html; then
        echo "✅ File structure intact"
    fi
    
    echo ""
    echo "📝 Next steps:"
    echo "1. Restart server: pkill -f faithh_professional_backend.py && python faithh_professional_backend.py &"
    echo "2. Open browser: http://localhost:5557"
    echo "3. Check console (F12) for errors"
    echo ""
    echo "If this version still has issues:"
    echo "  git checkout HEAD~2 -- faithh_pet_v3.html  (try 2 commits back)"
    echo ""
else
    echo "❌ Restoration cancelled"
    echo "Your file remains unchanged"
fi
