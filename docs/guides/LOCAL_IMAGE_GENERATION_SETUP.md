# 🎨 Local Image Generation Setup Guide
**Goal:** Turn your machine into an image creation powerhouse  
**Created:** November 9, 2025  
**Target:** Generate FAITHH/PULSE avatars and UI mockups locally

---

## 🚀 Quick Start: Best Options for Your Setup

You have **3 main options** for local image generation:

### Option 1: Ollama + LLaVA (Easiest - You Already Have Ollama!) ⭐
**Pros:**
- ✅ You already have Ollama installed
- ✅ Works immediately with existing setup
- ✅ No GPU required (works on CPU)
- ✅ Simple CLI commands

**Cons:**
- ❌ LLaVA is for image understanding, not generation
- ❌ Need to add a proper image generation model

**Action:** Add image generation model to Ollama

---

### Option 2: ComfyUI + Stable Diffusion (Most Powerful) ⭐⭐⭐
**Pros:**
- ✅ Industry-standard image generation
- ✅ Highest quality outputs
- ✅ Node-based workflow (visual programming)
- ✅ Tons of models available
- ✅ Works well on CPU or GPU

**Cons:**
- ❌ Initial setup takes 30-60 minutes
- ❌ Larger downloads (models are 2-7GB each)
- ❌ Steeper learning curve

**Action:** Install ComfyUI for professional results

---

### Option 3: Automatic1111 WebUI (Middle Ground) ⭐⭐
**Pros:**
- ✅ Great web interface
- ✅ Easy to use once installed
- ✅ Popular with lots of community support

**Cons:**
- ❌ Similar setup complexity to ComfyUI
- ❌ Less flexible than ComfyUI

**Action:** Install A1111 WebUI

---

## 🎯 Recommended Path: Start with ComfyUI

**Why ComfyUI?**
- Most powerful and flexible
- Works great locally
- Node-based workflow is intuitive once you learn it
- Can generate exactly what you need for FAITHH

Let's set it up!

---

## 📦 Part 1: Install ComfyUI (30 minutes)

### Step 1: Check Your System

```bash
# Check Python version (need 3.10 or higher)
python3 --version

# Check if you have git
git --version

# Check available disk space (need ~10GB)
df -h ~

# Check if you have GPU (optional but helpful)
lspci | grep -i vga
nvidia-smi  # If you have NVIDIA GPU
```

---

### Step 2: Install ComfyUI

```bash
# Navigate to your ai-stack
cd ~/ai-stack

# Create a directory for image generation
mkdir -p image-generation
cd image-generation

# Clone ComfyUI
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI

# Install dependencies
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
# OR if you have NVIDIA GPU:
# pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

pip install -r requirements.txt
```

**Expected output:** Installation completes without errors

---

### Step 3: Download Stable Diffusion Model

You need at least one checkpoint model. Here are good options:

#### Option A: Stable Diffusion 1.5 (Recommended - 4GB)
```bash
cd ~/ai-stack/image-generation/ComfyUI/models/checkpoints

# Download SD 1.5 (good all-around model)
wget https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned-emaonly.safetensors
```

#### Option B: Stable Diffusion XL (Better Quality - 7GB)
```bash
# Download SDXL (higher quality, slower)
wget https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors
```

#### Option C: DreamShaper (Community Favorite - 2GB)
```bash
# Great for character designs
wget https://civitai.com/api/download/models/128713 -O dreamshaper_8.safetensors
```

**Pick ONE to start.** I recommend SD 1.5 for speed and compatibility.

---

### Step 4: Start ComfyUI

```bash
cd ~/ai-stack/image-generation/ComfyUI

# Start the server
python main.py

# OR if you have GPU:
# python main.py --highvram
```

**Expected output:**
```
Starting server
To see the GUI go to: http://127.0.0.1:8188
```

---

### Step 5: Access ComfyUI

Open your browser and go to:
```
http://127.0.0.1:8188
```

**You should see:** A node-based interface with connected boxes

---

## 🎨 Part 2: Generate Your First Image (10 minutes)

