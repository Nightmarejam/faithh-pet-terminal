"""
Genomic Impedance Sensor Service
Phase 1: Genomic impedance detection and reading
Biological systems that detect environmental impedance patterns
"""

import math
import time
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

@dataclass
class ImpedancePattern:
    """Environmental impedance pattern detected by genomic sensors"""
    frequency: float
    amplitude: float
    phase: float
    source: str  # "internal" or "external"
    biological_impact: float

@dataclass
class GenomicSensor:
    """Genomic impedance sensor in biological organism"""
    sensor_id: str
    position: Tuple[float, float, float]
    sensitivity: float  # 0.0 to 1.0
    internal_reading: float
    external_reading: float
    combined_impedance: float
    detected_patterns: List[ImpedancePattern]
    biasing_potential: float

class GenomicImpedanceSensor:
    """Service for genomic impedance detection and reading"""
    
    def __init__(self, parasitic_alife_service, universal_impedance_service):
        self.parasitic_service = parasitic_alife_service
        self.universal_service = universal_impedance_service
        
        # Genomic sensor parameters
        self.internal_impedance_base = 50.0  # Base cellular impedance
        self.external_impedance_base = 100.0  # Base environmental impedance
        self.genomic_sensitivity = 0.7  # Genomic sensitivity to impedance
        self.biasing_threshold = 0.3  # Threshold for genetic biasing
        
        # Storage for genomic sensors
        self.genomic_sensors = {}
        self.impedance_patterns = []
        
    def create_genomic_sensor(self, organism_id: str, position: Tuple[float, float, float], 
                            sensitivity: float = 0.7) -> Dict[str, Any]:
        """Create a genomic impedance sensor for an organism"""
        try:
            # Get environmental impedance at position
            universal_field = self.universal_service.calculate_universal_impedance(position)
            
            # Calculate internal impedance (cellular metabolic state)
            internal_impedance = self._calculate_internal_impedance(position)
            
            # Calculate external impedance (environmental)
            external_impedance = universal_field.total_impedance
            
            # Combined impedance reading
            combined_impedance = (internal_impedance * 0.6 + external_impedance * 0.4)
            
            # Create genomic sensor
            sensor = GenomicSensor(
                sensor_id=f"{organism_id}_genomic_sensor",
                position=position,
                sensitivity=min(max(sensitivity, 0.1), 1.0),
                internal_reading=internal_impedance,
                external_reading=external_impedance,
                combined_impedance=combined_impedance,
                detected_patterns=[],
                biasing_potential=0.0
            )
            
            # Detect impedance patterns
            patterns = self._detect_impedance_patterns(sensor, universal_field)
            sensor.detected_patterns = patterns
            
            # Calculate biasing potential
            sensor.biasing_potential = self._calculate_biasing_potential(sensor, patterns)
            
            # Store sensor
            self.genomic_sensors[organism_id] = sensor
            
            return {
                "success": True,
                "sensor_id": sensor.sensor_id,
                "organism_id": organism_id,
                "position": position,
                "sensitivity": sensor.sensitivity,
                "readings": {
                    "internal_impedance": sensor.internal_reading,
                    "external_impedance": sensor.external_reading,
                    "combined_impedance": sensor.combined_impedance
                },
                "detected_patterns": len(patterns),
                "biasing_potential": sensor.biasing_potential,
                "timestamp": time.time()
            }
            
        except Exception as e:
            return {"error": f"Failed to create genomic sensor: {e}"}
    
    def _calculate_internal_impedance(self, position: Tuple[float, float, float]) -> float:
        """Calculate internal cellular impedance"""
        try:
            # Base cellular impedance
            base_impedance = self.internal_impedance_base
            
            # Position-dependent metabolic variation
            x, y, z = position
            metabolic_factor = 1.0 + 0.2 * math.sin(x * 0.1) * math.cos(y * 0.1)
            
            # Energy state modulation
            energy_factor = 1.0 + 0.1 * math.sin(z * 0.05)
            
            # Internal impedance calculation
            internal_impedance = base_impedance * metabolic_factor * energy_factor
            
            return internal_impedance
            
        except Exception as e:
            return self.internal_impedance_base
    
    def _detect_impedance_patterns(self, sensor: GenomicSensor, 
                                 universal_field) -> List[ImpedancePattern]:
        """Detect impedance patterns in the environment"""
        try:
            patterns = []
            
            # Detect stellar interference patterns
            stellar_patterns = self._detect_stellar_patterns(sensor, universal_field)
            patterns.extend(stellar_patterns)
            
            # Detect dark energy modulation patterns
            dark_energy_patterns = self._detect_dark_energy_patterns(sensor, universal_field)
            patterns.extend(dark_energy_patterns)
            
            # Detect quantum fluctuation patterns
            quantum_patterns = self._detect_quantum_patterns(sensor, universal_field)
            patterns.extend(quantum_patterns)
            
            # Filter patterns by sensor sensitivity
            filtered_patterns = []
            for pattern in patterns:
                if pattern.amplitude * sensor.sensitivity > 0.1:  # Sensitivity threshold
                    filtered_patterns.append(pattern)
            
            return filtered_patterns
            
        except Exception as e:
            return []
    
    def _detect_stellar_patterns(self, sensor: GenomicSensor, 
                                universal_field) -> List[ImpedancePattern]:
        """Detect stellar interference patterns"""
        try:
            patterns = []
            
            # Get stellar contribution from universal field
            stellar_contribution = universal_field.stellar_contribution
            
            if stellar_contribution > 0.1:
                # Create stellar pattern
                pattern = ImpedancePattern(
                    frequency=1.0e-6,  # Micro-frequency range
                    amplitude=stellar_contribution * 0.01,
                    phase=math.pi * sensor.position[0] / 10.0,
                    source="external",
                    biological_impact=stellar_contribution * 0.5
                )
                patterns.append(pattern)
            
            return patterns
            
        except Exception as e:
            return []
    
    def _detect_dark_energy_patterns(self, sensor: GenomicSensor, 
                                   universal_field) -> List[ImpedancePattern]:
        """Detect dark energy modulation patterns"""
        try:
            patterns = []
            
            # Get dark energy modulation
            dark_energy = universal_field.dark_energy_modulation
            
            if abs(dark_energy) > 1.0:
                # Create dark energy pattern
                pattern = ImpedancePattern(
                    frequency=1.0e-9,  # Nano-frequency range
                    amplitude=abs(dark_energy) * 0.001,
                    phase=math.pi * sensor.position[1] / 10.0,
                    source="external",
                    biological_impact=abs(dark_energy) * 0.3
                )
                patterns.append(pattern)
            
            return patterns
            
        except Exception as e:
            return []
    
    def _detect_quantum_patterns(self, sensor: GenomicSensor, 
                               universal_field) -> List[ImpedancePattern]:
        """Detect quantum fluctuation patterns"""
        try:
            patterns = []
            
            # Get quantum fluctuations
            quantum_fluctuation = universal_field.quantum_fluctuation
            
            if abs(quantum_fluctuation) > 0.001:
                # Create quantum pattern
                pattern = ImpedancePattern(
                    frequency=1.62e-33,  # Planck frequency
                    amplitude=abs(quantum_fluctuation) * 100,
                    phase=math.pi * sensor.position[2] / 10.0,
                    source="internal",
                    biological_impact=abs(quantum_fluctuation) * 10
                )
                patterns.append(pattern)
            
            return patterns
            
        except Exception as e:
            return []
    
    def _calculate_biasing_potential(self, sensor: GenomicSensor, 
                                   patterns: List[ImpedancePattern]) -> float:
        """Calculate genetic biasing potential based on detected patterns"""
        try:
            # Base biasing from impedance levels
            impedance_bias = sensor.combined_impedance / 100.0
            
            # Pattern-based biasing
            pattern_bias = 0.0
            for pattern in patterns:
                pattern_weight = 1.0 if pattern.source == "internal" else 0.7
                pattern_bias += pattern.biological_impact * pattern_weight * sensor.sensitivity
            
            # Normalize pattern bias
            if patterns:
                pattern_bias = pattern_bias / len(patterns)
            
            # Combined biasing potential
            total_bias = (impedance_bias * 0.4 + pattern_bias * 0.6)
            
            # Apply sensitivity modulation
            total_bias *= sensor.sensitivity
            
            # Cap at reasonable range
            return min(max(total_bias, 0.0), 1.0)
            
        except Exception as e:
            return 0.0
    
    def analyze_genomic_sensors(self) -> Dict[str, Any]:
        """Analyze all genomic sensors and their readings"""
        try:
            if not self.genomic_sensors:
                return {"error": "No genomic sensors found"}
            
            analysis = {
                "total_sensors": len(self.genomic_sensors),
                "average_biasing_potential": 0.0,
                "high_biasing_sensors": [],
                "pattern_analysis": {},
                "internal_vs_external": {},
                "position_analysis": {}
            }
            
            # Calculate statistics
            biasing_potentials = []
            internal_readings = []
            external_readings = []
            
            for organism_id, sensor in self.genomic_sensors.items():
                biasing_potentials.append(sensor.biasing_potential)
                internal_readings.append(sensor.internal_reading)
                external_readings.append(sensor.external_reading)
                
                # Track high biasing sensors
                if sensor.biasing_potential > 0.7:
                    analysis["high_biasing_sensors"].append({
                        "organism_id": organism_id,
                        "biasing_potential": sensor.biasing_potential,
                        "position": sensor.position
                    })
            
            # Calculate averages
            if biasing_potentials:
                analysis["average_biasing_potential"] = sum(biasing_potentials) / len(biasing_potentials)
                analysis["internal_vs_external"] = {
                    "avg_internal": sum(internal_readings) / len(internal_readings),
                    "avg_external": sum(external_readings) / len(external_readings),
                    "internal_dominance": sum(internal_readings) > sum(external_readings)
                }
            
            # Pattern analysis
            all_patterns = []
            for sensor in self.genomic_sensors.values():
                all_patterns.extend(sensor.detected_patterns)
            
            if all_patterns:
                internal_patterns = [p for p in all_patterns if p.source == "internal"]
                external_patterns = [p for p in all_patterns if p.source == "external"]
                
                analysis["pattern_analysis"] = {
                    "total_patterns": len(all_patterns),
                    "internal_patterns": len(internal_patterns),
                    "external_patterns": len(external_patterns),
                    "avg_biological_impact": sum(p.biological_impact for p in all_patterns) / len(all_patterns)
                }
            
            return {
                "success": True,
                "analysis": analysis,
                "timestamp": time.time()
            }
            
        except Exception as e:
            return {"error": f"Failed to analyze genomic sensors: {e}"}
    
    def get_sensor_readings(self, organism_id: str) -> Dict[str, Any]:
        """Get detailed readings for a specific genomic sensor"""
        try:
            if organism_id not in self.genomic_sensors:
                return {"error": "Genomic sensor not found"}
            
            sensor = self.genomic_sensors[organism_id]
            
            return {
                "success": True,
                "sensor_id": sensor.sensor_id,
                "organism_id": organism_id,
                "readings": {
                    "internal_impedance": sensor.internal_reading,
                    "external_impedance": sensor.external_reading,
                    "combined_impedance": sensor.combined_impedance,
                    "biasing_potential": sensor.biasing_potential
                },
                "patterns": [
                    {
                        "frequency": p.frequency,
                        "amplitude": p.amplitude,
                        "phase": p.phase,
                        "source": p.source,
                        "biological_impact": p.biological_impact
                    }
                    for p in sensor.detected_patterns
                ],
                "position": sensor.position,
                "sensitivity": sensor.sensitivity,
                "timestamp": time.time()
            }
            
        except Exception as e:
            return {"error": f"Failed to get sensor readings: {e}"}