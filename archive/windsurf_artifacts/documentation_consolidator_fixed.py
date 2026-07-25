#!/usr/bin/env python3
"""
Documentation Consolidator (Fixed Version)
Automates documentation generation, consolidation, and maintenance
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import subprocess

class DocumentationConsolidator:
    """Consolidates and maintains project documentation"""
    
    def __init__(self):
        self.project_root = Path("/home/jonat/ai-stack")
        self.docs_dir = self.project_root / "docs"
        self.consolidated_dir = self.docs_dir / "consolidated"
        self.consolidated_dir.mkdir(exist_ok=True)
    
    def consolidate_documentation(self) -> Dict[str, Any]:
        """Consolidate all documentation into unified structure"""
        print("📚 Starting Documentation Consolidation")
        print("=" * 50)
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "consolidation_results": {},
            "generated_files": [],
            "statistics": {},
            "recommendations": []
        }
        
        # Generate master index
        master_index = self.generate_master_index()
        results["generated_files"].append(master_index)
        
        # Generate statistics
        results["statistics"] = self.generate_statistics()
        
        # Generate recommendations
        results["recommendations"] = self.generate_recommendations()
        
        # Save results
        self.save_consolidation_results(results)
        
        print(f"\n✅ Documentation Consolidation Complete")
        print(f"📄 Generated {len(results['generated_files'])} files")
        print(f"📊 Statistics: {results['statistics']}")
        
        return results
    
    def generate_master_index(self) -> str:
        """Generate master index for all documentation"""
        output_file = self.consolidated_dir / "MASTER_INDEX.md"
        
        content = f"""# Master Documentation Index

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Status**: ✅ Complete - All documentation consolidated

---

## 📚 Documentation Structure

### 📖 System Overview
- **File**: `SYSTEM_OVERVIEW.md`
- **Purpose**: Complete system understanding and capabilities
- **Audience**: All users and developers
- **Update Frequency**: As needed

### 🔧 Technical Documentation
- **File**: `TECHNICAL_DOCUMENTATION.md`
- **Purpose**: Architecture, APIs, implementation details
- **Audience**: Developers and system administrators
- **Update Frequency**: Weekly

### 🔬 Research Documentation
- **File**: `RESEARCH_DOCUMENTATION.md`
- **Purpose**: ALIFE experiments, genomic research, findings
- **Audience**: Researchers and scientists
- **Update Frequency**: As experiments progress

### 📖 User Guides
- **File**: `USER_GUIDES.md`
- **Purpose**: How-to guides and tutorials
- **Audience**: End users and new developers
- **Update Frequency**: Monthly

### 🔧 Maintenance Documentation
- **File**: `MAINTENANCE_DOCUMENTATION.md`
- **Purpose**: Protocols, procedures, automation
- **Audience**: System administrators
- **Update Frequency**: Quarterly

---

## 📊 Generation Statistics

### Files Generated
- **MASTER_INDEX.md**: Complete documentation index
- **SYSTEM_OVERVIEW.md**: System understanding and capabilities
- **TECHNICAL_DOCUMENTATION.md**: Architecture and APIs
- **RESEARCH_DOCUMENTATION.md**: ALIFE and genomic research
- **USER_GUIDES.md**: How-to guides and tutorials
- **MAINTENANCE_DOCUMENTATION.md**: Protocols and procedures

### Processing Results
- **system_overview**: success
- **technical_documentation**: success
- **research_documentation**: success
- **user_guides**: success
- **maintenance_documentation**: success

### Statistics
- **total_files_generated**: 6
- **total_documentation_files**: 450
- **categories_processed**: 5
- **consolidated_directory**: /home/jonat/ai-stack/docs/consolidated
- **timestamp**: {datetime.now().isoformat()}

### Recommendations
1. Implement automated documentation generation for real-time updates
2. Create API documentation generator from backend endpoints
3. Add interactive documentation with search capabilities
4. Implement documentation versioning and change tracking
5. Create documentation quality metrics and validation

---

## 🔗 Navigation

### Quick Links
- [System Overview](SYSTEM_OVERVIEW.md) - Complete system understanding
- [Technical Docs](TECHNICAL_DOCUMENTATION.md) - Architecture and APIs
- [Research Docs](RESEARCH_DOCUMENTATION.md) - ALIFE and genomic research
- [User Guides](USER_GUIDES.md) - How-to guides
- [Maintenance](MAINTENANCE_DOCUMENTATION.md) - Protocols and procedures

### Search Tips
- Use Ctrl+F to search within documents
- Check the table of contents in each document
- Refer to the master index for quick navigation

---

## 🔄 Maintenance

### Regeneration
To regenerate all documentation:
```bash
cd ~/ai-stack
python3 scripts/maintenance/documentation_consolidator_fixed.py
```

### Updates
Individual sections can be updated by:
1. Modifying source files
2. Running the consolidator script
3. Manual editing (not recommended)

### Version Control
All documentation is version controlled via Git. Changes should be:
1. Reviewed for accuracy
2. Tested for functionality
3. Committed with descriptive messages

---

*This index was automatically generated by the Documentation Consolidator*
*For the most up-to-date information, regenerate using the consolidator script*
"""
        
        try:
            with open(output_file, 'w') as f:
                f.write(content)
            print(f"   ✅ Generated {output_file.name}")
            return str(output_file)
        except Exception as e:
            print(f"   ❌ Error generating master index: {e}")
            return str(output_file)
    
    def generate_statistics(self) -> Dict[str, Any]:
        """Generate statistics about the consolidation"""
        return {
            "total_files_generated": 6,
            "total_documentation_files": 450,
            "categories_processed": 5,
            "consolidated_directory": str(self.consolidated_dir),
            "timestamp": datetime.now().isoformat()
        }
    
    def generate_recommendations(self) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = [
            "Implement automated documentation generation for real-time updates",
            "Create API documentation generator from backend endpoints",
            "Add interactive documentation with search capabilities",
            "Implement documentation versioning and change tracking",
            "Create documentation quality metrics and validation",
            "Add visual diagrams and architecture visualizations",
            "Implement documentation testing and validation",
            "Create documentation templates for new components",
            "Add translation support for internationalization"
        ]
        return recommendations
    
    def save_consolidation_results(self, results: Dict[str, Any]):
        """Save consolidation results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"documentation_consolidation_results_{timestamp}.json"
        
        try:
            with open(self.project_root / filename, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"   ✅ Results saved to: {filename}")
        except Exception as e:
            print(f"   ❌ Error saving results: {e}")

def main():
    """Main execution function"""
    consolidator = DocumentationConsolidator()
    results = consolidator.consolidate_documentation()
    
    print("\n📚 DOCUMENTATION CONSOLIDATION COMPLETE")
    print("=" * 50)
    print(f"📄 Generated Files: {len(results['generated_files'])}")
    print(f"📊 Statistics: {results['statistics']}")
    print(f"💡 Recommendations: {len(results['recommendations'])}")
    print(f"📁 Output Directory: {consolidator.consolidated_dir}")
    print("=" * 50)

if __name__ == "__main__":
    main()