### Basic Workflow in ComfyUI:

1. **Default Workflow Loaded:** ComfyUI starts with a basic workflow
2. **Key Nodes:**
   - `Load Checkpoint` - Loads your SD model
   - `CLIP Text Encode (Prompt)` - Your text prompt
   - `Empty Latent Image` - Image size settings
   - `KSampler` - Does the generation
   - `VAE Decode` - Converts to visible image
   - `Save Image` - Saves the output

3. **Generate Test Image:**
   - Find the prompt node (usually says "beautiful scenery...")
   - Change text to: "cute AI robot assistant, friendly face, cyan highlights"
   - Click "Queue Prompt" button
   - Wait 30-60 seconds
   - Image appears on the right side!

**Output location:** `~/ai-stack/image-generation/ComfyUI/output/`

---

## 🤖 Part 3: Generate FAITHH Avatar (20 minutes)

Now let's create your actual FAITHH avatar!

### Workflow Setup:

1. **Set Image Size:**
   - Find `Empty Latent Image` node
   - Change to: 512x512 (square for avatar)

2. **Positive Prompt** (what you want):
```
cute AI assistant avatar, friendly helpful expression, 
glowing cyan highlights, MegaMan Battle Network style, 
retro-futuristic design, digital holographic character, 
geometric shapes, tech aesthetic, professional but playful, 
transparent background style, centered portrait, 
clean vector art look, cyberpunk chibi
```

