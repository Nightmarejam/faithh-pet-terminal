#!/usr/bin/env python3
"""
FAITHH Knowledge Graph Sync
Handles syncing the knowledge graph between sessions, git, and instances.

Supports multiple sync strategies:
1. Git-based sync (push/pull from repo)
2. File-based sync (copy between locations)
3. API-based sync (future: cloud sync)

Usage:
    python kg_sync.py status          # Show current status
    python kg_sync.py pull            # Pull latest from git
    python kg_sync.py push            # Push changes to git
    python kg_sync.py backup          # Create local backup
    python kg_sync.py regenerate      # Regenerate markdown docs
"""

import subprocess
import shutil
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List
import argparse
import hashlib


class KGSync:
    """Knowledge Graph synchronization manager."""
    
    def __init__(self, kg_path: Path = None, repo_path: Path = None):
        """
        Initialize sync manager.
        
        Args:
            kg_path: Path to knowledge graph YAML
            repo_path: Path to git repository root
        """
        self.ai_stack = Path.home() / "ai-stack"
        self.kg_path = kg_path or self.ai_stack / "faithh_knowledge_graph.yaml"
        self.repo_path = repo_path or self.ai_stack
        self.backup_dir = self.ai_stack / "backups" / "knowledge_graph"
        self.docs_dir = self.ai_stack / "docs" / "generated"
        
        # Ensure directories exist
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.docs_dir.mkdir(parents=True, exist_ok=True)
    
    def get_file_hash(self, path: Path) -> Optional[str]:
        """Get MD5 hash of a file."""
        if not path.exists():
            return None
        return hashlib.md5(path.read_bytes()).hexdigest()
    
    def get_status(self) -> Dict:
        """Get current sync status."""
        status = {
            "kg_exists": self.kg_path.exists(),
            "kg_path": str(self.kg_path),
            "kg_hash": self.get_file_hash(self.kg_path),
            "kg_modified": None,
            "git_status": None,
            "backups": [],
            "docs_generated": []
        }
        
        if self.kg_path.exists():
            stat = self.kg_path.stat()
            status["kg_modified"] = datetime.fromtimestamp(stat.st_mtime).isoformat()
            status["kg_size"] = stat.st_size
        
        # Check git status
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain", str(self.kg_path)],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                status["git_status"] = result.stdout.strip() or "clean"
            else:
                status["git_status"] = "not a git repo"
        except Exception as e:
            status["git_status"] = f"error: {e}"
        
        # List backups
        if self.backup_dir.exists():
            backups = sorted(self.backup_dir.glob("*.yaml"), reverse=True)[:5]
            status["backups"] = [b.name for b in backups]
        
        # List generated docs
        if self.docs_dir.exists():
            docs = list(self.docs_dir.glob("*.md"))
            status["docs_generated"] = [d.name for d in docs]
        
        return status
    
    def backup(self, tag: str = None) -> Path:
        """
        Create a backup of the knowledge graph.
        
        Args:
            tag: Optional tag for the backup (default: timestamp)
            
        Returns:
            Path to backup file
        """
        if not self.kg_path.exists():
            raise FileNotFoundError(f"Knowledge graph not found: {self.kg_path}")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        tag_suffix = f"_{tag}" if tag else ""
        backup_name = f"kg_backup_{timestamp}{tag_suffix}.yaml"
        backup_path = self.backup_dir / backup_name
        
        shutil.copy2(self.kg_path, backup_path)
        
        # Also save metadata
        meta_path = backup_path.with_suffix(".meta.json")
        meta = {
            "original_path": str(self.kg_path),
            "backup_time": datetime.now().isoformat(),
            "original_hash": self.get_file_hash(self.kg_path),
            "tag": tag
        }
        meta_path.write_text(json.dumps(meta, indent=2))
        
        # Clean old backups (keep last 10)
        self._cleanup_old_backups(keep=10)
        
        return backup_path
    
    def _cleanup_old_backups(self, keep: int = 10):
        """Remove old backups, keeping the most recent ones."""
        backups = sorted(self.backup_dir.glob("*.yaml"), reverse=True)
        for old_backup in backups[keep:]:
            old_backup.unlink()
            meta = old_backup.with_suffix(".meta.json")
            if meta.exists():
                meta.unlink()
    
    def restore(self, backup_name: str = None) -> bool:
        """
        Restore from a backup.
        
        Args:
            backup_name: Name of backup to restore (default: most recent)
            
        Returns:
            True if restored successfully
        """
        if backup_name:
            backup_path = self.backup_dir / backup_name
        else:
            backups = sorted(self.backup_dir.glob("*.yaml"), reverse=True)
            if not backups:
                raise FileNotFoundError("No backups found")
            backup_path = backups[0]
        
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup not found: {backup_path}")
        
        # Backup current before restoring
        if self.kg_path.exists():
            self.backup(tag="pre_restore")
        
        shutil.copy2(backup_path, self.kg_path)
        return True
    
    def git_pull(self) -> Dict:
        """Pull latest knowledge graph from git."""
        try:
            # First, backup current state
            if self.kg_path.exists():
                self.backup(tag="pre_pull")
            
            # Pull from remote
            result = subprocess.run(
                ["git", "pull", "origin", "main"],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def git_push(self, message: str = None) -> Dict:
        """Push knowledge graph changes to git."""
        try:
            # Add the file
            subprocess.run(
                ["git", "add", str(self.kg_path)],
                cwd=self.repo_path,
                check=True
            )
            
            # Commit
            commit_msg = message or f"Update knowledge graph {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            result = subprocess.run(
                ["git", "commit", "-m", commit_msg],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0 and "nothing to commit" in result.stdout:
                return {"success": True, "message": "No changes to commit"}
            
            # Push
            push_result = subprocess.run(
                ["git", "push", "origin", "main"],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            return {
                "success": push_result.returncode == 0,
                "commit_output": result.stdout,
                "push_output": push_result.stdout,
                "error": push_result.stderr if push_result.returncode != 0 else None
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def regenerate_docs(self) -> List[Path]:
        """Regenerate markdown docs from knowledge graph."""
        generated = []
        
        # Try to import and use the generator
        try:
            # Add parent dir to path for import
            import sys
            sys.path.insert(0, str(self.ai_stack))
            
            from generate_docs import (
                load_knowledge_graph,
                generate_roadmap,
                generate_project_map,
                generate_indexing_spec
            )
            
            kg = load_knowledge_graph(str(self.kg_path))
            
            docs = [
                ("ROADMAP.md", generate_roadmap(kg)),
                ("PROJECT_MAP.md", generate_project_map(kg)),
                ("INDEXING_SPEC.md", generate_indexing_spec(kg)),
            ]
            
            for filename, content in docs:
                path = self.docs_dir / filename
                path.write_text(content)
                generated.append(path)
            
        except ImportError:
            # Fall back to subprocess
            generator = self.ai_stack / "generate_docs.py"
            if generator.exists():
                result = subprocess.run(
                    ["python3", str(generator), str(self.kg_path), "--output", str(self.docs_dir)],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    generated = list(self.docs_dir.glob("*.md"))
        
        return generated
    
    def add_decision(self, decision: str, reasoning: str) -> bool:
        """
        Add a decision to the knowledge graph and optionally commit.
        
        This is a convenience method for updating the decisions log.
        """
        try:
            from knowledge_graph import KnowledgeGraph
            
            kg = KnowledgeGraph(self.kg_path)
            kg.load()
            success = kg.add_decision(decision, reasoning)
            
            if success:
                # Regenerate docs
                self.regenerate_docs()
            
            return success
        except Exception as e:
            print(f"Error adding decision: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(description="FAITHH Knowledge Graph Sync")
    parser.add_argument('command', choices=['status', 'pull', 'push', 'backup', 'restore', 'regenerate', 'decision'])
    parser.add_argument('--message', '-m', help='Commit message for push')
    parser.add_argument('--backup-name', help='Backup name for restore')
    parser.add_argument('--decision', help='Decision text (for decision command)')
    parser.add_argument('--reasoning', help='Reasoning text (for decision command)')
    args = parser.parse_args()
    
    sync = KGSync()
    
    print("=" * 70)
    print("FAITHH Knowledge Graph Sync")
    print("=" * 70)
    print()
    
    if args.command == 'status':
        status = sync.get_status()
        print(f"📁 Knowledge Graph: {status['kg_path']}")
        print(f"   Exists: {'✅' if status['kg_exists'] else '❌'}")
        if status['kg_exists']:
            print(f"   Modified: {status['kg_modified']}")
            print(f"   Size: {status.get('kg_size', 0)} bytes")
            print(f"   Hash: {status['kg_hash'][:12]}...")
        print(f"\n📊 Git Status: {status['git_status']}")
        print(f"\n💾 Recent Backups:")
        for b in status['backups'][:5]:
            print(f"   - {b}")
        print(f"\n📄 Generated Docs:")
        for d in status['docs_generated']:
            print(f"   - {d}")
    
    elif args.command == 'pull':
        print("⬇️ Pulling from git...")
        result = sync.git_pull()
        if result['success']:
            print("✅ Pull successful")
            if result.get('output'):
                print(result['output'])
        else:
            print(f"❌ Pull failed: {result.get('error')}")
    
    elif args.command == 'push':
        print("⬆️ Pushing to git...")
        result = sync.git_push(args.message)
        if result['success']:
            print("✅ Push successful")
            if result.get('message'):
                print(result['message'])
        else:
            print(f"❌ Push failed: {result.get('error')}")
    
    elif args.command == 'backup':
        print("💾 Creating backup...")
        try:
            path = sync.backup()
            print(f"✅ Backup created: {path.name}")
        except Exception as e:
            print(f"❌ Backup failed: {e}")
    
    elif args.command == 'restore':
        print("♻️ Restoring from backup...")
        try:
            sync.restore(args.backup_name)
            print("✅ Restore successful")
        except Exception as e:
            print(f"❌ Restore failed: {e}")
    
    elif args.command == 'regenerate':
        print("📝 Regenerating docs...")
        try:
            docs = sync.regenerate_docs()
            print(f"✅ Generated {len(docs)} documents:")
            for d in docs:
                print(f"   - {d.name}")
        except Exception as e:
            print(f"❌ Generation failed: {e}")
    
    elif args.command == 'decision':
        if not args.decision or not args.reasoning:
            print("❌ Both --decision and --reasoning are required")
            return
        print("📋 Adding decision...")
        if sync.add_decision(args.decision, args.reasoning):
            print("✅ Decision added and docs regenerated")
        else:
            print("❌ Failed to add decision")


if __name__ == "__main__":
    main()
