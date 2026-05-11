#!/usr/bin/env python3
"""
FAITHH Backend Integration Patch
Adds quality filtering and knowledge graph support to the existing backend.

This script patches the existing faithh_professional_backend_fixed.py to add:
1. Quality filtering for auto-indexer
2. Knowledge graph self-awareness
3. Tiered storage support

Usage:
    python apply_faithh_patch.py [--backup] [--dry-run]
    
Options:
    --backup    Create backup before patching (default: True)
    --dry-run   Show what would be changed without modifying files
"""

import sys
import shutil
from pathlib import Path
from datetime import datetime
import argparse


# The code to add to the backend
QUALITY_FILTER_IMPORT = '''
# FAITHH Quality Filter & Knowledge Graph Integration (added by patch)
try:
    from quality_filter import QualityFilter, TieredStorage, FilterResult
    from knowledge_graph import KnowledgeGraph, get_knowledge_graph
    QUALITY_FILTER_ENABLED = True
    print("✅ Quality filter and knowledge graph modules loaded")
except ImportError as e:
    QUALITY_FILTER_ENABLED = False
    print(f"⚠️ Quality filter modules not available: {e}")
'''

QUALITY_FILTER_INIT = '''
# Initialize quality filter and knowledge graph
if QUALITY_FILTER_ENABLED:
    quality_filter = QualityFilter()
    tiered_storage = TieredStorage()
    knowledge_graph = get_knowledge_graph()
    print(f"📊 Knowledge graph loaded: {knowledge_graph._loaded}")
else:
    quality_filter = None
    tiered_storage = None
    knowledge_graph = None
'''

AUTO_INDEX_FUNCTION = '''
def auto_index_response(response_text: str, metadata: dict = None) -> dict:
    """
    Automatically filter and index a response using tiered storage.
    
    Returns dict with tier, score, and whether it was stored.
    """
    if not QUALITY_FILTER_ENABLED or quality_filter is None:
        return {"enabled": False, "stored": False}
    
    try:
        result = quality_filter.classify(response_text, metadata)
        stored = tiered_storage.store(response_text, result)
        
        return {
            "enabled": True,
            "tier": result.tier,
            "score": result.score,
            "reasons": result.reasons,
            "stored": stored
        }
    except Exception as e:
        print(f"Auto-index error: {e}")
        return {"enabled": True, "error": str(e), "stored": False}


def get_kg_context(query: str) -> str:
    """Get relevant knowledge graph context for a query."""
    if not QUALITY_FILTER_ENABLED or knowledge_graph is None:
        return ""
    
    try:
        return knowledge_graph.get_context_for_query(query)
    except Exception as e:
        print(f"Knowledge graph context error: {e}")
        return ""
'''

CHAT_ENDPOINT_PATCH = '''
        # === FAITHH PATCH: Add knowledge graph context ===
        kg_context = get_kg_context(user_message)
        if kg_context:
            # Inject context into system prompt or prepend to user message
            enhanced_context = kg_context + "\\n\\n" + (context or "")
            context = enhanced_context
        # === END PATCH ===
'''

RESPONSE_INDEX_PATCH = '''
        # === FAITHH PATCH: Auto-index response ===
        if QUALITY_FILTER_ENABLED:
            index_result = auto_index_response(
                ai_response,
                metadata={
                    "source": "faithh_chat",
                    "query_type": query_type if 'query_type' in dir() else "unknown"
                }
            )
            # Optionally log the indexing result
            if index_result.get("tier") == "tier_1_index":
                print(f"📚 Indexed response (score: {index_result.get('score', 0):.2f})")
        # === END PATCH ===
'''


def find_backend_file() -> Path:
    """Find the active backend file."""
    ai_stack = Path.home() / "ai-stack"
    
    candidates = [
        ai_stack / "faithh_professional_backend_fixed.py",
        ai_stack / "faithh_professional_backend.py",
    ]
    
    for path in candidates:
        if path.exists():
            return path
    
    raise FileNotFoundError(
        f"Could not find backend file. Checked: {[str(c) for c in candidates]}"
    )


