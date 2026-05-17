#!/usr/bin/env python3
"""
ALIFE Training Pipeline Builder

Extracts and processes ALIFE experiment data from ChromaDB to build 
training datasets for Phase 2 weight optimization model.

Usage: python build_alife_training_pipeline.py [--output-dir ml/training_data]
"""

import sys
import os
import argparse
import json
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional
import chromadb

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class ALIFETrainingDataBuilder:
    """Builds training datasets from ALIFE ChromaDB data for Phase 2 ML."""
    
    def __init__(self, chroma_host: str = "192.158.1.10", chroma_port: int = 8000):
        self.chroma_host = chroma_host
        self.chroma_port = chroma_port
        self.client = None
        self.collection = None
        
    def connect_chromadb(self) -> bool:
        """Connect to ChromaDB and get alife_lineage collection."""
        try:
            self.client = chromadb.HttpClient(host=self.chroma_host, port=self.chroma_port)
            self.collection = self.client.get_collection("alife_lineage")
            print(f"✅ Connected to ChromaDB: {self.chroma_host}:{self.chroma_port}")
            print(f"📊 Collection 'alife_lineage': {self.collection.count()} documents")
            return True
        except Exception as e:
            print(f"❌ ChromaDB connection failed: {e}")
            return False
    
    def extract_alife_data(self, limit: int = 1000) -> List[Dict[str, Any]]:
        """Extract ALIFE experiment data from ChromaDB."""
        
        if not self.collection:
            return []
        
        try:
            # Get all documents (or limit if specified)
            results = self.collection.get(
                limit=limit,
                include=["documents", "metadatas"]
            )
            
            documents = results["documents"]
            metadatas = results["metadatas"]
            
            print(f"📥 Extracted {len(documents)} ALIFE documents")
            
            # Process into structured format
            alife_data = []
            for i, (doc, metadata) in enumerate(zip(documents, metadatas)):
                if limit and i >= limit:
                    break
                
                # Parse document content
                try:
                    # Try to parse as JSON first
                    content = json.loads(doc) if doc.startswith('{') else doc
                except:
                    content = doc
                
                alife_data.append({
                    "id": i,
                    "content": content,
                    "metadata": metadata,
                    "timestamp": metadata.get("timestamp", ""),
                    "experiment": metadata.get("experiment", ""),
                    "tick": metadata.get("tick", ""),
                    "event_type": metadata.get("event_type", "")
                })
            
            return alife_data
            
        except Exception as e:
            print(f"❌ Data extraction failed: {e}")
            return []
    
    def categorize_alife_content(self, alife_data: List[Dict[str, Any]]) -> Dict[str, List[Dict]]:
        """Categorize ALIFE data by experiment and content type."""
        
        categories = {
            "experiment_0": [],
            "experiment_1": [],
            "experiment_2": [],
            "experiment_3": [],
            "experiment_4": [],
            "experiment_5": [],
            "experiment_6": [],
            "cognitive_specialization": [],
            "mathematical_cognition": [],
            "fibonacci_patterns": [],
            "evolutionary_dynamics": [],
            "energy_economics": [],
            "population_dynamics": [],
            "zone_specialization": [],
            "pattern_recognition": [],
            "general_alife": []
        }
        
        for item in alife_data:
            content = str(item["content"]).lower()
            metadata = item["metadata"]
            
            # Categorize by experiment
            experiment = metadata.get("experiment", "")
            if f"experiment_{experiment}" in categories:
                categories[f"experiment_{experiment}"].append(item)
            
            # Categorize by content themes
            if any(term in content for term in ["cognitive", "specialization", "pattern recognition"]):
                categories["cognitive_specialization"].append(item)
            
            if any(term in content for term in ["mathematical", "fibonacci", "pattern", "recognition"]):
                categories["mathematical_cognition"].append(item)
            
            if any(term in content for term in ["fibonacci", "phi", "golden ratio", "zone"]):
                categories["fibonacci_patterns"].append(item)
            
            if any(term in content for term in ["evolution", "emergence", "adaptation", "selection"]):
                categories["evolutionary_dynamics"].append(item)
            
            if any(term in content for term in ["energy", "drain", "bonus", "efficiency"]):
                categories["energy_economics"].append(item)
            
            if any(term in content for term in ["population", "agents", "reproduction", "birth", "death"]):
                categories["population_dynamics"].append(item)
            
            if any(term in content for term in ["zone", "specialization", "preference", "habitat"]):
                categories["zone_specialization"].append(item)
            
            if any(term in content for term in ["pattern", "recognition", "detection", "cognitive"]):
                categories["pattern_recognition"].append(item)
            
            # Default category
            if not any(categories[key] for key in categories if key != "general_alife"):
                categories["general_alife"].append(item)
        
        return categories
    
    def build_training_examples(self, categories: Dict[str, List[Dict]]) -> List[Dict[str, Any]]:
        """Build training examples from categorized ALIFE data."""
        
        training_examples = []
        
        # Mathematical cognition examples
        for item in categories["mathematical_cognition"][:50]:
            training_examples.append({
                "query_type": "alife_query",
                "complexity": "high",
                "domain": "mathematical_cognition",
                "content": item["content"],
                "metadata": item["metadata"],
                "features": self.extract_features(item),
                "label": "mathematical_cognition_analysis"
            })
        
        # Cognitive specialization examples
        for item in categories["cognitive_specialization"][:50]:
            training_examples.append({
                "query_type": "alife_query",
                "complexity": "high",
                "domain": "cognitive_specialization",
                "content": item["content"],
                "metadata": item["metadata"],
                "features": self.extract_features(item),
                "label": "cognitive_specialization_analysis"
            })
        
        # Evolutionary dynamics examples
        for item in categories["evolutionary_dynamics"][:30]:
            training_examples.append({
                "query_type": "complex_query",
                "complexity": "high",
                "domain": "evolutionary_dynamics",
                "content": item["content"],
                "metadata": item["metadata"],
                "features": self.extract_features(item),
                "label": "evolutionary_dynamics_analysis"
            })
        
        # Energy economics examples
        for item in categories["energy_economics"][:30]:
            training_examples.append({
                "query_type": "project_query",
                "complexity": "medium",
                "domain": "energy_economics",
                "content": item["content"],
                "metadata": item["metadata"],
                "features": self.extract_features(item),
                "label": "energy_optimization"
            })
        
        # Fibonacci patterns examples
        for item in categories["fibonacci_patterns"][:25]:
            training_examples.append({
                "query_type": "alife_query",
                "complexity": "high",
                "domain": "fibonacci_patterns",
                "content": item["content"],
                "metadata": item["metadata"],
                "features": self.extract_features(item),
                "label": "fibonacci_pattern_analysis"
            })
        
        print(f"🏗️ Built {len(training_examples)} training examples")
        return training_examples
    
    def extract_features(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Extract features from ALIFE data item."""
        
        content = str(item["content"])
        metadata = item["metadata"]
        
        features = {
            "content_length": len(content),
            "experiment": metadata.get("experiment", ""),
            "tick": metadata.get("tick", ""),
            "event_type": metadata.get("event_type", ""),
            "has_numbers": any(c.isdigit() for c in content),
            "has_fibonacci": any(term in content.lower() for term in ["fibonacci", "phi", "golden ratio"]),
            "has_cognitive": any(term in content.lower() for term in ["cognitive", "specialization", "pattern"]),
            "has_evolution": any(term in content.lower() for term in ["evolution", "emergence", "adaptation"]),
            "has_energy": any(term in content.lower() for term in ["energy", "drain", "bonus"]),
            "has_population": any(term in content.lower() for term in ["population", "agents", "reproduction"])
        }
        
        return features
    
    def build_dataset(self, output_dir: str = "ml/training_data") -> Dict[str, Any]:
        """Build complete training dataset from ALIFE data."""
        
        print("🚀 Building ALIFE Training Dataset")
        print("=" * 50)
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Connect to ChromaDB
        if not self.connect_chromadb():
            return {"error": "Failed to connect to ChromaDB"}
        
        # Extract ALIFE data
        print("📥 Extracting ALIFE data...")
        alife_data = self.extract_alife_data(limit=500)
        
        if not alife_data:
            return {"error": "No ALIFE data extracted"}
        
        # Categorize data
        print("📂 Categorizing ALIFE content...")
        categories = self.categorize_alife_content(alife_data)
        
        # Print category statistics
        print("\n📊 Content Categories:")
        for category, items in categories.items():
            if items:
                print(f"  {category}: {len(items)} items")
        
        # Build training examples
        print("\n🏗️ Building training examples...")
        training_examples = self.build_training_examples(categories)
        
        # Create dataset splits
        print("📦 Creating dataset splits...")
        
        # Shuffle examples
        import random
        random.shuffle(training_examples)
        
        # Split into train/val/test (70/20/10)
        total = len(training_examples)
        train_end = int(total * 0.7)
        val_end = int(total * 0.9)
        
        train_data = training_examples[:train_end]
        val_data = training_examples[train_end:val_end]
        test_data = training_examples[val_end:]
        
        # Save datasets
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        datasets = {
            "train": train_data,
            "validation": val_data,
            "test": test_data
        }
        
        for split_name, data in datasets.items():
            filename = f"{output_dir}/alife_{split_name}_{timestamp}.json"
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            print(f"💾 Saved {split_name}: {len(data)} examples to {filename}")
        
        # Create metadata
        metadata = {
            "created": datetime.now().isoformat(),
            "total_examples": total,
            "splits": {
                "train": len(train_data),
                "validation": len(val_data),
                "test": len(test_data)
            },
            "categories": {k: len(v) for k, v in categories.items() if v},
            "feature_stats": self.calculate_feature_stats(training_examples),
            "source": "alife_lineage ChromaDB collection",
            "chroma_info": {
                "host": self.chroma_host,
                "port": self.chroma_port,
                "total_documents": self.collection.count()
            }
        }
        
        metadata_file = f"{output_dir}/alife_metadata_{timestamp}.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"\n📋 Metadata saved: {metadata_file}")
        
        return {
            "success": True,
            "total_examples": total,
            "splits": {k: len(v) for k, v in datasets.items()},
            "categories": {k: len(v) for k, v in categories.items() if v},
            "metadata_file": metadata_file,
            "output_dir": output_dir
        }
    
    def calculate_feature_stats(self, training_examples: List[Dict]) -> Dict[str, Any]:
        """Calculate statistics for training features."""
        
        if not training_examples:
            return {}
        
        # Aggregate feature statistics
        stats = {
            "content_length": {"min": float('inf'), "max": 0, "avg": 0},
            "feature_counts": {}
        }
        
        total_length = 0
        feature_counts = {}
        
        for example in training_examples:
            features = example.get("features", {})
            
            # Content length stats
            content_len = features.get("content_length", 0)
            total_length += content_len
            stats["content_length"]["min"] = min(stats["content_length"]["min"], content_len)
            stats["content_length"]["max"] = max(stats["content_length"]["max"], content_len)
            
            # Feature counts
            for feature_key, feature_value in features.items():
                if feature_key.startswith("has_") and feature_value:
                    feature_counts[feature_key] = feature_counts.get(feature_key, 0) + 1
        
        if training_examples:
            stats["content_length"]["avg"] = total_length / len(training_examples)
            stats["content_length"]["min"] = stats["content_length"]["min"] if stats["content_length"]["min"] != float('inf') else 0
        
        stats["feature_counts"] = feature_counts
        
        return stats

def main():
    parser = argparse.ArgumentParser(description="Build ALIFE training pipeline")
    parser.add_argument("--output-dir", default="ml/training_data", help="Output directory for training data")
    parser.add_argument("--chroma-host", default="192.158.1.10", help="ChromaDB host")
    parser.add_argument("--chroma-port", type=int, default=8000, help="ChromaDB port")
    
    args = parser.parse_args()
    
    builder = ALIFETrainingDataBuilder(args.chroma_host, args.chroma_port)
    result = builder.build_dataset(args.output_dir)
    
    if "error" in result:
        print(f"❌ Failed: {result['error']}")
    else:
        print("\n🎉 Training pipeline build complete!")
        print(f"📊 Total examples: {result['total_examples']}")
        print(f"📂 Splits: {result['splits']}")
        print(f"📋 Metadata: {result['metadata_file']}")

if __name__ == "__main__":
    main()
