@echo off
title NovaTech AI Customer Service Bot Launcher
echo ========================================================
echo   Starting NovaTech AI Customer Service Bot
echo ========================================================
echo.

cd /d "%~dp0"

REM Activate virtual environment
if not exist ".venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found in .venv!
    echo Please run: python -m venv .venv ^&^& .\.venv\Scripts\pip install -r requirements.txt
    pause
    exit /b 1
)

echo [*] Activating virtual environment...
call .\.venv\Scripts\activate.bat

echo [*] Starting FastAPI Backend on http://localhost:8000...
start "NovaTech Backend Server" cmd /k ".\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload"

timeout /t 2 >nul

echo [*] Starting Vite Frontend Dev Server on http://localhost:5173...
start "NovaTech Frontend Server" cmd /k "cd frontend && npm run dev"

timeout /t 3 >nul

echo [*] Opening application in default browser...
start http://localhost:5173

echo.
echo ========================================================
echo   Application successfully launched!
echo   - Chat Interface & Admin: http://localhost:5173
echo   - Production Unified URL: http://localhost:8000
echo   - API Health: http://localhost:8000/health
echo ========================================================
echo.
pause
