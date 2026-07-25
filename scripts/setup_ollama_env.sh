#!/bin/bash
# FAITHH Model Setup Script
# Sets optimal Ollama environment for RTX 3090 + 47GB RAM
# Run: source scripts/setup_ollama_env.sh

echo "=== FAITHH Ollama Environment Setup ==="
echo "Hardware: RTX 3090 (24GB VRAM), 47GB RAM"
echo ""

# ============================================
# ENVIRONMENT VARIABLES
# ============================================
export OLLAMA_NUM_PARALLEL=2          # Allow 2 concurrent requests
export OLLAMA_MAX_LOADED_MODELS=2     # Keep 2 models hot in VRAM
export OLLAMA_FLASH_ATTENTION=1       # Enable flash attention (faster)
export OLLAMA_NUM_GPU=1               # Use primary GPU (RTX 3090)
export OLLAMA_KEEP_ALIVE="10m"        # Keep models loaded for 10 minutes

echo "✅ Environment variables set:"
echo "   OLLAMA_NUM_PARALLEL=$OLLAMA_NUM_PARALLEL"
echo "   OLLAMA_MAX_LOADED_MODELS=$OLLAMA_MAX_LOADED_MODELS"
echo "   OLLAMA_FLASH_ATTENTION=$OLLAMA_FLASH_ATTENTION"
echo "   OLLAMA_NUM_GPU=$OLLAMA_NUM_GPU"
echo "   OLLAMA_KEEP_ALIVE=$OLLAMA_KEEP_ALIVE"
echo ""

# ============================================
# ADD TO BASHRC (Optional)
# ============================================
add_to_bashrc() {
    local BASHRC="$HOME/.bashrc"
    local MARKER="# FAITHH Ollama Settings"
    
    if grep -q "$MARKER" "$BASHRC" 2>/dev/null; then
        echo "⚠️  Ollama settings already in ~/.bashrc"
    else
        echo "" >> "$BASHRC"
        echo "$MARKER" >> "$BASHRC"
        echo "export OLLAMA_NUM_PARALLEL=2" >> "$BASHRC"
        echo "export OLLAMA_MAX_LOADED_MODELS=2" >> "$BASHRC"
        echo "export OLLAMA_FLASH_ATTENTION=1" >> "$BASHRC"
        echo "export OLLAMA_NUM_GPU=1" >> "$BASHRC"
        echo "export OLLAMA_KEEP_ALIVE=10m" >> "$BASHRC"
        echo "✅ Added to ~/.bashrc (will persist across sessions)"
    fi
}

# ============================================
# CREATE OPTIMIZED MODELS
# ============================================
create_optimized_models() {
    local MODELFILES_DIR="$HOME/ai-stack/modelfiles"
    
    echo "Creating optimized model variants..."
    echo ""
    
    # Check if modelfiles exist
    if [ ! -d "$MODELFILES_DIR" ]; then
        echo "❌ Modelfiles directory not found: $MODELFILES_DIR"
        return 1
    fi
    
    # Create clean baseline models (no persona)
    echo "Creating llama31-clean (baseline, no persona)..."
    ollama create llama31-clean -f "$MODELFILES_DIR/llama31-clean.Modelfile" 2>&1 | tail -1
    
    echo "Creating qwen3-clean (baseline, no persona)..."
    ollama create qwen3-clean -f "$MODELFILES_DIR/qwen3-clean.Modelfile" 2>&1 | tail -1
    
    # Create hardware-optimized models
    echo "Creating qwen25-optimized (speed optimized)..."
    ollama create qwen25-optimized -f "$MODELFILES_DIR/qwen25-optimized.Modelfile" 2>&1 | tail -1
    
    echo "Creating qwen25-coder-optimized..."
    ollama create qwen25-coder-optimized -f "$MODELFILES_DIR/qwen25-coder-optimized.Modelfile" 2>&1 | tail -1
    
    echo "Creating deepseek-r1-optimized (reasoning optimized)..."
    ollama create deepseek-r1-optimized -f "$MODELFILES_DIR/deepseek-r1-optimized.Modelfile" 2>&1 | tail -1
    
    echo ""
    echo "✅ Optimized models created!"
}

# ============================================
# SHOW CURRENT MODELS
# ============================================
show_models() {
    echo ""
    echo "=== Current Ollama Models ==="
    ollama list
}

# ============================================
# MAIN
# ============================================
echo "Options:"
echo "  1) Set environment only (current session)"
echo "  2) Set environment + add to ~/.bashrc (persistent)"
echo "  3) Create optimized model variants"
echo "  4) All of the above"
echo "  5) Show current models"
echo ""
read -p "Select option [1-5]: " choice

case $choice in
    1)
        echo "Environment set for current session."
        ;;
    2)
        add_to_bashrc
        ;;
    3)
        create_optimized_models
        show_models
        ;;
    4)
        add_to_bashrc
        create_optimized_models
        show_models
        ;;
    5)
        show_models
        ;;
    *)
        echo "Invalid option. Environment variables are set for this session."
        ;;
esac

echo ""
echo "=== Setup Complete ==="
echo "Run 'ollama list' to see available models"
echo "Run benchmark: python scripts/benchmarks/benchmark_models.py --quick"
