#!/usr/bin/env python3
"""
Constella Knowledge Discovery System

Searches existing conversation history to fill gaps in the master reference.
Outputs discoveries for review before updating the master doc.

Usage:
    python discover_constella.py                    # Run all discovery queries
    python discover_constella.py --section ucf      # Run specific section
    python discover_constella.py --interactive      # Interactive mode
"""

import chromadb
from chromadb.utils import embedding_functions
import json
from datetime import datetime
from pathlib import Path
import argparse

# Discovery queries for each unknown/partial section
DISCOVERY_QUERIES = {
    "ucf": {
        "section": "UCF (Unified Civic Framework)",
        "queries": [
            "UCF unified civic framework constella governance",
            "UCF compliance verification mechanism",
            "how does UCF work in constella",
            "UCF rules governance structure"
        ],
        "confidence": "partial",
        "seeking": [
            "Specific mechanisms within UCF",
            "How UCF relates to other components",
            "Examples of UCF in practice"
        ]
    },
    "tokens": {
        "section": "Tokens (Astris / Auctor)",
        "queries": [
            "Astris Auctor token governance",
            "how are tokens earned constella",
            "token voting participation governance",
            "Astris star token meaning",
            "Auctor author creator token"
        ],
        "confidence": "partial",
        "seeking": [
            "How tokens are earned",
            "How tokens are used in governance",
            "Relationship between Astris and Auctor",
            "How they amplify voices of those with weak resonance"
        ]
    },
    "tome": {
        "section": "Civic Tome",
        "queries": [
            "civic tome documentation decision",
            "tome entry structure format",
            "how to create tome entry",
            "tome governance transparency"
        ],
        "confidence": "partial",
        "seeking": [
            "Tome entry structure",
            "How entries are created",
            "How the Tome is referenced in governance"
        ]
    },
    "penumbra": {
        "section": "Penumbra Accord",
        "queries": [
            "penumbra accord constella",
            "penumbra edge case boundary",
            "penumbra exception governance",
            "what is penumbra in constella"
        ],
        "confidence": "unknown",
        "seeking": [
            "Definition of 'penumbra' in Constella context",
            "What situations the Accord governs",
            "How it handles edge cases"
        ]
    },
    "map_of_intent": {
        "section": "Map of Intent",
        "queries": [
            "map of intent constella",
            "intent alignment goal",
            "purpose mapping governance",
            "how intents are recorded"
        ],
        "confidence": "unknown",
        "seeking": [
            "What the Map tracks/documents",
            "How intents are recorded",
            "When the Map is referenced"
        ]
    },
    "relationships": {
        "section": "Component Relationships",
        "queries": [
            "how constella components connect",
            "decision flow governance process",
            "tokens tome UCF relationship",
            "constella system architecture"
        ],
        "confidence": "unknown",
        "seeking": [
            "How do decisions flow through the system?",
            "Which component triggers which?",
            "What's the information flow?"
        ]
    },
    "decisions": {
        "section": "Key Design Decisions",
        "queries": [
            "we decided constella",
            "design decision governance",
            "chose this approach because",
            "constella architecture decision"
        ],
        "confidence": "unknown",
        "seeking": [
            "Major architectural choices",
            "Reasoning behind decisions",
            "Trade-offs considered"
        ]
    }
}


def connect_chromadb():
    """Connect to ChromaDB and return collection"""
    try:
        client = chromadb.HttpClient(host="localhost", port=8000)
        embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-mpnet-base-v2"
        )
        collection = client.get_collection(
            name="documents_768",
            embedding_function=embedding_func
        )
        print(f"✅ Connected to ChromaDB: {collection.count()} documents")
        return collection
    except Exception as e:
        print(f"❌ ChromaDB connection failed: {e}")
        return None


def search_for_section(collection, section_key, n_results=5):
    """Search for information about a specific section"""
    config = DISCOVERY_QUERIES[section_key]
    
    print(f"\n{'='*60}")
    print(f"🔍 Discovering: {config['section']}")
    print(f"   Current confidence: {config['confidence'].upper()}")
    print(f"   Seeking: {', '.join(config['seeking'][:2])}...")
    print(f"{'='*60}")
    
    all_results = []
    seen_ids = set()
    
    for query in config['queries']:
        try:
            # Search conversation chunks first
            results = collection.query(
                query_texts=[query],
                n_results=n_results,
                where={"$or": [
                    {"category": "claude_conversation_chunk"},
                    {"category": "claude_conversation"},
                    {"category": "documentation"}
                ]}
            )
            
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    doc_id = results['ids'][0][i] if results['ids'] else f"unknown_{i}"
                    
                    # Skip duplicates
                    if doc_id in seen_ids:
                        continue
                    seen_ids.add(doc_id)
                    
                    distance = results['distances'][0][i] if results['distances'] else 1.0
                    metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                    
                    # Only include good matches
                    if distance < 0.7:
                        all_results.append({
                            'query': query,
                            'document': doc,
                            'distance': distance,
                            'id': doc_id,
                            'metadata': metadata,
                            'relevance': 'high' if distance < 0.4 else 'medium'
                        })
        except Exception as e:
            print(f"   ⚠️ Query failed: {query[:30]}... - {e}")
    
    # Sort by distance (best matches first)
    all_results.sort(key=lambda x: x['distance'])
    
    return all_results[:10]  # Return top 10


