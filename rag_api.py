#!/usr/bin/env python3
"""
Simple Flask API for RAG document search
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import chromadb

app = Flask(__name__)
CORS(app)  # Enable CORS for browser access

# Configuration
OLLAMA_EMBED_URL = "http://localhost:11435"
CHROMA_HOST = "localhost"
CHROMA_PORT = 8000

# Initialize ChromaDB client
client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
collection = client.get_or_create_collection(name="documents")


def get_embedding(text: str):
    """Generate embedding using nomic-embed"""
    response = requests.post(
        f"{OLLAMA_EMBED_URL}/api/embeddings",
        json={"model": "nomic-embed", "prompt": text}
    )
    response.raise_for_status()
    return response.json()["embedding"]


@app.route('/search', methods=['POST'])
def search():
    """Search for relevant document chunks"""
    data = request.json
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
        for i in range(len(results['documents'][0])):
            formatted.append({
                "text": results['documents'][0][i],
                "metadata": results['metadatas'][0][i],
                "distance": results['distances'][0][i] if 'distances' in results else None
            })
        
        return jsonify(formatted)
    
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