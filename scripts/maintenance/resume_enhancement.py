#!/usr/bin/env python3
"""
Resume Metadata Enhancement from checkpoint
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.maintenance.enhance_metadata import MetadataEnhancer

def main():
    enhancer = MetadataEnhancer()
    
    # Check if we have a previous report
    try:
        with open("logs/metadata_enhancement_report.json", "r") as f:
            report = json.load(f)
            start_offset = report.get("processed", 0)
            print(f"Resuming from document {start_offset}")
    except:
        start_offset = 0
        print("Starting fresh enhancement")
    
    # Run enhancement from checkpoint
    enhancer.processed = start_offset
    enhancer.enhanced = 0
    
    print(f"=== Resuming Metadata Enhancement ===")
    print(f"Starting from offset: {start_offset}")
    print(f"Total documents: {enhancer.total_docs}")
    print()
    
    offset = start_offset
    while enhancer.process_batch(offset):
        offset += enhancer.BATCH_SIZE
        # Stop if we've processed enough for testing
        if enhancer.processed >= start_offset + 1000:
            print(f"\nStopping at {enhancer.processed} for testing")
            break
    
    print()
    print("=== Enhancement Session Complete ===")
    print(f"Documents processed this session: {enhancer.processed - start_offset}")
    print(f"Documents enhanced this session: {enhancer.enhanced}")
    print(f"Total processed: {enhancer.processed}")
    print(f"Total enhanced: {enhancer.enhanced + report.get('enhanced', 0)}")

if __name__ == "__main__":
    main()
