"""
Genomic Biasing Engine Service (Fixed Version)
Phase 2: Implement copying bias mechanisms based on impedance readings
DNA/RNA copying bias, mutation rate modulation, gene expression bias

Fixed: Race condition between sensor creation and biasing application
"""

import math
import time
import json
import random
import threading
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from queue import Queue, Empty
from datetime import datetime

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
        
        # Queue-based processing to fix race condition
        self.biasing_queue = Queue()
        self.biasing_results = {}
        self.biasing_lock = threading.Lock()
        self.processing_thread = None
        self.shutdown_flag = False
        
        # Start processing thread
        self._start_processing_thread()
    
    def _start_processing_thread(self):
        """Start the background processing thread"""
        self.processing_thread = threading.Thread(target=self._process_biasing_queue, daemon=True)
        self.processing_thread.start()
    
    def _process_biasing_queue(self):
        """Background thread to process biasing requests"""
        while not self.shutdown_flag:
            try:
                # Get biasing request from queue
                request = self.biasing_queue.get(timeout=1.0)
                
                # Process the request
                result = self._process_biasing_request(request)
                
                # Store result
                with self.biasing_lock:
                    self.biasing_results[request["request_id"]] = result
                
                # Mark task as done
                self.biasing_queue.task_done()
                
            except Empty:
                # Queue is empty, continue
                continue
            except Exception as e:
                print(f"Error processing biasing request: {e}")
                continue
    
    def _process_biasing_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single biasing request"""
        request_id = request["request_id"]
        organism_id = request["organism_id"]
        original_genome = request["original_genome"]
        biasing_strength = request["biasing_strength"]
        
        try:
            # Retry getting sensor readings with exponential backoff
            sensor_readings = self._get_sensor_readings_with_retry(organism_id, max_retries=5)
            
            if not sensor_readings:
                return {
                    "success": False,
                    "error": "Failed to get sensor readings after retries",
                    "request_id": request_id
                }
            
            # Calculate genomic bias based on impedance
            genomic_bias = self._calculate_genomic_bias(sensor_readings, biasing_strength)
            
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
                "sensor_readings": sensor_readings,
                "timestamp": time.time(),
                "request_id": request_id
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to apply genomic biasing: {e}",
                "request_id": request_id
            }
    
    def _get_sensor_readings_with_retry(self, organism_id: str, max_retries: int = 5) -> Optional[Dict[str, Any]]:
        """Get sensor readings with retry logic and exponential backoff"""
        for attempt in range(max_retries):
            try:
                # Get sensor readings for organism
                sensor_data = self.sensor_service.get_sensor_readings(organism_id)
                
                if sensor_data.get("success"):
                    return sensor_data["readings"]
                
                # If not successful, wait with exponential backoff
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) * 0.1  # 0.1s, 0.2s, 0.4s, 0.8s, 1.6s
                    time.sleep(wait_time)
                    
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) * 0.1
                    time.sleep(wait_time)
                continue
        
        return None
    
    def apply_genomic_biasing(self, organism_id: str, original_genome: str, 
                            biasing_strength: float = 0.5) -> Dict[str, Any]:
        """Apply genomic biasing based on impedance readings (queue-based)"""
        try:
            # Generate unique request ID
            request_id = f"biasing_{organism_id}_{int(time.time() * 1000000)}"
            
            # Create biasing request
            request = {
                "request_id": request_id,
                "organism_id": organism_id,
                "original_genome": original_genome,
                "biasing_strength": biasing_strength,
                "timestamp": time.time()
            }
            
            # Add to queue
            self.biasing_queue.put(request)
            
            # Wait for result (with timeout)
            timeout_seconds = 30.0  # 30 second timeout
            start_time = time.time()
            
            while time.time() - start_time < timeout_seconds:
                with self.biasing_lock:
                    if request_id in self.biasing_results:
                        result = self.biasing_results.pop(request_id)
                        return result
                
                time.sleep(0.1)  # Check every 100ms
            
            # Timeout occurred
            return {
                "success": False,
                "error": f"Timeout waiting for biasing result after {timeout_seconds}s",
                "request_id": request_id
            }
            
        except Exception as e:
            return {"error": f"Failed to queue genomic biasing: {e}"}
    
    def apply_genomic_biasing_sync(self, organism_id: str, original_genome: str, 
                                 biasing_strength: float = 0.5) -> Dict[str, Any]:
        """Apply genomic biasing synchronously (fallback method)"""
        try:
            # Get sensor readings for organism with retry
            sensor_readings = self._get_sensor_readings_with_retry(organism_id, max_retries=3)
            
            if not sensor_readings:
                return {"error": "Failed to get sensor readings"}
            
            sensor = sensor_readings
            
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
        # Extract impedance values
        combined_impedance = sensor_readings.get("combined_impedance", 50.0)
        biasing_potential = sensor_readings.get("biasing_potential", 0.1)
        
        # Calculate mutation rate bias
        # Higher impedance -> lower mutation rate (more stable copying)
        impedance_factor = 1.0 / (1.0 + combined_impedance / 100.0)
        mutation_rate_bias = self.base_mutation_rate * (1.0 - impedance_factor * self.mutation_rate_modulation)
        
        # Calculate gene expression bias
        expression_bias = {}
        expression_genes = [
            "cognitive_processing",
            "energy_processing", 
            "environmental_sensing",
            "metabolic_genes",
            "stress_response"
        ]
        
        for gene in expression_genes:
            # Bias expression based on impedance and biasing potential
            base_bias = biasing_potential * biasing_strength
            impedance_modulation = (combined_impedance - 50.0) / 100.0
            
            # Different genes respond differently to impedance
            if gene == "cognitive_processing":
                expression_bias[gene] = base_bias * (1.0 + impedance_modulation * 0.5)
            elif gene == "energy_processing":
                expression_bias[gene] = base_bias * (1.0 - impedance_modulation * 0.3)
            elif gene == "environmental_sensing":
                expression_bias[gene] = base_bias * (1.0 + abs(impedance_modulation) * 0.4)
            else:
                expression_bias[gene] = base_bias * (1.0 + impedance_modulation * 0.2)
        
        # Calculate copying fidelity bias
        # Higher biasing potential -> higher fidelity
        fidelity_bias = 0.5 + (biasing_potential * self.fidelity_impact)
        
        # Calculate adaptive biasing
        adaptive_bias = biasing_strength * self.adaptive_learning_rate
        
        return GenomicBias(
            mutation_rate_bias=mutation_rate_bias,
            gene_expression_bias=expression_bias,
            copying_fidelity_bias=fidelity_bias,
            adaptive_biasing=adaptive_bias,
            source_impedance=combined_impedance
        )
    
    def _apply_bias_to_genome(self, original_genome: str, genomic_bias: GenomicBias) -> str:
        """Apply biasing to genome sequence"""
        biased_genome = list(original_genome)
        
        # Apply mutations based on mutation rate bias
        mutation_rate = genomic_bias.mutation_rate_bias
        mutations_applied = 0
        
        for i in range(len(biased_genome)):
            if random.random() < mutation_rate:
                # Apply mutation
                original_base = biased_genome[i]
                possible_bases = ['A', 'T', 'G', 'C']
                possible_bases.remove(original_base)
                biased_genome[i] = random.choice(possible_bases)
                mutations_applied += 1
        
        return ''.join(biased_genome)
    
    def _calculate_biasing_result(self, original_genome: str, biased_genome: str, 
                                genomic_bias: GenomicBias) -> BiasingResult:
        """Calculate the result of genomic biasing"""
        # Count mutations
        mutations_applied = sum(1 for a, b in zip(original_genome, biased_genome) if a != b)
        
        # Calculate expression changes based on gene expression bias
        expression_changes = genomic_bias.gene_expression_bias.copy()
        
        # Calculate fidelity score
        fidelity_score = genomic_bias.copying_fidelity_bias
        
        # Calculate biasing strength
        biasing_strength = genomic_bias.adaptive_biasing
        
        return BiasingResult(
            original_genome=original_genome,
            biased_genome=biased_genome,
            mutations_applied=mutations_applied,
            expression_changes=expression_changes,
            fidelity_score=fidelity_score,
            biasing_strength=biasing_strength
        )
    
    def _store_biasing_history(self, organism_id: str, genomic_bias: GenomicBias, 
                             result: BiasingResult):
        """Store biasing history for adaptive learning"""
        history_entry = {
            "organism_id": organism_id,
            "timestamp": datetime.now().isoformat(),
            "genomic_bias": {
                "mutation_rate_bias": genomic_bias.mutation_rate_bias,
                "copying_fidelity_bias": genomic_bias.copying_fidelity_bias,
                "adaptive_biasing": genomic_bias.adaptive_biasing,
                "source_impedance": genomic_bias.source_impedance
            },
            "result": {
                "mutations_applied": result.mutations_applied,
                "fidelity_score": result.fidelity_score,
                "biasing_strength": result.biasing_strength
            }
        }
        
        self.biasing_history.append(history_entry)
        
        # Keep only last 1000 entries
        if len(self.biasing_history) > 1000:
            self.biasing_history = self.biasing_history[-1000:]
    
    def get_biasing_statistics(self) -> Dict[str, Any]:
        """Get biasing statistics for monitoring"""
        if not self.biasing_history:
            return {
                "total_biasing_operations": 0,
                "avg_mutation_rate": 0,
                "avg_fidelity_score": 0,
                "queue_size": self.biasing_queue.qsize()
            }
        
        # Calculate statistics
        total_operations = len(self.biasing_history)
        mutation_rates = [entry["genomic_bias"]["mutation_rate_bias"] for entry in self.biasing_history]
        fidelity_scores = [entry["result"]["fidelity_score"] for entry in self.biasing_history]
        
        return {
            "total_biasing_operations": total_operations,
            "avg_mutation_rate": sum(mutation_rates) / len(mutation_rates),
            "avg_fidelity_score": sum(fidelity_scores) / len(fidelity_scores),
            "queue_size": self.biasing_queue.qsize(),
            "processing_thread_alive": self.processing_thread.is_alive() if self.processing_thread else False
        }
    
    def shutdown(self):
        """Shutdown the biasing engine"""
        self.shutdown_flag = True
        if self.processing_thread:
            self.processing_thread.join(timeout=5.0)

# Backward compatibility alias
GenomicBiasingEngineFixed = GenomicBiasingEngine