#!/usr/bin/env python3
"""
RAG Retrieval Quality Stress Test
Tests ChromaDB retrieval accuracy against known-answer questions.

Usage:
    python tests/test_rag_quality.py
    python tests/test_rag_quality.py --verbose
    python tests/test_rag_quality.py --n-results 10
"""

import sys
import os
import argparse
from datetime import datetime
from typing import Dict, List, Any

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import chromadb
    from chromadb.config import Settings
except ImportError:
    print("ERROR: chromadb not installed. Run: pip install chromadb")
    sys.exit(1)

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    print("ERROR: sentence-transformers not installed. Run: pip install sentence-transformers")
    sys.exit(1)


# Test queries with expected results
TEST_QUERIES = [
    {
        "query": "What is FAITHH?",
        "expected_keywords": ["friendly ai", "teaching", "helping", "hub"],
        "expected_sources": ["faithh", "master_context", "gpt_project"],
        "description": "Basic project identity query"
    },
    {
        "query": "Describe the phase flip zone in Harmony",
        "expected_keywords": ["phase flip", "controller", "exploration", "consolidation"],
        "expected_sources": ["harmony", "architecture"],
        "description": "Specific framework concept query"
    },
    {
        "query": "What is Constella?",
        "expected_keywords": ["civic", "governance", "astris", "auctor"],
        "expected_sources": ["constella"],
        "description": "Related project query"
    },
    {
        "query": "Why did we choose ChromaDB?",
        "expected_keywords": ["vector", "embedding", "database"],
        "expected_sources": ["decisions", "architecture"],
        "description": "Technical decision rationale"
    },
    {
        "query": "How do I start the FAITHH backend?",
        "expected_keywords": ["python", "flask", "5557", "backend"],
        "expected_sources": ["readme", "architecture", "guide", "quick"],
        "description": "Operational how-to query"
    },
    {
        "query": "What embedding model does FAITHH use?",
        "expected_keywords": ["mpnet", "768", "sentence-transformer"],
        "expected_sources": ["architecture", "backend", "chroma"],
        "description": "Technical specification query"
    },
    {
        "query": "What is the Penumbra Accord?",
        "expected_keywords": ["mediation", "governance", "dispute"],
        "expected_sources": ["constella"],
        "description": "Specific Constella concept"
    },
    {
        "query": "What audio gear does Jonathan use?",
        "expected_keywords": ["wavelab", "volt", "sonarworks"],
        "expected_sources": ["audio", "archived_projects", "life_map"],
        "description": "Personal context query"
    },
    {
        "query": "What providers does FAITHH support?",
        "expected_keywords": ["groq", "ollama", "local", "webui", "provider"],
        "expected_sources": ["model_config", "llm_providers", "phase2"],
        "description": "Current capabilities query"
    },
    {
        "query": "What is the human standard?",
        "expected_keywords": ["human standard", "harmony", "celestial", "equilibrium"],
        "expected_sources": ["harmony", "constella", "master"],
        "description": "Philosophical framework query"
    }
]


