#!/bin/bash
# GPU-Aware Model Router for FAITHH
# Respects 1080 Ti for gaming, uses RTX 3090 for AI

# Check if gaming/streaming is active (simplified check)
is_gaming() {
    # Check for common gaming processes
    if pgrep -f "steam\|nvidia\|obs\|elgato" > /dev/null; then
        return 0
    fi
    return 1
}

# Check which GPU is primary display
get_primary_gpu() {
    # Check xrandr or similar for display connection
    # For now, assume 1080 Ti is primary display
    echo "1080ti"
}

# Model selection logic
select_model() {
    local query_complexity=$1
    local needs_reasoning=$2
    
    # If gaming, use CPU only or very small model
    if is_gaming; then
        echo "llama3.1:8b"
        return
    fi
    
    # Complex reasoning -> 70B on 3090
    if [ "$needs_reasoning" = "true" ]; then
        echo "llama3.3:70b"
        return
    fi
    
    # Default -> 14B on 3090
    echo "qwen25-grounded:latest"
}

# Test the router
echo "Testing GPU-Aware Model Router..."
echo "Gaming active: $(is_gaming && echo 'Yes' || echo 'No')"
echo "Primary GPU: $(get_primary_gpu)"
echo "Simple query model: $(select_model 'low' 'false')"
echo "Complex query model: $(select_model 'high' 'true')"
