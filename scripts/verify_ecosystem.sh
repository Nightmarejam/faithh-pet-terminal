#!/bin/bash
# verify_ecosystem.sh - Quick verification of FAITHH ecosystem health

set -e

echo "======================================"
echo "FAITHH Ecosystem Verification"
echo "======================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check_pass() {
    echo -e "${GREEN}✓${NC} $1"
}

check_fail() {
    echo -e "${RED}✗${NC} $1"
}

check_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Check canonical files exist
echo "Checking canonical files..."
if [ -f "faithh_professional_backend_fixed.py" ]; then
    check_pass "Backend: faithh_professional_backend_fixed.py"
else
    check_fail "Backend: faithh_professional_backend_fixed.py NOT FOUND"
fi

if [ -f "faithh_pet_v4.html" ]; then
    check_pass "UI: faithh_pet_v4.html"
else
    check_fail "UI: faithh_pet_v4.html NOT FOUND"
fi

if [ -f "docker-compose.yml" ]; then
    check_pass "Docker: docker-compose.yml"
else
    check_fail "Docker: docker-compose.yml NOT FOUND"
fi

if [ -f "config.yaml" ]; then
    check_pass "Config: config.yaml"
else
    check_fail "Config: config.yaml NOT FOUND"
fi

echo ""
echo "Checking state files..."
for file in faithh_memory.json decisions_log.json project_states.json scaffolding_state.json; do
    if [ -f "$file" ]; then
        check_pass "State: $file"
    else
        check_warn "State: $file NOT FOUND"
    fi
done

echo ""
echo "Checking for duplicate issues..."

# Check for duplicate backends
backend_count=$(find . -maxdepth 1 -name "*backend*.py" -type f | wc -l)
if [ "$backend_count" -gt 2 ]; then
    check_warn "Found $backend_count backend files in root (expected 2: main + shim)"
else
    check_pass "Backend files: $backend_count (acceptable)"
fi

# Check for duplicate UIs
ui_count=$(find . -maxdepth 1 -name "faithh_pet*.html" -type f | wc -l)
if [ "$ui_count" -gt 2 ]; then
    check_warn "Found $ui_count UI files in root (expected 1-2)"
else
    check_pass "UI files: $ui_count (acceptable)"
fi

# Check for duplicate archives
if [ -d "archive" ] && [ -d "ARCHIVE" ]; then
    check_warn "Both 'archive' and 'ARCHIVE' directories exist"
elif [ -d "archive" ]; then
    check_pass "Archive directory: archive/"
else
    check_warn "No archive directory found"
fi

echo ""
echo "Checking Docker services..."
if command -v docker &> /dev/null; then
    if docker-compose ps 2>/dev/null | grep -q "Up"; then
        check_pass "Docker services are running"
        docker-compose ps | tail -n +2 | while read line; do
            service=$(echo $line | awk '{print $1}')
            status=$(echo $line | awk '{print $4}')
            if [[ "$status" == "Up" ]]; then
                check_pass "  - $service"
            else
                check_fail "  - $service ($status)"
            fi
        done
    else
        check_warn "Docker services not running (use: docker-compose up -d)"
    fi
else
    check_warn "Docker not installed or not in PATH"
fi

echo ""
echo "Checking backend status..."
if curl -s http://localhost:5557/health > /dev/null 2>&1; then
    check_pass "Backend is responding on :5557"
else
    check_warn "Backend not responding (use: ./restart_backend.sh)"
fi

echo ""
echo "Checking system resources..."
if command -v nvidia-smi &> /dev/null; then
    if nvidia-smi &> /dev/null; then
        check_pass "NVIDIA GPU detected"
        gpu_count=$(nvidia-smi --list-gpus | wc -l)
        echo "  GPUs: $gpu_count"
    else
        check_warn "nvidia-smi failed (driver issue?)"
    fi
else
    check_warn "nvidia-smi not found (no GPU support)"
fi

total_mem=$(free -g | awk '/^Mem:/{print $2}')
if [ "$total_mem" -ge 80 ]; then
    check_pass "Memory: ${total_mem}GB (sufficient for full stack)"
elif [ "$total_mem" -ge 32 ]; then
    check_warn "Memory: ${total_mem}GB (may be tight for all services)"
else
    check_fail "Memory: ${total_mem}GB (insufficient for recommended setup)"
fi

disk_free=$(df -BG . | awk 'NR==2 {print $4}' | sed 's/G//')
if [ "$disk_free" -ge 100 ]; then
    check_pass "Disk space: ${disk_free}GB free"
elif [ "$disk_free" -ge 50 ]; then
    check_warn "Disk space: ${disk_free}GB free (monitor usage)"
else
    check_fail "Disk space: ${disk_free}GB free (critically low)"
fi

echo ""
echo "Checking for common issues..."

# Check for Zone.Identifier files
zone_count=$(find . -name "*.Zone.Identifier" 2>/dev/null | wc -l)
if [ "$zone_count" -gt 0 ]; then
    check_warn "Found $zone_count Zone.Identifier files (Windows metadata)"
    echo "  Run: find . -name '*.Zone.Identifier' -delete"
else
    check_pass "No Zone.Identifier files"
fi

# Check for Jupyter checkpoints
checkpoint_count=$(find . -type d -name ".ipynb_checkpoints" 2>/dev/null | wc -l)
if [ "$checkpoint_count" -gt 0 ]; then
    check_warn "Found $checkpoint_count Jupyter checkpoint directories"
    echo "  Run: find . -type d -name '.ipynb_checkpoints' -exec rm -rf {} +"
else
    check_pass "No Jupyter checkpoints"
fi

# Check for empty files in root
empty_count=$(find . -maxdepth 1 -type f -size 0 2>/dev/null | wc -l)
if [ "$empty_count" -gt 0 ]; then
    check_warn "Found $empty_count empty files in root"
else
    check_pass "No empty files in root"
fi

echo ""
echo "======================================"
echo "Verification complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo "  1. Review reports/ecosystem_analysis_*.md for detailed analysis"
echo "  2. Read ECOSYSTEM_CONSOLIDATION_PLAN.md for cleanup recommendations"
echo "  3. Read MULTI_DEVICE_DEPLOYMENT_STRATEGY.md for deployment guide"
echo ""
