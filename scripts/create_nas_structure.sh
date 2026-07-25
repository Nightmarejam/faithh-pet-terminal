#!/bin/bash
# ⚠️ SUPERSEDED 2026-07-25 — DO NOT RUN AS-IS.
#
# This script creates shares that no longer exist. The NAS was reorganized on
# 2026-07-24 into two primary shares:
#     /volume1/media      — Plex-facing library only
#     /volume1/homelab    — everything else (ai/ audio/ backups/ personal/ projects/ triage/)
#   plus /volume1/pve (hypervisor backups + ISOs) and the DSM-managed homes.
# The old raw_ingest / projects / archive / AI / Personal / Audio / Backups shares were
# migrated and deleted. Running this would recreate empty husks of deleted shares.
#
# New homes for what this used to create:
#     /volume1/raw_ingest/gov_api  ->  /volume1/homelab/projects/civic-data
#     /volume1/projects/<name>     ->  /volume1/homelab/projects/<name>
#     /volume1/archive/*           ->  /volume1/homelab/archive/*
# Rewrite against the new layout before using. Guard below prevents accidental runs.

echo "create_nas_structure.sh is superseded — see the header. Exiting."; exit 1

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
