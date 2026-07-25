#!/usr/bin/env python3
"""
Detailed Concurrent Genomic Biasing Test
Tests the fixed race condition with detailed error analysis
"""

import json
import time
import requests
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

class DetailedConcurrentBiasingTest:
    """Test concurrent genomic biasing operations with detailed analysis"""
    
    def __init__(self, backend_url="http://localhost:5557"):
        self.backend_url = backend_url
        self.results = []
    
    def test_concurrent_biasing_detailed(self, concurrent_requests=10):
        """Test concurrent genomic biasing operations with detailed analysis"""
        print("🧪 Detailed Concurrent Genomic Biasing Test")
        print(f"📊 Concurrent Requests: {concurrent_requests}")
        print("=" * 60)
        
        start_time = time.time()
        
        # Test concurrent sensor creation and biasing
        with ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
            futures = []
            
            for i in range(concurrent_requests):
                organism_id = f"detailed_test_{i+1:03d}"
                
                # Create sensor and biasing in parallel
                sensor_future = executor.submit(
                    self.create_sensor_and_biasing_detailed,
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
        
        print(f"\n📊 DETAILED TEST RESULTS")
        print(f"⏱️ Total Time: {total_time:.2f}s")
        print(f"📈 Total Requests: {len(self.results)}")
        print(f"✅ Successful Sensors: {successful_sensors}/{concurrent_requests} ({successful_sensors/concurrent_requests:.1%})")
        print(f"✅ Successful Biasing: {successful_biasing}/{concurrent_requests} ({successful_biasing/concurrent_requests:.1%})")
        
        # Show failed operations
        failed_operations = [r for r in self.results if not r.get("biasing_success", False)]
        if failed_operations:
            print(f"\n❌ FAILED OPERATIONS ({len(failed_operations)}):")
            for i, failed in enumerate(failed_operations[:5]):  # Show first 5
                print(f"   {i+1}. {failed.get('organism_id', 'unknown')}: {failed.get('biasing_error', 'Unknown error')}")
        
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
            "race_condition_fixed": successful_biasing == concurrent_requests,
            "failed_operations": failed_operations
        }
    
    def create_sensor_and_biasing_detailed(self, organism_id, index):
        """Create sensor and apply biasing for an organism with detailed logging"""
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
                
                if not sensor_result.get("success", False):
                    result["sensor_error"] = sensor_result.get("error", "Unknown sensor error")
                    return result
            else:
                result["sensor_success"] = False
                result["sensor_error"] = f"HTTP {sensor_response.status_code}"
                return result
            
            # Wait a moment to ensure sensor is stored
            time.sleep(0.1)
            
            # Apply biasing
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
                
                if not biasing_result.get("success", False):
                    result["biasing_error"] = biasing_result.get("error", "Unknown biasing error")
            else:
                result["biasing_success"] = False
                result["biasing_error"] = f"HTTP {biasing_response.status_code}: {biasing_response.text[:100]}"
            
        except Exception as e:
            result["sensor_success"] = False
            result["biasing_success"] = False
            result["error"] = str(e)
        
        return result

def main():
    """Main execution function"""
    tester = DetailedConcurrentBiasingTest()
    
    # Test with moderate concurrency first
    print("🔥 Testing with detailed analysis...")
    results = tester.test_concurrent_biasing_detailed(concurrent_requests=10)
    
    if results["race_condition_fixed"]:
        print("✅ RACE CONDITION FIXED")
    else:
        print("❌ RACE CONDITION STILL EXISTS")
        print(f"📊 Success Rate: {results['success_rate']:.1%}")
    
    print("\n🎯 DETAILED CONCURRENT TESTING COMPLETE")

if __name__ == "__main__":
    main()