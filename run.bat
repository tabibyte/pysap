@echo off
echo Starting Terminal Audio Player...
echo.

REM Check if virtual environment exists
if not exist ".venv\Scripts\python.exe" (
    echo Error: Virtual environment not found!
    echo Please run: python -m venv .venv
    echo Then: .venv\Scripts\pip install -r requirements.txt
    pause
    exit /b 1
)

REM Run the audio player
.venv\Scripts\python.exe main.py %*

pause
