#!/usr/bin/env python3
"""
FAITHH Constella AI Integration
=============================
Integrates Constella data collection to enhance FAITHH's AI responses.

This module provides:
- Context-aware response enhancement
- Project state integration
- Decision-based recommendations
- Knowledge synthesis from collected data
- Proactive assistance based on patterns
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

class ConstellaAIIntegration:
    """AI integration layer for Constella framework"""
    
    def __init__(self):
        self.constella_data = None
        self.last_data_refresh = None
        self.context_cache = {}
        
    def load_constella_data(self, force_refresh: bool = False) -> bool:
        """Load Constella dataset for AI integration"""
        try:
            dataset_file = Path("ml/output/constella_dataset.json")
            
            if not dataset_file.exists():
                print("⚠️  Constella dataset not found - run data collection first")
                return False
            
            # Check if data is fresh (less than 1 hour old)
            if not force_refresh and self.last_data_refresh:
                if (datetime.now() - self.last_data_refresh).total_seconds() < 3600:
                    return True  # Data is still fresh
            
            with open(dataset_file, 'r') as f:
                self.constella_data = json.load(f)
            
            self.last_data_refresh = datetime.now()
            print("✅ Constella data loaded for AI integration")
            return True
            
        except Exception as e:
            print(f"❌ Failed to load Constella data: {e}")
            return False
    
    def enhance_query_context(self, query: str, current_context: Dict = None) -> Dict:
        """Enhance query context with Constella data"""
        if not self.constella_data:
            if not self.load_constella_data():
                return current_context or {}
        
        enhanced_context = current_context.copy() if current_context else {}
        
        # Add project state awareness
        project_context = self._get_project_context_for_query(query)
        if project_context:
            enhanced_context["project_awareness"] = project_context
        
        # Add recent decisions context
        decisions_context = self._get_decisions_context_for_query(query)
        if decisions_context:
            enhanced_context["recent_decisions"] = decisions_context
        
        # Add knowledge base context
        kb_context = self._get_knowledge_base_context_for_query(query)
        if kb_context:
            enhanced_context["knowledge_context"] = kb_context
        
        # Add user behavior patterns
        behavior_context = self._get_behavior_context_for_query(query)
        if behavior_context:
            enhanced_context["behavior_insights"] = behavior_context
        
        # Add performance context
        perf_context = self._get_performance_context()
        if perf_context:
            enhanced_context["system_performance"] = perf_context
        
        return enhanced_context
    
    def _get_project_context_for_query(self, query: str) -> Dict:
        """Get relevant project context for query"""
        if not self.constella_data or "project_states" not in self.constella_data["data_sources"]:
            return {}
        
        project_data = self.constella_data["data_sources"]["project_states"]
        query_lower = query.lower()
        
        context = {
            "active_projects": project_data.get("active_projects", {}),
            "strategic_overview": project_data.get("strategic_overview", {}),
            "recent_decisions": project_data.get("recent_decisions", {}),
            "relevant_projects": []
        }
        
        # Identify relevant projects based on query keywords
        keyword_matches = {
            "faithh": ["technical", "backend", "ai", "optimization"],
            "constella": ["civic", "governance", "framework", "harmony"],
            "tom cat": ["business", "music", "llc", "revenue"],
            "gen8": ["server", "homelab", "infrastructure", "hardware"],
            "alife": ["research", "experiment", "evolution", "cultural"]
        }
        
        for keyword, related_terms in keyword_matches.items():
            if keyword in query_lower or any(term in query_lower for term in related_terms):
                for project_name, project_info in context["active_projects"].items():
                    if keyword.lower() in project_name.lower():
                        context["relevant_projects"].append({
                            "name": project_name,
                            "status": project_info.get("status", ""),
                            "priorities": project_info.get("priorities", []),
                            "next_steps": self._extract_next_steps(project_info)
                        })
        
        return context
    
    def _get_decisions_context_for_query(self, query: str) -> Dict:
        """Get relevant decisions context for query"""
        if not self.constella_data or "conversations" not in self.constella_data["data_sources"]:
            return {}
        
        conv_data = self.constella_data["data_sources"]["conversations"]
        query_lower = query.lower()
        
        context = {
            "recent_decisions": conv_data.get("decision_points", [])[:5],
            "decision_themes": {},
            "relevant_decisions": []
        }
        
        # Find decisions relevant to query
        for decision in context["recent_decisions"]:
            decision_context = decision.get("context", "").lower()
            decision_rationale = decision.get("rationale", "").lower()
            
            # Check relevance
            if (any(word in decision_context for word in query_lower.split()) or
                any(word in decision_rationale for word in query_lower.split())):
                context["relevant_decisions"].append(decision)
        
        return context
    
    def _get_knowledge_base_context_for_query(self, query: str) -> Dict:
        """Get relevant knowledge base context for query"""
        if not self.constella_data or "knowledge_base" not in self.constella_data["data_sources"]:
            return {}
        
        kb_data = self.constella_data["data_sources"]["knowledge_base"]
        query_lower = query.lower()
        
        context = {
            "frequent_concepts": kb_data.get("frequent_concepts", [])[:10],
            "project_summaries": kb_data.get("project_summaries", {}),
            "ml_chips": kb_data.get("ml_chips", {}),
            "relevant_concepts": []
        }
        
        # Find concepts relevant to query
        for concept_info in context["frequent_concepts"]:
            concept = concept_info.get("concept", "").lower()
            if concept and concept in query_lower:
                context["relevant_concepts"].append(concept_info)
        
        return context
    
    def _get_behavior_context_for_query(self, query: str) -> Dict:
        """Get user behavior context for query"""
        if not self.constella_data or "user_behavior" not in self.constella_data["data_sources"]:
            return {}
        
        behavior_data = self.constella_data["data_sources"]["user_behavior"]
        
        context = {
            "project_focus": behavior_data.get("project_focus", {}),
            "decision_themes": behavior_data.get("decision_themes", {}),
            "engagement_level": behavior_data.get("recent_documentation_activity", {}).get("activity_level", 0)
        }
        
        return context
    
    def _get_performance_context(self) -> Dict:
        """Get current system performance context"""
        if not self.constella_data or "performance_metrics" not in self.constella_data["data_sources"]:
            return {}
        
        perf_data = self.constella_data["data_sources"]["performance_metrics"]
        
        context = {
            "system_health": perf_data.get("system_health", {}),
            "service_health": perf_data.get("service_health", {}),
            "monitoring_alerts": perf_data.get("monitoring_alerts", []),
            "health_status": "unknown"
        }
        
        # Determine overall health status
        system_health = context["system_health"]
        if "overall_health" in system_health:
            context["health_status"] = system_health["overall_health"]
        
        return context
    
    def _extract_next_steps(self, project_info: Dict) -> List[str]:
        """Extract next steps from project info"""
        priorities = project_info.get("priorities", [])
        
        # Filter for incomplete items
        next_steps = []
        for priority in priorities:
            if not priority.startswith("✅"):  # Not completed
                next_steps.append(priority)
        
        return next_steps[:3]  # Return top 3 next steps
    
    def generate_intelligent_response_guidance(self, query: str, enhanced_context: Dict) -> Dict:
        """Generate intelligent response guidance based on Constella data"""
        guidance = {
            "response_strategy": "standard",
            "context_sources": [],
            "suggested_content": [],
            "tone_recommendations": [],
            "proactive_suggestions": []
        }
        
        # Analyze query intent
        query_lower = query.lower()
        
        # Project-related queries
        if any(word in query_lower for word in ["project", "status", "progress", "next steps"]):
            guidance["response_strategy"] = "project_aware"
            
            if "project_awareness" in enhanced_context:
                projects = enhanced_context["project_awareness"].get("relevant_projects", [])
                if projects:
                    guidance["suggested_content"].append(f"Reference current project states for: {', '.join([p['name'] for p in projects])}")
                    guidance["context_sources"].append("project_states.json")
        
        # Decision-related queries
        if any(word in query_lower for word in ["decision", "why", "choose", "rationale"]):
            guidance["response_strategy"] = "decision_aware"
            
            if "recent_decisions" in enhanced_context:
                decisions = enhanced_context["recent_decisions"].get("relevant_decisions", [])
                if decisions:
                    guidance["suggested_content"].append("Reference recent decisions and their rationale")
                    guidance["context_sources"].append("decisions_log.json")
        
        # System health queries
        if any(word in query_lower for word in ["health", "status", "monitoring", "performance"]):
            guidance["response_strategy"] = "system_aware"
            
            if "system_performance" in enhanced_context:
                health_status = enhanced_context["system_performance"].get("health_status", "unknown")
                guidance["suggested_content"].append(f"Include current system health status: {health_status}")
                guidance["context_sources"].append("monitoring_system")
        
        # Constella framework queries
        if "constella" in query_lower:
            guidance["response_strategy"] = "constella_aware"
            guidance["suggested_content"].append("Reference Constella framework documentation and current integration status")
            guidance["context_sources"].append("constella_awareness")
        
        # Add proactive suggestions based on patterns
        if "project_focus" in enhanced_context.get("behavior_insights", {}):
            focus_areas = enhanced_context["behavior_insights"]["project_focus"]
            high_engagement = [name for name, data in focus_areas.items() if data.get("engagement_level", 0) > 2]
            
            if high_engagement:
                guidance["proactive_suggestions"].append(f"User is highly engaged with: {', '.join(high_engagement)}")
        
        # Add tone recommendations
        if guidance["response_strategy"] != "standard":
            guidance["tone_recommendations"].append("Use confident, knowledgeable tone")
            guidance["tone_recommendations"].append("Provide specific, actionable recommendations")
            guidance["tone_recommendations"].append("Cite sources and context")
        
        return guidance
    
    def enhance_response_with_constella_data(self, query: str, base_response: str) -> str:
        """Enhance a base response with Constella data insights"""
        if not self.load_constella_data():
            return base_response
        
        # Get enhanced context
        enhanced_context = self.enhance_query_context(query)
        
        # Generate response guidance
        guidance = self.generate_intelligent_response_guidance(query, enhanced_context)
        
        # Build enhanced response
        enhanced_sections = []
        
        # Add context header if relevant
        if guidance["response_strategy"] != "standard":
            strategy_headers = {
                "project_aware": "=== PROJECT CONTEXT ===",
                "decision_aware": "=== RECENT DECISIONS ===", 
                "system_aware": "=== SYSTEM STATUS ===",
                "constella_aware": "=== CONSTELLA FRAMEWORK ==="
            }
            
            header = strategy_headers.get(guidance["response_strategy"], "=== ENHANCED CONTEXT ===")
            enhanced_sections.append(header)
        
        # Add project insights
        if "project_awareness" in enhanced_context:
            project_ctx = enhanced_context["project_awareness"]
            if project_ctx.get("relevant_projects"):
                enhanced_sections.append("\n**Current Project States:**")
                for project in project_ctx["relevant_projects"][:2]:  # Top 2 projects
                    status = project.get("status", "Unknown")
                    next_steps = project.get("next_steps", [])
                    enhanced_sections.append(f"- {project['name']}: {status}")
                    if next_steps:
                        enhanced_sections.append(f"  Next steps: {', '.join(next_steps[:2])}")
        
        # Add recent decisions
        if "recent_decisions" in enhanced_context:
            decisions = enhanced_context["recent_decisions"].get("relevant_decisions", [])
            if decisions:
                enhanced_sections.append("\n**Recent Decisions:**")
                for decision in decisions[:2]:  # Top 2 decisions
                    title = decision.get("title", "Untitled")
                    date = decision.get("date", "Unknown date")
                    enhanced_sections.append(f"- {title} ({date})")
        
        # Add system health
        if "system_performance" in enhanced_context:
            perf = enhanced_context["system_performance"]
            health_status = perf.get("health_status", "unknown")
            if health_status != "unknown":
                enhanced_sections.append(f"\n**System Health:** {health_status.upper()}")
                
                alerts = perf.get("monitoring_alerts", [])
                if alerts:
                    enhanced_sections.append(f"Active alerts: {len(alerts)}")
        
        # Combine enhanced response
        if enhanced_sections:
            enhanced_prefix = "\n".join(enhanced_sections) + "\n\n"
            return enhanced_prefix + base_response
        else:
            return base_response
    
    def get_constella_summary_for_response(self) -> str:
        """Get a Constella summary that can be included in responses"""
        if not self.load_constella_data():
            return "Constella data not available"
        
        summary_parts = []
        
        # Project overview
        if "project_states" in self.constella_data["data_sources"]:
            project_data = self.constella_data["data_sources"]["project_states"]
            total_projects = project_data.get("total_projects", 0)
            if total_projects > 0:
                summary_parts.append(f"Tracking {total_projects} active projects")
        
        # Knowledge base overview
        if "knowledge_base" in self.constella_data["data_sources"]:
            kb_data = self.constella_data["data_sources"]["knowledge_base"]
            concepts = len(kb_data.get("frequent_concepts", []))
            if concepts > 0:
                summary_parts.append(f"Knowledge base with {concepts} key concepts")
        
        # System health
        if "performance_metrics" in self.constella_data["data_sources"]:
            perf_data = self.constella_data["data_sources"]["performance_metrics"]
            system_health = perf_data.get("system_health", {})
            if "overall_health" in system_health:
                summary_parts.append(f"System health: {system_health['overall_health']}")
        
        # Recent activity
        if "user_behavior" in self.constella_data["data_sources"]:
            behavior_data = self.constella_data["data_sources"]["user_behavior"]
            total_decisions = behavior_data.get("total_decisions", 0)
            if total_decisions > 0:
                summary_parts.append(f"Recent decisions: {total_decisions}")
        
        if summary_parts:
            return "Constella AI Integration: " + " | ".join(summary_parts)
        else:
            return "Constella framework operational"


# Global integration instance
constella_integration = ConstellaAIIntegration()


def enhance_faithh_context(query: str, current_context: Dict = None) -> Dict:
    """Public function to enhance FAITHH context with Constella data"""
    return constella_integration.enhance_query_context(query, current_context)


def enhance_faithh_response(query: str, base_response: str) -> str:
    """Public function to enhance FAITHH response with Constella data"""
    return constella_integration.enhance_response_with_constella_data(query, base_response)


def get_constella_status() -> str:
    """Public function to get Constella integration status"""
    return constella_integration.get_constella_summary_for_response()


def refresh_constella_data() -> bool:
    """Public function to refresh Constella data"""
    return constella_integration.load_constella_data(force_refresh=True)


if __name__ == "__main__":
    # Test the integration
    print("🧠 Testing FAITHH Constella AI Integration")
    print("=" * 50)
    
    # Load data
    if refresh_constella_data():
        print("✅ Constella data loaded successfully")
        
        # Test query enhancement
        test_query = "What's the current status of our projects?"
        enhanced_context = enhance_faithh_context(test_query)
        
        print(f"\n📝 Test Query: {test_query}")
        print(f"🔍 Enhanced Context Keys: {list(enhanced_context.keys())}")
        
        # Test response enhancement
        base_response = "I can help you understand the current project status."
        enhanced_response = enhance_faithh_response(test_query, base_response)
        
        print(f"\n💬 Enhanced Response:")
        print(enhanced_response)
        
        # Get status
        print(f"\n📊 Constella Status: {get_constella_status()}")
        
        print(f"\n🎉 Integration test complete!")
    else:
        print("❌ Failed to load Constella data")
