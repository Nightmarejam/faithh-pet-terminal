#!/usr/bin/env python3
"""
AI-Stack Comprehensive Analyzer
Phase 7: System Analysis and Cleanup Planning
Analyzes, categorizes, and provides recommendations for ai-stack cleanup
"""

import os
import json
import hashlib
import mimetypes
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
import re
import ast
import subprocess
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AIStackAnalyzer:
    """Comprehensive analyzer for ai-stack directory"""
    
    def __init__(self, root_path: str = "/home/jonat/ai-stack"):
        self.root_path = Path(root_path)
        self.analysis_results = {
            "scan_summary": {},
            "file_analysis": {},
            "category_analysis": {},
            "importance_analysis": {},
            "cleanup_recommendations": {},
            "organization_plan": {}
        }
        
        # File categories
        self.categories = {
            "core_system": {
                "description": "Essential system files",
                "importance": "critical",
                "action": "keep_organized",
                "patterns": [
                    r"faithh_professional_backend.*\.py$",
                    r"faithh_pet.*\.html$",
                    r"config\.yaml$",
                    r"requirements\.txt$",
                    r"README\.md$"
                ]
            },
            "phase7_implementations": {
                "description": "Phase 7 specific implementations",
                "importance": "high",
                "action": "keep_documented",
                "patterns": [
                    r"app/services/.*\.py$",
                    r"phase7_.*\.md$",
                    r"sonnet_.*\.md$",
                    r"day.*\.md$"
                ]
            },
            "legacy_systems": {
                "description": "Old or deprecated systems",
                "importance": "low",
                "action": "archive_or_delete",
                "patterns": [
                    r".*old.*\.py$",
                    r".*deprecated.*\.py$",
                    r".*backup.*\.py$",
                    r".*test.*\.py$",
                    r".*temp.*\.py$"
                ]
            },
            "experimental": {
                "description": "Experimental or test implementations",
                "importance": "medium",
                "action": "evaluate_keep",
                "patterns": [
                    r"experiments/.*\.py$",
                    r"test_.*\.py$",
                    r".*experiment.*\.py$",
                    r".*prototype.*\.py$"
                ]
            },
            "documentation": {
                "description": "Documentation and guides",
                "importance": "medium",
                "action": "keep_organized",
                "patterns": [
                    r"docs/.*\.md$",
                    r".*guide.*\.md$",
                    r".*manual.*\.md$",
                    r".*documentation.*\.md$"
                ]
            },
            "scripts": {
                "description": "Utility and automation scripts",
                "importance": "medium",
                "action": "keep_organized",
                "patterns": [
                    r"scripts/.*\.py$",
                    r".*\.sh$",
                    r".*script.*\.py$"
                ]
            },
            "data": {
                "description": "Data files and storage",
                "importance": "medium",
                "action": "keep_organized",
                "patterns": [
                    r"data/.*",
                    r".*\.json$",
                    r".*\.csv$",
                    r".*\.db$"
                ]
            },
            "tests": {
                "description": "Test files and testing frameworks",
                "importance": "medium",
                "action": "keep_organized",
                "patterns": [
                    r"tests/.*",
                    r"test_.*\.py$",
                    r".*_test\.py$"
                ]
            },
            "ml": {
                "description": "Machine learning and AI models",
                "importance": "medium",
                "action": "evaluate_keep",
                "patterns": [
                    r"ml/.*",
                    r".*model.*\.py$",
                    r".*ml_.*\.py$"
                ]
            },
            "maintenance": {
                "description": "Maintenance and monitoring scripts",
                "importance": "low",
                "action": "evaluate_keep",
                "patterns": [
                    r".*maintenance.*\.py$",
                    r".*monitor.*\.py$",
                    r".*health.*\.py$"
                ]
            }
        }
        
        # Importance scoring factors
        self.importance_factors = {
            "recent_access": 0.3,  # Recently accessed files
            "file_size": 0.1,      # File size (normalized)
            "dependencies": 0.2,  # Number of dependencies
            "references": 0.2,     # Number of references in other files
            "complexity": 0.1,      # Code complexity
            "documentation": 0.1    # Has documentation
        }
    
    def analyze_stack(self) -> Dict[str, Any]:
        """Perform comprehensive analysis of ai-stack"""
        logger.info("Starting comprehensive AI-Stack analysis")
        logger.info(f"Root path: {self.root_path}")
        
        # Step 1: Scan all files
        self.scan_all_files()
        
        # Step 2: Analyze each file
        self.analyze_files()
        
        # Step 3: Categorize files
        self.categorize_files()
        
        # Step 4: Assess importance
        self.assess_importance()
        
        # Step 5: Generate cleanup recommendations
        self.generate_cleanup_recommendations()
        
        # Step 6: Create organization plan
        self.create_organization_plan()
        
        return self.analysis_results
    
    def scan_all_files(self):
        """Scan all files in ai-stack directory"""
        logger.info("Scanning all files...")
        
        files = []
        total_size = 0
        file_types = defaultdict(int)
        
        for file_path in self.root_path.rglob("*"):
            if file_path.is_file():
                try:
                    stat = file_path.stat()
                    relative_path = file_path.relative_to(self.root_path)
                    file_size = stat.st_size
                    
                    file_info = {
                        "path": str(relative_path),
                        "absolute_path": str(file_path),
                        "size": file_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime),
                        "created": datetime.fromtimestamp(stat.st_ctime),
                        "extension": file_path.suffix.lower(),
                        "name": file_path.name,
                        "parent": str(file_path.parent.relative_to(self.root_path))
                    }
                    
                    # Detect file type
                    mime_type, _ = mimetypes.guess_type(str(file_path))
                    file_info["mime_type"] = mime_type
                    
                    # Calculate file hash
                    file_info["hash"] = self.calculate_file_hash(file_path)
                    
                    files.append(file_info)
                    total_size += file_size
                    file_types[file_info["extension"]] += 1
                    
                except Exception as e:
                    logger.warning(f"Error scanning file {file_path}: {e}")
        
        self.analysis_results["scan_summary"] = {
            "total_files": len(files),
            "total_size": total_size,
            "file_types": dict(file_types),
            "scan_time": datetime.now().isoformat()
        }
        
        self.analysis_results["file_analysis"] = {
            "files": files
        }
        
        logger.info(f"Scanned {len(files)} files, total size: {self.format_size(total_size)}")
    
    def analyze_files(self):
        """Analyze individual files"""
        logger.info("Analyzing individual files...")
        
        files = self.analysis_results["file_analysis"]["files"]
        
        for file_info in files:
            try:
                file_path = Path(file_info["absolute_path"])
                
                # Analyze based on file type
                if file_path.suffix.lower() == ".py":
                    file_info.update(self.analyze_python_file(file_path))
                elif file_path.suffix.lower() in [".md", ".txt"]:
                    file_info.update(self.analyze_text_file(file_path))
                elif file_path.suffix.lower() == ".json":
                    file_info.update(self.analyze_json_file(file_path))
                elif file_path.suffix.lower() == ".yaml" or file_path.suffix.lower() == ".yml":
                    file_info.update(self.analyze_yaml_file(file_path))
                else:
                    file_info.update(self.analyze_generic_file(file_path))
                
                # Calculate complexity score
                file_info["complexity_score"] = self.calculate_complexity_score(file_info)
                
            except Exception as e:
                logger.warning(f"Error analyzing file {file_info['path']}: {e}")
                file_info["analysis_error"] = str(e)
    
    def analyze_python_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze Python file"""
        analysis = {
            "type": "python",
            "imports": [],
            "functions": [],
            "classes": [],
            "lines_of_code": 0,
            "docstrings": 0,
            "dependencies": 0
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Parse AST
            tree = ast.parse(content)
            
            # Count imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        analysis["imports"].append(alias.name)
                        analysis["dependencies"] += 1
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        analysis["imports"].append(node.module)
                        analysis["dependencies"] += 1
                elif isinstance(node, ast.FunctionDef):
                    analysis["functions"].append(node.name)
                elif isinstance(node, ast.ClassDef):
                    analysis["classes"].append(node.name)
            
            # Count lines and docstrings
            lines = content.split('\n')
            analysis["lines_of_code"] = len([line for line in lines if line.strip()])
            analysis["docstrings"] = content.count('"""') // 2 + content.count("'''") // 2
            
        except Exception as e:
            analysis["parse_error"] = str(e)
        
        return analysis
    
    def analyze_text_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze text file"""
        analysis = {
            "type": "text",
            "lines": 0,
            "words": 0,
            "characters": 0,
            "headings": 0,
            "links": 0
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            analysis["lines"] = len(lines)
            analysis["words"] = len(content.split())
            analysis["characters"] = len(content)
            
            # Count markdown headings
            analysis["headings"] = len(re.findall(r'^#+\s+', content))
            
            # Count links
            analysis["links"] = len(re.findall(r'\[.*?\]\(.*?\)', content))
            
        except Exception as e:
            analysis["parse_error"] = str(e)
        
        return analysis
    
    def analyze_json_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze JSON file"""
        analysis = {
            "type": "json",
            "keys": 0,
            "values": 0,
            "depth": 0,
            "size_formatted": self.format_size(file_path.stat().st_size)
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            def count_items(obj, depth=0):
                if isinstance(obj, dict):
                    return sum(count_items(v, depth + 1) for v in obj.values()) + len(obj), depth + 1
                elif isinstance(obj, list):
                    return sum(count_items(item, depth + 1) for item in obj), depth
                else:
                    return 1, depth
            
            total_items, max_depth = count_items(data)
            analysis["keys"] = total_items
            analysis["depth"] = max_depth
            
        except Exception as e:
            analysis["parse_error"] = str(e)
        
        return analysis
    
    def analyze_yaml_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze YAML file"""
        analysis = {
            "type": "yaml",
            "keys": 0,
            "sections": 0,
            "size_formatted": self.format_size(file_path.stat().st_size)
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Count sections (top-level keys)
            lines = content.split('\n')
            analysis["keys"] = len([line for line in lines if line.strip().endswith(':')])
            analysis["sections"] = len(re.findall(r'^[a-zA-Z_][a-zA-Z0-9_]*:', content))
            
        except Exception as e:
            analysis["parse_error"] = str(e)
        
        return analysis
    
    def analyze_generic_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze generic file"""
        return {
            "type": "generic",
            "size_formatted": self.format_size(file_path.stat().st_size)
        }
    
    def calculate_complexity_score(self, file_info: Dict[str, Any]) -> float:
        """Calculate complexity score for file"""
        score = 0.0
        
        # Base score from file type
        if file_info.get("type") == "python":
            score += file_info.get("lines_of_code", 0) * 0.01
            score += file_info.get("functions", 0) * 0.1
            score += file_info.get("classes", 0) * 0.2
            score += file_info.get("dependencies", 0) * 0.1
        elif file_info.get("type") == "json":
            score += file_info.get("keys", 0) * 0.01
            score += file_info.get("depth", 0) * 0.1
        elif file_info.get("type") == "text":
            score += file_info.get("lines", 0) * 0.001
            score += file_info.get("headings", 0) * 0.1
            score += file_info.get("links", 0) * 0.05
        
        # Normalize score
        return min(score, 10.0)
    
    def categorize_files(self):
        """Categorize files based on patterns and content"""
        logger.info("Categorizing files...")
        
        files = self.analysis_results["file_analysis"]["files"]
        category_counts = defaultdict(int)
        
        for file_info in files:
            category = self.determine_category(file_info)
            file_info["category"] = category
            category_counts[category] += 1
        
        self.analysis_results["category_analysis"] = {
            "category_counts": dict(category_counts),
            "uncategorized": [f["path"] for f in files if f.get("category") == "uncategorized"]
        }
        
        logger.info(f"Categorized files: {dict(category_counts)}")
    
    def determine_category(self, file_info: Dict[str, Any]) -> str:
        """Determine category for file based on patterns and content"""
        file_path = file_info["path"]
        
        # Check patterns for each category
        for category, config in self.categories.items():
            for pattern in config["patterns"]:
                if re.search(pattern, file_path, re.IGNORECASE):
                    return category
        
        # Content-based categorization
        if file_info.get("type") == "python":
            if "test" in file_path.lower() or "test_" in file_path.lower():
                return "tests"
            elif "experiment" in file_path.lower():
                return "experimental"
            elif "maintenance" in file_path.lower() or "monitor" in file_path.lower():
                return "maintenance"
            elif file_info.get("dependencies", 0) > 10:
                return "core_system"
            elif file_info.get("lines_of_code", 0) > 500:
                return "core_system"
            else:
                return "experimental"
        
        return "uncategorized"
    
    def assess_importance(self):
        """Assess importance of files"""
        logger.info("Assessing file importance...")
        
        files = self.analysis_results["file_analysis"]["files"]
        
        for file_info in files:
            importance_score = self.calculate_importance_score(file_info)
            file_info["importance_score"] = importance_score
            file_info["importance_level"] = self.get_importance_level(importance_score)
        
        # Sort files by importance
        files.sort(key=lambda x: x["importance_score"], reverse=True)
        
        self.analysis_results["importance_analysis"] = {
            "top_files": files[:20],  # Top 20 most important files
            "importance_distribution": self.calculate_importance_distribution(files)
        }
        
        logger.info("File importance assessment completed")
    
    def calculate_importance_score(self, file_info: Dict[str, Any]) -> float:
        """Calculate importance score for file"""
        score = 0.0
        
        # Base score from category
        category = file_info.get("category", "uncategorized")
        if category in self.categories:
            category_importance = self.categories[category]["importance"]
            if category_importance == "critical":
                score += 5.0
            elif category_importance == "high":
                score += 3.0
            elif category_importance == "medium":
                score += 1.0
            else:
                score += 0.0
        
        # File size factor (normalized)
        file_size = file_info.get("size", 0)
        if file_size > 0:
            size_factor = min(file_size / 1000000, 1.0)  # Normalize to 1MB
            score += size_factor * self.importance_factors["file_size"]
        
        # Complexity factor
        complexity = file_info.get("complexity_score", 0)
        score += complexity * self.importance_factors["complexity"]
        
        # Dependencies factor
        dependencies = file_info.get("dependencies", 0)
        score += min(dependencies / 10, 1.0) * self.importance_factors["dependencies"]
        
        # Documentation factor
        if file_info.get("docstrings", 0) > 0:
            score += self.importance_factors["documentation"]
        
        return score
    
    def get_importance_level(self, score: float) -> str:
        """Get importance level from score"""
        if score >= 4.0:
            return "critical"
        elif score >= 2.5:
            return "high"
        elif score >= 1.0:
            return "medium"
        else:
            return "low"
    
    def calculate_importance_distribution(self, files: List[Dict[str, Any]]) -> Dict[str, int]:
        """Calculate distribution of importance levels"""
        distribution = defaultdict(int)
        for file_info in files:
            distribution[file_info.get("importance_level", "low")] += 1
        return dict(distribution)
    
    def generate_cleanup_recommendations(self):
        """Generate cleanup recommendations"""
        logger.info("Generating cleanup recommendations...")
        
        files = self.analysis_results["file_analysis"]["files"]
        recommendations = []
        
        for file_info in files:
            category = file_info.get("category", "uncategorized")
            importance = file_info.get("importance_level", "low")
            
            if category in self.categories:
                action = self.categories[category]["action"]
                recommendation = {
                    "path": file_info["path"],
                    "category": category,
                    "importance": importance,
                    "action": action,
                    "reason": self.get_cleanup_reason(file_info, action)
                }
                recommendations.append(recommendation)
        
        # Group recommendations by action
        grouped_recommendations = defaultdict(list)
        for rec in recommendations:
            grouped_recommendations[rec["action"]].append(rec)
        
        self.analysis_results["cleanup_recommendations"] = {
            "total_files": len(files),
            "recommendations": recommendations,
            "grouped_recommendations": dict(grouped_recommendations),
            "summary": self.generate_cleanup_summary(grouped_recommendations)
        }
        
        logger.info(f"Generated {len(recommendations)} cleanup recommendations")
    
    def get_cleanup_reason(self, file_info: Dict[str, Any], action: str) -> str:
        """Get reason for cleanup action"""
        category = file_info.get("category", "uncategorized")
        importance = file_info.get("importance_level", "low")
        
        if action == "keep_organized":
            return f"Essential {category} file with {importance} importance"
        elif action == "keep_documented":
            return f"Important {category} file with {importance} importance"
        elif action == "archive_or_delete":
            return f"Legacy {category} file with {importance} importance"
        elif action == "evaluate_keep":
            return f"Experimental {category} file with {importance} importance"
        else:
            return f"Uncategorized file with {importance} importance"
    
    def generate_cleanup_summary(self, grouped_recommendations: Dict[str, List]) -> Dict[str, Any]:
        """Generate summary of cleanup recommendations"""
        summary = {}
        
        for action, recs in grouped_recommendations.items():
            summary[action] = {
                "count": len(recs),
                "total_size": sum(r.get("size", 0) for r in recs),
                "categories": list(set(r.get("category") for r in recs)),
                "importance_levels": list(set(r.get("importance") for r in recs))
            }
        
        return summary
    
    def create_organization_plan(self):
        """Create organization plan"""
        logger.info("Creating organization plan...")
        
        recommendations = self.analysis_results["cleanup_recommendations"]
        
        plan = {
            "target_structure": {
                "core_system": {
                    "description": "Essential system files",
                    "location": "root/",
                    "keep_files": []
                },
                "app": {
                    "description": "Application modules",
                    "location": "app/",
                    "keep_files": []
                },
                "docs": {
                    "description": "Documentation",
                    "location": "docs/",
                    "keep_files": []
                },
                "scripts": {
                    "description": "Utility scripts",
                    "location": "scripts/",
                    "keep_files": []
                },
                "tests": {
                    "description": "Test files",
                    "location": "tests/",
                    "keep_files": []
                },
                "data": {
                    "description": "Data files",
                    "location": "data/",
                    "keep_files": []
                },
                "archive": {
                    "description": "Archived files",
                    "location": "archive/",
                    "keep_files": []
                },
                "delete": {
                    "description": "Files to delete",
                    "location": null,
                    "keep_files": []
                }
            },
            "actions": [],
            "estimated_impact": {
                "files_moved": 0,
                "files_archived": 0,
                "files_deleted": 0,
                "space_saved": 0
            }
        }
        
        # Populate plan
        for rec in recommendations["recommendations"]:
            action = rec["action"]
            file_path = rec["path"]
            
            if action == "keep_organized":
                # Determine appropriate location
                if rec["category"] == "core_system":
                    plan["target_structure"]["core_system"]["keep_files"].append(file_path)
                elif rec["category"] == "phase7_implementations":
                    if "app/services/" in file_path:
                        plan["target_structure"]["app"]["keep_files"].append(file_path)
                    else:
                        plan["target_structure"]["core_system"]["keep_files"].append(file_path)
                elif rec["category"] == "documentation":
                    plan["target_structure"]["docs"]["keep_files"].append(file_path)
                elif rec["category"] == "scripts":
                    plan["target_structure"]["scripts"]["keep_files"].append(file_path)
                elif rec["category"] == "tests":
                    plan["target_structure"]["tests"]["keep_files"].append(file_path)
                elif rec["category"] == "data":
                    plan["target_structure"]["data"]["keep_files"].append(file_path)
                else:
                    plan["target_structure"]["core_system"]["keep_files"].append(file_path)
                
            elif action == "keep_documented":
                plan["target_structure"]["core_system"]["keep_files"].append(file_path)
                
            elif action == "archive_or_delete":
                if rec["importance"] == "critical" or rec["importance"] == "high":
                    plan["target_structure"]["archive"]["keep_files"].append(file_path)
                else:
                    plan["target_structure"]["delete"]["keep_files"].append(file_path)
                
            elif action == "evaluate_keep":
                # Manual evaluation needed
                plan["actions"].append({
                    "type": "manual_evaluation",
                    "file": file_path,
                    "reason": f"Experimental {rec['category']} file with {rec['importance']} importance"
                })
        
        # Calculate impact
        plan["estimated_impact"]["files_moved"] = len(plan["target_structure"]["core_system"]["keep_files"]) + \
                                              len(plan["target_structure"]["app"]["keep_files"]) + \
                                              len(plan["target_structure"]["docs"]["keep_files"]) + \
                                              len(plan["target_structure"]["scripts"]["keep_files"]) + \
                                              len(plan["target_structure"]["tests"]["keep_files"]) + \
                                              len(plan["target_structure"]["data"]["keep_files"])
        plan["estimated_impact"]["files_archived"] = len(plan["target_structure"]["archive"]["keep_files"])
        plan["estimated_impact"]["files_deleted"] = len(plan["target_structure"]["delete"]["keep_files"])
        
        self.analysis_results["organization_plan"] = plan
        
        logger.info("Organization plan created")
    
    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate file hash for comparison"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:
            return "unknown"
    
    def format_size(self, size_bytes: int) -> str:
        """Format file size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f}{unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f}TB"
    
    def generate_report(self) -> str:
        """Generate comprehensive analysis report"""
        report = []
        report.append("# AI-Stack Comprehensive Analysis Report")
        report.append(f"Generated: {datetime.now().isoformat()}")
        report.append("")
        
        # Scan Summary
        scan_summary = self.analysis_results["scan_summary"]
        report.append("## Scan Summary")
        report.append(f"- Total Files: {scan_summary['total_files']}")
        report.append(f"- Total Size: {self.format_size(scan_summary['total_size'])}")
        report.append(f"- File Types: {len(scan_summary['file_types'])}")
        report.append("")
        
        # Category Analysis
        category_analysis = self.analysis_results["category_analysis"]
        report.append("## Category Analysis")
        for category, count in category_analysis["category_counts"].items():
            config = self.categories.get(category, {})
            report.append(f"- {category}: {count} files ({config.get('description', 'No description')})")
        report.append("")
        
        # Importance Analysis
        importance_analysis = self.analysis_results["importance_analysis"]
        report.append("## Top 20 Most Important Files")
        for i, file_info in enumerate(importance_analysis["top_files"][:20], 1):
            report.append(f"{i}. {file_info['path']} ({file_info.get('importance_level', 'low')} importance)")
        report.append("")
        
        # Cleanup Recommendations
        cleanup_rec = self.analysis_results["cleanup_recommendations"]
        report.append("## Cleanup Recommendations Summary")
        summary = cleanup_rec["summary"]
        for action, info in summary.items():
            report.append(f"- {action}: {info['count']} files, {self.format_size(info['total_size'])}")
        report.append("")
        
        # Organization Plan
        plan = self.analysis_results["organization_plan"]
        report.append("## Organization Plan")
        for location, info in plan["target_structure"].items():
            if info["keep_files"]:
                report.append(f"- {location}: {len(info['keep_files'])} files")
        report.append("")
        
        # Manual Evaluations Needed
        if plan["actions"]:
            report.append("## Manual Evaluations Needed")
            for action in plan["actions"]:
                report.append(f"- {action['file']}: {action['reason']}")
            report.append("")
        
        return "\n".join(report)
    
    def save_analysis(self, output_path: str = "/home/jonat/ai-stack/ai_stack_analysis_report.md"):
        """Save analysis results to file"""
        report = self.generate_report()
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report)
            logger.info(f"Analysis report saved to {output_path}")
        except Exception as e:
            logger.error(f"Error saving report: {e}")
    
    def save_json_results(self, output_path: str = "/home/jonat/ai-stack/ai_stack_analysis_results.json"):
        """Save analysis results to JSON file"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.analysis_results, f, indent=2, default=str)
            logger.info(f"Analysis results saved to {output_path}")
        except Exception as e:
            logger.error(f"Error saving JSON results: {e}")

def main():
    """Main function to run AI-Stack analyzer"""
    analyzer = AIStackAnalyzer()
    
    logger.info("Starting AI-Stack Comprehensive Analysis")
    logger.info("=" * 60)
    
    # Run analysis
    results = analyzer.analyze_stack()
    
    # Save results
    analyzer.save_analysis()
    analyzer.save_json_results()
    
    # Print summary
    scan_summary = results["scan_summary"]
    cleanup_summary = results["cleanup_recommendations"]["summary"]
    
    logger.info("=" * 60)
    logger.info("AI-Stack Analysis Complete")
    logger.info(f"Files Analyzed: {scan_summary['total_files']}")
    logger.info(f"Total Size: {analyzer.format_size(scan_summary['total_size'])}")
    logger.info(f"Cleanup Actions: {sum(c['count'] for c in cleanup_summary.values())}")
    logger.info("=" * 60)
    
    # Print top recommendations
    logger.info("Top Cleanup Recommendations:")
    for action, info in cleanup_summary.items():
        logger.info(f"  {action}: {info['count']} files ({analyzer.format_size(info['total_size'])})")
    
    logger.info("=" * 60)
    logger.info("Reports saved:")
    logger.info("  - ai_stack_analysis_report.md")
    logger.info("  - ai_stack_analysis_results.json")

if __name__ == "__main__":
    main()