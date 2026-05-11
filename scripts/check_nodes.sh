#!/usr/bin/env bash
# Probe SSH ports for infra nodes (matches ~/.ssh/config HostName values).
# Exit 0 only if every nc succeeds.

set -euo pipefail

declare -a TARGETS=(
  "gen8:192.158.1.243:22"
  "dsm:192.158.1.65:22"
  "unifi:192.158.1.1:22"
)

ok=0
fail=0

for entry in "${TARGETS[@]}"; do
  IFS=':' read -r name host port <<<"$entry"
  echo "==> $name ($host:$port)"
  if nc -zv -w 5 "$host" "$port" 2>&1; then
    ((ok++)) || true
  else
    ((fail++)) || true
  fi
  echo
done

echo "Summary: $ok ok, $fail failed"
if (( fail > 0 )); then
  exit 1
fi
