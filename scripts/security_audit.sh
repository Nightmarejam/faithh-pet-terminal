#!/usr/bin/env bash
# On-demand security posture snapshot (Gen8, NAS, Prometheus, Chroma).
set -uo pipefail

REPORT_DIR="/home/jonat/ai-stack/reports/security"
STAMP=$(date +%Y%m%d_%H%M%S)
REPORT="$REPORT_DIR/security_snapshot_${STAMP}.md"
mkdir -p "$REPORT_DIR"

{
  echo "# Security Snapshot — $STAMP"
  echo ""
  echo "## Gen8 fail2ban"
  ssh -o BatchMode=yes -o ConnectTimeout=10 gen8 "sudo -n /usr/bin/fail2ban-client status sshd 2>&1 || echo 'fail2ban: requires sudo (NOPASSWD) or run interactively on Gen8'" 2>&1 || echo "Gen8 unreachable"
  echo ""
  echo "## Gen8 UFW"
  ssh -o BatchMode=yes -o ConnectTimeout=10 gen8 "sudo -n /usr/sbin/ufw status numbered 2>&1 || echo 'UFW: sudo password required or ufw unavailable'" 2>&1 || echo "Gen8 unreachable"
  echo ""
  echo "## UDM gateway"
  ssh -o BatchMode=yes -o ConnectTimeout=10 udm "uname -a; echo '---'; ip -brief addr | head -20; echo '---'; ss -tuln | grep -E '(:22|:80|:443|:8443|:8444|:8080|:8880|:8843)'" 2>&1 || echo "UDM unreachable"
  echo ""
  echo "## UDM NAT forwards (summary)"
  ssh -o BatchMode=yes -o ConnectTimeout=10 udm "iptables -t nat -S | grep -E 'DNAT|MASQUERADE' | head -40" 2>&1 || echo "UDM NAT query failed"
  echo ""
  echo "## NAS listening ports"
  ssh -o BatchMode=yes -o ConnectTimeout=10 nas "netstat -tlnp 2>/dev/null | grep LISTEN" 2>&1 || echo "NAS unreachable"
  echo ""
  echo "## NAS shell users"
  ssh -o BatchMode=yes -o ConnectTimeout=10 nas "cat /etc/passwd | grep -v nologin | grep -v false" 2>&1 || echo "NAS unreachable"
  echo ""
  echo "## Active Prometheus alerts"
  python3 - <<'PY' 2>&1 || echo "Prometheus alerts query failed"
import json
import sys
import urllib.request
try:
    with urllib.request.urlopen("http://192.158.1.243:9090/api/v1/alerts", timeout=15) as r:
        d = json.load(r)
    alerts = [a for a in d.get("data", {}).get("alerts", []) if a.get("state") == "firing"]
    print(f"{len(alerts)} alerts firing")
    for a in alerts:
        print(f"  {a.get('labels', {}).get('alertname', '?')}")
except Exception as e:
    print(f"Prometheus unreachable: {e}")
PY
  echo ""
  echo "## ChromaDB"
  chroma_ok=0
  for path in /api/v2/heartbeat /api/v1/heartbeat; do
    if out=$(curl -fsS --connect-timeout 10 "http://192.158.1.243:8000${path}" 2>&1); then
      echo "${path}: ${out}"
      chroma_ok=1
      break
    fi
  done
  if [[ "$chroma_ok" -eq 0 ]]; then
    echo "ChromaDB unreachable (tried v2 and v1 heartbeat)"
  fi
  echo ""
  echo "Snapshot complete: $REPORT"
} >"$REPORT"

cat "$REPORT"