def display_results(results, section_key):
    """Display discovery results in a readable format"""
    config = DISCOVERY_QUERIES[section_key]
    
    if not results:
        print(f"\n❌ No relevant information found for {config['section']}")
        print(f"   This section remains: {config['confidence'].upper()}")
        return
    
    print(f"\n📚 Found {len(results)} relevant passages:")
    print("-" * 60)
    
    for i, result in enumerate(results, 1):
        print(f"\n[{i}] Relevance: {result['relevance'].upper()} (distance: {result['distance']:.3f})")
        print(f"    Query: \"{result['query']}\"")
        
        # Show preview of document
        doc_preview = result['document'][:500].replace('\n', ' ')
        if len(result['document']) > 500:
            doc_preview += "..."
        print(f"    Content: {doc_preview}")
        
        # Show metadata if available
        if result['metadata']:
            category = result['metadata'].get('category', 'unknown')
            timestamp = result['metadata'].get('timestamp', 'unknown')
            print(f"    Source: {category} | {timestamp}")
    
    print("-" * 60)


def save_discoveries(all_discoveries, output_path):
    """Save discoveries to a JSON file for review"""
    output = {
        'discovered_at': datetime.now().isoformat(),
        'sections': all_discoveries,
        'summary': {
            'total_discoveries': sum(len(d['results']) for d in all_discoveries.values()),
            'sections_with_finds': len([d for d in all_discoveries.values() if d['results']]),
            'sections_empty': len([d for d in all_discoveries.values() if not d['results']])
        }
    }
    
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2, default=str)
    
    print(f"\n💾 Discoveries saved to: {output_path}")
    return output


def generate_update_suggestions(discoveries):
    """Generate suggestions for updating the master reference"""
    suggestions = []
    
    for section_key, data in discoveries.items():
        if not data['results']:
            continue
            
        config = DISCOVERY_QUERIES[section_key]
        
        # Get the best result
        best = data['results'][0]
        
        suggestion = {
            'section': config['section'],
            'current_confidence': config['confidence'],
            'suggested_confidence': 'partial' if config['confidence'] == 'unknown' else 'known',
            'top_finding': best['document'][:300],
            'relevance': best['relevance'],
            'action': f"Review finding and update {config['section']} section"
        }
        suggestions.append(suggestion)
    
    return suggestions


def interactive_mode(collection):
    """Interactive discovery mode"""
    print("\n🔮 Interactive Discovery Mode")
    print("Type a section name or 'all' to discover, 'quit' to exit")
    print(f"Available sections: {', '.join(DISCOVERY_QUERIES.keys())}")
    
    while True:
        choice = input("\n> ").strip().lower()
        
        if choice == 'quit':
            break
        elif choice == 'all':
            run_all_discoveries(collection)
        elif choice in DISCOVERY_QUERIES:
            results = search_for_section(collection, choice)
            display_results(results, choice)
        else:
            print(f"Unknown section. Available: {', '.join(DISCOVERY_QUERIES.keys())}")


def run_all_discoveries(collection):
    """Run discovery for all sections"""
    all_discoveries = {}
    
    for section_key in DISCOVERY_QUERIES:
        results = search_for_section(collection, section_key)
        display_results(results, section_key)
        all_discoveries[section_key] = {
            'config': DISCOVERY_QUERIES[section_key],
            'results': results
        }
    
    # Save discoveries
    output_path = Path.home() / "ai-stack/docs/constella_discoveries.json"
    save_discoveries(all_discoveries, output_path)
    
    # Generate suggestions
    suggestions = generate_update_suggestions(all_discoveries)
    
    print("\n" + "=" * 60)
    print("📋 UPDATE SUGGESTIONS")
    print("=" * 60)
    
    for s in suggestions:
        print(f"\n✏️  {s['section']}")
        print(f"   Current: {s['current_confidence']} → Suggested: {s['suggested_confidence']}")
        print(f"   Top finding ({s['relevance']}): {s['top_finding'][:100]}...")
    
    return all_discoveries


def main():
    parser = argparse.ArgumentParser(description='Constella Knowledge Discovery')
    parser.add_argument('--section', type=str, help='Specific section to discover')
    parser.add_argument('--interactive', action='store_true', help='Interactive mode')
    args = parser.parse_args()
    
    print("🔍 Constella Knowledge Discovery System")
    print("=" * 60)
    
    collection = connect_chromadb()
    if not collection:
        return
    
    if args.interactive:
        interactive_mode(collection)
    elif args.section:
        if args.section in DISCOVERY_QUERIES:
            results = search_for_section(collection, args.section)
            display_results(results, args.section)
        else:
            print(f"Unknown section: {args.section}")
            print(f"Available: {', '.join(DISCOVERY_QUERIES.keys())}")
    else:
        run_all_discoveries(collection)


if __name__ == "__main__":
    main()
