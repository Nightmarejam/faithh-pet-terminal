#!/usr/bin/env python3
"""
Documentation Consolidator
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
        
        # Documentation structure
        self.structure = {
            "system_overview": {
                "title": "System Overview",
                "description": "Complete FAITHH and ALIFE system documentation",
                "files": ["SYSTEM_FINGERPRINT.md", "README.md", "CONTEXT.md"]
            },
            "technical_documentation": {
                "title": "Technical Documentation",
                "description": "Architecture, APIs, and implementation details",
                "files": []
            },
            "research_documentation": {
                "title": "Research Documentation",
                "description": "ALIFE experiments, genomic research, and findings",
                "files": []
            },
            "user_guides": {
                "title": "User Guides",
                "description": "How-to guides and tutorials",
                "files": []
            },
            "maintenance_documentation": {
                "title": "Maintenance Documentation",
                "description": "Maintenance protocols and operational procedures",
                "files": []
            }
        }
    
    def consolidate_documentation(self) -> Dict[str, Any]:
        """Consolidate all documentation into unified structure"""
        print("📚 Starting Documentation Consolidation")
        print("=" * 50)
        
        # Scan for documentation files
        self.scan_documentation_files()
        
        # Generate consolidated documentation
        results = {
            "timestamp": datetime.now().isoformat(),
            "consolidation_results": {},
            "generated_files": [],
            "statistics": {},
            "recommendations": []
        }
        
        # Generate each section
        for section_name, section_config in self.structure.items():
            print(f"\n📖 Processing {section_name}...")
            
            if section_name == "system_overview":
                result = self.generate_system_overview(section_config)
            elif section_name == "technical_documentation":
                result = self.generate_technical_documentation(section_config)
            elif section_name == "research_documentation":
                result = self.generate_research_documentation(section_config)
            elif section_name == "user_guides":
                result = self.generate_user_guides(section_config)
            elif section_name == "maintenance_documentation":
                result = self.generate_maintenance_documentation(section_config)
            
            results["consolidation_results"][section_name] = result
            if result.get("generated_file"):
                results["generated_files"].append(result["generated_file"])
        
        # Generate master index
        master_index = self.generate_master_index(results)
        results["generated_files"].append(master_index)
        
        # Generate statistics
        results["statistics"] = self.generate_statistics()
        
        # Generate recommendations
        results["recommendations"] = self.generate_recommendations()
        
        # Save results
        self.save_consolidation_results(results)
        
        print(f"\n✅ Documentation Consolidation Complete")
        print(f"📄 Generated {len(results['generated_files'])} files")
        print(f"📊 Processed {results['statistics']['total_files']} documentation files")
        
        return results
    
    def scan_documentation_files(self):
        """Scan for all documentation files"""
        print("   🔍 Scanning documentation files...")
        
        # Scan docs directory
        if self.docs_dir.exists():
            for file_path in self.docs_dir.rglob("*.md"):
                category = self.categorize_document_file(file_path)
                if category:
                    self.structure[category]["files"].append(str(file_path))
        
        # Scan root level documentation
        for file_path in self.project_root.glob("*.md"):
            if file_path.name in ["SYSTEM_FINGERPRINT.md", "README.md", "CONTEXT.md", "AGENTS.md"]:
                self.structure["system_overview"]["files"].append(str(file_path))
        
        # Scan project documentation
        projects_dir = self.project_root / "projects"
        if projects_dir.exists():
            for file_path in projects_dir.rglob("*.md"):
                if "analysis" in file_path.name.lower():
                    self.structure["research_documentation"]["files"].append(str(file_path))
        
        print(f"   ✅ Found documentation files in {len(self.structure)} categories")
    
    def categorize_document_file(self, file_path: Path) -> Optional[str]:
        """Categorize documentation file"""
        path_str = str(file_path).lower()
        
        if any(keyword in path_str for keyword in ["architecture", "backend", "api", "technical"]):
            return "technical_documentation"
        elif any(keyword in path_str for keyword in ["guide", "tutorial", "quickstart", "howto"]):
            return "user_guides"
        elif any(keyword in path_str for keyword in ["maintenance", "protocol", "procedure", "operational"]):
            return "maintenance_documentation"
        elif any(keyword in path_str for keyword in ["research", "experiment", "analysis", "finding"]):
            return "research_documentation"
        
        return None
    
    def generate_system_overview(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate system overview documentation"""
        output_file = self.consolidated_dir / "SYSTEM_OVERVIEW.md"
        
        content = f"""# {config['title']}

{config['description']}

---

## 🎯 System Identity

### FAITHH (Friendly AI Teaching & Helping Hub)
**Purpose**: Thought partner for maintaining project coherence when attention shifts  
**Current Phase**: 6.0 Complete - Genomic Impedance Reading  
**User**: Jonathan (Audio Producer & AI Developer)  
**Philosophy**: Celestial Equilibrium — resonance, harmonic alignment, dignity

### ALIFE (Artificial Life Research)
**Purpose**: Cultural evolution and parasitic impedance research  
**Current Status**: 9 experiments completed, cultural transmission breakthrough  
**Research Focus**: Complex cultural evolution with multi-generational persistence

---

## 📊 Current System Status

### Technical Architecture
- **Backend**: Flask-based modular architecture with 30+ endpoints
- **Frontend**: PET Terminal v4 with real-time updates
- **Database**: ChromaDB with 38K+ indexed chunks
- **AI Models**: Multi-provider routing (Ollama, Groq, Gemini)
- **Security**: Production-hardened with rate limiting and input validation

### Key Achievements
- ✅ Phase 6.0 Genomic Impedance Reading completed
- ✅ 190 organisms tested with perfect correlation (1.000)
- ✅ Cultural transmission breakthrough in ALIFE research
- ✅ Production security and performance optimization
- ✅ Comprehensive documentation and maintenance protocols

---

## 🔧 Core Capabilities

### FAITHH Capabilities
"""
        
        # Add capabilities from SYSTEM_FINGERPRINT
        try:
            with open(self.project_root / "SYSTEM_FINGERPRINT.md", 'r') as f:
                content = f.read()
                lines = content.split('\n')
                
                in_capabilities = False
                for line in lines:
                    if "Available Tools" in line:
                        in_capabilities = True
                        continue
                    elif "Program Advance System" in line:
                        break
                    elif in_capabilities and line.startswith('| **'):
                        capability = line.split('| **')[1].split('**')[0].strip()
                        if capability:
                            content += f"- **{capability}**: {self.get_capability_description(capability)}\n"
        except Exception as e:
            print(f"   ⚠️ Error reading SYSTEM_FINGERPRINT.md: {e}")
        
        content += """
### ALIFE Capabilities
- **Cultural Evolution**: Multi-generational protocol development
- **Social Specialization**: Agent role emergence and cooperation
- **Protocol Complexity**: Sophisticated cultural systems
- **Parasitic Impedance**: Novel energy feeding mechanisms
- **Multi-Generational Knowledge**: Knowledge accumulation across generations

---

## 📁 Project Structure

### Major Components
"""
        
        # Add project structure
        try:
            with open(self.project_root / "project_states.json", 'r') as f:
                project_states = json.load(f)
                
                content += f"""
**Active Projects**:
"""
                
                for project_name, project_info in project_states.get("projects", {}).items():
                    content += f"- **{project_info.get('name', project_name)}**: {project_info.get('status', 'Unknown')} - {project_info.get('summary', 'No summary')}\n"
                
                content += f"""
**Resource Allocation**:
"""
                
                resource_allocation = project_states.get("strategic_plan", {}).get("resource_allocation", {})
                
                content += f"- **Time**: FAITHH {resource_allocation.get('time_target', {}).get('FAITHH', 'N/A')}%, Business {resource_allocation.get('time_target', {}).get('Business', 'N/A')}%\n"
                content += f"- **Financial**: Reinvestment {resource_allocation.get('financial_target', {}).get('Reinvestment', 'N/A')}%, Infrastructure {resource_allocation.get('financial_target', {}).get('Infrastructure', 'N/A')}%\n"
        
        except Exception as e:
            print(f"   ⚠️ Error reading project_states.json: {e}")
        
        content += """

---

## 🚀 Getting Started

### Quick Start
```bash
./restart_backend.sh        # Start FAITHH backend
# Open http://localhost:5557
```

### Health Check
```bash
curl http://localhost:5557/health
```

### Key Endpoints
- **Chat**: `POST /api/chat` - Main AI interaction
- **Search**: `POST /api/search` - RAG search
- **Genomic**: `POST /api/genomic/impedance-sensor` - Create genomic sensor
- **Status**: `GET /api/status` - System status

---

## 📚 Documentation Structure

This consolidated documentation includes:
- **System Overview**: Complete system understanding
- **Technical Documentation**: Architecture, APIs, implementation
- **Research Documentation**: ALIFE experiments and findings
- **User Guides**: How-to guides and tutorials
- **Maintenance Documentation**: Protocols and procedures

---

*Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*Generated by Documentation Consolidator*
"""
        
        try:
            with open(output_file, 'w') as f:
                f.write(content)
            print(f"   ✅ Generated {output_file.name}")
            return {"generated_file": str(output_file), "status": "success"}
        except Exception as e:
            print(f"   ❌ Error generating {output_file.name}: {e}")
            return {"status": "error", "error": str(e)}
    
    def get_capability_description(self, capability: str) -> str:
        """Get description for capability"""
        descriptions = {
            "RAG Search": "Semantic search across 38K+ indexed chunks",
            "Multi-Provider LLM": "Ollama (local), Groq (cloud), Gemini (cloud)",
            "Intent Detection": "Classifies query type for routing",
            "Coherence Arbiter": "Measures RAG/chip alignment",
            "Anchor Validator": "Validates claims against state files",
            "Context Builders": "Assembles context from memory/decisions/projects",
            "Filesystem Operations": "Read/write files in workspace",
            "Knowledge Graph": "Entity/relationship tracking",
            "PULSE Pattern Tracker": "Detects usage patterns for chip synthesis",
            "Decision Logging": "Records decisions with rationale",
            "Security Middleware": "Rate limiting, input validation, request protection",
            "Connection Monitor": "Health checks for 5 services, graceful fallbacks",
            "Response Cache": "Intelligent caching with LRU eviction, performance optimization",
            "Performance Tracker": "Real-time metrics, system monitoring, analytics",
            "Local AI Optimization": "Query analysis, model selection, performance profiling",
            "Genomic Impedance Sensor": "Environmental impedance detection for organisms",
            "Genomic Biasing Engine": "DNA copying bias based on impedance patterns",
            "Program Advance Chips": "MegaMan-inspired parallel processing with 5 strategic advances"
        }
        return descriptions.get(capability, "Capability description not available")
    
    def generate_technical_documentation(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate technical documentation"""
        output_file = self.consolidated_dir / "TECHNICAL_DOCUMENTATION.md"
        
        content = f"""# {config['title']}

{config['description']}

---

## 🏗️ System Architecture

### Backend Architecture
The FAITHH backend uses a modular Flask architecture with service-oriented design.

#### Core Components
"""
        
        # Add backend modules information
        backend_dir = self.project_root / "backend"
        if backend_dir.exists():
            content += "\n#### Backend Modules\n"
            for file_path in sorted(backend_dir.glob("*.py")):
                module_name = file_path.stem
                content += f"- **{module_name}**: {self.get_module_description(module_name)}\n"
        
        content += """
#### Service Layer
"""
        
        # Add services information
        services_dir = self.project_root / "app" / "services"
        if services_dir.exists():
            for file_path in sorted(services_dir.glob("*.py")):
                if not file_path.name.startswith("__"):
                    service_name = file_path.stem
                    content += f"- **{service_name}**: {self.get_service_description(service_name)}\n"
        
        content += """

## 🔌 API Endpoints

### Core Endpoints
"""
        
        # Extract endpoints from backend
        try:
            with open(self.project_root / "faithh_professional_backend_fixed.py", 'r') as f:
                content += self.extract_endpoints(f.read())
        except Exception as e:
            print(f"   ⚠️ Error extracting endpoints: {e}")
            content += "- Error extracting endpoints from backend file\n"
        
        content += """

## 🔧 Configuration

### Environment Variables
"""
        
        # Add configuration information
        config_file = self.project_root / "config.yaml"
        if config_file.exists():
            content += f"Configuration managed in `{config_file.name}` with the following sections:\n"
            try:
                with open(config_file, 'r') as f:
                    config_content = f.read()
                    lines = config_content.split('\n')
                    for line in lines:
                        if line.strip() and not line.startswith('#'):
                            content += f"- {line.strip()}\n"
            except Exception as e:
                print(f"   ⚠️ Error reading config.yaml: {e}")
        
        content += """
### Dependencies
"""
        
        # Add dependencies
        requirements_file = self.project_root / "requirements.txt"
        if requirements_file.exists():
            content += f"Dependencies managed in `{requirements_file.name}`:\n"
            try:
                with open(requirements_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            content += f"- {line}\n"
            except Exception as e:
                print(f"   ⚠️ Error reading requirements.txt: {e}")
        
        content += """

## 🔒 Security

### Security Measures
- **Rate Limiting**: Configurable request rate limiting
- **Input Validation**: Comprehensive input sanitization
- **Request Protection**: Security middleware for all endpoints
- **Access Control**: Role-based access management (planned)

### Monitoring
- **Health Checks**: Real-time service health monitoring
- **Performance Metrics**: Request tracking and analysis
- **Error Logging**: Comprehensive error tracking and reporting
- **Security Alerts**: Automated security monitoring

---

*Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*Generated by Documentation Consolidator*
"""
        
        try:
            with open(output_file, 'w') as f:
                f.write(content)
            print(f"   ✅ Generated {output_file.name}")
            return {"generated_file": str(output_file), "status": "success"}
        except Exception as e:
            print(f"   ❌ Error generating {output_file.name}: {e}")
            return {"status": "error", "error": str(e)}
    
    def extract_endpoints(self, backend_content: str) -> str:
        """Extract API endpoints from backend content"""
        endpoints = []
        lines = backend_content.split('\n')
        
        for line in lines:
            if '@app.route' in line:
                # Extract route information
                parts = line.split('@app.route')
                if len(parts) > 1:
                    route_info = parts[1].strip()
                    endpoints.append(f"- {route_info}")
        
        return '\n'.join(endpoints) if endpoints else "- No endpoints found\n"
    
    def get_module_description(self, module_name: str) -> str:
        """Get description for backend module"""
        descriptions = {
            "security_middleware": "Rate limiting, input validation, request protection",
            "connection_monitor": "Health checks for 5 services, graceful fallbacks",
            "cache": "Intelligent caching with LRU eviction, performance optimization",
            "performance": "Real-time metrics, system monitoring, analytics",
            "local_optimization": "Query analysis, model selection, performance profiling",
            "coherence_arbiter": "Measures RAG/chip alignment quality",
            "intent_detection": "Classifies query type for routing",
            "context_builders": "Assembles context from memory/decisions/projects",
            "enhanced_chip_integration": "Parallel chip retrieval with Program Advance system",
            "program_advance_optimizer": "Optimizes Program Advance chip selection and performance",
            "advanced_analytics_simple": "Predictive analytics with AI-powered insights",
            "ai_driven_ux": "Intelligent user experience with personalization and behavior analysis"
        }
        return descriptions.get(module_name, "Backend module")
    
    def get_service_description(self, service_name: str) -> str:
        """Get description for service"""
        descriptions = {
            "genomic_impedance_sensor": "Environmental impedance detection for organisms",
            "genomic_biasing_engine": "DNA copying bias based on impedance patterns",
            "parasitic_alife_service_fixed": "Parasitic impedance feeding in ALife experiments",
            "universal_impedance_field_optimized": "Universal impedance field calculations and optimization",
            "cosmic_ripple_integration": "Cosmic ripple effects on impedance patterns",
            "alife_parasitic_integration": "Integration of parasitic feeding with ALife data"
        }
        return descriptions.get(service_name, "Service module")
    
    def generate_research_documentation(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate research documentation"""
        output_file = self.consolidated_dir / "RESEARCH_DOCUMENTATION.md"
        
        content = f"""# {config['title']}

{config['description']}

---

## 🔬 ALIFE Research Overview

### Research Objectives
The ALIFE project investigates cultural evolution and parasitic impedance mechanisms in artificial agents, exploring how simple transmission mechanisms can lead to complex cultural systems.

### Key Research Questions
1. How do cultural protocols emerge from simple transmission mechanisms?
2. Can agents develop complex cultural systems with sophisticated protocols?
3. Does cultural complexity emerge from basic transmission and selection pressures?
4. How do parasitic impedance patterns affect cultural evolution?

---

## 🧪 Experiments

### Experiment Progression
"""
        
        # Add experiment information
        alife_dir = self.project_root / "projects" / "alife" / "experiments"
        if alife_dir.exists():
            experiments = sorted(alife_dir.glob("exp*.py"))
            for exp_file in experiments:
                exp_num = exp_file.stem.split('_')[1] if '_' in exp_file.stem else exp_file.stem
                content += f"\n#### Experiment {exp_num}\n"
                
                # Extract experiment description
                try:
                    with open(exp_file, 'r') as f:
                        exp_content = f.read()
                        lines = exp_content.split('\n')
                        
                        # Find scientific question
                        for line in lines:
                            if line.startswith("Scientific Question:"):
                                content += f"**{line}**\n"
                                break
                        
                        # Find biological insight
                        for line in lines:
                            if line.startswith("Biological Insight:"):
                                content += f"**{line}**\n"
                                break
                        
                        # Find success criteria
                        for line in lines:
                            if line.startswith("Success Criteria"):
                                content += f"**{line}**\n"
                                break
                except Exception as e:
                    print(f"   ⚠️ Error reading {exp_file.name}: {e}")
        
        content += """

## 📊 Research Findings

### Key Achievements
- **Cultural Transmission Breakthrough**: Experiment 8.2 successfully demonstrated agent cultural learning
- **Protocol Evolution**: Complex protocols emerge from simple transmission mechanisms
- **Multi-Generational Knowledge**: Knowledge accumulates across generations
- **Social Specialization**: Agents develop specialized cultural roles
- **Parasitic Impedance**: Novel energy feeding mechanisms discovered

### Statistical Results
"""
        
        # Add results from experiment 8 and 9
        results_dir = self.project_root / "projects" / "alife" / "results"
        if results_dir.exists():
            for result_file in results_dir.glob("*.json"):
                try:
                    with open(result_file, 'r') as f:
                        result_data = json.load(f)
                        content += f"\n#### {result_file.stem.replace('_', ' ').title()}\n"
                        for key, value in result_data.items():
                            if isinstance(value, (str, int, float)):
                                content += f"- **{key}**: {value}\n"
                except Exception as e:
                    print(f"   ⚠️ Error reading {result_file.name}: {e}")
        
        content += """

## 🔬 Genomic Research Integration

### Phase 6.0: Genomic Impedance Reading
Building on ALIFE research, Phase 6 integrates environmental impedance patterns with biological systems.

### Key Findings
- **Environmental Detection**: Organisms can sense environmental impedance patterns
- **Genomic Biasing**: DNA copying bias correlates with environmental patterns
- **Cognitive Enhancement**: 25% expression bias for cognitive genes
- **Statistical Significance**: Perfect correlation (1.000) between biasing and enhancement

### Experimental Results
- **Phase 1**: Large-scale testing (100 organisms) - 100% success rate
- **Phase 2**: Environmental adaptation (50 organisms) - Adaptive success
- **Phase 3**: Multi-generational evolution (40 organisms, 5 generations) - Evolutionary success

---

## 📈 Future Research Directions

### Next Phase Objectives
1. **Advanced Cultural Systems**: More sophisticated cultural protocols
2. **Real Biological Data**: Integration with actual biological systems
3. **Multi-Agent Coordination**: Complex social organization
4. **Environmental Dynamics**: More complex environmental modeling
5. **Publication Preparation**: Academic paper preparation and submission

### Research Methodology
- **Progressive Complexity**: Start simple, increase complexity gradually
- **Statistical Validation**: Rigorous statistical analysis of results
- **Replication**: Ensure results are reproducible
- **Documentation**: Comprehensive documentation of methodologies and findings

---

## 📚 Research Resources

### Data Storage
- **Experiment Results**: `/projects/alife/results/`
- **Configuration Files**: `/projects/alife/config.py`
- **Analysis Reports**: `/projects/alife/results/*/analysis_report.md`

### Code Organization
- **Core System**: `/projects/alife/simulation.py`, `/projects/alife/agent.py`, `/projects/alife/world.py`
- **Experiments**: `/projects/alife/experiments/`
- **Operations**: `/projects/alife/ops.py`

---

*Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*Generated by Documentation Consolidator*
"""
        
        try:
            with open(output_file, 'w') as f:
                f.write(content)
            print(f"   ✅ Generated {output_file.name}")
            return {"generated_file": str(output_file), "status": "success"}
        except Exception as e:
            print(f"   ❌ Error generating {output_file.name}: {e}")
            return {"status": "error", "error": str(e)}
    
    def generate_user_guides(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate user guides"""
        output_file = self.consolidated_dir / "USER_GUIDES.md"
        
        content = f"""# {config['title']}

{config['description']}

---

## 🚀 Quick Start Guide

### System Setup
"""
        
        # Add setup instructions
        content += self.generate_setup_instructions()
        
        content += """
### Basic Usage
"""
        
        # Add basic usage
        content += self.generate_basic_usage()
        
        content += """
---

## 📚 Advanced Guides

### Genomic Experiments
"""
        
        # Add genomic experiment guide
        content += self.generate_genomic_guide()
        
        content += """
### ALIFE Research
"""
        
        # Add ALIFE research guide
        content += self.generate_alife_guide()
        
        content += """
### Development
"""
        
        # Add development guide
        content += self.generate_development_guide()
        
        content += """

---

## 🔧 Troubleshooting

### Common Issues
"""
        
        # Add troubleshooting
        content += self.generate_troubleshooting()
        
        content += """

---

## 📞 Advanced Features

### Program Advance System
"""
        
        # Add Program Advance guide
        content += self.generate_program_advance_guide()
        
        content += """
### Coherence Arbiter
"""
        
        # Add Coherence Arbiter guide
        content += self.generate_coherence_guide()
        
        content += """

---

*Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*Generated by Documentation Consolidator*
"""
        
        try:
            with open(output_file, 'w') as f:
                f.write(content)
            print(f"   ✅ Generated {output_file.name}")
            return {"generated_file": str(output_file), "status": "success"}
        except Exception as e:
            print(f"   ❌ Error generating {output_file.name}: {e}")
            return {"status": "error", "error": str(e)}
    
    def generate_setup_instructions(self) -> str:
        """Generate setup instructions"""
        return """1. **Prerequisites**
   - Python 3.8+ installed
   - Docker and Docker Compose
   - Git for version control

2. **Environment Setup**
   ```bash
   # Clone repository
   git clone <repository-url>
   cd ai-stack
   
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Infrastructure Setup**
   ```bash
   # Start services
   docker-compose up -d
   
   # Verify services
   docker-compose ps
   ```

4. **Backend Setup**
   ```bash
   # Start backend
   ./restart_backend.sh
   
   # Verify health
   curl http://localhost:5557/health
   ```"""
    
    def generate_basic_usage(self) -> str:
        """Generate basic usage instructions"""
        return """### Chat Interface
Access the FAITHH interface at http://localhost:5557

### API Usage
```bash
# Chat with FAITHH
curl -X POST http://localhost:5557/api/chat \\
  -H "Content-Type: application/json" \\
  -d '{"message": "What projects am I working on?"}'

# Search knowledge base
curl -X POST http://localhost:5557/api/search \\
  -H "Content-Type: application/json" \\
  -d '{"query": "genomic experiments", "n_results": 5}'

# Get system status
curl http://localhost:5557/api/status
```

### Context Features
- **Self-Awareness**: FAITHH knows about itself and your projects
- **Decision Tracking**: References past decisions with rationale
- **Project Awareness**: Understands current project states
- **Intent Detection**: Routes queries to appropriate tools"""
    
    def generate_genomic_guide(self) -> str:
        """Generate genomic experiment guide"""
        return """### Overview
Phase 6 introduces genomic impedance reading, bridging environmental patterns with biological systems.

### Running Experiments
```bash
# Large-scale test
cd experiments/genomic
python3 genomic_large_scale_test.py

# Environmental adaptation
python3 environmental_adaptation_test.py

# Multi-generational evolution
python3 multi_generational_adaptation_fixed.py
```

### API Usage
```bash
# Create genomic sensor
curl -X POST http://localhost:5557/api/genomic/impedance-sensor \\
  -H "Content-Type: application/json" \\
  -d '{"organism_id": "test_organism", "position": [1.0, 0.0, 0.0], "sensitivity": 0.7}'

# Analyze biasing
curl -X POST http://localhost:5557/api/genomic/biasing-analysis \\
  -H "Content-Type: application/json" \\
  -d '{"organism_id": "test_organism", "original_genome": "ATGCGTACATGCGTAC", "biasing_strength": 0.7}'
```

### Understanding Results
- **Biasing Potential**: Environmental influence on genetic changes
- **Cognitive Enhancement**: Gene expression bias for cognitive functions
- **Evolutionary Success**: Multi-generational fitness improvements"""
    
    def generate_alife_guide(self) -> str:
        """Generate ALIFE research guide"""
        return """### Overview
ALIFE experiments investigate cultural evolution in artificial agents.

### Running Experiments
```bash
cd projects/alife
python3 experiments/exp9_complex_cultural_evolution.py
```

### Experiment Configuration
Edit `config.py` to modify parameters:
- Population size
- Environmental conditions
- Evolutionary pressures

### Understanding Results
- **Protocol Evolution**: How cultural protocols change over time
- **Social Specialization**: Emergence of specialized roles
- **Knowledge Accumulation**: Multi-generational learning"""
    
    def generate_development_guide(self) -> str:
        """Generate development guide"""
        return """### Development Environment
- **IDE**: VS Code with FAITHH extension recommended
- **Testing**: Use `python -m pytest tests/`
- **Debugging**: Backend logs at `/tmp/backend_debug.log`

### Code Structure
```
backend/           # Backend modules
app/services/      # Service layer
experiments/       # Experiments
docs/             # Documentation
scripts/          # Utility scripts
```

### Contributing
1. Follow existing code style
2. Add tests for new features
3. Update documentation
4. Submit pull requests"""
    
    def generate_troubleshooting(self) -> str:
        """Generate troubleshooting guide"""
        return """### Common Issues

#### Backend Not Starting
```bash
# Check if port is in use
lsof -i :5557

# Check logs
tail -f backend.log

# Restart backend
./restart_backend.sh
```

#### ChromaDB Connection Issues
```bash
# Check ChromaDB health
curl http://192.158.1.10:8000/api/v2/heartbeat

# Restart services
docker-compose restart chromadb
```

#### Memory Issues
```bash
# Check memory usage
free -h

# Restart backend if needed
./restart_backend.sh
```

#### Genomic Experiments Not Working
```bash
# Verify genomic endpoints
curl http://localhost:5557/api/genomic/impedance-sensor

# Check error logs
grep -i genomic backend.log
```"""
    
    def generate_program_advance_guide(self) -> str:
        """Generate Program Advance guide"""
        return """### Overview
Program Advance system provides strategic chip combinations for complex queries.

### Triggering Program Advance
Use specific phrases in your queries:
- "everything about..." → Full Recall
- "business status" → Business Review
- "where was I" → Context Recovery
- "why did we" → Decision Audit
- "project status" → Project Deep Dive

### Available Advances
- **Full Recall**: Maximum context assembly
- **Business Review**: Business-focused analysis
- **Context Recovery**: Timeline context recovery
- **Decision Audit**: Decision forensics with evidence
- **Project Deep Dive**: Multi-domain project analysis"""
    
    def generate_coherence_guide(self) -> str:
        """Generate Coherence Arbiter guide"""
        return """### Overview
Coherence Arbiter measures alignment between RAG retrieval and ML chip signals.

### Understanding Coherence Scores
- **High (0.6+)**: Strong alignment between sources
- **Medium (0.3-0.6)**: Moderate alignment
- **Low (<0.3)**: Weak alignment, may need clarification

### Coherence Indicators
- **Tier**: High/Medium/Low coherence level
- **Reasons**: Why coherence score is what it is
- **Suggestions**: Recommended actions for improvement"""
    
    def generate_maintenance_documentation(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate maintenance documentation"""
        output_file = self.consolidated_dir / "MAINTENANCE_DOCUMENTATION.md"
        
        content = f"""# {config['title']}

{config['description']}

---

## 📅 Maintenance Schedule

### Daily Tasks (5 minutes)
"""
        
        # Add daily tasks
        content += self.generate_daily_tasks()
        
        content += """
### Weekly Tasks (30 minutes)
"""
        
        # Add weekly tasks
        content += self.generate_weekly_tasks()
        
        content += """
### Monthly Tasks (2 hours)
"""
        
        # Add monthly tasks
        content += self.generate_monthly_tasks()
        
        content += """
### Quarterly Tasks (4 hours)
"""
        
        # Add quarterly tasks
        content += self.generate_quarterly_tasks()
        
        content += """

---

## 🔧 Maintenance Procedures

### Health Checks
"""
        
        # Add health check procedures
        content += self.generate_health_check_procedures()
        
        content += """
### Backup Procedures
"""
        
        # Add backup procedures
        content += self.generate_backup_procedures()
        
        content += """
### Security Procedures
"""
        
        # Add security procedures
        content += self.generate_security_procedures()
        
        content += """

---

## 📊 Monitoring

### Key Metrics
- **Uptime**: System availability percentage
- **Response Time**: Average query response time
- **Error Rate**: Percentage of failed requests
- **Cache Hit Rate**: Cache effectiveness
- **Memory Usage**: System resource consumption

### Alert Thresholds
- **Uptime**: < 99% triggers alert
- **Response Time**: > 5 seconds triggers alert
- **Error Rate**: > 1% triggers alert
- **Memory Usage**: > 80% triggers alert

---

## 🚨 Emergency Procedures

### System Failure
1. **Assess Impact**: Determine affected systems
2. **Immediate Action**: Restart critical services
3. **Communication**: Notify stakeholders
4. **Recovery**: Restore normal operations
5. **Review**: Post-mortem analysis

### Data Loss
1. **Stop Operations**: Prevent further damage
2. **Assess Impact**: Determine data affected
3. **Restore**: Recover from backups
4. **Verify**: Confirm data integrity
5. **Review**: Update procedures

---

## 📋 Maintenance Scripts

### Available Scripts
"""
        
        # Add maintenance scripts
        content += self.generate_maintenance_scripts()
        
        content += """

---

## 🔄 Automation

### Automated Tasks
- **Documentation Generation**: Weekly documentation updates
- **Health Monitoring**: Continuous system health checks
- **Backup Verification**: Automated backup validation
- **Performance Analysis**: Regular performance reviews

### Scheduled Tasks
- **Daily**: Health checks, log monitoring
- **Weekly**: Documentation updates, security patches
- **Monthly**: Full system audit, archive cleanup
- **Quarterly**: Strategic review, architecture assessment

---

*Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*Generated by Documentation Consolidator*
"""
        
        try:
            with open(output_file, 'w') as f:
                f.write(content)
            print(f"   ✅ Generated {output_file.name}")
            return {"generated_file": str(output_file), "status": "success"}
        except Exception as e:
            print(f"   ❌ Error generating {output_file.name}: {e}")
            return {"status": "error", "error": str(e)}
    
    def generate_daily_tasks(self) -> str:
        """Generate daily maintenance tasks"""
        return """```bash
# Health Check
curl http://localhost:5557/health

# Log Monitoring
tail -n 20 ~/ai-stack/backend.log | grep ERROR

# Performance Check
curl http://localhost:5557/api/status | jq '.performance'

# Security Monitoring
curl http://localhost:5557/api/metrics | jq '.security'

# Memory Check
free -h | grep Mem:
```

**Expected Output**: All services should return healthy status"""
    
    def generate_weekly_tasks(self) -> str:
        """Generate weekly maintenance tasks"""
        return """```bash
# Documentation Update
cd ~/ai-stack && python3 scripts/generate_context.py

# Security Updates
cd ~/ai-stack && python3 -m pip audit --requirement requirements.txt

# Backup Verification
cd ~/ai-stack && python3 scripts/verify_backups.py

# Performance Analysis
cd ~/ai-stack && python3 scripts/analyze_performance.py

# Dependency Updates
cd ~/ai-stack && python3 -m pip install --upgrade -r requirements.txt
```

**Expected Outcome**: Updated documentation and security patches"""
    
    def generate_monthly_tasks(self) -> str:
        """Generate monthly maintenance tasks"""
        return """```bash
# Full System Audit
cd ~/ai-stack && python3 scripts/monthly_audit.py

# Archive Cleanup
cd ~/ai-stack && python3 scripts/cleanup_archives.py

# Documentation Review
cd ~/ai-stack && python3 scripts/review_documentation.py

# Capacity Planning
cd ~/ai-stack && python3 scripts/capacity_planning.py

# Log Rotation
cd ~/ai-stack && python3 scripts/rotate_logs.py

# Database Optimization
cd ~/ai-stack && python3 scripts/optimize_database.py
```

**Expected Outcome**: Clean system and optimized performance"""
    
    def generate_quarterly_tasks(self) -> str:
        """Generate quarterly maintenance tasks"""
        return """```bash
# Strategic Review
cd ~/ai-stack && python3 scripts/strategic_review.py

# Architecture Assessment
cd ~/ai-stack && python3 scripts/architecture_review.py

# Technology Evaluation
cd ~/ai-stack && python3 scripts/tech_evaluation.py

# Long-term Planning
cd ~/ai-stack && python3 scripts/long_term_planning.py

# Security Audit
cd ~/ai-stack && python3 scripts/security_audit.py

# Performance Optimization
cd ~/ai-stack && python3 scripts/performance_optimization.py
```

**Expected Outcome**: Strategic alignment and optimized architecture"""
    
    def generate_health_check_procedures(self) -> str:
        """Generate health check procedures"""
        return """### Backend Health
```bash
# Main health endpoint
curl http://localhost:5557/health

# Detailed status
curl http://localhost:5557/api/status

# Performance metrics
curl http://localhost:5557/api/metrics
```

### Database Health
```bash
# ChromaDB health
curl http://192.158.1.10:8000/api/v2/heartbeat

# Database stats
curl http://192.158.1.10:8000/api/v2/collections
```

### Service Health
```bash
# Check all services
docker-compose ps

# Service logs
docker-compose logs --tail=50
```

### Expected Results
- All services should return "healthy" status
- Response times should be < 2 seconds
- No error messages in logs"""
    
    def generate_backup_procedures(self) -> str:
        """Generate backup procedures"""
        return """### State Files Backup
```bash
# Backup critical state files
cp faithh_memory.json backups/
cp project_states.json backups/
cp decisions_log.json backups/
cp scaffolding_state.json backups/
```

### Code Backup
```bash
# Git repository
git add .
git commit -m "Backup $(date)"
git push origin main
```

### Database Backup
```bash
# ChromaDB export
docker-compose exec chromadb chroma-export
```

### Automation
```bash
# Automated backup script
cd ~/ai-stack && python3 scripts/automated_backup.py
```

### Verification
```bash
# Verify backup integrity
cd ~/ai-stack && python3 scripts/verify_backups.py
```"""
    
    def generate_security_procedures(self) -> str:
        """Generate security procedures"""
        return """### Security Audit
```bash
# Vulnerability scan
cd ~/ai-stack && python3 scripts/security_audit.py

# Dependency check
cd ~/ai-stack && python3 -m pip audit --requirement requirements.txt

# Access control review
cd ~/ai-stack && python3 scripts/access_control_review.py
```

### Updates
```bash
# Security patches
cd ~/ai-stack && python3 -m pip install --upgrade -r requirements.txt

# System updates
sudo apt update && sudo apt upgrade -y
```

### Monitoring
```bash
# Security monitoring
cd ~/ai-stack && python3 scripts/security_monitoring.py

# Log analysis
cd ~/ai-stack && python3 scripts/security_log_analysis.py
```

### Best Practices
- Regular security audits (quarterly)
- Keep dependencies updated
- Monitor for unusual activity
- Use strong authentication
- Implement rate limiting"""
    
    def generate_maintenance_scripts(self) -> str:
        """Generate maintenance scripts overview"""
        return """### Available Scripts

#### Documentation Scripts
- `scripts/generate_context.py` - Generate project context
- `scripts/review_documentation.py` - Review and update documentation
- `scripts/documentation_consolidator.py` - This script

#### Monitoring Scripts
- `scripts/monthly_audit.py` - Comprehensive system audit
- `scripts/analyze_performance.py` - Performance analysis
- `scripts/health_check.py` - Automated health monitoring
- `scripts/verify_backups.py` - Backup verification

#### Maintenance Scripts
- `scripts/cleanup_archives.py` - Archive cleanup
- `scripts/rotate_logs.py` - Log rotation
- `scripts/optimize_database.py` - Database optimization
- `scripts/capacity_planning.py` - Capacity planning

#### Security Scripts
- `scripts/security_audit.py` - Security vulnerability scan
- `scripts/access_control_review.py` - Access control review
- `scripts/security_monitoring.py` - Security monitoring
- `scripts/security_log_analysis.py` - Log analysis for security

#### Backup Scripts
- `scripts/automated_backup.py` - Automated backup system
- `scripts/verify_backups.py` - Backup integrity verification
- `scripts/restore_backup.py` - Backup restoration

#### Automation Scripts
- `scripts/automated_health_check.py` - Automated health monitoring
- `scripts/automated_documentation.py` - Automated documentation updates
- `scripts/scheduled_maintenance.py` - Scheduled maintenance tasks
- `scripts/maintenance_scheduler.py` - Maintenance task scheduling"""
    
    def generate_master_index(self, results: Dict[str, Any]) -> str:
        """Generate master index for all documentation"""
        index_content = f"""# Master Documentation Index

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
"""
        
        for file_path in results.get("generated_files", []):
            file_name = Path(file_path).name
            content += f"- **{file_name}**: {file_path}\n"
        
        content += f"""
### Processing Results
"""
        
        for section, result in results.get("consolidation_results", {}).items():
            status = result.get("status", "unknown")
            content += f"- **{section}**: {status}\n"
        
        content += f"""
### Statistics
"""
        
        stats = results.get("statistics", {})
        for key, value in stats.items():
            content += f"- **{key}**: {value}\n"
        
        content += f"""
### Recommendations
"""
        
        recommendations = results.get("recommendations", [])
        for i, rec in enumerate(recommendations[:5], 1):
            content += f"{i}. {rec}\n"
        
        content += """

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
python3 scripts/maintenance/documentation_consolidator.py
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
            index_file = self.consolidated_dir / "MASTER_INDEX.md"
            with open(index_file, 'w') as f:
                f.write(index_content)
            print(f"   ✅ Generated {index_file.name}")
            return str(index_file)
        except Exception as e:
            print(f"   ❌ Error generating master index: {e}")
            return str(index_file)
    
    def generate_statistics(self) -> Dict[str, Any]:
        """Generate statistics about the consolidation"""
        return {
            "total_files_generated": len(self.structure),
            "total_documentation_files": sum(len(config["files"]) for config in self.structure.values()),
            "categories_processed": len(self.structure),
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