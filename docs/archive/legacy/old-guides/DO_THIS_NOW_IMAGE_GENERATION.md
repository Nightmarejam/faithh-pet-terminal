# ⚡ DO THIS NOW: Image Generation Session

**Time Required:** 90 minutes  
**Goal:** Generate FAITHH and PULSE avatar images

---

## 🎯 Step-by-Step: No Thinking Required

### Step 1: Start Stable Diffusion WebUI (5 min)

Open WSL terminal and run:

```bash
cd ~/stable-diffusion-webui
./webui.sh --listen
```

**Wait for this message:**
```
Running on local URL:  http://127.0.0.1:7860
```

Then open browser to: **http://localhost:7860**

---

### Step 2: Generate FAITHH Avatars (35 min)

In the Stable Diffusion WebUI:

**1. Paste this in "Prompt" box:**
```
cute AI assistant robot character, chibi style avatar, friendly welcoming expression with big smile, glowing cyan blue highlights and accents, geometric tech patterns, digital holographic effect, MegaMan Battle Network inspired design, retro futuristic aesthetic, clean vector art style, centered portrait composition, simple background, professional quality, detailed face, kawaii robot character, helpful personality, high quality, masterpiece, 8k
```

**2. Paste this in "Negative prompt" box:**
```
blurry, low quality, bad anatomy, distorted face, asymmetric features, messy lines, realistic photo, complex background, multiple characters, human face, text, watermark, signature, dark colors, scary, menacing, low resolution, jpeg artifacts
```

**3. Set these parameters:**
- Width: **512**
- Height: **512**
- Sampling steps: **25**
- CFG Scale: **7.5**
- Sampler: **Euler a** (or DPM++ 2M Karras)

**4. Click "Generate"** 

**5. Wait 30-90 seconds for first image**

**6. Like it? Great! Hate it? Click Generate again**

**7. Repeat 10 times** (each time generates a new variation)

**8. Save your favorites** (right-click → Save image as → "faithh_01.png", "faithh_02.png", etc.)

---

### Step 3: Generate PULSE Avatars (35 min)

**1. Clear the prompt box and paste this:**
```
technical system monitoring AI avatar, hexagonal geometric face design, blue neon highlights and glowing elements, analytical robotic appearance, precise clean lines, monitoring interface aesthetic, status indicator style, MegaMan Battle Network inspired, professional utility-focused design, hexagonal frame border, tech readout style, blue theme, centered icon composition, high quality, clean, masterpiece
```

**2. Clear negative prompt and paste this:**
```
friendly, cute, playful, warm colors, complex background, messy, cluttered, realistic, human, organic shapes, red, yellow, green colors, low quality, blurry, distorted, text, watermark
```

**3. Keep same parameters:**
- Width: **512**
- Height: **512**
- Sampling steps: **25**
- CFG Scale: **8.0** (slightly higher for PULSE)
- Sampler: **Euler a**

**4. Click "Generate" 10 times** (generate 10 variations)

**5. Save favorites** as "pulse_01.png", "pulse_02.png", etc.

---

### Step 4: Pick Your Winners (10 min)

**Review all images and select:**
- **Best FAITHH image** (friendliest, clearest, most cyan)
- **Best PULSE image** (most technical, clearest, most blue)

**Criteria:**
- ✅ Clear at 128x128 size (zoom out to check)
- ✅ Matches aesthetic (retro-futuristic, MegaMan style)
- ✅ Distinct personalities (FAITHH friendly, PULSE technical)
- ✅ No weird artifacts or distortions

---

### Step 5: Save to Project (5 min)

Open **another** WSL terminal (keep SD-WebUI running):

```bash
# Create directory
mkdir -p ~/ai-stack/images/faithh_v2/avatars

# Navigate to generated images
cd ~/stable-diffusion-webui/outputs/txt2img-images

# List recent directories (today's date)
ls -ltr | tail -5

# Enter today's directory (replace DATE with actual)
cd $(date +%Y-%m-%d)

# View all images
ls -lh *.png

# Copy your selected winners
cp [your_best_faithh_image].png ~/ai-stack/images/faithh_v2/avatars/faithh_small.png
cp [your_best_pulse_image].png ~/ai-stack/images/faithh_v2/avatars/pulse_small.png

# Verify they're there
ls -lh ~/ai-stack/images/faithh_v2/avatars/
```

