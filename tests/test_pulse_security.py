#!/usr/bin/env python3
"""
Test suite for Pulse Security endpoints
Critical new features - validates security scanning, health checks, healing, and audit functionality
"""

import pytest
import requests
import json
import time

BASE_URL = "http://localhost:5557"

class TestPulseSecurity:
    """Test suite for Pulse Security functionality"""
    
    def test_security_scan_endpoint(self):
        """Test security scanner endpoint"""
        response = requests.post(f"{BASE_URL}/api/pulse/security/scan", json={
            "target": "system",
            "depth": "quick"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "is_safe" in data or "scan_results" in data or "status" in data
        assert isinstance(data, dict)
    
    def test_security_scan_with_options(self):
        """Test security scanner with different options"""
        response = requests.post(f"{BASE_URL}/api/pulse/security/scan", json={
            "target": "filesystem",
            "depth": "deep",
            "options": {
                "check_permissions": True,
                "scan_uploads": True
            }
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "is_safe" in data or "scan_results" in data or "status" in data
    
    def test_health_check_endpoint(self):
        """Test comprehensive health check endpoint"""
        response = requests.get(f"{BASE_URL}/api/pulse/health/check")
        
        assert response.status_code == 200
        data = response.json()
        # Response is either {services: {}} or direct {chromadb: {}, ollama: {}, ...}
        if "services" in data:
            services = data["services"]
        else:
            services = data  # Services are at top level
        assert isinstance(services, dict)
        # Check for expected services
        expected_services = ["chromadb", "ollama", "faithh_backend"]
        for service in expected_services:
            assert service in services, f"Missing service: {service}"
    
    def test_healing_endpoint_dry_run(self):
        """Test healing cycle in dry-run mode"""
        response = requests.post(f"{BASE_URL}/api/pulse/health/heal", json={
            "dry_run": True,
            "services": ["chromadb", "ollama"]
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "actions" in data or "healing_actions" in data or "status" in data
        assert isinstance(data, dict)
    
    def test_healing_endpoint_actual(self):
        """Test healing cycle with actual execution"""
        response = requests.post(f"{BASE_URL}/api/pulse/health/heal", json={
            "dry_run": False,
            "services": ["chromadb"]
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "actions" in data or "healing_actions" in data or "status" in data
    
    def test_audit_summary_endpoint(self):
        """Test audit log summary endpoint"""
        response = requests.get(f"{BASE_URL}/api/pulse/audit/summary")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        
        # Should contain summary statistics
        possible_keys = ["total_events", "events_by_type", "recent_events", "summary"]
        assert any(key in data for key in possible_keys)
    
    def test_audit_recent_endpoint_default(self):
        """Test recent audit events with default limit"""
        response = requests.get(f"{BASE_URL}/api/pulse/audit/recent")
        
        assert response.status_code == 200
        data = response.json()
        assert "events" in data or "recent_events" in data
        events = data.get("events", data.get("recent_events", []))
        assert isinstance(events, list)
    
    def test_audit_recent_endpoint_with_limit(self):
        """Test recent audit events with custom limit"""
        response = requests.get(f"{BASE_URL}/api/pulse/audit/recent?limit=5")
        
        assert response.status_code == 200
        data = response.json()
        assert "events" in data or "recent_events" in data
        events = data.get("events", data.get("recent_events", []))
        assert len(events) <= 5
    
    def test_audit_recent_endpoint_large_limit(self):
        """Test recent audit events with larger limit"""
        response = requests.get(f"{BASE_URL}/api/pulse/audit/recent?limit=100")
        
        assert response.status_code == 200
        data = response.json()
        assert "events" in data or "recent_events" in data
        events = data.get("events", data.get("recent_events", []))
        assert isinstance(events, list)
    
    @pytest.mark.integration
    def test_pulse_security_workflow(self):
        """Test complete Pulse Security workflow"""
        # 1. Run security scan
        scan_response = requests.post(f"{BASE_URL}/api/pulse/security/scan", json={
            "target": "system",
            "depth": "quick"
        })
        assert scan_response.status_code == 200
        
        # 2. Check health
        health_response = requests.get(f"{BASE_URL}/api/pulse/health/check")
        assert health_response.status_code == 200
        
        # 3. Get audit summary
        audit_response = requests.get(f"{BASE_URL}/api/pulse/audit/summary")
        assert audit_response.status_code == 200
        
        # All should return valid responses
        responses = [scan_response.json(), health_response.json(), audit_response.json()]
        for response_data in responses:
            assert isinstance(response_data, dict)
    
    @pytest.mark.slow
    def test_pulse_security_performance(self):
        """Test Pulse Security endpoint performance"""
        import time
        
        # Test response times for key endpoints
        endpoints = [
            "/api/pulse/health/check",
            "/api/pulse/audit/summary",
            "/api/pulse/audit/recent"
        ]
        
        for endpoint in endpoints:
            start_time = time.time()
            response = requests.get(f"{BASE_URL}{endpoint}")
            end_time = time.time()
            
            assert response.status_code == 200
            response_time = end_time - start_time
            
            # Should respond within reasonable time (5 seconds for security operations)
            assert response_time < 5.0, f"Endpoint {endpoint} took too long: {response_time}s"
    
    def test_pulse_security_error_handling(self):
        """Test Pulse Security error handling"""
        # Test invalid JSON
        response = requests.post(f"{BASE_URL}/api/pulse/security/scan", 
                                data="invalid json", 
                                headers={"Content-Type": "application/json"})
        
        # Should handle gracefully
        assert response.status_code in [400, 422]
        
        # Test missing required fields
        response = requests.post(f"{BASE_URL}/api/pulse/security/scan", json={})
        
        # Should handle missing fields gracefully
        assert response.status_code == 200  # Should use defaults
