@echo off
echo ================================================
echo ShivAI Atlas - Starting Backend Server
echo ================================================
echo.

:: Activate virtual environment
call venv\Scripts\activate.bat

:: Navigate to backend directory
cd backend

:: Start FastAPI server
echo Starting FastAPI server on http://localhost:8000
echo Press Ctrl+C to stop the server
echo.
python main.py

pause
