"""
Alife Data Processing Service
Integrates Alife experimental data with chat functionality
"""

import json
import time
import os
from typing import Dict, List, Any, Optional
from pathlib import Path

class AlifeService:
    """Service for processing and analyzing Alife experimental data"""
    
    def __init__(self):
        self.data_dir = Path("/home/jonat/ai-stack/ml/training_data")
        self.cache = {}
        self._load_alife_data()
    
    def _load_alife_data(self):
        """Load Alife training data"""
        try:
            # Load training data
            train_file = self.data_dir / "alife_train_20260326_154506.json"
            if train_file.exists():
                with open(train_file, 'r') as f:
                    self.cache['training_data'] = json.load(f)
                print(f"✅ Loaded {len(self.cache['training_data'])} Alife training examples")
            
            # Load metadata
            metadata_file = self.data_dir / "alife_metadata_20260326_150710.json"
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    self.cache['metadata'] = json.load(f)
                print(f"✅ Loaded Alife metadata")
            
        except Exception as e:
            print(f"❌ Failed to load Alife data: {e}")
            self.cache = {'training_data': [], 'metadata': {}}
    
    def get_alife_summary(self) -> Dict[str, Any]:
        """Get summary of Alife data"""
        metadata = self.cache.get('metadata', {})
        training_data = self.cache.get('training_data', [])
        
        return {
            "total_examples": len(training_data),
            "metadata": metadata,
            "domains": self._get_domains(training_data),
            "experiment_types": self._get_experiment_types(training_data),
            "recent_events": self._get_recent_events(training_data, 5)
        }
    
    def _get_domains(self, training_data: List[Dict]) -> Dict[str, int]:
        """Get domain distribution"""
        domains = {}
        for item in training_data:
            domain = item.get('domain', 'unknown')
            domains[domain] = domains.get(domain, 0) + 1
        return domains
    
    def _get_experiment_types(self, training_data: List[Dict]) -> Dict[str, int]:
        """Get experiment type distribution"""
        experiments = {}
        for item in training_data:
            exp_type = item.get('query_type', 'unknown')
            experiments[exp_type] = experiments.get(exp_type, 0) + 1
        return experiments
    
    def _get_recent_events(self, training_data: List[Dict], limit: int = 5) -> List[Dict]:
        """Get recent Alife events"""
        # Sort by tick if available
        sorted_data = sorted(
            training_data, 
            key=lambda x: x.get('metadata', {}).get('tick', 0), 
            reverse=True
        )
        return sorted_data[:limit]
    
    def analyze_alife_event(self, event_data: Dict[str, Any]) -> str:
        """Analyze Alife event and return insights"""
        try:
            content = event_data.get('content', '')
            domain = event_data.get('domain', 'unknown')
            metadata = event_data.get('metadata', {})
            
            # Create analysis prompt
            analysis_prompt = f"""
Analyze this Alife experimental event:

Domain: {domain}
Event Type: {event_data.get('query_type', 'unknown')}
Content: {content}

Metadata:
- Agent ID: {metadata.get('agent_id', 'N/A')}
- Tick: {metadata.get('tick', 'N/A')}
- Generation: {metadata.get('generation', 'N/A')}
- Energy: {metadata.get('agent_energy', 'N/A')}
- Environment Energy: {metadata.get('env_energy', 'N/A')}
- Genome: {metadata.get('genome_readable', 'N/A')}

Please provide insights about:
1. What this event indicates about the agent's behavior
2. Any patterns or anomalies in the data
3. Evolutionary or cognitive implications
4. Energy efficiency observations
5. Recommendations for further analysis
"""
            
            return analysis_prompt
            
        except Exception as e:
            return f"Error analyzing Alife event: {e}"
    
    def get_alife_insights(self, domain: Optional[str] = None) -> str:
        """Get insights about Alife experiments"""
        training_data = self.cache.get('training_data', [])
        
        # Filter by domain if specified
        if domain:
            training_data = [item for item in training_data if item.get('domain') == domain]
        
        if not training_data:
            return f"No Alife data available for domain: {domain}"
        
        # Get recent events for analysis
        recent_events = self._get_recent_events(training_data, 3)
        
        insights = []
        for event in recent_events:
            insight = self.analyze_alife_event(event)
            insights.append(f"Event {event.get('metadata', {}).get('tick', 'N/A')}: {insight}")
        
        return "\n\n".join(insights)
    
    def create_alife_query(self, query_type: str = "analysis") -> Dict[str, Any]:
        """Create a query for Alife data analysis"""
        training_data = self.cache.get('training_data', [])
        
        if query_type == "summary":
            return {
                "query_type": "alife_summary",
                "content": f"Provide a comprehensive summary of {len(training_data)} Alife experimental events, including domain distribution, evolutionary patterns, and key insights.",
                "context": self.get_alife_summary()
            }
        
        elif query_type == "energy_analysis":
            energy_events = [
                item for item in training_data 
                if item.get('features', {}).get('has_energy', False)
            ]
            
            return {
                "query_type": "alife_energy_analysis",
                "content": f"Analyze energy patterns from {len(energy_events)} Alife events. Focus on energy efficiency, environmental interactions, and survival strategies.",
                "context": {
                    "total_energy_events": len(energy_events),
                    "recent_events": self._get_recent_events(energy_events, 5)
                }
            }
        
        elif query_type == "cognitive_analysis":
            cognitive_events = [
                item for item in training_data 
                if item.get('features', {}).get('has_cognitive', False)
            ]
            
            return {
                "query_type": "alife_cognitive_analysis",
                "content": f"Analyze cognitive development patterns from {len(cognitive_events)} Alife events. Focus on memory, learning, and behavioral complexity.",
                "context": {
                    "total_cognitive_events": len(cognitive_events),
                    "recent_events": self._get_recent_events(cognitive_events, 5)
                }
            }
        
        elif query_type == "evolutionary_analysis":
            return {
                "query_type": "alife_evolutionary_analysis",
                "content": "Analyze evolutionary dynamics and patterns in the Alife experiments. Focus on trait development, population dynamics, and adaptation strategies.",
                "context": self.get_alife_summary()
            }
        
        else:
            return {
                "query_type": "alife_general",
                "content": f"Provide insights about the Alife experimental data, covering {len(training_data)} events across multiple domains and experiment types.",
                "context": self.get_alife_summary()
            }
    
    def process_alife_data_with_chat(self, query_type: str = "analysis") -> str:
        """Process Alife data through chat endpoint"""
        try:
            # Create Alife query
            alife_query = self.create_alife_query(query_type)
            
            # Format as chat message
            chat_message = f"""
I need you to analyze Alife experimental data. Here's the query:

{alife_query['content']}

Context: {json.dumps(alife_query.get('context', {}), indent=2)}

Please provide a comprehensive analysis with actionable insights about the Alife experiments.
"""
            
            return chat_message
            
        except Exception as e:
            return f"Error processing Alife data: {e}"
    
    def get_available_domains(self) -> List[str]:
        """Get available Alife domains"""
        training_data = self.cache.get('training_data', [])
        domains = set()
        for item in training_data:
            domains.add(item.get('domain', 'unknown'))
        return sorted(list(domains))
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get Alife data statistics"""
        training_data = self.cache.get('training_data', [])
        
        if not training_data:
            return {"error": "No Alife data available"}
        
        # Calculate statistics
        stats = {
            "total_events": len(training_data),
            "domains": self._get_domains(training_data),
            "experiment_types": self._get_experiment_types(training_data),
            "feature_coverage": {
                "has_numbers": sum(1 for item in training_data if item.get('features', {}).get('has_numbers', False)),
                "has_cognitive": sum(1 for item in training_data if item.get('features', {}).get('has_cognitive', False)),
                "has_energy": sum(1 for item in training_data if item.get('features', {}).get('has_energy', False)),
                "has_population": sum(1 for item in training_data if item.get('features', {}).get('has_population', False))
            }
        }
        
        # Add tick range
        ticks = [item.get('metadata', {}).get('tick', 0) for item in training_data]
        if ticks:
            stats["tick_range"] = {"min": min(ticks), "max": max(ticks)}
        
        return stats