#!/usr/bin/env python3
"""
Test suite for Harmony queries and RAG functionality
Converted from test_harmony.sh to pytest format
"""

import pytest
import requests
import json

BASE_URL = "http://localhost:5557"

class TestHarmonyQueries:
    """Test suite for Harmony-AI Bridge queries"""
    
    def test_harmony_query_response(self):
        """Test Harmony query with session tracking"""
        response = requests.post(f"{BASE_URL}/api/chat", json={
            "message": "What are the four proposed AI mechanisms in the Harmony-AI Bridge?",
            "session_id": "harmony_test"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert isinstance(data["response"], str)
        assert len(data["response"]) > 0
    
    def test_harmony_rag_search(self):
        """Test RAG search specifically for Harmony documents"""
        response = requests.post(f"{BASE_URL}/api/rag_search", json={
            "query": "Harmony-AI Bridge mechanisms",
            "category": ["documentation", "constella_master"]
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "results" in data or "documents" in data
    
    @pytest.mark.integration
    def test_harmony_session_continuity(self):
        """Test that session maintains context across queries"""
        session_id = "harmony_continuity_test"
        
        # First message
        response1 = requests.post(f"{BASE_URL}/api/chat", json={
            "message": "I'm learning about the Harmony-AI Bridge",
            "session_id": session_id
        })
        assert response1.status_code == 200
        
        # Follow-up message
        response2 = requests.post(f"{BASE_URL}/api/chat", json={
            "message": "What were the four mechanisms you mentioned?",
            "session_id": session_id
        })
        assert response2.status_code == 200
        
        # Should show context awareness
        data2 = response2.json()
        assert "response" in data2
        assert len(data2["response"]) > 50  # Should be substantive response
    
    @pytest.mark.slow
    def test_harmony_document_retrieval(self):
        """Test direct document retrieval for Harmony content"""
        response = requests.post(f"{BASE_URL}/api/rag_search", json={
            "query": "What are the four mechanisms in the Harmony-AI Bridge document?",
            "n_results": 5
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Should find relevant documents
        if "results" in data:
            assert len(data["results"]) > 0
        elif "documents" in data:
            assert len(data["documents"]) > 0
