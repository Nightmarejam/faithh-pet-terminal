#!/usr/bin/env python3
"""
Project Cleanup and Architecture Review for Sonnet
Compiles current project state, identifies issues, and requests comprehensive cleanup guidance
"""

import json
import time
from datetime import datetime
import os
from pathlib import Path

def compile_project_cleanup_review():
    """Compile comprehensive project state for Sonnet's cleanup review"""
    
    # Count backend files
    backend_files = []
    project_root = Path("/home/jonat/ai-stack")
    for file_path in project_root.glob("*backend*.py"):
        if file_path.is_file() and not any(skip in str(file_path) for skip in ["venv", "archive", "ml", "tests"]):
            backend_files.append({
                "name": file_path.name,
                "size": file_path.stat().st_size,
                "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
            })
    
    # Check current backend status
    try:
        with open("/home/jonat/ai-stack/backend.log", "r") as f:
            backend_log_lines = f.readlines()[-10:]  # Last 10 lines
    except:
        backend_log_lines = ["Backend log not accessible"]
    
    # Check genomic endpoints
    genomic_backend = None
    canonical_backend = None
    
    try:
        # Check which backend has genomic endpoints
        with open("/home/jonat/ai-stack/faithh_backend_optimized.py", "r") as f:
            content = f.read()
            if "genomic" in content.lower():
                genomic_backend = "faithh_backend_optimized.py"
    except:
        pass
    
    try:
        # Check canonical backend
        with open("/home/jonat/ai-stack/faithh_professional_backend_fixed.py", "r") as f:
            content = f.read()
            if "genomic" not in content.lower():
                canonical_backend = "faithh_professional_backend_fixed.py (no genomic)"
    except:
        pass
    
    review = {
        "review_type": "Project Cleanup and Architecture Review",
        "timestamp": datetime.now().isoformat(),
        "prepared_for": "Sonnet Scientific Review Board",
        "urgency": "HIGH - Architecture Confusion Blocking Progress",
        
        "critical_issues": {
            "backend_proliferation": {
                "problem": "51 backend files causing confusion and redundancy",
                "impact": "Development paralysis, unclear which backend to use",
                "backend_files": backend_files,
                "canonical_backend": "faithh_professional_backend_fixed.py (per SYSTEM_FINGERPRINT.md)",
                "genomic_backend": genomic_backend,
                "current_running": "faithh_professional_backend_fixed.py (no genomic endpoints)"
            },
            "documentation_drift": {
                "problem": "Top-level documents not updated with recent changes",
                "impact": "New sessions can't understand current state",
                "critical_docs": [
                    "SYSTEM_FINGERPRINT.md",
                    "AGENTS.md", 
                    "CONTEXT.md",
                    "README.md"
                ]
            },
            "experiment_isolation": {
                "problem": "Genomic experiments completed but backend endpoints missing",
                "impact": "190 organisms tested but can't continue experiments",
                "experiments_completed": [
                    "Phase 1: Large-Scale Genomic Testing (100 organisms)",
                    "Phase 2: Environmental Adaptation (50 organisms)", 
                    "Phase 3: Multi-Generational Evolution (40 organisms, 5 generations)"
                ]
            }
        },
        
        "project_structure_analysis": {
            "root_level_clutter": {
                "problem": "Too many files at project root",
                "files_at_root": len([f for f in project_root.iterdir() if f.is_file()]),
                "recommended_max": 20,
                "actual_count": len([f for f in project_root.iterdir() if f.is_file()])
            },
            "archive_organization": {
                "problem": "Inconsistent archiving of old files",
                "archive_locations": ["archive/", "archive/legacy/", "docs/archive/"],
                "needs_consolidation": True
            },
            "experiment_organization": {
                "problem": "Experiments scattered, no dedicated structure",
                "current_locations": ["experiments/", "scripts/", "root level"],
                "recommended": "experiments/ with proper substructure"
            }
        },
        
        "immediate_needs": {
            "backend_consolidation": {
                "priority": 1,
                "action": "Consolidate genomic endpoints into canonical backend",
                "target": "faithh_professional_backend_fixed.py",
                "backup": "Archive all other backend variants"
            },
            "documentation_update": {
                "priority": 2, 
                "action": "Update all top-level documentation",
                "documents": [
                    "SYSTEM_FINGERPRINT.md - Update backend architecture",
                    "AGENTS.md - Add cleanup protocols",
                    "CONTEXT.md - Regenerate with current state",
                    "README.md - Update project overview"
                ]
            },
            "file_organization": {
                "priority": 3,
                "action": "Implement consistent file organization",
                "structure": {
                    "root_level": "Only essential files",
                    "experiments/": "All experimental code",
                    "archive/": "Consolidated archive",
                    "docs/": "Living documentation"
                }
            }
        },
        
        "proposed_cleanup_protocol": {
            "name": "FAITHH Project Maintenance Protocol",
            "frequency": "Monthly major cleanup, weekly minor maintenance",
            "components": [
                {
                    "component": "Backend Architecture Review",
                    "frequency": "Monthly",
                    "checks": [
                        "Verify single canonical backend",
                        "Archive experimental variants",
                        "Update SYSTEM_FINGERPRINT.md"
                    ]
                },
                {
                    "component": "Documentation Synchronization", 
                    "frequency": "Weekly",
                    "checks": [
                        "Regenerate CONTEXT.md",
                        "Update project_states.json",
                        "Review decisions_log.json"
                    ]
                },
                {
                    "component": "File Organization Audit",
                    "frequency": "Monthly", 
                    "checks": [
                        "Archive legacy files",
                        "Organize experiments/",
                        "Clean root directory"
                    ]
                }
            ]
        },
        
        "sonnet_guidance_requested": {
            "backend_strategy": {
                "question": "Should we consolidate all features into single canonical backend or maintain feature-specific backends?",
                "context": "SYSTEM_FINGERPRINT.md specifies faithh_professional_backend_fixed.py as canonical, but genomic endpoints are in faithh_backend_optimized.py"
            },
            "cleanup_priorities": {
                "question": "What should be the priority order for cleanup tasks?",
                "options": [
                    "Backend consolidation first",
                    "Documentation update first", 
                    "File organization first",
                    "Parallel approach"
                ]
            },
            "maintenance_protocol": {
                "question": "Is the proposed maintenance protocol appropriate or should it be modified?",
                "suggestions": "Request improvements to frequency, scope, or automation"
            },
            "project_structure": {
                "question": "What is the ideal long-term project structure for FAITHH?",
                "considerations": [
                    "Scalability for new features",
                    "Clarity for new AI sessions",
                    "Maintenance burden",
                    "Documentation accessibility"
                ]
            }
        },
        
        "success_metrics": {
            "cleanup_complete": {
                "backend_files": "Reduce from 51 to 1 canonical + archived variants",
                "root_files": "Reduce to < 20 essential files",
                "documentation": "All top-level docs updated and synchronized",
                "experiments": "All experiments working with canonical backend"
            },
            "protocol_working": {
                "monthly_cleanup": "Automated cleanup script running",
                "documentation_sync": "CONTEXT.md auto-updated weekly",
                "backend_health": "Single backend verified monthly"
            }
        },
        
        "next_steps_after_sonnet_review": [
            "Execute backend consolidation based on Sonnet's guidance",
            "Implement cleanup protocol with automation scripts",
            "Update all top-level documentation",
            "Test consolidated system with genomic experiments",
            "Archive legacy files according to new protocol"
        ]
    }
    
    return review

