#!/usr/bin/env bash
# Detect Windows host IP from WSL and add windows_exporter scrape job to Prometheus.
# Run after windows_exporter is installed on Windows (see install_windows_exporter.ps1).

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

if [[ -f /home/jonat/ops/monitoring/prometheus.yml ]]; then
  PROMETHEUS_YML="/home/jonat/ops/monitoring/prometheus.yml"
elif [[ -f "$REPO_ROOT/ops/monitoring/prometheus.yml" ]]; then
  PROMETHEUS_YML="$REPO_ROOT/ops/monitoring/prometheus.yml"
else
  echo "prometheus.yml not found (tried ~/ops/monitoring and repo ops/monitoring)"
  exit 1
fi

WINDOWS_IP=$(grep -m1 '^nameserver' /etc/resolv.conf | awk '{print $2}')
if [[ -z "${WINDOWS_IP}" ]]; then
  echo "Could not detect Windows host IP from /etc/resolv.conf"
  exit 1
fi

echo "Using prometheus.yml: $PROMETHEUS_YML"
echo "Detected Windows host IP: $WINDOWS_IP"

if curl -s --connect-timeout 3 "http://${WINDOWS_IP}:9182/metrics" | grep -q "windows_"; then
  echo "windows_exporter reachable at ${WINDOWS_IP}:9182"
else
  echo "WARNING: windows_exporter not reachable at ${WINDOWS_IP}:9182"
  echo "Run install_windows_exporter.ps1 as Administrator and confirm firewall rule."
  exit 1
fi

if grep -qE "windows_host|${WINDOWS_IP}:9182" "$PROMETHEUS_YML" 2>/dev/null; then
  echo "windows_host / ${WINDOWS_IP}:9182 already referenced in prometheus.yml"
else
  cat >> "$PROMETHEUS_YML" << YAML

  - job_name: windows_host
    static_configs:
      - targets: ['${WINDOWS_IP}:9182']
        labels:
          instance: windows-host
          role: workstation
YAML
  echo "Appended windows_host scrape job to $PROMETHEUS_YML"
fi

REL_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST http://localhost:9090/-/reload || true)
echo "Prometheus reload HTTP ${REL_CODE:-err}"

sleep 6
echo ""
echo "Target status (jobs containing windows):"
curl -s http://localhost:9090/api/v1/targets | python3 -c "
import json, sys
data = json.load(sys.stdin)
for t in data.get('data', {}).get('activeTargets', []):
    job = t.get('labels', {}).get('job', '')
    if 'windows' in job.lower():
        print(f\"  {job}: {t.get('health')}  {t.get('scrapeUrl', '')}\")
"
