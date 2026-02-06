# 🚀 ShivAI Atlas - Complete Deployment Guide

## 📋 Prerequisites Checklist

### Required Software
- [ ] **Windows 10/11** (64-bit)
- [ ] **Python 3.11+** - [Download](https://www.python.org/downloads/)
- [ ] **Node.js 16+** - [Download](https://nodejs.org/)
- [ ] **Git** - [Download](https://git-scm.com/downloads)

### Optional (for Android control)
- [ ] **ADB Platform Tools** - [Download](https://developer.android.com/tools/releases/platform-tools)

### System Requirements
- **RAM**: Minimum 4GB, Recommended 8GB+
- **Storage**: 2GB free space
- **Network**: Internet for initial setup only

---

## 🔧 Step-by-Step Installation

### Step 1: Clone Repository
```bash
git clone https://github.com/yourusername/ShivAI_Atlas.git
cd ShivAI_Atlas
```

### Step 2: Install Python Dependencies
```bash
# Run installation script
scripts\install_dependencies.bat

# Or manually:
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Step 3: Install Frontend Dependencies
```bash
cd frontend
npm install
cd ..
```

### Step 4: Verify Installation
```bash
# Check Python
python --version  # Should be 3.11+

# Check Node
node --version    # Should be 16+

# Check packages
pip list | findstr fastapi
npm list react
```

---

## ⚙️ Configuration

### 1. Initial Configuration
On first run, Atlas creates `data/config.json`:
```json
{
  "permissions": {
    "can_access_files": false,
    "can_control_keyboard_mouse": false,
    "can_capture_screen": false,
    "can_control_android": false,
    "can_control_enterchat": false,
    "can_use_network": false,
    "can_use_ai_remote": false
  },
  "voice": {
    "enabled": true,
    "language": "hi-IN",
    "tts_rate": 150
  },
  "server": {
    "host": "0.0.0.0",
    "port": 8000,
    "debug": false
  }
}
```

### 2. Enable Permissions
Edit `data/config.json` and set required permissions to `true`:
```json
{
  "permissions": {
    "can_access_files": true,
    "can_control_keyboard_mouse": true,
    "can_capture_screen": true
  }
}
```

Or use the UI:
1. Start Atlas
2. Go to Settings > Permissions
3. Toggle permissions as needed

### 3. Android Setup (Optional)
```bash
# Download ADB Platform Tools
# Extract to C:\adb\

# Add to PATH
# Windows: System Properties > Environment Variables > Path
# Add: C:\adb\platform-tools

# Verify
adb version
```

Update config:
```json
{
  "android": {
    "enabled": true,
    "adb_path": "adb",
    "device_id": null
  }
}
```

### 4. EnterChat Integration (Optional)
If you have EnterChat vX running:
```json
{
  "enterchat": {
    "enabled": true,
    "api_url": "http://localhost:9000",
    "api_key": "your_api_key_here"
  }
}
```

---

## 🚀 Running Atlas

### Method 1: Using Scripts (Recommended)

#### Start Backend
```bash
scripts\run_backend.bat
```
✅ Server starts at: `http://localhost:8000`
✅ API docs at: `http://localhost:8000/docs`

#### Start Frontend (New Terminal)
```bash
scripts\run_frontend.bat
```
✅ UI available at: `http://localhost:3000`

### Method 2: Manual Start

#### Backend
```bash
cd backend
..\venv\Scripts\activate
python main.py
```

#### Frontend
```bash
cd frontend
npm run dev
```

---

## 🧪 Verification & Testing

### 1. Health Check
```bash
# Check backend health
curl http://localhost:8000/api/health

# Expected response:
{
  "status": "healthy",
  "version": "1.0.0",
  "agent": "ShivAI Atlas"
}
```

### 2. Test Commands

#### Via API
```bash
# Test simple command
curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d "{\"command\": \"system info dikao\", \"dry_run\": true}"
```

#### Via UI
1. Open `http://localhost:3000`
2. Enter command: "system info dikao"
3. Click "Dry Run" to test without execution
4. Click "Execute" to run

### 3. Test Permissions
1. Go to Permissions page
2. Enable "File Access"
3. Try command: "desktop organize karo"
4. Check audit log for activity

### 4. Test Android (if configured)
1. Connect Android device via USB
2. Enable USB debugging
3. Command: "phone unlock karo"
4. Check device control

---

## 🔍 Troubleshooting

### Backend Issues

#### Port Already in Use
```bash
# Find process using port 8000
netstat -ano | findstr :8000

# Kill process
taskkill /PID <process_id> /F
```

#### Module Not Found
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

#### Permission Errors
```bash
# Run as Administrator
# Right-click run_backend.bat > Run as administrator
```

### Frontend Issues

#### npm Install Fails
```bash
# Clear cache
npm cache clean --force

# Delete node_modules
rmdir /s /q node_modules
rm package-lock.json

# Reinstall
npm install
```

#### Port 3000 in Use
```bash
# Change port in vite.config.ts
server: {
  port: 3001
}
```

### Android Issues

#### Device Not Found
```bash
# Check USB debugging
adb devices

# If unauthorized, accept prompt on phone
# If offline, restart ADB
adb kill-server
adb start-server
```

#### Permission Denied
```bash
# Reconnect device
adb kill-server
adb start-server
adb devices
```

---

## 📊 Monitoring & Logs

### Log Locations
```
logs/
├── atlas.log           # Main application log
├── agents.log          # Agent activity
├── automation.log      # Automation actions
├── security.log        # Security events
└── api.log            # API requests
```

### View Logs
```bash
# Real-time tail
Get-Content logs\atlas.log -Wait -Tail 50

# Search logs
findstr "ERROR" logs\atlas.log
```

### Audit Trail
```
data/audit_log.jsonl    # All actions logged here
```

---

## 🔐 Security Best Practices

### 1. Permission Management
- ✅ Enable only required permissions
- ✅ Use "Ask Every Time" for sensitive actions
- ✅ Review audit log regularly
- ❌ Don't enable all permissions by default

### 2. Network Security
- ✅ Backend runs on localhost by default
- ✅ Use firewall for external access
- ✅ Set strong API keys if exposing
- ❌ Don't expose to public internet

### 3. Data Protection
- ✅ All data stored locally
- ✅ No cloud sync by default
- ✅ Encrypted sensitive data
- ❌ Don't share config.json

### 4. Android Security
- ✅ USB debugging only when needed
- ✅ Trust only your PC
- ✅ Disable after use
- ❌ Don't leave debugging on

---

## 🔄 Updates & Maintenance

### Update Atlas
```bash
# Pull latest changes
git pull origin main

# Update Python dependencies
pip install -r requirements.txt --upgrade

# Update frontend dependencies
cd frontend
npm update
```

### Database Maintenance
```bash
# Backup database
copy data\db\atlas.db data\db\atlas.db.backup

# Vacuum database (optimize)
sqlite3 data\db\atlas.db "VACUUM;"
```

### Clean Logs
```bash
# Archive old logs
move logs\*.log logs\archive\

# Clean temp files
python -c "from backend.automation.file_actions import file_actions; file_actions.clean_temp_files()"
```

---

## 🌐 Production Deployment

### For Personal Use

#### Create Desktop Shortcuts
```batch
@echo off
cd C:\path\to\ShivAI_Atlas
start scripts\run_backend.bat
timeout /t 3
start scripts\run_frontend.bat
```

#### Auto-start on Windows Boot
1. Press `Win + R`
2. Type `shell:startup`
3. Create shortcut to start script
4. Enable "Run as administrator"

### For Team/Server Use

#### Use Production Server
```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn backend.main:app \
  --workers 4 \
  --bind 0.0.0.0:8000 \
  --timeout 120
```

#### Build Frontend for Production
```bash
cd frontend
npm run build

# Serve with nginx or serve static files
npx serve -s dist -l 3000
```

#### Set Environment Variables
```bash
# .env file
ATLAS_ENV=production
ATLAS_DEBUG=false
ATLAS_LOG_LEVEL=INFO
```

---

## 📞 Support & Resources

### Documentation
- **README.md**: Complete feature documentation
- **PROJECT_SUMMARY.md**: Architecture overview
- **API Docs**: http://localhost:8000/docs

### Community
- **GitHub Issues**: Bug reports & feature requests
- **Discussions**: Q&A and community support

### Getting Help
1. Check logs in `logs/` directory
2. Review audit log for action history
3. Test with dry run mode
4. Check GitHub issues for similar problems
5. Create new issue with:
   - Error message
   - Log excerpt
   - Steps to reproduce
   - System info

---

## ✅ Post-Installation Checklist

After successful installation, verify:

- [ ] Backend running on port 8000
- [ ] Frontend accessible at localhost:3000
- [ ] API docs viewable at /docs
- [ ] Database created in data/db/
- [ ] Logs being written to logs/
- [ ] Permissions configurable in UI
- [ ] Test command executes successfully
- [ ] Android device connects (if applicable)
- [ ] Audit log recording actions

---

## 🎯 Quick Commands Reference

```bash
# Installation
scripts\install_dependencies.bat

# Run
scripts\run_backend.bat
scripts\run_frontend.bat

# Test
curl http://localhost:8000/api/health

# Update
git pull && pip install -r requirements.txt --upgrade

# Logs
Get-Content logs\atlas.log -Wait -Tail 50

# Backup
copy data\db\atlas.db backups\atlas_%date%.db
```

---

**Deployment Status**: ✅ Ready for Production
**Last Updated**: 2024
**Support**: GitHub Issues

---

Need help? Check our [troubleshooting guide](#-troubleshooting) or [open an issue](https://github.com/yourusername/ShivAI_Atlas/issues).