class RAGQualityTester:
    """Tests RAG retrieval quality against known-answer questions."""

    def __init__(self, chroma_path: str = None, chroma_host: str = "localhost",
                 chroma_port: int = 8000, collection_name: str = "documents_768",
                 n_results: int = 5, verbose: bool = False):
        """
        Initialize the RAG quality tester.

        Args:
            chroma_path: Path to ChromaDB directory (for PersistentClient, optional)
            chroma_host: ChromaDB server host (for HttpClient)
            chroma_port: ChromaDB server port (for HttpClient)
            collection_name: Name of the ChromaDB collection
            n_results: Number of results to retrieve per query
            verbose: Enable verbose output
        """
        self.collection_name = collection_name
        self.n_results = n_results
        self.verbose = verbose
        self.results = []

        # Initialize ChromaDB client (prefer HTTP client if no path specified)
        if chroma_path:
            print(f"Loading ChromaDB from {chroma_path}...")
            try:
                self.client = chromadb.PersistentClient(
                    path=chroma_path,
                    settings=Settings(allow_reset=True, anonymized_telemetry=False)
                )
                self.connection_type = f"PersistentClient({chroma_path})"
            except Exception as e:
                print(f"ERROR: Failed to connect to PersistentClient at {chroma_path}: {e}")
                sys.exit(1)
        else:
            print(f"Connecting to ChromaDB server at {chroma_host}:{chroma_port}...")
            try:
                self.client = chromadb.HttpClient(host=chroma_host, port=chroma_port)
                self.connection_type = f"HttpClient({chroma_host}:{chroma_port})"
            except Exception as e:
                print(f"ERROR: Failed to connect to ChromaDB server at {chroma_host}:{chroma_port}: {e}")
                print("Make sure ChromaDB server is running (check port 8000)")
                sys.exit(1)

        # Get collection
        try:
            self.collection = self.client.get_collection(collection_name)
            doc_count = self.collection.count()
            print(f"✓ Loaded collection '{collection_name}' with {doc_count:,} documents")
            print(f"  Connection: {self.connection_type}\n")
        except Exception as e:
            print(f"ERROR: Failed to load ChromaDB collection '{collection_name}': {e}")
            print("\nAvailable collections:")
            try:
                for coll in self.client.list_collections():
                    print(f"  - {coll.name} ({coll.count()} docs)")
            except:
                print("  (Unable to list collections)")
            sys.exit(1)

    def score_result(self, query_data: Dict, retrieval_results: Dict) -> Dict[str, Any]:
        """
        Score a single query result.

        Scoring:
        - 0 = Miss (no expected keywords or sources found)
        - 1 = Partial (some keywords OR some sources found)
        - 2 = Good hit (keywords AND sources found)

        Args:
            query_data: Test query with expected results
            retrieval_results: ChromaDB query results

        Returns:
            Dict with score and details
        """
        documents = retrieval_results.get('documents', [[]])[0]
        metadatas = retrieval_results.get('metadatas', [[]])[0]
        distances = retrieval_results.get('distances', [[]])[0]

        # Combine all retrieved text for keyword search
        all_text = " ".join(documents).lower()

        # Check for expected keywords
        found_keywords = []
        for keyword in query_data['expected_keywords']:
            if keyword.lower() in all_text:
                found_keywords.append(keyword)

        keyword_match = len(found_keywords) > 0

        # Check for expected sources in metadata
        found_sources = []
        for metadata in metadatas:
            source = metadata.get('source', '').lower()
            for expected_source in query_data['expected_sources']:
                if expected_source.lower() in source:
                    found_sources.append(expected_source)
                    break

        source_match = len(found_sources) > 0

        # Calculate score
        if keyword_match and source_match:
            score = 2  # Good hit
            status = "✅ GOOD"
        elif keyword_match or source_match:
            score = 1  # Partial
            status = "⚠️  PARTIAL"
        else:
            score = 0  # Miss
            status = "❌ MISS"

        # Get top result details
        top_source = metadatas[0].get('source', 'unknown') if metadatas else 'unknown'
        top_distance = distances[0] if distances else float('inf')

        return {
            'score': score,
            'status': status,
            'keyword_match': keyword_match,
            'source_match': source_match,
            'found_keywords': found_keywords,
            'found_sources': list(set(found_sources)),  # Deduplicate
            'top_source': top_source,
            'top_distance': top_distance,
            'num_results': len(documents)
        }

    def run_test(self, query_data: Dict) -> Dict[str, Any]:
        """
        Run a single test query.

        Args:
            query_data: Test query configuration

        Returns:
            Test result dictionary
        """
        query = query_data['query']

        if self.verbose:
            print(f"\n{'='*80}")
            print(f"Query: {query}")
            print(f"Description: {query_data['description']}")
            print(f"Expected keywords: {query_data['expected_keywords']}")
            print(f"Expected sources: {query_data['expected_sources']}")
            print(f"{'-'*80}")

        # Query ChromaDB
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=self.n_results
            )
        except Exception as e:
            print(f"ERROR querying ChromaDB: {e}")
            return {
                'query': query,
                'error': str(e),
                'score': 0,
                'status': '❌ ERROR'
            }

        # Score the results
        score_data = self.score_result(query_data, results)

        # Combine query data with score
        result = {
            'query': query,
            'description': query_data['description'],
            **score_data
        }

        if self.verbose:
            print(f"Status: {score_data['status']}")
            print(f"Keywords found: {score_data['found_keywords']}")
            print(f"Sources found: {score_data['found_sources']}")
            print(f"Top result source: {score_data['top_source']}")
            print(f"Top result distance: {score_data['top_distance']:.4f}")

            # Show top 3 results
            documents = results.get('documents', [[]])[0]
            metadatas = results.get('metadatas', [[]])[0]
            distances = results.get('distances', [[]])[0]

            print(f"\nTop {min(3, len(documents))} Results:")
            for i, (doc, meta, dist) in enumerate(zip(documents[:3], metadatas[:3], distances[:3])):
                source = meta.get('source', 'unknown')
                preview = doc[:150].replace('\n', ' ')
                print(f"  {i+1}. [{source}] (distance: {dist:.4f})")
                print(f"     {preview}...")

        return result

    def run_all_tests(self) -> List[Dict[str, Any]]:
        """Run all test queries and return results."""
        print(f"Running {len(TEST_QUERIES)} test queries...\n")

        for i, query_data in enumerate(TEST_QUERIES, 1):
            if not self.verbose:
                print(f"Test {i}/{len(TEST_QUERIES)}: {query_data['query'][:50]}...", end=' ')

            result = self.run_test(query_data)
            self.results.append(result)

            if not self.verbose:
                print(result['status'])

        return self.results

    def generate_report(self) -> str:
        """Generate a quality report from test results."""
        total_tests = len(self.results)
        total_score = sum(r['score'] for r in self.results)
        max_score = total_tests * 2  # Max score is 2 per test

        # Count by status
        good_hits = sum(1 for r in self.results if r['score'] == 2)
        partial_hits = sum(1 for r in self.results if r['score'] == 1)
        misses = sum(1 for r in self.results if r['score'] == 0)

        # Calculate percentage
        accuracy_pct = (total_score / max_score * 100) if max_score > 0 else 0

        # Generate report
        report_lines = [
            "\n" + "="*80,
            "RAG RETRIEVAL QUALITY REPORT",
            "="*80,
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Connection: {self.connection_type}",
            f"Collection: {self.collection_name}",
            f"Results Retrieved per Query: {self.n_results}",
            "",
            "SUMMARY",
            "-"*80,
            f"Total Tests: {total_tests}",
            f"Total Score: {total_score}/{max_score} ({accuracy_pct:.1f}%)",
            "",
            f"✅ Good Hits (2 pts):  {good_hits:2d} ({good_hits/total_tests*100:5.1f}%)",
            f"⚠️  Partial Hits (1 pt): {partial_hits:2d} ({partial_hits/total_tests*100:5.1f}%)",
            f"❌ Misses (0 pts):     {misses:2d} ({misses/total_tests*100:5.1f}%)",
            "",
            "QUALITY GRADE",
            "-"*80
        ]

        # Assign grade
        if accuracy_pct >= 90:
            grade = "A (Excellent)"
            assessment = "RAG retrieval is highly accurate and reliable."
        elif accuracy_pct >= 75:
            grade = "B (Good)"
            assessment = "RAG retrieval is generally reliable with minor gaps."
        elif accuracy_pct >= 60:
            grade = "C (Acceptable)"
            assessment = "RAG retrieval works but has notable accuracy issues."
        elif accuracy_pct >= 40:
            grade = "D (Needs Improvement)"
            assessment = "RAG retrieval quality is concerning. Review indexing and embeddings."
        else:
            grade = "F (Poor)"
            assessment = "RAG retrieval is unreliable. Immediate attention required."

        report_lines.extend([
            f"Grade: {grade}",
            f"Assessment: {assessment}",
            "",
            "DETAILED RESULTS",
            "-"*80
        ])

        # Add detailed results
        for i, result in enumerate(self.results, 1):
            report_lines.extend([
                f"\n{i}. {result['query']}",
                f"   Status: {result['status']} | Score: {result['score']}/2",
                f"   Type: {result['description']}",
                f"   Keywords found: {result.get('found_keywords', [])}",
                f"   Sources found: {result.get('found_sources', [])}",
                f"   Top result: {result.get('top_source', 'unknown')} (distance: {result.get('top_distance', 0):.4f})"
            ])

        # Add recommendations
        report_lines.extend([
            "",
            "RECOMMENDATIONS",
            "-"*80
        ])

        if accuracy_pct >= 90:
            report_lines.append("✓ RAG system is performing well. Continue monitoring.")
        else:
            report_lines.append("Issues detected. Consider:")
            if misses > 0:
                report_lines.append("  • Review embedding model choice (current: all-mpnet-base-v2)")
                report_lines.append("  • Check if expected documents are actually indexed")
                report_lines.append("  • Verify metadata source fields are populated correctly")
            if partial_hits > good_hits:
                report_lines.append("  • Improve document chunking strategy")
                report_lines.append("  • Add more context to document metadata")
                report_lines.append("  • Consider increasing n_results for retrieval")

        report_lines.extend([
            "",
            "="*80,
            ""
        ])

        return "\n".join(report_lines)

    def save_report(self, filename: str = None):
        """Save the report to a file."""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"rag_quality_report_{timestamp}.txt"

        report = self.generate_report()

        # Save to tests directory
        report_path = os.path.join(os.path.dirname(__file__), filename)
        with open(report_path, 'w') as f:
            f.write(report)

        print(f"\n✓ Report saved to: {report_path}")
        return report_path


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="RAG Retrieval Quality Stress Test",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python tests/test_rag_quality.py
  python tests/test_rag_quality.py --verbose
  python tests/test_rag_quality.py --n-results 10 --save-report
  python tests/test_rag_quality.py --chroma-path ./faithh_rag
        """
    )

    parser.add_argument(
        '--chroma-path',
        default=None,
        help='Path to ChromaDB directory (for PersistentClient). If not specified, uses HttpClient.'
    )
    parser.add_argument(
        '--chroma-host',
        default='localhost',
        help='ChromaDB server host (default: localhost)'
    )
    parser.add_argument(
        '--chroma-port',
        type=int,
        default=8000,
        help='ChromaDB server port (default: 8000)'
    )
    parser.add_argument(
        '--collection',
        default='documents_768',
        help='ChromaDB collection name (default: documents_768)'
    )
    parser.add_argument(
        '--n-results',
        type=int,
        default=5,
        help='Number of results to retrieve per query (default: 5)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output showing all results'
    )
    parser.add_argument(
        '--save-report',
        action='store_true',
        help='Save report to file in tests/ directory'
    )

    args = parser.parse_args()

    # Run tests
    tester = RAGQualityTester(
        chroma_path=args.chroma_path,
        chroma_host=args.chroma_host,
        chroma_port=args.chroma_port,
        collection_name=args.collection,
        n_results=args.n_results,
        verbose=args.verbose
    )

    tester.run_all_tests()

    # Generate and print report
    report = tester.generate_report()
    print(report)

    # Save report if requested
    if args.save_report:
        tester.save_report()

    # Exit with status code based on grade
    total_score = sum(r['score'] for r in tester.results)
    max_score = len(tester.results) * 2
    accuracy_pct = (total_score / max_score * 100) if max_score > 0 else 0

    if accuracy_pct >= 75:
        sys.exit(0)  # Success
    elif accuracy_pct >= 60:
        sys.exit(1)  # Warning
    else:
        sys.exit(2)  # Failure


if __name__ == '__main__':
    main()
