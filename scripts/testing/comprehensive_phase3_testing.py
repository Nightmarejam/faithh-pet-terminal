#!/usr/bin/env python3
"""
Comprehensive Phase 3 Testing Script
Tests Constitutional AI and Focus Management Systems
Phase 7: Academic Publication & Multi-User Deployment
"""

import requests
import json
import time
import sys
from datetime import datetime
from typing import Dict, List, Any
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Phase3ComprehensiveTest:
    """Comprehensive testing for Phase 3 systems"""
    
    def __init__(self, base_url: str = "http://localhost:5557"):
        self.base_url = base_url
        self.test_results = {
            "constitutional_tests": {},
            "focus_management_tests": {},
            "integration_tests": {},
            "performance_tests": {},
            "summary": {
                "total_tests": 0,
                "passed_tests": 0,
                "failed_tests": 0,
                "success_rate": 0.0
            }
        }
        
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all comprehensive tests"""
        logger.info("Starting Comprehensive Phase 3 Testing")
        logger.info("=" * 60)
        
        # Test Constitutional System
        self.test_constitutional_system()
        
        # Test Focus Management System
        self.test_focus_management_system()
        
        # Test Integration Scenarios
        self.test_integration_scenarios()
        
        # Test Performance
        self.test_performance_scenarios()
        
        # Calculate Summary
        self.calculate_summary()
        
        # Generate Report
        self.generate_test_report()
        
        return self.test_results
    
    def test_constitutional_system(self):
        """Test constitutional system functionality"""
        logger.info("Testing Constitutional System")
        logger.info("-" * 40)
        
        tests = [
            ("constitution_summary", self.test_constitution_summary),
            ("constitution_principles", self.test_constitution_principles),
            ("constitution_compliance", self.test_constitution_compliance),
            ("modern_rights_update", self.test_modern_rights_update),
            ("constitutional_evaluation", self.test_constitutional_evaluation)
        ]
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                self.test_results["constitutional_tests"][test_name] = result
                status = "✅ PASS" if result["success"] else "❌ FAIL"
                logger.info(f"  {status} {test_name}: {result.get('message', 'No message')}")
            except Exception as e:
                self.test_results["constitutional_tests"][test_name] = {
                    "success": False,
                    "error": str(e),
                    "message": "Test execution failed"
                }
                logger.error(f"  ❌ FAIL {test_name}: {e}")
    
    def test_focus_management_system(self):
        """Test focus management system functionality"""
        logger.info("Testing Focus Management System")
        logger.info("-" * 40)
        
        tests = [
            ("concept_capture", self.test_concept_capture),
            ("concept_evaluation", self.test_concept_evaluation),
            ("focus_health", self.test_focus_health),
            ("concept_pipeline", self.test_concept_pipeline),
            ("active_concepts", self.test_active_concepts),
            ("focus_drift_detection", self.test_focus_drift_detection)
        ]
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                self.test_results["focus_management_tests"][test_name] = result
                status = "✅ PASS" if result["success"] else "❌ FAIL"
                logger.info(f"  {status} {test_name}: {result.get('message', 'No message')}")
            except Exception as e:
                self.test_results["focus_management_tests"][test_name] = {
                    "success": False,
                    "error": str(e),
                    "message": "Test execution failed"
                }
                logger.error(f"  ❌ FAIL {test_name}: {e}")
    
    def test_integration_scenarios(self):
        """Test integration scenarios between systems"""
        logger.info("Testing Integration Scenarios")
        logger.info("-" * 40)
        
        tests = [
            ("constitutional_focus_integration", self.test_constitutional_focus_integration),
            ("cross_system_compliance", self.test_cross_system_compliance),
            ("ethical_concept_evaluation", self.test_ethical_concept_evaluation),
            ("strategic_alignment", self.test_strategic_alignment)
        ]
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                self.test_results["integration_tests"][test_name] = result
                status = "✅ PASS" if result["success"] else "❌ FAIL"
                logger.info(f"  {status} {test_name}: {result.get('message', 'No message')}")
            except Exception as e:
                self.test_results["integration_tests"][test_name] = {
                    "success": False,
                    "error": str(e),
                    "message": "Test execution failed"
                }
                logger.error(f"  ❌ FAIL {test_name}: {e}")
    
    def test_performance_scenarios(self):
        """Test performance scenarios"""
        logger.info("Testing Performance Scenarios")
        logger.info("-" * 40)
        
        tests = [
            ("api_response_times", self.test_api_response_times),
            ("concurrent_operations", self.test_concurrent_operations),
            ("load_testing", self.test_load_testing)
        ]
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                self.test_results["performance_tests"][test_name] = result
                status = "✅ PASS" if result["success"] else "❌ FAIL"
                logger.info(f"  {status} {test_name}: {result.get('message', 'No message')}")
            except Exception as e:
                self.test_results["performance_tests"][test_name] = {
                    "success": False,
                    "error": str(e),
                    "message": "Test execution failed"
                }
                logger.error(f"  ❌ FAIL {test_name}: {e}")
    
    # Constitutional System Tests
    def test_constitution_summary(self) -> Dict[str, Any]:
        """Test constitution summary endpoint"""
        try:
            response = requests.get(f"{self.base_url}/api/constitution/summary")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "constitution" in data:
                    constitution = data["constitution"]
                    required_fields = ["total_principles", "universal_principles", "modern_rights", "civic_principles"]
                    
                    for field in required_fields:
                        if field not in constitution:
                            return {
                                "success": False,
                                "message": f"Missing required field: {field}",
                                "data": constitution
                            }
                    
                    return {
                        "success": True,
                        "message": f"Constitution summary loaded: {constitution['total_principles']} principles",
                        "data": constitution
                    }
                else:
                    return {
                        "success": False,
                        "message": "API response indicates failure",
                        "data": data
                    }
            else:
                return {
                    "success": False,
                    "message": f"HTTP {response.status_code}",
                    "data": response.text
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Request failed: {str(e)}",
                "error": str(e)
            }
    
    def test_constitution_principles(self) -> Dict[str, Any]:
        """Test constitution principles endpoint"""
        try:
            response = requests.get(f"{self.base_url}/api/constitution/principles?domain=ai")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "principles" in data:
                    principles = data["principles"]
                    
                    if not isinstance(principles, list):
                        return {
                            "success": False,
                            "message": "Principles should be a list",
                            "data": principles
                        }
                    
                    return {
                        "success": True,
                        "message": f"Retrieved {len(principles)} principles for AI domain",
                        "data": principles
                    }
                else:
                    return {
                        "success": False,
                        "message": "API response indicates failure",
                        "data": data
                    }
            else:
                return {
                    "success": False,
                    "message": f"HTTP {response.status_code}",
                    "data": response.text
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Request failed: {str(e)}",
                "error": str(e)
            }
    
    def test_constitution_compliance(self) -> Dict[str, Any]:
        """Test constitutional compliance evaluation"""
        try:
            test_action = {
                "action": {
                    "description": "Implement AI system with privacy protection and fairness",
                    "context": {"domain": "ai", "privacy": "protected", "fairness": "ensured"}
                },
                "domain": "ai"
            }
            
            response = requests.post(
                f"{self.base_url}/api/constitution/evaluate",
                json=test_action,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "compliance_report" in data:
                    report = data["compliance_report"]
                    required_fields = ["compliance_level", "compliance_score", "violated_principles"]
                    
                    for field in required_fields:
                        if field not in report:
                            return {
                                "success": False,
                                "message": f"Missing required field: {field}",
                                "data": report
                            }
                    
                    return {
                        "success": True,
                        "message": f"Compliance evaluation: {report['compliance_level']} with score {report['compliance_score']}",
                        "data": report
                    }
                else:
                    return {
                        "success": False,
                        "message": "API response indicates failure",
                        "data": data
                    }
            else:
                return {
                    "success": False,
                    "message": f"HTTP {response.status_code}",
                    "data": response.text
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Request failed: {str(e)}",
                "error": str(e)
            }
    
    def test_modern_rights_update(self) -> Dict[str, Any]:
        """Test modern rights update functionality"""
        try:
            response = requests.post(f"{self.base_url}/api/constitution/update-modern-rights")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    return {
                        "success": True,
                        "message": f"Modern rights updated: {len(data.get('new_principles', []))} new principles",
                        "data": data
                    }
                else:
                    return {
                        "success": False,
                        "message": "Modern rights update failed",
                        "data": data
                    }
            else:
                return {
                    "success": False,
                    "message": f"HTTP {response.status_code}",
                    "data": response.text
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Request failed: {str(e)}",
                "error": str(e)
            }
    
    def test_constitutional_evaluation(self) -> Dict[str, Any]:
        """Test constitutional evaluation with various scenarios"""
        try:
            test_scenarios = [
                {
                    "name": "Privacy-focused AI",
                    "action": {
                        "description": "AI system with strong privacy protections",
                        "context": {"domain": "ai", "privacy": "high", "data_protection": "gdpr"}
                    },
                    "domain": "ai"
                },
                {
                    "name": "Educational AI",
                    "action": {
                        "description": "AI for education with equal access",
                        "context": {"domain": "education", "access": "equal", "privacy": "protected"}
                    },
                    "domain": "education"
                },
                {
                    "name": "Healthcare AI",
                    "action": {
                        "description": "AI for healthcare with bias prevention",
                        "context": {"domain": "healthcare", "bias_prevention": "enabled", "privacy": "strict"}
                    },
                    "domain": "healthcare"
                }
            ]
            
            results = []
            for scenario in test_scenarios:
                response = requests.post(
                    f"{self.base_url}/api/constitution/evaluate",
                    json=scenario,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        report = data["compliance_report"]
                        results.append({
                            "scenario": scenario["name"],
                            "compliance_level": report["compliance_level"],
                            "compliance_score": report["compliance_score"],
                            "violations": len(report.get("violated_principles", []))
                        })
                    else:
                        results.append({
                            "scenario": scenario["name"],
                            "error": "API failure",
                            "data": data
                        })
                else:
                    results.append({
                        "scenario": scenario["name"],
                        "error": f"HTTP {response.status_code}",
                        "data": response.text
                    })
            
            successful_evaluations = [r for r in results if "error" not in r]
            
            return {
                "success": len(successful_evaluations) == len(test_scenarios),
                "message": f"Evaluated {len(successful_evaluations)}/{len(test_scenarios)} scenarios",
                "data": results
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Evaluation failed: {str(e)}",
                "error": str(e)
            }
    
    # Focus Management Tests
    def test_concept_capture(self) -> Dict[str, Any]:
        """Test concept capture functionality"""
        try:
            test_concepts = [
                {
                    "name": "Educational Platform",
                    "raw_idea": "Create an AI-powered educational platform that respects student privacy and provides personalized learning",
                    "context": {"domain": "education", "urgency": 0.7}
                },
                {
                    "name": "Healthcare Assistant",
                    "raw_idea": "Develop a healthcare AI assistant that ensures patient confidentiality and prevents bias",
                    "context": {"domain": "healthcare", "urgency": 0.9}
                },
                {
                    "name": "Civic Engagement Tool",
                    "raw_idea": "Build a tool for civic engagement that promotes democratic participation and protects free speech",
                    "context": {"domain": "civic", "urgency": 0.6}
                }
            ]
            
            results = []
            for concept in test_concepts:
                response = requests.post(
                    f"{self.base_url}/api/focus/capture-concept",
                    json={
                        "raw_idea": concept["raw_idea"],
                        "context": concept["context"]
                    },
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") and "concept" in data:
                        concept_data = data["concept"]
                        results.append({
                            "scenario": concept["name"],
                            "concept_id": concept_data.get("id"),
                            "evaluation_score": concept_data.get("evaluation_score"),
                            "constitutional_feasibility": concept_data.get("constitutional_feasibility"),
                            "priority": concept_data.get("priority")
                        })
                    else:
                        results.append({
                            "scenario": concept["name"],
                            "error": "API failure",
                            "data": data
                        })
                else:
                    results.append({
                        "scenario": concept["name"],
                        "error": f"HTTP {response.status_code}",
                        "data": response.text
                    })
            
            successful_captures = [r for r in results if "error" not in r]
            
            return {
                "success": len(successful_captures) == len(test_concepts),
                "message": f"Captured {len(successful_captures)}/{len(test_concepts)} concepts",
                "data": results
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Concept capture failed: {str(e)}",
                "error": str(e)
            }
    
    def test_concept_evaluation(self) -> Dict[str, Any]:
        """Test concept evaluation quality"""
        try:
            response = requests.get(f"{self.base_url}/api/focus/concepts")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "concepts" in data:
                    concepts = data["concepts"]
                    
                    if not concepts:
                        return {
                            "success": True,
                            "message": "No concepts to evaluate",
                            "data": []
                        }
                    
                    # Check evaluation quality
                    evaluation_scores = [c.get("evaluation_score", 0) for c in concepts]
                    constitutional_compliance = [c.get("constitutional_feasibility") for c in concepts]
                    
                    avg_score = sum(evaluation_scores) / len(evaluation_scores) if evaluation_scores else 0
                    full_compliance = sum(1 for c in constitutional_compliance if c == "full")
                    compliance_rate = (full_compliance / len(constitutional_compliance)) if constitutional_compliance else 0
                    
                    return {
                        "success": True,
                        "message": f"Evaluation quality: {avg_score:.2f} avg score, {compliance_rate:.1%} full compliance",
                        "data": {
                            "total_concepts": len(concepts),
                            "average_score": avg_score,
                            "compliance_rate": compliance_rate,
                            "score_distribution": evaluation_scores
                        }
                    }
                else:
                    return {
                        "success": False,
                        "message": "API response indicates failure",
                        "data": data
                    }
            else:
                return {
                    "success": False,
                    "message": f"HTTP {response.status_code}",
                    "data": response.text
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Concept evaluation failed: {str(e)}",
                "error": str(e)
            }
    
    def test_focus_health(self) -> Dict[str, Any]:
        """Test focus health monitoring"""
        try:
            response = requests.get(f"{self.base_url}/api/focus/health")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "focus_health" in data:
                    health = data["focus_health"]
                    required_fields = ["status", "active_concepts", "total_concepts", "drift_score"]
                    
                    for field in required_fields:
                        if field not in health:
                            return {
                                "success": False,
                                "message": f"Missing required field: {field}",
                                "data": health
                            }
                    
                    return {
                        "success": True,
                        "message": f"Focus health: {health['status']} with {health['drift_score']} drift score",
                        "data": health
                    }
                else:
                    return {
                        "success": False,
                        "message": "API response indicates failure",
                        "data": data
                    }
            else:
                return {
                    "success": False,
                    "message": f"HTTP {response.status_code}",
                    "data": response.text
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Focus health check failed: {str(e)}",
                "error": str(e)
            }
    
    def test_concept_pipeline(self) -> Dict[str, Any]:
        """Test concept pipeline functionality"""
        try:
            response = requests.get(f"{self.base_url}/api/focus/pipeline")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "pipeline" in data:
                    pipeline = data["pipeline"]
                    
                    if not isinstance(pipeline, dict):
                        return {
                            "success": False,
                            "message": "Pipeline should be a dictionary",
                            "data": pipeline
                        }
                    
                    expected_states = ["captured", "evaluating", "prioritized", "active", "paused", "completed", "archived"]
                    
                    for state in expected_states:
                        if state not in pipeline:
                            return {
                                "success": False,
                                "message": f"Missing pipeline state: {state}",
                                "data": pipeline
                            }
                    
                    total_concepts = sum(len(concepts) for concepts in pipeline.values())
                    
                    return {
                        "success": True,
                        "message": f"Pipeline loaded: {total_concepts} concepts across {len(pipeline)} states",
                        "data": pipeline
                    }
                else:
                    return {
                        "success": False,
                        "message": "API response indicates failure",
                        "data": data
                    }
            else:
                return {
                    "success": False,
                    "message": f"HTTP {response.status_code}",
                    "data": response.text
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Concept pipeline test failed: {str(e)}",
                "error": str(e)
            }
    
    def test_active_concepts(self) -> Dict[str, Any]:
        """Test active concepts retrieval"""
        try:
            response = requests.get(f"{self.base_url}/api/focus/active-concepts")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "active_concepts" in data:
                    concepts = data["active_concepts"]
                    
                    if not isinstance(concepts, list):
                        return {
                            "success": False,
                            "message": "Active concepts should be a list",
                            "data": concepts
                        }
                    
                    return {
                        "success": True,
                        "message": f"Retrieved {len(concepts)} active concepts",
                        "data": concepts
                    }
                else:
                    return {
                        "success": False,
                        "message": "API response indicates failure",
                        "data": data
                    }
            else:
                return {
                    "success": False,
                    "message": f"HTTP {response.status_code}",
                    "data": response.text
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Active concepts test failed: {str(e)}",
                "error": str(e)
            }
    
    def test_focus_drift_detection(self) -> Dict[str, Any]:
        """Test focus drift detection"""
        try:
            response = requests.get(f"{self.base_url}/api/focus/health")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "focus_health" in data:
                    health = data["focus_health"]
                    
                    if "drift_score" in health and "drift_indicators" in health:
                        drift_score = health["drift_score"]
                        drift_indicators = health["drift_indicators"]
                        
                        if isinstance(drift_indicators, dict):
                            return {
                                "success": True,
                                "message": f"Drift detection working: score {drift_score}, {len(drift_indicators)} indicators",
                                "data": {
                                    "drift_score": drift_score,
                                    "drift_indicators": drift_indicators
                                }
                            }
                        else:
                            return {
                                "success": False,
                                "message": "Drift indicators should be a dictionary",
                                "data": drift_indicators
                            }
                    else:
                        return {
                            "success": False,
                            "message": "Missing drift detection fields",
                            "data": health
                        }
                else:
                    return {
                        "success": False,
                        "message": "API response indicates failure",
                        "data": data
                    }
            else:
                return {
                    "success": False,
                    "message": f"HTTP {response.status_code}",
                    "data": response.text
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Drift detection test failed: {str(e)}",
                "error": str(e)
            }
    
    # Integration Tests
    def test_constitutional_focus_integration(self) -> Dict[str, Any]:
        """Test integration between constitutional and focus systems"""
        try:
            # Capture a concept and check its constitutional compliance
            test_concept = {
                "raw_idea": "Create an AI system for democratic participation that protects free speech and ensures privacy",
                "context": {"domain": "civic", "urgency": 0.8}
            }
            
            # Step 1: Capture concept
            capture_response = requests.post(
                f"{self.base_url}/api/focus/capture-concept",
                json=test_concept,
                headers={"Content-Type": "application/json"}
            )
            
            if capture_response.status_code != 200:
                return {
                    "success": False,
                    "message": "Concept capture failed",
                    "data": capture_response.text
                }
            
            capture_data = capture_response.json()
            if not capture_data.get("success"):
                return {
                    "success": False,
                    "message": "Concept capture API failure",
                    "data": capture_data
                }
            
            concept = capture_data["concept"]
            constitutional_feasibility = concept.get("constitutional_feasibility")
            
            # Step 2: Verify constitutional compliance
            if constitutional_feasibility not in ["full", "partial", "violation", "unknown"]:
                return {
                    "success": False,
                    "message": f"Invalid constitutional feasibility: {constitutional_feasibility}",
                    "data": concept
                }
            
            return {
                "success": True,
                "message": f"Integration successful: concept with {constitutional_feasibility} constitutional feasibility",
                "data": {
                    "concept_id": concept.get("id"),
                    "evaluation_score": concept.get("evaluation_score"),
                    "constitutional_feasibility": constitutional_feasibility
                }
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Integration test failed: {str(e)}",
                "error": str(e)
            }
    
    def test_cross_system_compliance(self) -> Dict[str, Any]:
        """Test cross-system compliance checking"""
        try:
            # Test the same action in both systems
            test_action = {
                "action": {
                    "description": "AI system for healthcare with strict privacy and bias prevention",
                    "context": {"domain": "healthcare", "privacy": "strict", "bias_prevention": "enabled"}
                },
                "domain": "healthcare"
            }
            
            # Step 1: Evaluate in constitutional system
            const_response = requests.post(
                f"{self.base_url}/api/constitution/evaluate",
                json=test_action,
                headers={"Content-Type": "application/json"}
            )
            
            # Step 2: Capture as concept in focus system
            focus_response = requests.post(
                f"{self.base_url}/api/focus/capture-concept",
                json={
                    "raw_idea": test_action["action"]["description"],
                    "context": test_action["action"]["context"]
                },
                headers={"Content-Type": "application/json"}
            )
            
            if const_response.status_code != 200 or focus_response.status_code != 200:
                return {
                    "success": False,
                    "message": "One or both API calls failed",
                    "data": {
                        "constitutional_response": const_response.status_code,
                        "focus_response": focus_response.status_code
                    }
                }
            
            const_data = const_response.json()
            focus_data = focus_response.json()
            
            if not (const_data.get("success") and focus_data.get("success")):
                return {
                    "success": False,
                    "message": "API responses indicate failure",
                    "data": {
                        "constitutional": const_data,
                        "focus": focus_data
                    }
                }
            
            const_compliance = const_data["compliance_report"]["compliance_level"]
            focus_feasibility = focus_data["concept"]["constitutional_feasibility"]
            
            # Check consistency (both should indicate similar compliance levels)
            return {
                "success": True,
                "message": f"Cross-system compliance: constitutional {const_compliance}, focus {focus_feasibility}",
                "data": {
                    "constitutional_compliance": const_compliance,
                    "focus_feasibility": focus_feasibility,
                    "consistent": self._check_compliance_consistency(const_compliance, focus_feasibility)
                }
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Cross-system test failed: {str(e)}",
                "error": str(e)
            }
    
    def test_ethical_concept_evaluation(self) -> Dict[str, Any]:
        """Test ethical concept evaluation scenarios"""
        try:
            ethical_scenarios = [
                {
                    "name": "Privacy-First AI",
                    "idea": "AI system that prioritizes user privacy above all other considerations",
                    "expected_compliance": "full"
                },
                {
                    "name": "Surveillance AI",
                    "idea": "AI system for mass surveillance without privacy protections",
                    "expected_compliance": "violation"
                },
                {
                    "name": "Educational AI",
                    "idea": "AI for education with equal access and privacy protection",
                    "expected_compliance": "full"
                }
            ]
            
            results = []
            for scenario in ethical_scenarios:
                # Test in focus system
                focus_response = requests.post(
                    f"{self.base_url}/api/focus/capture-concept",
                    json={
                        "raw_idea": scenario["idea"],
                        "context": {"domain": "ai", "ethical": True}
                    },
                    headers={"Content-Type": "application/json"}
                )
                
                if focus_response.status_code == 200:
                    focus_data = focus_response.json()
                    if focus_data.get("success"):
                        actual_compliance = focus_data["concept"]["constitutional_feasibility"]
                        expected_compliance = scenario["expected_compliance"]
                        
                        results.append({
                            "scenario": scenario["name"],
                            "expected": expected_compliance,
                            "actual": actual_compliance,
                            "correct": self._check_compliance_consistency(expected_compliance, actual_compliance)
                        })
                    else:
                        results.append({
                            "scenario": scenario["name"],
                            "error": "Focus API failure",
                            "data": focus_data
                        })
                else:
                    results.append({
                        "scenario": scenario["name"],
                        "error": f"HTTP {focus_response.status_code}",
                        "data": focus_response.text
                    })
            
            correct_evaluations = sum(1 for r in results if r.get("correct", False))
            
            return {
                "success": correct_evaluations == len(ethical_scenarios),
                "message": f"Ethical evaluation: {correct_evaluations}/{len(ethical_scenarios)} correct",
                "data": results
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Ethical evaluation test failed: {str(e)}",
                "error": str(e)
            }
    
    def test_strategic_alignment(self) -> Dict[str, Any]:
        """Test strategic alignment of concepts"""
        try:
            # Test concepts with different strategic alignments
            strategic_concepts = [
                {
                    "name": "High Alignment",
                    "idea": "AI system that directly supports current strategic goals",
                    "context": {"strategic_importance": "high", "alignment": 0.9}
                },
                {
                    "name": "Medium Alignment",
                    "idea": "AI system with moderate strategic alignment",
                    "context": {"strategic_importance": "medium", "alignment": 0.6}
                },
                {
                    "name": "Low Alignment",
                    "idea": "AI system with low strategic alignment",
                    "context": {"strategic_importance": "low", "alignment": 0.3}
                }
            ]
            
            results = []
            for concept in strategic_concepts:
                response = requests.post(
                    f"{self.base_url}/api/focus/capture-concept",
                    json={
                        "raw_idea": concept["idea"],
                        "context": concept["context"]
                    },
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        concept_data = data["concept"]
                        results.append({
                            "scenario": concept["name"],
                            "strategic_alignment": concept_data.get("strategic_alignment"),
                            "evaluation_score": concept_data.get("evaluation_score"),
                            "priority": concept_data.get("priority")
                        })
                    else:
                        results.append({
                            "scenario": concept["name"],
                            "error": "API failure",
                            "data": data
                        })
                else:
                    results.append({
                        "scenario": concept["name"],
                        "error": f"HTTP {response.status_code}",
                        "data": response.text
                    })
            
            successful_tests = [r for r in results if "error" not in r]
            
            return {
                "success": len(successful_tests) == len(strategic_concepts),
                "message": f"Strategic alignment: {len(successful_tests)}/{len(strategic_concepts)} successful",
                "data": results
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Strategic alignment test failed: {str(e)}",
                "error": str(e)
            }
    
    # Performance Tests
    def test_api_response_times(self) -> Dict[str, Any]:
        """Test API response times"""
        try:
            endpoints = [
                ("/api/constitution/summary", "GET"),
                ("/api/focus/health", "GET"),
                ("/api/constitution/principles?domain=ai", "GET")
            ]
            
            response_times = []
            
            for endpoint, method in endpoints:
                start_time = time.time()
                
                if method == "GET":
                    response = requests.get(f"{self.base_url}{endpoint}")
                else:
                    response = requests.post(f"{self.base_url}{endpoint}")
                
                end_time = time.time()
                response_time = (end_time - start_time) * 1000  # Convert to milliseconds
                
                response_times.append({
                    "endpoint": endpoint,
                    "method": method,
                    "response_time_ms": response_time,
                    "status_code": response.status_code,
                    "success": response.status_code == 200
                })
            
            avg_response_time = sum(rt["response_time_ms"] for rt in response_times) / len(response_times)
            max_response_time = max(rt["response_time_ms"] for rt in response_times)
            successful_requests = sum(1 for rt in response_times if rt["success"])
            
            # Performance criteria: average < 200ms, max < 1000ms
            performance_good = avg_response_time < 200 and max_response_time < 1000 and successful_requests == len(endpoints)
            
            return {
                "success": performance_good,
                "message": f"Response times: avg {avg_response_time:.1f}ms, max {max_response_time:.1f}ms",
                "data": {
                    "average_response_time": avg_response_time,
                    "max_response_time": max_response_time,
                    "successful_requests": successful_requests,
                    "total_requests": len(endpoints),
                    "response_times": response_times
                }
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Response time test failed: {str(e)}",
                "error": str(e)
            }
    
    def test_concurrent_operations(self) -> Dict[str, Any]:
        """Test concurrent operations"""
        try:
            import threading
            import queue
            
            results_queue = queue.Queue()
            
            def concurrent_request(endpoint, method, data=None):
                try:
                    start_time = time.time()
                    if method == "GET":
                        response = requests.get(f"{self.base_url}{endpoint}")
                    else:
                        response = requests.post(f"{self.base_url}{endpoint}", json=data)
                    end_time = time.time()
                    
                    results_queue.put({
                        "endpoint": endpoint,
                        "response_time": end_time - start_time,
                        "status_code": response.status_code,
                        "success": response.status_code == 200
                    })
                except Exception as e:
                    results_queue.put({
                        "endpoint": endpoint,
                        "error": str(e),
                        "success": False
                    })
            
            # Create concurrent requests
            threads = []
            endpoints = [
                ("/api/constitution/summary", "GET"),
                ("/api/focus/health", "GET"),
                ("/api/constitution/principles?domain=ai", "GET")
            ]
            
            # Start 3 concurrent requests for each endpoint
            for endpoint, method in endpoints:
                for i in range(3):
                    thread = threading.Thread(target=concurrent_request, args=(endpoint, method))
                    threads.append(thread)
                    thread.start()
            
            # Wait for all threads to complete
            for thread in threads:
                thread.join()
            
            # Collect results
            results = []
            while not results_queue.empty():
                results.append(results_queue.get())
            
            successful_requests = sum(1 for r in results if r.get("success", False))
            total_requests = len(results)
            
            return {
                "success": successful_requests == total_requests,
                "message": f"Concurrent operations: {successful_requests}/{total_requests} successful",
                "data": {
                    "total_requests": total_requests,
                    "successful_requests": successful_requests,
                    "results": results
                }
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Concurrent operations test failed: {str(e)}",
                "error": str(e)
            }
    
    def test_load_testing(self) -> Dict[str, Any]:
        """Test load handling"""
        try:
            # Simple load test: 10 sequential requests
            endpoint = "/api/constitution/summary"
            response_times = []
            
            for i in range(10):
                start_time = time.time()
                response = requests.get(f"{self.base_url}{endpoint}")
                end_time = time.time()
                
                response_times.append({
                    "request": i + 1,
                    "response_time": end_time - start_time,
                    "status_code": response.status_code,
                    "success": response.status_code == 200
                })
            
            successful_requests = sum(1 for rt in response_times if rt["success"])
            avg_response_time = sum(rt["response_time"] for rt in response_times) / len(response_times)
            
            return {
                "success": successful_requests == 10,
                "message": f"Load test: {successful_requests}/10 successful, avg {avg_response_time:.3f}s",
                "data": {
                    "successful_requests": successful_requests,
                    "average_response_time": avg_response_time,
                    "response_times": response_times
                }
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Load test failed: {str(e)}",
                "error": str(e)
            }
    
    # Helper methods
    def _check_compliance_consistency(self, const_compliance: str, focus_feasibility: str) -> bool:
        """Check if compliance levels are consistent"""
        # Map compliance levels to consistency
        consistency_map = {
            "full": "full",
            "partial": "partial", 
            "violation": "violation",
            "unknown": "unknown"
        }
        
        return consistency_map.get(const_compliance) == focus_feasibility
    
    def calculate_summary(self):
        """Calculate test summary statistics"""
        all_tests = []
        
        # Collect all test results
        for category in ["constitutional_tests", "focus_management_tests", "integration_tests", "performance_tests"]:
            for test_name, test_result in self.test_results[category].items():
                all_tests.append({
                    "category": category,
                    "test": test_name,
                    "success": test_result.get("success", False)
                })
        
        total_tests = len(all_tests)
        passed_tests = sum(1 for test in all_tests if test["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests) if total_tests > 0 else 0.0
        
        self.test_results["summary"] = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate
        }
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        summary = self.test_results["summary"]
        
        logger.info("=" * 60)
        logger.info("COMPREHENSIVE PHASE 3 TESTING REPORT")
        logger.info("=" * 60)
        logger.info(f"Total Tests: {summary['total_tests']}")
        logger.info(f"Passed: {summary['passed_tests']}")
        logger.info(f"Failed: {summary['failed_tests']}")
        logger.info(f"Success Rate: {summary['success_rate']:.1%}")
        logger.info("=" * 60)
        
        # Category breakdowns
        for category in ["constitutional_tests", "focus_management_tests", "integration_tests", "performance_tests"]:
            category_tests = self.test_results[category]
            category_passed = sum(1 for test in category_tests.values() if test.get("success", False))
            category_total = len(category_tests)
            category_rate = (category_passed / category_total) if category_total > 0 else 0.0
            
            logger.info(f"{category.replace('_', ' ').title()}: {category_passed}/{category_total} ({category_rate:.1%})")
        
        logger.info("=" * 60)
        
        # Failed tests details
        failed_tests = []
        for category in ["constitutional_tests", "focus_management_tests", "integration_tests", "performance_tests"]:
            for test_name, test_result in self.test_results[category].items():
                if not test_result.get("success", False):
                    failed_tests.append({
                        "category": category,
                        "test": test_name,
                        "error": test_result.get("error", test_result.get("message", "Unknown error"))
                    })
        
        if failed_tests:
            logger.info("FAILED TESTS:")
            for failed_test in failed_tests:
                logger.info(f"  ❌ {failed_test['category']}.{failed_test['test']}: {failed_test['error']}")
        else:
            logger.info("🎉 ALL TESTS PASSED!")
        
        logger.info("=" * 60)

def main():
    """Main function to run comprehensive tests"""
    tester = Phase3ComprehensiveTest()
    results = tester.run_all_tests()
    
    # Exit with appropriate code
    summary = results["summary"]
    if summary["success_rate"] >= 0.9:  # 90% success rate threshold
        logger.info("🎉 COMPREHENSIVE TESTING SUCCESSFUL!")
        sys.exit(0)
    else:
        logger.error(f"❌ TESTING FAILED: {summary['success_rate']:.1%} success rate")
        sys.exit(1)

if __name__ == "__main__":
    main()