3. **Negative Prompt** (what you don't want):
```
blurry, low quality, distorted, asymmetric, messy, 
realistic photo, human, complex background, 
multiple characters, text, watermark
```

4. **Settings in KSampler:**
   - Steps: 20-30
   - CFG Scale: 7-8
   - Seed: Random (or set specific number for reproducibility)

5. **Click "Queue Prompt"**

6. **Wait 30-60 seconds**

7. **Check output folder:**
```bash
ls -lh ~/ai-stack/image-generation/ComfyUI/output/
```

---

## 🔷 Part 4: Generate PULSE Avatar (10 minutes)

Same process but different prompt:

### PULSE Prompt:
```
technical system monitoring AI avatar, 
geometric hexagonal design, blue neon highlights, 
analytical robotic appearance, precise clean lines, 
MegaMan Battle Network inspired, monitoring interface aesthetic, 
hexagonal frame, technical readout style, 
professional utility-focused design, blue theme, 
centered icon, clean geometric shapes
```

**Generate multiple variations:**
- Change seed for different versions
- Adjust CFG scale (lower = more creative, higher = more literal)
- Try different models if available

---

## 🛠️ Part 5: Advanced Setup (Optional)

### Install Custom Nodes (Extend ComfyUI):

```bash
cd ~/ai-stack/image-generation/ComfyUI/custom_nodes

# ComfyUI Manager (highly recommended!)
git clone https://github.com/ltdrdata/ComfyUI-Manager.git

# Restart ComfyUI
# Now you can install more nodes via the UI
```

### Download More Models:

**ControlNet** (for pose control):
```bash
cd ~/ai-stack/image-generation/ComfyUI/models/controlnet
wget https://huggingface.co/lllyasviel/ControlNet-v1-1/resolve/main/control_v11p_sd15_openpose.pth
```

**LoRA** (for specific styles):
```bash
cd ~/ai-stack/image-generation/ComfyUI/models/loras
# Download from CivitAI or HuggingFace as needed
```

---

## 🚀 Part 6: Create FAITHH Image Generation Script

Let's automate this with a Python script!

### Create: `generate_faithh_avatar.py`

```python
#!/usr/bin/env python3
"""
FAITHH Avatar Generator
Uses ComfyUI API to generate avatars programmatically
"""

import json
import urllib.request
import urllib.parse
import time
import random

# ComfyUI server details
SERVER_ADDRESS = "127.0.0.1:8188"

# Prompts
FAITHH_PROMPT = """
cute AI assistant avatar, friendly helpful expression, 
glowing cyan highlights, MegaMan Battle Network style, 
retro-futuristic design, digital holographic character, 
geometric shapes, tech aesthetic, professional but playful, 
centered portrait, clean vector art look, cyberpunk chibi
"""

PULSE_PROMPT = """
technical system monitoring AI avatar, 
geometric hexagonal design, blue neon highlights, 
analytical robotic appearance, precise clean lines, 
MegaMan Battle Network inspired, monitoring interface aesthetic, 
hexagonal frame, professional utility-focused design
"""

NEGATIVE_PROMPT = """
blurry, low quality, distorted, asymmetric, messy, 
realistic photo, human, complex background, 
multiple characters, text, watermark
"""

def queue_prompt(prompt_workflow):
    """Send prompt to ComfyUI"""
    p = {"prompt": prompt_workflow}
    data = json.dumps(p).encode('utf-8')
    req = urllib.request.Request(f"http://{SERVER_ADDRESS}/prompt", data=data)
    return json.loads(urllib.request.urlopen(req).read())

def get_workflow(character_name, prompt_text, seed=None):
    """Create workflow for character generation"""
    if seed is None:
        seed = random.randint(1, 1000000)
    
    workflow = {
        "3": {
            "class_type": "KSampler",
            "inputs": {
                "seed": seed,
                "steps": 25,
                "cfg": 7.5,
                "sampler_name": "euler",
                "scheduler": "normal",
                "denoise": 1,
                "model": ["4", 0],
                "positive": ["6", 0],
                "negative": ["7", 0],
                "latent_image": ["5", 0]
            }
        },
        "4": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {
                "ckpt_name": "v1-5-pruned-emaonly.safetensors"
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
                "text": NEGATIVE_PROMPT,
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
                "filename_prefix": f"{character_name}_avatar",
                "images": ["8", 0]
            }
        }
    }
    return workflow

def generate_avatar(character_name, prompt_text, count=4):
    """Generate multiple variations of avatar"""
    print(f"\n🎨 Generating {count} variations of {character_name}...\n")
    
    for i in range(count):
        seed = random.randint(1, 1000000)
        workflow = get_workflow(character_name, prompt_text, seed)
        
        print(f"  [{i+1}/{count}] Generating with seed {seed}...")
        result = queue_prompt(workflow)
        print(f"  ✅ Queued: {result}")
        
        # Wait a bit between generations
        time.sleep(2)
    
    print(f"\n✅ Done! Check ComfyUI/output/ for results\n")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python generate_faithh_avatar.py [faithh|pulse|both] [count]")
        print("Example: python generate_faithh_avatar.py both 4")
        sys.exit(1)
    
    character = sys.argv[1].lower()
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    
    if character == "faithh":
        generate_avatar("FAITHH", FAITHH_PROMPT, count)
    elif character == "pulse":
        generate_avatar("PULSE", PULSE_PROMPT, count)
    elif character == "both":
        generate_avatar("FAITHH", FAITHH_PROMPT, count)
        generate_avatar("PULSE", PULSE_PROMPT, count)
    else:
        print("Unknown character. Use: faithh, pulse, or both")
```

### Usage:

```bash
# Make executable
chmod +x generate_faithh_avatar.py

# Generate 4 FAITHH variations
python generate_faithh_avatar.py faithh 4

# Generate 4 PULSE variations
python generate_faithh_avatar.py pulse 4

# Generate both (4 of each)
python generate_faithh_avatar.py both 4
```

---

## 🎯 Part 7: Integrate with FAITHH Backend

Add image generation endpoint to your backend:

```python
# Add to faithh_professional_backend.py

@app.route('/api/generate/avatar', methods=['POST'])
def generate_avatar_api():
    """
    Generate avatar via ComfyUI
    Body: { "character": "faithh" or "pulse", "count": 4 }
    """
    data = request.json
    character = data.get('character', 'faithh')
    count = data.get('count', 4)
    
    # Call generation script
    import subprocess
    result = subprocess.run(
        ['python', 'generate_faithh_avatar.py', character, str(count)],
        cwd='/home/jonat/ai-stack/image-generation',
        capture_output=True,
        text=True
    )
    
    return jsonify({
        'success': True,
        'character': character,
        'count': count,
        'output': result.stdout,
        'location': '/home/jonat/ai-stack/image-generation/ComfyUI/output/'
    })
```

---

## 📊 Expected Results

### After Setup You'll Have:
- ✅ ComfyUI running locally
- ✅ Stable Diffusion model installed
- ✅ Ability to generate images via UI
- ✅ Python script for automation
- ✅ Backend API endpoint for generation

### Generated Files:
```
~/ai-stack/image-generation/ComfyUI/output/
├── FAITHH_avatar_00001.png
├── FAITHH_avatar_00002.png
├── FAITHH_avatar_00003.png
├── FAITHH_avatar_00004.png
├── PULSE_avatar_00001.png
├── PULSE_avatar_00002.png
└── ... (more variations)
```

---

## 🔧 Troubleshooting

### ComfyUI won't start:
```bash
# Check Python version
python3 --version  # Need 3.10+

# Install missing dependencies
pip install -r requirements.txt

# Try with lower memory settings
python main.py --lowvram
```

### Generation is too slow:
```bash
# Reduce steps (faster, lower quality)
# In workflow: steps: 20 -> 10

# Use smaller model
# Download SD 1.5 instead of SDXL

# Reduce resolution
# 512x512 -> 256x256 for testing
```

### Images look bad:
```bash
# Increase steps
# steps: 20 -> 30

# Adjust CFG scale
# cfg: 7.5 -> 8.5 (more prompt adherence)

# Try different seed
# Generate 10+ variations, pick best

# Download better model
# DreamShaper or RealisticVision
```

### Can't access web UI:
```bash
# Check if server is running
ps aux | grep main.py

# Check port
lsof -i :8188

# Try different port
python main.py --port 8189
```

---

## 🚀 Next Steps After Setup

### 1. Generate Avatar Set (30 min):
```bash
python generate_faithh_avatar.py both 10
# Generate 10 of each, pick best 2
```

### 2. Post-Process (Optional):
```bash
# Remove backgrounds with rembg
pip install rembg
rembg i FAITHH_avatar_00001.png FAITHH_avatar_final.png

# Resize to exact size
convert FAITHH_avatar_final.png -resize 128x128 faithh_small.png
```

### 3. Integrate into FAITHH UI:
```bash
cp FAITHH_avatar_final.png ~/ai-stack/images/faithh_v2/avatars/faithh_small.png
cp PULSE_avatar_final.png ~/ai-stack/images/faithh_v2/avatars/pulse_small.png
```

### 4. Test in UI:
```html
<img src="images/faithh_v2/avatars/faithh_small.png" alt="FAITHH">
```

---

## ⚡ Quick Reference Commands

```bash
# Start ComfyUI
cd ~/ai-stack/image-generation/ComfyUI && python main.py

# Generate avatars
cd ~/ai-stack/image-generation && python generate_faithh_avatar.py both 4

# View outputs
ls -lh ~/ai-stack/image-generation/ComfyUI/output/

# Open output folder
explorer.exe ~/ai-stack/image-generation/ComfyUI/output/

# Stop ComfyUI
# Ctrl+C in terminal
```

---

## 📚 Resources

- **ComfyUI Wiki:** https://github.com/comfyanonymous/ComfyUI/wiki
- **Model Downloads:** https://civitai.com/ and https://huggingface.co/
- **ComfyUI Workflows:** https://openart.ai/workflows
- **Tutorial Videos:** Search "ComfyUI tutorial" on YouTube

---

## ✅ Success Checklist

- [ ] ComfyUI installed and running
- [ ] At least one SD model downloaded
- [ ] Can generate test image via UI
- [ ] Generated FAITHH avatar variations
- [ ] Generated PULSE avatar variations
- [ ] Selected best versions
- [ ] Copied to correct image folder
- [ ] Tested in FAITHH UI

---

**You're now a local image generation powerhouse!** 🎨🚀

Generate as many variations as you want, no API costs, no rate limits!
