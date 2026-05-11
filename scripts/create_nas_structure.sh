#!/bin/bash
# Create the new NAS folder structure for data pipelines
# Run via: bash scripts/create_nas_structure.sh

ssh nas << 'ENDSSH'
echo "=== Creating NAS project structure ==="

mkdir -p /volume1/raw_ingest/gov_api/oregon_sos
mkdir -p /volume1/raw_ingest/gov_api/census
mkdir -p /volume1/raw_ingest/gov_api/fcc
mkdir -p /volume1/raw_ingest/torrents
mkdir -p /volume1/raw_ingest/manual

mkdir -p /volume1/projects/constella/design_docs
mkdir -p /volume1/projects/constella/research/papers
mkdir -p /volume1/projects/constella/research/datasets
mkdir -p /volume1/projects/alife/results
mkdir -p /volume1/projects/alife/experiments
mkdir -p /volume1/projects/faithh/chromadb_backups
mkdir -p /volume1/projects/faithh/knowledge_base_exports
mkdir -p /volume1/projects/faithh/processed

mkdir -p /volume1/archive/processed
mkdir -p /volume1/archive/deep_archive

echo ""
echo "=== Created structure ==="
find /volume1/raw_ingest /volume1/projects /volume1/archive -type d | sort

echo ""
echo "=== Done ==="
ENDSSH
