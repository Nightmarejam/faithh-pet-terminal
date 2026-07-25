#!/usr/bin/env python3
"""
Test suite for Groq provider integration
Converted from test_groq.sh to pytest format
"""

import pytest
import requests
import json

BASE_URL = "http://localhost:5557"

class TestGroqProvider:
    """Test suite for Groq LLM provider"""
    
    def test_groq_chat_response(self):
        """Test basic Groq chat functionality"""
        response = requests.post(f"{BASE_URL}/api/chat", json={
            "message": "What are the four mechanisms in the Harmony-AI Bridge document?",
            "model": "llama3.1-8b"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert isinstance(data["response"], str)
        assert len(data["response"]) > 0
    
    def test_groq_model_availability(self):
        """Test that Groq models are available"""
        response = requests.get(f"{BASE_URL}/api/models")
        
        assert response.status_code == 200
        data = response.json()
        assert "models" in data
        
        # Check for Groq models
        groq_models = [m for m in data["models"] if m.get("provider") == "groq"]
        assert len(groq_models) > 0, "No Groq models found"
    
    @pytest.mark.slow
    def test_groq_rag_query(self):
        """Test Groq with RAG query"""
        response = requests.post(f"{BASE_URL}/api/chat", json={
            "message": "What are the four mechanisms in the Harmony-AI Bridge document?",
            "model": "llama3.1-8b",
            "use_rag": True
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        # RAG responses should typically be longer for document queries
        assert len(data["response"]) > 100
