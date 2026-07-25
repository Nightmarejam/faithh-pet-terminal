#!/bin/bash

echo "=========================================="
echo "🔍 FAITHH System Diagnostics"
echo "=========================================="
echo ""

echo "1️⃣ Checking what's using the ports..."
echo "Port 5557 (Backend):"
lsof -i:5557 2>/dev/null || echo "   Nothing found (might need sudo)"
netstat -tuln | grep 5557 2>/dev/null || ss -tuln | grep 5557 2>/dev/null
echo ""
echo "Port 8000 (UI Server):"
lsof -i:8000 2>/dev/null || echo "   Nothing found (might need sudo)"
netstat -tuln | grep 8000 2>/dev/null || ss -tuln | grep 8000 2>/dev/null
echo ""

echo "2️⃣ Looking for Python processes..."
ps aux | grep -E "python.*faithh|python.*8000" | grep -v grep
echo ""

echo "3️⃣ Checking for backup files..."
cd ~/ai-stack 2>/dev/null || cd /home/*/ai-stack 2>/dev/null
echo "Backend backups:"
ls -lht faithh_professional_backend*.py 2>/dev/null | head -5
echo ""
echo "HTML backups:"
ls -lht faithh_pet_v3*.html 2>/dev/null | head -5
echo ""

echo "4️⃣ Checking git status (if available)..."
if [ -d .git ]; then
    echo "Git changes to backend:"
    git diff --name-only | grep ".py"
    echo ""
    echo "Git changes to HTML:"
    git diff --name-only | grep ".html"
else
    echo "   Not a git repository"
fi
echo ""

echo "5️⃣ Last modified files in ai-stack..."
ls -lht ~/ai-stack/*.py ~/ai-stack/*.html 2>/dev/null | head -10
echo ""

echo "=========================================="
echo "💡 Quick Fixes:"
echo "=========================================="
echo "Kill processes on ports:"
echo "  fuser -k 5557/tcp && fuser -k 8000/tcp"
echo ""
echo "Restore from git (if available):"
echo "  git checkout HEAD -- faithh_professional_backend.py"
echo "  git checkout HEAD -- faithh_pet_v3.html"
echo ""
echo "Find what changed in backend:"
echo "  git diff faithh_professional_backend.py"
echo "=========================================="
