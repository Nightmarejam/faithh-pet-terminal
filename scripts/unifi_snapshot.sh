#!/usr/bin/env bash
# unifi_snapshot.sh — one-command UniFi snapshot + summarize
# Loads credentials from .env, prompts only for the MFA token.
# Usage:
#   ./scripts/unifi_snapshot.sh                    # prompts for MFA token
#   UDM_MFA_TOKEN=123456 ./scripts/unifi_snapshot.sh  # non-interactive
#
# From Cursor: just run this script. It handles everything.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${REPO_ROOT}/.env"

# Load .env (skip blank lines and comments)
if [[ -f "${ENV_FILE}" ]]; then
  set -o allexport
  # shellcheck disable=SC1090
  source <(grep -v '^\s*#' "${ENV_FILE}" | grep -v '^\s*$')
  set +o allexport
fi

# Prompt for MFA token if not already set
if [[ -z "${UDM_MFA_TOKEN:-}" ]]; then
  read -r -p "UniFi Verify app code: " UDM_MFA_TOKEN
  export UDM_MFA_TOKEN
fi

# Require password to be set
if [[ -z "${UDM_PASS:-}" ]]; then
  read -r -s -p "UniFi password: " UDM_PASS
  echo
  export UDM_PASS
fi

export UDM_BASE_URL UDM_USER UDM_PASS UDM_MFA_TOKEN

cd "${REPO_ROOT}"

echo "--- Running snapshot ---"
bash scripts/unifi_api_readonly_snapshot.sh

echo ""
echo "--- Summarizing ---"
python3 scripts/unifi_api_summarize_snapshot.py

echo ""
echo "Done. Check reports/security/unifi_api/ for latest snapshot."
