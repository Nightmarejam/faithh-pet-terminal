#!/bin/bash
# Refresh all data files for the static dashboard (projects/status).
# Copies process_registry.json here so dashboard.html can fetch it first; fallbacks
# are ../../docs/architecture/... and /docs/architecture/... (repo-root server).
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
STATUS_DIR="$REPO_ROOT/projects/status"

mkdir -p "$STATUS_DIR"
cp "$REPO_ROOT/docs/architecture/process_registry.json" "$STATUS_DIR/process_registry.json"

cd "$REPO_ROOT"
if [[ -x "$REPO_ROOT/venv/bin/python3" ]]; then
  PY="$REPO_ROOT/venv/bin/python3"
else
  PY="python3"
fi

"$PY" "$REPO_ROOT/scripts/export_status_csv.py"
"$PY" "$REPO_ROOT/scripts/check_project_staleness.py" --days 7 || true

echo "Dashboard data refreshed at $(date)"
echo "Serve: cd $STATUS_DIR && python3 -m http.server 8765"
echo "Open:  http://localhost:8765/dashboard.html"
