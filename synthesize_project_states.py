#!/usr/bin/env python3
"""
FAITHH Project State Synthesis
===============================
Generates summary documents of each project's current state from the knowledge base.

This script analyzes project states, recent decisions, and current context to create
comprehensive Markdown summaries for team members and stakeholders.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

def load_project_states() -> Dict:
    """Load project states from JSON file"""
    try:
        with open('project_states.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("⚠️  project_states.json not found")
        return {}
    except json.JSONDecodeError as e:
        print(f"⚠️  Error reading project_states.json: {e}")
        return {}

def load_recent_decisions() -> List[Dict]:
    """Load recent decisions from decisions log"""
    try:
        with open('decisions_log.json', 'r') as f:
            data = json.load(f)
            return data.get('decisions', [])
    except FileNotFoundError:
        print("⚠️  decisions_log.json not found")
        return []
    except json.JSONDecodeError as e:
        print(f"⚠️  Error reading decisions_log.json: {e}")
        return []

def load_faithh_memory() -> Dict:
    """Load FAITHH memory for context"""
    try:
        with open('faithh_memory.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("⚠️  faithh_memory.json not found")
        return {}
    except json.JSONDecodeError as e:
        print(f"⚠️  Error reading faithh_memory.json: {e}")
        return {}

def synthesize_project_state(project_name: str, project_data: Dict, recent_decisions: List[Dict], memory: Dict) -> str:
    """Generate a comprehensive project state summary"""
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Extract project information
    status = project_data.get('status', 'unknown')
    priority = project_data.get('priority', 'medium')
    progress = project_data.get('progress', 0)
    description = project_data.get('description', 'No description available')
    
    # Get recent decisions relevant to this project
    project_decisions = [d for d in recent_decisions if project_name.lower() in d.get('context', '').lower()]
    
    # Get memory entries relevant to this project
    relevant_memory = {k: v for k, v in memory.items() if project_name.lower() in str(v).lower()}
    
    # Build the summary
    summary = f"""# {project_name} Project State Summary

**Generated**: {timestamp}  
**Status**: {status.upper()}  
**Priority**: {priority}  
**Progress**: {progress}%

---

## 📋 **Project Overview**

{description}

---

## 🎯 **Current Status**

### **Health Indicators**
- **Status**: {status}
- **Priority Level**: {priority}
- **Completion Progress**: {progress}%
- **Last Updated**: {project_data.get('last_updated', 'Unknown')}

