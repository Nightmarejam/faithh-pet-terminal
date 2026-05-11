# UDM API Read-Only Setup (LAN)

Purpose: safely enable repeatable API visibility from your workstation without editing policy via API.

---

## 1) What is already confirmed

- `https://192.158.1.1/api/auth/login` is reachable and returns `401 Unauthorized` when unauthenticated (expected).
- `https://192.158.1.1/unifi-api/network` is the UniFi OS frontend path (not a direct data API endpoint).

This means API surface is present; authenticated session setup is the remaining step.

---

## 2) One-command read-only snapshot

Script:

- `scripts/unifi_api_readonly_snapshot.sh`

Set credentials in your current shell:

```bash
export UDM_USER="your-unifi-console-username"
export UDM_PASS="your-unifi-console-password"
```

If your UniFi account has MFA enabled (common), also set:

```bash
export UDM_MFA_TOKEN="123456"
```

`UDM_MFA_TOKEN` should be a current one-time code from your configured authenticator flow.

Run snapshot:

```bash
cd /home/jonat/ai-stack
./scripts/unifi_api_readonly_snapshot.sh
```

Output folder:

- `reports/security/unifi_api/snapshot_<timestamp>/`

Includes:

- login/logout responses
- redacted auth responses (`*_redacted.json`)
- per-endpoint JSON payloads
- `summary.txt` with endpoint -> HTTP status

---

## 3) Safety guardrails

- Keep this script read-only (GET calls only).
- Do not commit credentials, cookie jars, or raw auth tokens.
- Prefer dedicated low-privilege UniFi operator account for automation.
- Store long-term secrets in vault tooling, not shell history.

---

## 4) Mapping your Policy Engine article to your environment

For your current goals (latency + stability + hardening), prioritize in this order:

1. **QoS / traffic shaping** (gateway-level)
2. **Zone-based firewall + port forwarding cleanup**
3. **Application/content filtering** (if needed after latency baseline)
4. **Policy-based routing** (only when you intentionally route by WAN/VPN)

Use with caution or skip for now:

- **Pro AV optimization**: only if you actually run Dante/Q-SYS/NDI/AES67 workflows.
- **Complex ACL + object choreography** on day one: adds operational complexity quickly.

Object Manager is useful, but start with a small set of outcomes first:

- Gaming device group: prioritize, avoid hard bandwidth caps.
- IoT group: internet-only + local isolation.
- Admin devices group: management-plane access only from trusted clients.

---

## 5) UI label drift (where to look if names changed)

Search in UniFi settings for these terms:

- `Policy Engine`
- `Objects`
- `Traffic Rules`
- `Smart Queue`
- `Port Forwarding`
- `Firewall`
- `Application Filtering`
- `Minimum RSSI`

If menu paths differ by version, rely on term search rather than exact breadcrumb.

---

## 6) Suggested next steps

1. Run read-only API snapshot and save artifact path.
2. Summarize snapshot into runbook-friendly inventory artifacts.
3. Apply QoS/policy changes in UI (source of truth).
4. Re-run snapshot and diff `summary.txt` + key endpoint payloads.
5. Capture before/after latency tests for gaming host and Wi-Fi clients.

---

## 7) Endpoint compatibility note (observed 2026-04-02)

From snapshot `reports/security/unifi_api/snapshot_20260402_160218/summary.txt`:

- `200`:
  - `/proxy/network/api/self`
  - `/proxy/network/api/s/default/stat/health`
  - `/proxy/network/api/s/default/stat/device`
  - `/proxy/network/api/s/default/stat/sta`
  - `/proxy/network/api/s/default/stat/sysinfo`
  - `/proxy/network/v2/api/site/default/trafficrules`
  - `/proxy/network/v2/api/site/default/firewall-policies`
- `404` (not exposed on this build/path):
  - `/proxy/network/v2/api/site/default/port-forwarding`
  - `/proxy/network/v2/api/site/default/application-filters`

Interpretation:

- Use `trafficrules` and `firewall-policies` as canonical policy sources.
- Port forward visibility may be embedded in `firewall-policies` (`origin_type:"port_forward"` entries) rather than a dedicated endpoint on this version.
- `logout` returning `403` can occur after token invalidation and is acceptable for this read-only workflow.

---

## 8) Snapshot summarizer workflow

Summarizer script:

- `scripts/unifi_api_summarize_snapshot.py`

Generate inventory from latest snapshot:

```bash
cd /home/jonat/ai-stack
python3 scripts/unifi_api_summarize_snapshot.py
```

Generate inventory from a specific snapshot:

```bash
python3 scripts/unifi_api_summarize_snapshot.py \
  --snapshot-dir /home/jonat/ai-stack/reports/security/unifi_api/snapshot_<timestamp>
```

Default outputs (inside the selected snapshot directory):

- `policy_inventory.md`
- `policy_inventory.csv`

Inventory sections produced:

- Active custom traffic rules
- Disabled/stale custom traffic rules
- Active custom firewall policies
- Disabled/stale custom firewall policies
- Port-forward-derived firewall entries

Stale detection:

- A rule is marked stale when schedule windows appear inactive (ended or not started).
- Disabled/stale sections include both disabled and schedule-stale rules.

---

## 9) Runbook insertion order

After each snapshot run, insert artifacts in this order:

1. `summary.txt` (endpoint health/evidence)
2. `policy_inventory.md` (human review baseline)
3. `policy_inventory.csv` (sortable/filterable source)

For `RUNBOOK_SOURCE_PACK` style updates, attach the latest snapshot path and include key count deltas (active vs disabled/stale, plus port-forward-derived count) in the run log.

