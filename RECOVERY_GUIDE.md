# FAITHH UI Recovery Guide
**Last Working State → Current Broken State → Recovery Options**

## 🎯 Quick Diagnosis

Run this in your `~/ai-stack` directory:

```bash
cd ~/ai-stack
chmod +x check_git_history.sh restore_from_git.sh restore_from_backup.sh
./check_git_history.sh
```

This will tell you:
- ✅ If you have Git history
- 📋 What versions are available
- 🔍 Which version you're currently on
- 💡 Best recovery path

---

## 📊 Recovery Path Decision Tree

### PATH A: You Have Git History
**Best option**: Rollback to working commit

```bash
# 1. Check history
cd ~/ai-stack
git log --oneline -- faithh_pet_v3.html

# 2. See what's in a specific commit
git show <commit-hash>:faithh_pet_v3.html | grep -A10 "Object.entries"

# 3. Restore from working commit
git checkout <commit-hash> -- faithh_pet_v3.html

# 4. Restart server
pkill -f faithh_professional_backend.py
python faithh_professional_backend.py &
```

### PATH B: No Git History, But Have Backups
**Second best**: Restore from .bak or .broken files

```bash
# Find backups
ls -lht ~/ai-stack/faithh_pet_v3.html* 

# Pick the oldest/largest (likely the working version)
# Example: faithh_pet_v3.html.bak or faithh_pet_v3.html.broken_20251112_XXXXXX

# Restore
cp faithh_pet_v3.html faithh_pet_v3.html.current_broken
cp faithh_pet_v3.html.bak faithh_pet_v3.html  # or whatever backup file
```

### PATH C: No Git, No Backups
**Manual fix required**: Apply the patch correctly

See "Manual Fix Section" below

---

## 🔧 Manual Fix (If No Git/Backups)

The issue is in the JavaScript status loop. Here's the fix:

### Step 1: Open the file
```bash
nano ~/ai-stack/faithh_pet_v3.html
# Or: code ~/ai-stack/faithh_pet_v3.html
```

### Step 2: Find this broken code (Ctrl+W to search):
```javascript
for (const [service, status] of Object.entries(data.services)) {
```

### Step 3: Replace the ENTIRE loop with this:
```javascript
for (const [service, info] of Object.entries(data.services)) {
    const statusItem = document.createElement('div');
    statusItem.className = 'status-item';
    const statusValue = info.status || 'unknown';
    const isOnline = statusValue === 'online' || statusValue === 'configured';
    const statusIcon = isOnline ? '●' : '○';
    const statusColor = isOnline ? '' : 'style="color: #ff6666;"';
    statusItem.innerHTML = `
        <span class="status-name">${service}</span>
        <span class="status-value" ${statusColor}>${statusIcon} ${statusValue.toUpperCase()}</span>
    `;
    statusList.appendChild(statusItem);
}
```

### Step 4: Save and test
```bash
# Save in nano: Ctrl+O, Enter, Ctrl+X
# Save in VS Code: Ctrl+S

# Restart server
pkill -f faithh_professional_backend.py
python faithh_professional_backend.py &

# Test
curl -s http://localhost:5557 | grep "status-value" | head -3
```

---

## 🧪 Validation Tests

After ANY recovery method, run these:

```bash
# 1. Check file syntax
grep -n "Object.entries(data.services)" ~/ai-stack/faithh_pet_v3.html

# 2. Check for innerHTML
grep -n "statusItem.innerHTML" ~/ai-stack/faithh_pet_v3.html

# 3. Test server response
curl -s http://localhost:5557 | grep -i "status-value" | head -3

# 4. Open browser
# http://localhost:5557
# Press F12 → Console → Should have NO red errors
```

Expected output in browser console: **NO ERRORS**
Expected in UI: **Status panel shows ● ONLINE, ● CONFIGURED, ○ OFFLINE**

---

## 🎓 Git Setup for Future (Recommended)

Prevent this from happening again:

```bash
cd ~/ai-stack

# Initialize Git (if not already)
git init
git config user.name "Jonathan"
git config user.email "jonathan@local"

# Add all files
git add .
git commit -m "Working FAITHH v3 state"

# From now on, after ANY change:
git add faithh_pet_v3.html
git commit -m "Fixed status loop"

# To see history:
git log --oneline

# To rollback:
git checkout HEAD~1 -- faithh_pet_v3.html  # Go back 1 commit
git checkout <commit-hash> -- faithh_pet_v3.html  # Go to specific version
```

### Create .gitignore
```bash
cat > ~/ai-stack/.gitignore << 'EOF'
# Ignore large/temp files
chroma.sqlite3
venv/
__pycache__/
*.pyc
backups/
uploads/
*.log
.env
EOF

git add .gitignore
git commit -m "Added gitignore"
```

---

## 📁 VS Code Local History (Alternative to Git)

If you use VS Code:

1. **Right-click** `faithh_pet_v3.html` in the editor
2. **Select** "Timeline: Open Timeline"
3. **Browse** previous versions (shows timestamps)
4. **Right-click** a version → "Restore Contents"
5. **Save** and test

---

## 🚨 Emergency: Complete UI Restoration

If ALL else fails, here's a minimal working UI:

```bash
curl -o ~/ai-stack/faithh_pet_v3_emergency.html https://raw.githubusercontent.com/YOUR_REPO/faithh_pet_v3.html
# Or copy from the COMPLETE_PACKAGE_INDEX.md document
```

Then:
```bash
cp faithh_pet_v3.html faithh_pet_v3.html.totally_broken
cp faithh_pet_v3_emergency.html faithh_pet_v3.html
```

---

## ✅ Success Checklist

- [ ] Backend starts without "Address already in use"
- [ ] Browser loads http://localhost:5557 
- [ ] No red errors in console (F12)
- [ ] Status panel shows service icons
- [ ] Chat responds to "Hello"
- [ ] RAG toggle works

---

## 📞 Debug Commands

If still broken:

```bash
# Check server logs
tail -f ~/ai-stack/faithh.log  # if you have logging

# Check process
ps aux | grep faithh_professional_backend.py

# Kill all
pkill -f faithh_professional_backend.py

# Start with verbose output
python faithh_professional_backend.py 2>&1 | tee server.log
```

---

## 🎯 Prevention Tips

1. **Always backup before experimenting**:
   ```bash
   cp faithh_pet_v3.html faithh_pet_v3.html.bak_$(date +%Y%m%d_%H%M%S)
   ```

2. **Use Git for every change**:
   ```bash
   git commit -am "Description of change"
   ```

3. **Test in VS Code's integrated terminal**:
   - Changes save automatically
   - Timeline tracks everything
   - Diff view shows exactly what changed

4. **Create a dev/test version**:
   ```bash
   cp faithh_pet_v3.html faithh_pet_v3_test.html
   # Edit test version, keep original safe
   ```

---

**Run `./check_git_history.sh` now to see your options!**
