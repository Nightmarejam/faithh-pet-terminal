#!/usr/bin/env python3
"""
FAITHH LoRA Training Script — Pixel Art Battle Chip Style
Trains a LoRA on SD 1.5 for consistent MMBN-style pixel art chip icons.
SDXL LoRA training support planned (requires StableDiffusionXLPipeline).

Usage:
    # From ai-stack root:
    CUDA_VISIBLE_DEVICES=0 ml/lora_venv/bin/python ml/lora/train_pixel_art_lora.py

Prerequisites:
    1. Put 20-50 training images in ml/lora/training_data/
    2. Each image should have a matching .txt caption file
       e.g. image_01.png + image_01.txt
    3. RTX 3090 (24GB VRAM) recommended

Output:
    ml/lora/output/faithh_pixel_art_lora/
    Copy the .safetensors file to ~/ComfyUI/models/loras/
"""

import os
import sys
import json
import shutil
from pathlib import Path

# Paths
SCRIPT_DIR = Path(__file__).parent
TRAINING_DATA = SCRIPT_DIR / "training_data"
OUTPUT_DIR = SCRIPT_DIR / "output" / "faithh_pixel_art_lora"
COMFYUI_LORA_DIR = Path.home() / "ComfyUI" / "models" / "loras"
SD15_CHECKPOINT = Path.home() / "ComfyUI" / "models" / "checkpoints" / "v1-5-pruned-emaonly.safetensors"


def convert_webp_to_png():
    """Auto-convert any WebP files (including .png files that are secretly WebP) to real PNG."""
    from PIL import Image
    converted = 0

    for f in TRAINING_DATA.iterdir():
        if f.suffix.lower() in ('.webp',):
            # Explicit .webp files
            out = f.with_suffix('.png')
            Image.open(f).convert('RGB').save(out, 'PNG')
            f.unlink()
            print(f"  Converted WebP→PNG: {f.name} → {out.name}")
            converted += 1
        elif f.suffix.lower() in ('.png', '.jpg', '.jpeg'):
            # Check if file is secretly WebP (wrong extension)
            try:
                with open(f, 'rb') as fh:
                    header = fh.read(4)
                if header == b'RIFF':
                    out = f.with_stem(f.stem + '_converted') if f.suffix == '.png' else f.with_suffix('.png')
                    Image.open(f).convert('RGB').save(out, 'PNG')
                    if out != f:
                        f.unlink()
                    print(f"  Fixed fake-PNG (was WebP): {f.name}")
                    converted += 1
            except Exception:
                pass

    if converted:
        print(f"  Converted {converted} WebP files to real PNG")
    return converted


def check_prerequisites():
    """Verify training environment is ready."""
    errors = []

    # Check GPU
    try:
        import torch
        if not torch.cuda.is_available():
            errors.append("CUDA not available")
        else:
            gpu_name = torch.cuda.get_device_name(0)
            vram_gb = torch.cuda.get_device_properties(0).total_memory // 1024**3
            print(f"  GPU: {gpu_name} ({vram_gb}GB VRAM)")
            if vram_gb < 12:
                errors.append(f"Need >=12GB VRAM, have {vram_gb}GB")
    except ImportError:
        errors.append("PyTorch not installed")

    # Check SD checkpoint
    if not SD15_CHECKPOINT.exists():
        errors.append(f"SD 1.5 checkpoint not found: {SD15_CHECKPOINT}")

    # Check training data
    images = list(TRAINING_DATA.glob("*.png")) + list(TRAINING_DATA.glob("*.jpg"))
    if len(images) < 5:
        errors.append(
            f"Need at least 5 training images in {TRAINING_DATA}, found {len(images)}.\n"
            f"  See ml/lora/README.md for how to prepare training data."
        )
    else:
        # Check for captions
        captioned = sum(1 for img in images if img.with_suffix('.txt').exists())
        print(f"  Training images: {len(images)} ({captioned} captioned)")
        if captioned < len(images):
            print(f"  ⚠️  {len(images) - captioned} images missing .txt captions — will auto-caption")

    # Check libraries
    try:
        import diffusers
        import accelerate
        import peft
        print(f"  diffusers={diffusers.__version__}, accelerate={accelerate.__version__}")
    except ImportError as e:
        errors.append(f"Missing library: {e}")

    return errors


