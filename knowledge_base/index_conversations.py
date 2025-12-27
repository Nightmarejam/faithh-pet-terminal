#!/usr/bin/env python3
"""
FAITHH Knowledge Base Indexer
Indexes conversations from ChatGPT, Claude, and Grok into ChromaDB with BGE embeddings.
"""

import json
import os
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

# === CONFIGURATION ===
CHROMADB_HOST = "100.79.85.32"
CHROMADB_PORT = 8000
COLLECTION_NAME = "faithh_knowledge_base"
EMBEDDING_MODEL = "BAAI/bge-base-en-v1.5"
CHUNK_SIZE = 2000  # characters
CHUNK_OVERLAP = 200

# Project detection keywords
PROJECT_KEYWORDS = {
    "faithh": ["faithh", "pulse", "rag", "chromadb", "ai-stack", "backend", 
               "resonance journal", "scaffolding", "ollama", "groq", "embedding"],
    "constella": ["constella", "harmony", "civic", "penumbra", "thread",
                  "resonance", "framework", "governance", "equilibrium", "sky lattice"],
    "tomcat": ["tom cat", "floating garden", "mastering", "mixing", 
               "audio production", "wavelab", "presonus", "volt", "soundid"],
    "personal": ["adhd", "health", "family", "schedule", "california", "oregon"],
}

