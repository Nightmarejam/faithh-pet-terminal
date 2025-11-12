# 🚀 START HERE - Generate FAITHH Avatars

**Created:** November 9, 2025
**Time needed:** 45-75 minutes
**Goal:** Generate FAITHH and PULSE avatar images

---

## ⚡ Ultra-Quick Start (Copy & Paste)

### Step 1: Start Image Generator (2 min)

```bash
cd ~/stable-diffusion-webui && ./webui.sh --listen
```

**Wait for:** `Running on local URL:  http://127.0.0.1:7860`

Then open in browser: **http://localhost:7860**

---

### Step 2: Generate FAITHH Avatars (20-30 min)

**In the Web UI:**

1. **Paste this in "Prompt" box:**
```
cute AI assistant chibi character, friendly robot mascot,
cyan glowing accents, tech-inspired design, MegaMan Battle Network style,
digital avatar, professional but approachable, clean background,
minimalist geometric shapes, holographic effect, kawaii aesthetic
```

2. **Paste this in "Negative prompt" box:**
```
realistic, photo, human, blurry, low quality, dark, scary
```

3. **Set these settings:**
   - Width: **512**
   - Height: **512**
   - Steps: **30**
   - CFG Scale: **7**

4. **Click "Generate"** → Wait 30-60 seconds

5. **Click "Generate" 9 more times** (for 10 total variations)

---

### Step 3: Generate PULSE Avatars (20-30 min)

**In the Web UI:**

1. **Paste this in "Prompt" box:**
```
technical system monitoring AI icon, robotic face with blue theme,
hexagonal design, circuit board patterns, health monitoring motifs,
geometric minimalist style, serious analytical character,
tech readout aesthetic, MegaMan Battle Network inspired,
clean professional design
```

2. **Keep same negative prompt and settings**

3. **Click "Generate" 10 times** (for 10 PULSE variations)

---

### Step 4: Save Your Favorites (10 min)

```bash
# 1. Create folders
mkdir -p ~/ai-stack/images/raw_generations

# 2. Go to output folder
cd ~/stable-diffusion-webui/outputs/txt2img-images

# 3. Look at all your images
ls -lh

# 4. Copy ALL to raw folder (for safekeeping)
cp *.png ~/ai-stack/images/raw_generations/

# 5. Find your 2 favorite FAITHH images (look at filenames/timestamps)
# Copy best FAITHH to project
cp 00005_.png ~/ai-stack/images/faithh.png

# 6. Find your 2 favorite PULSE images
# Copy best PULSE to project
cp 00015_.png ~/ai-stack/images/pulse.png
```

*(Replace `00005_.png` and `00015_.png` with your actual favorite file numbers)*

---

## ✅ Success Check

**You're done when:**
- ✅ You have `~/ai-stack/images/faithh.png`
- ✅ You have `~/ai-stack/images/pulse.png`
- ✅ Both images look good
- ✅ Raw generations saved in `~/ai-stack/images/raw_generations/`

---

## 🎯 Next Steps (After Images Are Ready)

See **[CURRENT_STATUS_SUMMARY.md](CURRENT_STATUS_SUMMARY.md)** for Phase 3-5:
- Integrate into v3 UI
- Test in browser
- Update parity files
- Commit to git

---

## 🆘 Troubleshooting

### Web UI won't start
```bash
cd ~/stable-diffusion-webui
./webui.sh --skip-torch-cuda-test --precision full --no-half
```

### Images are blurry
- Increase steps to 40-50
- Try CFG Scale 8-10

### Don't like any results
- Change the prompt slightly
- Add more descriptive words
- Try "professional" or "cute" or "minimalist"

---

## 💡 Pro Tips

1. **Don't settle for first result!** Generate 10+ variations
2. **Shrink to 128x128** to test if it works small
3. **Try different words:** "chibi", "kawaii", "professional", "minimalist"
4. **Save ALL raw images** - you might want variations later
5. **Have fun!** Experiment with the prompts

---

**First command:**
```bash
cd ~/stable-diffusion-webui && ./webui.sh --listen
```

**Then open:** http://localhost:7860

**Good luck! You've got this!** 🎨✨

---

**For detailed guide, see:** [IMAGE_GENERATION_SETUP.md](IMAGE_GENERATION_SETUP.md)
**For project status, see:** [CURRENT_STATUS_SUMMARY.md](CURRENT_STATUS_SUMMARY.md)