**You should see:**
```
faithh_small.png
pulse_small.png
```

---

### Step 6: Quick Visual Check (2 min)

```bash
# View the images in Windows
cd ~/ai-stack/images/faithh_v2/avatars
explorer.exe .
```

Double-click each image. Do they look good? Great!

---

## ✅ Success Checklist

You're done when:
- [ ] Generated 10+ FAITHH variations
- [ ] Generated 10+ PULSE variations
- [ ] Selected best of each
- [ ] Saved to `~/ai-stack/images/faithh_v2/avatars/`
- [ ] Files named: `faithh_small.png` and `pulse_small.png`
- [ ] Images look good at small size
- [ ] FAITHH has cyan highlights, friendly face
- [ ] PULSE has blue theme, technical appearance

---

## 🎯 What's Next?

After completing this, you have two options:

### Option A: Integrate into v3 UI (Quick - 15 min)

```bash
cd ~/ai-stack
code faithh_pet_v3.html
```

Find these lines (~890 and ~904):
```html
<img src="images/faithh.png" alt="FAITHH">
<img src="images/pulse.png" alt="PULSE">
```

Change to:
```html
<img src="images/faithh_v2/avatars/faithh_small.png" alt="FAITHH">
<img src="images/faithh_v2/avatars/pulse_small.png" alt="PULSE">
```

Save and test:
```bash
cd ~/ai-stack
python -m http.server 8000
```

Open: http://localhost:8000/faithh_pet_v3.html

See your new avatars? **Success!** 🎉

### Option B: Build v4 UI (Longer - 3 hours)

Follow `VS_CODE_IMPLEMENTATION_HANDOFF.md` Phase 4

---

## 🐛 Troubleshooting

### SD-WebUI won't start?
```bash
cd ~/stable-diffusion-webui
./webui.sh --listen --skip-torch-cuda-test
```

### Images are too small/blurry?
- Try generating at 768x768 instead of 512x512
- Increase sampling steps to 30
- Use "DPM++ 2M Karras" sampler

### Don't like any results?
- Adjust the prompt (add more descriptive words)
- Change CFG scale (lower = more creative, higher = more literal)
- Try different seeds
- Generate 20+ variations instead of 10

### Can't find generated images?
```bash
find ~/stable-diffusion-webui/outputs -name "*.png" -mtime -1
```

---

## ⏱️ Time Tracking

**Start Time:** ___:___

**Checkpoints:**
- [ ] SD-WebUI running (5 min)
- [ ] FAITHH batch 1 done (15 min)
- [ ] FAITHH batch 2 done (30 min)  
- [ ] PULSE batch 1 done (45 min)
- [ ] PULSE batch 2 done (60 min)
- [ ] Winners selected (70 min)
- [ ] Saved to project (75 min)
- [ ] Verified images (77 min)

**End Time:** ___:___

**Total:** ___ minutes

---

## 📸 Document Your Results

Take notes on what worked:

**FAITHH Winner:**
- Seed: ___
- Why I picked it: ___
- What I liked: ___

**PULSE Winner:**
- Seed: ___
- Why I picked it: ___
- What I liked: ___

**Lessons learned:**
- ___
- ___
- ___

---

## 🎊 Congratulations!

When you finish this, you'll have:
- ✅ Real avatar images for your AI project
- ✅ Experience with local image generation
- ✅ Foundation for future image needs
- ✅ Zero dollars spent
- ✅ Complete creative control

**Now go create some avatars!** 🎨

---

**Questions?** Refer to:
- `MASTER_INTEGRATION_DOCUMENT.md` - Full context
- `IMAGE_GENERATION_SETUP.md` - Detailed guide
- `READY_TO_USE_PROMPTS.md` - More prompt variations
