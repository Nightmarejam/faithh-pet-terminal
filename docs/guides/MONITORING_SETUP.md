# FAITHH Monitoring Setup

Guide for integrating FAITHH with Prometheus/Grafana on Gen8 server.

## Prerequisites

- FAITHH backend running on WSL2 (port 5557)
- Gen8 server with Prometheus/Grafana (servicebox.taileb8c60.ts.net)
- Tailscale VPN connecting both machines

## 1. FAITHH Metrics Endpoint

The backend exposes Prometheus-compatible metrics at `/api/metrics`:

```bash
curl http://localhost:5557/api/metrics
```

### Metrics Exposed

| Metric | Type | Description |
|--------|------|-------------|
| `faithh_up` | gauge | Backend is up (1/0) |
| `faithh_info` | gauge | Version info |
| `faithh_ml_chips_total` | gauge | Number of ML chips loaded |
| `faithh_chromadb_connected` | gauge | ChromaDB connection status |
| `faithh_chromadb_documents_total` | gauge | Total docs in ChromaDB |
| `faithh_ollama_up` | gauge | Ollama service status |
| `faithh_ollama_models_total` | gauge | Number of Ollama models |
| `pulse_avatar_energy` | gauge | PULSE avatar energy (0-1) |
| `pulse_alerts_active` | gauge | Active PULSE alerts |
| `pulse_avatar_mood` | gauge | Avatar mood state |
| `pulse_sweep_runs_total` | counter | PULSE sweep run counts |
| `pulse_last_sweep_timestamp` | gauge | Last sweep timestamps |
| `faithh_cache_hits_total` | counter | Cache hits |
| `faithh_cache_misses_total` | counter | Cache misses |
| `faithh_provider_health` | gauge | LLM provider health |

## 2. Windows Firewall Setup

**Run as Administrator in PowerShell:**

```powershell
# Allow FAITHH backend port from Tailscale network
netsh advfirewall firewall add rule name="FAITHH Backend" dir=in action=allow protocol=TCP localport=5557

# Or more restrictively, only from Tailscale subnet:
netsh advfirewall firewall add rule name="FAITHH Backend Tailscale" dir=in action=allow protocol=TCP localport=5557 remoteip=100.64.0.0/10
```

## 3. Prometheus Configuration

On Gen8, the Prometheus config is at:
`/home/jonat/services/monitoring/prometheus.yml`

Add FAITHH scrape target:

```yaml
  - job_name: 'faithh'
    static_configs:
      - targets: ['100.115.225.100:5557']
    metrics_path: '/api/metrics'
```

Restart Prometheus:
```bash
docker restart prometheus
```

## 4. Verify Scraping

Check Prometheus targets:
```bash
curl -s 'http://servicebox.taileb8c60.ts.net:9090/api/v1/targets' | jq '.data.activeTargets[] | {job: .labels.job, health: .health}'
```

## 5. Grafana Dashboard

Access Grafana at: http://servicebox.taileb8c60.ts.net:3000
- Username: admin
- Password: Grafana2026!

### Import Dashboard

Create a new dashboard with panels for:
- FAITHH uptime and version
- ChromaDB document count
- PULSE avatar energy and mood
- PULSE sweep timing
- Provider health

### Example PromQL Queries

```promql
# FAITHH uptime
faithh_up

# ChromaDB documents
faithh_chromadb_documents_total

# PULSE alerts
pulse_alerts_active

# Avatar mood (alert state)
pulse_avatar_mood{mood="alert"}

# Time since last staleness sweep
time() - pulse_last_sweep_timestamp{tier="staleness"}
```

## 6. Current Gen8 Services

| Service | Port | Status |
|---------|------|--------|
| Prometheus | 9090 | ✅ Running (host network) |
| Grafana | 3000 | ✅ Running |
| Node Exporter | 9100 | ✅ Running |
| ChromaDB | 8000 | ✅ Running |
| Uptime Kuma | 3001 | ✅ Running |

## 7. Cockpit dependency verification

When backend health is green but cockpit looks stale, run:

```bash
cd /home/jonat/ai-stack
bash scripts/smoke_cockpit.sh
```

This validates:

- cockpit page and key APIs are returning HTTP 200
- `/api/plc/state` includes `project_status.summary.next_action`
- dashboard snapshot files are refreshed

Reference: `docs/guides/COCKPIT_DEPENDENCY_RUNBOOK.md`.

## Troubleshooting

### FAITHH target shows "down" in Prometheus

1. Check Windows firewall allows port 5557
2. Verify FAITHH backend is running: `curl http://localhost:5557/health`
3. Test from Gen8: `curl http://100.115.225.100:5557/api/metrics`

### Metrics not updating

1. Check PULSE scheduler is running: `systemctl status faithh-pulse`
2. Verify pulse_state.json exists: `cat ml/output/pulse_state.json`

---

*Created: 2026-03-02*