def auto_caption_images():
    """Generate simple captions for images that don't have .txt files."""
    images = list(TRAINING_DATA.glob("*.png")) + list(TRAINING_DATA.glob("*.jpg"))
    default_caption = (
        "pixel art battle chip icon, MMBN megaman battle network style, "
        "retro game item, clean pixel edges, metallic chip body, "
        "glowing screen element, dark background"
    )
    for img in images:
        caption_file = img.with_suffix('.txt')
        if not caption_file.exists():
            caption_file.write_text(default_caption)
            print(f"  Auto-captioned: {img.name}")


def train():
    """Run LoRA training using diffusers."""
    import torch
    from diffusers import StableDiffusionPipeline, DDPMScheduler
    from diffusers.loaders import StableDiffusionLoraLoaderMixin
    from peft import LoraConfig
    from accelerate import Accelerator
    from torch.utils.data import Dataset, DataLoader
    from torchvision import transforms
    from PIL import Image
    from transformers import CLIPTokenizer

    # --- Config ---
    LEARNING_RATE = 1e-4
    TRAIN_STEPS = 1000
    BATCH_SIZE = 1
    GRADIENT_ACCUMULATION = 4
    LORA_RANK = 16
    RESOLUTION = 512
    SAVE_EVERY = 250

    print(f"\n{'='*50}")
    print(f"  LoRA Training Config")
    print(f"  Steps: {TRAIN_STEPS}")
    print(f"  LR: {LEARNING_RATE}")
    print(f"  Rank: {LORA_RANK}")
    print(f"  Resolution: {RESOLUTION}")
    print(f"  Batch: {BATCH_SIZE} x {GRADIENT_ACCUMULATION} accum")
    print(f"{'='*50}\n")

    # --- Load model ---
    print("Loading SD 1.5 pipeline...")
    pipe = StableDiffusionPipeline.from_single_file(
        str(SD15_CHECKPOINT),
        torch_dtype=torch.float16,
        safety_checker=None,
    )
    pipe.scheduler = DDPMScheduler.from_config(pipe.scheduler.config)

    tokenizer = pipe.tokenizer
    text_encoder = pipe.text_encoder
    vae = pipe.vae
    unet = pipe.unet

    # Freeze everything except LoRA
    vae.requires_grad_(False)
    text_encoder.requires_grad_(False)
    unet.requires_grad_(False)

    # --- Add LoRA to UNet ---
    lora_config = LoraConfig(
        r=LORA_RANK,
        lora_alpha=LORA_RANK,
        target_modules=["to_k", "to_q", "to_v", "to_out.0"],
        lora_dropout=0.05,
    )
    unet.add_adapter(lora_config)
    unet.train()

    # Move to GPU
    device = torch.device("cuda")
    vae.to(device, dtype=torch.float16)
    text_encoder.to(device, dtype=torch.float16)
    unet.to(device, dtype=torch.float32)  # LoRA layers need float32

    # --- Dataset ---
    class ChipArtDataset(Dataset):
        def __init__(self, data_dir, tokenizer, resolution):
            self.images = sorted(
                list(Path(data_dir).glob("*.png")) +
                list(Path(data_dir).glob("*.jpg"))
            )
            self.tokenizer = tokenizer
            self.transform = transforms.Compose([
                transforms.Resize(resolution, interpolation=transforms.InterpolationMode.BILINEAR),
                transforms.CenterCrop(resolution),
                transforms.ToTensor(),
                transforms.Normalize([0.5], [0.5]),
            ])

        def __len__(self):
            return len(self.images)

        def __getitem__(self, idx):
            img_path = self.images[idx % len(self.images)]
            image = Image.open(img_path).convert("RGB")
            image = self.transform(image)

            caption_path = img_path.with_suffix('.txt')
            caption = caption_path.read_text().strip() if caption_path.exists() else "pixel art battle chip"

            tokens = self.tokenizer(
                caption,
                max_length=self.tokenizer.model_max_length,
                padding="max_length",
                truncation=True,
                return_tensors="pt",
            )

            return {"pixel_values": image, "input_ids": tokens.input_ids.squeeze()}

    dataset = ChipArtDataset(TRAINING_DATA, tokenizer, RESOLUTION)
    dataloader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=0)
    print(f"Dataset: {len(dataset)} images")

    # --- Optimizer ---
    lora_params = [p for p in unet.parameters() if p.requires_grad]
    optimizer = torch.optim.AdamW(lora_params, lr=LEARNING_RATE, weight_decay=1e-2)
    noise_scheduler = DDPMScheduler.from_config(pipe.scheduler.config)

    # --- Training Loop ---
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    global_step = 0
    epoch = 0

    print(f"\nStarting training for {TRAIN_STEPS} steps...")
    while global_step < TRAIN_STEPS:
        epoch += 1
        for batch in dataloader:
            if global_step >= TRAIN_STEPS:
                break

            pixel_values = batch["pixel_values"].to(device, dtype=torch.float16)
            input_ids = batch["input_ids"].to(device)

            # Encode image to latents
            with torch.no_grad():
                latents = vae.encode(pixel_values).latent_dist.sample() * vae.config.scaling_factor

            # Sample noise
            noise = torch.randn_like(latents)
            timesteps = torch.randint(0, noise_scheduler.config.num_train_timesteps, (BATCH_SIZE,), device=device).long()
            noisy_latents = noise_scheduler.add_noise(latents, noise, timesteps)

            # Get text embeddings
            with torch.no_grad():
                encoder_hidden_states = text_encoder(input_ids)[0].to(dtype=torch.float32)

            # Predict noise
            model_pred = unet(noisy_latents.float(), timesteps, encoder_hidden_states).sample

            # Loss
            loss = torch.nn.functional.mse_loss(model_pred.float(), noise.float(), reduction="mean")

            loss.backward()

            if (global_step + 1) % GRADIENT_ACCUMULATION == 0:
                torch.nn.utils.clip_grad_norm_(lora_params, 1.0)
                optimizer.step()
                optimizer.zero_grad()

            global_step += 1

            if global_step % 50 == 0:
                print(f"  Step {global_step}/{TRAIN_STEPS} | Loss: {loss.item():.4f} | Epoch: {epoch}")

            if global_step % SAVE_EVERY == 0:
                checkpoint_dir = OUTPUT_DIR / f"checkpoint-{global_step}"
                checkpoint_dir.mkdir(exist_ok=True)
                unet.save_attn_procs(str(checkpoint_dir))
                print(f"  💾 Saved checkpoint: {checkpoint_dir.name}")

    # --- Save final LoRA ---
    final_path = OUTPUT_DIR / "faithh_pixel_art.safetensors"
    unet.save_attn_procs(str(OUTPUT_DIR))
    print(f"\n✅ Training complete!")
    print(f"   LoRA saved to: {OUTPUT_DIR}")

    # Copy to ComfyUI
    lora_files = list(OUTPUT_DIR.glob("*.safetensors"))
    if lora_files and COMFYUI_LORA_DIR.exists():
        dest = COMFYUI_LORA_DIR / "faithh_pixel_art.safetensors"
        shutil.copy2(lora_files[0], dest)
        print(f"   Copied to ComfyUI: {dest}")


if __name__ == "__main__":
    print("=" * 50)
    print("  FAITHH LoRA Training — Pixel Art Battle Chips")
    print("=" * 50)
    print()

    print("Converting WebP files (if any)...")
    convert_webp_to_png()

    print("Checking prerequisites...")
    errors = check_prerequisites()

    if errors:
        print(f"\n❌ Cannot start training:")
        for err in errors:
            print(f"   - {err}")
        print(f"\nSee ml/lora/README.md for setup instructions.")
        sys.exit(1)

    # Auto-caption uncaptioned images
    auto_caption_images()

    # Train
    train()
