#!/usr/bin/env python3
"""
Simple Flask API for RAG document search.

Run standalone on port 5001: ``python services/rag_api.py`` (repo root as cwd).
"""

import os
from urllib.parse import urlparse

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import chromadb

app = Flask(__name__)
CORS(app)  # Enable CORS for browser access

# Configuration (align with main backend where possible)
OLLAMA_EMBED_URL = os.environ.get("OLLAMA_EMBED_URL", "http://localhost:11435")
_raw_chroma = os.environ.get("CHROMA_HOST", "localhost")
if _raw_chroma.startswith("http://") or _raw_chroma.startswith("https://"):
    _pu = urlparse(_raw_chroma)
    CHROMA_HOST = _pu.hostname or "localhost"
    CHROMA_PORT = int(os.environ.get("CHROMA_PORT", _pu.port or 8000))
elif ":" in _raw_chroma and _raw_chroma.count(":") == 1:
    _h, _, _p = _raw_chroma.partition(":")
    CHROMA_HOST = _h
    CHROMA_PORT = int(os.environ.get("CHROMA_PORT", _p))
else:
    CHROMA_HOST = _raw_chroma
    CHROMA_PORT = int(os.environ.get("CHROMA_PORT", "8000"))
CHROMA_COLLECTION = os.environ.get("CHROMA_COLLECTION", "documents")
RAG_MAX_DISTANCE_CONFIDENT = float(os.environ.get("RAG_MAX_DISTANCE_CONFIDENT", "0.55"))

# Initialize ChromaDB client
client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
collection = client.get_or_create_collection(name=CHROMA_COLLECTION)


def get_embedding(text: str):
    """Generate embedding using nomic-embed"""
    response = requests.post(
        f"{OLLAMA_EMBED_URL}/api/embeddings",
        json={"model": "nomic-embed", "prompt": text},
        timeout=60,
    )
    response.raise_for_status()
    return response.json()["embedding"]


@app.route('/search', methods=['POST'])
def search():
    """Search for relevant document chunks"""
    data = request.json or {}
    query = data.get('query', '')
    n_results = data.get('n_results', 3)

    if not query:
        return jsonify({"error": "No query provided"}), 400

    try:
        # Generate query embedding
        query_embedding = get_embedding(query)

        # Search ChromaDB
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )

        # Format results
        formatted = []
        best_distance = None
        row_docs = results.get("documents") or []
        row_meta = results.get("metadatas") or []
        row_dist = results.get("distances") or []
        n = len(row_docs[0]) if row_docs and row_docs[0] else 0
        for i in range(n):
            dist = None
            if row_dist and row_dist[0] and i < len(row_dist[0]):
                dist = row_dist[0][i]
                if dist is not None:
                    fdist = float(dist)
                    if best_distance is None or fdist < best_distance:
                        best_distance = fdist
            formatted.append({
                "text": row_docs[0][i],
                "metadata": row_meta[0][i] if row_meta and row_meta[0] else {},
                "distance": dist,
            })

        low_confidence = best_distance is None or best_distance > RAG_MAX_DISTANCE_CONFIDENT

        # Wrapped response (hits + meta) for Phase 4 relevance signaling
        return jsonify({
            "hits": formatted,
            "low_confidence": low_confidence,
            "best_distance": best_distance,
            "threshold": RAG_MAX_DISTANCE_CONFIDENT,
            "collection": CHROMA_COLLECTION,
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/list', methods=['GET'])
def list_documents():
    """List all indexed documents"""
    try:
        all_items = collection.get()
        filenames = set()

        if all_items['metadatas']:
            for metadata in all_items['metadatas']:
                filenames.add(metadata.get('filename', 'unknown'))

        return jsonify({"documents": sorted(list(filenames))})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok", "service": "RAG API"})


if __name__ == '__main__':
    print("🚀 Starting RAG API server on http://localhost:5001")
    app.run(host='0.0.0.0', port=5001, debug=False)
