# NAS Node Exporter Setup (Synology DSM)

Gen8 LAN IP used in this stack: **servicebox.taileb8c60.ts.net**. Metrics port: **9100**.

## Verify from WSL or Gen8

```bash
curl -s --connect-timeout 5 "http://servicebox.taileb8c60.ts.net:9100/metrics" | grep "^node_cpu_seconds_total" | head -3
```

You should see `node_cpu_seconds_total{cpu=...}` lines. Custom metrics (for example `fail2ban_*`) may appear if a textfile collector is configured.

## If SSH is available

```bash
ssh admin@servicebox.taileb8c60.ts.net
docker run -d --name node-exporter --restart unless-stopped \
  --net=host --pid=host \
  -v /:/host:ro,rslave \
  prom/node-exporter:latest --path.rootfs=/host
```

If a container named `node-exporter` already exists, remove or rename it before creating a new one.

## If using DSM Container Manager UI

1. Open DSM → **Container Manager** → **Registry**
2. Search: `prom/node-exporter`
3. Download the **latest** tag
4. **Container** → **Create**
5. Image: `prom/node-exporter:latest`
6. Network: **Host** (recommended on Synology for correct host metrics)
7. **Volume**: map **`/`** → **`/host`** (read-only)
8. **Command** (execution command / arguments): `--path.rootfs=/host`
9. Enable **auto-restart**
10. **Launch**

## Prometheus (this repo)

Scrape job is defined in `ops/monitoring/prometheus.yml` under `job_name: nas`. After editing the file on the host that runs Prometheus:

```bash
curl -X POST http://localhost:9090/-/reload
```

Or restart the Prometheus container if reload is disabled.

## Grafana

- Import dashboard **1860** (*Node Exporter Full*): **Dashboards** → **Import** → ID `1860` → Load → choose Prometheus datasource.
- **Template variables** on that dashboard use **`node_uname_info`** (not `node_exporter_build_info`). With only the **`nas`** scrape healthy, set **job = `nas`**, **nodename = `servicebox`**, **node = `nas`** (or run the patch below).
- **Dedicated NAS dashboard** (no variables): from the repo, with Grafana on `localhost:3000` and password in `~/ops/monitoring/.env`:

  ```bash
  python3 ~/ai-stack/scripts/provision_grafana_infra_dashboards.py
  ```

  Creates/updates **NAS Storage (Synology)**, **Windows Host**, and **Infrastructure Overview** (CPU for `nas`+`wsl_node`+Windows, filtered `up{job=~"...")}`, memory, WSL `/` disk, NAS disks, FAITHH request rate).

  Panel audit (instant PromQL; ignores `$variable` panels on Node Exporter Full):

  ```bash
  python3 ~/ai-stack/scripts/audit_grafana_dashboard_panels.py
  ```

- **Admin password**: WSL Docker stack uses `GRAFANA_PASSWORD` in **`~/ops/monitoring/.env`** (not `admin`/`admin`).

API import requires that password or an API key (`POST /api/dashboards/db`).

## Related

- `docs/guides/MONITORING_SETUP.md`
- `docs/guides/NAS_MONTHLY_OPERATIONS_RUNBOOK.md`
