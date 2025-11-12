# 🔧 Git Cleanup and Repository Preparation

**Issue:** Your .git folder is 28GB with 27.41GB of garbage from failed pack operations.

---

## 🚨 **Current Status:**

```bash
Git repository size: 28GB
Actual code size: ~225MB
Garbage: 27.41GB (failed pack files)
```

**This happened because:** At some point, git tried to pack large files (models/venv) and failed, leaving temp files behind.

---

## ✅ **Solution: Clean Up Git**

### **Step 1: Clean Up Garbage (Safe)**

```bash
cd ~/ai-stack

# Remove garbage
git gc --prune=now --aggressive

# This will:
# - Remove the 27GB of temp pack files
# - Optimize the repository
# - Take 5-10 minutes
```

### **Step 2: Verify .gitignore is Complete**

Your .gitignore is good, but let's add a few more safety items:

```bash
cd ~/ai-stack

# Add these to .gitignore if not already there:
cat >> .gitignore << 'EOF'

# Additional safety items
*.pid
.backend.pid
.server.pid

# Uploads
uploads/

# Backups folder
backups/

# ComfyUI and Stable Diffusion (in parent directory)
../ComfyUI/
../stable-diffusion-webui/

# Node modules if any
node_modules/

# Large temporary files
file_list_*.txt
discovery_*.txt
EOF
```

### **Step 3: Check Nothing Large is Staged**

```bash
cd ~/ai-stack

# Check what's currently staged
git status

# If you see venv/, models/, or cache/ listed, unstage them:
git reset HEAD venv/
git reset HEAD models/
git reset HEAD cache/
git reset HEAD faithh_rag/
git reset HEAD data/
```

### **Step 4: Clean Workspace**

```bash
cd ~/ai-stack

# Remove untracked files (if any large ones)
git clean -fd --dry-run   # Preview what will be removed
git clean -fd             # Actually remove (if looks safe)
```

---

## 📊 **After Cleanup:**

Your git repository should be:
- **Before:** 28GB
- **After:** ~500MB (code + history)
- **Savings:** 27.5GB freed!

---

## 🎯 **Preparing for Git Commit:**

### **Step 1: Review Changes**

```bash
cd ~/ai-stack
git status
```

You should see:
- Modified files (from cleanup)
- New organized structure
- No large files

### **Step 2: Stage Changes**

```bash
# Stage all changes
git add .

# Or stage specific files:
git add faithh_professional_backend.py
git add faithh_pet_v3.html
git add faithh_ui_v4.html
git add docs/
git add backend/
git add scripts/
git add tests/
git add README.md
git add .gitignore
```

### **Step 3: Create Commit**

```bash
git commit -m "chore: major project cleanup and organization

- Organized 50+ files from root into proper directories
- Moved documentation to docs/ with subdirectories
- Moved tests to tests/
- Moved backend modules to backend/
- Moved scripts to scripts/
- Removed 63 Zone.Identifier files
- Removed temporary discovery files
- Created comprehensive documentation
- Updated .gitignore
- Cleaned up git repository (removed 27GB garbage)

Project now has clean structure with only 17 essential files in root.
Backend running stable on port 5557.
All tests passing."
```

### **Step 4: Verify Commit**

```bash
# Check commit was successful
git log -1 --stat

# Check repository size
du -sh .git
```

---

## 🚀 **Setting Up Remote (Optional)**

If you want to push to GitHub/GitLab:

### **Option 1: New Repository**

```bash
# Create new repo on GitHub/GitLab, then:
git remote add origin https://github.com/YOUR_USERNAME/faithh-project.git
git branch -M main
git push -u origin main
```

### **Option 2: Existing Repository**

```bash
# Check current remote
git remote -v

# If exists, push:
git push origin main

# If doesn't exist, add it first (see Option 1)
```

---

## ⚠️ **Before Pushing to Remote:**

### **Security Check:**

```bash
# Make ABSOLUTELY SURE no API keys are committed
grep -r "AIzaSy" . --exclude-dir=.git
grep -r "sk-" . --exclude-dir=.git
grep -r "GEMINI_API_KEY" . --exclude-dir=.git

# Check .env is not committed
git ls-files | grep .env

# If .env shows up, remove it from git:
git rm --cached .env
git commit -m "security: remove .env from git"
```

### **Current API Key Status:**

⚠️ **Your .env file contains:**
```
GEMINI_API_KEY=YOUR_GEMINI_API_KEY_HERE
```

**Action needed:**
1. This key should **NOT** be committed to git
2. Your .gitignore already excludes `.env` ✅
3. If it's in git history, remove it:

```bash
# Check if .env is in git
git log --all --full-history -- .env

# If it appears, use git-filter-repo to remove it:
# (Install: pip install git-filter-repo)
git filter-repo --path .env --invert-paths
```

---

## 📝 **Git Workflow Going Forward:**

### **Daily Workflow:**

```bash
# 1. Check status
git status

# 2. Stage changes
git add <files>

# 3. Commit
git commit -m "feat: description of changes"

# 4. Push (if using remote)
git push
```

### **Commit Message Convention:**

```
feat: new feature
fix: bug fix
docs: documentation changes
style: formatting, no code change
refactor: code restructuring
test: adding tests
chore: maintenance, cleanup
```

### **Example Commits:**

```bash
git commit -m "feat: add v4 UI with avatar panels"
git commit -m "fix: correct API endpoint for RAG search"
git commit -m "docs: add ComfyUI integration guide"
git commit -m "refactor: organize backend modules"
git commit -m "chore: update dependencies"
```

---

## 🎯 **Quick Cleanup Script:**

Save this as `scripts/git_cleanup.sh`:

```bash
#!/bin/bash

echo "🔧 Git Cleanup Starting..."

cd ~/ai-stack

# Step 1: Garbage collection
echo "Removing garbage and optimizing..."
git gc --prune=now --aggressive

# Step 2: Check size
echo ""
echo "Repository size:"
du -sh .git

# Step 3: Check for large files
echo ""
echo "Checking for large files..."
git rev-list --objects --all | \
git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' | \
sed -n 's/^blob //p' | \
sort -nk2 | \
tail -10

echo ""
echo "✅ Cleanup complete!"
echo ""
echo "Next steps:"
echo "  1. Review changes: git status"
echo "  2. Stage files: git add ."
echo "  3. Commit: git commit -m 'your message'"
echo "  4. Push: git push (if using remote)"
```

---

## 📊 **Repository Health Check:**

```bash
# Check repo status
cd ~/ai-stack

# Size
echo "=== Repository Size ==="
du -sh .git

# Object count
echo ""
echo "=== Object Statistics ==="
git count-objects -vH

# Tracked files
echo ""
echo "=== Tracked Files ==="
git ls-files | wc -l

# Branch info
echo ""
echo "=== Branch Info ==="
git branch -v

# Recent commits
echo ""
echo "=== Recent Commits ==="
git log --oneline -10
```

---

## ✅ **Success Criteria:**

After cleanup, you should have:

- [ ] .git folder < 1GB (down from 28GB)
- [ ] No garbage files
- [ ] .gitignore properly configured
- [ ] No API keys in git history
- [ ] Clean git status
- [ ] All files organized
- [ ] Ready to commit and push

---

**Run the cleanup now:**

```bash
cd ~/ai-stack
git gc --prune=now --aggressive
du -sh .git   # Check new size
```

Then we can move on to setting up your local AI agent system! 🚀
