#!/usr/bin/env python3
"""
Enhanced Multi-Generational Adaptation Test
Phase 3+: Advanced multi-generational evolution with lineage tracking
"""

import json
import time
import requests
import random
from datetime import datetime

class EnhancedMultiGenerational:
    """Enhanced multi-generational adaptation experiment"""
    
    def __init__(self, backend_url="http://localhost:5557"):
        self.backend_url = backend_url
        self.config = {
            "generations": 5,
            "population_size": 40,
            "selection_pressure": 0.7,
            "mutation_rate": 0.1
        }
    
    def run_enhanced_evolution(self) -> Dict[str, Any]:
        """Run enhanced multi-generational evolution"""
        print("🧬 Starting Enhanced Multi-Generational Evolution")
        print("=" * 60)
        
        results = {
            "experiment_type": "enhanced_multi_generational_evolution",
            "timestamp": datetime.now().isoformat(),
            "config": self.config,
            "generations": []
        }
        
        # Run evolution
        for generation in range(self.config["generations"]):
            print(f"🔄 Generation {generation + 1}/{self.config['generations']}")
            
            gen_result = self.run_generation(generation)
            results["generations"].append(gen_result)
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"enhanced_multi_generational_results_{timestamp}.json"
        
        results_dir = Path("/home/jonat/ai-stack/genomic_results")
        results_dir.mkdir(exist_ok=True)
        
        with open(results_dir / filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"📄 Results saved to: {filename}")
        return results
    
    def run_generation(self, generation: int) -> Dict[str, Any]:
        """Run single generation"""
        # Create organisms for this generation
        organisms = []
        for i in range(self.config["population_size"]):
            organism_id = f"gen{generation}_org{i+1:03d}"
            position = [
                random.uniform(-15, 15),
                random.uniform(-15, 15),
                random.uniform(-5, 5)
            ]
            sensitivity = random.uniform(0.2, 0.8)
            
            organisms.append({
                "organism_id": organism_id,
                "position": position,
                "sensitivity": sensitivity,
                "generation": generation
            })
        
        # Create sensors and apply biasing
        sensors_created = 0
        biasing_applied = 0
        
        for organism in organisms:
            try:
                # Create sensor
                response = requests.post(
                    f"{self.backend_url}/api/genomic/impedance-sensor",
                    json=organism,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("success"):
                        sensors_created += 1
                        
                        # Apply biasing
                        biasing_data = {
                            "organism_id": organism["organism_id"],
                            "original_genome": "ATGCGTACATGCGTACATGCGTACATGCGTACATGCGTACATGCGTAC",
                            "biasing_strength": organism["sensitivity"]
                        }
                        
                        bias_response = requests.post(
                            f"{self.backend_url}/api/genomic/biasing-analysis",
                            json=biasing_data,
                            timeout=30
                        )
                        
                        if bias_response.status_code == 200:
                            bias_result = bias_response.json()
                            if bias_result.get("success"):
                                biasing_applied += 1
            except:
                pass
        
        return {
            "generation": generation,
            "organisms": len(organisms),
            "sensors_created": sensors_created,
            "biasing_applied": biasing_applied,
            "success_rate": (sensors_created / len(organisms)) * (biasing_applied / len(organisms))
        }

def main():
    """Main execution function"""
    experiment = EnhancedMultiGenerational()
    results = experiment.run_enhanced_evolution()
    
    print("\n🚀 Enhanced Multi-Generational Evolution Completed!")

if __name__ == "__main__":
    main()
