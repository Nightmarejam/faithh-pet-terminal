# Gen8 NOPASSWD Sudo Policy (Least Privilege)

Purpose: allow automated security snapshots without granting broad passwordless root.

## Scope

Grant `jonat` NOPASSWD for exactly:

- `/usr/sbin/ufw status numbered`
- `/usr/bin/fail2ban-client status sshd`

No wildcard sudo. No shell sudo. No service restart sudo.

## One-command installer

From WSL:

```bash
cd /home/jonat/ai-stack
bash scripts/gen8_enable_nopasswd_audit.sh
```

This prompts once for the Gen8 sudo password, writes `/etc/sudoers.d/jonat-security-audit`, validates it with `visudo -cf`, then tests non-interactive sudo.

## Manual equivalent

On Gen8:

```bash
printf '%s\n' 'jonat ALL=(root) NOPASSWD: /usr/sbin/ufw status numbered, /usr/bin/fail2ban-client status sshd' | sudo tee /etc/sudoers.d/jonat-security-audit >/dev/null
sudo chmod 440 /etc/sudoers.d/jonat-security-audit
sudo visudo -cf /etc/sudoers.d/jonat-security-audit
```

## Rollback

```bash
sudo rm -f /etc/sudoers.d/jonat-security-audit
```
