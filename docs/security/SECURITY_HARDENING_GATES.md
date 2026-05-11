# Security Hardening Gates

Status tracker for repeatable hardening and evidence-driven completion.

## Gate model

Each gate requires:

- defined checks
- objective completion criteria
- artifact evidence path(s)

## G0 - Incident Containment

**Goal:** account takeover window closed.

- [x] Microsoft sessions revoked
- [x] password rotated and unique
- [x] MFA active (authenticator — Microsoft Authenticator + fez backup account)
- [x] unknown recovery methods removed
- [x] unknown inbox rules/forwarding/OAuth removed

**Status: COMPLETE — 2026-04-02**

Artifacts:

- `docs/security/account_and_network_hardening_plan_2026-04-02.md`
- operator notes/screenshots (external, private vault)
- backup account confirmed: fez account enrolled as secondary recovery

## G1 - Exposure Baseline Captured

**Goal:** known-good snapshot before changes.

- [x] local and Gen8 listening ports captured
- [x] docker published port map captured
- [x] local firewall and fail2ban status captured
- [x] Gen8 connectivity validated

Artifacts:

- `reports/security/security_hardening_snapshot_20260402_125523.json`
- `reports/security/security_hardening_snapshot_20260402_125523.md`
- `docs/security/network_baseline_2026-04-02.md`

## G2 - SSH and Host Controls Enforced (Gen8)

**Goal:** administrative access hardened.

- [x] `PasswordAuthentication no`
- [x] `PermitRootLogin no`
- [x] key auth verified from trusted client
- [x] fail2ban installed and ssh jail enabled
- [x] rollback path tested

Artifacts:

- `docs/security/gen8_hardening_command_pack.md`
- `docs/security/security_hardening_execution_log_2026-04-02.md`
- post-change snapshot: `reports/security/security_hardening_snapshot_<timestamp>.json`

Evidence captured:

- `reports/security/security_hardening_snapshot_20260402_130948.json`
- `reports/security/G2_rollback_drill_20260402.md`

## G3 - Service Exposure Reduced

**Goal:** infra ports are private-only.

- [ ] public edge minimized (prefer 80/443 only)
- [x] infra ports restricted (3000/3001/3002/5000/5001/8000/9090/9100)
- [x] infra ports restricted (3000/3001/3002/5000/5001/8000/9090/9100/2222)
- [x] vault/service admin endpoints loopback or private ACL only
- [x] external probe confirms denied access for non-edge ports

Artifacts:

- updated `ss -tuln` + docker port snapshot
- firewall rule export and test log

Evidence captured:

- `reports/security/security_hardening_snapshot_20260402_131202.json`
- UFW numbered rules supplied by operator (allow private CIDRs, deny anywhere)
- trusted-network probe confirms private access remains functional
- `reports/security/G3_external_probe_20260402.md` — iPhone 14 cellular, no Tailscale, ports 3000/8000/9090 all timed out (NSURL error domain)

## G4 - Monitoring and Alerting Live

**Goal:** detect auth/network anomalies quickly.

- [x] central log collection enabled (fail2ban metrics via node_exporter textfile collector)
- [x] auth anomaly alerts configured (9 rules in security_alerts.yml)
- [x] network spike/new-listener alerts configured
- [x] alert test event completed (ChromaDBDown fired and recovered during node_exporter stop/start drill)
- [x] fail2ban metrics flowing to Prometheus via textfile collector at `/var/lib/node_exporter/textfile_collector/fail2ban.prom`
- [x] cron updating fail2ban metrics every 30 seconds

Artifacts:

- `reports/security/G4_monitoring_deploy_20260402.md`
- `/home/jonat/ops/monitoring/alert_rules/security_alerts.yml` (9 rules)
- `/usr/local/bin/fail2ban_metrics.py` on Gen8
- `/var/lib/node_exporter/textfile_collector/fail2ban.prom` on Gen8

Evidence captured:

- Prometheus healthy: `http://localhost:9090/-/healthy`
- Alertmanager healthy: `http://localhost:9093/-/healthy`
- Alert fired during test: `ChromaDBDown` (alertname confirmed in API response)
- fail2ban metrics confirmed at: `curl http://localhost:9100/metrics | grep ^fail2ban`
  - `fail2ban_banned_current{jail="sshd"} 0`
  - `fail2ban_banned_total{jail="sshd"} 0`
  - `fail2ban_failed_current{jail="sshd"} 0`
  - `fail2ban_failed_total{jail="sshd"} 0`

## G5 - Runbook-Ready Repeatability

**Goal:** process can be repeated with low error.

- [x] runbook entry created
- [x] run history includes date, outcome, artifact paths
- [x] rollback and failure modes documented
- [x] next-cycle improvement list captured

Artifacts:

- `runbook-to-rule-them-all/runbooks/entries/2026-04-02_account-network-hardening-baseline.md`
- `runbook-to-rule-them-all/runbooks/index.md`

## G6 - UDM Audit

**Goal:** edge firewall/router posture verified and corrected.

- [ ] Admin MFA verified
- [ ] Firmware currency verified
- [x] Port-forwarding rules audited
- [x] VLAN/firewall segmentation reviewed
- [x] Action list executed/documented

Artifacts:

- `docs/security/G5_UDM_audit_20260402.md`
- `docs/security/G6_UDM_audit_20260402.md`

## G7 - NAS and Endpoint Audit

**Goal:** NAS and workstation baseline controls verified.

- [ ] NAS account/firewall/service audit completed (G6_NAS_audit template created — operator fill-in pending)
- [x] Windows endpoint audit completed — PASS WITH FINDINGS (2026-04-02)
- [x] Findings recorded with remediation actions

**Windows findings summary:**
- Defender enabled, real-time protection active ✅
- All firewall profiles enabled ✅
- Updates current (2026-03-14) ✅
- All scheduled tasks recognized (FAITHH, Ollama, AMD, NVIDIA, Firefox, OneDrive) ✅
- Minor: FAITHH backend (:5557) and node_exporter (:9100) on 0.0.0.0 — acceptable on LAN
- Minor: DefaultInboundAction NotConfigured — recommend setting to Block
- No unknown processes or suspicious tasks found ✅

Artifacts:

- `docs/security/G6_NAS_audit_20260402.md`
- `reports/security/G7_windows_audit_20260402.md`
