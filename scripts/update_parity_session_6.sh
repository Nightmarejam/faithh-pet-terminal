#!/bin/bash
# update_parity_session_6.sh
# Updates parity files with Session 6 progress

PARITY_DIR="$HOME/ai-stack/parity"
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")

echo "🔄 Updating parity files for Session 6..."

# Update changelog
cat >> "$PARITY_DIR/changelog/SESSION_6_CHANGELOG.md" << 'EOF'

## Session 6 Continuation - Image Generation Setup
**Date:** 2025-11-09
**Focus:** Discovered existing image gen tools, prepared for avatar creation

### Discoveries Made
- ✅ ComfyUI already installed at ~/ComfyUI/
- ✅ Stable Diffusion WebUI at ~/stable-diffusion-webui/
- ✅ Both tools ready to use - no installation needed
- ✅ Backend v3 stable and running (port 5557)
- ✅ UI v4 files prepared but awaiting avatar images

### Documentation Created
- IMAGE_GENERATION_SETUP.md - Comprehensive guide
- START_HERE.md - Quick reference
- CURRENT_STATUS_SUMMARY.md - Project state
- Multiple prompt guides from Claude sessions

### Next Steps Defined
1. Generate FAITHH avatar (chibi style, cyan highlights)
2. Generate PULSE avatar (technical style, blue theme)
3. Save to ~/ai-stack/images/faithh_v2/avatars/
4. Integrate into v3 UI first
5. Complete v4 UI with new avatars

### Tools Status
| Tool | Status | Location | Purpose |
|------|--------|----------|---------|
| Stable Diffusion WebUI | ✅ Ready | ~/stable-diffusion-webui/ | Image generation |
| ComfyUI | ✅ Ready | ~/ComfyUI/ | Advanced image workflows |
| Backend v3 | ✅ Running | Port 5557 | API server |
| ChromaDB | ✅ Active | 91,302 docs | RAG system |
| Ollama | ✅ Active | 2 models | Local AI |

### Time Estimates
- Avatar generation: 45-75 minutes
- Integration into v3: 20 minutes  
- Testing: 10 minutes
- v4 UI completion: 2-3 hours
- v4 backend endpoints: 1-2 hours

### Decision Points
- **Image Tool Choice:** Recommend Stable Diffusion WebUI (easier)
- **UI Strategy:** Update v3 first, then complete v4
- **Backend:** Add v4 endpoints after UI stable

EOF

echo "✅ Changelog updated"

# Create quick status file
cat > "$HOME/ai-stack/SESSION_6_STATUS.md" << 'EOF'
# Session 6 Status Report
**Last Updated:** $(date +"%Y-%m-%d %H:%M:%S")

## 🎯 Current Objective
Generate FAITHH and PULSE avatar images using existing local tools

## ✅ Completed
- [x] Reviewed all documentation from multiple AI sessions
- [x] Located existing ComfyUI installation
- [x] Located existing Stable Diffusion WebUI installation
- [x] Verified backend is running (port 5557)
- [x] Confirmed v3 UI is working
- [x] Prepared prompts for avatar generation
- [x] Created comprehensive documentation
- [x] Updated parity files

## ⏳ In Progress
- [ ] Generate FAITHH avatar variations
- [ ] Generate PULSE avatar variations
- [ ] Select best versions
- [ ] Save to project images folder

## 📋 Next Actions
1. Start Stable Diffusion WebUI: `cd ~/stable-diffusion-webui && ./webui.sh --listen`
2. Open browser: http://localhost:7860
3. Generate 10 FAITHH variations using prompts
4. Generate 10 PULSE variations
5. Pick best 2 of each
6. Save to `~/ai-stack/images/faithh_v2/avatars/`

## 🔧 Tools Ready
- Stable Diffusion WebUI: ~/stable-diffusion-webui/ ✅
- ComfyUI: ~/ComfyUI/ ✅
- Backend: http://localhost:5557 ✅
- ChromaDB: 91,302 documents ✅
- Ollama: 2 models ✅

## 📊 Success Criteria
- [ ] Have faithh_small.png (128x128 or scalable)
- [ ] Have pulse_small.png (128x128 or scalable)
- [ ] Images match retro-futuristic aesthetic
- [ ] FAITHH looks friendly, cyan highlights
- [ ] PULSE looks technical, blue theme
- [ ] Both are distinct but cohesive

