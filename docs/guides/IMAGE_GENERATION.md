# Stable Diffusion — Getting Started Guide for FAITHH

## What You Have
- **RTX 3090 (24GB VRAM)** — more than enough for SD XL and training LoRAs
- **WSL2 / Linux** — native CUDA support
- GPU 1 (`CUDA_VISIBLE_DEVICES=1`) is the 3090

## Quick Setup: ComfyUI (Recommended)

ComfyUI is a node-based UI for Stable Diffusion — powerful, flexible, and lighter than
Automatic1111. It's the modern standard for SD workflows.

### Install
```bash
# Set GPU
export CUDA_VISIBLE_DEVICES=1

# Clone ComfyUI
cd ~/
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI

# Create venv (keep separate from FAITHH)
python3 -m venv venv
source venv/bin/activate

# Install PyTorch for CUDA 12.x (matches your setup)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128

# Install ComfyUI requirements
pip install -r requirements.txt

# Download a base model (SDXL recommended for quality)
mkdir -p models/checkpoints
cd models/checkpoints

# SDXL 1.0 base (~6.5GB)
wget https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors

# Or SD 1.5 (smaller, faster, more LoRAs available, ~4GB)
# wget https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned.safetensors

cd ~/ComfyUI
```

### Run
```bash
export CUDA_VISIBLE_DEVICES=1
cd ~/ComfyUI
source venv/bin/activate
python main.py --listen 0.0.0.0 --port 8188
```
Then open `http://localhost:8188` in your browser.

### First Generation
1. ComfyUI opens with a default workflow
2. Click "Queue Prompt" to generate an image
3. Modify the text prompt node to try your own prompts

## Alternative: Automatic1111 (A1111)

More traditional UI, easier for beginners but heavier.

```bash
export CUDA_VISIBLE_DEVICES=1
cd ~/
git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui.git
cd stable-diffusion-webui

# It auto-installs everything on first run
./webui.sh --listen --port 7860
```

## Key Concepts

### Models (Checkpoints)
- **SDXL 1.0** — best quality, needs ~8GB VRAM (you have 24GB, no problem)
- **SD 1.5** — faster, huge ecosystem of LoRAs and fine-tunes
- **Flux** — newest generation, excellent quality
- Place `.safetensors` files in `models/checkpoints/`

### LoRA (Low-Rank Adaptation)
- Small model add-ons that teach a specific style without full retraining
- For MMBN chip art, you'd either find or train a pixel-art / game-art LoRA
- Place in `models/loras/`
- Useful LoRAs to search for on CivitAI (https://civitai.com):
  - "pixel art" style LoRAs
  - "game icon" or "game UI" LoRAs
  - "megaman" or "retro game" LoRAs

### Prompting Tips
- Be specific: describe the subject, style, colors, composition
- Use negative prompts: "blurry, low quality, text, watermark"
- For consistent style across chips, use the same seed + similar prompt structure
- Prompt weighting: `(important detail:1.3)` increases emphasis

## Training Your Own LoRA

This is how you'd create a consistent MMBN battle chip art style:

### 1. Gather Reference Images (10-30 images)
```bash
mkdir -p ~/sd-training/mmbn-chips/
# Save 15-30 MMBN battle chip artwork images here
# Include: game sprites, official art, fan art in the style
```

### 2. Prepare Dataset
Each image needs a text caption describing it:
```
mmbn-chips/
├── image_001.png
├── image_001.txt    # "mmbn battle chip icon, digital artwork, green screen..."
├── image_002.png
├── image_002.txt
└── ...
```

### 3. Train with Kohya_ss (GUI tool)
```bash
cd ~/
git clone https://github.com/bmaltais/kohya_ss.git
cd kohya_ss
./setup.sh

# Launch GUI
./gui.sh --listen 0.0.0.0 --port 7861
```

### Training Settings (for RTX 3090)
- **Method**: LoRA (not full fine-tune)
- **Base model**: SDXL or SD 1.5
- **Resolution**: 512x512 (SD 1.5) or 1024x1024 (SDXL)
- **Training steps**: 1000-3000 (for 15-30 images)
- **Learning rate**: 1e-4
- **Network rank**: 32 (balance of quality vs file size)
- **Batch size**: 1-2 (with 24GB VRAM you can do 2)
- **Output**: a `.safetensors` LoRA file (~50-150MB)

### 4. Use Your LoRA
Place the output `.safetensors` in ComfyUI's `models/loras/` folder.
In your workflow, add a "Load LoRA" node between the checkpoint and the sampler.
Set strength to 0.6-0.8 for best results.

## Workflow for FAITHH Chip Art

### Step 1: Generate base chip icons
```
Prompt: "mmbn battle chip icon, [SUBJECT], digital game art,
         pixel art style, flat colors, dark background, 
         clean vector, game UI asset"

Negative: "blurry, low quality, text, watermark, 3d render,
           photograph, realistic"

Settings: 512x512, 30 steps, CFG 7.5, DPM++ 2M Karras
```

### Step 2: Batch generate all 15 chips
Use ComfyUI's batch mode or a simple script to generate with different subjects.

### Step 3: Post-process
- Remove backgrounds (transparent PNG)
- Resize to consistent dimensions
- Save to `/home/jonat/ai-stack/images/chips/chip_0.png` through `chip_14.png`

### Step 4: Auto-display in FAITHH
The `renderMlChips()` function already tries to load images from `/images/chips/`.
Once the files exist, they'll appear inside the chip screen windows automatically.

## Resources
- [ComfyUI GitHub](https://github.com/comfyanonymous/ComfyUI)
- [CivitAI](https://civitai.com) — models, LoRAs, prompts
- [Kohya_ss](https://github.com/bmaltais/kohya_ss) — LoRA training GUI
- [Stable Diffusion Subreddit](https://reddit.com/r/StableDiffusion)
- [ComfyUI Examples](https://comfyanonymous.github.io/ComfyUI_examples/)

## Important Notes
- Always set `CUDA_VISIBLE_DEVICES=1` before running SD tools (your 3090 is GPU 1)
- Keep SD in its own venv, separate from FAITHH's backend
- ComfyUI uses ~4-8GB VRAM per generation with SDXL
- You can run ComfyUI + Ollama simultaneously on the 3090 (24GB is plenty)
