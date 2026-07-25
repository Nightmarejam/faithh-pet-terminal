#!/usr/bin/env python3
"""
Genomic Analysis Utilities
Shared utilities for genomic data analysis
"""

import statistics
import json
from typing import List, Dict, Any

class GenomicAnalysisUtils:
    """Shared analysis utilities"""
    
    @staticmethod
    def calculate_correlation(x: List[float], y: List[float]) -> float:
        """Calculate Pearson correlation coefficient"""
        if len(x) != len(y) or len(x) < 2:
            return 0.0
        
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(xi * yi for xi, yi in zip(x, y))
        sum_x2 = sum(xi ** 2 for xi in x)
        sum_y2 = sum(yi ** 2 for yi in y)
        
        numerator = n * sum_xy - sum_x * sum_y
        denominator = ((n * sum_x2 - sum_x ** 2) * (n * sum_y2 - sum_y ** 2)) ** 0.5
        
        if denominator == 0:
            return 0.0
        
        return numerator / denominator
    
    @staticmethod
    def calculate_statistics(data: List[float]) -> Dict[str, float]:
        """Calculate basic statistics"""
        if not data:
            return {}
        
        return {
            "mean": statistics.mean(data),
            "median": statistics.median(data),
            "std_dev": statistics.stdev(data) if len(data) > 1 else 0,
            "min": min(data),
            "max": max(data)
        }
    
    @staticmethod
    def save_results(results: Dict[str, Any], filename: str):
        """Save results to file"""
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)

def main():
    """Main execution function"""
    utils = GenomicAnalysisUtils()
    print("Genomic analysis utilities initialized")

if __name__ == "__main__":
    main()
