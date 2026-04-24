"""
Genomic Biasing Engine Service
Phase 2: Implement copying bias mechanisms based on impedance readings
DNA/RNA copying bias, mutation rate modulation, gene expression bias
"""

import math
import time
import json
import random
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

@dataclass
class GenomicBias:
    """Genomic bias applied to copying process"""
    mutation_rate_bias: float
    gene_expression_bias: Dict[str, float]
    copying_fidelity_bias: float
    adaptive_biasing: float
    source_impedance: float

@dataclass
class BiasingResult:
    """Result of genomic biasing process"""
    original_genome: str
    biased_genome: str
    mutations_applied: int
    expression_changes: Dict[str, float]
    fidelity_score: float
    biasing_strength: float

class GenomicBiasingEngine:
    """Service for implementing genomic biasing based on impedance readings"""
    
    def __init__(self, genomic_impedance_sensor):
        self.sensor_service = genomic_impedance_sensor
        
        # Biasing parameters
        self.base_mutation_rate = 0.001  # Base mutation rate
        self.mutation_rate_modulation = 0.5  # Impedance-driven modulation
        self.expression_bias_strength = 0.3  # Gene expression bias strength
        self.fidelity_impact = 0.2  # Impact on copying fidelity
        self.adaptive_learning_rate = 0.1  # Learning from impedance patterns
        
        # Biasing history for adaptive learning
        self.biasing_history = []
        self.expression_patterns = {}
        
    def apply_genomic_biasing(self, organism_id: str, original_genome: str, 
                            biasing_strength: float = 0.5) -> Dict[str, Any]:
        """Apply genomic biasing based on impedance readings"""
        try:
            # Get sensor readings for organism
            sensor_data = self.sensor_service.get_sensor_readings(organism_id)
            if not sensor_data.get("success"):
                return {"error": "Failed to get sensor readings"}
            
            sensor = sensor_data["readings"]
            
            # Calculate genomic bias based on impedance
            genomic_bias = self._calculate_genomic_bias(sensor, biasing_strength)
            
            # Apply biasing to genome
            biased_genome = self._apply_bias_to_genome(original_genome, genomic_bias)
            
            # Calculate biasing result
            result = self._calculate_biasing_result(original_genome, biased_genome, genomic_bias)
            
            # Store biasing history for adaptive learning
            self._store_biasing_history(organism_id, genomic_bias, result)
            
            return {
                "success": True,
                "organism_id": organism_id,
                "biasing_result": {
                    "original_genome_length": len(original_genome),
                    "biased_genome_length": len(biased_genome),
                    "mutations_applied": result.mutations_applied,
                    "expression_changes": result.expression_changes,
                    "fidelity_score": result.fidelity_score,
                    "biasing_strength": result.biasing_strength
                },
                "genomic_bias": {
                    "mutation_rate_bias": genomic_bias.mutation_rate_bias,
                    "copying_fidelity_bias": genomic_bias.copying_fidelity_bias,
                    "adaptive_biasing": genomic_bias.adaptive_biasing,
                    "source_impedance": genomic_bias.source_impedance
                },
                "sensor_readings": sensor,
                "timestamp": time.time()
            }
            
        except Exception as e:
            return {"error": f"Failed to apply genomic biasing: {e}"}
    
    def _calculate_genomic_bias(self, sensor_readings: Dict[str, Any], 
                               biasing_strength: float) -> GenomicBias:
        """Calculate genomic bias based on impedance readings"""
        try:
            # Get impedance values
            internal_impedance = sensor_readings["internal_impedance"]
            external_impedance = sensor_readings["external_impedance"]
            combined_impedance = sensor_readings["combined_impedance"]
            biasing_potential = sensor_readings["biasing_potential"]
            
            # Calculate mutation rate bias
            # Higher impedance -> higher mutation rate (more environmental pressure)
            impedance_factor = combined_impedance / 100.0
            mutation_rate_bias = self.base_mutation_rate * impedance_factor * self.mutation_rate_modulation
            
            # Calculate gene expression bias
            # Different impedance patterns favor different gene expressions
            gene_expression_bias = self._calculate_expression_bias(
                internal_impedance, external_impedance, biasing_potential
            )
            
            # Calculate copying fidelity bias
            # High impedance can reduce fidelity (stress conditions)
            fidelity_impact = min(impedance_factor * self.fidelity_impact, 0.5)
            copying_fidelity_bias = 1.0 - fidelity_impact
            
            # Calculate adaptive biasing
            # Learning from historical patterns
            adaptive_biasing = self._calculate_adaptive_biasing(
                combined_impedance, biasing_potential
            )
            
            return GenomicBias(
                mutation_rate_bias=mutation_rate_bias,
                gene_expression_bias=gene_expression_bias,
                copying_fidelity_bias=copying_fidelity_bias,
                adaptive_biasing=adaptive_biasing,
                source_impedance=combined_impedance
            )
            
        except Exception as e:
            # Return default bias on error
            return GenomicBias(
                mutation_rate_bias=self.base_mutation_rate,
                gene_expression_bias={},
                copying_fidelity_bias=1.0,
                adaptive_biasing=0.0,
                source_impedance=0.0
            )
    
    def _calculate_expression_bias(self, internal_impedance: float, 
                                  external_impedance: float, 
                                  biasing_potential: float) -> Dict[str, float]:
        """Calculate gene expression bias based on impedance patterns"""
        try:
            expression_bias = {}
            
            # Internal impedance favors metabolic genes
            if internal_impedance > 50.0:
                expression_bias["metabolic_genes"] = 0.7 * biasing_potential
                expression_bias["energy_processing"] = 0.6 * biasing_potential
            else:
                expression_bias["metabolic_genes"] = 0.3 * biasing_potential
                expression_bias["energy_processing"] = 0.4 * biasing_potential
            
            # External impedance favors environmental response genes
            if external_impedance > 80.0:
                expression_bias["stress_response"] = 0.8 * biasing_potential
                expression_bias["environmental_sensing"] = 0.7 * biasing_potential
                expression_bias["protective_mechanisms"] = 0.6 * biasing_potential
            else:
                expression_bias["stress_response"] = 0.2 * biasing_potential
                expression_bias["environmental_sensing"] = 0.3 * biasing_potential
                expression_bias["protective_mechanisms"] = 0.4 * biasing_potential
            
            # High biasing potential favors cognitive genes
            if biasing_potential > 0.7:
                expression_bias["cognitive_processing"] = 0.9 * biasing_potential
                expression_bias["pattern_recognition"] = 0.8 * biasing_potential
                expression_bias["mathematical_cognition"] = 0.7 * biasing_potential
            else:
                expression_bias["cognitive_processing"] = 0.1 * biasing_potential
                expression_bias["pattern_recognition"] = 0.2 * biasing_potential
                expression_bias["mathematical_cognition"] = 0.1 * biasing_potential
            
            return expression_bias
            
        except Exception as e:
            return {}
    
    def _calculate_adaptive_biasing(self, combined_impedance: float, 
                                   biasing_potential: float) -> float:
        """Calculate adaptive biasing based on historical patterns"""
        try:
            # Base adaptive biasing from current conditions
            base_adaptive = biasing_potential * 0.5
            
            # Historical learning component
            if self.biasing_history:
                # Find similar impedance conditions in history
                similar_conditions = [
                    h for h in self.biasing_history 
                    if abs(h["impedance"] - combined_impedance) < 20.0
                ]
                
                if similar_conditions:
                    # Learn from successful past biasing
                    avg_success = sum(h["success_rate"] for h in similar_conditions) / len(similar_conditions)
                    adaptive_component = avg_success * self.adaptive_learning_rate
                else:
                    adaptive_component = 0.0
            else:
                adaptive_component = 0.0
            
            # Combined adaptive biasing
            total_adaptive = base_adaptive + adaptive_component
            
            return min(max(total_adaptive, 0.0), 1.0)
            
        except Exception as e:
            return 0.0
    
    def _apply_bias_to_genome(self, original_genome: str, genomic_bias: GenomicBias) -> str:
        """Apply genomic bias to create biased genome"""
        try:
            biased_genome = list(original_genome)
            
            # Apply mutation bias
            mutations = self._apply_mutations(biased_genome, genomic_bias.mutation_rate_bias)
            
            # Apply expression bias (represented as sequence modifications)
            expression_changes = self._apply_expression_bias(
                biased_genome, genomic_bias.gene_expression_bias
            )
            
            # Apply fidelity bias (sequence quality changes)
            fidelity_changes = self._apply_fidelity_bias(
                biased_genome, genomic_bias.copying_fidelity_bias
            )
            
            return "".join(biased_genome)
            
        except Exception as e:
            return original_genome
    
    def _apply_mutations(self, genome: List[str], mutation_rate: float) -> int:
        """Apply mutations based on bias"""
        try:
            mutations_applied = 0
            genome_length = len(genome)
            
            # Calculate number of mutations
            num_mutations = int(genome_length * mutation_rate)
            
            # Apply random mutations
            for _ in range(num_mutations):
                if genome_length > 0:
                    position = random.randint(0, genome_length - 1)
                    original_base = genome[position]
                    
                    # Simple mutation: change to different base
                    bases = ['A', 'T', 'G', 'C']
                    available_bases = [b for b in bases if b != original_base]
                    
                    if available_bases:
                        genome[position] = random.choice(available_bases)
                        mutations_applied += 1
            
            return mutations_applied
            
        except Exception as e:
            return 0
    
    def _apply_expression_bias(self, genome: List[str], expression_bias: Dict[str, float]) -> Dict[str, float]:
        """Apply gene expression bias (represented as sequence patterns)"""
        try:
            expression_changes = {}
            
            # For each gene type, modify sequence patterns
            for gene_type, bias_strength in expression_bias.items():
                if bias_strength > 0.5:
                    # Add expression-enhancing patterns
                    pattern = self._get_expression_pattern(gene_type)
                    if pattern and len(genome) > len(pattern):
                        # Insert pattern at random position
                        position = random.randint(0, len(genome) - len(pattern))
                        for i, base in enumerate(pattern):
                            if position + i < len(genome):
                                genome[position + i] = base
                    
                    expression_changes[gene_type] = bias_strength
            
            return expression_changes
            
        except Exception as e:
            return {}
    
    def _get_expression_pattern(self, gene_type: str) -> str:
        """Get expression pattern for gene type"""
        patterns = {
            "metabolic_genes": "ATGCGTAC",
            "energy_processing": "GCTAGCTA",
            "stress_response": "TTACGGTA",
            "environmental_sensing": "CGATCGAT",
            "protective_mechanisms": "TACGATCG",
            "cognitive_processing": "ATCGATCG",
            "pattern_recognition": "GCTAGCTA",
            "mathematical_cognition": "CGATCGAT"
        }
        return patterns.get(gene_type, "")
    
    def _apply_fidelity_bias(self, genome: List[str], fidelity_bias: float) -> float:
        """Apply copying fidelity bias"""
        try:
            # Fidelity bias affects sequence quality
            # Lower fidelity = more errors/uncertainty in sequence
            if fidelity_bias < 0.8:
                # Introduce some uncertainty (represented as ambiguous bases)
                num_uncertain = int(len(genome) * (1.0 - fidelity_bias) * 0.1)
                for _ in range(num_uncertain):
                    if genome:
                        position = random.randint(0, len(genome) - 1)
                        genome[position] = 'N'  # Ambiguous base
            
            return fidelity_bias
            
        except Exception as e:
            return 1.0
    
    def _calculate_biasing_result(self, original_genome: str, biased_genome: str, 
                                 genomic_bias: GenomicBias) -> BiasingResult:
        """Calculate the result of biasing process"""
        try:
            # Count mutations
            mutations_applied = sum(1 for a, b in zip(original_genome, biased_genome) if a != b)
            
            # Calculate expression changes (from bias)
            expression_changes = genomic_bias.gene_expression_bias
            
            # Calculate fidelity score
            fidelity_score = genomic_bias.copying_fidelity_bias
            
            # Calculate overall biasing strength
            biasing_strength = (
                genomic_bias.mutation_rate_bias * 0.3 +
                len(expression_changes) * 0.01 * 0.3 +
                genomic_bias.adaptive_biasing * 0.4
            )
            
            return BiasingResult(
                original_genome=original_genome,
                biased_genome=biased_genome,
                mutations_applied=mutations_applied,
                expression_changes=expression_changes,
                fidelity_score=fidelity_score,
                biasing_strength=min(biasing_strength, 1.0)
            )
            
        except Exception as e:
            return BiasingResult(
                original_genome=original_genome,
                biased_genome=biased_genome,
                mutations_applied=0,
                expression_changes={},
                fidelity_score=1.0,
                biasing_strength=0.0
            )
    
    def _store_biasing_history(self, organism_id: str, genomic_bias: GenomicBias, 
                             result: BiasingResult):
        """Store biasing history for adaptive learning"""
        try:
            history_entry = {
                "organism_id": organism_id,
                "timestamp": time.time(),
                "impedance": genomic_bias.source_impedance,
                "mutation_rate": genomic_bias.mutation_rate_bias,
                "fidelity": genomic_bias.copying_fidelity_bias,
                "adaptive_biasing": genomic_bias.adaptive_biasing,
                "mutations_applied": result.mutations_applied,
                "fidelity_score": result.fidelity_score,
                "biasing_strength": result.biasing_strength,
                "success_rate": result.fidelity_score * (1.0 - result.mutations_applied / len(result.original_genome))
            }
            
            self.biasing_history.append(history_entry)
            
            # Keep only recent history (last 1000 entries)
            if len(self.biasing_history) > 1000:
                self.biasing_history = self.biasing_history[-1000:]
            
        except Exception as e:
            pass
    
    def analyze_biasing_patterns(self) -> Dict[str, Any]:
        """Analyze biasing patterns across all organisms"""
        try:
            if not self.biasing_history:
                return {"error": "No biasing history available"}
            
            analysis = {
                "total_biasing_events": len(self.biasing_history),
                "average_mutation_rate": 0.0,
                "average_fidelity": 0.0,
                "average_biasing_strength": 0.0,
                "success_rate_distribution": {},
                "impedance_correlation": {},
                "adaptive_effectiveness": 0.0
            }
            
            # Calculate averages
            mutation_rates = []
            fidelities = []
            biasing_strengths = []
            success_rates = []
            impedances = []
            
            for entry in self.biasing_history:
                mutation_rates.append(entry["mutation_rate"])
                fidelities.append(entry["fidelity"])
                biasing_strengths.append(entry["biasing_strength"])
                success_rates.append(entry["success_rate"])
                impedances.append(entry["impedance"])
            
            if mutation_rates:
                analysis["average_mutation_rate"] = sum(mutation_rates) / len(mutation_rates)
                analysis["average_fidelity"] = sum(fidelities) / len(fidelities)
                analysis["average_biasing_strength"] = sum(biasing_strengths) / len(biasing_strengths)
                
                # Success rate distribution
                high_success = len([s for s in success_rates if s > 0.8])
                medium_success = len([s for s in success_rates if 0.5 <= s <= 0.8])
                low_success = len([s for s in success_rates if s < 0.5])
                
                analysis["success_rate_distribution"] = {
                    "high_success_rate": high_success / len(success_rates),
                    "medium_success_rate": medium_success / len(success_rates),
                    "low_success_rate": low_success / len(success_rates)
                }
                
                # Impedance correlation
                if len(impedances) > 1 and len(success_rates) > 1:
                    correlation = self._calculate_correlation(impedances, success_rates)
                    analysis["impedance_correlation"] = {
                        "correlation_coefficient": correlation,
                        "impedance_biasing_correlation": correlation > 0.3
                    }
                
                # Adaptive effectiveness
                adaptive_entries = [e for e in self.biasing_history if e["adaptive_biasing"] > 0.1]
                if adaptive_entries:
                    adaptive_success = sum(e["success_rate"] for e in adaptive_entries) / len(adaptive_entries)
                    overall_success = sum(success_rates) / len(success_rates)
                    analysis["adaptive_effectiveness"] = adaptive_success - overall_success
            
            return {
                "success": True,
                "analysis": analysis,
                "timestamp": time.time()
            }
            
        except Exception as e:
            return {"error": f"Failed to analyze biasing patterns: {e}"}
    
    def _calculate_correlation(self, x_values: List[float], y_values: List[float]) -> float:
        """Calculate correlation coefficient between two lists"""
        try:
            if len(x_values) != len(y_values) or len(x_values) < 2:
                return 0.0
            
            n = len(x_values)
            sum_x = sum(x_values)
            sum_y = sum(y_values)
            sum_xy = sum(x * y for x, y in zip(x_values, y_values))
            sum_x2 = sum(x * x for x in x_values)
            sum_y2 = sum(y * y for y in y_values)
            
            numerator = n * sum_xy - sum_x * sum_y
            denominator = math.sqrt((n * sum_x2 - sum_x ** 2) * (n * sum_y2 - sum_y ** 2))
            
            if denominator == 0:
                return 0.0
            
            return numerator / denominator
            
        except Exception as e:
            return 0.0