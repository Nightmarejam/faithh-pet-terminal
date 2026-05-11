# Security Hardening Execution Log (2026-04-02)

## Step evidence: SSH service discovery on Gen8

Operator session confirmed:

- host: `servicebox`
- ssh daemon: `ssh.service` (systemd-managed OpenSSH)
- ssh listeners:
  - `0.0.0.0:22`
  - `[::]:22`
- auth events show accepted `publickey` login for `jonat`

Interpretation:

- SSH is host-managed (not only container-managed).
- Key-based auth is confirmed working.
- Environment is ready for SSH hardening directives + fail2ban + firewall steps.

## Gate impact

- `G1 Exposure Baseline Captured`: confirmed complete
- `G2 SSH and Host Controls Enforced`: in progress (discovery + key-auth verification complete)

## Step evidence: SSH hardening + fail2ban enforcement

Operator output confirmed:

- `sshd -t` passed and `ssh.service` reloaded successfully
- hardening directives present in `/etc/ssh/sshd_config`:
  - `PasswordAuthentication no`
  - `PermitRootLogin no`
  - `PubkeyAuthentication yes`
  - `KbdInteractiveAuthentication no`
  - `ChallengeResponseAuthentication no`
  - `MaxAuthTries 3`
  - `LoginGraceTime 30`
  - `AllowUsers jonat`
- `fail2ban` installed and running
- `fail2ban-client status sshd` shows active `sshd` jail

Artifacts:

- `reports/security/security_hardening_snapshot_20260402_130948.json`
- `reports/security/security_hardening_snapshot_20260402_130948.md`

Updated gate status:

- `G2`: mostly complete; rollback drill remains open item
- Next gate: `G3 Service Exposure Reduced`

## Step evidence: UFW policy deployment for infra ports

Operator output confirmed:

- UFW enabled with default `deny incoming`, `allow outgoing`
- SSH allow rules retained before enforcement
- infra ports policy applied:
  - allow from `100.64.0.0/10` (Tailscale/private)
  - allow from `192.168.0.0/16` (LAN/private)
  - deny from `Anywhere` (+ v6 deny)
  - ports: `3000, 3001, 3002, 5000, 5001, 8000, 9090, 9100`

Interpretation:

- service processes still listen on `0.0.0.0`, but firewall now mediates reachability.
- trusted-source tests from this client succeed by design (client is in private allowed range).
- pending validation: test from non-allowed source to confirm deny behavior.

Artifacts:

- `reports/security/security_hardening_snapshot_20260402_131202.json`
- `reports/security/security_hardening_snapshot_20260402_131202.md`

## Next required actions

1. enforce sshd directives (`PasswordAuthentication no`, `PermitRootLogin no`, etc.)
2. validate config and reload ssh service
3. install/enable fail2ban ssh jail
4. apply UFW baseline with SSH-safe sequencing
5. re-run security snapshot and compare artifacts
