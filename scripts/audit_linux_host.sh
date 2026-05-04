#!/usr/bin/env bash
# Linux host baseline audit → Markdown (faithh, Gen8/servicebox, or any Linux).
# Versioned under ai-stack; symlink ~/audit_run.sh → this file on faithh if desired.
#
# Usage:
#   bash ~/ai-stack/scripts/audit_linux_host.sh
#   AUDIT_SLUG=servicebox AUDIT_ROLE="Gen8 homelab" bash ~/ai-stack/scripts/audit_linux_host.sh
#   OUT=~/audit/audit-gen8-$(date -u +%Y-%m-%d).md AUDIT_SLUG=gen8 bash ~/ai-stack/scripts/audit_linux_host.sh
set -uo pipefail

AUDIT_DIR="${AUDIT_DIR:-$HOME/audit}"
mkdir -p "$AUDIT_DIR"

AUDIT_SLUG="${AUDIT_SLUG:-$(hostname)}"
AUDIT_ROLE="${AUDIT_ROLE:-Ubuntu VM / server}"
TS=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
DATE_UTC=$(date -u +"%Y-%m-%d")
OUT="${OUT:-$AUDIT_DIR/audit-${AUDIT_SLUG}-${DATE_UTC}.md}"

INCLUDE_FAITHH_HANDOFF="${INCLUDE_FAITHH_HANDOFF:-}"
if [ "$AUDIT_SLUG" = "faithh" ] || [ "$(hostname)" = "faithh" ]; then
  INCLUDE_FAITHH_HANDOFF=1
fi

