#!/usr/bin/env python3
"""
File Deduplication & Archive Script
Organizes FAITHH repository by archiving duplicates and variants.

Usage:
    python archive_dedupe.py --scan          # Scan for duplicates
    python archive_dedupe.py --dry-run       # Preview archiving
    python archive_dedupe.py --execute       # Execute archiving

Safety:
    - Never deletes files (only moves to ARCHIVE/)
    - Preserves git history with 'git mv'
    - Creates recovery notes
    - Backup recommended before execution
"""

import argparse
import hashlib
import json
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
from collections import defaultdict


# Files that must never be archived/moved
PROTECTED_FILES = {
    "faithh_pet.html",
    "faithh_pet_v4.html",
}


class ArchiveManager:
    """Manages safe archiving and deduplication."""
    
    def __init__(self, repo_root=".", dry_run=True):
        self.repo_root = Path(repo_root)
        self.dry_run = dry_run
        self.archive_root = self.repo_root / "ARCHIVE" / f"{datetime.now().strftime('%Y-%m-%d')}_dedupe"
        
        # Archive categories
        self.categories = {
            "ui_variants": self.archive_root / "ui_variants",
            "scripts_oneoff": self.archive_root / "scripts_oneoff",
            "backend_experiments": self.archive_root / "backend_experiments",
            "export_duplicates": self.archive_root / "export_duplicates"
        }
        
        # Files to archive (from audit reports)
        self.archive_candidates = {
            "ui_variants": [
                "faithh_pet_v4_backup.html",
                "faithh_pet_v4_enhanced_patched.html"
            ],
            "scripts_oneoff": [
                "check_all_dbs.py",
                "check_backup_db.py",
                "analyze_gen8.py",
                "analyze_gen8_deep.py",
                "add_harmony_docs.py"
            ],
            "backend_experiments": [
                "backend/agent_demo.py"
            ]
        }
    
    def create_archive_structure(self):
        """Create archive directory structure."""
        print("\n📁 Creating archive structure...")
        
        for category, path in self.categories.items():
            if self.dry_run:
                print(f"   [DRY RUN] Would create: {path}")
            else:
                path.mkdir(parents=True, exist_ok=True)
                print(f"   ✅ Created: {path}")
    
    def hash_file(self, filepath):
        """Calculate SHA256 hash of file."""
        hasher = hashlib.sha256()
        try:
            with open(filepath, 'rb') as f:
                while chunk := f.read(8192):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception as e:
            print(f"   ⚠️  Could not hash {filepath}: {e}")
            return None
    
    def scan_duplicates(self, base_path="AI_Chat_Exports"):
        """Scan for duplicate files by content hash."""
        print("\n" + "="*60)
        print("SCANNING FOR DUPLICATES")
        print("="*60)
        
        base = self.repo_root / base_path
        if not base.exists():
            print(f"⚠️  Path not found: {base}")
            return {}
        
        print(f"\n🔍 Scanning: {base}")
        
        hashes = defaultdict(list)
        total_files = 0
        
        for filepath in base.rglob("*"):
            if filepath.is_file():
                total_files += 1
                h = self.hash_file(filepath)
                if h:
                    hashes[h].append(filepath)
                
                if total_files % 100 == 0:
                    print(f"   Scanned {total_files} files...", end="\r")
        
        print(f"\n   Scanned {total_files} total files")
        
        # Find duplicates
        duplicates = {h: files for h, files in hashes.items() if len(files) > 1}
        
        if duplicates:
            total_dupes = sum(len(files) - 1 for files in duplicates.values())
            total_size = sum(
                sum(f.stat().st_size for f in files[1:])
                for files in duplicates.values()
            )
            
            print(f"\n📊 Duplicate Summary:")
            print(f"   Duplicate groups: {len(duplicates)}")
            print(f"   Duplicate files: {total_dupes}")
            print(f"   Wasted space: {total_size / 1024 / 1024:.1f} MB")
            
            # Save deduplication map
            dupe_map = {
                "scan_date": datetime.now().isoformat(),
                "base_path": str(base),
                "total_files": total_files,
                "duplicate_groups": len(duplicates),
                "duplicate_files": total_dupes,
                "wasted_bytes": total_size,
                "duplicates": {
                    h: [str(f) for f in files]
                    for h, files in list(duplicates.items())[:100]  # Limit to first 100 groups
                }
            }
            
            map_file = self.categories["export_duplicates"] / "deduplication_map.json"
            
            if self.dry_run:
                print(f"\n🔶 [DRY RUN] Would save map to: {map_file}")
            else:
                map_file.parent.mkdir(parents=True, exist_ok=True)
                with open(map_file, "w") as f:
                    json.dump(dupe_map, f, indent=2)
                print(f"\n✅ Deduplication map saved: {map_file}")
        
        else:
            print("\n✅ No duplicates found")
        
        return duplicates
    
    def archive_file(self, source, category):
        """Archive a single file with git mv."""
        if Path(source).name in PROTECTED_FILES:
            print(f"   ⚠️  Protected file, skipping: {source}")
            return False

        source_path = self.repo_root / source
        
        if not source_path.exists():
            print(f"   ⚠️  File not found: {source}")
            return False
        
        dest_path = self.categories[category] / source_path.name
        
        if self.dry_run:
            print(f"   [DRY RUN] Would move: {source} → {dest_path}")
            return True
        
        try:
            # Use git mv to preserve history
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            result = subprocess.run(
                ["git", "mv", str(source_path), str(dest_path)],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"   ✅ Moved: {source} → {dest_path}")
                return True
            else:
                # Fallback to regular move if not in git
                shutil.move(str(source_path), str(dest_path))
                print(f"   ✅ Moved (non-git): {source} → {dest_path}")
                return True
        
        except Exception as e:
            print(f"   ❌ Failed to move {source}: {e}")
            return False
    
    def process_archive_candidates(self):
        """Archive all identified candidate files."""
        print("\n" + "="*60)
        print("ARCHIVING CANDIDATES")
        print("="*60)
        
        for category, files in self.archive_candidates.items():
            print(f"\n📦 Category: {category}")
            print(f"   Files to archive: {len(files)}")
            
            for file in files:
                self.archive_file(file, category)
    
    def create_recovery_notes(self):
        """Create recovery documentation for archived content."""
        print("\n📝 Creating recovery notes...")
        
        for category, path in self.categories.items():
            readme = path / "README.md"
            
            content = f"""# Archived: {category.replace('_', ' ').title()}
**Archived:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Reason:** Repository cleanup - redundant/superseded files

## Files in This Archive
"""
            
            if category in self.archive_candidates:
                for file in self.archive_candidates[category]:
                    content += f"- `{file}`\n"
            
            content += f"""
## Recovery Instructions
To restore a file from this archive:

```bash
# Copy back to original location
cp {path}/<filename> ./<original_path>

# Or use git to restore and preserve history
git mv {path}/<filename> ./<original_path>
```

## Notes
- These files are not deleted, only moved
- Git history is preserved
- Safe to delete after 30-day safety period
- See ARCHIVE_PLAN.md for full context
"""
            
            if self.dry_run:
                print(f"   [DRY RUN] Would create: {readme}")
            else:
                with open(readme, "w") as f:
                    f.write(content)
                print(f"   ✅ Created: {readme}")
    
    def update_gitignore(self):
        """Update .gitignore to exclude runtime artifacts."""
        print("\n📝 Updating .gitignore...")
        
        gitignore = self.repo_root / ".gitignore"
        
        new_entries = [
            "# Runtime artifacts (added by archive_dedupe.py)",
            "*.log",
            "*.pid",
            ".backend.pid",
            ".server.pid",
            "chroma_db/*.sqlite3",
            "chroma_db/*.sqlite3-*",
            "__pycache__/",
            "*.pyc",
            "*.pyo",
            ""
        ]
        
        if gitignore.exists():
            current = gitignore.read_text()
            
            # Check if already updated
            if "archive_dedupe.py" in current:
                print("   ℹ️  .gitignore already up to date")
                return
            
            if self.dry_run:
                print("   [DRY RUN] Would append to .gitignore:")
                for entry in new_entries:
                    print(f"      {entry}")
            else:
                with open(gitignore, "a") as f:
                    f.write("\n".join(new_entries))
                print("   ✅ Updated .gitignore")
        else:
            print("   ⚠️  .gitignore not found")
    
    def generate_summary(self):
        """Generate final summary report."""
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        
        total_archived = sum(len(files) for files in self.archive_candidates.values())
        
        print(f"\n📊 Archiving Complete:")
        print(f"   Categories: {len(self.categories)}")
        print(f"   Files archived: {total_archived}")
        print(f"   Archive location: {self.archive_root}")
        
        if self.dry_run:
            print("\n🔶 This was a DRY RUN - no changes made")
            print("   To execute: python archive_dedupe.py --execute")
        else:
            print("\n✅ Next steps:")
            print("   1. Review archived files in ARCHIVE/")
            print("   2. Test that system still works")
            print("   3. Commit changes: git add ARCHIVE/ && git commit")
            print("   4. After 30-day safety period, delete ARCHIVE/ if confirmed safe")


