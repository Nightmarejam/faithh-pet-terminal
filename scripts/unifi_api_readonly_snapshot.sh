#!/usr/bin/env bash
set -euo pipefail

# Read-only UniFi API snapshot helper for local gateway management.
# This script logs into UniFi OS, pulls selected Network app endpoints,
# writes JSON responses to disk, and logs out.

UDM_BASE_URL="${UDM_BASE_URL:-https://192.168.1.1}"
UDM_USER="${UDM_USER:-}"
UDM_PASS="${UDM_PASS:-}"
UDM_MFA_TOKEN="${UDM_MFA_TOKEN:-}"
OUT_DIR="${OUT_DIR:-reports/security/unifi_api}"
COOKIE_JAR="${COOKIE_JAR:-/tmp/unifi_api_cookie_$$.txt}"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
RUN_DIR="${OUT_DIR}/snapshot_${TIMESTAMP}"
SUMMARY_FILE="${RUN_DIR}/summary.txt"

if [[ -z "${UDM_USER}" || -z "${UDM_PASS}" ]]; then
  echo "ERROR: set UDM_USER and UDM_PASS environment variables." >&2
  echo "Example:" >&2
  echo "  export UDM_USER='your-console-user'" >&2
  echo "  export UDM_PASS='your-console-password'" >&2
  echo "  ./scripts/unifi_api_readonly_snapshot.sh" >&2
  exit 1
fi

mkdir -p "${RUN_DIR}"
touch "${SUMMARY_FILE}"

login_payload="$(printf '{"username":"%s","password":"%s","rememberMe":false}' "${UDM_USER}" "${UDM_PASS}")"

login_code="$(
  curl -k -sS \
    -o "${RUN_DIR}/auth_login.json" \
    -w "%{http_code}" \
    -c "${COOKIE_JAR}" \
    -H "Content-Type: application/json" \
    -X POST "${UDM_BASE_URL}/api/auth/login" \
    -d "${login_payload}"
)"

redact_json_file() {
  local input_file="$1"
  local output_file="$2"
  python3 - <<'PY' "${input_file}" "${output_file}"
import json
import sys
from pathlib import Path

in_path = Path(sys.argv[1])
out_path = Path(sys.argv[2])
try:
    data = json.loads(in_path.read_text())
except Exception:
    out_path.write_text(in_path.read_text())
    raise SystemExit(0)

def redact(obj):
    if isinstance(obj, dict):
        for key in list(obj.keys()):
            if key.lower() in {"mfacookie", "token", "authorization", "password"}:
                obj[key] = "<redacted>"
            else:
                redact(obj[key])
    elif isinstance(obj, list):
        for item in obj:
            redact(item)

redact(data)
out_path.write_text(json.dumps(data, indent=2, sort_keys=True))
PY
}

if [[ "${login_code}" != "200" ]]; then
  login_error_code="$(python3 - <<'PY' "${RUN_DIR}/auth_login.json"
import json
import sys
try:
    data = json.load(open(sys.argv[1]))
    print(data.get("code", ""))
except Exception:
    print("")
PY
)"

  if [[ "${login_error_code}" == "MFA_AUTH_REQUIRED" ]]; then
    if [[ -z "${UDM_MFA_TOKEN}" ]]; then
      redact_json_file "${RUN_DIR}/auth_login.json" "${RUN_DIR}/auth_login_redacted.json"
      echo "ERROR: MFA is required. Set UDM_MFA_TOKEN and re-run." >&2
      echo "Saved redacted response: ${RUN_DIR}/auth_login_redacted.json" >&2
      rm -f "${COOKIE_JAR}"
      exit 1
    fi

    mfa_cookie="$(
      python3 - <<'PY' "${RUN_DIR}/auth_login.json"
import json
import sys
try:
    data = json.load(open(sys.argv[1]))
    print(data.get("data", {}).get("mfaCookie", ""))
except Exception:
    print("")
