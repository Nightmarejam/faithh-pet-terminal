#!/usr/bin/env python3
"""
Zone Comparison Analysis Experiment
Advanced comparison of different environmental zones
"""

import json
import requests
import statistics
from datetime import datetime

class ZoneComparisonAnalysis:
    """Zone comparison analysis system"""
    
    def __init__(self, backend_url="http://localhost:5557"):
        self.backend_url = backend_url
        self.zones = {
            "low_impedance": {"position_range": (-15, -5), "sensitivity": (0.7, 1.0)},
            "medium_impedance": {"position_range": (-5, 5), "sensitivity": (0.4, 0.7)},
            "high_impedance": {"position_range": (5, 15), "sensitivity": (0.1, 0.4)}
        }
    
    def compare_zones(self) -> Dict[str, Any]:
        """Compare different environmental zones"""
        print("🌍 Starting Zone Comparison Analysis")
        print("=" * 50)
        
        zone_results = {}
        
        for zone_name, zone_config in self.zones.items():
            print(f"🔬 Testing {zone_name} zone...")
            result = self.test_zone(zone_name, zone_config)
            zone_results[zone_name] = result
        
        # Analyze differences
        analysis = self.analyze_zone_differences(zone_results)
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"zone_comparison_results_{timestamp}.json"
        
        results_dir = Path("/home/jonat/ai-stack/genomic_results")
        results_dir.mkdir(exist_ok=True)
        
        with open(results_dir / filename, 'w') as f:
            json.dump({
                "zone_results": zone_results,
                "analysis": analysis,
                "timestamp": datetime.now().isoformat()
            }, f, indent=2)
        
        print(f"📄 Zone comparison results saved to: {filename}")
        return {"status": "success", "zones": zone_results, "analysis": analysis}
    
    def test_zone(self, zone_name: str, zone_config: Dict[str, Any]) -> Dict[str, Any]:
        """Test specific zone"""
        organisms = []
        
        # Create organisms for this zone
        for i in range(30):
            organism_id = f"{zone_name}_org{i+1:03d}"
            position = [
                random.uniform(zone_config["position_range"][0], zone_config["position_range"][1]),
                random.uniform(-10, 10),
                random.uniform(-5, 5)
            ]
            sensitivity = random.uniform(*zone_config["sensitivity"])
            
            organisms.append({
                "organism_id": organism_id,
                "position": position,
                "sensitivity": sensitivity
            })
        
        # Create sensors and collect data
        biasing_potentials = []
        cognitive_enhancements = []
        
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
                        sensor_data = result.get("genomic_sensor", {})
                        biasing_potentials.append(sensor_data.get("biasing_potential", 0))
                        
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
                                biasing_info = bias_result.get("biasing_analysis", {})
                                expression_changes = biasing_info.get("biasing_result", {}).get("expression_changes", {})
                                cognitive_enhancements.append(expression_changes.get("cognitive_processing", 0))
            except:
                pass
        
        return {
            "zone": zone_name,
            "organisms_tested": len(organisms),
            "avg_biasing_potential": statistics.mean(biasing_potentials) if biasing_potentials else 0,
            "avg_cognitive_enhancement": statistics.mean(cognitive_enhancements) if cognitive_enhancements else 0,
            "success_rate": len(biasing_potentials) / len(organisms)
        }
    
    def analyze_zone_differences(self, zone_results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze differences between zones"""
        analysis = {
            "biasing_potential_comparison": {},
            "cognitive_enhancement_comparison": {},
            "success_rate_comparison": {}
        }
        
        for zone_name, result in zone_results.items():
            analysis["biasing_potential_comparison"][zone_name] = result["avg_biasing_potential"]
            analysis["cognitive_enhancement_comparison"][zone_name] = result["avg_cognitive_enhancement"]
            analysis["success_rate_comparison"][zone_name] = result["success_rate"]
        
        return analysis

def main():
    """Main execution function"""
    analyzer = ZoneComparisonAnalysis()
    results = analyzer.compare_zones()
    
    print("
🚀 Zone Comparison Analysis Completed!")

if __name__ == "__main__":
    main()
