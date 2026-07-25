# 🎨 FAITHH Image Generation Setup Guide
**Created:** November 9, 2025
**Status:** Ready to Use - ComfyUI & Stable Diffusion WebUI Already Installed!

---

## ✅ What You Already Have

**GREAT NEWS:** I found both image generation tools already installed!

```
~/ComfyUI/                      ✅ Installed (Oct 22, 2025)
~/stable-diffusion-webui/       ✅ Installed (Oct 21, 2025)
```

**You DON'T need to:**
- ❌ Install ComfyUI from scratch
- ❌ Install Stable Diffusion WebUI
- ❌ Copy/move folders to ai-stack (not needed!)

**You DO need to:**
- ✅ Create symlinks for easy access
- ✅ Generate FAITHH and PULSE avatars
- ✅ Copy generated images to `~/ai-stack/images/`

---

## 🚀 Quick Start (5 Minutes to First Image!)

### Option 1: Stable Diffusion WebUI (Recommended for Beginners)

**Why:** Easier UI, faster setup, great for quick iterations

```bash
# 1. Navigate to Stable Diffusion WebUI
cd ~/stable-diffusion-webui

# 2. Start the web interface
./webui.sh --listen --api

# 3. Open in browser
# http://localhost:7860
```

**Expected Output:**
```
Running on local URL:  http://127.0.0.1:7860
To create a public link, set `share=True` in `launch()`.
```

---

### Option 2: ComfyUI (Advanced, More Control)

**Why:** More powerful, workflow-based, better for automation

```bash
# 1. Navigate to ComfyUI
cd ~/ComfyUI

# 2. Activate virtual environment (if you have one)
source venv/bin/activate  # Skip if no venv

# 3. Start ComfyUI
python main.py --listen --port 8188

# 4. Open in browser
# http://localhost:8188
```

---

## 📸 Generating FAITHH Avatars

### Using Stable Diffusion WebUI

#### Step 1: Start the WebUI
```bash
cd ~/stable-diffusion-webui
./webui.sh --listen
```

#### Step 2: Open Browser
Navigate to: `http://localhost:7860`

#### Step 3: Generate FAITHH Small Avatar

**Prompt to use:**
```
cute AI assistant chibi character, friendly robot mascot,
cyan glowing accents, tech-inspired design, MegaMan Battle Network style,
digital avatar, professional but approachable, clean background,
minimalist geometric shapes, holographic effect, kawaii aesthetic

Negative prompt: realistic, photo, human, blurry, low quality
```

**Settings:**
- Width: 512
- Height: 512
- Steps: 30
- CFG Scale: 7
- Sampler: Euler a
- Seed: -1 (random)

**Click "Generate" → Wait 30-60 seconds**

#### Step 4: Generate PULSE System Monitor Avatar

**Prompt to use:**
```
technical system monitoring AI icon, robotic face with blue theme,
hexagonal design, circuit board patterns, health monitoring motifs,
geometric minimalist style, serious analytical character,
tech readout aesthetic, MegaMan Battle Network inspired,
clean professional design

Negative prompt: realistic, photo, organic, blurry, complex background
```

**Same settings as above, click "Generate"**

#### Step 5: Save Generated Images

**In WebUI:**
1. Right-click generated image → "Save image as..."
2. Save to: `~/ai-stack/images/faithh_generated_1.png`
3. Generate 5-10 variations (click "Generate" multiple times)
4. Pick the best 2

---

## 📁 Organizing Generated Images

### Recommended Folder Structure

```bash
# Create image folders
mkdir -p ~/ai-stack/images/avatars/faithh
mkdir -p ~/ai-stack/images/avatars/pulse
mkdir -p ~/ai-stack/images/raw_generations

# Move generated images
mv ~/stable-diffusion-webui/outputs/*.png ~/ai-stack/images/raw_generations/

# Copy best versions
cp ~/ai-stack/images/raw_generations/best_faithh.png \
   ~/ai-stack/images/avatars/faithh/faithh_small.png

cp ~/ai-stack/images/raw_generations/best_pulse.png \
   ~/ai-stack/images/avatars/pulse/pulse_small.png
```

