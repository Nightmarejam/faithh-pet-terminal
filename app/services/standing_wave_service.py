"""
Standing Wave Resonance Service
Implements Option C: Lagrange Point Model for Alife experiments
"""

import math
import time
import json
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass

@dataclass
class WaveParameters:
    """Parameters for standing wave resonance experiment"""
    world_width: int = 480
    wave_ratio: float = 2.0  # 1:2 octave ratio
    nodes: List[int] = None  # Lagrange points
    antinodes: List[int] = None  # Energy zones
    energy_scale: float = 100.0
    
    def __post_init__(self):
        if self.nodes is None:
            self.nodes = [120, 240, 360]  # Lagrange points
        if self.antinodes is None:
            self.antinodes = [0, 60, 180, 300, 420, 480]  # Energy zones

class StandingWaveService:
    """Service for managing standing wave resonance experiments"""
    
    def __init__(self):
        self.params = WaveParameters()
        self.experiments = {}
        self.current_phase = 0
        
    def setup_standing_wave_experiment(self, experiment_id: str = "standing_wave_v1") -> Dict[str, Any]:
        """Setup a new standing wave resonance experiment"""
        try:
            experiment = {
                "id": experiment_id,
                "type": "standing_wave_resonance",
                "parameters": {
                    "world_width": self.params.world_width,
                    "wave_ratio": self.params.wave_ratio,
                    "nodes": self.params.nodes,
                    "antinodes": self.params.antinodes,
                    "energy_scale": self.params.energy_scale
                },
                "wave_state": {
                    "wave1_phase": 0.0,
                    "wave2_phase": 0.0,
                    "time_step": 0
                },
                "agent_positions": {},
                "energy_distribution": self._calculate_initial_energy_distribution(),
                "selection_pressure_zones": self._calculate_selection_pressure_zones(),
                "created_at": time.time()
            }
            
            self.experiments[experiment_id] = experiment
            return experiment
            
        except Exception as e:
            return {"error": f"Failed to setup experiment: {e}"}
    
    def _calculate_initial_energy_distribution(self) -> Dict[str, Any]:
        """Calculate initial energy distribution across world"""
        distribution = {}
        
        for x in range(self.params.world_width):
            # Initial energy based on position relative to nodes/antinodes
            energy = self.energy_at_position(x, 0.0, 0.0)
            zone_type = self._get_zone_type(x)
            
            distribution[str(x)] = {
                "energy": energy,
                "zone_type": zone_type,
                "selection_pressure": self._calculate_selection_pressure(zone_type)
            }
        
        return distribution
    
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
    
    def update_wave_state(self, experiment_id: str, dt: float = 0.1) -> Dict[str, Any]:
        """Update wave state for one time step"""
        try:
            if experiment_id not in self.experiments:
                return {"error": "Experiment not found"}
            
            experiment = self.experiments[experiment_id]
            wave_state = experiment["wave_state"]
            
            # Update phases (wave1 and wave2 at 1:2 ratio)
            wave_state["wave1_phase"] += dt
            wave_state["wave2_phase"] += dt * self.params.wave_ratio
            wave_state["time_step"] += 1
            
            # Update energy distribution
            new_distribution = {}
            for x in range(self.params.world_width):
                energy = self.energy_at_position(x, wave_state["wave1_phase"], wave_state["wave2_phase"])
                zone_type = self._get_zone_type(x)
                
                new_distribution[str(x)] = {
                    "energy": energy,
                    "zone_type": zone_type,
                    "selection_pressure": self._calculate_selection_pressure(zone_type),
                    "wave_amplitude": abs(
                        math.sin(2 * math.pi * x / self.params.world_width - wave_state["wave1_phase"]) +
                        math.sin(2 * math.pi * x / self.params.world_width + wave_state["wave2_phase"])
                    )
                }
            
            experiment["energy_distribution"] = new_distribution
            
            return {
                "success": True,
                "time_step": wave_state["time_step"],
                "phases": {
                    "wave1": wave_state["wave1_phase"],
                    "wave2": wave_state["wave2_phase"]
                },
                "energy_summary": self._get_energy_summary(new_distribution)
            }
            
        except Exception as e:
            return {"error": f"Failed to update wave state: {e}"}
    
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
        """Place an agent at a specific position"""
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
                "wave_amplitude": energy_dist[str(position)].get("wave_amplitude", 0),
                "placed_at": time.time()
            }
            
            experiment["agent_positions"][agent_id] = agent_data
            
            return {
                "success": True,
                "agent_data": agent_data,
                "survival_prediction": self._predict_survival(agent_data)
            }
            
        except Exception as e:
            return {"error": f"Failed to place agent: {e}"}
    
    def _predict_survival(self, agent_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict agent survival based on position and wave state"""
        zone_type = agent_data["zone_type"]
        energy = agent_data["current_energy"]
        pressure = agent_data["selection_pressure"]
        
        if zone_type == "node":
            # Safe but energetically poor - slow starvation
            survival_time = "long (slow starvation)"
            cognitive_requirement = "minimal"
            energy_abundance = "very low"
        elif zone_type == "antinode":
            # High energy, high pressure - requires cognition
            survival_time = "variable (high pressure)"
            cognitive_requirement = "high"
            energy_abundance = "very high"
        else:  # transition
            # Mixed conditions - adaptation needed
            survival_time = "moderate"
            cognitive_requirement = "moderate"
            energy_abundance = "moderate"
        
        return {
            "predicted_survival_time": survival_time,
            "cognitive_requirement": cognitive_requirement,
            "energy_abundance": energy_abundance,
            "adaptation_pressure": pressure
        }
    
    def analyze_agent_distribution(self, experiment_id: str) -> Dict[str, Any]:
        """Analyze distribution of agents across zones"""
        try:
            if experiment_id not in self.experiments:
                return {"error": "Experiment not found"}
            
            experiment = self.experiments[experiment_id]
            agents = experiment["agent_positions"]
            
            distribution = {
                "nodes": [],
                "antinodes": [],
                "transition_zones": []
            }
            
            for agent_id, agent_data in agents.items():
                zone_type = agent_data["zone_type"]
                if zone_type == "node":
                    distribution["nodes"].append(agent_id)
                elif zone_type == "antinode":
                    distribution["antinodes"].append(agent_id)
                else:
                    distribution["transition_zones"].append(agent_id)
            
            # Calculate statistics
            total_agents = len(agents)
            stats = {
                "total_agents": total_agents,
                "zone_distribution": {
                    "nodes": len(distribution["nodes"]),
                    "antinodes": len(distribution["antinodes"]),
                    "transition_zones": len(distribution["transition_zones"])
                },
                "percentages": {
                    "nodes": len(distribution["nodes"]) / total_agents * 100 if total_agents > 0 else 0,
                    "antinodes": len(distribution["antinodes"]) / total_agents * 100 if total_agents > 0 else 0,
                    "transition_zones": len(distribution["transition_zones"]) / total_agents * 100 if total_agents > 0 else 0
                },
                "selection_pressure_analysis": self._analyze_selection_pressure_by_zone(agents)
            }
            
            return {
                "success": True,
                "experiment_id": experiment_id,
                "analysis": stats,
                "agent_lists": distribution
            }
            
        except Exception as e:
            return {"error": f"Failed to analyze distribution: {e}"}
    
    def _analyze_selection_pressure_by_zone(self, agents: Dict[str, Any]) -> Dict[str, float]:
        """Analyze average selection pressure by zone"""
        pressures = {"nodes": [], "antinodes": [], "transition_zones": []}
        
        for agent_data in agents.values():
            zone_type = agent_data["zone_type"]
            pressure = agent_data["selection_pressure"]
            
            if zone_type == "node":
                pressures["nodes"].append(pressure)
            elif zone_type == "antinode":
                pressures["antinodes"].append(pressure)
            else:
                pressures["transition_zones"].append(pressure)
        
        return {
            "nodes": sum(pressures["nodes"]) / len(pressures["nodes"]) if pressures["nodes"] else 0,
            "antinodes": sum(pressures["antinodes"]) / len(pressures["antinodes"]) if pressures["antinodes"] else 0,
            "transition_zones": sum(pressures["transition_zones"]) / len(pressures["transition_zones"]) if pressures["transition_zones"] else 0
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
                "antinodes": self.params.antinodes
            }
        }