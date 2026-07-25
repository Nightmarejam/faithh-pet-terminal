#!/usr/bin/env python3
"""
Batch generate MMBN battle chip screen icons using ComfyUI API.
Supports SD 1.5 (512x512) and SDXL (1024x1024), with optional LoRA.
Output: /home/jonat/ai-stack/images/chips/

Usage:
    python scripts/generate_chip_art.py              # SD 1.5 (default)
    python scripts/generate_chip_art.py --sdxl        # SDXL (higher quality)
    python scripts/generate_chip_art.py --sdxl --lora  # SDXL + FAITHH pixel art LoRA
    python scripts/generate_chip_art.py --sdxl --seed 123
"""

import argparse
import json
import urllib.request
import urllib.error
import time
import os
import sys
import shutil

COMFYUI_URL = "http://localhost:8188"
OUTPUT_DIR = "/home/jonat/ai-stack/images/chips"
COMFYUI_OUTPUT = os.path.expanduser("~/ComfyUI/output")

# Model configs
MODELS = {
    "sd15": {
        "checkpoint": "v1-5-pruned-emaonly.safetensors",
        "width": 512,
        "height": 512,
        "steps": 30,
        "cfg": 7.5,
        "sampler": "dpmpp_2m",
        "scheduler": "karras",
    },
    "sdxl": {
        "checkpoint": "sd_xl_base_1.0.safetensors",
        "width": 1024,
        "height": 1024,
        "steps": 35,
        "cfg": 7.0,
        "sampler": "dpmpp_2m_sde",
        "scheduler": "karras",
    },
}

BASE_STYLE = (
    "MegaMan Battle Network battle chip screen icon, flat 2D game sprite style, "
    "pixel-art influenced, clean sharp edges, vibrant subject on gradient background, "
    "game UI asset, centered composition, no text, Rockman EXE style, Capcom GBA era aesthetic"
)

NEGATIVE = (
    "blurry, low quality, text, watermark, 3d render, photograph, realistic, "
    "deformed, ugly, disfigured, noisy, grainy, oversaturated, underexposed, "
    "multiple subjects, border, frame, signature, logo, words, letters"
)

CHIPS = [
    {"id": "chip_0",  "subject": "glowing neural network brain with electric blue data streams and circuits"},
    {"id": "chip_1",  "subject": "server rack with glowing gears and cloud nodes connected by orange data pipes"},
    {"id": "chip_2",  "subject": "sound wave oscilloscope with neon green audio waveform and headphones"},
    {"id": "chip_3",  "subject": "digital shield with lock icon surrounded by red firewall grid lines"},
    {"id": "chip_4",  "subject": "globe connected to API endpoints with cyan data flow arrows and JSON brackets"},
    {"id": "chip_5",  "subject": "blueprint system diagram with microchip processor and teal schematic lines"},
    {"id": "chip_6",  "subject": "3D bar chart with scatter plot dots and purple data visualization glow"},
    {"id": "chip_7",  "subject": "person climbing mountain of books with warm sunrise gradient and star at peak"},
    {"id": "chip_8",  "subject": "chat bubble with brain neurons forming glowing green text on terminal screen"},
    {"id": "chip_9",  "subject": "chess king piece on strategy board with gold dollar signs and growth arrows"},
    {"id": "chip_10", "subject": "paint palette with digital pen and pixel art canvas with rainbow splash"},
    {"id": "chip_11", "subject": "circuit board with sensor nodes and robotic arm with copper PCB traces"},
    {"id": "chip_12", "subject": "game controller with VR headset and pixel character in neon arcade glow"},
    {"id": "chip_13", "subject": "network of connected avatars with handshake icon in warm blue glow"},
    {"id": "chip_14", "subject": "robotic arm with conveyor belt of gears in industrial orange and steel"},
]


def build_workflow(prompt_text: str, negative_text: str, seed: int,
                   model_key: str = "sd15", lora_name: str = None, lora_strength: float = 0.8) -> dict:
    """Build a ComfyUI API workflow for txt2img, optionally with LoRA."""
    cfg = MODELS[model_key]

    # Model source: checkpoint loader or checkpoint+LoRA
    model_ref = ["4", 0]
    clip_ref = ["4", 1]
    if lora_name:
        model_ref = ["10", 0]
        clip_ref = ["10", 1]

    workflow = {
        "3": {
            "class_type": "KSampler",
            "inputs": {
                "seed": seed,
                "steps": cfg["steps"],
                "cfg": cfg["cfg"],
                "sampler_name": cfg["sampler"],
                "scheduler": cfg["scheduler"],
                "denoise": 1.0,
                "model": model_ref,
                "positive": ["6", 0],
                "negative": ["7", 0],
                "latent_image": ["5", 0]
            }
        },
        "4": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {
                "ckpt_name": cfg["checkpoint"]
            }
        },
        "5": {
            "class_type": "EmptyLatentImage",
            "inputs": {
                "width": cfg["width"],
                "height": cfg["height"],
                "batch_size": 1
            }
        },
        "6": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": prompt_text,
                "clip": clip_ref
            }
        },
        "7": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": negative_text,
                "clip": clip_ref
            }
        },
        "8": {
            "class_type": "VAEDecode",
            "inputs": {
                "samples": ["3", 0],
                "vae": ["4", 2]
            }
        },
        "9": {
            "class_type": "SaveImage",
            "inputs": {
                "filename_prefix": "faithh_chip",
                "images": ["8", 0]
            }
        }
    }

    if lora_name:
        workflow["10"] = {
            "class_type": "LoraLoader",
            "inputs": {
                "lora_name": lora_name,
                "strength_model": lora_strength,
                "strength_clip": lora_strength,
                "model": ["4", 0],
                "clip": ["4", 1]
            }
        }

    return workflow


