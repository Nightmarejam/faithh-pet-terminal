# Runbook Source Pack (2026-04-02)

Purpose: single reference pack for building and maintaining the account/network hardening runbook without context switching.

---

## 1) Primary anchor documents (start here)

Use these in order:

1. `docs/security/SECURITY_HARDENING_GATES.md`  
   Gate status and completion evidence.
2. `docs/security/FAITHH_SECURITY_IMPLEMENTATION_SPEC.md`  
   What artifacts/components were implemented.
3. `docs/security/account_and_network_hardening_plan_2026-04-02.md`  
   Baseline intent and operating sequence.

---

## 2) Local evidence artifacts (repo paths)

### Core security state

- `docs/security/network_baseline_2026-04-02.md`
- `docs/security/security_hardening_execution_log_2026-04-02.md`
- `reports/security/security_snapshot_20260402_150630.md`
- `reports/security/security_hardening_snapshot_20260402_125523.md`
- `reports/security/security_hardening_snapshot_20260402_130948.md`
- `reports/security/security_hardening_snapshot_20260402_131202.md`

### Gate-specific evidence

- `reports/security/G0_account_lockdown_complete_20260402.md`
- `reports/security/G2_rollback_drill_20260402.md`
- `reports/security/G2_nopasswd_validation_20260402.md`
- `reports/security/G3_external_probe_20260402.md`
- `reports/security/G4_monitoring_deploy_20260402.md`

### UDM / NAS / Endpoint audit material

- `docs/security/G5_UDM_audit_20260402.md`
- `docs/security/G6_UDM_audit_20260402.md`
- `docs/security/G6_NAS_audit_20260402.md`
- `reports/security/G7_windows_audit_20260402.md`
- `docs/security/UDM_SSH_discovery_20260402.md`
- `docs/security/UDM_SSH_routing_20260402.md`

### Monitoring config (for reproducible deploy)

- `ops/monitoring/prometheus.yml`
- `ops/monitoring/alertmanager.yml`
- `ops/monitoring/docker-compose.yml`
- `ops/monitoring/alert_rules/security_alerts.yml`
- `ops/monitoring/README.md`

### Runbook linkage

- `runbook-to-rule-them-all/runbooks/entries/2026-04-02_account-network-hardening-baseline.md`
- `runbook-to-rule-them-all/runbooks/index.md`

---

## 3) Official external references

### UniFi / Ubiquiti

- [UniFi Help Center](https://help.ui.com/hc/en-us)
- [UniFi Network category](https://help.ui.com/hc/en-us/categories/200320654-UniFi-Network)
- [Firewall and Traffic Rules guidance](https://help.ui.com/hc/en-us/articles/115003173168)

### Security frameworks

- [NIST Cybersecurity Framework 2.0](https://www.nist.gov/cyberframework)
- [CIS Controls v8](https://www.cisecurity.org/controls)
- [OWASP Web Security Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
- [CISA Logging Made Easy](https://www.cisa.gov/resources-tools/services/logging-made-easy)

### Defensive learning platforms (legal/ethical)

- [PortSwigger Web Security Academy](https://portswigger.net/web-security)
- [TryHackMe](https://tryhackme.com)
- [Hack The Box Academy](https://academy.hackthebox.com)
- [MITRE ATT&CK](https://attack.mitre.org)

---

## 4) UniFi UI crosswalk (new policy engine names)

The UI names can drift by version. Use this map as a translation guide:

- **Traffic shaping / QoS**
  - Usually under `Settings -> Internet -> [WAN] -> Smart Queues` or
  - `Settings -> Policy Engine -> Traffic Management / Application QoS`
- **Firewall policy**
  - Usually under `Settings -> Policy Engine -> Traffic Rules`
- **Port forwards**
  - Usually under `Settings -> Policy Engine -> Port Forwarding`
- **Wi-Fi radio tuning**
  - Usually under `Settings -> WiFi -> [SSID]` and `Settings -> WiFi -> Radios`
- **Admin/MFA**
  - Usually under `Settings -> System -> Admins` and `Settings -> System -> Authentication`
- **System logs**
  - Usually under `System Log`, `Insights`, or `Settings -> System -> Log`

If a menu is missing, use search in settings for these terms:
`smart queue`, `traffic rule`, `port forward`, `wifi channel`, `minimum rssi`, `band steering`.

---

## 5) What is automatable vs UI-only

- Safe to automate by SSH: diagnostics, snapshots, validation checks.
- Prefer UI for persistent policy changes: Smart Queues, Wi-Fi settings, policy engine rules.
- Internal API/DB changes are possible but version-fragile and can be overwritten by reprovision.

---

## 6) API status notes (current environment)

- Local endpoint `https://192.168.1.1/unifi-api/network` is reachable from trusted LAN.
- Reachability does not mean API automation is fully configured.
- To operationalize API usage, define:
  - auth method (session/cookie/token),
  - allowed automation scope (read-only first),
  - secret storage path (Vaultwarden or equivalent),
  - rollback process for write operations.

---

## 7) Practical runbook build order

1. Copy Sections 1-2 into your runbook draft.
2. Add your chosen UI settings and final values (with screenshots).
3. Add command-based verification outputs after each UI change.
4. Record before/after latency and packet-loss metrics.
5. Close each gate in `SECURITY_HARDENING_GATES.md` only with artifact evidence.

