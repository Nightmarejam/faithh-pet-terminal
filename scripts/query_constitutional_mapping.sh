#!/bin/bash
# Query FAITHH backend to draft the constitutional mapping document
# Uses Anthropic Claude via the backend RAG system

PAYLOAD=$(cat <<'ENDJSON'
{
  "message": "You have access to the full Constella Framework documentation indexed in your knowledge base (1,904 documents) and the ALife experiment results (experiments 0-5). Please draft a comprehensive constitutional mapping document titled 'Constella-ALife Constitutional Mapping'. For each core Constella principle (Astris token, Auctor token, Penumbra Accord, Universal Civic Floor, Civic Tome), provide: (1) the precise Constella definition, (2) the ALife mechanical analog - what parameter, agent behavior, or emergent phenomenon maps to it, (3) the specific experiment that validates or tests this mapping, (4) what data we still need to fully validate the mapping. Also include a section on what external data sources (government APIs, academic papers, open datasets) would strengthen the constitutional grounding. Format as a structured markdown document suitable for saving to docs/constella_alife_constitution.md",
  "provider": "anthropic",
  "model": "claude-opus-4-5",
  "use_rag": true
}
ENDJSON
)

curl -s -X POST http://localhost:5557/api/chat \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD"
