#!/usr/bin/env python3
"""
Index Constella Constitutional Principles and Evidence Mapping into ChromaDB

This script reads:
1. constitutional_principles.json from constella-framework repo
2. projects/constella-framework/docs/governance/alife_evidence_mapping.md

And indexes them into ChromaDB collection 'faithh_knowledge_base' with domain='constella_constitutional'
"""

import json
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import chromadb
    from chromadb.config import Settings
except ImportError:
    print("ERROR: chromadb not installed. Install with: pip install chromadb")
    sys.exit(1)

# Configuration
CONSTELLA_FRAMEWORK_PATH = os.getenv('CONSTELLA_FRAMEWORK_PATH', 
                                    '/home/jonat/ai-stack/projects/constella-framework')
PRINCIPLES_JSON_PATH = os.path.join(CONSTELLA_FRAMEWORK_PATH, 'config', 'constitutional_principles.json')
MAPPING_MD_PATH = os.path.join(CONSTELLA_FRAMEWORK_PATH, 'docs', 'governance', 'alife_evidence_mapping.md')

CHROMA_HOST = os.getenv('CHROMA_HOST', 'servicebox.taileb8c60.ts.net')
CHROMA_PORT = os.getenv('CHROMA_PORT', '8000')
COLLECTION_NAME = 'faithh_knowledge_base'
DOMAIN = 'constella_constitutional'


def connect_to_chroma():
    """Connect to ChromaDB instance"""
    try:
        client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
        collection = client.get_or_create_collection(name=COLLECTION_NAME)
        return client, collection
    except Exception as e:
        print(f"ERROR: Failed to connect to ChromaDB at {CHROMA_HOST}:{CHROMA_PORT}")
        print(f"Details: {e}")
        sys.exit(1)


def load_principles():
    """Load constitutional principles from JSON"""
    try:
        with open(PRINCIPLES_JSON_PATH, 'r') as f:
            principles = json.load(f)
        print(f"Loaded {len(principles)} principles from {PRINCIPLES_JSON_PATH}")
        return principles
    except FileNotFoundError:
        print(f"ERROR: Principles file not found: {PRINCIPLES_JSON_PATH}")
        print("Set CONSTELLA_FRAMEWORK_PATH environment variable if using custom path")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in principles file: {e}")
        sys.exit(1)


def load_mapping_document():
    """Load the evidence mapping markdown document"""
    try:
        with open(MAPPING_MD_PATH, 'r') as f:
            content = f.read()
        print(f"Loaded mapping document from {MAPPING_MD_PATH}")
        return content
    except FileNotFoundError:
        print(f"ERROR: Mapping document not found: {MAPPING_MD_PATH}")
        sys.exit(1)


def chunk_mapping_document(content):
    """Chunk the mapping document into logical sections"""
    chunks = []
    
    # Find section boundaries
    lines = content.split('\n')
    ucf_start = None
    penumbra_start = None
    table_start = None
    
    for i, line in enumerate(lines):
        if '### 1. Universal Civic Floor (UCF)' in line:
            ucf_start = i
        elif '### 2. Penumbra Accord' in line:
            penumbra_start = i
        elif '| Finding | Evidence Type | External Validation |' in line:
            table_start = i
    
    # UCF section (from UCF start to before Penumbra)
    if ucf_start is not None and penumbra_start is not None:
        ucf_lines = lines[ucf_start:penumbra_start]
        ucf_content = '\n'.join(ucf_lines)
        chunks.append({
            'id': 'constella-ucf-section',
            'content': ucf_content,
            'title': 'Universal Civic Floor - ALife Evidence',
            'section': 'ucf'
        })
    
    # Penumbra section (from Penumbra start to before table)
    if penumbra_start is not None and table_start is not None:
        penumbra_lines = lines[penumbra_start:table_start]
        penumbra_content = '\n'.join(penumbra_lines)
        chunks.append({
            'id': 'constella-penumbra-section',
            'content': penumbra_content,
            'title': 'Penumbra Accord - ALife Evidence',
            'section': 'penumbra'
        })
    
    # Full epistemic status table
    if table_start is not None:
        table_lines = lines[table_start:]
        table_content = '\n'.join(table_lines)
        chunks.append({
            'id': 'constella-epistemic-table',
            'content': table_content,
            'title': 'Epistemic Status Summary - All Findings',
            'section': 'epistemic'
        })
    
    return chunks


