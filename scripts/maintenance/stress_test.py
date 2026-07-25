#!/usr/bin/env python3
"""
Stress Testing Script for FAITHH Backend
Tests system performance under load
"""

import json
import time
import requests
import threading
import statistics
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

class StressTester:
    """Stress testing system"""
    
    def __init__(self, backend_url="http://localhost:5557"):
        self.backend_url = backend_url
        self.results = []
        
    def run_stress_test(self, concurrent_requests=10, test_duration=30):
        """Run comprehensive stress test"""
        print("🔥 Starting Stress Test")
        print(f"📊 Concurrent Requests: {concurrent_requests}")
        print(f"⏱️ Duration: {test_duration} seconds")
        print("=" * 50)
        
        start_time = time.time()
        end_time = start_time + test_duration
        
        # Test endpoints
        test_endpoints = [
            ("health", "GET", "/health", None),
            ("plc_state", "GET", "/api/plc/state", None),
            ("metrics", "GET", "/api/metrics", None),
            ("genomic_sensor", "POST", "/api/genomic/impedance-sensor", self.genomic_sensor_data),
            ("genomic_biasing", "POST", "/api/genomic/biasing-analysis", self.genomic_biasing_data),
            ("chat", "POST", "/api/chat", self.chat_data)
        ]
        
        results = {
            "test_duration": test_duration,
            "concurrent_requests": concurrent_requests,
            "endpoints": {},
            "performance": {},
            "errors": [],
            "summary": {}
        }
        
        with ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
            futures = []
            
            # Submit continuous requests for the duration
            while time.time() < end_time:
                for endpoint_name, method, path, data_generator in test_endpoints:
                    future = executor.submit(
                        self.make_request, 
                        method, 
                        path, 
                        data_generator,
                        endpoint_name
                    )
                    futures.append(future)
                
                # Wait for some requests to complete
                completed = []
                for future in as_completed(futures):
                    if len(completed) < concurrent_requests:
                        result = future.result()
                        completed.append(result)
                        self.results.append(result)
                
                # Clear futures for next batch
                futures = []
                time.sleep(1)  # Brief pause between batches
        
        # Analyze results
        results["summary"] = self.analyze_results()
        results["performance"] = self.calculate_performance_metrics()
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"stress_test_results_{timestamp}.json"
        
        with open(Path("/home/jonat/ai-stack") / filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n✅ Stress Test Complete")
        print(f"📊 Duration: {results['test_duration']} seconds")
        print(f"📈 Total Requests: {len(self.results)}")
        print(f"📄 Results saved to: {filename}")
        
        # Print summary
        self.print_summary(results)
        
        return results
    
    def make_request(self, method, path, data_generator, endpoint_name):
        """Make a single request"""
        start_time = time.time()
        
        try:
            if method == "GET":
                response = requests.get(f"{self.backend_url}{path}", timeout=30)
            elif method == "POST":
                data = data_generator() if data_generator else None
                response = requests.post(
                    f"{self.backend_url}{path}",
                    json=data,
                    timeout=30
                )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            result = {
                "endpoint": endpoint_name,
                "method": method,
                "path": path,
                "status_code": response.status_code,
                "response_time": response_time,
                "success": response.status_code == 200,
                "timestamp": datetime.now().isoformat()
            }
            
            if response.status_code != 200:
                result["error"] = f"HTTP {response.status_code}: {response.text[:100]}"
                self.results.append(result)
            else:
                result["data"] = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
                self.results.append(result)
                
        except Exception as e:
            result = {
                "endpoint": endpoint_name,
                "method": method,
                "path": path,
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            self.results.append(result)
        
        return result
    
    def genomic_sensor_data(self):
        """Generate genomic sensor test data"""
        import random
        return {
            "organism_id": f"stress_test_{random.randint(1000, 9999)}",
            "position": [random.uniform(-10, 10), random.uniform(-10, 10), random.uniform(-5, 5)],
            "sensitivity": random.uniform(0.1, 1.0)
        }
    
    def genomic_biasing_data(self):
        """Generate genomic biasing test data"""
        import random
        return {
            "organism_id": f"stress_test_{random.randint(1000, 9999)}",
            "original_genome": "ATGCGTACATGCGTACATGCGTACATGCGTACATGCGTACATGCGTAC",
            "biasing_strength": random.uniform(0.1, 1.0)
        }
    
    def chat_data(self):
        """Generate chat test data"""
        return {
            "message": "What is the status of the genomic experiments?",
            "provider": "auto"
        }
    
    def analyze_results(self):
        """Analyze stress test results"""
        if not self.results:
            return {}
        
        # Group by endpoint
        endpoint_stats = {}
        for result in self.results:
            endpoint = result["endpoint"]
            if endpoint not in endpoint_stats:
                endpoint_stats[endpoint] = {
                    "requests": 0,
                    "successes": 0,
                    "failures": 0,
                    "response_times": [],
                    "errors": []
                }
            
            endpoint_stats[endpoint]["requests"] += 1
            if result["success"]:
                endpoint_stats[endpoint]["successes"] += 1
                endpoint_stats[endpoint]["response_times"].append(result["response_time"])
            else:
                endpoint_stats[endpoint]["failures"] += 1
                endpoint_stats[endpoint]["errors"].append(result["error"])
        
        # Calculate statistics for each endpoint
        summary = {}
        for endpoint, stats in endpoint_stats.items():
            if stats["response_times"]:
                stats["avg_response_time"] = statistics.mean(stats["response_times"])
                stats["min_response_time"] = min(stats["response_times"])
                stats["max_response_time"] = max(stats["response_times"])
                stats["p95_response_time"] = sorted(stats["response_times"])[int(len(stats["response_times"]) * 0.95)]
            else:
                stats["avg_response_time"] = 0
                stats["min_response_time"] = 0
                stats["max_response_time"] = 0
                stats["p95_response_time"] = 0
            
            stats["success_rate"] = stats["successes"] / stats["requests"] if stats["requests"] > 0 else 0
            stats["failure_rate"] = stats["failures"] / stats["requests"] if stats["requests"] > 0 else 0
            
            summary[endpoint] = stats
        
        return summary
    
    def calculate_performance_metrics(self):
        """Calculate overall performance metrics"""
        if not self.results:
            return {}
        
        response_times = [r["response_time"] for r in self.results if r.get("success", False) and "response_time" in r]
        
        if not response_times:
            return {"avg_response_time": 0, "total_requests": 0}
        
        metrics = {
            "total_requests": len(self.results),
            "successful_requests": len([r for r in self.results if r.get("success", False)]),
            "failed_requests": len([r for r in self.results if not r.get("success", False)]),
            "avg_response_time": statistics.mean(response_times),
            "min_response_time": min(response_times),
            "max_response_time": max(response_times),
            "p95_response_time": sorted(response_times)[int(len(response_times) * 0.95)],
            "requests_per_second": len(self.results) / (max([r["timestamp"] for r in self.results]) - min([r["timestamp"] for r in self.results])) if len(self.results) > 1 else 0
        }
        
        metrics["success_rate"] = metrics["successful_requests"] / metrics["total_requests"] if metrics["total_requests"] > 0 else 0
        metrics["failure_rate"] = metrics["failed_requests"] / metrics["total_requests"] if metrics["total_requests"] > 0 else 0
        
        return metrics
    
    def print_summary(self, results):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 STRESS TEST SUMMARY")
        print("=" * 60)
        
        print(f"📈 Total Requests: {results['summary'].get('total_requests', 0)}")
        print(f"✅ Successful: {results['performance'].get('successful_requests', 0)}")
        print(f"❌ Failed: {results['performance'].get('failed_requests', 0)}")
        print(f"📊 Success Rate: {results['performance'].get('success_rate', 0):.1%}")
        print(f"⏱️ Avg Response Time: {results['performance'].get('avg_response_time', 0):.3f}s")
        print(f"📈 P95 Response Time: {results['performance'].get('p95_response_time', 0):.3f}s")
        print(f"🚀 Requests/Second: {results['performance'].get('requests_per_second', 0):.1f}")
        
        print("\n📊 Endpoint Performance:")
        for endpoint, stats in results['summary'].items():
            print(f"   {endpoint}:")
            print(f"     Requests: {stats['requests']}")
            print(f"     Success Rate: {stats['success_rate']:.1%}")
            print(f"     Avg Time: {stats.get('avg_response_time', 0):.3f}s")
            print(f"     Failures: {stats['failures']}")
        
        print("=" * 60)

def main():
    """Main execution function"""
    tester = StressTester()
    
    # Run stress test
    results = tester.run_stress_test(
        concurrent_requests=10,
        test_duration=30
    )
    
    # Exit with appropriate code
    if results['performance']['success_rate'] < 0.95:
        exit(1)  # Failure
    elif results['performance']['success_rate'] < 0.98:
        exit(2)  # Warning
    else:
        exit(0)  # Success

if __name__ == "__main__":
    main()