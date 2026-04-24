#!/usr/bin/env python3
"""
Multi-Generational Adaptation Experiment
Phase 3: Test genomic biasing across multiple generations
Measure evolutionary advantages and trait inheritance patterns
"""

import json
import time
import requests
import statistics
from typing import List, Dict, Any
import random

class MultiGenerationalAdaptationExperiment:
    """Multi-generational adaptation experiment using genomic biasing"""

    def __init__(self, backend_url="http://localhost:5557"):
        self.backend_url = backend_url
        self.results = []
        self.generations = []
        self.environments = self._define_environments()

    def _define_environments(self) -> List[Dict[str, Any]]:
        """Define evolutionary environments"""
        environments = [
            {
                "name": "Evolutionary_Pressure_High",
                "description": "High evolutionary pressure with rapid environmental change",
                "radiation_level": 0.9,
                "temperature_variance": 0.8,
                "resource_scarcity": 0.8,
                "mutation_pressure": 0.95,
                "selection_strength": 0.9
            },
            {
                "name": "Evolutionary_Pressure_Medium",
                "description": "Medium evolutionary pressure with moderate change",
                "radiation_level": 0.5,
                "temperature_variance": 0.5,
                "resource_scarcity": 0.5,
                "mutation_pressure": 0.6,
                "selection_strength": 0.6
            },
            {
                "name": "Evolutionary_Pressure_Low",
                "description": "Low evolutionary pressure with stable conditions",
                "radiation_level": 0.2,
                "temperature_variance": 0.2,
                "resource_scarcity": 0.3,
                "mutation_pressure": 0.3,
                "selection_strength": 0.3
            },
            {
                "name": "Control_Evolution",
                "description": "Controlled evolutionary conditions",
                "radiation_level": 0.1,
                "temperature_variance": 0.1,
                "resource_scarcity": 0.2,
                "mutation_pressure": 0.2,
                "selection_strength": 0.2
            }
        ]
        return environments

    def create_initial_population(self, population_size: int = 40) -> List[Dict[str, Any]]:
        """Create initial population for multi-generational study"""
        population = []

        for i in range(population_size):
            organism_id = f"gen0_organism_{i+1:03d}"

            # Distribute across evolutionary environments
            env_zone = i % len(self.environments)
            environment = self.environments[env_zone]
            
            # Initial traits - diverse genetic background
            traits = random.choices(
                ["radiation_resistance", "nutrient_efficiency", "thermal_regulation", "general_adaptation"],
                k=random.randint(1, 3)  # 1-3 traits per organism
            )

            organism = {
                "organism_id": organism_id,
                "generation": 0,
                "position": [
                    random.uniform(-10, 10),
                    random.uniform(-10, 10),
                    random.uniform(-5, 5)
                ],
                "sensitivity": random.uniform(0.4, 0.8),
                "environment_zone": env_zone,
                "adaptation_traits": traits,
                "fitness_score": 0.0,
                "parent_ids": [],
                "genomic_lineage": []
            }

            population.append(organism)

        return population

    def apply_evolutionary_pressure(self, organism: Dict[str, Any], generation: int) -> Dict[str, Any]:
        """Apply evolutionary pressure based on generation and environment"""
        environment = self.environments[organism["environment_zone"]]
        
        # Evolutionary pressure increases with generation
        generation_factor = min(1.5, 1.0 + generation * 0.1)
        
        # Calculate pressure based on traits and environment
        pressure_score = 0.0
        trait_matches = 0
        
        for trait in organism["adaptation_traits"]:
            if trait == "radiation_resistance":
                trait_pressure = environment["radiation_level"] * 0.8
                if environment["radiation_level"] > 0.7:
                    trait_matches += 1
            elif trait == "nutrient_efficiency":
                trait_pressure = environment["resource_scarcity"] * 0.7
                if environment["resource_scarcity"] > 0.7:
                    trait_matches += 1
            elif trait == "thermal_regulation":
                trait_pressure = environment["temperature_variance"] * 0.9
                if environment["temperature_variance"] > 0.7:
                    trait_matches += 1
            else:  # general_adaptation
                trait_pressure = (environment["radiation_level"] + environment["resource_scarcity"] + 
                                environment["temperature_variance"]) / 3 * 0.6
                trait_matches += 0.5
            
            pressure_score += trait_pressure
        
        # Average pressure across traits
        if organism["adaptation_traits"]:
            pressure_score /= len(organism["adaptation_traits"])
        
        # Apply generation and selection factors
        evolutionary_pressure = pressure_score * generation_factor * environment["selection_strength"]
        
        return {
            "organism_id": organism["organism_id"],
            "generation": generation,
            "environment": environment["name"],
            "evolutionary_pressure": evolutionary_pressure,
            "trait_matches": trait_matches,
            "selection_pressure": environment["selection_strength"] * generation_factor,
            "adaptation_needed": evolutionary_pressure > 0.6
        }

    def create_genomic_sensors_evolutionary(self, organisms: List[Dict[str, Any]], generation: int) -> Dict[str, Any]:
        """Create genomic sensors with evolutionary pressure"""
        results = {"successful": 0, "failed": 0, "sensors": []}

        for organism in organisms:
            try:
                # Apply evolutionary pressure
                # Add position information to sensor data
                for organism in current_population:
                    if organism["organism_id"] == sensor["organism_id"]:
                        sensor["position"] = organism["position"]
                        sensor["environment_zone"] = organism["environment_zone"]
                        break

                pressure_analysis = self.apply_evolutionary_pressure(organism, generation)

                # Enhanced sensitivity for evolutionary pressure
                evolutionary_sensitivity = organism["sensitivity"] * (1 + pressure_analysis["evolutionary_pressure"] * 0.4)

                sensor_request = {
                    "organism_id": organism["organism_id"],
                    "position": organism["position"],
                    "sensitivity": min(1.0, evolutionary_sensitivity)
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
                            "generation": generation,
                            "environment": pressure_analysis["environment"],
                            "adaptation_traits": organism["adaptation_traits"],
                            "evolutionary_pressure": pressure_analysis,
                            "biasing_potential": data["genomic_sensor"]["biasing_potential"],
                            "impedance_readings": data["genomic_sensor"]["readings"],
                            "detected_patterns": data["genomic_sensor"]["detected_patterns"]
                        })
                    else:
                        results["failed"] += 1
                else:
                    results["failed"] += 1

            except Exception as e:
                print(f"Error creating evolutionary sensor for {organism['organism_id']}: {e}")
                results["failed"] += 1

        return results

    def apply_evolutionary_biasing(self, sensors: List[Dict[str, Any]], generation: int) -> Dict[str, Any]:
        """Apply evolutionary genomic biasing"""
        results = {"successful": 0, "failed": 0, "evolutionary_results": []}

        # Evolutionary genome templates - become more specialized over generations
        base_genomes = {
            "Evolutionary_Pressure_High": "ATGCGTAC" * 2000 + "GCTAGCTA" * 300,
            "Evolutionary_Pressure_Medium": "CGATCGAT" * 1800 + "TACGATCG" * 250,
            "Evolutionary_Pressure_Low": "GCTAGCTA" * 1600 + "ATGCGTAC" * 200,
            "Control_Evolution": "ATGCGTAC" * 1500 + "CGATCGAT" * 200
        }

        for sensor in sensors:
            try:
                environment = sensor["environment"]
                evolutionary_pressure = sensor["evolutionary_pressure"]["evolutionary_pressure"]
                
                # Select and evolve genome based on generation
                base_genome = base_genomes.get(environment, base_genomes["Control_Evolution"])
                
                # Add evolutionary mutations based on generation
                if generation > 0:
                    mutation_count = generation * 50  # More mutations in later generations
                    for _ in range(mutation_count):
                        pos = random.randint(0, len(base_genome) - 1)
                        base_genome = base_genome[:pos] + random.choice("ATCG") + base_genome[pos+1:]
                
                # Evolutionary biasing strength
                biasing_strength = min(0.95, 0.4 + evolutionary_pressure * 0.5 + generation * 0.05)

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
                        
                        # Calculate evolutionary fitness
                        biasing_result = data["biasing_analysis"]["biasing_result"]
                        evolutionary_fitness = self._calculate_evolutionary_fitness(
                            sensor["adaptation_traits"], 
                            biasing_result, 
                            evolutionary_pressure,
                            generation
                        )

                        results["evolutionary_results"].append({
                            "organism_id": sensor["organism_id"],
                            "generation": generation,
                            "environment": environment,
                            "adaptation_traits": sensor["adaptation_traits"],
                            "position": sensor["position"],
                            "environment_zone": sensor.get("environment_zone", 0),
                            "evolutionary_pressure": evolutionary_pressure,
                            "biasing_result": biasing_result,
                            "genomic_bias": data["biasing_analysis"]["genomic_bias"],
                            "evolutionary_fitness": evolutionary_fitness,
                            "reproductive_fitness": evolutionary_fitness * (1 - evolutionary_pressure * 0.2)
                        })
                    else:
                        results["failed"] += 1
                else:
                    results["failed"] += 1

            except Exception as e:
                print(f"Error applying evolutionary biasing for {sensor['organism_id']}: {e}")
                results["failed"] += 1

        return results

    def _calculate_evolutionary_fitness(self, traits: List[str], biasing_result: Dict[str, Any], 
                                      pressure: float, generation: int) -> float:
        """Calculate evolutionary fitness score"""
        expression_changes = biasing_result["expression_changes"]
        
        # Base fitness from trait expression
        trait_fitness = 0.0
        for trait in traits:
            if trait == "radiation_resistance":
                trait_fitness += expression_changes.get("dna_repair", 0) + expression_changes.get("antioxidant", 0)
            elif trait == "nutrient_efficiency":
                trait_fitness += expression_changes.get("metabolic_efficiency", 0) + expression_changes.get("nutrient_assimilation", 0)
            elif trait == "thermal_regulation":
                trait_fitness += expression_changes.get("heat_shock_proteins", 0) + expression_changes.get("membrane_stability", 0)
            else:  # general_adaptation
                trait_fitness += expression_changes.get("cognitive_processing", 0) + expression_changes.get("pattern_recognition", 0)
        
        # Normalize by number of traits
        if traits:
            trait_fitness /= len(traits)
        
        # Evolutionary advantages
        cognitive_bonus = expression_changes.get("cognitive_processing", 0) * 0.3
        generation_bonus = generation * 0.02  # Small bonus for surviving to later generations
        
        # Pressure adjustment
        pressure_adjustment = 1 - (pressure * 0.15)
        
        # Calculate final fitness
        fitness = (trait_fitness + cognitive_bonus + generation_bonus) * pressure_adjustment
        
        return min(1.0, fitness * 2.5)  # Scale to 0-1 range

    def select_next_generation(self, evolutionary_results: List[Dict[str, Any]], 
                              population_size: int = 40) -> List[Dict[str, Any]]:
        """Select organisms for next generation based on fitness"""
        # Sort by reproductive fitness
        sorted_results = sorted(evolutionary_results, key=lambda x: x["reproductive_fitness"], reverse=True)
        
        # Select top performers (80% of population)
        selected_count = int(population_size * 0.8)
        selected = sorted_results[:selected_count]
        
        next_generation = []
        
        for i, organism in enumerate(selected):
            # Create offspring
            offspring_count = 1 if i < selected_count // 2 else 2  # Top performers reproduce more
            
            for j in range(offspring_count):
                offspring_id = f"gen{organism['generation']+1}_offspring_{i+1:03d}_{j+1}"
                
                # Inherit traits with possible mutations
                inherited_traits = organism["adaptation_traits"].copy()
                if random.random() < 0.2:  # 20% chance of trait mutation
                    if random.random() < 0.5 and len(inherited_traits) > 1:
                        # Lose a trait
                        inherited_traits.pop(random.randint(0, len(inherited_traits) - 1))
                    else:
                        # Gain a trait
                        new_trait = random.choice(["radiation_resistance", "nutrient_efficiency", 
                                                 "thermal_regulation", "general_adaptation"])
                        if new_trait not in inherited_traits:
                            inherited_traits.append(new_trait)
                
                # Genetic drift in position
                new_position = [
                    organism["position"][0] + random.uniform(-2, 2),
                    organism["position"][1] + random.uniform(-2, 2),
                    organism["position"][2] + random.uniform(-1, 1)
                ]
                
                offspring = {
                    "organism_id": offspring_id,
                    "generation": organism["generation"] + 1,
                    "position": new_position,
                    "sensitivity": max(0.3, min(1.0, organism["biasing_result"]["fidelity_score"] + random.uniform(-0.1, 0.1))),
                    "environment_zone": organism["environment_zone"],
                    "adaptation_traits": inherited_traits,
                    "fitness_score": 0.0,
                    "parent_ids": [organism["organism_id"]],
                    "genomic_lineage": organism.get("genomic_lineage", []) + [organism["organism_id"]]
                }
                
                next_generation.append(offspring)
        
        # Fill remaining slots with random organisms (immigration)
        while len(next_generation) < population_size:
            immigrant_id = f"gen{organism['generation']+1}_immigrant_{len(next_generation)+1:03d}"
            immigrant = {
                "organism_id": immigrant_id,
                "generation": organism["generation"] + 1,
                "position": [random.uniform(-10, 10), random.uniform(-10, 10), random.uniform(-5, 5)],
                "sensitivity": random.uniform(0.4, 0.8),
                "environment_zone": random.randint(0, len(self.environments) - 1),
                "adaptation_traits": random.choices(
                    ["radiation_resistance", "nutrient_efficiency", "thermal_regulation", "general_adaptation"],
                    k=random.randint(1, 2)
                ),
                "fitness_score": 0.0,
                "parent_ids": [],
                "genomic_lineage": []
            }
            next_generation.append(immigrant)
        
        return next_generation[:population_size]

    def run_multi_generational_experiment(self, generations: int = 5, population_size: int = 40) -> Dict[str, Any]:
        """Run complete multi-generational experiment"""
        print(f"🧬 Starting Multi-Generational Adaptation Experiment")
        print(f"📊 Generations: {generations}, Population Size: {population_size}")

        all_results = {}
        current_population = self.create_initial_population(population_size)
        
        for generation in range(generations):
            print(f"\n🔄 Generation {generation}:")
            
            # Step 1: Create genomic sensors
            print(f"   🔬 Creating genomic sensors...")
            sensor_results = self.create_genomic_sensors_evolutionary(current_population, generation)
            print(f"   ✅ Sensors: {sensor_results['successful']} successful, {sensor_results['failed']} failed")

            # Step 2: Apply evolutionary biasing
            print(f"   🧬 Applying evolutionary biasing...")
            evolutionary_results = self.apply_evolutionary_biasing(sensor_results["sensors"], generation)
            print(f"   ✅ Biasing: {evolutionary_results['successful']} successful, {evolutionary_results['failed']} failed")

            # Step 3: Store generation results
            generation_data = {
                "generation": generation,
                "population_size": len(current_population),
                "sensor_results": sensor_results,
                "evolutionary_results": evolutionary_results,
                "analysis": self.analyze_generation_results(evolutionary_results["evolutionary_results"])
            }
            all_results[f"generation_{generation}"] = generation_data
            
            # Step 4: Select next generation (unless this is the last generation)
            if generation < generations - 1:
                print(f"   🧬 Selecting next generation...")
                current_population = self.select_next_generation(evolutionary_results["evolutionary_results"], population_size)
                print(f"   ✅ Next generation: {len(current_population)} organisms")

        # Final analysis
        print(f"\n📊 Analyzing multi-generational trends...")
        final_analysis = self.analyze_multi_generational_trends(all_results)
        
        experiment_report = {
            "experiment_metadata": {
                "timestamp": time.time(),
                "generations": generations,
                "population_size": population_size,
                "backend_url": self.backend_url,
                "total_organisms_tested": population_size * generations
            },
            "environments": self.environments,
            "generation_results": all_results,
            "multi_generational_analysis": final_analysis
        }

        return experiment_report

    def analyze_generation_results(self, evolutionary_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze results for a single generation"""
        if not evolutionary_results:
            return {}

        fitness_scores = [r["evolutionary_fitness"] for r in evolutionary_results]
        reproductive_fitness = [r["reproductive_fitness"] for r in evolutionary_results]
        evolutionary_pressures = [r["evolutionary_pressure"] for r in evolutionary_results]

        return {
            "avg_evolutionary_fitness": statistics.mean(fitness_scores),
            "avg_reproductive_fitness": statistics.mean(reproductive_fitness),
            "avg_evolutionary_pressure": statistics.mean(evolutionary_pressures),
            "fitness_variance": statistics.stdev(fitness_scores) if len(fitness_scores) > 1 else 0,
            "high_fitness_count": len([f for f in fitness_scores if f > 0.7]),
            "trait_diversity": len(set(tuple(sorted(r["adaptation_traits"])) for r in evolutionary_results))
        }

    def analyze_multi_generational_trends(self, all_results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze trends across all generations"""
        generation_data = []
        
        for gen_key, gen_data in all_results.items():
            if gen_key.startswith("generation_"):
                analysis = gen_data.get("analysis", {})
                generation_data.append({
                    "generation": gen_data["generation"],
                    "avg_fitness": analysis.get("avg_evolutionary_fitness", 0),
                    "avg_reproductive_fitness": analysis.get("avg_reproductive_fitness", 0),
                    "fitness_variance": analysis.get("fitness_variance", 0),
                    "high_fitness_count": analysis.get("high_fitness_count", 0),
                    "trait_diversity": analysis.get("trait_diversity", 0)
                })
        
        # Sort by generation
        generation_data.sort(key=lambda x: x["generation"])
        
        # Calculate trends
        fitness_trend = []
        reproductive_trend = []
        diversity_trend = []
        
        for i in range(1, len(generation_data)):
            prev_fitness = generation_data[i-1]["avg_fitness"]
            curr_fitness = generation_data[i]["avg_fitness"]
            fitness_change = curr_fitness - prev_fitness
            fitness_trend.append(fitness_change)
            
            prev_reproductive = generation_data[i-1]["avg_reproductive_fitness"]
            curr_reproductive = generation_data[i]["avg_reproductive_fitness"]
            reproductive_change = curr_reproductive - prev_reproductive
            reproductive_trend.append(reproductive_change)
            
            prev_diversity = generation_data[i-1]["trait_diversity"]
            curr_diversity = generation_data[i]["trait_diversity"]
            diversity_change = curr_diversity - prev_diversity
            diversity_trend.append(diversity_change)
        
        return {
            "generation_summary": generation_data,
            "fitness_trend": {
                "avg_change": statistics.mean(fitness_trend) if fitness_trend else 0,
                "trend_direction": "improving" if statistics.mean(fitness_trend) > 0 else "declining" if fitness_trend else "stable",
                "total_improvement": generation_data[-1]["avg_fitness"] - generation_data[0]["avg_fitness"] if len(generation_data) > 1 else 0
            },
            "reproductive_trend": {
                "avg_change": statistics.mean(reproductive_trend) if reproductive_trend else 0,
                "trend_direction": "improving" if statistics.mean(reproductive_trend) > 0 else "declining" if reproductive_trend else "stable"
            },
            "diversity_trend": {
                "avg_change": statistics.mean(diversity_trend) if diversity_trend else 0,
                "trend_direction": "increasing" if statistics.mean(diversity_trend) > 0 else "decreasing" if diversity_trend else "stable"
            },
            "evolutionary_success": {
                "overall_improvement": generation_data[-1]["avg_fitness"] - generation_data[0]["avg_fitness"] if len(generation_data) > 1 else 0,
                "generational_improvement_rate": statistics.mean(fitness_trend) if fitness_trend else 0,
                "peak_fitness_generation": max(generation_data, key=lambda x: x["avg_fitness"])["generation"] if generation_data else 0
            }
        }

    def save_results(self, experiment_report: Dict[str, Any], filename: str = None):
        """Save experiment results to file"""
        if filename is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"multi_generational_results_{timestamp}.json"

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
    experiment = MultiGenerationalAdaptationExperiment()

    try:
        # Run multi-generational experiment
        results = experiment.run_multi_generational_experiment(generations=5, population_size=40)

        # Save results
        filename = experiment.save_results(results)

        # Print summary
        multi_analysis = results["multi_generational_analysis"]
        print("\n" + "="*70)
        print("🧬 MULTI-GENERATIONAL ADAPTATION EXPERIMENT RESULTS")
        print("="*70)

        if "evolutionary_success" in multi_analysis:
            es = multi_analysis["evolutionary_success"]
            print(f"🧬 Evolutionary Success:")
            print(f"   Overall Improvement: {es['overall_improvement']:.3f}")
            print(f"   Generational Improvement Rate: {es['generational_improvement_rate']:.3f}")
            print(f"   Peak Fitness Generation: {es['peak_fitness_generation']}")

        if "fitness_trend" in multi_analysis:
            ft = multi_analysis["fitness_trend"]
            print(f"\n📈 Fitness Trend:")
            print(f"   Average Change: {ft['avg_change']:.3f}")
            print(f"   Trend Direction: {ft['trend_direction']}")
            print(f"   Total Improvement: {ft['total_improvement']:.3f}")

        if "reproductive_trend" in multi_analysis:
            rt = multi_analysis["reproductive_trend"]
            print(f"\n🧬 Reproductive Trend:")
            print(f"   Average Change: {rt['avg_change']:.3f}")
            print(f"   Trend Direction: {rt['trend_direction']}")

        if "diversity_trend" in multi_analysis:
            dt = multi_analysis["diversity_trend"]
            print(f"\n🌿 Diversity Trend:")
            print(f"   Average Change: {dt['avg_change']:.3f}")
            print(f"   Trend Direction: {dt['trend_direction']}")

        # Generation-by-generation summary
        if "generation_summary" in multi_analysis:
            print(f"\n📊 Generation Summary:")
            for gen in multi_analysis["generation_summary"]:
                print(f"   Gen {gen['generation']}: Fitness={gen['avg_fitness']:.3f}, "
                      f"Reproductive={gen['avg_reproductive_fitness']:.3f}, "
                      f"Diversity={gen['trait_diversity']}")

        print("="*70)
        print(f"📄 Full results saved to: {filename}")
        print("🚀 Multi-generational adaptation experiment completed successfully!")

    except Exception as e:
        print(f"❌ Experiment failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()