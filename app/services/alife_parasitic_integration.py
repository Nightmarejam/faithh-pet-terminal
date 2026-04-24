"""
Alife Parasitic Integration Service
Phase 3B: Connect parasitic feeding to existing Alife data
"""

import math
import time
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

@dataclass
class ParasiticSignature:
    """Parasitic signature for Alife events"""
    parasitic_efficiency: float
    moon_damping_correlation: float
    impedance_gradient: float
    cognitive_complexity: float
    fusion_potential: float
    earth_mars_analog: str  # "earth_like" or "mars_like"

class AlifeParasiticIntegration:
    """Service for integrating parasitic feeding with existing Alife data"""
    
    def __init__(self, alife_service, parasitic_alife_service):
        self.alife_service = alife_service
        self.parasitic_service = parasitic_alife_service
        self.alife_data = []
        self.parasitic_signatures = {}
        self.domain_analysis = {}
        self.earth_mars_validation = {}
        
    def load_alife_data(self) -> Dict[str, Any]:
        """Load existing 92 Alife events"""
        try:
            # Get Alife summary to understand data structure
            alife_summary = self.alife_service.get_alife_summary()
            
            # Load training data
            training_data = self.alife_service.cache.get('training_data', [])
            
            self.alife_data = training_data
            
            return {
                "success": True,
                "total_events": len(self.alife_data),
                "data_structure": self._analyze_data_structure(),
                "timestamp": time.time()
            }
            
        except Exception as e:
            return {"error": f"Failed to load Alife data: {e}"}
    
    def _analyze_data_structure(self) -> Dict[str, Any]:
        """Analyze the structure of Alife data"""
        if not self.alife_data:
            return {"error": "No Alife data loaded"}
        
        sample_event = self.alife_data[0] if self.alife_data else {}
        
        structure = {
            "sample_keys": list(sample_event.keys()),
            "sample_event": sample_event,
            "data_types": {key: type(value).__name__ for key, value in sample_event.items()},
            "total_events": len(self.alife_data)
        }
        
        # Identify domains
        domains = set()
        for event in self.alife_data:
            if 'domain' in event:
                domains.add(event['domain'])
            elif 'type' in event:
                domains.add(event['type'])
        
        structure["identified_domains"] = list(domains)
        
        return structure
    
    def calculate_parasitic_signature(self, event: Dict[str, Any]) -> ParasiticSignature:
        """Calculate parasitic signature for an Alife event"""
        try:
            # Extract relevant features from event
            event_type = event.get('domain', event.get('type', 'unknown'))
            event_data = event.get('data', {})
            
            # Calculate parasitic efficiency based on event characteristics
            parasitic_efficiency = self._calculate_parasitic_efficiency(event)
            
            # Calculate Moon damping correlation
            moon_damping_correlation = self._calculate_moon_correlation(event)
            
            # Estimate impedance gradient from event complexity
            impedance_gradient = self._estimate_impedance_gradient(event)
            
            # Calculate cognitive complexity
            cognitive_complexity = self._calculate_cognitive_complexity(event)
            
            # Calculate fusion potential
            fusion_potential = self._calculate_fusion_potential(event)
            
            # Determine Earth vs Mars analog
            earth_mars_analog = self._determine_earth_mars_analog(event)
            
            return ParasiticSignature(
                parasitic_efficiency=parasitic_efficiency,
                moon_damping_correlation=moon_damping_correlation,
                impedance_gradient=impedance_gradient,
                cognitive_complexity=cognitive_complexity,
                fusion_potential=fusion_potential,
                earth_mars_analog=earth_mars_analog
            )
            
        except Exception as e:
            # Return default signature if calculation fails
            return ParasiticSignature(
                parasitic_efficiency=0.1,
                moon_damping_correlation=0.0,
                impedance_gradient=1.0,
                cognitive_complexity=0.3,
                fusion_potential=0.1,
                earth_mars_analog="mars_like"
            )
    
    def _calculate_parasitic_efficiency(self, event: Dict[str, Any]) -> float:
        """Calculate parasitic efficiency based on event characteristics"""
        try:
            # Base efficiency from event type
            event_type = event.get('domain', event.get('type', 'unknown'))
            
            # Domain-specific efficiency factors
            domain_efficiency = {
                'cognitive_specialization': 0.7,
                'energy_economics': 0.6,
                'mathematical_cognition': 0.8,
                'evolutionary_dynamics': 0.5,
                'reproduction': 0.4,
                'foraging': 0.3,
                'social': 0.6
            }
            
            base_efficiency = domain_efficiency.get(event_type, 0.2)
            
            # Adjust based on event complexity
            event_data = event.get('data', {})
            complexity_factor = min(len(str(event_data)) / 1000, 1.0)  # Complexity up to 1.0
            
            # Energy-based adjustment
            energy_data = event_data.get('energy', {})
            if energy_data:
                energy_level = energy_data.get('level', 0.5)
                energy_factor = min(energy_level / 100, 1.0)
            else:
                energy_factor = 0.5
            
            # Combined efficiency
            total_efficiency = base_efficiency * (0.5 + 0.3 * complexity_factor + 0.2 * energy_factor)
            
            return min(total_efficiency, 0.9)  # Cap at 90%
            
        except Exception as e:
            return 0.1  # Default low efficiency
    
    def _calculate_moon_correlation(self, event: Dict[str, Any]) -> float:
        """Calculate correlation with Moon damping effects"""
        try:
            # Check for stability-related features
            event_data = event.get('data', {})
            
            # Stability indicators
            stability_score = 0.0
            
            # Temporal stability (consistent patterns)
            if 'timestamp' in event and 'duration' in event_data:
                duration = event_data.get('duration', 1)
                stability_score += min(duration / 100, 0.3)
            
            # Pattern stability (repetitive behaviors)
            if 'pattern' in event_data:
                pattern_complexity = len(str(event_data['pattern'])) / 100
                stability_score += min(pattern_complexity, 0.3)
            
            # Energy stability (consistent energy levels)
            energy_data = event_data.get('energy', {})
            if 'variance' in energy_data:
                variance = energy_data.get('variance', 1.0)
                stability_score += max(0, 0.4 - variance / 10)
            
            # Social stability (group cohesion)
            social_data = event_data.get('social', {})
            if 'cohesion' in social_data:
                cohesion = social_data.get('cohesion', 0.5)
                stability_score += cohesion * 0.3
            
            return min(stability_score, 1.0)
            
        except Exception as e:
            return 0.0  # No Moon correlation
    
    def _estimate_impedance_gradient(self, event: Dict[str, Any]) -> float:
        """Estimate impedance gradient from event complexity"""
        try:
            event_data = event.get('data', {})
            
            # Calculate complexity-based gradient
            text_complexity = len(str(event_data))
            gradient = min(text_complexity / 100, 10.0)  # Max gradient of 10
            
            # Adjust for energy variations
            energy_data = event_data.get('energy', {})
            if 'fluctuations' in energy_data:
                fluctuations = energy_data.get('fluctuations', 0.1)
                gradient += fluctuations * 5  # Add fluctuation component
            
            return min(gradient, 15.0)  # Cap at 15
            
        except Exception as e:
            return 1.0  # Default low gradient
    
    def _calculate_cognitive_complexity(self, event: Dict[str, Any]) -> float:
        """Calculate cognitive complexity from event data"""
        try:
            event_data = event.get('data', {})
            
            # Base complexity from event type
            event_type = event.get('domain', event.get('type', 'unknown'))
            
            domain_complexity = {
                'cognitive_specialization': 0.8,
                'mathematical_cognition': 0.9,
                'energy_economics': 0.6,
                'evolutionary_dynamics': 0.7,
                'reproduction': 0.4,
                'foraging': 0.3,
                'social': 0.5
            }
            
            base_complexity = domain_complexity.get(event_type, 0.3)
            
            # Learning indicators
            learning_data = event_data.get('learning', {})
            if learning_data:
                learning_rate = learning_data.get('rate', 0.1)
                base_complexity += learning_rate * 0.2
            
            # Problem-solving indicators
            problem_solving = event_data.get('problem_solving', {})
            if problem_solving:
                success_rate = problem_solving.get('success_rate', 0.5)
                base_complexity += success_rate * 0.2
            
            return min(base_complexity, 1.0)
            
        except Exception as e:
            return 0.3  # Default low complexity
    
    def _calculate_fusion_potential(self, event: Dict[str, Any]) -> float:
        """Calculate fusion-like process potential"""
        try:
            # Combine parasitic efficiency and cognitive complexity
            signature = self.calculate_parasitic_signature(event)
            
            # Fusion potential = efficiency * complexity * energy availability
            energy_data = event.get('data', {}).get('energy', {})
            energy_availability = energy_data.get('available', 0.5) / 100
            
            fusion_potential = signature.parasitic_efficiency * signature.cognitive_complexity * energy_availability
            
            return min(fusion_potential, 1.0)
            
        except Exception as e:
            return 0.1  # Default low potential
    
    def _determine_earth_mars_analog(self, event: Dict[str, Any]) -> str:
        """Determine if event is Earth-like or Mars-like"""
        try:
            signature = self.calculate_parasitic_signature(event)
            
            # Earth-like: High efficiency + high Moon correlation + high complexity
            earth_score = signature.parasitic_efficiency + signature.moon_damping_correlation + signature.cognitive_complexity
            
            # Threshold for Earth-like (sum > 1.5)
            if earth_score > 1.5:
                return "earth_like"
            else:
                return "mars_like"
                
        except Exception as e:
            return "mars_like"  # Default to Mars-like
    
    def map_parasitic_signatures(self) -> Dict[str, Any]:
        """Map parasitic signatures to all Alife events"""
        try:
            if not self.alife_data:
                return {"error": "No Alife data loaded"}
            
            signatures = {}
            domain_efficiencies = {}
            earth_mars_counts = {"earth_like": 0, "mars_like": 0}
            
            for i, event in enumerate(self.alife_data):
                event_id = f"event_{i}"
                signature = self.calculate_parasitic_signature(event)
                
                signatures[event_id] = signature
                
                # Track domain efficiencies
                event_type = event.get('domain', event.get('type', 'unknown'))
                if event_type not in domain_efficiencies:
                    domain_efficiencies[event_type] = []
                domain_efficiencies[event_type].append(signature.parasitic_efficiency)
                
                # Track Earth vs Mars counts
                earth_mars_counts[signature.earth_mars_analog] += 1
            
            # Calculate domain averages
            domain_averages = {
                domain: sum(efficiencies) / len(efficiencies)
                for domain, efficiencies in domain_efficiencies.items()
            }
            
            self.parasitic_signatures = signatures
            self.domain_analysis = domain_averages
            self.earth_mars_validation = earth_mars_counts
            
            return {
                "success": True,
                "total_events_mapped": len(signatures),
                "domain_averages": domain_averages,
                "earth_mars_distribution": earth_mars_counts,
                "avg_parasitic_efficiency": sum(s.parasitic_efficiency for s in signatures.values()) / len(signatures),
                "avg_cognitive_complexity": sum(s.cognitive_complexity for s in signatures.values()) / len(signatures),
                "timestamp": time.time()
            }
            
        except Exception as e:
            return {"error": f"Failed to map parasitic signatures: {e}"}
    
    def identify_parasitic_domains(self) -> Dict[str, Any]:
        """Find domains with highest parasitic efficiency"""
        try:
            if not self.domain_analysis:
                return {"error": "No domain analysis available"}
            
            # Sort domains by efficiency
            sorted_domains = sorted(
                self.domain_analysis.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            # Identify top parasitic domains
            top_domains = sorted_domains[:5]
            low_domains = sorted_domains[-5:]
            
            return {
                "success": True,
                "top_parasitic_domains": top_domains,
                "low_parasitic_domains": low_domains,
                "domain_rankings": sorted_domains,
                "efficiency_range": {
                    "highest": sorted_domains[0][1] if sorted_domains else 0,
                    "lowest": sorted_domains[-1][1] if sorted_domains else 0
                },
                "timestamp": time.time()
            }
            
        except Exception as e:
            return {"error": f"Failed to identify parasitic domains: {e}"}