def save_cleanup_review(review, filename=None):
    """Save cleanup review to file"""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"project_cleanup_review_for_sonnet_{timestamp}.json"
    
    try:
        with open(filename, 'w') as f:
            json.dump(review, f, indent=2)
        print(f"✅ Project cleanup review saved to: {filename}")
        return filename
    except Exception as e:
        print(f"❌ Failed to save review: {e}")
        return None

def main():
    """Main review compilation"""
    print("🧹 Compiling Project Cleanup Review for Sonnet")
    print("="*70)
    
    # Compile comprehensive review
    review = compile_project_cleanup_review()
    
    # Save review
    filename = save_cleanup_review(review)
    
    # Print key highlights
    print("\n🚨 Critical Issues Identified:")
    print("-" * 40)
    
    critical = review["critical_issues"]
    print(f"🔧 Backend Proliferation: {critical['backend_proliferation']['problem']}")
    print(f"   Files: {len(critical['backend_proliferation']['backend_files'])} backend files")
    print(f"   Canonical: {critical['backend_proliferation']['canonical_backend']}")
    print(f"   Genomic: {critical['backend_proliferation']['genomic_backend']}")
    
    print(f"\n📚 Documentation Drift: {critical['documentation_drift']['problem']}")
    for doc in critical['documentation_drift']['critical_docs']:
        print(f"   • {doc}")
    
    print(f"\n🧪 Experiment Isolation: {critical['experiment_isolation']['problem']}")
    for exp in critical['experiment_isolation']['experiments_completed']:
        print(f"   • {exp}")
    
    print(f"\n🎯 Immediate Needs (Priority Order):")
    needs = review["immediate_needs"]
    priorities = sorted(needs.items(), key=lambda x: x[1]['priority'])
    for priority, (name, details) in enumerate(priorities, 1):
        print(f"   {priority}. {details['action']}")
    
    print(f"\n🤝 Sonnet Guidance Requested:")
    guidance = review["sonnet_guidance_requested"]
    for question, details in guidance.items():
        print(f"   • {details['question']}")
    
    print(f"\n📋 Proposed Maintenance Protocol:")
    protocol = review["proposed_cleanup_protocol"]
    print(f"   Name: {protocol['name']}")
    print(f"   Frequency: {protocol['frequency']}")
    for component in protocol['components']:
        print(f"   • {component['component']} ({component['frequency']})")
    
    print("\n" + "="*70)
    print("🚀 PROJECT CLEANUP REVIEW READY FOR SONNET")
    print(f"📄 Complete review saved to: {filename}")
    print("🔍 Awaiting Sonnet's guidance for cleanup execution")

if __name__ == "__main__":
    main()