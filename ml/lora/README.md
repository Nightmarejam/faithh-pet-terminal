# FAITHH LoRA Training — Pixel Art Battle Chips

Train a custom LoRA on SD 1.5 for consistent MMBN-style battle chip pixel art.

## Quick Start

### Option A: Download Pre-Made Pixel Art LoRA (fastest)

1. Go to [CivitAI](https://civitai.com) and search for "pixel art" or "MMBN" LoRAs
2. Download a `.safetensors` file
3. Place it in `~/ComfyUI/models/loras/`
4. Use it in ComfyUI with `<lora:filename:0.7>` in your prompt

### Option B: Train Your Own LoRA (custom style)

#### 1. Collect Training Images (20-50 images)

Good sources for MMBN-style battle chip references:
- Screenshots of actual MMBN battle chips from the games
- Pixel art icons from sprite databases (spriters-resource.com)
- The existing generated chips in `images/chips/` (if you like the current style)

**Image requirements:**
- PNG or JPG format
- Square or near-square aspect ratio preferred
- At least 512x512 pixels (will be resized)
- Consistent style across all images

#### 2. Place Images in Training Directory

```bash
# Put your images here:
cp your_images/*.png ~/ai-stack/ml/lora/training_data/
```

#### 3. (Optional) Add Captions

For each image, create a `.txt` file with the same name:
```
training_data/
  chip_01.png
  chip_01.txt  → "pixel art battle chip icon, MMBN style, fire element, metallic body"
  chip_02.png
  chip_02.txt  → "pixel art battle chip icon, MMBN style, water element, blue glow"
```

If you skip captions, the script auto-generates a generic one.

#### 4. Run Training

```bash
cd ~/ai-stack
CUDA_VISIBLE_DEVICES=0 ml/lora_venv/bin/python ml/lora/train_pixel_art_lora.py
```

Training takes ~20-40 minutes on RTX 3090 (1000 steps).

#### 5. Use in ComfyUI

The trained LoRA is automatically copied to `~/ComfyUI/models/loras/`.
In your ComfyUI prompt, add: `<lora:faithh_pixel_art:0.7>`

## Directory Structure

```
ml/lora/
├── training_data/     # Put training images + captions here
├── output/            # Trained LoRA checkpoints
├── configs/           # Training config overrides
├── train_pixel_art_lora.py  # Training script
└── README.md          # This file
```

## Tuning Tips

- **More images = better**: 20 minimum, 50+ ideal
- **Consistent style**: All training images should share the same art style
- **LoRA strength**: Start at 0.7, adjust 0.5-1.0 in ComfyUI
- **Training steps**: 1000 is a good default, increase to 2000 for more complex styles
- **Learning rate**: 1e-4 default, try 5e-5 if results are unstable

## GPU Requirements

| GPU | VRAM | Training Time |
|-----|------|---------------|
| RTX 3090 | 24GB | ~20-40 min |
| RTX 3080 | 10GB | ~30-60 min (reduce batch) |
| GTX 1080 Ti | 11GB | Not recommended |
