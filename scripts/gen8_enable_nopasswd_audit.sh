#!/usr/bin/env bash
set -euo pipefail

# Installs a least-privilege sudoers rule on Gen8 for audit automation only.
# This will prompt once for the Gen8 sudo password.

RULE_FILE="/etc/sudoers.d/jonat-security-audit"
RULE_LINE='jonat ALL=(root) NOPASSWD: /usr/sbin/ufw status numbered, /usr/bin/fail2ban-client status sshd'

echo "Applying least-privilege NOPASSWD rule on Gen8..."
ssh -tt gen8 "printf '%s\n' \"$RULE_LINE\" | sudo tee \"$RULE_FILE\" >/dev/null && sudo chmod 440 \"$RULE_FILE\" && sudo visudo -cf \"$RULE_FILE\""

echo "Verifying non-interactive sudo commands on Gen8..."
ssh -o BatchMode=yes gen8 "sudo -n /usr/sbin/ufw status numbered >/dev/null && echo 'ufw sudo-nopasswd: OK' || echo 'ufw sudo-nopasswd: FAIL'"
ssh -o BatchMode=yes gen8 "sudo -n /usr/bin/fail2ban-client status sshd >/dev/null && echo 'fail2ban sudo-nopasswd: OK' || echo 'fail2ban sudo-nopasswd: FAIL'"

echo "Done."
