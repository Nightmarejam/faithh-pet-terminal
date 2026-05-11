# ⚡ Ultra Quick Start: Get Generating Images in 15 Minutes

**Goal:** Generate FAITHH and PULSE avatars ASAP

---

## 🚀 Copy-Paste Command Sequence

Run these commands in order. Don't think, just execute:

```bash
# 1. Navigate to your project (30 seconds)
cd ~/ai-stack
mkdir -p image-generation
cd image-generation

# 2. Clone ComfyUI (2 minutes)
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI

# 3. Install dependencies (5 minutes)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt

# 4. Download SD 1.5 model (5 minutes - 4GB download)
cd models/checkpoints
wget https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned-emaonly.safetensors
cd ../..

# 5. Start ComfyUI (immediate)
python main.py
```

**Stop here and open browser!**

---

## 🎨 Generate Your First Avatar (3 minutes)

1. Open browser: http://127.0.0.1:8188

2. You'll see a node interface. Find the text box that says:
   ```
   "beautiful scenery nature glass bottle landscape..."
   ```

3. Replace with:
   ```
   cute AI assistant avatar, friendly expression, 
   cyan glowing highlights, MegaMan Battle Network style, 
   chibi robot character, digital holographic design
   ```

4. Click **"Queue Prompt"** button (top right)

5. Wait 30-60 seconds

6. **Image appears!** 🎉

7. Right-click image → Save as: `faithh_test_01.png`

---

## 🔷 Generate PULSE Avatar (2 minutes)

1. Change prompt to:
   ```
   technical system monitor avatar, hexagonal design, 
   blue neon highlights, analytical robot face, 
   MegaMan Battle Network style, monitoring icon
   ```

2. Click **"Queue Prompt"**

3. Wait 30-60 seconds

4. Save as: `pulse_test_01.png`

---

## 📦 Where Are My Images?

```bash
# View generated images
cd ~/ai-stack/image-generation/ComfyUI/output
ls -lh

# Open folder in Windows Explorer
explorer.exe ~/ai-stack/image-generation/ComfyUI/output
```

---

## 🎯 Generate 10 Variations Each (10 minutes)

For FAITHH:
1. Type prompt (from above)
2. Click "Queue Prompt"
3. Change seed (random button or type new number)
4. Repeat 10 times

For PULSE:
1. Change to PULSE prompt
2. Click "Queue Prompt"
3. Change seed
4. Repeat 10 times

**Pick your favorites!**

---

## 🏆 Move Best Images to FAITHH

```bash
# Create image folders
mkdir -p ~/ai-stack/images/faithh_v2/avatars

# Copy your best FAITHH image
cp ~/ai-stack/image-generation/ComfyUI/output/ComfyUI_00005.png \
   ~/ai-stack/images/faithh_v2/avatars/faithh_small.png

# Copy your best PULSE image
cp ~/ai-stack/image-generation/ComfyUI/output/ComfyUI_00012.png \
   ~/ai-stack/images/faithh_v2/avatars/pulse_small.png
```

---

## ✅ Success! You Now Have:

- ✅ Local image generation working
- ✅ FAITHH avatar image
- ✅ PULSE avatar image  
- ✅ Ability to generate unlimited variations
- ✅ No API costs, no rate limits

**Total time:** 15-20 minutes

---

## 🔧 If Something Goes Wrong

### Can't install torch:
```bash
# Try pip3 instead
pip3 install torch torchvision torchaudio
```

### Download is slow:
```bash
# Use smaller model (1.4GB instead of 4GB)
cd ~/ai-stack/image-generation/ComfyUI/models/checkpoints
wget https://huggingface.co/CompVis/stable-diffusion-v1-4/resolve/main/sd-v1-4.ckpt
```

### ComfyUI won't start:
```bash
# Check Python version
python3 --version  # Need 3.10 or higher

# If too old, use conda or pyenv to get newer Python
```

### Images look bad:
- Generate 20+ variations
- Adjust prompt: add "high quality, detailed, professional"
- Increase steps: find "steps: 20" node, change to 30

---

## 🚀 Next: Automate It

After you get it working manually, check:
- `LOCAL_IMAGE_GENERATION_SETUP.md` for the Python automation script
- Full ComfyUI guide for advanced features

---

**Stop reading. Start generating! 🎨**

Run those 5 commands and you'll be making images in 15 minutes.
