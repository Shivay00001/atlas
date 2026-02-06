# 🚀 ShivAI Atlas

**Local AI Agent OS** - A powerful, privacy-first automation platform that runs entirely on your PC with deep PC + Android integration.

## ✨ Features

### 🎯 Core Capabilities

- **Multi-Agent Brain**
  - Planner Agent: Intelligent task decomposition
  - Executor Agent: Reliable action execution
  - Safety Agent: Permission-based access control
  - Memory Agent: Long-term learning and preferences

- **PC Automation** (500+ actions)
  - Application control (open, close, switch)
  - File operations (create, delete, organize)
  - Keyboard & mouse automation
  - System control (volume, shutdown, etc.)
  - Screenshot capture
  - Desktop organization

- **Android Control** (ADB-based)
  - Device connection and management
  - App launching and control
  - Screen capture
  - Touch and swipe gestures
  - Text input
  - Phone unlock automation

- **EnterChat Integration**
  - Unified inbox from 80+ messaging apps
  - Send/receive messages across platforms
  - WhatsApp, Telegram, and more
  - Message search and summarization
  - Bulk messaging capabilities

- **Voice + Text Interface**
  - Hindi + English (Hinglish) support
  - Speech recognition
  - Text-to-speech responses
  - Natural language understanding

- **Workflow Engine**
  - Pre-built workflows (Morning Routine, Backup, etc.)
  - Custom workflow creation
  - Scheduled execution
  - Usage-based suggestions

- **App Builder**
  - Generate GUI apps from templates
  - Todo, Calculator, Notes, and more
  - Python Tkinter-based
  - Customizable layouts

- **User-Consent Model**
  - Explicit permission for every capability
  - "Ask every time" option
  - Complete audit log
  - Revokable permissions

## 🛠️ Installation

### Prerequisites

