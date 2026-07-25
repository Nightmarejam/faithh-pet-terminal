# FAITHH Testing Quick Start

**Date:** 2026-01-18  
**Purpose:** Quick guide for running and creating tests in FAITHH  
**Audience:** Developers working on FAITHH  

---

## Current Test Status

⚠️ **WARNING:** FAITHH currently has **minimal test infrastructure**. Most tests are manual scripts with no automation. This guide covers both current state and recommended improvements.

---

## Running Current Tests

### Backend Health Tests
```bash
# Run backend health check test
cd /home/jonat/ai-stack
python tests/test_backend.py

# Expected output:
# Testing FAITHH Backend...
# ========================================
# ✅ Health check: {'status': 'healthy', ...}
# 📊 Service Status:
#   ✅ chromadb: online
#   ✅ ollama: online
#   ...
```

### RAG Quality Tests
```bash
# Run RAG quality stress test
python tests/test_rag_quality.py

# Run with specific options
python tests/test_rag_quality.py --verbose
python tests/test_rag_quality.py --n-results 10
```

### Shell Tests
```bash
# Test Groq provider
./tests/test_groq.sh

# Test Harmony queries
./tests/test_harmony.sh
```

### Individual Component Tests
```bash
# ChromaDB query testing
python tests/test_chroma_query.py

# End-to-end pipeline test
python tests/test_e2e.py

# Environment validation
python tests/test_env.py
```

---

## Current Test Limitations

### Problems with Current Tests
- **Manual execution only** - no automation
- **No assertions** - just print statements
- **No test isolation** - tests may interfere
- **No coverage reporting** - unknown test coverage
- **No error handling** - tests fail silently
- **No test data management** - hardcoded values

### What's Missing
- pytest configuration
- Test dependencies
- Automated test running
- Coverage tracking
- Mock/stub infrastructure
- CI/CD integration

---

## Recommended Test Setup (Future State)

### Install Test Dependencies
```bash
# Add to requirements.txt
echo "pytest>=7.0.0
pytest-asyncio>=0.21.0
pytest-mock>=3.10.0
requests-mock>=1.10.0
pytest-cov>=4.0.0" >> requirements.txt

# Install dependencies
pip install -r requirements.txt
```

### Create pytest Configuration
```bash
# Create pytest.ini
cat > pytest.ini << EOF
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = --cov=. --cov-report=html --cov-report=term-missing
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    slow: Slow running tests
EOF
```

---

## Creating New Tests

### Basic Test Structure
```python
# tests/test_new_feature.py
import pytest
from unittest.mock import Mock, patch

class TestNewFeature:
    """Test suite for new feature"""
    
    def test_basic_functionality(self):
        """Test basic feature functionality"""
        # Arrange
        expected = "expected_result"
        
        # Act
        result = function_under_test()
        
        # Assert
        assert result == expected
    
    @pytest.mark.integration
    def test_with_dependencies(self):
        """Test feature with external dependencies"""
        with patch('module.dependency') as mock_dep:
            mock_dep.return_value = "mocked_value"
            result = function_under_test()
            assert result is not None
    
    def test_error_handling(self):
        """Test error scenarios"""
        with pytest.raises(ValueError):
            function_under_test(invalid_input)
```

### API Endpoint Tests
```python
# tests/test_api_endpoints.py
import pytest
from fastapi.testclient import TestClient

class TestAPIEndpoints:
    """Test suite for API endpoints"""
    
    def test_health_endpoint(self, client):
        """Test /health endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_chat_endpoint(self, client):
        """Test /api/chat endpoint"""
        response = client.post("/api/chat", json={
            "message": "Hello, test!"
        })
        assert response.status_code == 200
        assert "response" in response.json()
    
    def test_invalid_request(self, client):
        """Test invalid request handling"""
        response = client.post("/api/chat", json={})
        assert response.status_code == 400
```

### File Upload Tests
```python
# tests/test_file_upload.py
import pytest
import io
from pathlib import Path

class TestFileUpload:
    """Test suite for file upload functionality"""
    
    def test_valid_file_upload(self, client):
        """Test uploading a valid file"""
        file_content = b"test file content"
        file_name = "test.txt"
        
        response = client.post(
            "/api/upload",
            files={"file": (file_name, io.BytesIO(file_content))}
        )
        assert response.status_code == 200
        assert "filename" in response.json()
    
    def test_invalid_file_type(self, client):
        """Test rejection of invalid file types"""
        file_content = b"fake exe content"
        file_name = "malware.exe"
        
        response = client.post(
            "/api/upload",
            files={"file": (file_name, io.BytesIO(file_content))}
        )
        assert response.status_code == 400
        assert "error" in response.json()
```

