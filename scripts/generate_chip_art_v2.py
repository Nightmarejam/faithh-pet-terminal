#!/usr/bin/env python3
"""
Batch generate MMBN battle chip screen icons v2 — tighter prompts for cleaner icons.
Focuses on single centered subjects with solid backgrounds.
"""

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

CHECKPOINT = "v1-5-pruned-emaonly.safetensors"

# Tighter base style — emphasize SINGLE icon, CENTERED, clean
BASE_STYLE = (
    "single centered game icon sprite, pixel art style, clean sharp edges, "
    "solid color background, 16-bit retro game asset, simple composition, "
    "one subject only, no border, no text, no frame, square icon"
)

NEGATIVE = (
    "blurry, low quality, text, watermark, 3d render, photograph, realistic, "
    "deformed, ugly, noisy, grainy, multiple subjects, border, frame, "
    "signature, logo, words, letters, complex background, scene, landscape, "
    "busy, cluttered, screenshot, UI elements, HUD"
)

# Simplified subjects — short, focused descriptions
CHIPS = [
    {"id": "chip_0",  "subject": "glowing blue brain made of circuits and neural connections, electric blue on dark purple background"},
    {"id": "chip_1",  "subject": "orange server tower with spinning gears, metallic steel on dark blue background"},
    {"id": "chip_2",  "subject": "green sound waveform with headphones, neon green on black background"},
    {"id": "chip_3",  "subject": "red shield with golden lock, glowing red on dark background"},
    {"id": "chip_4",  "subject": "cyan globe with connection arrows, bright cyan on navy background"},
    {"id": "chip_5",  "subject": "teal microchip processor with gold pins, teal on dark background"},
    {"id": "chip_6",  "subject": "purple crystal ball with bar chart inside, purple glow on dark background"},
    {"id": "chip_7",  "subject": "golden book with glowing star above it, warm gold on sunset gradient"},
    {"id": "chip_8",  "subject": "green chat bubble with brain inside, bright green on dark background"},
    {"id": "chip_9",  "subject": "golden chess king piece, metallic gold on navy blue background"},
    {"id": "chip_10", "subject": "rainbow paint palette with brush, colorful on white background"},
    {"id": "chip_11", "subject": "copper circuit board with blinking LED, copper on dark green background"},
    {"id": "chip_12", "subject": "neon game controller, bright neon colors on dark purple background"},
    {"id": "chip_13", "subject": "blue handshake icon with connection nodes, warm blue on dark background"},
    {"id": "chip_14", "subject": "orange robotic arm with gear, industrial orange on steel gray background"},
]


def build_workflow(prompt_text: str, negative_text: str, seed: int) -> dict:
    """Build a ComfyUI API workflow — higher CFG for more prompt adherence."""
    return {
        "3": {
            "class_type": "KSampler",
            "inputs": {
                "seed": seed,
                "steps": 25,
                "cfg": 9.0,
                "sampler_name": "dpmpp_2m",
                "scheduler": "karras",
                "denoise": 1.0,
                "model": ["4", 0],
                "positive": ["6", 0],
                "negative": ["7", 0],
                "latent_image": ["5", 0]
            }
        },
        "4": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {
                "ckpt_name": CHECKPOINT
            }
        },
        "5": {
            "class_type": "EmptyLatentImage",
            "inputs": {
                "width": 512,
                "height": 512,
                "batch_size": 1
            }
        },
        "6": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": prompt_text,
                "clip": ["4", 1]
            }
        },
        "7": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": negative_text,
                "clip": ["4", 1]
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
                "filename_prefix": "faithh_chip_v2",
                "images": ["8", 0]
            }
        }
    }


def queue_prompt(workflow: dict) -> str:
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
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Backup v1 images
    backup_dir = os.path.join(OUTPUT_DIR, "v1_backup")
    os.makedirs(backup_dir, exist_ok=True)
    for f in os.listdir(OUTPUT_DIR):
        if f.startswith("chip_") and f.endswith(".png"):
            src = os.path.join(OUTPUT_DIR, f)
            dst = os.path.join(backup_dir, f)
            if not os.path.exists(dst):
                shutil.copy2(src, dst)
    print(f"Backed up v1 images to {backup_dir}")

    try:
        urllib.request.urlopen(f"{COMFYUI_URL}/system_stats")
    except:
        print("ERROR: ComfyUI not reachable at", COMFYUI_URL)
        sys.exit(1)

    print(f"Generating {len(CHIPS)} battle chip icons (v2 — tighter prompts)...")
    print(f"Checkpoint: {CHECKPOINT}")
    print(f"Settings: 512x512, 25 steps, CFG 9.0, DPM++ 2M Karras")
    print()

    base_seed = 1337  # New seed base for v2

    for i, chip in enumerate(CHIPS):
        prompt_text = f"{chip['subject']}, {BASE_STYLE}"
        seed = base_seed + i

        print(f"[{i+1}/{len(CHIPS)}] {chip['id']}: {chip['subject'][:60]}...")

        workflow = build_workflow(prompt_text, NEGATIVE, seed)
        prompt_id = queue_prompt(workflow)

        if not prompt_id:
            print(f"  FAILED to queue {chip['id']}")
            continue

        print(f"  Queued, waiting...")

        if wait_for_completion(prompt_id):
            filename = get_latest_output(prompt_id)
            if filename:
                src = os.path.join(COMFYUI_OUTPUT, filename)
                dst = os.path.join(OUTPUT_DIR, f"{chip['id']}.png")
                if os.path.exists(src):
                    shutil.copy2(src, dst)
                    print(f"  OK -> {dst}")
                else:
                    print(f"  WARNING: output not found at {src}")
            else:
                print(f"  WARNING: no output filename")
        else:
            print(f"  TIMEOUT")

    print()
    print("Done! Check images at:", OUTPUT_DIR)
    generated = [f for f in os.listdir(OUTPUT_DIR) if f.startswith("chip_") and f.endswith(".png")]
    print(f"Generated: {len(generated)}/{len(CHIPS)} chips")


if __name__ == "__main__":
    main()
