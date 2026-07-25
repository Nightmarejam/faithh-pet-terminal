#!/bin/bash
# Cockpit dependency smoke test
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

cd "$REPO_ROOT"

if [[ -x "$REPO_ROOT/venv/bin/python3" ]]; then
  PY="$REPO_ROOT/venv/bin/python3"
else
  PY="python3"
fi

echo "== Refreshing dashboard data =="
bash "$REPO_ROOT/scripts/refresh_dashboard_data.sh"

echo ""
echo "== Impact check: api_plc_state =="
"$PY" "$REPO_ROOT/scripts/impact_analyzer.py" --component api_plc_state | sed -n '1,18p'

echo ""
echo "== Endpoint ping matrix =="
FAIL=0
# Ecosystem contract: /api/plc/state (includes faithh_status). /api/status kept as thin alias only.
for u in /cockpit /api/plc/state /api/pulse/state /api/compass /faithh_live_state.json /api/health; do
  code=$(curl -s -o /tmp/cockpit_ping.json -w "%{http_code}" "http://127.0.0.1:5557$u" || true)
  bytes=$(wc -c < /tmp/cockpit_ping.json 2>/dev/null || echo 0)
  echo "$u $code ${bytes}B"
  if [[ "$code" != "200" ]]; then
    FAIL=1
  fi
done

echo ""
echo "== PLC payload sanity =="
"$PY" - << 'PY'
import json, sys, urllib.request
u = "http://127.0.0.1:5557/api/plc/state"
with urllib.request.urlopen(u, timeout=5) as r:
    d = json.loads(r.read().decode("utf-8"))
ps = d.get("project_status", {})
fs = d.get("faithh_status") or {}
sv = (fs.get("services") or {}) if isinstance(fs, dict) else {}
print("current_state:", d.get("current_state"))
print("tracks:", len(ps.get("tracks", [])))
print("next_action:", (ps.get("summary") or {}).get("next_action", "<missing>"))
print("recent_component_changes:", len(d.get("recent_component_changes", [])))
ver = fs.get("version")
cm = sv.get("current_model")
print("faithh_status.version:", ver or "<missing>")
print("faithh_status.current_model:", cm if cm is not None else "<missing>")
if not ver:
    print("FAIL: faithh_status.version required (restart backend after PLC contract change)", file=sys.stderr)
    sys.exit(1)
if cm is None:
    print("FAIL: faithh_status.services.current_model required", file=sys.stderr)
    sys.exit(1)
PY

if [[ "$FAIL" -ne 0 ]]; then
  echo ""
  echo "Smoke result: FAIL (one or more endpoints non-200)"
  exit 1
fi

echo ""
echo "== Ecosystem baseline probe (PLC + health + ping chat; --skip-llm for speed) =="
if ! "$PY" "$REPO_ROOT/scripts/ecosystem_baseline_probe.py" --skip-llm --out /tmp/faithh_probe_smoke.json; then
  echo "Probe FAILED (see /tmp/faithh_probe_smoke.json). For full LLM+RAG timing run: python scripts/ecosystem_baseline_probe.py --with-rag"
  exit 1
fi

echo ""
echo "Smoke result: PASS"
