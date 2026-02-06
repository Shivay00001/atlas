# ⚡ ShivAI Atlas - 5 Minute Quick Start

Get Atlas running in 5 minutes!

## 🎯 Prerequisites

✅ Windows 10/11  
✅ Python 3.11+ installed  
✅ Node.js 16+ installed  

**Don't have them?** Download:
- Python: https://www.python.org/downloads/
- Node.js: https://nodejs.org/

---

## 🚀 Installation (2 minutes)

### 1️⃣ Download Atlas
```bash
git clone https://github.com/yourusername/ShivAI_Atlas.git
cd ShivAI_Atlas
```

Or download ZIP and extract.

### 2️⃣ Install Dependencies
```bash
scripts\install_dependencies.bat
```

Wait for installation to complete (~2 minutes).

---

## ▶️ Run Atlas (1 minute)

### Step 1: Start Backend
```bash
scripts\run_backend.bat
```

✅ You should see: `Server running on http://localhost:8000`

### Step 2: Start Frontend (New Terminal)
```bash
scripts\run_frontend.bat
```

✅ Browser opens automatically at `http://localhost:3000`

---

## 🎮 Try Your First Command (2 minutes)

### 1. Enable Permissions
1. Click **"Settings"** → **"Permissions"**
2. Enable these toggles:
   - ✅ **File Access**
   - ✅ **Keyboard/Mouse Control**
   - ✅ **Screen Capture**

### 2. Test Commands

#### Command 1: System Info
```
system info dikao
```
**Expected**: Shows CPU, RAM, disk usage

#### Command 2: Screenshot
```
screenshot lo
```
**Expected**: Takes screenshot, saves to generated_apps/

#### Command 3: Open App
```
calculator kholo
```
**Expected**: Opens Windows Calculator

#### Command 4: Desktop Organize
```
desktop organize karo
```
**Expected**: Organizes files into folders

---

## 🔥 Quick Tips

### Dry Run Mode
Test commands without executing:
```
desktop clean karo  # Type this
Click "Dry Run"     # Shows what will happen
Click "Execute"     # Actually run it
```

### Voice Input
Click the 🎤 microphone button and speak your command in Hindi or English.

### View Logs
- **Dashboard**: See real-time activity
- **Permissions**: View audit trail
- **File**: Check `logs/atlas.log`

---

## 📱 Android Setup (Optional, +3 minutes)

### 1. Install ADB
Download: https://developer.android.com/tools/releases/platform-tools
Extract to `C:\adb\`

### 2. Enable USB Debugging
On your Android:
1. **Settings** → **About Phone**
2. Tap **"Build Number"** 7 times
3. **Settings** → **Developer Options**
4. Enable **"USB Debugging"**

### 3. Connect Device
```bash
# Connect phone via USB
adb devices

# In Atlas UI:
Settings → Android → "Connect Device"
```

### 4. Test Android Command
```
phone unlock karo
```

---

## 🆘 Quick Troubleshooting

### Backend won't start?
```bash
# Check Python version
python --version  # Should be 3.11+

# Reinstall dependencies
pip install -r requirements.txt
```

### Frontend won't start?
```bash
# Check Node version
node --version  # Should be 16+

# Reinstall packages
cd frontend
npm install
```

### Permission denied?
- Go to **Permissions** page
- Enable required permission
- Try command again

### Port already in use?
```bash
# Kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID <process_id> /F
```

---

## 🎓 Learn More

### Example Commands

```bash
# File Operations
"desktop par naya folder banao Projects"
"temp files delete karo"
"Documents ka backup lo"

# PC Control
"volume badhao"
"notepad kholo"
"screenshot le kar desktop pe save karo"

# Android (if connected)
"phone ka screenshot lo"
"WhatsApp kholo phone mein"
"battery status check karo"

# Workflows
"morning routine chalo"
"backup workflow run karo"
```

### Full Documentation
- **README.md**: Complete features
- **DEPLOYMENT.md**: Detailed setup
- **PROJECT_SUMMARY.md**: Architecture

---

## ✅ Success Checklist

After 5 minutes, you should have:

- [x] Backend running (green text in terminal)
- [x] Frontend loaded (browser at localhost:3000)
- [x] Permissions enabled (at least 3)
- [x] First command executed successfully
- [x] Activity log showing results

---

## 🎉 You're Ready!

Atlas is now running! Try these next:

1. **Explore Workflows**: Pre-built automation routines
2. **Create Apps**: Generate Todo/Calculator apps
3. **Connect Android**: Control your phone from PC
4. **Set Schedules**: Automate daily tasks

---

## 🚨 Quick Reference Card

```
┌─────────────────────────────────────────┐
│         ShivAI Atlas Commands           │
├─────────────────────────────────────────┤
│ System:                                 │
│  • system info dikao                    │
│  • screenshot lo                        │
│  • volume badhao/kam karo               │
│                                         │
│ Files:                                  │
│  • desktop organize karo                │
│  • temp files clean karo                │
│  • backup lo                            │
│                                         │
│ Apps:                                   │
│  • calculator/notepad kholo             │
│  • chrome band karo                     │
│  • task manager kholo                   │
│                                         │
│ Android:                                │
│  • phone unlock karo                    │
│  • WhatsApp kholo                       │
│  • screenshot lo phone ka               │
│                                         │
│ Shortcuts:                              │
│  • Ctrl+Enter = Execute                 │
│  • 🎤 Button = Voice input              │
│  • Dry Run = Test first                 │
└─────────────────────────────────────────┘
```

---

**Need Help?** 
- Check logs in `logs/atlas.log`
- Open an issue on GitHub
- Read full docs in README.md

**Ready to build amazing automations!** 🚀
