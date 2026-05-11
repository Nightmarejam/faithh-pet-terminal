# 🎯 Ready-to-Use Prompts for Local Image Generation
**Optimized for Stable Diffusion 1.5 on ComfyUI**

Copy these directly into ComfyUI!

---

## 🤖 FAITHH Avatar Prompts

### Version 1: Chibi Style (Recommended)
**Positive Prompt:**
```
cute AI assistant robot character, chibi style avatar, 
friendly welcoming expression with big smile, 
glowing cyan blue highlights and accents, 
geometric tech patterns, digital holographic effect,
MegaMan Battle Network inspired design,
retro futuristic aesthetic, clean vector art style,
centered portrait composition, simple background,
professional quality, detailed face, 
kawaii robot character, helpful personality,
high quality, masterpiece, 8k
```

**Negative Prompt:**
```
blurry, low quality, bad anatomy, distorted face,
asymmetric features, messy lines, realistic photo,
complex background, multiple characters, 
human face, text, watermark, signature,
dark colors, scary, menacing, 
low resolution, jpeg artifacts
```

**Settings:**
- Size: 512x512
- Steps: 25
- CFG Scale: 7.5
- Sampler: Euler a or DPM++ 2M Karras

---

### Version 2: Geometric Minimalist
**Positive Prompt:**
```
minimalist AI avatar icon, geometric shapes forming friendly face,
cyan glowing elements, simple clean design,
hexagonal or circular frame border,
digital tech aesthetic, holographic glow,
MegaMan Battle Network style, modern minimalist,
works at small sizes, memorable design,
professional icon, tech company logo style,
high quality, clean lines, centered composition
```

**Negative Prompt:**
```
complex, detailed, busy, cluttered,
realistic, photographic, human,
messy, blurry, low quality,
multiple characters, text
```

**Settings:**
- Size: 512x512
- Steps: 20
- CFG Scale: 8
- Sampler: Euler a

---

### Version 3: Holographic Character
**Positive Prompt:**
```
holographic AI assistant character, full body standing pose,
transparent glowing blue cyan energy form,
friendly welcoming gesture with raised hand,
digital particle effects and circuit patterns,
futuristic sci-fi design, MegaMan Battle Network navi style,
professional but playful appearance,
clean geometric shapes, tech aesthetic,
dark background with grid pattern,
high quality, detailed, masterpiece, 8k
```

**Negative Prompt:**
```
solid body, opaque, realistic human,
complex background, cluttered, messy,
low quality, blurry, distorted,
scary, menacing, dark colors,
text, watermark
```

**Settings:**
- Size: 512x768 (vertical)
- Steps: 30
- CFG Scale: 7
- Sampler: DPM++ 2M Karras

---

## 🔷 PULSE Avatar Prompts

### Version 1: Technical Monitor (Recommended)
**Positive Prompt:**
```
technical system monitoring AI avatar,
hexagonal geometric face design,
blue neon highlights and glowing elements,
analytical robotic appearance, precise clean lines,
monitoring interface aesthetic, status indicator style,
MegaMan Battle Network inspired,
professional utility-focused design,
hexagonal frame border, tech readout style,
blue theme #3b82f6, centered icon composition,
high quality, clean, masterpiece
```

**Negative Prompt:**
```
friendly, cute, playful, warm colors,
complex background, messy, cluttered,
realistic, human, organic shapes,
red, yellow, green colors,
low quality, blurry, distorted,
text, watermark
```

**Settings:**
- Size: 512x512
- Steps: 25
- CFG Scale: 8
- Sampler: Euler a

---

### Version 2: Abstract System Icon
**Positive Prompt:**
```
abstract system health monitoring icon,
geometric blue glowing elements,
hexagonal grid pattern, pulse wave integrated,
minimalist technical design, status indicator,
blue #3b82f6 theme, dark background,
clean lines, professional monitoring symbol,
works at small icon sizes 64x64,
high quality, simple, clean
```

**Negative Prompt:**
```
complex, detailed, realistic,
multiple elements, cluttered,
warm colors, friendly appearance,
low quality, messy, blurry
```

**Settings:**
- Size: 512x512
- Steps: 20
- CFG Scale: 8.5
- Sampler: Euler a

---

### Version 3: Full Monitoring Interface
**Positive Prompt:**
```
advanced system monitoring AI interface,
central AI entity surrounded by holographic displays,
blue transparent form with technical patterns,
hexagonal design elements throughout,
floating technical readouts and metrics,
data streams and graphs around character,
monitoring station aesthetic, command center vibes,
radial UI arrangement, professional dashboard,
blue #3b82f6 primary color, dark background,
high quality, detailed, masterpiece, 8k
```

**Negative Prompt:**
```
colorful, playful, cute, friendly,
warm colors, red, yellow, orange,
simple, minimal, realistic photo,
cluttered, messy, low quality,
text, watermark
```