### **Active Components"""
    
    # Add components if available
    components = project_data.get('components', {})
    if components:
        for comp_name, comp_data in components.items():
            comp_status = comp_data.get('status', 'unknown')
            summary += f"\n- **{comp_name}**: {comp_status}"
    
    summary += f"""

### **Key Metrics**
"""
    
    # Add metrics if available
    metrics = project_data.get('metrics', {})
    if metrics:
        for metric_name, metric_value in metrics.items():
            summary += f"\n- **{metric_name}**: {metric_value}"
    else:
        summary += "\n- No specific metrics tracked"
    
    summary += f"""

---

## 🔄 **Recent Activity**

### **Latest Decisions ({len(project_decisions)} decisions)**
"""
    
    if project_decisions:
        for i, decision in enumerate(project_decisions[:5], 1):  # Show last 5 decisions
            decision_date = decision.get('date', 'Unknown date')
            decision_title = decision.get('title', 'Untitled decision')
            decision_status = decision.get('status', 'pending')
            summary += f"\n{i}. **{decision_title}** ({decision_date}) - {decision_status}"
            
            # Add brief rationale if available
            rationale = decision.get('rationale', '')
            if rationale and len(rationale) > 0:
                summary += f"\n   - *Rationale*: {rationale[:100]}{'...' if len(rationale) > 100 else ''}"
    else:
        summary += "\nNo recent decisions found for this project."
    
    summary += f"""

### **Memory Context ({len(relevant_memory)} relevant entries)**
"""
    
    if relevant_memory:
        for memory_key, memory_value in list(relevant_memory.items())[:3]:  # Show top 3
            summary += f"\n- **{memory_key}**: {str(memory_value)[:100]}{'...' if len(str(memory_value)) > 100 else ''}"
    else:
        summary += "\nNo specific memory context found for this project."
    
    summary += f"""

---

## 🚀 **Next Steps & Actions**

### **Immediate Actions (Next 7 days)**
"""
    
    # Add next steps if available
    next_steps = project_data.get('next_steps', [])
    if next_steps:
        for i, step in enumerate(next_steps[:3], 1):
            summary += f"\n{i}. {step}"
    else:
        summary += "\n- Review project priorities and define immediate actions"
        summary += "\n- Update progress metrics and status indicators"
    
    summary += f"""

### **Upcoming Milestones**
"""
    
    # Add milestones if available
    milestones = project_data.get('milestones', [])
    if milestones:
        for milestone in milestones[:3]:  # Show next 3 milestones
            milestone_name = milestone.get('name', 'Unnamed milestone')
            milestone_date = milestone.get('target_date', 'No target date')
            summary += f"\n- **{milestone_name}**: {milestone_date}"
    else:
        summary += "\n- Define specific milestones and target dates"
    
    summary += f"""

---

## 🔧 **Technical Details**

### **Dependencies & Integrations**
"""
    
    # Add dependencies if available
    dependencies = project_data.get('dependencies', [])
    if dependencies:
        for dep in dependencies:
            summary += f"\n- {dep}"
    else:
        summary += "\n- No specific dependencies documented"
    
    summary += f"""

### **Configuration & Settings**
"""
    
    # Add configuration if available
    config = project_data.get('config', {})
    if config:
        for config_key, config_value in list(config.items())[:5]:  # Show top 5
            summary += f"\n- **{config_key}**: {config_value}"
    else:
        summary += "\n- No specific configuration documented"
    
    summary += f"""

---

## 📊 **Risk Assessment & Mitigation**

### **Current Risks**
"""
    
    # Add risks if available
    risks = project_data.get('risks', [])
    if risks:
        for risk in risks[:3]:  # Show top 3 risks
            risk_name = risk.get('name', 'Unnamed risk')
            risk_impact = risk.get('impact', 'unknown')
            risk_probability = risk.get('probability', 'unknown')
            summary += f"\n- **{risk_name}** (Impact: {risk_impact}, Probability: {risk_probability})"
    else:
        summary += "\n- No specific risks documented"
    
    summary += f"""

### **Mitigation Strategies**
"""
    
    # Add mitigation strategies if available
    mitigations = project_data.get('mitigations', [])
    if mitigations:
        for mitigation in mitigations[:3]:  # Show top 3 mitigations
            summary += f"\n- {mitigation}"
    else:
        summary += "\n- Develop risk assessment framework"
        summary += "\n- Create mitigation strategies for identified risks"
    
    summary += f"""

---

## 📈 **Success Metrics & KPIs**

### **Performance Indicators**
"""
    
    # Add KPIs if available
    kpis = project_data.get('kpis', {})
    if kpis:
        for kpi_name, kpi_value in kpis.items():
            summary += f"\n- **{kpi_name}**: {kpi_value}"
    else:
        summary += "\n- Define specific KPIs for project success"
        summary += "\n- Establish baseline measurements"
    
    summary += f"""

---

## 👥 **Team & Stakeholders**

### **Team Members**
"""
    
    # Add team members if available
    team = project_data.get('team', [])
    if team:
        for member in team:
            member_name = member.get('name', 'Unnamed member')
            member_role = member.get('role', 'No role specified')
            summary += f"\n- **{member_name}**: {member_role}"
    else:
        summary += "\n- Document team members and their roles"
    
    summary += f"""

### **Stakeholders**
"""
    
    # Add stakeholders if available
    stakeholders = project_data.get('stakeholders', [])
    if stakeholders:
        for stakeholder in stakeholders:
            stakeholder_name = stakeholder.get('name', 'Unnamed stakeholder')
            stakeholder_interest = stakeholder.get('interest', 'No interest specified')
            summary += f"\n- **{stakeholder_name}**: {stakeholder_interest}"
    else:
        summary += "\n- Identify key stakeholders and their interests"
    
    summary += f"""

---

## 📝 **Notes & Observations**

### **Key Insights**
- Project status synthesized from available data sources
- Recent decisions and memory context analyzed for relevance
- Recommendations generated based on current project state

### **Data Sources**
- project_states.json
- decisions_log.json  
- faithh_memory.json

### **Generation Information**
- Generated by FAITHH Project State Synthesis
- Timestamp: {timestamp}
- Version: 1.0

---

*This summary was automatically generated. Please review and update as needed.*
"""
    
    return summary

