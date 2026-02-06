@echo off
echo ================================================
echo ShivAI Atlas - Installation Script
echo ================================================
echo.

:: Check Python version
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.11+ from https://www.python.org/
    pause
    exit /b 1
)

echo [1/5] Creating virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

echo.
echo [2/5] Upgrading pip...
python -m pip install --upgrade pip

echo.
echo [3/5] Installing backend dependencies...
pip install fastapi uvicorn pydantic
pip install pyautogui psutil keyboard mouse
pip install requests aiohttp websockets
pip install pyttsx3 SpeechRecognition
pip install python-dotenv
pip install Pillow

echo.
echo [4/5] Installing development tools...
pip install pytest black flake8

echo.
echo [5/5] Setting up frontend...
cd frontend
if exist package.json (
    echo Installing npm packages...
    call npm install
    if errorlevel 1 (
        echo WARNING: npm install failed. Make sure Node.js is installed.
    )
)
cd ..

echo.
echo ================================================
echo Installation Complete!
echo ================================================
echo.
echo Next steps:
echo 1. Configure settings in data/config.json
echo 2. Run backend: scripts\run_backend.bat
echo 3. Run frontend: scripts\run_frontend.bat
echo.
echo For Android control, ensure ADB is installed:
echo https://developer.android.com/tools/releases/platform-tools
echo.
pause