**Settings:**
- Size: 768x512 (horizontal) or 1024x768
- Steps: 30
- CFG Scale: 7
- Sampler: DPM++ 2M Karras

---

## 🎨 UI Mockup Prompts

### Main Chat Interface
**Positive Prompt:**
```
retro futuristic chat interface UI design,
dark blue black background with cyan neon accents,
three panel layout, left sidebar with avatar boxes,
center chat area with message bubbles,
right panel with statistics and settings,
MegaMan Battle Network PET terminal aesthetic,
CRT scanline effects, glowing borders,
corner accent decorations, cyberpunk terminal design,
professional UI mockup, clean layout,
monospace font, tech interface,
high quality, detailed, 8k
```

**Negative Prompt:**
```
modern flat design, bright colors,
messy, cluttered, low quality,
realistic, photographic,
text readable, specific text content
```

**Settings:**
- Size: 1024x768 or 1536x1024
- Steps: 30
- CFG Scale: 7
- Sampler: DPM++ 2M Karras

---

## 🔧 Advanced Prompt Techniques

### Add These for Better Results:

**For Sharper Details:**
```
, highly detailed, sharp focus, 4k, 8k, masterpiece
```

**For Consistent Style:**
```
, vector art style, clean lines, professional graphic design
```

**For Retro Aesthetic:**
```
, pixel art inspired, retro gaming aesthetic, 90s anime style
```

**For Tech Feel:**
```
, holographic display, digital interface, cyberpunk tech, neon glow
```

---

## 🎯 Prompt Engineering Tips

### 1. Token Order Matters
- Put important concepts first
- "cute AI robot" vs "AI robot, cute" 
- First version emphasizes cuteness more

### 2. Use Weights (Advanced)
```
(cute:1.3) AI robot, (cyan highlights:1.2)
```
- Values > 1.0 = more emphasis
- Values < 1.0 = less emphasis

### 3. Negative Prompts are Powerful
- Always include "low quality, blurry"
- Add specific things you DON'T want
- Be specific: "red colors" not just "bad colors"

### 4. Style Keywords
- "masterpiece" = higher quality
- "8k" = more detail
- "professional" = cleaner look
- "high quality" = generally better

### 5. Composition Keywords
- "centered" = subject in middle
- "portrait" = face focus
- "full body" = whole character
- "close up" = zoomed in

---

## 🔄 Iteration Strategy

### Round 1: Generate 10 variations
- Use same prompt, different seeds
- See what style emerges
- Note which seeds give best results

### Round 2: Refine prompt
- Add keywords based on Round 1
- Remove elements you don't like
- Adjust negative prompt

### Round 3: Generate 10 more
- With refined prompt
- Should be closer to target
- Pick top 3

### Round 4: Fine-tune
- Adjust CFG scale (higher = more literal)
- Adjust steps (higher = more refined)
- Try different samplers

---

## 📋 Quick Test Prompts

### Test if everything works:
```
Positive: cute robot mascot, simple design, blue highlights
Negative: complex, realistic, human
Steps: 20
CFG: 7
```

### Test quality:
```
Positive: professional logo design, high quality, 8k, masterpiece
Negative: low quality, blurry, distorted
Steps: 25
CFG: 8
```

---

## 🎨 Color-Specific Prompts

### Cyan Theme (FAITHH):
```
glowing cyan highlights (#00ffff), bright blue accents,
teal and turquoise elements, electric blue glow,
cyan neon effects, blue-green color scheme
```

### Blue Theme (PULSE):
```
deep blue primary color (#3b82f6), 
royal blue highlights, cobalt blue accents,
blue tech aesthetic, blue holographic effects
```

### Avoid These Colors:
```
Negative: red, orange, yellow, pink, green, purple,
warm colors, vibrant rainbow
```

---

## ✅ Prompt Checklist

Before generating, verify your prompt has:

- [ ] Main subject clearly defined
- [ ] Style keywords (chibi, minimalist, etc.)
- [ ] Color specifications (cyan, blue)
- [ ] Quality keywords (high quality, masterpiece)
- [ ] Composition (centered, portrait)
- [ ] Aesthetic (MegaMan, retro-futuristic)
- [ ] Negative prompt with exclusions
- [ ] Settings configured (size, steps, CFG)

---

## 🚀 Ready to Generate!

**Quick Start Workflow:**

1. Copy FAITHH V1 prompt (chibi style)
2. Paste into ComfyUI positive prompt box
3. Copy negative prompt
4. Paste into ComfyUI negative prompt box
5. Set: 512x512, 25 steps, CFG 7.5
6. Click "Queue Prompt"
7. Generate 10 variations (change seed each time)
8. Pick best 2-3
9. Repeat for PULSE V1 prompt

**Time:** 30-60 minutes for 20 total images

---

**These prompts are battle-tested and ready to use!** 🎨

Just copy, paste, and generate. No thinking required.
