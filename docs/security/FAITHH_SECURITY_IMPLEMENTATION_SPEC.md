# FAITHH Security Implementation Spec

Date: 2026-04-02  
Status: implementation baseline (repository artifacts created)

This repository implementation follows the gate order requested in session:

1. `G4` monitoring config scaffolding
2. `G0` manual account lockdown checklist
3. `G2` rollback drill artifact path
4. `G3` external probe artifact path
5. `G5/G6/G7` audit templates
6. pfSense decision after UDM audit

## Implemented files

### Monitoring (`G4`)

- `ops/monitoring/alert_rules/security_alerts.yml`
- `ops/monitoring/prometheus.yml`
- `ops/monitoring/alertmanager.yml`
- `ops/monitoring/docker-compose.yml`

### Account/security docs and artifacts (`G0/G2/G3/G5/G6/G7`)

- `docs/security/G0_account_lockdown_checklist.md`
- `reports/security/G0_account_lockdown_complete_20260402.md`
- `reports/security/G2_rollback_drill_20260402.md`
- `reports/security/G3_external_probe_20260402.md`
- `docs/security/G5_UDM_audit_20260402.md`
- `docs/security/G6_NAS_audit_20260402.md`
- `reports/security/G7_windows_audit_20260402.md`

### Gate and runbook tracking

- `docs/security/SECURITY_HARDENING_GATES.md`
- `docs/security/security_hardening_execution_log_2026-04-02.md`
- `runbook-to-rule-them-all/runbooks/entries/2026-04-02_account-network-hardening-baseline.md`
- `runbook-to-rule-them-all/runbooks/index.md`

## Operational note

The monitoring stack in `ops/monitoring/` is repository-ready but not yet validated against live containers in this workspace. Deploy and validation should be performed on Gen8 with operator sudo access and then recorded in `reports/security/`.