def main():
    parser = argparse.ArgumentParser(description="Deduplicate and archive FAITHH repository files")
    parser.add_argument("--scan", action="store_true", help="Scan for duplicate files only")
    parser.add_argument("--dry-run", action="store_true", help="Preview archiving without making changes")
    parser.add_argument("--execute", action="store_true", help="Execute archiving (no dry run)")
    
    args = parser.parse_args()
    
    # Default to dry run unless --execute specified
    dry_run = not args.execute
    
    print("="*60)
    print("FAITHH Repository Deduplication & Archiving")
    print("="*60)
    
    if dry_run and not args.scan:
        print("🔶 DRY RUN MODE - No changes will be made")
        print("   Use --execute to perform actual archiving")
    
    manager = ArchiveManager(repo_root=".", dry_run=dry_run)
    
    # Create archive structure
    manager.create_archive_structure()
    
    # Scan for duplicates if requested
    if args.scan:
        duplicates = manager.scan_duplicates("AI_Chat_Exports")
        
        if duplicates:
            print("\n💡 Recommendation:")
            print("   Large duplicate sets found in AI_Chat_Exports/")
            print("   Consider cleaning these up manually or with a dedicated script")
        
        return
    
    # Archive candidates
    manager.process_archive_candidates()
    
    # Create recovery notes
    manager.create_recovery_notes()
    
    # Update .gitignore
    manager.update_gitignore()
    
    # Generate summary
    manager.generate_summary()


if __name__ == "__main__":
    main()
