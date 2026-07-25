#!/usr/bin/env python3
"""
FAITHH Ecosystem Analysis Script
Analyzes the project for duplicates, consistency, and multi-device deployment readiness.
"""

import os
import json
import hashlib
import subprocess
from pathlib import Path
from collections import defaultdict
from datetime import datetime

class EcosystemAnalyzer:
    def __init__(self, root_path="/home/jonat/ai-stack"):
        self.root = Path(root_path)
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "duplicates": {},
            "backend_files": [],
            "frontend_files": [],
            "config_files": [],
            "state_files": [],
            "archive_candidates": [],
            "consistency_issues": [],
            "system_requirements": {},
            "deployment_readiness": {}
        }
        
    def calculate_file_hash(self, filepath):
        """Calculate MD5 hash of file content."""
        try:
            with open(filepath, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception as e:
            return None
            
    def find_duplicates(self):
        """Find duplicate files by content hash."""
        print("🔍 Scanning for duplicate files...")
        hash_map = defaultdict(list)
        
        exclude_dirs = {'venv', '.git', '__pycache__', 'node_modules', 'chroma_db', 
                       'models', 'backups', '.aider.tags.cache.v4'}
        exclude_exts = {'.pyc', '.pyo', '.so', '.dylib', '.dll', '.png', '.jpg', 
                       '.jpeg', '.gif', '.ico', '.svg', '.woff', '.woff2', '.ttf'}
        
        for filepath in self.root.rglob('*'):
            if filepath.is_file():
                if any(ex in filepath.parts for ex in exclude_dirs):
                    continue
                if filepath.suffix in exclude_exts:
                    continue
                if filepath.stat().st_size > 10_000_000:
                    continue
                    
                file_hash = self.calculate_file_hash(filepath)
                if file_hash:
                    hash_map[file_hash].append(str(filepath.relative_to(self.root)))
        
        duplicates = {h: files for h, files in hash_map.items() if len(files) > 1}
        self.results["duplicates"] = duplicates
        print(f"   Found {len(duplicates)} sets of duplicate files")
        
    def analyze_backend_files(self):
        """Analyze backend Python files for consistency."""
        print("🐍 Analyzing backend files...")
        
        backend_patterns = ['*backend*.py', '*api*.py', '*server*.py']
        backend_files = []
        
        for pattern in backend_patterns:
            for filepath in self.root.rglob(pattern):
                if 'venv' not in filepath.parts and '__pycache__' not in filepath.parts:
                    rel_path = filepath.relative_to(self.root)
                    size = filepath.stat().st_size
                    backend_files.append({
                        "path": str(rel_path),
                        "size": size,
                        "modified": datetime.fromtimestamp(filepath.stat().st_mtime).isoformat()
                    })
        
        self.results["backend_files"] = sorted(backend_files, key=lambda x: x["size"], reverse=True)
        print(f"   Found {len(backend_files)} backend-related files")
        
    def analyze_frontend_files(self):
        """Analyze frontend HTML files."""
        print("🌐 Analyzing frontend files...")
        
        frontend_files = []
        for filepath in self.root.rglob('*.html'):
            if 'venv' not in filepath.parts:
                rel_path = filepath.relative_to(self.root)
                size = filepath.stat().st_size
                frontend_files.append({
                    "path": str(rel_path),
                    "size": size,
                    "modified": datetime.fromtimestamp(filepath.stat().st_mtime).isoformat()
                })
        
        self.results["frontend_files"] = sorted(frontend_files, key=lambda x: x["size"], reverse=True)
        print(f"   Found {len(frontend_files)} HTML files")
        
    def analyze_config_files(self):
        """Analyze configuration files."""
        print("⚙️  Analyzing configuration files...")
        
        config_patterns = ['*.yaml', '*.yml', '*.env*', '*.json', '*.toml', '*.ini']
        config_files = []
        
        for pattern in config_patterns:
            for filepath in self.root.glob(pattern):
                if filepath.is_file():
                    rel_path = filepath.relative_to(self.root)
                    config_files.append({
                        "path": str(rel_path),
                        "type": filepath.suffix,
                        "size": filepath.stat().st_size
                    })
        
        self.results["config_files"] = config_files
        print(f"   Found {len(config_files)} configuration files in root")
        
    def analyze_state_files(self):
        """Analyze state/data JSON files."""
        print("📋 Analyzing state files...")
        
        state_patterns = ['*_memory.json', '*_log.json', '*_state*.json', 
                         'project_states.json', 'decisions_log.json']
        state_files = []
        
        for pattern in state_patterns:
            for filepath in self.root.glob(pattern):
                if filepath.is_file():
                    rel_path = filepath.relative_to(self.root)
                    state_files.append({
                        "path": str(rel_path),
                        "size": filepath.stat().st_size,
                        "modified": datetime.fromtimestamp(filepath.stat().st_mtime).isoformat()
                    })
        
        self.results["state_files"] = state_files
        print(f"   Found {len(state_files)} state files")
        
    def identify_archive_candidates(self):
        """Identify files that could be archived."""
        print("📦 Identifying archive candidates...")
        
        candidates = []
        
        # Old session summaries in root
        for filepath in self.root.glob('SESSION_*.md'):
            candidates.append({
                "path": str(filepath.relative_to(self.root)),
                "reason": "Old session summary in root",
                "suggest_move": "archive/sessions/"
            })
        
        # Old handoff docs in root
        for filepath in self.root.glob('HANDOFF_*.md'):
            candidates.append({
                "path": str(filepath.relative_to(self.root)),
                "reason": "Handoff document in root",
                "suggest_move": "archive/handoffs/"
            })
        
        # Backup files
        for filepath in self.root.rglob('*.bak'):
            if 'venv' not in filepath.parts:
                candidates.append({
                    "path": str(filepath.relative_to(self.root)),
                    "reason": "Backup file",
                    "suggest_move": "backups/"
                })
        
        self.results["archive_candidates"] = candidates
        print(f"   Found {len(candidates)} archive candidates")
        
    def check_consistency(self):
        """Check for consistency issues."""
        print("🔧 Checking consistency...")
        
        issues = []
        
        # Check for multiple backend entry points
        backend_entry_points = [
            'faithh_professional_backend.py',
            'faithh_professional_backend_fixed.py'
        ]
        existing_backends = [f for f in backend_entry_points if (self.root / f).exists()]
        if len(existing_backends) > 1:
            issues.append({
                "type": "multiple_backends",
                "severity": "medium",
                "description": f"Multiple backend entry points: {existing_backends}",
                "recommendation": "Consolidate to single canonical backend"
            })
        
        # Check for multiple UI versions
        ui_files = list(self.root.glob('faithh_pet*.html'))
        if len(ui_files) > 2:
            issues.append({
                "type": "multiple_uis",
                "severity": "low",
                "description": f"Multiple UI versions in root: {[f.name for f in ui_files]}",
                "recommendation": "Keep only canonical UI in root, move others to archive"
            })
        
        # Check for duplicate archive directories
        if (self.root / 'archive').exists() and (self.root / 'ARCHIVE').exists():
            issues.append({
                "type": "duplicate_archive",
                "severity": "low",
                "description": "Both 'archive' and 'ARCHIVE' directories exist",
                "recommendation": "Consolidate to single archive directory"
            })
        
        self.results["consistency_issues"] = issues
        print(f"   Found {len(issues)} consistency issues")
        
    def analyze_system_requirements(self):
        """Analyze system requirements from docker-compose and configs."""
        print("💻 Analyzing system requirements...")
        
        requirements = {
            "gpu": {"required": False, "details": []},
            "memory": {"minimum_gb": 0, "recommended_gb": 0},
            "storage": {"minimum_gb": 0},
            "ports": [],
            "services": []
        }
        
        # Parse docker-compose.yml
        docker_compose = self.root / 'docker-compose.yml'
        if docker_compose.exists():
            with open(docker_compose) as f:
                content = f.read()
                
                # Check for GPU requirements
                if 'nvidia' in content or 'gpu' in content.lower():
                    requirements["gpu"]["required"] = True
                    requirements["gpu"]["details"].append("NVIDIA GPU required for Ollama containers")
                
                # Extract memory limits
                import re
                memory_matches = re.findall(r'memory:\s*(\d+)G', content)
                if memory_matches:
                    total_memory = sum(int(m) for m in memory_matches)
                    requirements["memory"]["minimum_gb"] = total_memory
                    requirements["memory"]["recommended_gb"] = total_memory + 8
                
                # Extract ports
                port_matches = re.findall(r'"(\d+):\d+"', content)
                requirements["ports"] = sorted(set(port_matches))
                
                # Extract services
                service_matches = re.findall(r'^\s{2}(\w+):', content, re.MULTILINE)
                requirements["services"] = service_matches
        
        # Check storage requirements
        try:
            result = subprocess.run(['du', '-sb', str(self.root)], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                bytes_used = int(result.stdout.split()[0])
                gb_used = bytes_used / (1024**3)
                requirements["storage"]["minimum_gb"] = round(gb_used + 10, 1)
        except:
            pass
        
        self.results["system_requirements"] = requirements
        print(f"   GPU Required: {requirements['gpu']['required']}")
        print(f"   Memory: {requirements['memory']['minimum_gb']}GB minimum")
        print(f"   Services: {', '.join(requirements['services'])}")
        
    def assess_deployment_readiness(self):
        """Assess readiness for multi-device deployment."""
        print("🚀 Assessing deployment readiness...")
        
        readiness = {
            "docker_ready": False,
            "config_portable": False,
            "dependencies_documented": False,
            "blockers": [],
            "recommendations": []
        }
        
        # Check Docker setup
        if (self.root / 'docker-compose.yml').exists():
            readiness["docker_ready"] = True
        else:
            readiness["blockers"].append("No docker-compose.yml found")
        
        # Check for portable configuration
        if (self.root / 'config.yaml').exists() and (self.root / '.env.example').exists():
            readiness["config_portable"] = True
        else:
            readiness["blockers"].append("Missing config.yaml or .env.example")
        
        # Check dependencies
        if (self.root / 'requirements.txt').exists():
            readiness["dependencies_documented"] = True
        else:
            readiness["blockers"].append("No requirements.txt found")
        
        # Recommendations for multi-device setup
        readiness["recommendations"] = [
            "Use Tailscale or VPN for secure cross-device communication",
            "Centralize ChromaDB on Gen8 server for shared knowledge base",
            "Run Ollama on Gen8 with GPU, expose via network",
            "Use NAS for shared storage (AI_Chat_Exports, backups)",
            "Deploy backend on Gen8, access from MacBook/Windows via browser",
            "Consider Docker Swarm or K3s for orchestration across devices"
        ]
        
        self.results["deployment_readiness"] = readiness
        print(f"   Docker Ready: {readiness['docker_ready']}")
        print(f"   Config Portable: {readiness['config_portable']}")
        print(f"   Blockers: {len(readiness['blockers'])}")
        
    def generate_report(self):
        """Generate comprehensive analysis report."""
        report_path = self.root / 'reports' / f'ecosystem_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        report_path.parent.mkdir(exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n📄 Full report saved to: {report_path}")
        
        # Generate human-readable summary
        summary_path = report_path.with_suffix('.md')
        self.generate_markdown_summary(summary_path)
        print(f"📄 Summary saved to: {summary_path}")
        
        return report_path
        
    def generate_markdown_summary(self, output_path):
        """Generate human-readable markdown summary."""
        with open(output_path, 'w') as f:
            f.write("# FAITHH Ecosystem Analysis Report\n\n")
            f.write(f"**Generated**: {self.results['timestamp']}\n\n")
            
            f.write("## 📊 Summary\n\n")
            f.write(f"- **Duplicate file sets**: {len(self.results['duplicates'])}\n")
            f.write(f"- **Backend files**: {len(self.results['backend_files'])}\n")
            f.write(f"- **Frontend files**: {len(self.results['frontend_files'])}\n")
            f.write(f"- **Archive candidates**: {len(self.results['archive_candidates'])}\n")
            f.write(f"- **Consistency issues**: {len(self.results['consistency_issues'])}\n\n")
            
            f.write("## 🔍 Duplicate Files\n\n")
            if self.results['duplicates']:
                for hash_val, files in list(self.results['duplicates'].items())[:10]:
                    f.write(f"### Duplicate Set\n")
                    for file in files:
                        f.write(f"- `{file}`\n")
                    f.write("\n")
            else:
                f.write("No duplicates found.\n\n")
            
            f.write("## 🐍 Backend Files\n\n")
            for bf in self.results['backend_files'][:10]:
                f.write(f"- `{bf['path']}` ({bf['size']} bytes)\n")
            f.write("\n")
            
            f.write("## 🌐 Frontend Files\n\n")
            for ff in self.results['frontend_files'][:10]:
                f.write(f"- `{ff['path']}` ({ff['size']} bytes)\n")
            f.write("\n")
            
            f.write("## ⚠️ Consistency Issues\n\n")
            for issue in self.results['consistency_issues']:
                f.write(f"### {issue['type']} (Severity: {issue['severity']})\n")
                f.write(f"**Description**: {issue['description']}\n\n")
                f.write(f"**Recommendation**: {issue['recommendation']}\n\n")
            
            f.write("## 💻 System Requirements\n\n")
            req = self.results['system_requirements']
            f.write(f"- **GPU Required**: {req.get('gpu', {}).get('required', False)}\n")
            f.write(f"- **Memory**: {req.get('memory', {}).get('minimum_gb', 0)}GB minimum, ")
            f.write(f"{req.get('memory', {}).get('recommended_gb', 0)}GB recommended\n")
            f.write(f"- **Storage**: {req.get('storage', {}).get('minimum_gb', 0)}GB minimum\n")
            f.write(f"- **Ports**: {', '.join(req.get('ports', []))}\n")
            f.write(f"- **Services**: {', '.join(req.get('services', []))}\n\n")
            
            f.write("## 🚀 Deployment Readiness\n\n")
            dr = self.results['deployment_readiness']
            f.write(f"- **Docker Ready**: {dr.get('docker_ready', False)}\n")
            f.write(f"- **Config Portable**: {dr.get('config_portable', False)}\n")
            f.write(f"- **Dependencies Documented**: {dr.get('dependencies_documented', False)}\n\n")
            
            if dr.get('blockers'):
                f.write("### Blockers\n\n")
                for blocker in dr['blockers']:
                    f.write(f"- {blocker}\n")
                f.write("\n")
            
            f.write("### Recommendations for Multi-Device Setup\n\n")
            for rec in dr.get('recommendations', []):
                f.write(f"- {rec}\n")
            f.write("\n")
            
            f.write("## 📦 Archive Candidates\n\n")
            for candidate in self.results['archive_candidates'][:20]:
                f.write(f"- `{candidate['path']}` → `{candidate['suggest_move']}`\n")
                f.write(f"  - Reason: {candidate['reason']}\n")
            
    def run_full_analysis(self):
        """Run complete ecosystem analysis."""
        print("=" * 60)
        print("FAITHH Ecosystem Analysis")
        print("=" * 60)
        print()
        
        self.find_duplicates()
        self.analyze_backend_files()
        self.analyze_frontend_files()
        self.analyze_config_files()
        self.analyze_state_files()
        self.identify_archive_candidates()
        self.check_consistency()
        self.analyze_system_requirements()
        self.assess_deployment_readiness()
        
        print()
        report_path = self.generate_report()
        
        print("\n" + "=" * 60)
        print("Analysis complete!")
        print("=" * 60)
        
        return report_path

if __name__ == "__main__":
    analyzer = EcosystemAnalyzer()
    analyzer.run_full_analysis()
