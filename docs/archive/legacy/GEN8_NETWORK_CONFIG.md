# Gen8 Network Configuration Guide

**Date:** 2026-01-20  
**Server IP:** servicebox.taileb8c60.ts.net (LAN) / servicebox.taileb8c60.ts.net (Tailscale)

## 🌐 Service Port Map

| Service | Port | URL | Purpose |
|---------|------|-----|---------|
| ChromaDB | 8000 | http://servicebox.taileb8c60.ts.net:8000 | Vector Database |
| Docker Registry | 5000 | http://servicebox.taileb8c60.ts.net:5000 | Private Docker Registry |
| Registry UI | 5001 | http://servicebox.taileb8c60.ts.net:5001 | Registry Web Interface |
| Prometheus | 9090 | http://servicebox.taileb8c60.ts.net:9090 | Metrics Collection |
| Grafana | 3000 | http://servicebox.taileb8c60.ts.net:3000 | Monitoring Dashboard |
| Gitea | 3002 | http://servicebox.taileb8c60.ts.net:3002 | Git Repository Hosting |
| Uptime Kuma | 3001 | http://servicebox.taileb8c60.ts.net:3001 | Uptime Monitoring |
| Node Exporter | 9100 | http://servicebox.taileb8c60.ts.net:9100 | System Metrics |
| GitLab Runner | - | - | CI/CD Runner |

## 🔧 Pi-hole Configuration

### Current State:
- Pi-hole container running on Gen8
- **NOT configured as DNS server** yet

### Steps to Configure Pi-hole:

1. **Access Pi-hole Admin:**
   ```
   http://servicebox.taileb8c60.ts.net:???? (check port)
   ```

2. **Set as DNS Server on Windows:**
   - Open Network Settings
   - Change DNS to: servicebox.taileb8c60.ts.net
   - Alternative: 8.8.8.8 (fallback)

3. **Set as DNS Server on Router:**
   - Access router admin
   - DHCP Settings → DNS
   - Primary: servicebox.taileb8c60.ts.net
   - Secondary: 8.8.8.8

4. **Configure Pi-hole:**
   - Add blocklists
   - Set up local DNS records
   - Enable query logging

## 🏠 Home Network DNS Records

Add these to Pi-hole Local DNS:

| Name | IP | Purpose |
|------|----|---------|
| gen8.local | servicebox.taileb8c60.ts.net | Gen8 Server |
| faithh.local | servicebox.taileb8c60.ts.net | FAITHH Backend |
| registry.local | servicebox.taileb8c60.ts.net | Docker Registry |
| monitoring.local | servicebox.taileb8c60.ts.net | Grafana |
| git.local | servicebox.taileb8c60.ts.net | Gitea |

## 📱 External Access (Tailscale)

All services accessible via Tailscale:
- ChromaDB: http://servicebox.taileb8c60.ts.net:8000
- Grafana: http://servicebox.taileb8c60.ts.net:3000
- Registry: http://servicebox.taileb8c60.ts.net:5000
- Gitea: http://servicebox.taileb8c60.ts.net:3002

## 🔒 Security Recommendations

1. **Firewall Rules:**
   ```bash
   # Allow only necessary ports
   sudo ufw allow 22/tcp    # SSH
   sudo ufw allow 53/tcp    # DNS
   sudo ufw allow 53/udp    # DNS
   sudo ufw allow 80/tcp    # HTTP
   sudo ufw allow 443/tcp   # HTTPS
   ```

2. **Service Authentication:**
   - Grafana: Change default password
   - Gitea: Set up authentication
   - Registry: Add authentication if needed

3. **VPN Access:**
   - Use Tailscale for external access
   - Disable external port forwarding where possible

## 📊 Monitoring Setup

### Grafana Dashboards to Create:
1. **System Overview**
   - CPU, Memory, Disk usage
   - Network traffic
   - Uptime status

2. **Docker Containers**
   - Container health
   - Resource usage per container
   - Restart counts

3. **ChromaDB Metrics**
   - Query performance
   - Document count
   - Storage usage

### Prometheus Targets:
- Node Exporter: System metrics
- ChromaDB: Database metrics
- Docker: Container metrics
- Custom: Application metrics

## 🚀 Performance Optimization

1. **Network Optimization:**
   - Use LAN IP for internal traffic
   - Reserve Tailscale for remote access
   - Consider dedicated network card

2. **Service Distribution:**
   - Heavy tasks on Windows host
   - Background services on Gen8
   - Load balance where possible

3. **Resource Monitoring:**
   - Set alerts for high CPU/memory
   - Monitor disk space
   - Track network bandwidth

## 🔧 Troubleshooting

### Service Not Accessible:
1. Check container status: `docker ps`
2. Check logs: `docker logs <service>`
3. Verify port: `netstat -tlnp | grep <port>`

### High Resource Usage:
1. Check top processes: `htop`
2. Monitor containers: `docker stats`
3. Check disk usage: `df -h`

### Network Issues:
1. Ping test: `ping servicebox.taileb8c60.ts.net`
2. Port test: `telnet servicebox.taileb8c60.ts.net <port>`
3. DNS test: `nslookup gen8.local`

## 📋 Next Steps

1. **Configure Pi-hole** as primary DNS
2. **Set up Grafana dashboards**
3. **Configure monitoring alerts**
4. **Test service redundancy**
5. **Document backup procedures**

---

**All services running successfully!** 🎉

The Gen8 is now a fully equipped development and monitoring server.