- **Windows 10/11** (primary support)
- **Python 3.11+** ([Download](https://www.python.org/downloads/))
- **Node.js 16+** ([Download](https://nodejs.org/))
- **ADB Platform Tools** (for Android control) ([Download](https://developer.android.com/tools/releases/platform-tools))

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/ShivAI_Atlas.git
   cd ShivAI_Atlas
   ```

2. **Install dependencies**
   ```bash
   scripts\install_dependencies.bat
   ```

3. **Start the backend**
   ```bash
   scripts\run_backend.bat
   ```

4. **Start the frontend** (in a new terminal)
   ```bash
   scripts\run_frontend.bat
   ```

5. **Access the dashboard**
   - Open browser: `http://localhost:3000`
   - Backend API: `http://localhost:8000`
   - API Docs: `http://localhost:8000/docs`

## 📱 Android Setup

1. **Enable Developer Options** on your Android device
   - Go to Settings > About Phone
   - Tap "Build Number" 7 times

2. **Enable USB Debugging**
   - Settings > Developer Options > USB Debugging

3. **Connect your device**
   - Connect via USB cable
   - Accept the "Allow USB Debugging" prompt

4. **Verify connection**
   - Open terminal: `adb devices`
   - You should see your device listed

5. **Connect in Atlas**
   - Go to Settings > Android
   - Click "Connect Device"

## 🔐 Permissions Setup

Atlas uses a consent-based permission model. On first use:

1. Go to **Settings > Permissions**
2. Review each permission:
   - **Files**: Read/write files and folders
   - **Keyboard/Mouse**: Control input devices
   - **Screen Capture**: Take screenshots
   - **Android**: Control connected devices
   - **EnterChat**: Access messaging apps
   - **Network**: Make external requests
   - **AI Remote**: Use cloud AI services

3. Enable permissions as needed
4. Configure "Ask Every Time" for sensitive actions

## 💬 Command Examples

### PC Automation
```
"Desktop organize karo"
"Screenshot lo aur save karo"
"Notepad kholo"
"Calculator chalo"
"Volume badhao"
"System info dikao"
```

### File Operations
```
"Desktop par naya folder banao 'Projects'"
"Documents folder clean karo"
"Important files ka backup lo"
"temp files delete karo"
```

### Android Control
```
"Phone unlock karo"
"WhatsApp kholo phone mein"
"Phone ka screenshot lo"
"Battery status check karo"
```

### Messaging
```
"Rahul ko WhatsApp pe message bhejo 'Meeting at 5pm'"
"Telegram pe Team channel ke last 20 messages dikao"
"Unread messages check karo"
```

### Workflows
```
"Morning routine chalo"
"Backup workflow execute karo"
"Productivity setup karo"
```

## 🏗️ Architecture

```
ShivAI_Atlas/
├── backend/
│   ├── main.py                 # FastAPI server
│   ├── core/
│   │   ├── config.py          # Configuration management
│   │   ├── logger.py          # Logging system
│   │   ├── permissions.py     # Access control
│   │   └── memory.py          # Long-term memory
│   ├── agents/
│   │   ├── planner_agent.py   # Task planning
│   │   ├── executor_agent.py  # Action execution
│   │   ├── safety_agent.py    # Security checks
│   │   └── memory_agent.py    # Memory management
│   └── automation/
│       ├── pc_actions.py      # PC control
│       ├── file_actions.py    # File operations
│       ├── android_bridge.py  # Android control
│       ├── enterchat_connector.py  # Messaging
│       ├── workflow_engine.py  # Workflows
│       └── app_builder.py     # App generation
├── frontend/
│   └── src/
│       ├── pages/
│       │   ├── Dashboard.tsx       # Main interface
│       │   ├── Permissions.tsx     # Permission control
│       │   ├── Workflows.tsx       # Workflow management
│       │   └── Settings.tsx        # Configuration
│       └── components/
├── data/
│   ├── config.json            # User configuration
│   ├── db/
│   │   └── atlas.db          # SQLite database
│   └── templates/            # App & workflow templates
└── scripts/
    ├── install_dependencies.bat
    ├── run_backend.bat
    └── run_frontend.bat
```

## 🔧 Configuration

Configuration is stored in `data/config.json`:

```json
{
  "permissions": {
    "can_access_files": false,
    "can_control_keyboard_mouse": false,
    "can_capture_screen": false,
    "can_control_android": false,
    "can_control_enterchat": false
  },
  "android": {
    "enabled": false,
    "adb_path": "adb",
    "device_id": null
  },
  "enterchat": {
    "enabled": false,
    "api_url": "http://localhost:9000",
    "api_key": null
  }
}
```

## 📊 Database Schema

### Memories
- `id`, `key`, `value`, `category`, `metadata`, `created_at`, `updated_at`

### Workflows
- `id`, `name`, `description`, `steps`, `category`, `enabled`, `usage_count`, `last_used`

### Usage Stats
- `id`, `command`, `agent`, `success`, `duration_ms`, `metadata`, `timestamp`

### Conversations
- `id`, `user_input`, `agent_response`, `intent`, `confidence`, `metadata`, `timestamp`

## 🔒 Security

- **Local-First**: All core automation runs locally
- **Permission-Based**: Explicit consent required for every capability
- **Audit Log**: Complete history of all actions
- **No Cloud Dependency**: Works offline for PC automation
- **Encrypted Storage**: Sensitive data encrypted at rest

## 🐛 Troubleshooting

### Backend won't start
- Ensure Python 3.11+ is installed
- Activate virtual environment: `venv\Scripts\activate`
- Check port 8000 is not in use

### Android connection fails
- Verify USB debugging is enabled
- Check ADB is in system PATH
- Try `adb kill-server` then `adb start-server`
- Accept USB debugging prompt on phone

### Permissions not working
- Check Settings > Permissions
- Enable required permissions
- Restart backend after permission changes

### EnterChat not connecting
- Ensure EnterChat vX is running
- Verify API URL in settings
- Check API key if required

## 📝 Development

### Running Tests
```bash
cd backend
python -m pytest tests/
```

### Code Style
```bash
black backend/
flake8 backend/
```

### Adding New Actions

1. Add method to appropriate module (e.g., `pc_actions.py`)
2. Add intent patterns to `planner_agent.py`
3. Add plan creation logic in `create_plan()`
4. Test with dry run mode

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- Built with FastAPI, React, and Python
- Inspired by ChatGPT Atlas and Comet
- Powered by open-source libraries

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/ShivAI_Atlas/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/ShivAI_Atlas/discussions)
- **Email**: support@yourmail.com

## 🚦 Roadmap

- [ ] macOS and Linux support
- [ ] iOS device control
- [ ] Cloud sync (optional)
- [ ] Plugin system
- [ ] Natural language workflow creation
- [ ] Advanced AI integration
- [ ] Multi-device orchestration
- [ ] Voice-only mode
- [ ] Task scheduling UI
- [ ] Performance monitoring dashboard

---

**Made with ❤️ for productivity and automation**

**ShivAI Atlas** - Your Local AI Agent OS
