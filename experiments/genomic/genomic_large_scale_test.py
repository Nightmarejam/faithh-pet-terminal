#!/usr/bin/env python3
"""
Genomic Large-Scale Testing Experiment
Phase 1: Test 100+ genomic sensors across different positions
Measure cognitive enhancement and validate statistical significance
"""

import json
import time
import requests
import statistics
from typing import List, Dict, Any
import random

class GenomicLargeScaleExperiment:
    """Large-scale genomic impedance reading experiment"""
    
    def __init__(self, backend_url="http://localhost:5557"):
        self.backend_url = backend_url
        self.results = []
        self.organisms = []
        
    def create_test_organisms(self, count: int = 100) -> List[Dict[str, Any]]:
        """Create test organisms across different positions"""
        organisms = []
        
        for i in range(count):
            organism_id = f"test_organism_{i+1:03d}"
            
            # Generate diverse positions across 3D space
            x = random.uniform(-10, 10)
            y = random.uniform(-10, 10) 
            z = random.uniform(-5, 5)
            
            # Vary sensitivity levels
            sensitivity = random.uniform(0.3, 1.0)
            
            organism = {
                "organism_id": organism_id,
                "position": [x, y, z],
                "sensitivity": sensitivity
            }
            
            organisms.append(organism)
            
        return organisms
    
    def create_genomic_sensors(self, organisms: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create genomic sensors for all organisms"""
        results = {"successful": 0, "failed": 0, "sensors": []}
        
        for organism in organisms:
            try:
                response = requests.post(
                    f"{self.backend_url}/api/genomic/impedance-sensor",
                    json=organism,
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        results["successful"] += 1
                        results["sensors"].append({
                            "organism_id": organism["organism_id"],
                            "position": organism["position"],
                            "sensitivity": organism["sensitivity"],
                            "biasing_potential": data["genomic_sensor"]["biasing_potential"],
                            "impedance_readings": data["genomic_sensor"]["readings"],
                            "detected_patterns": data["genomic_sensor"]["detected_patterns"]
                        })
                    else:
                        results["failed"] += 1
                else:
                    results["failed"] += 1
                    
            except Exception as e:
                print(f"Error creating sensor for {organism['organism_id']}: {e}")
                results["failed"] += 1
        
        return results
    
    def apply_genomic_biasing(self, sensors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Apply genomic biasing to all sensors"""
        results = {"successful": 0, "failed": 0, "biasing_results": []}
        
        # Test genome sequences
        test_genomes = [
            "ATGCGTAC" * 2000,  # 16,000 base pairs
            "GCTAGCTA" * 1800,  # 14,400 base pairs
            "CGATCGAT" * 1600,  # 12,800 base pairs
        ]
        
        for sensor in sensors:
            try:
                # Select random test genome
                original_genome = random.choice(test_genomes)
                biasing_strength = 0.7
                
                bias_request = {
                    "organism_id": sensor["organism_id"],
                    "original_genome": original_genome,
                    "biasing_strength": biasing_strength
                }
                
                response = requests.post(
                    f"{self.backend_url}/api/genomic/biasing-analysis",
                    json=bias_request,
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        results["successful"] += 1
                        results["biasing_results"].append({
                            "organism_id": sensor["organism_id"],
                            "biasing_result": data["biasing_analysis"]["biasing_result"],
                            "genomic_bias": data["biasing_analysis"]["genomic_bias"],
                            "sensor_readings": data["biasing_analysis"]["sensor_readings"]
                        })
                    else:
                        results["failed"] += 1
                else:
                    results["failed"] += 1
                    
            except Exception as e:
                print(f"Error applying biasing for {sensor['organism_id']}: {e}")
                results["failed"] += 1
        
        return results
    
    def analyze_results(self, sensors: List[Dict[str, Any]], biasing_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze experimental results"""
        analysis = {
            "sensor_analysis": {},
            "biasing_analysis": {},
            "cognitive_enhancement": {},
            "statistical_significance": {}
        }
        
        # Sensor Analysis
        if sensors:
            biasing_potentials = [s["biasing_potential"] for s in sensors]
            internal_impedances = [s["impedance_readings"]["internal_impedance"] for s in sensors]
            external_impedances = [s["impedance_readings"]["external_impedance"] for s in sensors]
            combined_impedances = [s["impedance_readings"]["combined_impedance"] for s in sensors]
            
            analysis["sensor_analysis"] = {
                "total_sensors": len(sensors),
                "avg_biasing_potential": statistics.mean(biasing_potentials),
                "median_biasing_potential": statistics.median(biasing_potentials),
                "std_biasing_potential": statistics.stdev(biasing_potentials) if len(biasing_potentials) > 1 else 0,
                "avg_internal_impedance": statistics.mean(internal_impedances),
                "avg_external_impedance": statistics.mean(external_impedances),
                "avg_combined_impedance": statistics.mean(combined_impedances),
                "high_biasing_count": len([bp for bp in biasing_potentials if bp > 0.5]),
                "low_biasing_count": len([bp for bp in biasing_potentials if bp < 0.2])
            }
        
        # Biasing Analysis
        if biasing_results:
            mutations_applied = [br["biasing_result"]["mutations_applied"] for br in biasing_results]
            fidelity_scores = [br["biasing_result"]["fidelity_score"] for br in biasing_results]
            biasing_strengths = [br["biasing_result"]["biasing_strength"] for br in biasing_results]
            
            analysis["biasing_analysis"] = {
                "total_biasing_results": len(biasing_results),
                "avg_mutations_applied": statistics.mean(mutations_applied),
                "avg_fidelity_score": statistics.mean(fidelity_scores),
                "avg_biasing_strength": statistics.mean(biasing_strengths),
                "high_fidelity_count": len([fs for fs in fidelity_scores if fs > 0.9]),
                "high_biasing_count": len([bs for bs in biasing_strengths if bs > 0.1])
            }
        
        # Cognitive Enhancement Analysis
        if biasing_results:
            cognitive_processing = []
            mathematical_cognition = []
            pattern_recognition = []
            
            for br in biasing_results:
                expression_changes = br["biasing_result"]["expression_changes"]
                cognitive_processing.append(expression_changes.get("cognitive_processing", 0))
                mathematical_cognition.append(expression_changes.get("mathematical_cognition", 0))
                pattern_recognition.append(expression_changes.get("pattern_recognition", 0))
            
            analysis["cognitive_enhancement"] = {
                "avg_cognitive_processing": statistics.mean(cognitive_processing),
                "avg_mathematical_cognition": statistics.mean(mathematical_cognition),
                "avg_pattern_recognition": statistics.mean(pattern_recognition),
                "cognitive_enhancement_count": len([cp for cp in cognitive_processing if cp > 0.1]),
                "mathematical_enhancement_count": len([mc for mc in mathematical_cognition if mc > 0.01])
            }
        
        # Statistical Significance
        if sensors and biasing_results:
            # Correlation between biasing potential and cognitive enhancement
            biasing_potentials = [s["biasing_potential"] for s in sensors]
            cognitive_enhancements = [br["biasing_result"]["expression_changes"].get("cognitive_processing", 0) for br in biasing_results]
            
            if len(biasing_potentials) > 1 and len(cognitive_enhancements) > 1:
                correlation = self._calculate_correlation(biasing_potentials, cognitive_enhancements)
                analysis["statistical_significance"] = {
                    "biasing_potential_cognitive_correlation": correlation,
                    "significant_correlation": abs(correlation) > 0.3,
                    "sample_size": len(biasing_potentials)
                }
        
        return analysis
    
    def _calculate_correlation(self, x_values: List[float], y_values: List[float]) -> float:
        """Calculate correlation coefficient"""
        if len(x_values) != len(y_values) or len(x_values) < 2:
            return 0.0
        
        n = len(x_values)
        sum_x = sum(x_values)
        sum_y = sum(y_values)
        sum_xy = sum(x * y for x, y in zip(x_values, y_values))
        sum_x2 = sum(x * x for x in x_values)
        sum_y2 = sum(y * y for y in y_values)
        
        numerator = n * sum_xy - sum_x * sum_y
        denominator = ((n * sum_x2 - sum_x ** 2) * (n * sum_y2 - sum_y ** 2)) ** 0.5
        
        if denominator == 0:
            return 0.0
        
        return numerator / denominator
    
    def run_experiment(self, organism_count: int = 100) -> Dict[str, Any]:
        """Run the complete large-scale experiment"""
        print(f"🧬 Starting Genomic Large-Scale Experiment with {organism_count} organisms")
        
        # Step 1: Create test organisms
        print("📝 Creating test organisms...")
        organisms = self.create_test_organisms(organism_count)
        print(f"✅ Created {len(organisms)} test organisms")
        
        # Step 2: Create genomic sensors
        print("🔬 Creating genomic sensors...")
        sensor_results = self.create_genomic_sensors(organisms)
        print(f"✅ Sensors created: {sensor_results['successful']} successful, {sensor_results['failed']} failed")
        
        # Step 3: Apply genomic biasing
        print("🧬 Applying genomic biasing...")
        biasing_results = self.apply_genomic_biasing(sensor_results["sensors"])
        print(f"✅ Biasing applied: {biasing_results['successful']} successful, {biasing_results['failed']} failed")
        
        # Step 4: Analyze results
        print("📊 Analyzing results...")
        analysis = self.analyze_results(sensor_results["sensors"], biasing_results["biasing_results"])
        print("✅ Analysis complete")
        
        # Step 5: Generate report
        experiment_report = {
            "experiment_metadata": {
                "timestamp": time.time(),
                "organism_count": organism_count,
                "backend_url": self.backend_url,
                "success_rate": {
                    "sensor_creation": sensor_results["successful"] / len(organisms),
                    "biasing_application": biasing_results["successful"] / len(sensor_results["sensors"]) if sensor_results["sensors"] else 0
                }
            },
            "sensor_results": sensor_results,
            "biasing_results": biasing_results,
            "analysis": analysis
        }
        
        return experiment_report
    
    def save_results(self, experiment_report: Dict[str, Any], filename: str = None):
        """Save experiment results to file"""
        if filename is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"genomic_large_scale_results_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(experiment_report, f, indent=2)
            print(f"✅ Results saved to {filename}")
            return filename
        except Exception as e:
            print(f"❌ Failed to save results: {e}")
            return None

def main():
    """Main experiment runner"""
    experiment = GenomicLargeScaleExperiment()
    
    try:
        # Run experiment with 100 organisms
        results = experiment.run_experiment(organism_count=100)
        
        # Save results
        filename = experiment.save_results(results)
        
        # Print summary
        analysis = results["analysis"]
        print("\n" + "="*60)
        print("🧬 GENOMIC LARGE-SCALE EXPERIMENT RESULTS")
        print("="*60)
        
        if "sensor_analysis" in analysis:
            sa = analysis["sensor_analysis"]
            print(f"📊 Sensor Analysis:")
            print(f"   Total Sensors: {sa['total_sensors']}")
            print(f"   Avg Biasing Potential: {sa['avg_biasing_potential']:.3f}")
            print(f"   High Biasing Count: {sa['high_biasing_count']}")
            print(f"   Low Biasing Count: {sa['low_biasing_count']}")
        
        if "biasing_analysis" in analysis:
            ba = analysis["biasing_analysis"]
            print(f"\n🧬 Biasing Analysis:")
            print(f"   Total Results: {ba['total_biasing_results']}")
            print(f"   Avg Mutations Applied: {ba['avg_mutations_applied']:.1f}")
            print(f"   Avg Fidelity Score: {ba['avg_fidelity_score']:.3f}")
            print(f"   High Fidelity Count: {ba['high_fidelity_count']}")
        
        if "cognitive_enhancement" in analysis:
            ce = analysis["cognitive_enhancement"]
            print(f"\n🧠 Cognitive Enhancement:")
            print(f"   Avg Cognitive Processing: {ce['avg_cognitive_processing']:.3f}")
            print(f"   Avg Mathematical Cognition: {ce['avg_mathematical_cognition']:.3f}")
            print(f"   Avg Pattern Recognition: {ce['avg_pattern_recognition']:.3f}")
            print(f"   Cognitive Enhancement Count: {ce['cognitive_enhancement_count']}")
        
        if "statistical_significance" in analysis:
            ss = analysis["statistical_significance"]
            print(f"\n📈 Statistical Significance:")
            print(f"   Biasing-Cognitive Correlation: {ss['biasing_potential_cognitive_correlation']:.3f}")
            print(f"   Significant Correlation: {ss['significant_correlation']}")
            print(f"   Sample Size: {ss['sample_size']}")
        
        print("="*60)
        print(f"📄 Full results saved to: {filename}")
        print("🚀 Experiment completed successfully!")
        
    except Exception as e:
        print(f"❌ Experiment failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()