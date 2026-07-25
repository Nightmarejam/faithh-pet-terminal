#!/bin/bash
# Restore faithh_pet_v3.html from backup files
# Run this if no Git history but you have .bak or timestamped backups

echo "🔄 Backup File Restoration Script"
echo "=================================="
echo ""

cd ~/ai-stack || exit 1

echo "📁 Available backup files:"
echo "-------------------------"
ls -lht faithh_pet_v3.html* | head -15
echo ""

# Find all backups
BACKUPS=$(ls -t faithh_pet_v3.html.* 2>/dev/null)

if [ -z "$BACKUPS" ]; then
    echo "❌ No backup files found!"
    echo ""
    echo "Searched for files matching: faithh_pet_v3.html.*"
    echo ""
    echo "Options:"
    echo "1. Check Git history: ./check_git_history.sh"
    echo "2. VS Code Timeline: Right-click file → Timeline"
    echo "3. Manual fix: See RECOVERY_GUIDE.md"
    exit 1
fi

echo "🔍 Analyzing backups..."
echo ""

# Score each backup
echo "Backup File Analysis:"
echo "---------------------"
for backup in $BACKUPS; do
    SIZE=$(stat -f%z "$backup" 2>/dev/null || stat -c%s "$backup" 2>/dev/null)
    if grep -q "Object.entries(data.services)" "$backup" 2>/dev/null; then
        if grep -q "statusItem.innerHTML" "$backup" 2>/dev/null; then
            echo "✅ $backup (${SIZE} bytes) - Looks complete"
        else
            echo "⚠️  $backup (${SIZE} bytes) - Missing innerHTML"
        fi
    else
        echo "❌ $backup (${SIZE} bytes) - Missing main loop"
    fi
done
echo ""

# Recommend the largest/oldest backup
RECOMMENDED=$(ls -S faithh_pet_v3.html.* 2>/dev/null | head -1)
echo "💡 Recommended restore: $RECOMMENDED"
echo ""

read -p "Enter backup filename to restore (or press Enter for recommended): " CHOICE
echo ""

if [ -z "$CHOICE" ]; then
    CHOICE="$RECOMMENDED"
fi

if [ ! -f "$CHOICE" ]; then
    echo "❌ File not found: $CHOICE"
    exit 1
fi

# Backup current version
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
echo "📦 Backing up current version..."
cp faithh_pet_v3.html "faithh_pet_v3.html.before_restore_${TIMESTAMP}"
echo "✅ Saved to: faithh_pet_v3.html.before_restore_${TIMESTAMP}"
echo ""

echo "🔄 Restoring from: $CHOICE"
cp "$CHOICE" faithh_pet_v3.html

echo "✅ File restored!"
echo ""

# Validate
echo "🧪 Validating restored file..."
if grep -q "Object.entries(data.services)" faithh_pet_v3.html; then
    echo "✅ Main loop found"
fi
if grep -q "statusItem.innerHTML" faithh_pet_v3.html; then
    echo "✅ innerHTML present"
fi
echo ""

echo "📝 Next steps:"
echo "1. Restart server:"
echo "   pkill -f faithh_professional_backend.py"
echo "   python faithh_professional_backend.py &"
echo ""
echo "2. Test in browser:"
echo "   http://localhost:5557"
echo "   Check console (F12) for errors"
echo ""
echo "3. If still broken, try another backup:"
echo "   ./restore_from_backup.sh"
echo ""
