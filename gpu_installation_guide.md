# Tesla T1000 8GB Installation Guide for Gen8 MicroServer

## Pre-Installation Checklist

### Hardware Requirements
- **Tesla T1000 8GB** (low profile, single-slot)
- **Gen8 MicroServer** with 150W PSU
- **PCIe x16 slot** (should be available)
- **Power connector**: None required (draws from PCIe)

### Compatibility Check
- ✅ **Power**: 50W TDP fits within 150W PSU budget
- ✅ **Form Factor**: Low profile fits Gen8 chassis
- ✅ **PCIe**: Standard PCIe x16 interface
- ✅ **Cooling**: Passive cooling, no extra fans needed

## Installation Steps

### 1. Prepare Server
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install NVIDIA drivers (prepare)
sudo apt install nvidia-driver-470 nvidia-cuda-toolkit -y

# Check current kernel
uname -r
```

### 2. Physical Installation
1. **Power down** Gen8 server completely
2. **Open chassis** (remove side panel)
3. **Locate PCIe x16 slot** (should be empty)
4. **Remove slot cover** if present
5. **Insert Tesla T1000** firmly into slot
6. **Secure with screw** if bracket has hole
7. **Close chassis**
8. **Power on** server

### 3. Driver Installation
```bash
# After boot, check GPU detection
lspci | grep -i nvidia

# Install appropriate driver
sudo ubuntu-drivers autoinstall
# Or specific version:
sudo apt install nvidia-driver-535 -y

# Reboot
sudo reboot

# Verify installation
nvidia-smi
```

### 4. Configure for Plex & Embeddings

#### Plex GPU Transcoding
```bash
# Install Plex Media Server
# In Plex settings: Settings > Transcoder > Enable GPU hardware acceleration
# Select "NVIDIA NVENC" for transcoding
```

#### Embedding Acceleration
```python
# Test GPU acceleration
import torch
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Test with sentence-transformers
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2', device=device)
embeddings = model.encode(["test text"])
print(f"Embeddings shape: {embeddings.shape}")
```

## Post-Installation Validation

### Power Monitoring
```bash
# Monitor power usage
nvidia-smi -l 1 -q -d POWER

# Check total system power
sudo tlp-stat | grep -E "(POWER|THROTTLE)"
```

### Performance Testing
```bash
# Test Plex transcoding
ffmpeg -i test_video.mp4 -c:v h264_nvenc -preset fast output.mp4

# Test embedding speed
python3 -c "
from sentence_transformers import SentenceTransformer
import time
model = SentenceTransformer('all-MiniLM-L6-v2', device='cuda')
start = time.time()
embeddings = model.encode(['test'] * 100)
print(f'100 embeddings in {time.time()-start:.2f}s')
"
```

## Troubleshooting

### Common Issues
1. **GPU not detected**: Check PCIe seating, power, drivers
2. **Driver conflicts**: Remove old drivers first
3. **Power issues**: Monitor total draw <140W
4. **Thermal throttling**: Ensure adequate ventilation

### Commands
```bash
# Check GPU status
nvidia-smi
lspci -v | grep -A10 -B5 nvidia

# Check driver version
cat /proc/driver/nvidia/version

# Monitor temperature
nvidia-smi --query-gpu=temperature.gpu --format=csv

# Reset drivers if needed
sudo apt purge nvidia-* -y
sudo apt autoremove -y
sudo reboot
```

## Expected Performance

### Tesla T1000 8GB Specifications
- **CUDA Cores**: 640
- **Memory**: 8GB GDDR5
- **Memory Bandwidth**: 112 GB/s
- **Power**: 50W TDP
- **Encoding**: 1x Decode, 2x Encode engines

### Performance Targets
- **Plex Transcoding**: >2x real-time for 1080p
- **Embeddings**: 3-5x faster than CPU
- **Power Usage**: <60W under load
- **Temperature**: <70°C under load

## Next Steps After Installation

1. Configure Plex for GPU transcoding
2. Setup embedding acceleration in FAITHH
3. Monitor power usage and performance
4. Optimize settings for workloads
