"""
Parasitic Alife Service
Extension of Moon damping with parasitic impedance feeding
"""

import math
import time
import json
import random
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

@dataclass
class ParasiticParameters:
    """Parameters for parasitic impedance feeding"""
    universal_impedance_base: float = 100.0  # Base universal impedance
    impedance_gradient_threshold: float = 10.0  # Minimum gradient for parasitic extraction
    fusion_energy_threshold: float = 100.0  # Energy needed for fusion-like processes
    parasitic_efficiency_base: float = 0.3  # Base parasitic efficiency
    impedance_mismatch_factor: float = 0.2  # How much impedance mismatch affects extraction
    
class ParasiticAlifeService:
    """Service for managing parasitic impedance feeding in Alife experiments"""
    
    def __init__(self):
        self.params = ParasiticParameters()
        self.universal_field = self._calculate_universal_impedance_field()
        self.parasitic_agents = {}
        self.parasitic_networks = {}
        
    def _calculate_universal_impedance_field(self) -> Dict[str, Any]:
        """Calculate background universal impedance field"""
        field = {}
        
        # Create universal impedance pattern across world
        for x in range(480):
            # Universal impedance varies with position (cosmic background variation)
            base_impedance = self.params.universal_impedance_base
            
            # Add universal harmonics (cosmic microwave background variations)
            harmonic1 = 20 * math.sin(2 * math.pi * x / 480)  # Primary harmonic
            harmonic2 = 10 * math.sin(4 * math.pi * x / 480)  # Secondary harmonic
            harmonic3 = 5 * math.cos(6 * math.pi * x / 480)   # Tertiary harmonic
            
            # Quantum fluctuation noise
            noise = random.gauss(0, 2)
            
            total_impedance = base_impedance + harmonic1 + harmonic2 + harmonic3 + noise
            
            field[str(x)] = {
                "universal_impedance": total_impedance,
                "impedance_gradient": 0.0,  # Will be calculated based on neighbors
                "energy_density": total_impedance * 0.1  # Energy available for extraction
            }
        
        # Calculate impedance gradients
        for x in range(480):
            if x > 0 and x < 479:
                left = field[str(x-1)]["universal_impedance"]
                right = field[str(x+1)]["universal_impedance"]
                current = field[str(x)]["universal_impedance"]
                
                # Gradient is difference from neighbors
                gradient = abs(current - (left + right) / 2)
                field[str(x)]["impedance_gradient"] = gradient
        
        return field
    
    def add_parasitic_feeding_to_experiment(self, experiment_id: str, moon_damping_service) -> Dict[str, Any]:
        """Add parasitic feeding capabilities to existing Moon damping experiment"""
        try:
            # Get existing experiment data
            experiment_status = moon_damping_service.get_experiment_status(experiment_id)
            if not experiment_status.get("success"):
                return {"error": "Experiment not found"}
            
            # Initialize parasitic agents for this experiment
            self.parasitic_agents[experiment_id] = {}
            self.parasitic_networks[experiment_id] = {
                "total_parasitic_energy": 0.0,
                "parasitic_efficiency": 0.0,
                "fusion_active_agents": 0,
                "starvation_agents": 0,
                "network_complexity": 0.0
            }
            
            return {
                "success": True,
                "experiment_id": experiment_id,
                "parasitic_capabilities": "enabled",
                "universal_field_stats": self._get_field_statistics(),
                "timestamp": time.time()
            }
            
        except Exception as e:
            return {"error": f"Failed to add parasitic feeding: {e}"}
    
    def _get_field_statistics(self) -> Dict[str, float]:
        """Get statistics about the universal impedance field"""
        impedances = [data["universal_impedance"] for data in self.universal_field.values()]
        gradients = [data["impedance_gradient"] for data in self.universal_field.values()]
        energy_densities = [data["energy_density"] for data in self.universal_field.values()]
        
        return {
            "avg_impedance": sum(impedances) / len(impedances),
            "max_gradient": max(gradients),
            "avg_energy_density": sum(energy_densities) / len(energy_densities),
            "total_extractable_energy": sum(energy_densities),
            "parasitic_zones": len([g for g in gradients if g > self.params.impedance_gradient_threshold])
        }
    
    def create_parasitic_agent(self, experiment_id: str, agent_id: str, position: int, 
                              moon_damping_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a parasitic agent at a specific position"""
        try:
            if experiment_id not in self.parasitic_agents:
                self.parasitic_agents[experiment_id] = {}
            
            # Get universal field data at position
            field_data = self.universal_field.get(str(position), {})
            universal_impedance = field_data.get("universal_impedance", self.params.universal_impedance_base)
            impedance_gradient = field_data.get("impedance_gradient", 0.0)
            
            # Create parasitic impedance mismatch (agent's own impedance)
            parasitic_impedance = self._create_impedance_mismatch(universal_impedance)
            
            # Calculate parasitic efficiency based on gradient and mismatch
            parasitic_efficiency = self._calculate_parasitic_efficiency(
                impedance_gradient, 
                parasitic_impedance, 
                universal_impedance
            )
            
            # Get Moon damping data
            moon_damping = moon_damping_data.get("moon_damping", "none")
            stability_factor = moon_damping_data.get("stability_factor", 0.5)
            
            # Create parasitic agent
            agent_data = {
                "agent_id": agent_id,
                "position": position,
                "universal_impedance": universal_impedance,
                "parasitic_impedance": parasitic_impedance,
                "impedance_mismatch": abs(parasitic_impedance - universal_impedance),
                "impedance_gradient": impedance_gradient,
                "parasitic_efficiency": parasitic_efficiency,
                "parasitic_energy": 0.0,
                "extracted_energy": 0.0,
                "fusion_threshold": self.params.fusion_energy_threshold,
                "nuclear_state": "inactive",
                "moon_damping": moon_damping,
                "stability_factor": stability_factor,
                "cognitive_complexity": self._calculate_cognitive_complexity(parasitic_efficiency, stability_factor),
                "feeding_strategy": self._determine_feeding_strategy(parasitic_efficiency, impedance_gradient),
                "created_at": time.time()
            }
            
            self.parasitic_agents[experiment_id][agent_id] = agent_data
            
            return {
                "success": True,
                "agent_data": agent_data,
                "parasitic_potential": self._assess_parasitic_potential(agent_data),
                "timestamp": time.time()
            }
            
        except Exception as e:
            return {"error": f"Failed to create parasitic agent: {e}"}
    
    def _create_impedance_mismatch(self, universal_impedance: float) -> float:
        """Create parasitic impedance mismatch for energy extraction"""
        # Parasitic agent creates impedance different from universal field
        mismatch = random.gauss(0, self.params.impedance_mismatch_factor * universal_impedance)
        return universal_impedance + mismatch
    
    def _calculate_parasitic_efficiency(self, gradient: float, parasitic_impedance: float, 
                                      universal_impedance: float) -> float:
        """Calculate parasitic extraction efficiency"""
        # Base efficiency from gradient
        gradient_efficiency = min(gradient / self.params.impedance_gradient_threshold, 1.0)
        
        # Efficiency from impedance mismatch
        mismatch = abs(parasitic_impedance - universal_impedance)
        mismatch_efficiency = 1.0 - min(mismatch / universal_impedance, 0.8)  # Too much mismatch reduces efficiency
        
        # Combined efficiency
        total_efficiency = self.params.parasitic_efficiency_base * gradient_efficiency * mismatch_efficiency
        
        return min(total_efficiency, 0.9)  # Cap at 90% efficiency
    
    def _calculate_cognitive_complexity(self, parasitic_efficiency: float, stability_factor: float) -> float:
        """Calculate cognitive complexity based on parasitic efficiency and stability"""
        # Higher parasitic efficiency and stability enable higher cognition
        base_complexity = 0.3
        efficiency_bonus = parasitic_efficiency * 0.4
        stability_bonus = stability_factor * 0.3
        
        return min(base_complexity + efficiency_bonus + stability_bonus, 1.0)
    
    def _determine_feeding_strategy(self, efficiency: float, gradient: float) -> str:
        """Determine agent's feeding strategy based on conditions"""
        if efficiency > 0.7 and gradient > 15:
            return "aggressive_parasite"  # High efficiency, high gradient
        elif efficiency > 0.4:
            return "moderate_parasite"   # Moderate efficiency
        elif gradient > 10:
            return "opportunistic_parasite"  # Low efficiency but high gradient
        else:
            return "survival_mode"  # Poor conditions
    
    def _assess_parasitic_potential(self, agent_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess the parasitic potential of an agent"""
        efficiency = agent_data["parasitic_efficiency"]
        gradient = agent_data["impedance_gradient"]
        stability = agent_data["stability_factor"]
        
        if efficiency > 0.6 and gradient > 12 and stability > 0.7:
            potential = "excellent"
            prediction = "Likely to achieve fusion-like state"
        elif efficiency > 0.3 and gradient > 8:
            potential = "good"
            prediction = "Moderate parasitic success"
        elif gradient > 5:
            potential = "fair"
            prediction = "Survival-level parasitism"
        else:
            potential = "poor"
            prediction = "Energy starvation likely"
        
        return {
            "parasitic_potential": potential,
            "prediction": prediction,
            "efficiency_score": efficiency,
            "gradient_score": gradient,
            "stability_advantage": stability
        }
    
    def extract_parasitic_energy(self, experiment_id: str, agent_id: str) -> Dict[str, Any]:
        """Extract energy from universal impedance field"""
        try:
            if experiment_id not in self.parasitic_agents:
                return {"error": "Experiment not found"}
            
            if agent_id not in self.parasitic_agents[experiment_id]:
                return {"error": "Agent not found"}
            
            agent = self.parasitic_agents[experiment_id][agent_id]
            field_data = self.universal_field.get(str(agent["position"]), {})
            
            # Calculate energy extraction
            energy_density = field_data.get("energy_density", 0.0)
            extracted_energy = energy_density * agent["parasitic_efficiency"]
            
            # Update agent energy
            agent["parasitic_energy"] += extracted_energy
            agent["extracted_energy"] = extracted_energy
            
            # Update network statistics
            if experiment_id in self.parasitic_networks:
                self.parasitic_networks[experiment_id]["total_parasitic_energy"] += extracted_energy
            
            # Determine nuclear state
            if agent["parasitic_energy"] > agent["fusion_threshold"]:
                agent["nuclear_state"] = "active"
                if experiment_id in self.parasitic_networks:
                    self.parasitic_networks[experiment_id]["fusion_active_agents"] += 1
            else:
                agent["nuclear_state"] = "starvation"
                if experiment_id in self.parasitic_networks:
                    self.parasitic_networks[experiment_id]["starvation_agents"] += 1
            
            return {
                "success": True,
                "extracted_energy": extracted_energy,
                "total_parasitic_energy": agent["parasitic_energy"],
                "nuclear_state": agent["nuclear_state"],
                "efficiency": agent["parasitic_efficiency"],
                "timestamp": time.time()
            }
            
        except Exception as e:
            return {"error": f"Failed to extract energy: {e}"}
    
    def sustain_nuclear_processes(self, experiment_id: str, agent_id: str) -> Dict[str, Any]:
        """Sustain nuclear-like processes using parasitic energy"""
        try:
            # First extract energy
            extraction_result = self.extract_parasitic_energy(experiment_id, agent_id)
            if not extraction_result.get("success"):
                return extraction_result
            
            agent = self.parasitic_agents[experiment_id][agent_id]
            
            # Sustain nuclear processes based on energy
            if agent["nuclear_state"] == "active":
                # Energy cost for maintaining fusion-like processes
                energy_cost = self.params.fusion_energy_threshold * 0.1  # 10% of threshold per cycle
                agent["parasitic_energy"] -= energy_cost
                
                # Check if still active
                if agent["parasitic_energy"] > agent["fusion_threshold"]:
                    return {
                        "success": True,
                        "nuclear_state": "active",
                        "energy_remaining": agent["parasitic_energy"],
                        "process": "fusion_maintenance",
                        "cognitive_output": self._generate_cognitive_output(agent)
                    }
                else:
                    agent["nuclear_state"] "starvation"
                    return {
                        "success": True,
                        "nuclear_state": "starvation",
                        "energy_remaining": agent["parasitic_energy"],
                        "process": "fusion_shutdown"
                    }
            else:
                return {
                    "success": True,
                    "nuclear_state": "starvation",
                    "energy_remaining": agent["parasitic_energy"],
                    "process": "energy_conservation"
                }
                
        except Exception as e:
            return {"error": f"Failed to sustain nuclear processes: {e}"}
    
    def _generate_cognitive_output(self, agent: Dict[str, Any]) -> Dict[str, Any]:
        """Generate cognitive output based on nuclear state and parasitic efficiency"""
        complexity = agent["cognitive_complexity"]
        efficiency = agent["parasitic_efficiency"]
        
        if complexity > 0.8 and efficiency > 0.7:
            return {
                "cognitive_level": "high",
                "output_type": "pattern_recognition",
                "parasitic_strategy": "optimized_extraction",
                "learning_capability": "advanced"
            }
        elif complexity > 0.5:
            return {
                "cognitive_level": "moderate",
                "output_type": "basic_adaptation",
                "parasitic_strategy": "efficient_feeding",
                "learning_capability": "present"
            }
        else:
            return {
                "cognitive_level": "basic",
                "output_type": "survival_instinct",
                "parasitic_strategy": "energy_conservation",
                "learning_capability": "minimal"
            }
    
    def analyze_parasitic_network(self, experiment_id: str) -> Dict[str, Any]:
        """Analyze the parasitic network in an experiment"""
        try:
            if experiment_id not in self.parasitic_agents:
                return {"error": "Experiment not found"}
            
            agents = self.parasitic_agents[experiment_id]
            network_stats = self.parasitic_networks.get(experiment_id, {})
            
            if not agents:
                return {"error": "No parasitic agents in experiment"}
            
            # Calculate network statistics
            total_agents = len(agents)
            fusion_active = len([a for a in agents.values() if a["nuclear_state"] == "active"])
            starvation_agents = len([a for a in agents.values() if a["nuclear_state"] == "starvation"])
            
            avg_efficiency = sum(a["parasitic_efficiency"] for a in agents.values()) / total_agents
            avg_complexity = sum(a["cognitive_complexity"] for a in agents.values()) / total_agents
            total_energy = sum(a["parasitic_energy"] for a in agents.values())
            
            # Feeding strategy distribution
            strategies = {}
            for agent in agents.values():
                strategy = agent["feeding_strategy"]
                strategies[strategy] = strategies.get(strategy, 0) + 1
            
            # Moon damping impact
            moon_damped_agents = [a for a in agents.values() if a["moon_damping"] != "none"]
            moon_damped_efficiency = sum(a["parasitic_efficiency"] for a in moon_damped_agents) / len(moon_damped_agents) if moon_damped_agents else 0
            
            non_moon_agents = [a for a in agents.values() if a["moon_damping"] == "none"]
            non_moon_efficiency = sum(a["parasitic_efficiency"] for a in non_moon_agents) / len(non_moon_agents) if non_moon_agents else 0
            
            analysis = {
                "network_statistics": {
                    "total_agents": total_agents,
                    "fusion_active": fusion_active,
                    "starvation_agents": starvation_agents,
                    "fusion_success_rate": fusion_active / total_agents if total_agents > 0 else 0,
                    "total_parasitic_energy": total_energy,
                    "avg_parasitic_efficiency": avg_efficiency,
                    "avg_cognitive_complexity": avg_complexity
                },
                "feeding_strategies": strategies,
                "moon_damping_impact": {
                    "moon_damped_agents": len(moon_damped_agents),
                    "non_moon_agents": len(non_moon_agents),
                    "moon_damped_efficiency": moon_damped_efficiency,
                    "non_moon_efficiency": non_moon_efficiency,
                    "moon_advantage": moon_damped_efficiency - non_moon_efficiency
                },
                "universal_field_interaction": {
                    "avg_impedance_mismatch": sum(a["impedance_mismatch"] for a in agents.values()) / total_agents,
                    "avg_gradient_utilization": sum(a["impedance_gradient"] for a in agents.values()) / total_agents,
                    "parasitic_zones_utilized": len([a for a in agents.values() if a["impedance_gradient"] > self.params.impedance_gradient_threshold])
                }
            }
            
            return {
                "success": True,
                "experiment_id": experiment_id,
                "analysis": analysis,
                "timestamp": time.time()
            }
            
        except Exception as e:
            return {"error": f"Failed to analyze parasitic network: {e}"}
    
    def compare_parasitic_with_without_moon(self, experiment_id: str) -> Dict[str, Any]:
        """Compare parasitic feeding with and without Moon damping"""
        try:
            analysis = self.analyze_parasitic_network(experiment_id)
            if not analysis.get("success"):
                return analysis
            
            moon_impact = analysis["analysis"]["moon_damping_impact"]
            
            comparison = {
                "moon_damping_advantage": moon_impact["moon_advantage"],
                "efficiency_improvement": (moon_impact["moon_damped_efficiency"] - moon_impact["non_moon_efficiency"]) / moon_impact["non_moon_efficiency"] if moon_impact["non_moon_efficiency"] > 0 else 0,
                "moon_damped_success_rate": len([a for a in self.parasitic_agents[experiment_id].values() if a["moon_damping"] != "none" and a["nuclear_state"] == "active"]) / moon_impact["moon_damped_agents"] if moon_impact["moon_damped_agents"] > 0 else 0,
                "non_moon_success_rate": len([a for a in self.parasitic_agents[experiment_id].values() if a["moon_damping"] == "none" and a["nuclear_state"] == "active"]) / moon_impact["non_moon_agents"] if moon_impact["non_moon_agents"] > 0 else 0
            }
            
            return {
                "success": True,
                "comparison": comparison,
                "conclusion": "Moon damping significantly improves parasitic feeding efficiency and nuclear process success" if moon_impact["moon_advantage"] > 0.1 else "Moon damping has minimal impact on parasitic feeding",
                "timestamp": time.time()
            }
            
        except Exception as e:
            return {"error": f"Failed to compare parasitic performance: {e}"}