def index_principles(collection, principles):
    """Index constitutional principles as individual documents"""
    indexed_count = 0
    
    for principle in principles:
        # Create document content
        content = f"""{principle['name']}

Mechanism: {principle['mechanism']}
Evidence Type: {principle['evidence_type']}
Experiments: {', '.join(principle['experiment_ids'])}
Confidence: {principle['confidence']}

Summary: {principle['summary']}
"""
        
        # Metadata
        metadata = {
            'domain': DOMAIN,
            'document_type': 'principle',
            'principle_id': principle['id'],
            'mechanism': principle['mechanism'],
            'evidence_type': principle['evidence_type'],
            'experiment_ids': ','.join(principle['experiment_ids']),  # Convert list to string
            'confidence': principle['confidence'],
            'title': principle['name']
        }
        
        # Add to collection
        try:
            collection.add(
                documents=[content],
                metadatas=[metadata],
                ids=[f"{DOMAIN}-principle-{principle['id']}"]
            )
            indexed_count += 1
        except Exception as e:
            print(f"WARNING: Failed to index principle {principle['id']}: {e}")
    
    print(f"Indexed {indexed_count} constitutional principles")
    return indexed_count


def index_mapping_chunks(collection, chunks):
    """Index mapping document chunks"""
    indexed_count = 0
    
    for chunk in chunks:
        # Metadata
        metadata = {
            'domain': DOMAIN,
            'document_type': 'mapping_section',
            'section': chunk['section'],
            'title': chunk['title']
        }
        
        # Add to collection
        try:
            collection.add(
                documents=[chunk['content']],
                metadatas=[metadata],
                ids=[f"{DOMAIN}-mapping-{chunk['id']}"]
            )
            indexed_count += 1
        except Exception as e:
            print(f"WARNING: Failed to index chunk {chunk['id']}: {e}")
    
    print(f"Indexed {indexed_count} mapping document chunks")
    return indexed_count


def get_collection_count(collection):
    """Get current document count in collection"""
    try:
        count = collection.count()
        return count
    except Exception as e:
        print(f"WARNING: Could not get collection count: {e}")
        return 0


def clear_existing_constitional_docs(collection):
    """Clear existing constitutional documents before reindexing"""
    try:
        # Get all documents with domain=constella_constitutional
        results = collection.get(
            where={'domain': DOMAIN}
        )
        
        if results['ids']:
            collection.delete(ids=results['ids'])
            print(f"Cleared {len(results['ids'])} existing constitutional documents")
        else:
            print("No existing constitutional documents to clear")
            
    except Exception as e:
        print(f"WARNING: Failed to clear existing documents: {e}")


def main():
    print("=" * 60)
    print("Constella Constitutional Indexing Script")
    print("=" * 60)
    print(f"Constella Framework Path: {CONSTELLA_FRAMEWORK_PATH}")
    print(f"ChromaDB: {CHROMA_HOST}:{CHROMA_PORT}")
    print(f"Collection: {COLLECTION_NAME}")
    print(f"Domain: {DOMAIN}")
    print("=" * 60)
    
    # Connect to ChromaDB
    client, collection = connect_to_chroma()
    
    # Get initial count
    initial_count = get_collection_count(collection)
    print(f"Initial collection count: {initial_count}")
    
    # Clear existing constitutional documents
    clear_existing_constitional_docs(collection)
    
    # Load data
    principles = load_principles()
    mapping_content = load_mapping_document()
    
    # Process mapping document
    mapping_chunks = chunk_mapping_document(mapping_content)
    print(f"Created {len(mapping_chunks)} mapping document chunks")
    
    # Index principles
    principles_indexed = index_principles(collection, principles)
    
    # Index mapping chunks
    chunks_indexed = index_mapping_chunks(collection, mapping_chunks)
    
    # Get final count
    final_count = get_collection_count(collection)
    
    print("\n" + "=" * 60)
    print("INDEXING COMPLETE")
    print("=" * 60)
    print(f"Principles indexed: {principles_indexed}")
    print(f"Mapping chunks indexed: {chunks_indexed}")
    print(f"Total new documents: {principles_indexed + chunks_indexed}")
    print(f"Collection count before: {initial_count}")
    print(f"Collection count after: {final_count}")
    print("=" * 60)


if __name__ == '__main__':
    main()