def queue_prompt(workflow: dict) -> str:
    """Submit a workflow to ComfyUI and return the prompt_id."""
    data = json.dumps({"prompt": workflow}).encode("utf-8")
    req = urllib.request.Request(
        f"{COMFYUI_URL}/prompt",
        data=data,
        headers={"Content-Type": "application/json"}
    )
    try:
        resp = urllib.request.urlopen(req)
        result = json.loads(resp.read())
        return result.get("prompt_id", "")
    except urllib.error.URLError as e:
        print(f"  ERROR queuing prompt: {e}")
        return ""


def wait_for_completion(prompt_id: str, timeout: int = 120) -> bool:
    """Poll ComfyUI history until the prompt is done."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            resp = urllib.request.urlopen(f"{COMFYUI_URL}/history/{prompt_id}")
            history = json.loads(resp.read())
            if prompt_id in history:
                outputs = history[prompt_id].get("outputs", {})
                if outputs:
                    return True
        except:
            pass
        time.sleep(2)
    return False


def get_latest_output(prompt_id: str) -> str:
    """Get the filename of the generated image from history."""
    try:
        resp = urllib.request.urlopen(f"{COMFYUI_URL}/history/{prompt_id}")
        history = json.loads(resp.read())
        if prompt_id in history:
            outputs = history[prompt_id].get("outputs", {})
            for node_id, node_output in outputs.items():
                images = node_output.get("images", [])
                if images:
                    return images[0].get("filename", "")
    except:
        pass
    return ""


def main():
    parser = argparse.ArgumentParser(description="Generate MMBN battle chip art via ComfyUI")
    parser.add_argument("--sdxl", action="store_true", help="Use SDXL (1024x1024) instead of SD 1.5 (512x512)")
    parser.add_argument("--lora", action="store_true", help="Apply FAITHH pixel art LoRA (faithh_pixel_art.safetensors)")
    parser.add_argument("--lora-strength", type=float, default=0.8, help="LoRA strength 0.0-1.0 (default: 0.8)")
    parser.add_argument("--seed", type=int, default=42, help="Base seed for reproducibility (default: 42)")
    parser.add_argument("--chips", type=str, help="Comma-separated chip indices, e.g. '0,3,7'")
    args = parser.parse_args()

    model_key = "sdxl" if args.sdxl else "sd15"
    cfg = MODELS[model_key]
    lora_name = "faithh_pixel_art.safetensors" if args.lora else None
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Check ComfyUI is reachable
    try:
        urllib.request.urlopen(f"{COMFYUI_URL}/system_stats")
    except:
        print("ERROR: ComfyUI not reachable at", COMFYUI_URL)
        print("Start it with: scripts/start_comfyui.sh")
        sys.exit(1)

    # Filter chips if specified
    chips_to_gen = CHIPS
    if args.chips:
        indices = [int(x) for x in args.chips.split(",")]
        chips_to_gen = [CHIPS[i] for i in indices if i < len(CHIPS)]

    print(f"Generating {len(chips_to_gen)} battle chip icons...")
    print(f"Model: {model_key.upper()} ({cfg['width']}x{cfg['height']})")
    print(f"Checkpoint: {cfg['checkpoint']}")
    if lora_name:
        print(f"LoRA: {lora_name} (strength={args.lora_strength})")
    print(f"Output: {OUTPUT_DIR}")
    print()

    for i, chip in enumerate(chips_to_gen):
        prompt_text = f"{chip['subject']}, {BASE_STYLE}"
        seed = args.seed + i

        print(f"[{i+1}/{len(chips_to_gen)}] {chip['id']}: {chip['subject'][:50]}...")

        workflow = build_workflow(prompt_text, NEGATIVE, seed, model_key, lora_name, args.lora_strength)
        prompt_id = queue_prompt(workflow)

        if not prompt_id:
            print(f"  FAILED to queue {chip['id']}")
            continue

        print(f"  Queued (id: {prompt_id[:8]}...), waiting...")

        if wait_for_completion(prompt_id):
            filename = get_latest_output(prompt_id)
            if filename:
                src = os.path.join(COMFYUI_OUTPUT, filename)
                dst = os.path.join(OUTPUT_DIR, f"{chip['id']}.png")
                if os.path.exists(src):
                    shutil.copy2(src, dst)
                    print(f"  OK -> {dst}")
                else:
                    print(f"  WARNING: output file not found at {src}")
            else:
                print(f"  WARNING: no output filename found")
        else:
            print(f"  TIMEOUT waiting for {chip['id']}")

    print()
    print("Done! Check images at:", OUTPUT_DIR)
    generated = [f for f in os.listdir(OUTPUT_DIR) if f.startswith("chip_") and f.endswith(".png")]
    print(f"Generated: {len(generated)}/{len(CHIPS)} chips")


if __name__ == "__main__":
    main()
