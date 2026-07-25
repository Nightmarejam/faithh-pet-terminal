# Monitoring Security Stack

This directory contains the `G4` monitoring/alerting configuration scaffold.

## Files

- `prometheus.yml` - scrape config + rule wiring + alertmanager wiring
- `alert_rules/security_alerts.yml` - security/capacity/availability alerts
- `alertmanager.yml` - default routing and webhook receiver
- `docker-compose.yml` - Prometheus + Alertmanager local stack

## Deployment commands (run on Gen8)

```bash
cd /home/jonat/ai-stack/ops/monitoring
docker compose up -d
docker exec prometheus promtool check config /etc/prometheus/prometheus.yml
docker exec prometheus promtool check rules /etc/prometheus/alert_rules/security_alerts.yml
curl -s http://localhost:9093/-/healthy
```

## Optional: fail2ban exporter

```bash
docker run -d \
  --name fail2ban-exporter \
  --restart unless-stopped \
  -p 127.0.0.1:9635:9635 \
  -v /var/run/fail2ban/fail2ban.sock:/var/run/fail2ban/fail2ban.sock \
  jangrewe/fail2ban-exporter
```
