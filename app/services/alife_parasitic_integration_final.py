"""
Alife Parasitic Integration Service - Final Fixed Version
Phase 3B: Connect parasitic feeding to existing Alife data
All infinite loops and recursion issues fixed
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
        """Calculate parasitic signature for an Alife event - FINAL FIXED VERSION"""
        try:
            # Extract event type
            event_type = event.get('domain', event.get('type', 'unknown'))
            metadata = event.get('metadata', {})
            
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
            
            # Complexity factor (fixed - no infinite loop)
            event_str = str(event)
            complexity_factor = min(len(event_str) / 1000, 1.0)
            
            # Energy factor
            energy_level = metadata.get('agent_energy', 50)
            energy_factor = min(energy_level / 100, 1.0)
            
            # Combined parasitic efficiency
            parasitic_efficiency = base_efficiency * (0.5 + 0.3 * complexity_factor + 0.2 * energy_factor)
            parasitic_efficiency = min(parasitic_efficiency, 0.9)
            
            # Moon damping correlation
            stability_score = 0.0
            
            # Temporal stability
            tick = metadata.get('tick', 1)
            stability_score += min(tick / 100, 0.3)
            
            # Energy stability
            if energy_level > 50:
                stability_score += 0.3
            
            # Pattern stability
            genome = metadata.get('genome_readable', '')
            if len(genome) > 20:
                stability_score += 0.2
            
            moon_damping_correlation = min(stability_score, 1.0)
            
            # Impedance gradient
            text_complexity = len(event_str)
            gradient = min(text_complexity / 100, 10.0)
            
            if energy_level > 100:
                gradient += 2
            
            impedance_gradient = min(gradient, 15.0)
            
            # Cognitive complexity
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
            
            # Genome complexity
            genome_complexity = min(len(genome) / 50, 0.3)
            base_complexity += genome_complexity
            
            # Energy complexity
            if energy_level > 100:
                base_complexity += 0.1
            
            cognitive_complexity = min(base_complexity, 1.0)
            
            # Fusion potential (fixed - no recursion)
            energy_available = energy_level / 100
            fusion_potential = parasitic_efficiency * cognitive_complexity * energy_available
            fusion_potential = min(fusion_potential, 1.0)
            
            # Earth vs Mars analog
            earth_score = parasitic_efficiency + moon_damping_correlation + cognitive_complexity
            earth_mars_analog = "earth_like" if earth_score > 1.5 else "mars_like"
            
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
    
    def map_parasitic_signatures(self) -> Dict[str, Any]:
        """Map parasitic signatures to all Alife events - FINAL FIXED VERSION"""
        try:
            if not self.alife_data:
                return {"error": "No Alife data loaded"}
            
            print(f"📊 Processing {len(self.alife_data)} events...")
            
            signatures = {}
            domain_efficiencies = {}
            earth_mars_counts = {"earth_like": 0, "mars_like": 0}
            
            # Process events with progress tracking
            for i, event in enumerate(self.alife_data):
                if i % 10 == 0:  # Progress update every 10 events
                    print(f"📈 Processing event {i+1}/{len(self.alife_data)}")
                
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
            
            print("✅ Signature mapping completed!")
            
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
            print(f"❌ Error in signature mapping: {e}")
            import traceback
            traceback.print_exc()
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