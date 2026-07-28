#!/usr/bin/env python3
"""
Enhanced Environmental Adaptation Test
Phase 2+: Advanced environmental adaptation with dynamic zones
"""

import json
import time
import requests
import random
from datetime import datetime

class EnhancedEnvironmentalAdaptation:
    """Enhanced environmental adaptation experiment"""
    
    def __init__(self, backend_url="http://localhost:5557"):
        self.backend_url = backend_url
        self.config = {
            "environments": [
                {
                    "name": "stable",
                    "impedance_range": (10, 30),
                    "characteristics": "low variability"
                },
                {
                    "name": "dynamic",
                    "impedance_range": (30, 70),
                    "characteristics": "moderate variability"
                },
                {
                    "name": "chaotic",
                    "impedance_range": (70, 100),
                    "characteristics": "high variability"
                }
            ]
        }
    
    def run_enhanced_adaptation(self) -> Dict[str, Any]:
        """Run enhanced environmental adaptation experiment"""
        print("🌍 Starting Enhanced Environmental Adaptation Experiment")
        print("=" * 60)
        
        results = {
            "experiment_type": "enhanced_environmental_adaptation",
            "timestamp": datetime.now().isoformat(),
            "config": self.config,
            "results": []
        }
        
        # Test each environment
        for env in self.config["environments"]:
            print(f"🔬 Testing {env['name']} environment...")
            env_result = self.test_environment(env)
            results["results"].append(env_result)
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"enhanced_environmental_adaptation_results_{timestamp}.json"
        
        results_dir = Path("/home/jonat/ai-stack/genomic_results")
        results_dir.mkdir(exist_ok=True)
        
        with open(results_dir / filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"📄 Results saved to: {filename}")
        return results
    
    def test_environment(self, environment: Dict[str, Any]) -> Dict[str, Any]:
        """Test specific environment"""
        # Create test organisms for this environment
        organisms = []
        for i in range(50):
            organism_id = f"{environment['name']}_organism_{i+1:03d}"
            position = [
                random.uniform(-10, 10),
                random.uniform(-10, 10),
                random.uniform(-5, 5)
            ]
            sensitivity = random.uniform(0.3, 0.9)
            
            organisms.append({
                "organism_id": organism_id,
                "position": position,
                "sensitivity": sensitivity
            })
        
        # Create sensors
        sensors_created = 0
        for organism in organisms:
            try:
                response = requests.post(
                    f"{self.backend_url}/api/genomic/impedance-sensor",
                    json=organism,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("success"):
                        sensors_created += 1
            except:
                pass
        
        return {
            "environment": environment["name"],
            "organisms_tested": len(organisms),
            "sensors_created": sensors_created,
            "success_rate": sensors_created / len(organisms)
        }

def main():
    """Main execution function"""
    experiment = EnhancedEnvironmentalAdaptation()
    results = experiment.run_enhanced_adaptation()
    
    print("\n🚀 Enhanced Environmental Adaptation Experiment Completed!")

if __name__ == "__main__":
    main()
