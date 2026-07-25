#!/bin/bash
# Clone civic technology repositories to NAS for Constella research
# These are open-source platforms for participatory democracy

set -e

# Destination
DEST="/mnt/x/AI/civic_tech_repos"
mkdir -p "$DEST"

echo "=============================================="
echo "Cloning Civic Technology Repositories"
echo "Destination: $DEST"
echo "=============================================="

# Core platforms (most mature, well-documented)
REPOS=(
    "decidim/decidim"                    # Ruby - Participatory democracy platform
    "consul/consul"                      # Ruby - Citizen participation portal (Madrid)
    "loomio/loomio"                      # Ruby - Collaborative decision-making
    "DemocracyOS/democracyos"            # Node.js - Deliberation platform
    "citizenos/citizenos-web"            # Node.js - Discussion, voting, signatures
    "pol-is/polis"                       # Node.js - AI-mediated consensus
    "liquidfeedback/liquidfeedback-core" # Lua - Delegated voting
)

# Additional tools
EXTRA_REPOS=(
    "g0v/moedict-webkit"                 # Taiwan civic tech
    "mysociety/fixmystreet"              # Report local problems
    "openaustralia/planningalerts"       # Planning applications
    "codeforamerica/ohana-api"           # Social services directory
    "datamade/councilmatic"              # City council legislation
)

clone_repo() {
    local repo="$1"
    local name=$(basename "$repo")
    local target="$DEST/$name"
    
    if [ -d "$target/.git" ]; then
        echo "  ↻ Updating $name..."
        cd "$target" && git pull --quiet 2>/dev/null || echo "    (pull failed, skipping)"
        cd - > /dev/null
    else
        echo "  ↓ Cloning $name..."
        git clone --depth 1 "https://github.com/$repo.git" "$target" 2>/dev/null || echo "    (clone failed)"
    fi
}

echo ""
echo "📦 Core Platforms:"
for repo in "${REPOS[@]}"; do
    clone_repo "$repo"
done

echo ""
echo "📦 Additional Tools:"
for repo in "${EXTRA_REPOS[@]}"; do
    clone_repo "$repo"
done

# Summary
echo ""
echo "=============================================="
echo "Summary"
echo "=============================================="
echo "Location: $DEST"
du -sh "$DEST" 2>/dev/null || echo "Size: calculating..."
ls -1 "$DEST" | wc -l | xargs -I {} echo "Repositories: {}"

echo ""
echo "Key documentation to index:"
echo "  - decidim/docs/"
echo "  - consul/doc/"
echo "  - loomio/docs/"
echo "  - democracyos/docs/"
