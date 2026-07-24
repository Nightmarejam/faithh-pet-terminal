# Gen8 Service Optimization Plan

## Current Gen8 Specs (Post-Upgrade)
- CPU: Intel Xeon E3-1265L V2 (4C/8T @ 2.5-3.5GHz)
- RAM: 15GB DDR3-1600 ECC
- Storage: 915GB available
- Network: Gigabit LAN + Tailscale

## Recommended Services

### Tier 1: Immediate (This Week)
```yaml
ChromaDB:
  status: ✅ Already running
  ram_usage: ~2GB
  purpose: RAG vector storage
  priority: HIGH

Ollama (Small Models):
  models:
    - qwen2.5:7b (4.7GB)
    - llama31-faithh:latest (8.5GB)
  ram_usage: ~5GB
  purpose: Offload quick queries
  priority: HIGH

Monitoring:
  services:
    - Prometheus
    - Grafana
  ram_usage: ~1GB
  purpose: Track performance
  priority: MEDIUM
```

### Tier 2: Next Week
```yaml
Backup Service:
  tool: Restic or Duplicati
  ram_usage: ~500MB
  purpose: Automated backups
  priority: MEDIUM

Code Indexing Service:
  tool: Custom Python service
  ram_usage: ~1GB
  purpose: Continuous codebase indexing
  priority: MEDIUM
```

### Tier 3: Future (If Needed)
```yaml
Video Transcoding:
  gpu: Low-profile GPU (RTX 4000/2000)
  purpose: Video embeddings
  priority: LOW

Additional Storage:
  hardware: 2TB SSD
  purpose: More models/data
  priority: LOW
```

## Resource Allocation
```
Total RAM: 15GB
- ChromaDB: 2GB (13GB left)
- Ollama (2 models): 5GB (8GB left)
- OS/System: 2GB (6GB left)
- Monitoring: 1GB (5GB left)
- Buffer/Headroom: 5GB
```

## Network Optimization
- Use LAN IP (servicebox.taileb8c60.ts.net) for speed
- Keep Tailscale for remote access
- Consider dedicated network card if needed

## GPU Options (Low PSU)
1. **NVIDIA RTX 4000** (70W)
   - 8GB VRAM
   - Great for embeddings
   - Low power draw

2. **NVIDIA RTX 2000** (70W)
   - 8GB VRAM
   - Cheaper option
   - Good for inference

3. **Tesla P4** (50W)
   - 8GB VRAM
   - Passive cooling
   - Server-grade

## Implementation Steps

1. Set up Ollama on Gen8
2. Move qwen2.5:7b and llama31-faithh
3. Configure FAITHH to use Gen8 for these models
4. Add monitoring
5. Test performance
6. Consider GPU if needed
