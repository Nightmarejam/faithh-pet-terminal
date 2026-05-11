#!/usr/bin/env python3
"""
Genomic Experiments Configuration Management
Centralized configuration for all genomic experiments
"""

class GenomicConfig:
    """Centralized configuration management"""
    
    def __init__(self):
        self.backend_url = "http://localhost:5557"
        self.results_dir = "/home/jonat/ai-stack/genomic_results"
        self.experiments_dir = "/home/jonat/ai-stack/experiments/genomic"
        
        # Default configurations
        self.large_scale_config = {
            "organism_count": 200,
            "environmental_zones": 3,
            "statistical_tests": ["correlation", "significance", "distribution"]
        }
        
        self.environmental_config = {
            "environments": 3,
            "organisms_per_env": 50,
            "adaptation_cycles": 10
        }
        
        self.multi_gen_config = {
            "generations": 5,
            "population_size": 40,
            "selection_pressure": 0.7
        }
    
    def get_config(self, experiment_type: str) -> Dict[str, Any]:
        """Get configuration for experiment type"""
        configs = {
            "large_scale": self.large_scale_config,
            "environmental": self.environmental_config,
            "multi_generational": self.multi_gen_config
        }
        return configs.get(experiment_type, {})

def main():
    """Main execution function"""
    config = GenomicConfig()
    print("Genomic configuration management initialized")
    print(f"Backend URL: {config.backend_url}")
    print(f"Results directory: {config.results_dir}")

if __name__ == "__main__":
    main()