## ⚡ Quick Commands
```bash
# Start image generation
cd ~/stable-diffusion-webui && ./webui.sh --listen

# Check backend
curl http://localhost:5557/api/status

# Create images directory
mkdir -p ~/ai-stack/images/faithh_v2/avatars

# Test v3 UI
cd ~/ai-stack && python -m http.server 8000
# Open: http://localhost:8000/faithh_pet_v3.html
```

## 📁 Documentation Available
- IMAGE_GENERATION_SETUP.md
- START_HERE.md  
- CURRENT_STATUS_SUMMARY.md
- READY_TO_USE_PROMPTS.md
- LEONARDO_AI_PROMPTS_ENHANCED.md
- FAITHH_V4_UI_SPECIFICATION.md
- FAITHH_V4_BACKEND_API.md
- VS_CODE_IMPLEMENTATION_HANDOFF.md

---
**Next Update:** After generating first batch of images
EOF

echo "✅ Status file created: ~/ai-stack/SESSION_6_STATUS.md"

# Update main parity README
cat >> "$PARITY_DIR/README.md" << 'EOF'

## Session 6 Update (2025-11-09)
**Focus:** Image Generation Tool Discovery and Setup

### Key Achievements
- Discovered existing ComfyUI and SD-WebUI installations
- Prepared comprehensive prompts for FAITHH/PULSE avatars
- Documented multiple AI assistant sessions
- Created unified action plan

### Files Added
- `changelog/SESSION_6_CHANGELOG.md`
- `../SESSION_6_STATUS.md` (project root)
- `../IMAGE_GENERATION_SETUP.md`
- `../START_HERE.md`

### Status
Ready to generate avatar images. All tools confirmed working.

EOF

echo "✅ Parity README updated"

# Create image generation checklist
cat > "$HOME/ai-stack/IMAGE_GENERATION_CHECKLIST.md" << 'EOF'
# 🎨 Image Generation Checklist

## Pre-Generation Setup
- [x] Stable Diffusion WebUI installed
- [x] Prompts prepared
- [x] Output directory planned
- [ ] SD-WebUI running

## FAITHH Avatar Generation
- [ ] Generate variation 1 (seed: random)
- [ ] Generate variation 2 (seed: random)
- [ ] Generate variation 3 (seed: random)
- [ ] Generate variation 4 (seed: random)
- [ ] Generate variation 5 (seed: random)
- [ ] Generate variation 6 (seed: random)
- [ ] Generate variation 7 (seed: random)
- [ ] Generate variation 8 (seed: random)
- [ ] Generate variation 9 (seed: random)
- [ ] Generate variation 10 (seed: random)
- [ ] Select best 2 versions

## PULSE Avatar Generation
- [ ] Generate variation 1 (seed: random)
- [ ] Generate variation 2 (seed: random)
- [ ] Generate variation 3 (seed: random)
- [ ] Generate variation 4 (seed: random)
- [ ] Generate variation 5 (seed: random)
- [ ] Generate variation 6 (seed: random)
- [ ] Generate variation 7 (seed: random)
- [ ] Generate variation 8 (seed: random)
- [ ] Generate variation 9 (seed: random)
- [ ] Generate variation 10 (seed: random)
- [ ] Select best 2 versions

## Post-Generation
- [ ] Created ~/ai-stack/images/faithh_v2/avatars/ directory
- [ ] Copied FAITHH_best.png → faithh_small.png
- [ ] Copied PULSE_best.png → pulse_small.png
- [ ] Resized if needed (target: 128x128)
- [ ] Updated parity files
- [ ] Documented selections

## Integration Test
- [ ] Updated v3 UI to use new images
- [ ] Tested in browser
- [ ] Verified animations work
- [ ] Committed to git

## Notes
Record which seeds/variations worked best:
- FAITHH winner: Seed ___ (reason: ___)
- PULSE winner: Seed ___ (reason: ___)

---
**Time Started:** ___
**Time Completed:** ___
**Total Time:** ___
EOF

echo "✅ Image generation checklist created"

echo ""
echo "📊 Summary of Updates:"
echo "  ✅ SESSION_6_CHANGELOG.md updated"
echo "  ✅ SESSION_6_STATUS.md created"
echo "  ✅ Parity README updated"
echo "  ✅ IMAGE_GENERATION_CHECKLIST.md created"
echo ""
echo "🎯 Next Step: Generate images!"
echo "   cd ~/stable-diffusion-webui && ./webui.sh --listen"