def main():
    """Main synthesis process"""
    print("🔄 FAITHH Project State Synthesis")
    print("=" * 50)
    
    # Load data sources
    project_states = load_project_states()
    recent_decisions = load_recent_decisions()
    faithh_memory = load_faithh_memory()
    
    if not project_states:
        print("❌ No project states found. Exiting.")
        return
    
    # Create output directory
    output_dir = Path("docs/project_summaries")
    output_dir.mkdir(exist_ok=True, parents=True)
    
    # Generate summaries for each project
    summaries_generated = 0
    
    # Handle the actual project_states.json structure
    # It has metadata at top level and strategic_plan as the main project
    if 'strategic_plan' in project_states:
        # Generate summary for the strategic plan
        print(f"\n📋 Processing project: FAITHH Strategic Plan")
        
        strategic_data = project_states['strategic_plan']
        summary = synthesize_project_state("FAITHH Strategic Plan", strategic_data, recent_decisions, faithh_memory)
        
        # Save summary
        output_file = output_dir / "faithh_strategic_plan_summary.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        print(f"✅ Summary saved: {output_file}")
        summaries_generated += 1
        
        # Also generate domain summaries if they exist
        domains = strategic_data.get('domains', {})
        for domain_name, domain_data in domains.items():
            print(f"\n📋 Processing domain: {domain_name}")
            
            domain_summary = synthesize_project_state(f"{domain_name.title()} Domain", domain_data, recent_decisions, faithh_memory)
            
            # Save domain summary
            domain_file = output_dir / f"{domain_name.lower()}_domain_summary.md"
            with open(domain_file, 'w', encoding='utf-8') as f:
                f.write(domain_summary)
            
            print(f"✅ Domain summary saved: {domain_file}")
            summaries_generated += 1
    
    # Generate index file
    index_content = f"""# FAITHH Project Summaries Index

**Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Total Projects**: {summaries_generated}

---

## Available Project Summaries

"""
    
    # Add main strategic plan
    index_content += "- [FAITHH Strategic Plan](./faithh_strategic_plan_summary.md)\n"
    
    # Add domain summaries if they exist
    if 'strategic_plan' in project_states and 'domains' in project_states['strategic_plan']:
        for domain_name in project_states['strategic_plan']['domains'].keys():
            domain_file = f"{domain_name.lower()}_domain_summary.md"
            index_content += f"- [{domain_name.title()} Domain](./{domain_file})\n"
    
    index_content += f"""

---

## About These Summaries

These project state summaries were automatically generated by the FAITHH Project State Synthesis system. Each summary includes:

- **Project Overview**: Current status, priority, and progress
- **Recent Activity**: Latest decisions and memory context  
- **Next Steps**: Immediate actions and upcoming milestones
- **Technical Details**: Dependencies, configuration, and risks
- **Success Metrics**: KPIs and performance indicators
- **Team Information**: Members and stakeholders

### Data Sources
- `project_states.json` - Primary project state data
- `decisions_log.json` - Recent decision history
- `faithh_memory.json` - Contextual memory entries

### Generation Details
- **Tool**: FAITHH Project State Synthesis v1.0
- **Timestamp**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- **Format**: Markdown with structured sections

---

*For the most up-to-date information, refer to the primary data sources.*
"""
    
    # Save index
    index_file = output_dir / "index.md"
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write(index_content)
    
    print(f"\n📊 Synthesis Complete!")
    print(f"✅ Generated {summaries_generated} project summaries")
    print(f"✅ Created index: {index_file}")
    print(f"📁 Output directory: {output_dir}")
    
    # Display statistics
    print(f"\n📈 Statistics:")
    print(f"   Projects processed: {1 if 'strategic_plan' in project_states else 0}")
    print(f"   Decisions analyzed: {len(recent_decisions)}")
    print(f"   Memory entries: {len(faithh_memory)}")
    print(f"   Summaries generated: {summaries_generated}")

if __name__ == "__main__":
    main()
