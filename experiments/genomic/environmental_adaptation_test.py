#!/usr/bin/env python3
"""
Environmental Adaptation Experiment
Phase 2: Test genomic biasing under varying environmental conditions
Measure adaptation rates and survival advantages in different environments
"""

import json
import time
import requests
import statistics
from typing import List, Dict, Any
import random

class EnvironmentalAdaptationExperiment:
    """Environmental adaptation experiment using genomic biasing"""

    def __init__(self, backend_url="http://localhost:5557"):
        self.backend_url = backend_url
        self.results = []
        self.environments = self._define_environments()

    def _define_environments(self) -> List[Dict[str, Any]]:
        """Define different environmental conditions"""
        environments = [
            {
                "name": "High_Radiation",
                "description": "High radiation environment with strong stellar interference",
                "radiation_level": 0.8,
                "temperature_variance": 0.6,
                "resource_scarcity": 0.7,
                "mutation_pressure": 0.9
            },
            {
                "name": "Low_Nutrient",
                "description": "Low nutrient environment requiring efficient metabolism",
                "radiation_level": 0.2,
                "temperature_variance": 0.3,
                "resource_scarcity": 0.9,
                "mutation_pressure": 0.4
            },
            {
                "name": "Variable_Temperature",
                "description": "Highly variable temperature environment",
                "radiation_level": 0.4,
                "temperature_variance": 0.9,
                "resource_scarcity": 0.5,
                "mutation_pressure": 0.6
            },
            {
                "name": "Controlled",
                "description": "Stable laboratory conditions",
                "radiation_level": 0.1,
                "temperature_variance": 0.1,
                "resource_scarcity": 0.2,
                "mutation_pressure": 0.2
            }
        ]
        return environments

    def create_adaptive_organisms(self, count: int = 50) -> List[Dict[str, Any]]:
        """Create organisms with enhanced adaptive capabilities"""
        organisms = []

        for i in range(count):
            organism_id = f"adaptive_organism_{i+1:03d}"

            # Position organisms in different environmental zones
            env_zone = i % len(self.environments)
            base_position = [
                random.uniform(-5 + env_zone * 3, -3 + env_zone * 3),
                random.uniform(-5, 5),
                random.uniform(-2, 2)
            ]

            # Higher sensitivity for adaptation experiments
            sensitivity = random.uniform(0.6, 1.0)

            organism = {
                "organism_id": organism_id,
                "position": base_position,
                "sensitivity": sensitivity,
                "environment_zone": env_zone,
                "adaptation_trait": random.choice(["radiation_resistance", "nutrient_efficiency", "thermal_regulation", "general_adaptation"])
            }

            organisms.append(organism)

        return organisms

    def apply_environmental_pressure(self, organism: Dict[str, Any], environment: Dict[str, Any]) -> Dict[str, Any]:
        """Apply environmental pressure to organism"""
        pressure_score = 0.0
        survival_factors = []

        # Calculate environmental stress based on organism traits
        if organism["adaptation_trait"] == "radiation_resistance":
            pressure_score = environment["radiation_level"] * 0.8
            survival_factors.append(f"Radiation stress: {environment['radiation_level']:.2f}")
        elif organism["adaptation_trait"] == "nutrient_efficiency":
            pressure_score = environment["resource_scarcity"] * 0.7
            survival_factors.append(f"Nutrient scarcity: {environment['resource_scarcity']:.2f}")
        elif organism["adaptation_trait"] == "thermal_regulation":
            pressure_score = environment["temperature_variance"] * 0.9
            survival_factors.append(f"Temperature variance: {environment['temperature_variance']:.2f}")
        else:  # general_adaptation
            pressure_score = (environment["radiation_level"] + environment["resource_scarcity"] + 
                            environment["temperature_variance"]) / 3 * 0.6
            survival_factors.append(f"General environmental pressure: {pressure_score:.2f}")

        return {
            "organism_id": organism["organism_id"],
            "environment": environment["name"],
            "pressure_score": pressure_score,
            "survival_factors": survival_factors,
            "adaptation_needed": pressure_score > 0.5
        }

    def create_genomic_sensors_with_pressure(self, organisms: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create genomic sensors under environmental pressure"""
        results = {"successful": 0, "failed": 0, "sensors": []}

        for organism in organisms:
            try:
                # Apply environmental pressure
                environment = self.environments[organism["environment_zone"]]
                pressure_analysis = self.apply_environmental_pressure(organism, environment)

                # Create sensor with pressure-influenced parameters
                sensor_request = {
                    "organism_id": organism["organism_id"],
                    "position": organism["position"],
                    "sensitivity": organism["sensitivity"] * (1 + pressure_analysis["pressure_score"] * 0.3)
                }

                response = requests.post(
                    f"{self.backend_url}/api/genomic/impedance-sensor",
                    json=sensor_request,
                    timeout=30
                )

                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        results["successful"] += 1
                        results["sensors"].append({
                            "organism_id": organism["organism_id"],
                            "environment": environment["name"],
                            "adaptation_trait": organism["adaptation_trait"],
                            "pressure_analysis": pressure_analysis,
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

    def apply_adaptive_biasing(self, sensors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Apply adaptive genomic biasing based on environmental pressure"""
        results = {"successful": 0, "failed": 0, "adaptation_results": []}

        # Environment-specific genome templates
        genome_templates = {
            "High_Radiation": "ATGCGTAC" * 1800 + "GCTAGCTA" * 200,  # Radiation-resistant genes
            "Low_Nutrient": "CGATCGAT" * 1600 + "TACGATCG" * 300,  # Efficient metabolism genes
            "Variable_Temperature": "GCTAGCTA" * 1400 + "ATGCGTAC" * 400,  # Thermal regulation genes
            "Controlled": "ATGCGTAC" * 1500 + "CGATCGAT" * 250  # Balanced genome
        }

        for sensor in sensors:
            try:
                environment = sensor["environment"]
                pressure = sensor["pressure_analysis"]["pressure_score"]
                
                # Select environment-specific genome
                base_genome = genome_templates.get(environment, genome_templates["Controlled"])
                
                # Adaptive biasing strength based on pressure
                biasing_strength = min(0.9, 0.3 + pressure * 0.6)

                bias_request = {
                    "organism_id": sensor["organism_id"],
                    "original_genome": base_genome,
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
                        
                        # Calculate adaptation success
                        biasing_result = data["biasing_analysis"]["biasing_result"]
                        adaptation_success = self._calculate_adaptation_success(
                            sensor["adaptation_trait"], 
                            biasing_result, 
                            pressure
                        )

                        results["adaptation_results"].append({
                            "organism_id": sensor["organism_id"],
                            "environment": environment,
                            "adaptation_trait": sensor["adaptation_trait"],
                            "pressure_score": pressure,
                            "biasing_result": biasing_result,
                            "genomic_bias": data["biasing_analysis"]["genomic_bias"],
                            "adaptation_success": adaptation_success,
                            "survival_probability": adaptation_success * (1 - pressure * 0.3)
                        })
                    else:
                        results["failed"] += 1
                else:
                    results["failed"] += 1

            except Exception as e:
                print(f"Error applying adaptive biasing for {sensor['organism_id']}: {e}")
                results["failed"] += 1

        return results

    def _calculate_adaptation_success(self, trait: str, biasing_result: Dict[str, Any], pressure: float) -> float:
        """Calculate adaptation success based on trait and biasing results"""
        expression_changes = biasing_result["expression_changes"]
        
        # Trait-specific adaptation metrics
        if trait == "radiation_resistance":
            # Look for DNA repair and antioxidant gene expression
            success = expression_changes.get("dna_repair", 0) + expression_changes.get("antioxidant", 0)
        elif trait == "nutrient_efficiency":
            # Look for metabolic efficiency genes
            success = expression_changes.get("metabolic_efficiency", 0) + expression_changes.get("nutrient_assimilation", 0)
        elif trait == "thermal_regulation":
            # Look for heat shock and membrane stability genes
            success = expression_changes.get("heat_shock_proteins", 0) + expression_changes.get("membrane_stability", 0)
        else:  # general_adaptation
            # Overall cognitive and adaptive capacity
            success = expression_changes.get("cognitive_processing", 0) + expression_changes.get("pattern_recognition", 0)
        
        # Adjust for environmental pressure
        pressure_adjustment = 1 - (pressure * 0.2)
        
        return min(1.0, success * pressure_adjustment * 2)

    def analyze_adaptation_results(self, sensors: List[Dict[str, Any]], adaptation_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze environmental adaptation results"""
        analysis = {
            "environmental_analysis": {},
            "trait_analysis": {},
            "adaptation_success": {},
            "survival_analysis": {},
            "statistical_significance": {}
        }

        # Group results by environment
        env_groups = {}
        trait_groups = {}
        
        for result in adaptation_results:
            env = result["environment"]
            trait = result["adaptation_trait"]
            
            if env not in env_groups:
                env_groups[env] = []
            env_groups[env].append(result)
            
            if trait not in trait_groups:
                trait_groups[trait] = []
            trait_groups[trait].append(result)

        # Environmental Analysis
        for env, results in env_groups.items():
            adaptation_scores = [r["adaptation_success"] for r in results]
            survival_probs = [r["survival_probability"] for r in results]
            pressures = [r["pressure_score"] for r in results]

            analysis["environmental_analysis"][env] = {
                "sample_size": len(results),
                "avg_adaptation_success": statistics.mean(adaptation_scores),
                "avg_survival_probability": statistics.mean(survival_probs),
                "avg_pressure": statistics.mean(pressures),
                "high_survival_count": len([sp for sp in survival_probs if sp > 0.7]),
                "adaptation_variance": statistics.stdev(adaptation_scores) if len(adaptation_scores) > 1 else 0
            }

        # Trait Analysis
        for trait, results in trait_groups.items():
            adaptation_scores = [r["adaptation_success"] for r in results]
            survival_probs = [r["survival_probability"] for r in results]

            analysis["trait_analysis"][trait] = {
                "sample_size": len(results),
                "avg_adaptation_success": statistics.mean(adaptation_scores),
                "avg_survival_probability": statistics.mean(survival_probs),
                "specialization_bonus": statistics.mean(adaptation_scores) - 0.5,  # Compare to baseline
                "trait_effectiveness": len([as_ for as_ in adaptation_scores if as_ > 0.6]) / len(adaptation_scores)
            }

        # Overall Adaptation Success
        if adaptation_results:
            all_adaptation_scores = [r["adaptation_success"] for r in adaptation_results]
            all_survival_probs = [r["survival_probability"] for r in adaptation_results]
            all_pressures = [r["pressure_score"] for r in adaptation_results]

            analysis["adaptation_success"] = {
                "total_organisms": len(adaptation_results),
                "avg_adaptation_success": statistics.mean(all_adaptation_scores),
                "avg_survival_probability": statistics.mean(all_survival_probs),
                "avg_environmental_pressure": statistics.mean(all_pressures),
                "successful_adaptations": len([as_ for as_ in all_adaptation_scores if as_ > 0.5]),
                "high_survival_organisms": len([sp for sp in all_survival_probs if sp > 0.7]),
                "adaptation_rate": len([as_ for as_ in all_adaptation_scores if as_ > 0.5]) / len(all_adaptation_scores)
            }

        # Statistical Significance
        if len(env_groups) > 1:
            # Compare adaptation across environments
            env_adaptations = [statistics.mean([r["adaptation_success"] for r in results]) for results in env_groups.values()]
            if len(env_adaptations) > 1:
                analysis["statistical_significance"] = {
                    "environmental_variance": statistics.stdev(env_adaptations),
                    "significant_environmental_effect": statistics.stdev(env_adaptations) > 0.1,
                    "environment_count": len(env_groups)
                }

        return analysis

    def run_experiment(self, organism_count: int = 50) -> Dict[str, Any]:
        """Run the complete environmental adaptation experiment"""
        print(f"🌍 Starting Environmental Adaptation Experiment with {organism_count} organisms")

        # Step 1: Create adaptive organisms
        print("🧬 Creating adaptive organisms...")
        organisms = self.create_adaptive_organisms(organism_count)
        print(f"✅ Created {len(organisms)} adaptive organisms")

        # Step 2: Create genomic sensors under environmental pressure
        print("🔬 Creating genomic sensors with environmental pressure...")
        sensor_results = self.create_genomic_sensors_with_pressure(organisms)
        print(f"✅ Sensors created: {sensor_results['successful']} successful, {sensor_results['failed']} failed")

        # Step 3: Apply adaptive biasing
        print("🧬 Applying adaptive genomic biasing...")
        adaptation_results = self.apply_adaptive_biasing(sensor_results["sensors"])
        print(f"✅ Adaptations applied: {adaptation_results['successful']} successful, {adaptation_results['failed']} failed")

        # Step 4: Analyze results
        print("📊 Analyzing adaptation results...")
        analysis = self.analyze_adaptation_results(sensor_results["sensors"], adaptation_results["adaptation_results"])
        print("✅ Analysis complete")

        # Step 5: Generate report
        experiment_report = {
            "experiment_metadata": {
                "timestamp": time.time(),
                "organism_count": organism_count,
                "environments_tested": len(self.environments),
                "backend_url": self.backend_url,
                "success_rate": {
                    "sensor_creation": sensor_results["successful"] / len(organisms),
                    "adaptation_application": adaptation_results["successful"] / len(sensor_results["sensors"]) if sensor_results["sensors"] else 0
                }
            },
            "environments": self.environments,
            "sensor_results": sensor_results,
            "adaptation_results": adaptation_results,
            "analysis": analysis
        }

        return experiment_report

    def save_results(self, experiment_report: Dict[str, Any], filename: str = None):
        """Save experiment results to file"""
        if filename is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"environmental_adaptation_results_{timestamp}.json"

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
    experiment = EnvironmentalAdaptationExperiment()

    try:
        # Run experiment with 50 organisms
        results = experiment.run_experiment(organism_count=50)

        # Save results
        filename = experiment.save_results(results)

        # Print summary
        analysis = results["analysis"]
        print("\n" + "="*60)
        print("🌍 ENVIRONMENTAL ADAPTATION EXPERIMENT RESULTS")
        print("="*60)

        if "adaptation_success" in analysis:
            ad = analysis["adaptation_success"]
            print(f"🌍 Overall Adaptation Success:")
            print(f"   Total Organisms: {ad['total_organisms']}")
            print(f"   Avg Adaptation Success: {ad['avg_adaptation_success']:.3f}")
            print(f"   Avg Survival Probability: {ad['avg_survival_probability']:.3f}")
            print(f"   Successful Adaptations: {ad['successful_adaptations']}")
            print(f"   Adaptation Rate: {ad['adaptation_rate']:.2%}")

        if "environmental_analysis" in analysis:
            print(f"\n🏞️ Environmental Analysis:")
            for env, data in analysis["environmental_analysis"].items():
                print(f"   {env}:")
                print(f"     Sample Size: {data['sample_size']}")
                print(f"     Avg Adaptation: {data['avg_adaptation_success']:.3f}")
                print(f"     High Survival Count: {data['high_survival_count']}")

        if "trait_analysis" in analysis:
            print(f"\n🧬 Trait Analysis:")
            for trait, data in analysis["trait_analysis"].items():
                print(f"   {trait}:")
                print(f"     Sample Size: {data['sample_size']}")
                print(f"     Avg Adaptation: {data['avg_adaptation_success']:.3f}")
                print(f"     Trait Effectiveness: {data['trait_effectiveness']:.2%}")

        if "statistical_significance" in analysis:
            ss = analysis["statistical_significance"]
            print(f"\n📈 Statistical Significance:")
            print(f"   Environmental Variance: {ss['environmental_variance']:.3f}")
            print(f"   Significant Environmental Effect: {ss['significant_environmental_effect']}")
            print(f"   Environment Count: {ss['environment_count']}")

        print("="*60)
        print(f"📄 Full results saved to: {filename}")
        print("🚀 Environmental adaptation experiment completed successfully!")

    except Exception as e:
        print(f"❌ Experiment failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()