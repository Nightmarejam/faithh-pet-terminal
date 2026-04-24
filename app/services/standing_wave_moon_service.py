"""
Standing Wave Resonance Service with Moon Damping
Enhanced Option C: Lagrange Point Model + Moon Damping Mass
"""

import math
import time
import json
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass

@dataclass
class WaveParameters:
    """Parameters for standing wave resonance experiment with Moon damping"""
    world_width: int = 480
    wave_ratio: float = 2.0  # 1:2 octave ratio
    nodes: List[int] = None  # Lagrange points
    antinodes: List[int] = None  # Energy zones
    energy_scale: float = 100.0
    # Moon damping parameters
    moon_position: int = 240  # Damping mass at center node
    moon_mass: float = 0.3  # Damping coefficient (0-1)
    moon_influence_radius: int = 60  # Range of damping effect
    moon_enabled: bool = True  # Toggle for comparison experiments
    
    def __post_init__(self):
        if self.nodes is None:
            self.nodes = [120, 240, 360]  # Lagrange points
        if self.antinodes is None:
            self.antinodes = [0, 60, 180, 300, 420, 480]  # Energy zones

class StandingWaveMoonService:
    """Enhanced service for managing standing wave resonance with Moon damping"""
    
    def __init__(self):
        self.params = WaveParameters()
        self.experiments = {}
        self.current_phase = 0
        
    def setup_standing_wave_experiment(self, experiment_id: str = "standing_wave_moon_v1", 
                                     moon_enabled: bool = True, moon_mass: float = 0.3) -> Dict[str, Any]:
        """Setup a new standing wave resonance experiment with Moon damping"""
        try:
            # Update parameters for this experiment
            self.params.moon_enabled = moon_enabled
            self.params.moon_mass = moon_mass
            
            experiment = {
                "id": experiment_id,
                "type": "standing_wave_resonance_moon",
                "parameters": {
                    "world_width": self.params.world_width,
                    "wave_ratio": self.params.wave_ratio,
                    "nodes": self.params.nodes,
                    "antinodes": self.params.antinodes,
                    "energy_scale": self.params.energy_scale,
                    "moon_position": self.params.moon_position,
                    "moon_mass": self.params.moon_mass,
                    "moon_influence_radius": self.params.moon_influence_radius,
                    "moon_enabled": self.params.moon_enabled
                },
                "wave_state": {
                    "wave1_phase": 0.0,
                    "wave2_phase": 0.0,
                    "time_step": 0
                },
                "agent_positions": {},
                "energy_distribution": self._calculate_initial_energy_distribution(),
                "selection_pressure_zones": self._calculate_selection_pressure_zones(),
                "moon_damping_zones": self._calculate_moon_damping_zones() if moon_enabled else {},
                "stability_metrics": {
                    "oscillation_variance": 0.0,
                    "energy_stability": 0.0,
                    "pattern_predictability": 0.0
                },
                "created_at": time.time()
            }
            
            self.experiments[experiment_id] = experiment
            return experiment
            
        except Exception as e:
            return {"error": f"Failed to setup experiment: {e}"}
    
    def _calculate_moon_damping_zones(self) -> Dict[str, Any]:
        """Calculate Moon damping influence zones"""
        if not self.params.moon_enabled:
            return {}
        
        zones = {
            "strong_damping": [],
            "moderate_damping": [],
            "no_damping": []
        }
        
        for x in range(self.params.world_width):
            distance_to_moon = abs(x - self.params.moon_position)
            
            if distance_to_moon <= self.params.moon_influence_radius / 3:
                zones["strong_damping"].append(x)
            elif distance_to_moon <= self.params.moon_influence_radius:
                zones["moderate_damping"].append(x)
            else:
                zones["no_damping"].append(x)
        
        return zones
    
    def _calculate_initial_energy_distribution(self) -> Dict[str, Any]:
        """Calculate initial energy distribution across world with Moon damping"""
        distribution = {}
        
        for x in range(self.params.world_width):
            # Initial energy based on position relative to nodes/antinodes and Moon damping
            energy = self.energy_at_position_with_moon(x, 0.0, 0.0)
            zone_type = self._get_zone_type(x)
            moon_damping = self._get_moon_damping_level(x)
            
            distribution[str(x)] = {
                "energy": energy,
                "zone_type": zone_type,
                "selection_pressure": self._calculate_selection_pressure(zone_type),
                "moon_damping": moon_damping,
                "stability_factor": self._calculate_stability_factor(x, zone_type, moon_damping)
            }
        
        return distribution
    
    def _get_moon_damping_level(self, position: int) -> str:
        """Get Moon damping level at a position"""
        if not self.params.moon_enabled:
            return "none"
        
        distance_to_moon = abs(position - self.params.moon_position)
        
        if distance_to_moon <= self.params.moon_influence_radius / 3:
            return "strong"
        elif distance_to_moon <= self.params.moon_influence_radius:
            return "moderate"
        else:
            return "none"
    
    def _calculate_stability_factor(self, position: int, zone_type: str, moon_damping: str) -> float:
        """Calculate stability factor based on zone and Moon damping"""
        base_stability = {
            "node": 0.8,  # Naturally stable
            "antinode": 0.3,  # Naturally unstable
            "transition": 0.5  # Moderate
        }
        
        moon_stability_bonus = {
            "strong": 0.4,  # Moon greatly stabilizes
            "moderate": 0.2,  # Moon moderately stabilizes
            "none": 0.0  # No effect
        }
        
        stability = base_stability.get(zone_type, 0.5) + moon_stability_bonus.get(moon_damping, 0.0)
        return min(1.0, stability)  # Cap at 1.0
    
    def _get_zone_type(self, position: int) -> str:
        """Determine zone type for a position"""
        if position in self.params.nodes:
            return "node"  # Lagrange point - safe but energy poor
        elif position in self.params.antinodes:
            return "antinode"  # High energy, high pressure
        else:
            return "transition"  # Mixed zone
    
    def _calculate_selection_pressure(self, zone_type: str) -> float:
        """Calculate selection pressure based on zone type"""
        if zone_type == "node":
            return 0.1  # Low pressure, safe but sparse
        elif zone_type == "antinode":
            return 1.0  # High pressure, abundant energy
        else:  # transition
            return 0.5  # Moderate pressure
    
    def _calculate_selection_pressure_zones(self) -> Dict[str, List[int]]:
        """Calculate selection pressure zones across the world"""
        zones = {
            "low_pressure": [],  # Nodes
            "high_pressure": [],  # Antinodes
            "moderate_pressure": []  # Transition zones
        }
        
        for x in range(self.params.world_width):
            zone_type = self._get_zone_type(x)
            if zone_type == "node":
                zones["low_pressure"].append(x)
            elif zone_type == "antinode":
                zones["high_pressure"].append(x)
            else:
                zones["moderate_pressure"].append(x)
        
        return zones
    
    def energy_at_position(self, x: int, wave1_phase: float, wave2_phase: float) -> float:
        """Calculate energy at a given position based on wave interference"""
        # Normalize position to wavelength
        wavelength = self.params.world_width / 2  # Half wavelength fits in world
        k = 2 * math.pi / wavelength  # Wave number
        
        # Two waves traveling in opposite directions
        wave1 = math.sin(k * x - wave1_phase)
        wave2 = math.sin(k * x + wave2_phase)
        
        # Standing wave amplitude
        amplitude = abs(wave1 + wave2)
        
        # Scale energy
        energy = amplitude * self.params.energy_scale
        
        return energy
    
    def energy_at_position_with_moon(self, x: int, wave1_phase: float, wave2_phase: float) -> float:
        """Calculate energy at position with Moon damping effect"""
        base_energy = self.energy_at_position(x, wave1_phase, wave2_phase)
        
        if not self.params.moon_enabled:
            return base_energy
        
        # Moon damping effect
        distance_to_moon = abs(x - self.params.moon_position)
        if distance_to_moon < self.params.moon_influence_radius:
            # Damping factor decreases with distance from Moon
            damping_factor = 1 - (self.params.moon_mass * (1 - distance_to_moon / self.params.moon_influence_radius))
            base_energy *= damping_factor
        
        return base_energy
    
    def update_wave_state(self, experiment_id: str, dt: float = 0.1) -> Dict[str, Any]:
        """Update wave state for one time step and calculate stability metrics"""
        try:
            if experiment_id not in self.experiments:
                return {"error": "Experiment not found"}
            
            experiment = self.experiments[experiment_id]
            wave_state = experiment["wave_state"]
            
            # Store previous energy for stability calculation
            prev_energy_dist = experiment["energy_distribution"].copy()
            
            # Update phases (wave1 and wave2 at 1:2 ratio)
            wave_state["wave1_phase"] += dt
            wave_state["wave2_phase"] += dt * self.params.wave_ratio
            wave_state["time_step"] += 1
            
            # Update energy distribution
            new_distribution = {}
            for x in range(self.params.world_width):
                energy = self.energy_at_position_with_moon(x, wave_state["wave1_phase"], wave_state["wave2_phase"])
                zone_type = self._get_zone_type(x)
                moon_damping = self._get_moon_damping_level(x)
                
                new_distribution[str(x)] = {
                    "energy": energy,
                    "zone_type": zone_type,
                    "selection_pressure": self._calculate_selection_pressure(zone_type),
                    "moon_damping": moon_damping,
                    "stability_factor": self._calculate_stability_factor(x, zone_type, moon_damping),
                    "wave_amplitude": abs(
                        math.sin(2 * math.pi * x / self.params.world_width - wave_state["wave1_phase"]) +
                        math.sin(2 * math.pi * x / self.params.world_width + wave_state["wave2_phase"])
                    )
                }
            
            experiment["energy_distribution"] = new_distribution
            
            # Calculate stability metrics
            stability_metrics = self._calculate_stability_metrics(prev_energy_dist, new_distribution)
            experiment["stability_metrics"] = stability_metrics
            
            return {
                "success": True,
                "time_step": wave_state["time_step"],
                "phases": {
                    "wave1": wave_state["wave1_phase"],
                    "wave2": wave_state["wave2_phase"]
                },
                "energy_summary": self._get_energy_summary(new_distribution),
                "stability_metrics": stability_metrics,
                "moon_enabled": self.params.moon_enabled
            }
            
        except Exception as e:
            return {"error": f"Failed to update wave state: {e}"}
    
    def _calculate_stability_metrics(self, prev_dist: Dict, new_dist: Dict) -> Dict[str, float]:
        """Calculate stability metrics comparing previous and current energy distribution"""
        try:
            # Calculate oscillation variance
            prev_energies = [data["energy"] for data in prev_dist.values()]
            new_energies = [data["energy"] for data in new_dist.values()]
            
            # Energy variance (lower = more stable)
            energy_variance = sum((e - sum(new_energies)/len(new_energies))**2 for e in new_energies) / len(new_energies)
            
            # Energy change rate
            if len(prev_energies) == len(new_energies):
                energy_changes = [abs(new - prev) for prev, new in zip(prev_energies, new_energies)]
                avg_change = sum(energy_changes) / len(energy_changes)
                max_change = max(energy_changes)
            else:
                avg_change = 0
                max_change = 0
            
            # Pattern predictability (based on stability factors)
            stability_factors = [data["stability_factor"] for data in new_dist.values()]
            avg_stability = sum(stability_factors) / len(stability_factors)
            
            return {
                "oscillation_variance": energy_variance,
                "energy_stability": 1.0 / (1.0 + avg_change),  # Inverse of change rate
                "pattern_predictability": avg_stability,
                "max_energy_change": max_change,
                "avg_energy_change": avg_change
            }
            
        except Exception as e:
            return {
                "oscillation_variance": 0.0,
                "energy_stability": 0.0,
                "pattern_predictability": 0.0,
                "max_energy_change": 0.0,
                "avg_energy_change": 0.0,
                "error": str(e)
            }
    
    def _get_energy_summary(self, distribution: Dict[str, Any]) -> Dict[str, float]:
        """Get summary statistics of energy distribution"""
        energies = [data["energy"] for data in distribution.values()]
        
        return {
            "total_energy": sum(energies),
            "average_energy": sum(energies) / len(energies),
            "max_energy": max(energies),
            "min_energy": min(energies),
            "energy_variance": sum((e - sum(energies)/len(energies))**2 for e in energies) / len(energies)
        }
    
    def place_agent(self, experiment_id: str, agent_id: str, position: int) -> Dict[str, Any]:
        """Place an agent at a specific position with Moon-aware survival prediction"""
        try:
            if experiment_id not in self.experiments:
                return {"error": "Experiment not found"}
            
            if position < 0 or position >= self.params.world_width:
                return {"error": "Position out of bounds"}
            
            experiment = self.experiments[experiment_id]
            wave_state = experiment["wave_state"]
            energy_dist = experiment["energy_distribution"]
            
            agent_data = {
                "agent_id": agent_id,
                "position": position,
                "zone_type": self._get_zone_type(position),
                "current_energy": energy_dist[str(position)]["energy"],
                "selection_pressure": energy_dist[str(position)]["selection_pressure"],
                "moon_damping": energy_dist[str(position)]["moon_damping"],
                "stability_factor": energy_dist[str(position)]["stability_factor"],
                "wave_amplitude": energy_dist[str(position)].get("wave_amplitude", 0),
                "placed_at": time.time()
            }
            
            experiment["agent_positions"][agent_id] = agent_data
            
            return {
                "success": True,
                "agent_data": agent_data,
                "survival_prediction": self._predict_survival_with_moon(agent_data),
                "learning_potential": self._assess_learning_potential(agent_data)
            }
            
        except Exception as e:
            return {"error": f"Failed to place agent: {e}"}
    
    def _predict_survival_with_moon(self, agent_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict agent survival based on position, wave state, and Moon damping"""
        zone_type = agent_data["zone_type"]
        energy = agent_data["current_energy"]
        pressure = agent_data["selection_pressure"]
        moon_damping = agent_data["moon_damping"]
        stability = agent_data["stability_factor"]
        
        # Enhanced survival prediction with Moon damping
        if zone_type == "node":
            if moon_damping == "strong":
                survival_time = "very long (Moon-stabilized node)"
                cognitive_requirement = "minimal"
                energy_abundance = "very low but stable"
            else:
                survival_time = "long (slow starvation)"
                cognitive_requirement = "minimal"
                energy_abundance = "very low"
        elif zone_type == "antinode":
            if moon_damping == "strong":
                survival_time = "extended (Moon-damped antinode)"
                cognitive_requirement = "moderate-high"
                energy_abundance = "high but stable"
            else:
                survival_time = "variable (high pressure)"
                cognitive_requirement = "high"
                energy_abundance = "very high"
        else:  # transition
            if moon_damping == "moderate":
                survival_time = "good (Moon-stabilized transition)"
                cognitive_requirement = "moderate"
                energy_abundance = "moderate and stable"
            else:
                survival_time = "moderate"
                cognitive_requirement = "moderate"
                energy_abundance = "moderate"
        
        return {
            "predicted_survival_time": survival_time,
            "cognitive_requirement": cognitive_requirement,
            "energy_abundance": energy_abundance,
            "adaptation_pressure": pressure,
            "stability_advantage": stability,
            "moon_influence": moon_damping
        }
    
    def _assess_learning_potential(self, agent_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess learning potential based on pattern stability"""
        stability = agent_data["stability_factor"]
        moon_damping = agent_data["moon_damping"]
        zone_type = agent_data["zone_type"]
        
        # Learning potential depends on pattern stability
        if stability > 0.8:
            learning_potential = "excellent (stable patterns)"
            learning_speed = "fast"
        elif stability > 0.6:
            learning_potential = "good (moderately stable)"
            learning_speed = "moderate"
        elif stability > 0.4:
            learning_potential = "fair (somewhat stable)"
            learning_speed = "slow"
        else:
            learning_potential = "poor (chaotic patterns)"
            learning_speed = "very slow"
        
        return {
            "learning_potential": learning_potential,
            "learning_speed": learning_speed,
            "pattern_stability": stability,
            "moon_effect": f"{'stabilizing' if moon_damping != 'none' else 'neutral'}"
        }
    
    def compare_with_without_moon(self, experiment_id_with_moon: str, experiment_id_without_moon: str) -> Dict[str, Any]:
        """Compare experiments with and without Moon damping"""
        try:
            if experiment_id_with_moon not in self.experiments or experiment_id_without_moon not in self.experiments:
                return {"error": "One or both experiments not found"}
            
            exp_with_moon = self.experiments[experiment_id_with_moon]
            exp_without_moon = self.experiments[experiment_id_without_moon]
            
            # Compare stability metrics
            stability_with = exp_with_moon["stability_metrics"]
            stability_without = exp_without_moon["stability_metrics"]
            
            # Compare agent distributions
            agents_with = exp_with_moon["agent_positions"]
            agents_without = exp_without_moon["agent_positions"]
            
            comparison = {
                "stability_comparison": {
                    "with_moon": stability_with,
                    "without_moon": stability_without,
                    "improvement": {
                        "oscillation_variance": stability_without["oscillation_variance"] - stability_with["oscillation_variance"],
                        "energy_stability": stability_with["energy_stability"] - stability_without["energy_stability"],
                        "pattern_predictability": stability_with["pattern_predictability"] - stability_without["pattern_predictability"]
                    }
                },
                "agent_comparison": {
                    "with_moon_count": len(agents_with),
                    "without_moon_count": len(agents_without),
                    "survival_advantage": self._calculate_survival_advantage(agents_with, agents_without)
                },
                "moon_damping_effect": "stabilizing" if stability_with["pattern_predictability"] > stability_without["pattern_predictability"] else "destabilizing"
            }
            
            return {
                "success": True,
                "comparison": comparison,
                "timestamp": time.time()
            }
            
        except Exception as e:
            return {"error": f"Failed to compare experiments: {e}"}
    
    def _calculate_survival_advantage(self, agents_with: Dict, agents_without: Dict) -> Dict[str, float]:
        """Calculate survival advantage with Moon damping"""
        # Simple comparison based on stability factors
        with_stability = [data.get("stability_factor", 0) for data in agents_with.values()]
        without_stability = [data.get("stability_factor", 0) for data in agents_without.values()]
        
        avg_with = sum(with_stability) / len(with_stability) if with_stability else 0
        avg_without = sum(without_stability) / len(without_stability) if without_stability else 0
        
        return {
            "average_stability_with": avg_with,
            "average_stability_without": avg_without,
            "stability_advantage": avg_with - avg_without
        }
    
    def get_experiment_status(self, experiment_id: str) -> Dict[str, Any]:
        """Get current status of an experiment"""
        try:
            if experiment_id not in self.experiments:
                return {"error": "Experiment not found"}
            
            experiment = self.experiments[experiment_id]
            
            return {
                "success": True,
                "experiment_id": experiment_id,
                "type": experiment["type"],
                "time_step": experiment["wave_state"]["time_step"],
                "current_phases": {
                    "wave1": experiment["wave_state"]["wave1_phase"],
                    "wave2": experiment["wave_state"]["wave2_phase"]
                },
                "total_agents": len(experiment["agent_positions"]),
                "energy_summary": self._get_energy_summary(experiment["energy_distribution"]),
                "stability_metrics": experiment["stability_metrics"],
                "moon_enabled": experiment["parameters"]["moon_enabled"],
                "created_at": experiment["created_at"]
            }
            
        except Exception as e:
            return {"error": f"Failed to get experiment status: {e}"}
    
    def list_experiments(self) -> Dict[str, Any]:
        """List all standing wave experiments"""
        return {
            "success": True,
            "experiments": list(self.experiments.keys()),
            "total_count": len(self.experiments),
            "parameters": {
                "world_width": self.params.world_width,
                "wave_ratio": self.params.wave_ratio,
                "nodes": self.params.nodes,
                "antinodes": self.params.antinodes,
                "moon_position": self.params.moon_position,
                "moon_mass": self.params.moon_mass,
                "moon_influence_radius": self.params.moon_influence_radius
            }
        }