---

## �� Ready-to-Use Prompts for FAITHH Project

### FAITHH Avatar Variations

#### 1. Chibi Style (Cute & Friendly)
```
Positive: cute chibi AI assistant, friendly robot character,
big expressive eyes, cyan and blue color scheme, tech accessories,
MegaMan Battle Network PET aesthetic, kawaii style, clean simple design,
helpful supportive expression, holographic elements

Negative: realistic, human, photo, blurry, complex background, dark, scary
```

#### 2. Minimalist Icon Style
```
Positive: minimalist AI assistant icon, simple geometric shapes,
cyan glowing circles and triangles, clean tech logo design,
flat design, modern professional aesthetic, transparent background,
single character design, friendly abstract form

Negative: detailed, realistic, photo, 3d render, messy, busy composition
```

#### 3. Holographic Tech Style
```
Positive: holographic AI entity, glowing cyan wireframe character,
digital ghost, tech interface aesthetic, floating particles,
futuristic design, transparent glowing form, friendly AI presence,
MegaMan Battle Network cyberspace style

Negative: solid, realistic, physical form, photo, dark, scary
```

---

### PULSE Avatar Variations

#### 1. Technical Monitor Style
```
Positive: technical system monitor AI icon, blue themed robot face,
hexagonal frame, circuit patterns, health monitoring display,
geometric design, professional analytical look, blue neon glow,
serious utility-focused character, tech readout interface

Negative: cute, friendly, organic, realistic, photo, blurry
```

#### 2. Abstract Data Visualization
```
Positive: abstract system health visualization, geometric blue shapes,
data flow patterns, monitoring interface design, hexagonal grid,
technical dashboard aesthetic, clean professional design,
blue and cyan color scheme, minimalist tech art

Negative: character, face, realistic, photo, organic shapes, messy
```

#### 3. Radial Interface Design
```
Positive: circular monitoring interface, radial tech display,
blue holographic UI, system status visualization, geometric patterns,
futuristic command center aesthetic, glowing blue accents,
professional monitoring dashboard design

Negative: character based, realistic, photo, organic, cluttered
```

---

## 🔧 Troubleshooting

### Stable Diffusion WebUI Won't Start

**Error:** `No module named 'torch'`
```bash
cd ~/stable-diffusion-webui
pip install torch torchvision torchaudio
./webui.sh
```

**Error:** `CUDA not available`
```bash
# Use CPU mode (slower but works)
./webui.sh --skip-torch-cuda-test --precision full --no-half
```

---

### ComfyUI Won't Start

**Error:** `Missing models`
```bash
cd ~/ComfyUI/models/checkpoints
# Download a model if folder is empty
wget https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned-emaonly.safetensors
```

**Error:** `Port already in use`
```bash
# Use different port
python main.py --listen --port 8189
```

---

### Images Are Low Quality

**Solution 1:** Increase steps
- Change from 30 → 50 steps

**Solution 2:** Adjust CFG Scale
- Try CFG 5-12 (7 is default)

**Solution 3:** Try different sampler
- Euler a (fast, good quality)
- DPM++ 2M Karras (high quality, slower)

**Solution 4:** Use larger size
- 512x512 → 768x768 (slower but better)

---

## 🎨 Workflow: From Generation to Integration

### Phase 1: Mass Generation (60 min)
```bash
# Start WebUI
cd ~/stable-diffusion-webui
./webui.sh --listen

# Generate 20 FAITHH variations
# - Use prompts above
# - Change seed each time (-1 for random)
# - Try different styles (chibi, minimalist, holographic)

# Generate 20 PULSE variations
# - Use technical prompts
# - Vary between icon, abstract, interface styles
```

