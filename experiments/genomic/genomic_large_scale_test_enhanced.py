#!/usr/bin/env python3
"""
Enhanced Genomic Large-Scale Testing Experiment
Phase 1+: Advanced testing with statistical validation and real-time monitoring
"""

import json
import time
import requests
import statistics
import random
from datetime import datetime
import logging

class EnhancedGenomicLargeScaleExperiment:
    """Enhanced large-scale genomic impedance reading experiment"""
    
    def __init__(self, backend_url="http://localhost:5557"):
        self.backend_url = backend_url
        self.results = []
        self.organisms = []
        self.real_time_stats = {}
        
        # Enhanced configuration
        self.config = {
            "organism_count": 200,  # Increased from 100
            "position_ranges": {
                "x": (-20, 20),
                "y": (-20, 20),
                "z": (-10, 10)
            },
            "sensitivity_range": (0.1, 1.0),
            "environmental_zones": [
                {"name": "low_impedance", "range": (-10, -5), "characteristics": "stable"},
                {"name": "medium_impedance", "range": (-5, 5), "characteristics": "dynamic"},
                {"name": "high_impedance", "range": (5, 10), "characteristics": "chaotic"}
            ]
        }
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def run_enhanced_experiment(self) -> Dict[str, Any]:
        """Run the enhanced large-scale experiment"""
        print("🧬 Starting Enhanced Genomic Large-Scale Experiment")
        print(f"📊 Organism Count: {self.config['organism_count']}")
        print(f"🌍 Environmental Zones: {len(self.config['environmental_zones'])}")
        print("=" * 60)
        
        start_time = time.time()
        
        # Create enhanced organisms
        print("📝 Creating enhanced test organisms...")
        organisms = self.create_enhanced_test_organisms()
        print(f"✅ Created {len(organisms)} test organisms")
        
        # Create enhanced sensors
        print("🔬 Creating enhanced genomic sensors...")
        sensor_results = self.create_enhanced_genomic_sensors(organisms)
        print(f"✅ Sensors created: {sensor_results['successful']}, Failed: {sensor_results['failed']}")
        
        # Apply enhanced biasing
        print("🧬 Applying enhanced genomic biasing...")
        biasing_results = self.apply_enhanced_genomic_biasing(organisms)
        print(f"✅ Biasing applied: {biasing_results['successful']}, Failed: {biasing_results['failed']}")
        
        # Compile results
        total_time = time.time() - start_time
        
        results = {
            "experiment_type": "enhanced_large_scale_test",
            "timestamp": datetime.now().isoformat(),
            "duration": total_time,
            "config": self.config,
            "organisms": {
                "total": len(organisms),
                "zones": self.config["environmental_zones"]
            },
            "sensor_results": sensor_results,
            "biasing_results": biasing_results,
            "success_rate": (sensor_results["successful"] / len(organisms)) * (biasing_results["successful"] / len(organisms))
        }
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"enhanced_genomic_large_scale_results_{timestamp}.json"
        
        results_dir = Path("/home/jonat/ai-stack/genomic_results")
        results_dir.mkdir(exist_ok=True)
        
        with open(results_dir / filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"📄 Results saved to: {filename}")
        
        # Print summary
        print(f"\n✅ Overall Success Rate: {results['success_rate']:.1%}")
        print(f"⏱️  Duration: {results['duration']:.1f} seconds")
        
        return results
    
    def create_enhanced_test_organisms(self, count: int = None) -> List[Dict[str, Any]]:
        """Create enhanced test organisms with environmental zones"""
        if count is None:
            count = self.config["organism_count"]
        
        organisms = []
        
        for i in range(count):
            organism_id = f"enhanced_organism_{i+1:04d}"
            
            # Assign to environmental zone
            zone = random.choice(self.config["environmental_zones"])
            
            # Generate position within zone
            if zone["name"] == "low_impedance":
                x = random.uniform(-20, -10)
                y = random.uniform(-20, -10)
            elif zone["name"] == "medium_impedance":
                x = random.uniform(-10, 10)
                y = random.uniform(-10, 10)
            else:  # high_impedance
                x = random.uniform(10, 20)
                y = random.uniform(10, 20)
            
            z = random.uniform(-5, 5)
            
            # Enhanced sensitivity based on zone
            if zone["name"] == "low_impedance":
                sensitivity = random.uniform(0.8, 1.0)
            elif zone["name"] == "medium_impedance":
                sensitivity = random.uniform(0.4, 0.8)
            else:  # high_impedance
                sensitivity = random.uniform(0.1, 0.4)
            
            organism = {
                "organism_id": organism_id,
                "position": [x, y, z],
                "sensitivity": sensitivity,
                "environmental_zone": zone["name"],
                "zone_characteristics": zone["characteristics"]
            }
            
            organisms.append(organism)
        
        return organisms
    
    def create_enhanced_genomic_sensors(self, organisms: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create enhanced genomic sensors with real-time monitoring"""
        results = {"successful": 0, "failed": 0, "sensors": []}
        
        for i, organism in enumerate(organisms):
            try:
                sensor_data = {
                    "organism_id": organism["organism_id"],
                    "position": organism["position"],
                    "sensitivity": organism["sensitivity"],
                    "environmental_zone": organism["environmental_zone"],
                    "zone_characteristics": organism["zone_characteristics"]
                }
                
                response = requests.post(
                    f"{self.backend_url}/api/genomic/impedance-sensor",
                    json=sensor_data,
                    timeout=30
                )
                
                if response.status_code == 200:
                    sensor_result = response.json()
                    
                    if sensor_result.get("success"):
                        sensor_info = sensor_result.get("genomic_sensor", {})
                        
                        # Add enhanced metadata
                        sensor_info.update({
                            "environmental_zone": organism["environmental_zone"],
                            "zone_characteristics": organism["zone_characteristics"]
                        })
                        
                        results["sensors"].append(sensor_info)
                        results["successful"] += 1
                        
                        # Progress indicator
                        if (i + 1) % 50 == 0:
                            self.logger.info(f"Created {i + 1}/{len(organisms)} sensors")
                    else:
                        results["failed"] += 1
                else:
                    results["failed"] += 1
                    
            except Exception as e:
                results["failed"] += 1
                self.logger.error(f"Exception creating sensor: {str(e)}")
        
        return results
    
    def apply_enhanced_genomic_biasing(self, organisms: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Apply enhanced genomic biasing with evolutionary tracking"""
        results = {"successful": 0, "failed": 0, "biasing_results": []}
        
        for organism in organisms:
            try:
                biasing_data = {
                    "organism_id": organism["organism_id"],
                    "original_genome": "ATGCGTACATGCGTACATGCGTACATGCGTACATGCGTACATGCGTAC",
                    "biasing_strength": organism["sensitivity"],
                    "environmental_zone": organism["environmental_zone"]
                }
                
                response = requests.post(
                    f"{self.backend_url}/api/genomic/biasing-analysis",
                    json=biasing_data,
                    timeout=30
                )
                
                if response.status_code == 200:
                    biasing_result = response.json()
                    
                    if biasing_result.get("success"):
                        biasing_info = biasing_result.get("biasing_analysis", {})
                        
                        # Add enhanced metadata
                        biasing_info.update({
                            "environmental_zone": organism["environmental_zone"]
                        })
                        
                        results["biasing_results"].append(biasing_info)
                        results["successful"] += 1
                    else:
                        results["failed"] += 1
                else:
                    results["failed"] += 1
                    
            except Exception as e:
                results["failed"] += 1
                self.logger.error(f"Exception applying biasing: {str(e)}")
        
        return results

def main():
    """Main execution function"""
    experiment = EnhancedGenomicLargeScaleExperiment()
    results = experiment.run_enhanced_experiment()
    
    print("\n🚀 Enhanced Genomic Large-Scale Experiment Completed Successfully!")

if __name__ == "__main__":
    main()
