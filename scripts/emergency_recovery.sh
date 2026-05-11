#!/usr/bin/env bash
# FAITHH surgical recovery — kill only FAITHH/gunicorn workers, free :5557, cold restart.
# NEVER: pkill -9 -f "python" (kills Cursor, venv tools, and unrelated apps).

set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO"

echo "================================================"
echo "FAITHH emergency recovery (surgical)"
echo "Repo: $REPO"
echo "================================================"

echo ""
echo "[1] Gunicorn (list → TERM → KILL if needed)"
if pgrep -af gunicorn >/dev/null 2>&1; then
    pgrep -af gunicorn || true
    pkill -f gunicorn 2>/dev/null || true
    sleep 1
    if pgrep -af gunicorn >/dev/null 2>&1; then
        echo "    Still running — SIGKILL gunicorn"
        pkill -9 -f gunicorn 2>/dev/null || true
        sleep 1
    fi
else
    echo "    (no gunicorn processes)"
fi

echo ""
echo "[2] faithh_professional_backend_fixed.py (list → TERM → KILL)"
if pgrep -af "faithh_professional_backend_fixed.py" >/dev/null 2>&1; then
    pgrep -af "faithh_professional_backend_fixed.py" || true
    pkill -f "faithh_professional_backend_fixed.py" 2>/dev/null || true
    sleep 1
    if pgrep -af "faithh_professional_backend_fixed.py" >/dev/null 2>&1; then
        echo "    Still running — SIGKILL backend"
        pkill -9 -f "faithh_professional_backend_fixed.py" 2>/dev/null || true
        sleep 1
    fi
else
    echo "    (no faithh_professional_backend_fixed.py processes)"
fi

echo ""
echo "[3] tmux session faithh (if any)"
if tmux has-session -t faithh 2>/dev/null; then
    tmux kill-session -t faithh
    echo "    Killed tmux session: faithh"
else
    echo "    (no tmux session faithh)"
fi

echo ""
echo "[4] Force-release TCP :5557"
if command -v fuser >/dev/null 2>&1; then
    fuser -k 5557/tcp 2>/dev/null && echo "    fuser sent KILL to holders of 5557/tcp" || echo "    (nothing on 5557 or fuser had nothing to kill)"
else
    echo "    fuser not installed — skip (install psmisc on Debian/Ubuntu)"
fi
sleep 1

if command -v lsof >/dev/null 2>&1; then
    echo "    lsof :5557 (should be empty):"
    lsof -i :5557 2>/dev/null || echo "    (free)"
fi

echo ""
echo "[5] Cold start (restart_backend.sh)"
export FAITHH_FORCE_LOCAL="${FAITHH_FORCE_LOCAL:-1}"
./restart_backend.sh

echo ""
echo "================================================"
echo "Recovery complete"
echo "================================================"
