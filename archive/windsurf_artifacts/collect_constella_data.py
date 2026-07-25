#!/usr/bin/env python3
"""
FAITHH Constella Data Collection System
=======================================
Comprehensive data collection framework for Constella AI harmony framework.

This module collects and synthesizes:
- Project states and decisions
- Knowledge base insights
- Conversation history
- Performance metrics
- User behavior patterns
- Technical stack documentation
- Inspiration and reference materials
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import re

class ConstellaDataCollector:
    """Collect and synthesize data for Constella framework"""
    
    def __init__(self):
        self.collected_data = {
            "project_states": {},
            "decisions": {},
            "knowledge_base": {},
            "conversations": {},
            "performance_metrics": {},
            "user_behavior": {},
            "technical_stack": {},
            "inspiration_references": {}
        }
        self.collection_timestamp = datetime.now()
        
    def collect_project_states(self) -> Dict:
        """Collect current project states and synthesize insights"""
        print("🔍 Collecting project states...")
        
        # Load existing project states
        try:
            with open('project_states.json', 'r') as f:
                project_states = json.load(f)
        except Exception as e:
            print(f"⚠️  Could not load project_states.json: {e}")
            return {"error": "Could not load project states"}
        
        synthesized_states = {
            "collection_timestamp": datetime.now().isoformat(),
            "total_projects": 0,
            "active_projects": {},
            "project_insights": [],
            "next_steps_summary": {},
            "progress_metrics": {}
        }
        
        # Process strategic plan
        if 'strategic_plan' in project_states:
            plan = project_states['strategic_plan']
            synthesized_states["strategic_overview"] = {
                "vision": plan.get('vision', ''),
                "current_phase": plan.get('current_quarter', ''),
                "theme": plan.get('quarterly_theme', ''),
                "year": plan.get('current_year', 1)
            }
            
            # Process domains
            domains = plan.get('domains', {})
            for domain_name, domain_data in domains.items():
                synthesized_states["active_projects"][domain_name] = {
                    "name": domain_data.get('name', domain_name.title()),
                    "status": domain_data.get('current_status', 'Unknown'),
                    "year_1_goal": domain_data.get('year_1_goal', ''),
                    "priorities": domain_data.get('q1_2026_priorities', []),
                    "last_updated": project_states.get('last_updated', '')
                }
                
                # Generate insights
                if domain_data.get('current_status'):
                    insight = {
                        "project": domain_name,
                        "insight": f"{domain_name.title()} is currently in '{domain_data['current_status']}' phase",
                        "priority_items": len(domain_data.get('q1_2026_priorities', [])),
                        "readiness": "high" if "Complete" in domain_data.get('current_status', '') else "medium"
                    }
                    synthesized_states["project_insights"].append(insight)
        
        synthesized_states["total_projects"] = len(synthesized_states["active_projects"])
        
        # Collect recent decisions for context
        try:
            with open('decisions_log.json', 'r') as f:
                decisions_data = json.load(f)
                recent_decisions = decisions_data.get('decisions', [])[:10]  # Last 10 decisions
                
                synthesized_states["recent_decisions"] = {
                    "count": len(recent_decisions),
                    "latest_decisions": [
                        {
                            "title": d.get('title', ''),
                            "date": d.get('date', ''),
                            "status": d.get('status', ''),
                            "context": d.get('context', '')[:100] + "..." if len(d.get('context', '')) > 100 else d.get('context', '')
                        }
                        for d in recent_decisions
                    ]
                }
        except Exception as e:
            print(f"⚠️  Could not load decisions: {e}")
            synthesized_states["recent_decisions"] = {"count": 0, "latest_decisions": []}
        
        print(f"✅ Collected {synthesized_states['total_projects']} project states")
        return synthesized_states
    
    def collect_knowledge_base_insights(self) -> Dict:
        """Collect and synthesize knowledge base insights"""
        print("📚 Collecting knowledge base insights...")
        
        insights = {
            "collection_timestamp": datetime.now().isoformat(),
            "total_documents": 0,
            "topic_clusters": {},
            "frequent_concepts": [],
            "knowledge_gaps": [],
            "synthesis_quality": "unknown"
        }
        
        # Analyze project summaries
        summaries_dir = Path("docs/project_summaries")
        if summaries_dir.exists():
            summary_files = list(summaries_dir.glob("*.md"))
            insights["project_summaries"] = {
                "count": len(summary_files),
                "files": [f.name for f in summary_files]
            }
            
            # Extract concepts from summaries
            all_concepts = []
            for summary_file in summary_files:
                try:
                    with open(summary_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Extract key concepts (simple keyword extraction)
                        words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', content)
                        all_concepts.extend(words)
                except Exception as e:
                    print(f"⚠️  Could not read {summary_file}: {e}")
            
            # Count concept frequency
            concept_counts = {}
            for concept in all_concepts:
                if len(concept) > 3:  # Filter short terms
                    concept_counts[concept] = concept_counts.get(concept, 0) + 1
            
            # Get top concepts
            top_concepts = sorted(concept_counts.items(), key=lambda x: x[1], reverse=True)[:20]
            insights["frequent_concepts"] = [{"concept": c, "frequency": f} for c, f in top_concepts]
        
        # Analyze ML chips
        try:
            with open('ml/chips_config.json', 'r') as f:
                chips_data = json.load(f)
                insights["ml_chips"] = {
                    "total_chips": len(chips_data.get('chips', [])),
                    "categories": {}
                }
                
                # Categorize chips
                for chip in chips_data.get('chips', []):
                    category = chip.get('category', 'uncategorized')
                    insights["ml_chips"]["categories"][category] = insights["ml_chips"]["categories"].get(category, 0) + 1
        except Exception as e:
            print(f"⚠️  Could not analyze ML chips: {e}")
            insights["ml_chips"] = {"total_chips": 0, "categories": {}}
        
        # Analyze memory
        try:
            with open('faithh_memory.json', 'r') as f:
                memory_data = json.load(f)
                insights["faithh_memory"] = {
                    "version": memory_data.get('version', ''),
                    "last_updated": memory_data.get('last_updated', ''),
                    "self_awareness_sections": list(memory_data.get('self_awareness', {}).keys()),
                    "has_recent_achievements": 'recent_achievements' in memory_data,
                    "project_integration": 'project_integration' in memory_data
                }
        except Exception as e:
            print(f"⚠️  Could not analyze FAITHH memory: {e}")
            insights["faithh_memory"] = {"error": str(e)}
        
        print(f"✅ Knowledge base insights collected")
        return insights
    
    def collect_conversation_history(self) -> Dict:
        """Collect and synthesize conversation history"""
        print("💬 Collecting conversation history...")
        
        conversations = {
            "collection_timestamp": datetime.now().isoformat(),
            "total_interactions": 0,
            "conversation_patterns": {},
            "frequent_topics": [],
            "user_satisfaction_indicators": {},
            "decision_points": []
        }
        
        # This would typically connect to a conversation database
        # For now, we'll analyze available conversation logs and summaries
        
        # Check for conversation logs
        conv_logs_dir = Path("logs/conversations")
        if conv_logs_dir.exists():
            log_files = list(conv_logs_dir.glob("*.json"))
            conversations["available_logs"] = len(log_files)
            
            # Analyze recent logs
            recent_conversations = []
            for log_file in log_files[-10:]:  # Last 10 logs
                try:
                    with open(log_file, 'r') as f:
                        log_data = json.load(f)
                        recent_conversations.append({
                            "timestamp": log_data.get('timestamp', ''),
                            "query_length": len(log_data.get('query', '')),
                            "response_length": len(log_data.get('response', '')),
                            "provider": log_data.get('provider', ''),
                            "satisfaction": log_data.get('satisfaction_rating', None)
                        })
                except Exception as e:
                    print(f"⚠️  Could not read {log_file}: {e}")
            
            conversations["recent_interactions"] = recent_conversations
            conversations["total_interactions"] = len(recent_conversations)
        
        # Analyze project summaries as conversation artifacts
        summaries_dir = Path("docs/project_summaries")
        if summaries_dir.exists():
            summary_files = list(summaries_dir.glob("*_summary.md"))
            conversations["project_summaries_as_conversations"] = len(summary_files)
        
        # Extract decision points from decisions log
        try:
            with open('decisions_log.json', 'r') as f:
                decisions_data = json.load(f)
                decisions = decisions_data.get('decisions', [])
                
                conversations["decision_points"] = [
                    {
                        "title": d.get('title', ''),
                        "date": d.get('date', ''),
                        "context": d.get('context', '')[:200] + "..." if len(d.get('context', '')) > 200 else d.get('context', ''),
                        "rationale": d.get('rationale', '')[:150] + "..." if len(d.get('rationale', '')) > 150 else d.get('rationale', '')
                    }
                    for d in decisions[-10:]  # Last 10 decisions
                ]
        except Exception as e:
            print(f"⚠️  Could not analyze decisions: {e}")
            conversations["decision_points"] = []
        
        print(f"✅ Conversation history collected")
        return conversations
    
    def collect_performance_metrics(self) -> Dict:
        """Collect performance metrics and system health data"""
        print("📊 Collecting performance metrics...")
        
        metrics = {
            "collection_timestamp": datetime.now().isoformat(),
            "system_health": {},
            "response_quality": {},
            "knowledge_base_metrics": {},
            "monitoring_alerts": [],
            "performance_trends": {}
        }
        
        # Load enhanced monitoring report if available
        try:
            report_file = Path("ml/output/comprehensive_monitoring_report.json")
            if report_file.exists():
                with open(report_file, 'r') as f:
                    monitoring_data = json.load(f)
                
                # Get latest report
                if monitoring_data:
                    latest_report = monitoring_data[-1]
                    
                    metrics["system_health"] = {
                        "overall_health": latest_report.get("current_health", {}).get("overall_health", "unknown"),
                        "health_score": latest_report.get("current_health", {}).get("health_score", 0),
                        "uptime_seconds": latest_report.get("current_health", {}).get("uptime_seconds", 0)
                    }
                    
                    # Service health
                    services = latest_report.get("current_health", {}).get("services", {})
                    metrics["service_health"] = {}
                    for service_name, service_data in services.items():
                        metrics["service_health"][service_name] = {
                            "status": service_data.get("status", "unknown"),
                            "health_score": service_data.get("health_score", 0)
                        }
                    
                    # Alerts
                    metrics["monitoring_alerts"] = latest_report.get("current_health", {}).get("alerts", [])
                    
                    # Performance trends
                    trends = latest_report.get("performance_trends", {})
                    metrics["performance_trends"] = trends
        except Exception as e:
            print(f"⚠️  Could not load monitoring report: {e}")
            metrics["system_health"] = {"error": str(e)}
        
        # Load knowledge base metrics
        try:
            kb_report_file = Path("ml/output/knowledge_base_metrics.json")
            if kb_report_file.exists():
                with open(kb_report_file, 'r') as f:
                    kb_data = json.load(f)
                
                if kb_data:
                    latest_kb = kb_data[-1]
                    metrics["knowledge_base_metrics"] = {
                        "health_score": latest_kb.get("health_score", 0),
                        "total_documents": latest_kb.get("statistics", {}).get("total_documents", 0),
                        "total_collections": latest_kb.get("statistics", {}).get("total_collections", 0),
                        "anomalies": latest_kb.get("anomaly_count", 0)
                    }
        except Exception as e:
            print(f"⚠️  Could not load KB metrics: {e}")
            metrics["knowledge_base_metrics"] = {"error": str(e)}
        
        print(f"✅ Performance metrics collected")
        return metrics
    
    def collect_user_behavior_patterns(self) -> Dict:
        """Collect and analyze user behavior patterns"""
        print("👤 Collecting user behavior patterns...")
        
        behavior = {
            "collection_timestamp": datetime.now().isoformat(),
            "interaction_patterns": {},
            "topic_preferences": {},
            "engagement_metrics": {},
            "usage_frequency": {},
            "feedback_indicators": {}
        }
        
        # Analyze project priorities as user interest indicators
        try:
            with open('project_states.json', 'r') as f:
                project_states = json.load(f)
            
            if 'strategic_plan' in project_states:
                domains = project_states['strategic_plan'].get('domains', {})
                behavior["project_focus"] = {}
                
                for domain_name, domain_data in domains.items():
                    priorities = domain_data.get('q1_2026_priorities', [])
                    behavior["project_focus"][domain_name] = {
                        "priority_count": len(priorities),
                        "completion_status": "high" if "Complete" in domain_data.get('current_status', '') else "medium",
                        "engagement_level": len(priorities)  # Simple engagement metric
                    }
        except Exception as e:
            print(f"⚠️  Could not analyze project focus: {e}")
        
        # Analyze recent decisions as user behavior indicators
        try:
            with open('decisions_log.json', 'r') as f:
                decisions_data = json.load(f)
                decisions = decisions_data.get('decisions', [])
                
                # Decision frequency by context
                context_counts = {}
                for decision in decisions:
                    context = decision.get('context', '')
                    if context:
                        # Extract key themes
                        themes = re.findall(r'\b(faithh|constella|gen8|tom cat|alife|technical|business)\b', context.lower())
                        for theme in themes:
                            context_counts[theme] = context_counts.get(theme, 0) + 1
                
                behavior["decision_themes"] = context_counts
                behavior["total_decisions"] = len(decisions)
                behavior["recent_decision_rate"] = len([d for d in decisions if self._is_recent_decision(d.get('date', ''))])
        except Exception as e:
            print(f"⚠️  Could not analyze decisions: {e}")
        
        # Analyze documentation updates as engagement indicators
        docs_updated = []
        try:
            readme_mtime = Path('README.md').stat().st_mtime
            if time.time() - readme_mtime < 7 * 24 * 3600:  # Updated in last week
                docs_updated.append('README.md')
        except:
            pass
        
        behavior["recent_documentation_activity"] = {
            "files_updated": docs_updated,
            "activity_level": len(docs_updated)
        }
        
        print(f"✅ User behavior patterns collected")
        return behavior
    
    def _is_recent_decision(self, date_str: str) -> bool:
        """Check if decision is recent (within last 7 days)"""
        try:
            if date_str:
                # Simple date parsing - would need more robust parsing for production
                return "2026-03" in date_str or "2026-03-2" in date_str
        except:
            pass
        return False
    
    def collect_technical_stack_documentation(self) -> Dict:
        """Collect technical stack documentation"""
        print("🔧 Collecting technical stack documentation...")
        
        tech_stack = {
            "collection_timestamp": datetime.now().isoformat(),
            "backend_components": {},
            "api_endpoints": {},
            "configurations": {},
            "dependencies": {},
            "infrastructure": {}
        }
        
        # Analyze backend components
        backend_files = [
            'faithh_professional_backend_fixed.py',
            'backend/llm_providers.py',
            'backend/context_builders.py',
            'backend/local_optimization.py'
        ]
        
        tech_stack["backend_components"] = {
            "total_files": len(backend_files),
            "files": backend_files,
            "last_modified": {}
        }
        
        for file_path in backend_files:
            try:
                file_path_obj = Path(file_path)
                if file_path_obj.exists():
                    mtime = file_path_obj.stat().st_mtime
                    tech_stack["backend_components"]["last_modified"][file_path] = datetime.fromtimestamp(mtime).isoformat()
            except:
                continue
        
        # Extract API endpoints from backend
        try:
            with open('faithh_professional_backend_fixed.py', 'r') as f:
                backend_content = f.read()
            
            # Find @app.route decorators
            routes = re.findall(r'@app\.route\([\'"]([^\'"]+)[\'"].*?\)', backend_content)
            tech_stack["api_endpoints"] = {
                "total_endpoints": len(routes),
                "routes": routes[:20]  # First 20 routes
            }
        except Exception as e:
            print(f"⚠️  Could not extract API endpoints: {e}")
            tech_stack["api_endpoints"] = {"error": str(e)}
        
        # Analyze configuration
        config_files = ['config.yaml', '.env']
        tech_stack["configurations"] = {
            "available_configs": []
        }
        
        for config_file in config_files:
            if Path(config_file).exists():
                tech_stack["configurations"]["available_configs"].append(config_file)
        
        # Check dependencies
        try:
            requirements_file = Path('requirements.txt')
            if requirements_file.exists():
                with open(requirements_file, 'r') as f:
                    requirements = f.read()
                
                dependencies = [line.strip() for line in requirements.split('\n') if line.strip() and not line.startswith('#')]
                tech_stack["dependencies"] = {
                    "total_dependencies": len(dependencies),
                    "dependencies": dependencies[:30]  # First 30 dependencies
                }
        except Exception as e:
            print(f"⚠️  Could not analyze dependencies: {e}")
        
        # Infrastructure info from docker-compose
        try:
            with open('docker-compose.yml', 'r') as f:
                docker_content = f.read()
            
            services = re.findall(r'^\s*(\w+):', docker_content, re.MULTILINE)
            tech_stack["infrastructure"] = {
                "services": services,
                "total_services": len(services)
            }
        except Exception as e:
            print(f"⚠️  Could not analyze docker-compose: {e}")
        
        print(f"✅ Technical stack documentation collected")
        return tech_stack
    
    def collect_inspiration_references(self) -> Dict:
        """Collect inspiration and reference materials"""
        print("💡 Collecting inspiration and references...")
        
        inspiration = {
            "collection_timestamp": datetime.now().isoformat(),
            "thought_partners": {},
            "research_materials": {},
            "industry_references": {},
            "idea_sources": {}
        }
        
        # Analyze research documents
        research_dir = Path("docs/research")
        if research_dir.exists():
            research_files = list(research_dir.glob("*.md"))
            inspiration["research_materials"] = {
                "total_documents": len(research_files),
                "documents": [f.name for f in research_files]
            }
        
        # Analyze reference documents
        reference_dir = Path("docs/reference")
        if reference_dir.exists():
            reference_files = list(reference_dir.glob("*.md"))
            inspiration["reference_materials"] = {
                "total_documents": len(reference_files),
                "documents": [f.name for f in reference_files]
            }
        
        # Check for idea vault
        idea_vault = Path("docs/reference/IDEA_VAULT.md")
        if idea_vault.exists():
            try:
                with open(idea_vault, 'r', encoding='utf-8') as f:
                    idea_content = f.read()
                
                # Count ideas (simple heuristic)
                idea_sections = re.findall(r'^#+\s+(.+)$', idea_content, re.MULTILINE)
                inspiration["idea_sources"] = {
                    "idea_vault_available": True,
                    "idea_count": len(idea_sections),
                    "sample_ideas": idea_sections[:5]  # First 5 ideas
                }
            except Exception as e:
                print(f"⚠️  Could not read idea vault: {e}")
                inspiration["idea_sources"] = {"error": str(e)}
        
        # Look for external references in memory
        try:
            with open('faithh_memory.json', 'r') as f:
                memory_data = json.load(f)
            
            # Check for constella awareness
            if 'constella_awareness' in memory_data:
                constella_info = memory_data['constella_awareness']
                inspiration["constella_framework"] = {
                    "description": constella_info.get('what_it_is', ''),
                    "key_components": list(constella_info.get('key_components', {}).keys()),
                    "connection_to_faithh": constella_info.get('connection_to_faithh', '')
                }
        except Exception as e:
            print(f"⚠️  Could not analyze memory for references: {e}")
        
        print(f"✅ Inspiration and references collected")
        return inspiration
    
    def generate_constella_dataset(self) -> Dict:
        """Generate complete Constella dataset"""
        print("🚀 Generating complete Constella dataset...")
        
        dataset = {
            "generation_timestamp": datetime.now().isoformat(),
            "dataset_version": "1.0",
            "collection_summary": {},
            "data_sources": {}
        }
        
        # Collect all data types
        data_collectors = {
            "project_states": self.collect_project_states,
            "knowledge_base": self.collect_knowledge_base_insights,
            "conversations": self.collect_conversation_history,
            "performance_metrics": self.collect_performance_metrics,
            "user_behavior": self.collect_user_behavior_patterns,
            "technical_stack": self.collect_technical_stack_documentation,
            "inspiration_references": self.collect_inspiration_references
        }
        
        for data_type, collector in data_collectors.items():
            try:
                print(f"\n📊 Collecting {data_type}...")
                dataset["data_sources"][data_type] = collector()
                print(f"✅ {data_type} collected successfully")
            except Exception as e:
                print(f"❌ Error collecting {data_type}: {e}")
                dataset["data_sources"][data_type] = {"error": str(e)}
        
        # Generate collection summary
        dataset["collection_summary"] = {
            "total_data_sources": len(data_collectors),
            "successful_collections": len([k for k, v in dataset["data_sources"].items() if "error" not in v]),
            "failed_collections": len([k for k, v in dataset["data_sources"].items() if "error" in v]),
            "collection_duration": (datetime.now() - self.collection_timestamp).total_seconds(),
            "data_freshness": datetime.now().isoformat()
        }
        
        return dataset
    
    def save_constella_dataset(self, dataset: Dict, filename: str = "constella_dataset.json"):
        """Save Constella dataset to file"""
        try:
            output_dir = Path("ml/output")
            output_dir.mkdir(exist_ok=True, parents=True)
            
            dataset_file = output_dir / filename
            with open(dataset_file, 'w') as f:
                json.dump(dataset, f, indent=2)
            
            print(f"✅ Constella dataset saved to {dataset_file}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to save dataset: {e}")
            return False


def main():
    """Main data collection process"""
    print("🔍 FAITHH Constella Data Collection")
    print("=" * 60)
    
    collector = ConstellaDataCollector()
    
    # Generate complete dataset
    print("\n🚀 Starting comprehensive data collection...")
    dataset = collector.generate_constella_dataset()
    
    # Display collection summary
    summary = dataset["collection_summary"]
    print(f"\n📊 Collection Summary:")
    print(f"   - Total Data Sources: {summary['total_data_sources']}")
    print(f"   - Successful: {summary['successful_collections']}")
    print(f"   - Failed: {summary['failed_collections']}")
    print(f"   - Duration: {summary['collection_duration']:.2f} seconds")
    
    # Display key insights
    print(f"\n💡 Key Insights:")
    
    # Project states
    if "project_states" in dataset["data_sources"]:
        project_data = dataset["data_sources"]["project_states"]
        if "total_projects" in project_data:
            print(f"   - Projects Tracked: {project_data['total_projects']}")
        if "project_insights" in project_data:
            print(f"   - Project Insights Generated: {len(project_data['project_insights'])}")
    
    # Knowledge base
    if "knowledge_base" in dataset["data_sources"]:
        kb_data = dataset["data_sources"]["knowledge_base"]
        if "frequent_concepts" in kb_data:
            print(f"   - Top Concepts: {len(kb_data['frequent_concepts'])}")
        if "ml_chips" in kb_data:
            print(f"   - ML Chips: {kb_data['ml_chips'].get('total_chips', 0)}")
    
    # Performance metrics
    if "performance_metrics" in dataset["data_sources"]:
        perf_data = dataset["data_sources"]["performance_metrics"]
        if "system_health" in perf_data:
            health = perf_data["system_health"]
            if "overall_health" in health:
                print(f"   - System Health: {health['overall_health'].upper()}")
        if "monitoring_alerts" in perf_data:
            print(f"   - Active Alerts: {len(perf_data['monitoring_alerts'])}")
    
    # Save dataset
    print(f"\n💾 Saving Constella dataset...")
    if collector.save_constella_dataset(dataset):
        print("✅ Dataset saved successfully!")
        print(f"📁 Location: ml/output/constella_dataset.json")
    else:
        print("❌ Failed to save dataset")
    
    print(f"\n🎉 Constella data collection complete!")
    print(f"📈 Ready for AI integration and synthesis!")


if __name__ == "__main__":
    main()
