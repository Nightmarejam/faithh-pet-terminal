# Account and Network Hardening Plan (2026-04-02)

**Scope:** Microsoft account incident response + home-lab network hardening  
**Goal:** Reduce account takeover and lateral movement risk with practical controls now.

---

## 0) Threat framing

Likely event: credential/session compromise attempt against Microsoft account.  
Do not assume full infrastructure breach yet.

Guiding rule: **stabilize first, then expand controls.**

---

## 1) Immediate account hardening (today)

- [ ] Complete Microsoft "sign out everywhere"
- [ ] Set new unique password (not reused)
- [ ] Enforce 2FA with Microsoft Authenticator
- [ ] Remove unknown devices, aliases, app passwords
- [ ] Audit Outlook rules/forwarding/connected apps
- [ ] Rotate passwords for high-impact linked systems (GitHub, cloud, banking, vault)

Evidence:

- screenshots or notes of each completed control
- list of revoked devices/apps/rules

---

## 2) Identity architecture target (this week)

### Primary

- Password manager-generated unique secrets
- Authenticator-based OTP
- Recovery methods controlled and documented

### Fallbacks (multiple, but controlled)

- Fallback A: recovery code stored offline
- Fallback B: secondary recovery email (hardened separately)
- Fallback C: hardware key (recommended next upgrade)

No SMS-only fallback as sole backup.

---

## 3) Network hardening baseline (UDM-first)

Start with UDM v1 before introducing new firewall complexity.

- [ ] Update UDM firmware to latest stable
- [ ] Disable UPnP unless explicitly needed
- [ ] Review port forwarding; remove unknown/inactive rules
- [ ] Separate VLAN/SSID for lab servers and IoT
- [ ] Restrict management interfaces to trusted VLAN only
- [ ] Enable and export security/event logs
- [ ] Set DNS filtering policy (malware/phishing blocklists)

24/7 services to prioritize:

- secure DNS + egress policy
- centralized logging
- endpoint patch visibility

---

## 4) Monitoring uplift (10x visibility, practical version)

Minimum viable stack:

- UDM logs -> central collector (syslog)
- Gen8 server auth logs + service logs
- alert rules for:
  - impossible travel / unusual geo login
  - repeated auth failure bursts
  - new admin device enrollment
  - unexpected outbound spikes

Targets:

- detect critical auth anomalies within 5 minutes
- retain logs >= 30 days

---

## 5) SSH hardening standard (all hosts)

- [ ] Disable password auth (`PasswordAuthentication no`)
- [ ] Disable root login (`PermitRootLogin no`)
- [ ] Use key auth only (ed25519 preferred)
- [ ] Add fail2ban or equivalent rate limiting
- [ ] Restrict SSH by source IP/VPN where possible
- [ ] Rotate and inventory SSH keys

Optional:

- short-lived SSH certificates for admin access

---

## 6) pfSense decision gate (build P300 or not)

Only build pfSense if one of these is true after UDM hardening:

1. UDM cannot deliver required segmentation/egress controls
2. Logging/alerting depth remains insufficient
3. Throughput or rule complexity exceeds UDM stability

If none are true, keep UDM as primary and avoid operational overhead.

---

## 7) 14-day execution sequence

Day 0-1:

- Complete account incident controls
- UDM patch + rule audit

Day 2-4:

- VLAN segmentation and SSH baseline across hosts
- central log collection enabled

Day 5-7:

- alert tuning and test incidents
- rotate remaining high-risk credentials

Day 8-14:

- review alert quality and false positives
- decide on pfSense build via gate criteria

---

## 8) Success criteria

- no unknown account sessions
- no insecure SSH endpoints
- network policy documented and reproducible
- alerting in place for identity and network anomalies
- clear yes/no decision on pfSense migration