{
cat <<HEADER
# ${AUDIT_SLUG} — Linux host audit

**Generated (UTC)**: $TS
**Host audited**: ${AUDIT_SLUG} (${AUDIT_ROLE})
**Multi-host context**: \`~/ai-stack/docs/ops/MULTI_HOST_AUDIT.md\` (identify **faithh** vs **servicebox** / Gen8 before comparing ports). On the inference VM, \`~/audit/ECOSYSTEM-TOPOLOGY.md\` may also exist.

## Executive summary

- Read-only baseline (Phase A) and config drift scan (Phase B).
- Secrets are not pasted (netplan passwords, CIFS credentials redacted).

HEADER

echo "## Phase A — ${AUDIT_SLUG} baseline"
echo
echo "### A1 Identity and OS"
echo '```'
hostnamectl || true
uname -a
uptime
echo '```'
echo

echo "### A2 Networking"
echo '```'
ip -br a || true
ip r || true
echo "--- netplan (list + readable files only) ---"
ls -la /etc/netplan 2>/dev/null || true
for f in /etc/netplan/*.yaml; do
  [ -e "$f" ] || continue
  if [ -r "$f" ]; then echo "# $f"; sed 's/password:.*$/password: <redacted>/' "$f"; else echo "# $f (not readable without sudo)"; fi
done
echo "--- tailscale ---"
if command -v tailscale >/dev/null 2>&1; then tailscale status || true; else echo "tailscale: not installed"; fi
echo '```'
echo

echo "### A3 GPU and CUDA stack"
echo '```'
nvidia-smi || true
echo "--- venv python check ---"
if [ -f "$HOME/vllm-env/bin/activate" ]; then
  # shellcheck disable=SC1090
  source "$HOME/vllm-env/bin/activate"
  python -c "import vllm, torch; print('vllm', vllm.__version__); print('torch', torch.__version__); print('cuda_available', torch.cuda.is_available())" || true
else
  echo "MISSING: ~/vllm-env/bin/activate (optional on non-inference hosts)"
fi
echo '```'
echo

echo "### A4 Mounts and storage"
echo '```'
findmnt /mnt/nas 2>/dev/null || echo "/mnt/nas not mounted"
df -hT / /mnt/nas 2>/dev/null || df -hT /
echo "--- fstab (non-comment) ---"
grep -vE '^#|^$' /etc/fstab 2>/dev/null | sed 's/password=[^ ]*/password=<redacted>/g' || true
if [ -d "$HOME/wsl_migration" ]; then
  echo "--- wsl_migration sizes ---"
  du -sh "$HOME/wsl_migration"/* 2>/dev/null || true
else
  echo "--- wsl_migration: not present ---"
fi
echo '```'
echo

echo "### A5 Listeners (vLLM / common dev ports)"
echo '```'
ss -lntp 2>/dev/null | grep -E ':8000|:5557|:11434|:8080' || echo "No matches for :8000 :5557 :11434 :8080"
curl -sS --connect-timeout 2 http://127.0.0.1:8000/v1/models 2>&1 | head -20 || true
echo '```'
echo
echo "### A5b Listening sockets (first 50 lines)"
echo '_Use this on homelab hosts (e.g. Gen8) where many services run._'
echo '```'
ss -lntp 2>/dev/null | head -50 || true
echo '```'
echo

echo "### A6 Models on disk (NAS / local)"
echo '```'
ls -la /mnt/nas/models 2>/dev/null || echo "cannot list /mnt/nas/models (NAS may be unmounted)"
du -sh /mnt/nas/models/* 2>/dev/null | head -50 || true
if [ -d "$HOME/wsl_migration/ml_output/output" ]; then
  echo "--- LoRA output dirs ---"
  du -sh "$HOME/wsl_migration/ml_output/output"/* 2>/dev/null | head -30 || true
fi
echo '```'
echo

echo "### A7 Cursor paths (this user)"
echo '```'
ls -la "$HOME/.cursor" 2>/dev/null | head -30 || echo "no ~/.cursor"
ls -la "$HOME/.cursor-server" 2>/dev/null | head -15 || echo "no ~/.cursor-server"
test -f "$HOME/.cursor/skills-cursor/.sync-manifest.json" && echo "--- skills sync-manifest ---" && head -20 "$HOME/.cursor/skills-cursor/.sync-manifest.json" || true
echo '```'
echo

echo "## Phase B — codebase and config drift"

AI_STACK=""
if [ -d "$HOME/ai-stack" ]; then
  AI_STACK="$HOME/ai-stack"
elif [ -d "$HOME/wsl_migration/projects/projects/ai-stack" ]; then
  AI_STACK="$HOME/wsl_migration/projects/projects/ai-stack"
elif [ -d "$HOME/wsl_migration/projects/ai-stack" ]; then
  AI_STACK="$HOME/wsl_migration/projects/ai-stack"
else
  AI_STACK=$(find "$HOME/wsl_migration/projects" -maxdepth 6 -type d -name ai-stack 2>/dev/null | head -1)
fi
echo
echo "**Resolved ai-stack root**: \`${AI_STACK:-NOT FOUND}\`"
echo

if [ -n "$AI_STACK" ] && [ -d "$AI_STACK" ]; then
  echo "### B1 venv presence"
  echo '```'
  ls -la "$AI_STACK/.venv" 2>/dev/null || ls -la "$AI_STACK/venv" 2>/dev/null || echo "no .venv or venv in ai-stack root"
  echo '```'
  echo
  echo "### B2 Grep: ollama, Tailscale IPs, API bases"
  echo '```'
  cd "$AI_STACK"
  grep -RIn --exclude-dir=.git --exclude-dir=node_modules --exclude-dir=.venv --exclude-dir=venv \
    -e 'ollama' -e '11434' -e 'openai.com' -e 'OPENAI_API_BASE' -e 'api.openai' \
    -e 'BASE_URL' -e 'VITE_' \
    -e '100\.79\.85\.32' -e '100\.' \
    -e '192\.158\.1\.204' -e 'localhost:8000' \
    --include='*.py' --include='*.env' --include='*.env.*' --include='*.yaml' --include='*.yml' --include='*.ts' --include='*.tsx' --include='*.js' --include='*.json' \
    . 2>/dev/null | head -200 || true
  echo '```'
  echo
  echo "### B3 Environment file inventory"
  echo '```'
  find "$AI_STACK" -maxdepth 4 \( -name '.env' -o -name '.env.*' \) 2>/dev/null | head -40
  echo '```'
  echo "### B3b .env.example (preview)"
  echo '```'
  if [ -f "$AI_STACK/.env.example" ]; then head -80 "$AI_STACK/.env.example"; else echo "(no .env.example at root)"; fi
  echo '```'
  echo
  echo "### B4 ENVIRONMENT.md"
  echo '```'
  ls -la "$AI_STACK/ENVIRONMENT.md" 2>/dev/null || echo "ENVIRONMENT.md: absent"
  echo '```'
else
  echo "_ai-stack directory not found — install or clone under ~/ai-stack or extend find manually._"
fi

if [ -n "$INCLUDE_FAITHH_HANDOFF" ]; then
  echo
  echo "## Phase C — Checklist pointers (FAITHH handoff Section 7)"
  echo "- **FAITHH → vLLM**: use Phase B2 grep results; point base URL to \`http://192.158.1.204:8000\` (verify current IP in A2)."
  echo "- **ai-stack venv**: Phase B1."
  echo "- **QwQ smoke**: A6 model on disk + A5 listener; start server per handoff Section 6 when ready."
  echo "- **Static IP**: Phase A2 netplan + DHCP note."
  echo "- **MOTU / USB disk / Proxmox disk move**: blocked from Linux; handoff Phase D."
  echo "- **Chroma**: source \`~/wsl_migration/knowledge_base/\`; prior host 100.79.85.32 per handoff."
  echo "- **Tailscale on Ubuntu**: A2."
  echo
  echo "## Canonical handoff reference"
  echo "- **FAITHH_Environment_Handoff_2026-04-20.docx** (April 20, 2026)"
  echo "- Historical snapshot (same script, older filename): \`$AUDIT_DIR/2026-04-20-p2v-audit.md\` if preserved."
  echo
fi

} > "$OUT"

echo "WROTE:$OUT"
wc -l "$OUT"