---

## Running Tests (Future State)

### Run All Tests
```bash
# Run all tests with coverage
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_backend.py

# Run specific test function
pytest tests/test_backend.py::TestBackend::test_health
```

### Run Tests by Category
```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only fast tests (exclude slow)
pytest -m "not slow"
```

### Coverage Reports
```bash
# Generate coverage report
pytest --cov=. --cov-report=html

# View coverage in browser
open htmlcov/index.html

# Coverage threshold check
pytest --cov=. --cov-fail-under=80
```

---

## Test Data Management

### Test Fixtures
```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient

@pytest.fixture
def client():
    """Create test client"""
    from main import app
    return TestClient(app)

@pytest.fixture
def sample_text():
    """Sample text for testing"""
    return "This is a sample text for testing purposes."

@pytest.fixture
def mock_chroma_response():
    """Mock ChromaDB response"""
    return {
        "documents": ["Sample document"],
        "metadatas": [{"source": "test"}],
        "distances": [0.123]
    }
```

### Test Data Files
```
tests/
├── fixtures/
│   ├── sample_documents/
│   ├── test_images/
│   └── test_files/
├── conftest.py
└── test_data.py
```

---

## Continuous Integration

### GitHub Actions Example
```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    - name: Run tests
      run: |
        pytest --cov=. --cov-report=xml
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

---

## Debugging Tests

### Common Issues
1. **Import Errors**: Check PYTHONPATH and sys.path
2. **Database Connection**: Use test database, not production
3. **Async Tests**: Use pytest-asyncio for async functions
4. **Mock Issues**: Verify mock configuration and patching

### Debugging Tips
```bash
# Run with pdb debugger
pytest --pdb

# Stop on first failure
pytest -x

# Run with local debugging
pytest --pdb --pdbcls=IPdb.terminal_debugger

# Show local variables on failure
pytest -l
```

---

## Best Practices

### Test Writing
1. **Descriptive Names**: Test names should describe what they test
2. **AAA Pattern**: Arrange-Act-Assert structure
3. **One Assertion**: One assertion per test when possible
4. **Test Isolation**: Tests should not depend on each other
5. **Mock External Dependencies**: Don't test external services

### Test Organization
1. **Group Related Tests**: Use test classes for related functionality
2. **Use Markers**: Mark tests with categories (unit, integration, etc.)
3. **Clear Documentation**: Explain complex test scenarios
4. **Regular Maintenance**: Update tests when code changes

### Performance
1. **Fast Tests**: Keep unit tests fast (<1 second)
2. **Parallel Execution**: Use pytest-xdist for parallel runs
3. **Selective Testing**: Run only relevant tests during development
4. **Test Caching**: Use pytest-cache for expensive operations

---

## Current Test Files Reference

### Existing Tests to Convert
- `test_backend.py` → Convert to pytest with proper assertions
- `test_rag_quality.py` → Add pytest fixtures and markers
- `test_e2e.py` → Convert to proper async tests
- `test_groq.sh` → Convert to Python pytest test
- `test_harmony.sh` → Convert to Python pytest test

### Conversion Priority
1. **High Priority**: test_backend.py, test_rag_quality.py
2. **Medium Priority**: test_e2e.py, test_chroma_query.py
3. **Low Priority**: Shell tests, simple validation tests

---

## Getting Help

### Resources
- **Pytest Documentation**: https://docs.pytest.org/
- **FastAPI Testing**: https://fastapi.tiangolo.com/tutorial/testing/
- **Test Coverage**: https://coverage.readthedocs.io/

### Common Commands
```bash
# Show pytest help
pytest --help

# Show available markers
pytest --markers

# List all tests without running
pytest --collect-only
```

---

**Quick Start Guide Created:** 2026-01-18  
**Next Step:** Set up pytest infrastructure and convert existing tests  
**Priority:** Focus on critical endpoint testing first
