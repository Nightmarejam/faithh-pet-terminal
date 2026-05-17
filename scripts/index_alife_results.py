#!/usr/bin/env python3
"""
FAITHH ALife Results Indexing Script
===================================
Indexes verified ALife experiment results into the knowledge base.

This script indexes 4 verified experiment result documents with exact
values as provided. No inference or generation of values.
"""

import chromadb
from sentence_transformers import SentenceTransformer
embedder = SentenceTransformer('all-MiniLM-L6-v2')

def index_alife_results():
    """Index ALife experiment results into knowledge base"""
    
    # Document 1 - Experiment 3 Results
    doc1_content = """Experiment 3: The Anticipation Gap — Verified Results
Final population: 873 agents
Total reproductions: 443,708
Total deaths: 443,035  
Total memory emergences: 129,345
First negative anticipation gap: tick 402, agent_861, gap=-2
Peak negative gap percentage: 138.5% at tick 85,000
All thresholds crossed: 1%, 5%, 10%, 25%, 50%
Outcome: FULL_SUCCESS
Red Queen oscillating pattern confirmed.
Negative anticipation gap confirmed — agents phase-locking 
to wave beat frequency before wave arrives."""
    
    # Document 2 - Experiment 4 Results
    doc2_content = """Experiment 4: Harmonic Interference — Verified Results
Wave 1: left_to_right, interval=600 ticks
Wave 2: right_to_left, interval=900 ticks
Beat frequency: 1800 ticks
MIN_ARRIVAL_GAP bug: was 50, fixed to 10
Wave 2 arrival recording confirmed working after fix.
PROC_BEAT (dual-source prediction) did not outcompete 
PROC_PREDICT in 200K run.
Finding: single-interval prediction persists because it 
is cheaper. Dual-interval prediction needs stronger 
selection pressure at the interference zone.
Final population: 837
Outcome: RED_QUEEN_CONTINUES"""
    
    # Document 3 - Experiment 5 Results
    doc3_content = """Experiment 5: Parasitic Emergence — Verified Results
Run A (drain=3): first parasite tick 1377 gen 12,
  parasites peaked at 240 (30% of population) tick 5000,
  crashed to 0 by tick 6000. Outcome: FULL_OFFENSIVE_STACK
Run B (drain=1): first parasite tick 5125 gen 41,
  never established stable population. Outcome: FULL_OFFENSIVE_STACK
Run C (drain=2): first parasite tick 2812 gen 28,
  population collapsed tick 5787. Outcome: FULL_OFFENSIVE_STACK
Finding: all drain rates produced boom-bust not stable 
oscillation. Drain=1.5 not yet tested."""
    
    # Document 4 - PROC_BEAT Explanation
    doc4_content = """PROC_BEAT is the dual-source wave arrival prediction 
operator in the ALife genome. It stores arrival times 
from both Wave 1 (left_to_right) and Wave 2 
(right_to_left) separately. It attempts to predict 
when the next wave from each direction will arrive 
by computing intervals between past arrivals.
PROC_BEAT failed to dominate in Experiment 4 because:
1. PROC_PREDICT (single-source) is cheaper to execute
2. PROC_PREDICT provides sufficient survival advantage 
   in most of the world outside the interference zone
3. The interference zone (columns 160-320) does not 
   create strong enough selection pressure to overcome 
   PROC_PREDICT's advantage in the rest of the world
4. Agents with PROC_BEAT only outperform at interference 
   zone antinodes, not enough population pressure 
   to spread genome-wide"""
    
    # Documents to index
    documents = [
        {
            "id": "exp3_verified_results",
            "content": doc1_content,
            "metadata": {
                "source_type": "alife_experiment",
                "domain": "alife",
                "quality_score": 1.0,
                "is_verified": True,
                "experiment": 3,
                "title": "Experiment 3: The Anticipation Gap"
            }
        },
        {
            "id": "exp4_verified_results", 
            "content": doc2_content,
            "metadata": {
                "source_type": "alife_experiment",
                "domain": "alife",
                "quality_score": 1.0,
                "is_verified": True,
                "experiment": 4,
                "title": "Experiment 4: Harmonic Interference"
            }
        },
        {
            "id": "exp5_verified_results",
            "content": doc3_content,
            "metadata": {
                "source_type": "alife_experiment",
                "domain": "alife",
                "quality_score": 1.0,
                "is_verified": True,
                "experiment": 5,
                "title": "Experiment 5: Parasitic Emergence"
            }
        },
        {
            "id": "proc_beat_explanation",
            "content": doc4_content,
            "metadata": {
                "source_type": "alife_experiment",
                "domain": "alife",
                "quality_score": 1.0,
                "is_verified": True,
                "title": "PROC_BEAT Explanation"
            }
        }
    ]
    
    print("🧬 FAITHH ALife Results Indexing")
    print("=" * 50)
    
    try:
        # Connect to ChromaDB using same settings as backend
        chroma_client = chromadb.HttpClient(host="192.158.1.10", port=8000)
        collection_name = "faithh_knowledge_base"
        
        # Get or create collection
        try:
            collection = chroma_client.get_collection(name=collection_name)
            print(f"✅ Connected to existing collection: {collection_name}")
        except:
            collection = chroma_client.create_collection(name=collection_name)
            print(f"✅ Created new collection: {collection_name}")
        
        # Get initial count
        initial_count = collection.count()
        print(f"📚 Initial collection count: {initial_count}")
        
        # Delete the 4 incorrectly-indexed documents first
        print(f"\n🗑️  Deleting existing ALife documents...")
        try:
            collection.delete(ids=[
                'exp3_verified_results',
                'exp4_verified_results', 
                'exp5_verified_results',
                'proc_beat_explanation'
            ])
            print(f"✅ Deleted existing ALife documents")
        except Exception as e:
            print(f"⚠️  Delete failed (may not exist): {e}")
        
        # Get count after deletion
        count_after_delete = collection.count()
        print(f"📚 Count after deletion: {count_after_delete}")
        
        # Index each document with explicit embeddings
        indexed_count = 0
        for doc in documents:
            try:
                print(f"\n📝 Indexing: {doc['id']}")
                
                # Generate embedding explicitly
                text = doc['content']
                print(f"   🧠 Generating embedding...")
                embedding = embedder.encode(text).tolist()
                print(f"   ✅ Embedding generated (length: {len(embedding)})")
                
                # Add document to collection with explicit embedding
                collection.add(
                    ids=[doc['id']],
                    documents=[text],
                    embeddings=[embedding],
                    metadatas=[doc['metadata']]
                )
                
                indexed_count += 1
                print(f"   ✅ Indexed successfully with embedding")
                
            except Exception as e:
                print(f"   ❌ Failed to index {doc['id']}: {e}")
        
        # Get final count
        final_count = collection.count()
        
        print(f"\n📊 Indexing Summary:")
        print(f"   Documents indexed: {indexed_count}")
        print(f"   Initial count: {initial_count}")
        print(f"   Count after deletion: {count_after_delete}")
        print(f"   Final count: {final_count}")
        print(f"   Net change: {final_count - initial_count}")
        
        return indexed_count, final_count
        
    except Exception as e:
        print(f"❌ Indexing failed: {e}")
        return 0, 0


def main():
    """Main execution"""
    indexed_count, final_count = index_alife_results()
    
    if indexed_count > 0:
        print(f"\n🎉 Successfully indexed {indexed_count} ALife experiment documents!")
        print(f"📚 New total collection count: {final_count}")
    else:
        print(f"\n❌ No documents were indexed")
    
    return indexed_count, final_count


if __name__ == "__main__":
    main()