---

### Phase 2: Selection (15 min)
```bash
# Review all generated images
cd ~/stable-diffusion-webui/outputs/txt2img-images
ls -lh

# Use image viewer to pick best 2 of each
# Criteria:
# - Clear at small size (128x128)
# - Fits PET terminal aesthetic
# - Appropriate personality (FAITHH friendly, PULSE technical)
```

---

### Phase 3: Integration (10 min)
```bash
# Copy selected images to project
cp ~/stable-diffusion-webui/outputs/txt2img-images/00042.png \
   ~/ai-stack/images/faithh.png

cp ~/stable-diffusion-webui/outputs/txt2img-images/00067.png \
   ~/ai-stack/images/pulse.png

# Test in browser
cd ~/ai-stack
python -m http.server 8000
# Open http://localhost:8000/faithh_pet_v3.html
# Check if avatars load correctly
```

---

## 📊 Expected Results

### After This Guide You'll Have:

✅ Stable Diffusion WebUI running locally
✅ 20+ FAITHH avatar variations
✅ 20+ PULSE avatar variations
✅ 2 final selected avatars integrated into project
✅ Images properly organized in `~/ai-stack/images/`
✅ Experience with local AI image generation
✅ Foundation for future image generation needs

**Time Investment:** 90 minutes
**Cost:** $0 (all local)
**Value:** Unlimited image generation forever!

---

## 🎯 Next Steps After Image Generation

1. ✅ **Update v3 UI** with new avatars
   - Edit `faithh_pet_v3.html`
   - Replace emoji with `<img src="images/faithh.png">`

2. ✅ **Build v4 UI** with avatar panels
   - Use designs from `V3_VS_V4_ANALYSIS.md`
   - Integrate new avatar images

3. ✅ **Update parity files**
   - Document image generation process
   - Note which prompts worked best
   - Create changelog entry

4. ✅ **Commit to git**
   ```bash
   cd ~/ai-stack
   git add images/
   git commit -m "Add FAITHH and PULSE avatar images"
   ```

---

## 💡 Pro Tips

### For Best Results:

1. **Generate in batches**
   - 10 variations at once
   - Review all before deciding
   - Don't settle for first result

2. **Use negative prompts**
   - Prevent unwanted elements
   - `realistic, photo, blurry, dark` works well

3. **Iterate on winners**
   - Found a good one? Copy its seed
   - Generate 5 more with slight prompt changes

4. **Test at target size**
   - Shrink to 128x128 to test
   - Must look good small!

5. **Keep raw files**
   - Save all generations to `raw_generations/`
   - Never know when you'll want alternates

---

## ✅ Quick Commands Reference

```bash
# Start Stable Diffusion WebUI
cd ~/stable-diffusion-webui && ./webui.sh --listen

# Start ComfyUI
cd ~/ComfyUI && python main.py --listen --port 8188

# Create image folders
mkdir -p ~/ai-stack/images/avatars/{faithh,pulse,raw}

# Copy generated image
cp ~/stable-diffusion-webui/outputs/txt2img-images/XXXXX.png \
   ~/ai-stack/images/faithh.png

# Test in browser
cd ~/ai-stack && python -m http.server 8000
```

---

## 📞 When to Use Each Tool

### Use Stable Diffusion WebUI When:
- ✅ First time generating images
- ✅ Need quick iterations
- ✅ Want simple prompting
- ✅ Generating single images

### Use ComfyUI When:
- ✅ Need automation
- ✅ Want complex workflows
- ✅ Batch processing many images
- ✅ Advanced image manipulation

**For FAITHH Project:** Start with Stable Diffusion WebUI!

---

**Ready to generate!** 🎨🚀

**First command:**
```bash
cd ~/stable-diffusion-webui && ./webui.sh --listen
```

Then open: `http://localhost:7860`

Good luck! You've got this! 💪
