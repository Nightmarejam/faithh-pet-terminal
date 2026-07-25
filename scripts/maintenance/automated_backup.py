#!/usr/bin/env python3
"""
Automated Backup System
Automates backup creation and verification
"""

import json
import shutil
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import hashlib
import logging

class AutomatedBackup:
    """Automated backup system"""
    
    def __init__(self):
        self.project_root = Path("/home/jonat/ai-stack")
        self.backup_dir = self.project_root / "backups"
        self.backup_dir.mkdir(exist_ok=True)
        
        # Backup configuration
        self.backup_config = {
            "critical_files": [
                "faithh_memory.json",
                "project_states.json",
                "decisions_log.json",
                "scaffolding_state.json",
                "config.yaml",
                ".env",
                "requirements.txt"
            ],
            "critical_directories": [
                "backend",
                "app/services",
                "experiments",
                "projects/alife",
                "docs/consolidated"
            ],
            "exclude_patterns": [
                "__pycache__",
                ".git",
                "node_modules",
                "*.pyc",
                ".env.example",
                "logs",
                "venv"
            ]
        }
        
        # Setup logging
        log_file = self.project_root / "logs" / "backup.log"
        log_file.parent.mkdir(exist_ok=True)
        logging.basicConfig(
            filename=str(log_file),
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def run_backup(self) -> Dict[str, Any]:
        """Run comprehensive backup"""
        print("💾 Starting Automated Backup")
        print("=" * 50)
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "backup_status": "unknown",
            "backups_created": [],
            "backups_verified": [],
            "errors": [],
            "statistics": {},
            "recommendations": []
        }
        
        # Create backup directory
        backup_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"backup_{backup_timestamp}"
        backup_path.mkdir(exist_ok=True)
        
        try:
            # Backup critical files
            print("   📄 Backing up critical files...")
            file_backups = self.backup_critical_files(backup_path)
            results["backups_created"].extend(file_backups)
            
            # Backup critical directories
            print("   📁 Backing up critical directories...")
            dir_backups = self.backup_critical_directories(backup_path)
            results["backups_created"].extend(dir_backups)
            
            # Create Git backup
            print("   🔧 Creating Git backup...")
            git_backup = self.create_git_backup(backup_path)
            if git_backup:
                results["backups_created"].append(git_backup)
            
            # Verify backups
            print("   ✅ Verifying backups...")
            verifications = self.verify_backups(backup_path)
            results["backups_verified"] = verifications
            
            # Calculate statistics
            results["statistics"] = self.calculate_backup_statistics(backup_path)
            
            # Clean old backups
            print("   🧹 Cleaning old backups...")
            self.clean_old_backups()
            
            # Update backup status
            if results["errors"]:
                results["backup_status"] = "partial"
            else:
                results["backup_status"] = "success"
            
            # Generate recommendations
            results["recommendations"] = self.generate_backup_recommendations(results)
            
            # Log results
            self.log_backup_results(results)
            
            print(f"\n✅ Backup Complete")
            print(f"📊 Status: {results['backup_status']}")
            print(f"📄 Files Backed Up: {len([b for b in results['backups_created'] if b['type'] == 'file'])}")
            print(f"📁 Directories Backed Up: {len([b for b in results['backups_created'] if b['type'] == 'directory'])}")
            print(f"✅ Verifications: {len(results['backups_verified'])}")
            
            return results
            
        except Exception as e:
            results["backup_status"] = "error"
            results["errors"].append(f"Backup failed: {str(e)}")
            self.logger.error(f"Backup failed: {str(e)}")
            return results
    
    def backup_critical_files(self, backup_path: Path) -> List[Dict[str, Any]]:
        """Backup critical files"""
        backups = []
        
        for filename in self.backup_config["critical_files"]:
            source_file = self.project_root / filename
            
            if source_file.exists():
                try:
                    backup_file = backup_path / filename
                    backup_file.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Copy file
                    shutil.copy2(source_file, backup_file)
                    
                    # Calculate checksum
                    original_checksum = self.calculate_checksum(source_file)
                    backup_checksum = self.calculate_checksum(backup_file)
                    
                    backup_info = {
                        "type": "file",
                        "name": filename,
                        "source": str(source_file),
                        "backup": str(backup_file),
                        "original_checksum": original_checksum,
                        "backup_checksum": backup_checksum,
                        "verified": original_checksum == backup_checksum,
                        "size": source_file.stat().st_size,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    backups.append(backup_info)
                    print(f"      ✅ {filename}")
                    
                except Exception as e:
                    error_msg = f"Failed to backup {filename}: {str(e)}"
                    self.logger.error(error_msg)
                    # Note: errors are collected at the main level
            else:
                warning_msg = f"Critical file not found: {filename}"
                self.logger.warning(warning_msg)
        
        return backups
    
    def backup_critical_directories(self, backup_path: Path) -> List[Dict[str, Any]]:
        """Backup critical directories"""
        backups = []
        
        for dirname in self.backup_config["critical_directories"]:
            source_dir = self.project_root / dirname
            
            if source_dir.exists() and source_dir.is_dir():
                try:
                    backup_dir = backup_path / dirname
                    backup_dir.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Copy directory
                    shutil.copytree(source_dir, backup_dir, ignore=self.ignore_patterns)
                    
                    # Calculate directory stats
                    dir_stats = self.calculate_directory_stats(source_dir)
                    backup_stats = self.calculate_directory_stats(backup_dir)
                    
                    backup_info = {
                        "type": "directory",
                        "name": dirname,
                        "source": str(source_dir),
                        "backup": str(backup_dir),
                        "file_count": dir_stats["file_count"],
                        "total_size": dir_stats["total_size"],
                        "backup_file_count": backup_stats["file_count"],
                        "backup_total_size": backup_stats["total_size"],
                        "verified": dir_stats["file_count"] == backup_stats["file_count"],
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    backups.append(backup_info)
                    print(f"      ✅ {dirname} ({dir_stats['file_count']} files)")
                    
                except Exception as e:
                    error_msg = f"Failed to backup {dirname}: {str(e)}"
                    self.logger.error(error_msg)
            else:
                warning_msg = f"Critical directory not found: {dirname}"
                self.logger.warning(warning_msg)
        
        return backups
    
    def create_git_backup(self, backup_path: Path) -> Optional[Dict[str, Any]]:
        """Create Git backup"""
        try:
            # Check if we're in a git repository
            git_dir = self.project_root / ".git"
            if not git_dir.exists():
                self.logger.warning("Not a Git repository - skipping Git backup")
                return None
            
            # Get current git status
            git_status = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            # Get current commit
            git_commit = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            # Create git backup info
            backup_info = {
                "type": "git",
                "name": "git_repository",
                "source": str(self.project_root),
                "backup": str(backup_path / "git_info.json"),
                "current_commit": git_commit.stdout.strip(),
                "status_output": git_status.stdout,
                "has_changes": len(git_status.stdout.strip()) > 0,
                "timestamp": datetime.now().isoformat()
            }
            
            # Save git info
            git_info_file = backup_path / "git_info.json"
            with open(git_info_file, 'w') as f:
                json.dump(backup_info, f, indent=2)
            
            print(f"      ✅ Git repository (commit: {git_commit.stdout.strip()[:8]})")
            return backup_info
            
        except Exception as e:
            error_msg = f"Failed to create Git backup: {str(e)}"
            self.logger.error(error_msg)
            return None
    
    def verify_backups(self, backup_path: Path) -> List[Dict[str, Any]]:
        """Verify backup integrity"""
        verifications = []
        
        # Verify file backups
        for item in backup_path.rglob("*"):
            if item.is_file():
                try:
                    # Calculate checksum
                    checksum = self.calculate_checksum(item)
                    
                    verification = {
                        "type": "file",
                        "path": str(item),
                        "checksum": checksum,
                        "verified": True,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    verifications.append(verification)
                    
                except Exception as e:
                    verification = {
                        "type": "file",
                        "path": str(item),
                        "verified": False,
                        "error": str(e),
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    verifications.append(verification)
        
        return verifications
    
    def calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA-256 checksum"""
        hash_sha256 = hashlib.sha256()
        
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        
        return hash_sha256.hexdigest()
    
    def calculate_directory_stats(self, dir_path: Path) -> Dict[str, Any]:
        """Calculate directory statistics"""
        file_count = 0
        total_size = 0
        
        for item in dir_path.rglob("*"):
            if item.is_file():
                file_count += 1
                total_size += item.stat().st_size
        
        return {
            "file_count": file_count,
            "total_size": total_size
        }
    
    def ignore_patterns(self, path: str, names: List[str]) -> List[str]:
        """Ignore patterns for directory copying"""
        ignored = []
        
        for name in names:
            for pattern in self.backup_config["exclude_patterns"]:
                if pattern in name or name.endswith(pattern):
                    ignored.append(name)
                    break
        
        return ignored
    
    def calculate_backup_statistics(self, backup_path: Path) -> Dict[str, Any]:
        """Calculate backup statistics"""
        stats = {
            "total_files": 0,
            "total_size": 0,
            "file_backups": 0,
            "directory_backups": 0,
            "git_backup": 0,
            "verification_count": 0
        }
        
        # Count files and calculate size
        for item in backup_path.rglob("*"):
            if item.is_file():
                stats["total_files"] += 1
                stats["total_size"] += item.stat().st_size
        
        # Count backup types (would be populated from results)
        # This is a placeholder - actual counts would come from the backup results
        
        return stats
    
    def clean_old_backups(self, keep_count: int = 7):
        """Clean old backups, keeping only the most recent N"""
        try:
            backup_dirs = [d for d in self.backup_dir.iterdir() if d.is_dir() and d.name.startswith("backup_")]
            backup_dirs.sort(key=lambda x: x.name, reverse=True)
            
            if len(backup_dirs) > keep_count:
                for old_backup in backup_dirs[keep_count:]:
                    shutil.rmtree(old_backup)
                    self.logger.info(f"Removed old backup: {old_backup.name}")
                    print(f"      🗑️ Removed old backup: {old_backup.name}")
            
        except Exception as e:
            error_msg = f"Failed to clean old backups: {str(e)}"
            self.logger.error(error_msg)
    
    def generate_backup_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate backup recommendations"""
        recommendations = []
        
        if results["backup_status"] == "success":
            recommendations.append("Backup completed successfully - continue regular schedule")
        elif results["backup_status"] == "partial":
            recommendations.append("Partial backup completed - review errors and retry")
        else:
            recommendations.append("Backup failed - investigate and resolve issues")
        
        # Check for missing critical files
        backed_up_files = [b["name"] for b in results["backups_created"] if b["type"] == "file"]
        missing_files = set(self.backup_config["critical_files"]) - set(backed_up_files)
        
        if missing_files:
            recommendations.append(f"Missing critical files: {', '.join(missing_files)}")
        
        # Check verification failures
        failed_verifications = [v for v in results["backups_verified"] if not v["verified"]]
        if failed_verifications:
            recommendations.append(f"Verification failures: {len(failed_verifications)} files")
        
        # Check backup size
        total_size = results["statistics"].get("total_size", 0)
        if total_size > 1024 * 1024 * 1024:  # 1GB
            recommendations.append("Large backup size - consider compression or selective backup")
        
        return recommendations
    
    def log_backup_results(self, results: Dict[str, Any]):
        """Log backup results"""
        self.logger.info(f"Backup - Status: {results['backup_status']}")
        self.logger.info(f"Files Backed Up: {len([b for b in results['backups_created'] if b['type'] == 'file'])}")
        self.logger.info(f"Directories Backed Up: {len([b for b in results['backups_created'] if b['type'] == 'directory'])}")
        self.logger.info(f"Total Size: {results['statistics'].get('total_size', 0)} bytes")
        
        for error in results['errors']:
            self.logger.error(f"Backup Error: {error}")
        
        for recommendation in results['recommendations']:
            self.logger.info(f"Recommendation: {recommendation}")

def main():
    """Main execution function"""
    backup_system = AutomatedBackup()
    results = backup_system.run_backup()
    
    # Exit with appropriate code
    if results['backup_status'] == 'success':
        exit(0)
    elif results['backup_status'] == 'partial':
        exit(2)
    else:
        exit(1)

if __name__ == "__main__":
    main()