class KnowledgeBaseIndexer:
    def __init__(self):
        print(f"🔌 Connecting to ChromaDB at {CHROMADB_HOST}:{CHROMADB_PORT}...")
        self.client = chromadb.HttpClient(
            host=CHROMADB_HOST,
            port=CHROMADB_PORT,
        )
        
        print(f"📦 Loading embedding model: {EMBEDDING_MODEL}...")
        self.embedder = SentenceTransformer(EMBEDDING_MODEL)
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"description": "FAITHH Knowledge Base with BGE embeddings"}
        )
        print(f"✅ Collection '{COLLECTION_NAME}' ready. Current count: {self.collection.count()}")
    
    def detect_project(self, text: str) -> str:
        """Detect project based on keywords in text."""
        text_lower = text.lower()
        scores = {}
        for project, keywords in PROJECT_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > 0:
                scores[project] = score
        
        if scores:
            return max(scores, key=scores.get)
        return "general"
    
    def extract_topics(self, text: str) -> List[str]:
        """Extract simple topic tags from text."""
        topics = []
        topic_patterns = {
            "code": r"```|def |class |function |import ",
            "api": r"api|endpoint|request|response",
            "database": r"database|sql|chromadb|postgres|sqlite",
            "audio": r"audio|sound|mixing|mastering|wav|daw",
            "ai": r"llm|gpt|claude|model|embedding|neural",
            "infrastructure": r"server|docker|ssh|tailscale|network",
        }
        text_lower = text.lower()
        for topic, pattern in topic_patterns.items():
            if re.search(pattern, text_lower):
                topics.append(topic)
        return topics[:5]  # Max 5 topics
    
    def chunk_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks."""
        if len(text) <= CHUNK_SIZE:
            return [text]
        
        chunks = []
        start = 0
        while start < len(text):
            end = start + CHUNK_SIZE
            chunk = text[start:end]
            
            # Try to break at sentence boundary
            if end < len(text):
                last_period = chunk.rfind('. ')
                last_newline = chunk.rfind('\n')
                break_point = max(last_period, last_newline)
                if break_point > CHUNK_SIZE // 2:
                    chunk = chunk[:break_point + 1]
                    end = start + break_point + 1
            
            chunks.append(chunk.strip())
            start = end - CHUNK_OVERLAP
        
        return [c for c in chunks if len(c) > 50]  # Filter tiny chunks

    def parse_chatgpt(self, filepath: str) -> List[Dict]:
        """Parse ChatGPT export format."""
        print(f"  📖 Parsing ChatGPT export...")
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        documents = []
        for conv in data:
            title = conv.get('title', 'Untitled')
            create_time = conv.get('create_time', 0)
            
            # Extract messages from mapping
            mapping = conv.get('mapping', {})
            messages = []
            for node_id, node in mapping.items():
                msg = node.get('message')
                if msg and msg.get('content', {}).get('parts'):
                    role = msg.get('author', {}).get('role', 'unknown')
                    # Handle parts that can be strings or dicts (images)
                    parts = msg['content']['parts']
                    text_parts = []
                    for p in parts:
                        if isinstance(p, str):
                            text_parts.append(p)
                        elif isinstance(p, dict) and p.get('content_type') == 'text':
                            text_parts.append(p.get('text', ''))
                        # Skip image_asset_pointer and other non-text content
                    content = '\n'.join(text_parts)
                    if content.strip() and role in ['user', 'assistant']:
                        messages.append({
                            'role': role,
                            'content': content,
                            'create_time': msg.get('create_time', create_time)
                        })
            
            # Create document from conversation
            if messages:
                full_text = f"# {title}\n\n"
                for msg in messages:
                    full_text += f"**{msg['role'].upper()}:** {msg['content']}\n\n"
                
                documents.append({
                    'content': full_text,
                    'source': 'chatgpt',
                    'title': title,
                    'created_at': datetime.fromtimestamp(create_time).isoformat() if create_time else None,
                    'conversation_id': conv.get('id', str(uuid.uuid4())),
                })
        
        print(f"    Found {len(documents)} conversations")
        return documents

    def parse_claude(self, filepath: str) -> List[Dict]:
        """Parse Claude export format."""
        print(f"  📖 Parsing Claude export...")
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        documents = []
        for conv in data:
            title = conv.get('name', 'Untitled')
            created_at = conv.get('created_at', '')
            
            messages = conv.get('chat_messages', [])
            if messages:
                full_text = f"# {title}\n\n"
                for msg in messages:
                    role = msg.get('sender', 'unknown')
                    content = msg.get('text', '')
                    if content.strip():
                        full_text += f"**{role.upper()}:** {content}\n\n"
                
                documents.append({
                    'content': full_text,
                    'source': 'claude',
                    'title': title,
                    'created_at': created_at,
                    'conversation_id': conv.get('uuid', str(uuid.uuid4())),
                })
        
        print(f"    Found {len(documents)} conversations")
        return documents

    def parse_grok(self, filepath: str) -> List[Dict]:
        """Parse Grok/X export format."""
        print(f"  📖 Parsing Grok export...")
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        documents = []
        conversations = data.get('conversations', [])
        
        for conv in conversations:
            title = conv.get('title', 'Grok Conversation')
            created_at = conv.get('createTime', '')
            
            messages = conv.get('messages', [])
            if messages:
                full_text = f"# {title}\n\n"
                for msg in messages:
                    role = msg.get('role', 'unknown')
                    content = msg.get('message', '')
                    if content.strip():
                        full_text += f"**{role.upper()}:** {content}\n\n"
                
                documents.append({
                    'content': full_text,
                    'source': 'grok',
                    'title': title,
                    'created_at': created_at,
                    'conversation_id': conv.get('conversationId', str(uuid.uuid4())),
                })
        
        print(f"    Found {len(documents)} conversations")
        return documents

    def index_documents(self, documents: List[Dict]):
        """Index documents into ChromaDB."""
        print(f"\n📊 Indexing {len(documents)} documents...")
        
        all_chunks = []
        all_metadatas = []
        all_ids = []
        
        for doc in documents:
            chunks = self.chunk_text(doc['content'])
            project = self.detect_project(doc['content'])
            topics = self.extract_topics(doc['content'])
            
            for i, chunk in enumerate(chunks):
                chunk_id = f"{doc['source']}_{doc['conversation_id']}_{i}"
                
                metadata = {
                    'source': doc['source'],
                    'title': doc['title'][:200] if doc['title'] else 'Untitled',
                    'project': project,
                    'topics': ','.join(topics),
                    'chunk_index': i,
                    'total_chunks': len(chunks),
                    'conversation_id': doc['conversation_id'],
                    'created_at': doc['created_at'] or '',
                    'indexed_at': datetime.now().isoformat(),
                    'has_code': '```' in chunk,
                }
                
                all_chunks.append(chunk)
                all_metadatas.append(metadata)
                all_ids.append(chunk_id)
        
        print(f"  📝 Created {len(all_chunks)} chunks")
        print(f"  🧠 Generating embeddings (this may take a few minutes)...")
        
        # Batch process embeddings
        batch_size = 100
        for i in range(0, len(all_chunks), batch_size):
            batch_end = min(i + batch_size, len(all_chunks))
            batch_chunks = all_chunks[i:batch_end]
            batch_metas = all_metadatas[i:batch_end]
            batch_ids = all_ids[i:batch_end]
            
            # Generate embeddings
            embeddings = self.embedder.encode(batch_chunks, show_progress_bar=False).tolist()
            
            # Add to ChromaDB
            self.collection.add(
                documents=batch_chunks,
                metadatas=batch_metas,
                embeddings=embeddings,
                ids=batch_ids,
            )
            
            print(f"    ✅ Indexed {batch_end}/{len(all_chunks)} chunks")
        
        print(f"\n✅ Indexing complete! Total chunks in collection: {self.collection.count()}")

    def test_query(self, query: str, n_results: int = 3):
        """Test a query against the knowledge base."""
        print(f"\n🔍 Testing query: '{query}'")
        
        query_embedding = self.embedder.encode([query]).tolist()
        
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results,
            include=['documents', 'metadatas', 'distances']
        )
        
        print(f"\nTop {n_results} results:")
        for i, (doc, meta, dist) in enumerate(zip(
            results['documents'][0],
            results['metadatas'][0],
            results['distances'][0]
        )):
            print(f"\n--- Result {i+1} (distance: {dist:.4f}) ---")
            print(f"Source: {meta['source']} | Project: {meta['project']} | Title: {meta['title'][:50]}")
            print(f"Content: {doc[:200]}...")


def main():
    base_path = Path(__file__).parent / "imports"
    
    indexer = KnowledgeBaseIndexer()
    
    all_documents = []
    
    # Parse ChatGPT
    chatgpt_path = base_path / "chatgpt" / "conversations.json"
    if chatgpt_path.exists():
        all_documents.extend(indexer.parse_chatgpt(str(chatgpt_path)))
    
    # Parse Claude
    claude_path = base_path / "claude" / "conversations.json"
    if claude_path.exists():
        all_documents.extend(indexer.parse_claude(str(claude_path)))
    
    # Parse Grok
    grok_path = base_path / "grok" / "prod-grok-backend.json"
    if grok_path.exists():
        all_documents.extend(indexer.parse_grok(str(grok_path)))
    
    if all_documents:
        indexer.index_documents(all_documents)
        
        # Test queries
        indexer.test_query("How do I configure ChromaDB?")
        indexer.test_query("FAITHH backend setup")
        indexer.test_query("audio mastering workflow")
    else:
        print("❌ No documents found to index!")


if __name__ == "__main__":
    main()
