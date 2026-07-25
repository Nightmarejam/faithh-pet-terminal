# MMBN Battle Chip Art Generation Prompts

Reference: Original Capcom production design sketches for MegaMan Battle Network (Rockman EXE)
- Rectangular cartridge shape, wider than tall
- **Gold contact teeth at the BOTTOM edge** (like inserting into a PET slot)
- Small screen/artwork window in the upper-left area of the front face
- "BATTLE CHIP" text printed vertically on the right side
- Label strip with chip name below the screen window
- Small tab/notch on the top-right corner
- Gray metallic body with subtle shading

Target: 15 ML macro-chips + system chips for FAITHH UI
Image use: inside the chip "screen window" area (the green/colored rectangle)

## Base Style Prompt (use as prefix for all screen-window icons)

```
MegaMan Battle Network battle chip screen icon, flat 2D game sprite style,
pixel-art influenced, clean sharp edges, vibrant subject on gradient background,
game UI asset, centered composition, no text, 256x256, transparent or solid color background,
Rockman EXE style, Capcom GBA era aesthetic
```

## Full Cartridge Prompt (for generating complete chip cartridge art)

```
MegaMan Battle Network physical battle chip cartridge, original Capcom design,
rectangular gray metallic body, gold contact teeth at bottom edge,
small screen window showing [SUBJECT] icon, label strip with chip name,
"BATTLE CHIP" text vertically on right side, small tab on top-right corner,
production design sketch style, clean digital illustration, game merchandise art
```

## Per-Chip Prompts

### 1. AI/ML Engineering (chip_0)
```
A glowing neural network brain with data streams flowing through it,
electric blue circuits on a dark chip screen, MMBN battle chip style,
digital illustration, game UI icon
```

### 2. DevOps & Infrastructure (chip_1)
```
Server rack with glowing gears and cloud nodes connected by data pipes,
orange and steel colors, MMBN battle chip style, digital illustration,
game UI icon
```

### 3. Audio Engineering (chip_2)
```
Sound wave oscilloscope with headphones and mixing knobs, neon green
audio waveform, MMBN battle chip style, digital illustration, game UI icon
```

### 4. Security & Privacy (chip_3)
```
Digital shield with lock icon surrounded by firewall grid lines,
red warning glow, MMBN battle chip style, digital illustration, game UI icon
```

### 5. Web & API Development (chip_4)
```
Globe connected to API endpoints with JSON brackets and HTTP arrows,
cyan and white data flow, MMBN battle chip style, digital illustration,
game UI icon
```

### 6. System Architecture (chip_5)
```
Blueprint-style system diagram with microchip processor and connected
modules, teal and gold schematic lines, MMBN battle chip style,
digital illustration, game UI icon
```

### 7. Data Science & Analytics (chip_6)
```
3D bar chart with scatter plot dots and a magnifying glass over data,
purple and white visualization glow, MMBN battle chip style,
digital illustration, game UI icon
```

### 8. Personal Development (chip_7)
```
Person climbing a mountain of books with a star at the peak,
warm sunrise gradient, MMBN battle chip style, digital illustration,
game UI icon
```

### 9. LLM & NLP (chip_8)
```
Chat bubble with brain neurons forming text, glowing green letters
streaming from a terminal, MMBN battle chip style, digital illustration,
game UI icon
```

### 10. Business & Strategy (chip_9)
```
Chess king piece on a strategy board with dollar signs and growth arrows,
gold and navy colors, MMBN battle chip style, digital illustration,
game UI icon
```

### 11. Creative & Design (chip_10)
```
Paint palette with digital pen and pixel art canvas, rainbow gradient
splash, MMBN battle chip style, digital illustration, game UI icon
```

### 12. Hardware & IoT (chip_11)
```
Raspberry Pi board with sensor nodes and robotic arm, copper PCB traces,
MMBN battle chip style, digital illustration, game UI icon
```

### 13. Gaming & Simulation (chip_12)
```
Game controller with virtual reality headset and pixel character,
neon arcade glow, MMBN battle chip style, digital illustration,
game UI icon
```

### 14. Community & Collaboration (chip_13)
```
Network of connected avatars with handshake icon and chat bubbles,
warm blue community glow, MMBN battle chip style, digital illustration,
game UI icon
```

### 15. Workflow Automation (chip_14)
```
Robotic arm with conveyor belt of gears and automated task icons,
industrial orange and steel, MMBN battle chip style, digital illustration,
game UI icon
```

## Generation Tools

### Option A: Stable Diffusion (Local — your RTX 3090)
- Install ComfyUI or Automatic1111
- Use SDXL or SD 1.5 with a pixel art / game art LoRA
- Recommended LoRA: "pixel-art-xl" or "game-icon-institute"
- Generate at 512x512, upscale to desired size
- Batch generate all 15 in one session with consistent seed

### Option B: DALL-E 3 (API)
- Use the prompts above directly
- Add "no text, no watermark, clean icon" to avoid text artifacts
- $0.04-0.08 per image

### Option C: Midjourney
- Prefix each prompt with `/imagine`
- Add `--style raw --ar 1:1 --v 6` for consistent game art style

## Image Placement
Once generated, save images to:
```
/home/jonat/ai-stack/images/chips/
  chip_0.png   (AI/ML Engineering)
  chip_1.png   (DevOps)
  chip_2.png   (Audio)
  ...
  chip_14.png  (Workflow Automation)
```

The frontend `renderMlChips()` function can be updated to show
`<img>` tags inside `.chip-screen` instead of emoji icons.
