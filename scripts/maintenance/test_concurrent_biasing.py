#!/usr/bin/env python3
"""
Concurrent Genomic Biasing Test
Tests the fixed race condition in genomic biasing
"""

import json
import time
import requests
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

class ConcurrentBiasingTest:
    """Test concurrent genomic biasing operations"""
    
    def __init__(self, backend_url="http://localhost:5557"):
        self.backend_url = backend_url
        self.results = []
    
    def test_concurrent_biasing(self, concurrent_requests=10):
        """Test concurrent genomic biasing operations"""
        print("🧪 Testing Concurrent Genomic Biasing Operations")
        print(f"📊 Concurrent Requests: {concurrent_requests}")
        print("=" * 60)
        
        start_time = time.time()
        
        # Test concurrent sensor creation and biasing
        with ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
            futures = []
            
            for i in range(concurrent_requests):
                organism_id = f"concurrent_test_{i+1:03d}"
                
                # Create sensor and biasing in parallel
                sensor_future = executor.submit(
                    self.create_sensor_and_biasing,
                    organism_id,
                    i + 1
                )
                futures.append(sensor_future)
            
            # Wait for all to complete
            for future in as_completed(futures):
                try:
                    result = future.result()
                    self.results.append(result)
                except Exception as e:
                    self.results.append({
                        "success": False,
                        "error": str(e),
                        "timestamp": datetime.now().isoformat()
                    })
        
        total_time = time.time() - start_time
        
        # Analyze results
        successful_biasing = len([r for r in self.results if r.get("biasing_success", False)])
        successful_sensors = len([r for r in self.results if r.get("sensor_success", False)])
        
        print(f"\n📊 CONCURRENT TEST RESULTS")
        print(f"⏱️ Total Time: {total_time:.2f}s")
        print(f"📈 Total Requests: {len(self.results)}")
        print(f"✅ Successful Sensors: {successful_sensors}/{concurrent_requests} ({successful_sensors/concurrent_requests:.1%})")
        print(f"✅ Successful Biasing: {successful_biasing}/{concurrent_requests} ({successful_biasing/concurrent_requests:.1%})")
        
        # Check for race condition
        if successful_biasing == concurrent_requests:
            print("🎉 RACE CONDITION FIXED: All biasing operations successful!")
        else:
            print("❌ RACE CONDITION STILL EXISTS: Some biasing operations failed")
        
        return {
            "total_requests": concurrent_requests,
            "successful_sensors": successful_sensors,
            "successful_biasing": successful_biasing,
            "success_rate": successful_biasing / concurrent_requests,
            "total_time": total_time,
            "race_condition_fixed": successful_biasing == concurrent_requests
        }
    
    def create_sensor_and_biasing(self, organism_id, index):
        """Create sensor and apply biasing for an organism"""
        result = {
            "organism_id": organism_id,
            "index": index,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            # Create sensor
            sensor_data = {
                "organism_id": organism_id,
                "position": [index * 0.1, index * 0.2, index * 0.05],
                "sensitivity": 0.5 + (index * 0.05)
            }
            
            sensor_response = requests.post(
                f"{self.backend_url}/api/genomic/impedance-sensor",
                json=sensor_data,
                timeout=30
            )
            
            if sensor_response.status_code == 200:
                sensor_result = sensor_response.json()
                result["sensor_success"] = sensor_result.get("success", False)
                result["sensor_response"] = sensor_result
            else:
                result["sensor_success"] = False
                result["sensor_error"] = f"HTTP {sensor_response.status_code}"
                return result
            
            # Apply biasing immediately (this tests the race condition)
            biasing_data = {
                "organism_id": organism_id,
                "original_genome": "ATGCGTACATGCGTACATGCGTACATGCGTACATGCGTACATGCGTACATGCGTAC",
                "biasing_strength": 0.6 + (index * 0.02)
            }
            
            biasing_response = requests.post(
                f"{self.backend_url}/api/genomic/biasing-analysis",
                json=biasing_data,
                timeout=30
            )
            
            if biasing_response.status_code == 200:
                biasing_result = biasing_response.json()
                result["biasing_success"] = biasing_result.get("success", False)
                result["biasing_response"] = biasing_result
            else:
                result["biasing_success"] = False
                result["biasing_error"] = f"HTTP {biasing_response.status_code}"
            
        except Exception as e:
            result["sensor_success"] = False
            result["biasing_success"] = False
            result["error"] = str(e)
        
        return result

def main():
    """Main execution function"""
    tester = ConcurrentBiasingTest()
    
    # Test with different levels of concurrency
    test_levels = [5, 10, 15, 20]
    
    for level in test_levels:
        print(f"\n🔥 Testing with {level} concurrent requests...")
        results = tester.test_concurrent_biasing(concurrent_requests=level)
        
        if results["race_condition_fixed"]:
            print(f"✅ PASS: {level} concurrent requests - Race condition fixed")
        else:
            print(f"❌ FAIL: {level} concurrent requests - Race condition exists")
            break
    
    print("\n🎯 CONCURRENT TESTING COMPLETE")

if __name__ == "__main__":
    main()