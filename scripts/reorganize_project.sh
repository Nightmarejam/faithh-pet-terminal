#!/bin/bash
# FAITHH Project Reorganization Script
# Safely reorganizes project files into a clean structure

echo "============================================================"
echo "          FAITHH PROJECT REORGANIZATION"
echo "============================================================"

# Create timestamp for backup
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="$HOME/ai-stack-backup-$TIMESTAMP"

echo "Creating backup at: $BACKUP_DIR"
cp -r ~/ai-stack $BACKUP_DIR

cd ~/ai-stack

echo ""
echo "📁 Creating new directory structure..."

# Create directories
mkdir -p frontend
mkdir -p backend/{core,services,adapters}
mkdir -p scripts
mkdir -p docs/{active,archive}
mkdir -p legacy
mkdir -p images

echo "✅ Directories created"

echo ""
echo "📦 Moving files to organized locations..."

# Frontend files (only move HTML files, keep originals for now)
echo "  Moving frontend files..."
cp faithh_pet_v3.html frontend/ 2>/dev/null
cp rag-chat.html frontend/ 2>/dev/null

# Backend core files
echo "  Moving backend core files..."
cp faithh_simple_backend.py backend/core/ 2>/dev/null
cp faithh_unified_api.py backend/core/ 2>/dev/null
cp config.yaml backend/core/ 2>/dev/null

# Backend services
echo "  Moving backend services..."
cp tool_executor.py backend/services/ 2>/dev/null
cp tool_registry.py backend/services/ 2>/dev/null
cp security_manager.py backend/services/ 2>/dev/null
cp rag_processor.py backend/services/ 2>/dev/null

# Backend adapters
echo "  Moving backend adapters..."
cp faithh_backend_adapter.py backend/adapters/ 2>/dev/null
cp faithh_api_websocket.py backend/adapters/ 2>/dev/null

# Scripts
echo "  Moving scripts..."
cp main.py scripts/ 2>/dev/null
cp launch_faithh.sh scripts/ 2>/dev/null
cp system_health_check.py scripts/ 2>/dev/null
cp analyze_dependencies.py scripts/ 2>/dev/null
cp test_*.py scripts/ 2>/dev/null
cp setup_rag.py scripts/ 2>/dev/null

# Documentation
echo "  Organizing documentation..."
cp MASTER_CONTEXT.md docs/active/ 2>/dev/null
cp ARCHITECTURE.md docs/active/ 2>/dev/null
cp ROADMAP.md docs/active/ 2>/dev/null
cp QUICKSTART.md docs/active/ 2>/dev/null

# Archive old context files
cp FAITHH_CONTEXT.md docs/archive/ 2>/dev/null
cp *_COMPLETE.md docs/archive/ 2>/dev/null
cp SESSION_*.md docs/archive/ 2>/dev/null

# Legacy (alternative implementations)
echo "  Archiving alternative implementations..."
cp chat_ui.py legacy/ 2>/dev/null
cp search_ui.py legacy/ 2>/dev/null
cp faithh_api.py legacy/ 2>/dev/null
cp rag_api.py legacy/ 2>/dev/null

echo ""
echo "✅ Files organized (copied, not moved)"
echo ""
echo "============================================================"
echo "                    SUMMARY"
echo "============================================================"
echo "✅ Backup created at: $BACKUP_DIR"
echo "✅ New structure created in ~/ai-stack"
echo "✅ Original files preserved"
echo ""
echo "📝 Next steps:"
echo "1. Test that everything still works"
echo "2. Update import paths in Python files if needed"
echo "3. Remove original files when confirmed working"
echo "4. Update MASTER_CONTEXT.md with new structure"
echo ""
echo "To test the new structure:"
echo "  cd ~/ai-stack"
echo "  python3 scripts/main.py"
echo ""
echo "============================================================"