def create_backup(backend_path: Path) -> Path:
    """Create a timestamped backup of the backend file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backend_path.with_suffix(f".backup_{timestamp}.py")
    shutil.copy2(backend_path, backup_path)
    return backup_path


def patch_backend(backend_path: Path, dry_run: bool = False) -> dict:
    """
    Apply patches to the backend file.
    
    Returns dict with patch status.
    """
    with open(backend_path, 'r') as f:
        content = f.read()
    
    changes = []
    new_content = content
    
    # Check if already patched
    if "FAITHH Quality Filter" in content:
        return {
            "status": "already_patched",
            "message": "Backend already has quality filter patch",
            "changes": []
        }
    
    # 1. Add imports after existing imports
    import_marker = "from flask import"
    if import_marker in new_content:
        # Find end of imports section (first function or class definition)
        lines = new_content.split('\n')
        insert_line = 0
        for i, line in enumerate(lines):
            if line.startswith('def ') or line.startswith('class ') or line.startswith('@app'):
                insert_line = i
                break
        
        if insert_line > 0:
            lines.insert(insert_line, QUALITY_FILTER_IMPORT)
            lines.insert(insert_line + 1, QUALITY_FILTER_INIT)
            lines.insert(insert_line + 2, AUTO_INDEX_FUNCTION)
            new_content = '\n'.join(lines)
            changes.append("Added quality filter imports and initialization")
    
    # 2. Patch the chat endpoint to add knowledge graph context
    # This is trickier - we need to find the right place
    chat_function_marker = "def chat():" 
    if chat_function_marker in new_content and "get_kg_context" not in new_content:
        # Find where user_message is extracted
        if "user_message" in new_content:
            # Add after user_message extraction
            # This is a simplified patch - may need manual adjustment
            changes.append("Note: Manual integration of kg_context may be needed in chat()")
    
    if not changes:
        return {
            "status": "no_changes",
            "message": "No changes needed or patch points not found",
            "changes": []
        }
    
    if dry_run:
        return {
            "status": "dry_run",
            "message": "Would apply the following changes",
            "changes": changes
        }
    
    # Write patched content
    with open(backend_path, 'w') as f:
        f.write(new_content)
    
    return {
        "status": "patched",
        "message": "Successfully patched backend",
        "changes": changes
    }


def copy_modules(target_dir: Path):
    """Copy the quality filter and knowledge graph modules to ai-stack."""
    script_dir = Path(__file__).parent
    
    modules = [
        ("quality_filter.py", "faithh_quality_filter.py"),
        ("knowledge_graph.py", "faithh_knowledge_graph_loader.py"),
    ]
    
    copied = []
    for target_name, source_name in modules:
        source = script_dir / source_name
        target = target_dir / target_name
        
        if source.exists():
            shutil.copy2(source, target)
            copied.append(target_name)
        else:
            # Try without the faithh_ prefix
            alt_source = script_dir / target_name
            if alt_source.exists():
                shutil.copy2(alt_source, target)
                copied.append(target_name)
    
    return copied


def main():
    parser = argparse.ArgumentParser(description="Apply FAITHH backend patches")
    parser.add_argument('--no-backup', action='store_true', help='Skip backup creation')
    parser.add_argument('--dry-run', action='store_true', help='Show changes without applying')
    args = parser.parse_args()
    
    print("=" * 70)
    print("FAITHH Backend Integration Patch")
    print("=" * 70)
    print()
    
    # Find backend
    try:
        backend_path = find_backend_file()
        print(f"📁 Found backend: {backend_path}")
    except FileNotFoundError as e:
        print(f"❌ {e}")
        sys.exit(1)
    
    ai_stack = backend_path.parent
    
    # Copy modules
    print("\n📦 Copying modules...")
    copied = copy_modules(ai_stack)
    for module in copied:
        print(f"   ✅ {module}")
    
    if not copied:
        print("   ⚠️ No modules found to copy. Make sure quality_filter.py and")
        print("      knowledge_graph.py are in the same directory as this script,")
        print("      or manually copy them to ~/ai-stack/")
    
    # Create backup
    if not args.no_backup and not args.dry_run:
        print("\n💾 Creating backup...")
        backup_path = create_backup(backend_path)
        print(f"   ✅ Backup: {backup_path.name}")
    
    # Apply patch
    print("\n🔧 Applying patches...")
    result = patch_backend(backend_path, dry_run=args.dry_run)
    
    print(f"\n   Status: {result['status']}")
    print(f"   {result['message']}")
    
    if result['changes']:
        print("\n   Changes:")
        for change in result['changes']:
            print(f"   - {change}")
    
    # Copy knowledge graph YAML
    kg_source = Path(__file__).parent / "faithh_knowledge_graph.yaml"
    kg_target = ai_stack / "faithh_knowledge_graph.yaml"
    
    if kg_source.exists() and not kg_target.exists():
        if not args.dry_run:
            shutil.copy2(kg_source, kg_target)
        print(f"\n📋 Copied knowledge graph to {kg_target}")
    elif not kg_target.exists():
        print(f"\n⚠️ Knowledge graph YAML not found. Copy faithh_knowledge_graph.yaml to {ai_stack}")
    
    # Instructions
    print("\n" + "=" * 70)
    print("NEXT STEPS")
    print("=" * 70)
    print("""
1. Review the patched backend file for any manual adjustments needed

2. Ensure these files are in ~/ai-stack/:
   - quality_filter.py
   - knowledge_graph.py  
   - faithh_knowledge_graph.yaml

3. Restart the backend:
   pkill -f faithh_professional_backend
   cd ~/ai-stack && source venv/bin/activate
   nohup python faithh_professional_backend_fixed.py > faithh_backend.log 2>&1 &

4. Test the integration:
   - Send a message to FAITHH
   - Check if responses are being filtered and indexed
   - Verify knowledge graph context is being added

5. Monitor the tiered storage:
   - Tier 1 (indexed): Check ChromaDB document count
   - Tier 2 (archived): Check ~/ai-stack/data/tier2_archive.jsonl
   - Negative examples: Check ~/ai-stack/data/negative_examples.jsonl
""")


if __name__ == "__main__":
    main()
