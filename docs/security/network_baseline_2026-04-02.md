# Network Baseline Snapshot (2026-04-02)

## Current observed state

### Control plane access

- Gen8 SSH: reachable at LAN `192.158.1.243` (`gen8` in hosts) from contexts that route to that subnet
- NAS SSH from this node: timeout
- UDM SSH from this node: **timeout** to `192.168.1.1` (wrong segment from WSL). See `docs/security/UDM_SSH_discovery_20260402.md`: **`192.158.1.1` responds on port 22**; auth requires UniFi SSH setup (not open `root` key by default).

### Local dev node (WSL) security controls

- `ufw`: not installed
- `fail2ban`: not installed
- `sshd`: not present on this WSL instance

### Gen8 exposure (remote `ss -tuln` + `docker ps`)

Public/listening TCP services include:

- `22` (SSH)
- `80`, `443`
- `2222` (Gitea SSH)
- `3000` (Grafana)
- `3001` (Uptime Kuma)
- `3002` (Gitea HTTP)
- `5000`, `5001` (Registry + UI)
- `8000` (ChromaDB)
- `9090` (Prometheus)
- `9100` (node_exporter)

Loopback-only examples:

- Vaultwarden (`127.0.0.1:3012`, `127.0.0.1:8080`)
- some internal service ports (`127.0.0.1:*`)

## What a "good running network" should look like

### Exposure profile

- Internet-facing ports: minimal and intentional (ideally 80/443 only via reverse proxy)
- Infra/ops ports (Prometheus, Grafana, Chroma, Registry, Gitea admin): private-only (LAN or Tailscale ACL)
- SSH: key-only, IP-restricted where possible

### Identity posture

- MFA everywhere
- no stale sessions
- no forwarding rules or unknown OAuth app grants

### Monitoring posture

- central log retention >= 30 days
- auth anomaly alerts (geo, impossible travel, failures)
- network/service anomaly alerts (new listener, outbound spike, repeated denied traffic)

## P0 actions (execute next)

1. Lock down Gen8 port exposure:
   - move non-public services behind LAN/Tailscale-only access
   - keep only required public entry points
2. Harden SSH daemon on Gen8:
   - `PasswordAuthentication no`
   - `PermitRootLogin no`
   - key auth only
3. Enable host-level protection on Gen8:
   - firewall rules (UFW or equivalent)
   - fail2ban SSH jail
4. Validate UDM management path:
   - confirm current LAN IP and SSH enablement
   - update firmware and disable unnecessary WAN forwards

## "Not overreacting" decision on pfSense box

Build the P300 pfSense box only if UDM cannot satisfy at least one:

- required segmentation/ACL complexity
- required log/alert depth
- stable throughput with policy stack

If UDM can satisfy all three after tuning, keep UDM primary and avoid extra operational burden.
