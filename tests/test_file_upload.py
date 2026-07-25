#!/usr/bin/env python3
"""
Test suite for file upload functionality
Critical for security - validates file handling, type checking, and size limits
"""

import pytest
import requests
import io
import tempfile
import os
from pathlib import Path

BASE_URL = "http://localhost:5557"

class TestFileUpload:
    """Test suite for file upload endpoint"""
    
    def test_valid_text_file_upload(self):
        """Test uploading a valid text file"""
        file_content = b"This is a test file for upload testing."
        file_name = "test_document.txt"
        
        response = requests.post(
            f"{BASE_URL}/api/upload",
            files={"file": (file_name, io.BytesIO(file_content), "text/plain")}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "filename" in data
        assert data["filename"] == file_name
        assert "size" in data
        assert data["size"] == len(file_content)
    
    def test_valid_markdown_file_upload(self):
        """Test uploading a markdown file"""
        file_content = b"# Test Document\n\nThis is a **test** markdown file."
        file_name = "test_markdown.md"
        
        response = requests.post(
            f"{BASE_URL}/api/upload",
            files={"file": (file_name, io.BytesIO(file_content), "text/markdown")}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "filename" in data
        assert data["filename"] == file_name
    
    def test_invalid_executable_file_rejection(self):
        """Test that executable files are rejected"""
        file_content = b"fake executable content"
        file_name = "malware.exe"
        
        response = requests.post(
            f"{BASE_URL}/api/upload",
            files={"file": (file_name, io.BytesIO(file_content), "application/x-executable")}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert "file type" in data["error"].lower()
    
    def test_invalid_script_file_rejection(self):
        """Test that script files are rejected"""
        file_content = b"#!/bin/bash\necho 'malicious script'"
        file_name = "malicious.sh"
        
        response = requests.post(
            f"{BASE_URL}/api/upload",
            files={"file": (file_name, io.BytesIO(file_content), "application/x-sh")}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
    
    def test_oversized_file_rejection(self):
        """Test that oversized files are rejected"""
        # Create a large file (assuming limit is 10MB)
        large_content = b"x" * (11 * 1024 * 1024)  # 11MB
        file_name = "oversized.txt"
        
        response = requests.post(
            f"{BASE_URL}/api/upload",
            files={"file": (file_name, io.BytesIO(large_content), "text/plain")}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert "size" in data["error"].lower()
    
    def test_missing_file_error(self):
        """Test error when no file is provided"""
        response = requests.post(f"{BASE_URL}/api/upload", data={})
        
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert "file" in data["error"].lower()
    
    def test_empty_file_error(self):
        """Test error when empty file is uploaded"""
        file_content = b""
        file_name = "empty.txt"
        
        response = requests.post(
            f"{BASE_URL}/api/upload",
            files={"file": (file_name, io.BytesIO(file_content), "text/plain")}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
    
    @pytest.mark.integration
    def test_file_upload_with_special_characters(self):
        """Test upload with special characters in filename"""
        file_content = b"Test content with special characters"
        file_name = "test_file-with_special.chars&symbols.txt"
        
        response = requests.post(
            f"{BASE_URL}/api/upload",
            files={"file": (file_name, io.BytesIO(file_content), "text/plain")}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "filename" in data
    
    @pytest.mark.slow
    def test_concurrent_file_uploads(self):
        """Test handling multiple concurrent uploads"""
        import threading
        import queue
        
        results = queue.Queue()
        
        def upload_file(file_id):
            file_content = f"Test content for file {file_id}".encode()
            file_name = f"concurrent_test_{file_id}.txt"
            
            try:
                response = requests.post(
                    f"{BASE_URL}/api/upload",
                    files={"file": (file_name, io.BytesIO(file_content), "text/plain")}
                )
                results.put((file_id, response.status_code, response.json()))
            except Exception as e:
                results.put((file_id, None, {"error": str(e)}))
        
        # Start 5 concurrent uploads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=upload_file, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all to complete
        for thread in threads:
            thread.join()
        
        # Check results
        successful_uploads = 0
        while not results.empty():
            file_id, status, data = results.get()
            if status == 200:
                successful_uploads += 1
        
        # At least 4 out of 5 should succeed
        assert successful_uploads >= 4
