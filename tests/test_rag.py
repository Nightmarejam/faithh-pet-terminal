#!/usr/bin/env python3
"""RAG processor tests — require ChromaDB + Ollama running."""
import sys
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))


def _services_available():
    """Check if ChromaDB and Ollama are reachable."""
    import requests
    try:
        requests.get("http://localhost:8000/api/v2/heartbeat", timeout=3)
        requests.get("http://localhost:11434/api/tags", timeout=3)
        return True
    except Exception:
        return False


skipif_no_services = pytest.mark.skipif(
    not _services_available(),
    reason="ChromaDB or Ollama not running"
)


@skipif_no_services
def test_rag_processor_init():
    """RAGProcessor can connect to ChromaDB."""
    from rag_processor import RAGProcessor
    proc = RAGProcessor()
    assert proc.collection is not None


@skipif_no_services
def test_rag_search_returns_results():
    """Search returns a list of results."""
    from rag_processor import RAGProcessor
    proc = RAGProcessor()
    results = proc.search("FAITHH project structure", n_results=3)
    assert isinstance(results, list)
    # May be empty if no docs indexed in 'documents' collection


@skipif_no_services
def test_rag_chunking():
    """Chunk text produces valid chunks."""
    from rag_processor import RAGProcessor
    proc = RAGProcessor()
    chunks = proc.chunk_text("Hello world. " * 200, "test.txt")
    assert len(chunks) > 0
    assert all("id" in c and "text" in c and "metadata" in c for c in chunks)