PY
    )"

    if [[ -z "${mfa_cookie}" ]]; then
      redact_json_file "${RUN_DIR}/auth_login.json" "${RUN_DIR}/auth_login_redacted.json"
      echo "ERROR: MFA required but mfaCookie missing. See ${RUN_DIR}/auth_login_redacted.json" >&2
      rm -f "${COOKIE_JAR}"
      exit 1
    fi

    mfa_payload="$(
      printf '{"username":"%s","password":"%s","token":"%s","rememberMe":false}' \
        "${UDM_USER}" "${UDM_PASS}" "${UDM_MFA_TOKEN}"
    )"

    mfa_login_code="$(
      curl -k -sS \
        -o "${RUN_DIR}/auth_login_mfa.json" \
        -w "%{http_code}" \
        -b "${COOKIE_JAR}" \
        -c "${COOKIE_JAR}" \
        -H "Content-Type: application/json" \
        -H "Cookie: ${mfa_cookie}" \
        -X POST "${UDM_BASE_URL}/api/auth/login" \
        -d "${mfa_payload}"
    )"

    if [[ "${mfa_login_code}" != "200" ]]; then
      redact_json_file "${RUN_DIR}/auth_login.json" "${RUN_DIR}/auth_login_redacted.json"
      redact_json_file "${RUN_DIR}/auth_login_mfa.json" "${RUN_DIR}/auth_login_mfa_redacted.json"
      echo "ERROR: MFA login failed (HTTP ${mfa_login_code})." >&2
      echo "See ${RUN_DIR}/auth_login_redacted.json and ${RUN_DIR}/auth_login_mfa_redacted.json" >&2
      rm -f "${COOKIE_JAR}"
      exit 1
    fi

    echo "Login success with MFA: HTTP ${mfa_login_code}" | tee -a "${SUMMARY_FILE}"
  else
    redact_json_file "${RUN_DIR}/auth_login.json" "${RUN_DIR}/auth_login_redacted.json"
    echo "ERROR: login failed (HTTP ${login_code}). See ${RUN_DIR}/auth_login_redacted.json" >&2
    rm -f "${COOKIE_JAR}"
    exit 1
  fi
else
  echo "Login success: HTTP ${login_code}" | tee -a "${SUMMARY_FILE}"
fi

redact_json_file "${RUN_DIR}/auth_login.json" "${RUN_DIR}/auth_login_redacted.json"

declare -a endpoints=(
  "/proxy/network/api/self"
  "/proxy/network/api/s/default/stat/health"
  "/proxy/network/api/s/default/stat/device"
  "/proxy/network/api/s/default/stat/sta"
  "/proxy/network/api/s/default/stat/sysinfo"
  "/proxy/network/v2/api/site/default/trafficrules"
  "/proxy/network/v2/api/site/default/port-forwarding"
  "/proxy/network/v2/api/site/default/firewall-policies"
  "/proxy/network/v2/api/site/default/application-filters"
)

sanitize_name() {
  local value="$1"
  value="${value#/}"
  value="${value//\//_}"
  value="${value//\?/_}"
  value="${value//&/_}"
  echo "${value}"
}

for endpoint in "${endpoints[@]}"; do
  file_stub="$(sanitize_name "${endpoint}")"
  out_file="${RUN_DIR}/${file_stub}.json"
  code="$(
    curl -k -sS \
      -o "${out_file}" \
      -w "%{http_code}" \
      -b "${COOKIE_JAR}" \
      -H "Accept: application/json" \
      "${UDM_BASE_URL}${endpoint}"
  )"
  echo "${endpoint} -> HTTP ${code}" | tee -a "${SUMMARY_FILE}"
done

logout_code="$(
  curl -k -sS \
    -o "${RUN_DIR}/auth_logout.json" \
    -w "%{http_code}" \
    -b "${COOKIE_JAR}" \
    -H "Content-Type: application/json" \
    -X POST "${UDM_BASE_URL}/api/auth/logout" \
    -d '{}'
)"
echo "Logout attempt: HTTP ${logout_code}" | tee -a "${SUMMARY_FILE}"

redact_json_file "${RUN_DIR}/auth_logout.json" "${RUN_DIR}/auth_logout_redacted.json"

rm -f "${COOKIE_JAR}"
echo "Snapshot written to ${RUN_DIR}"
