@echo off
setlocal enabledelayedexpansion
title WSN Energy-Harvesting Simulator - Launcher
echo ============================================================
echo   Starting WSN Energy Routing System (Offline Mode)
echo ============================================================
echo.

cd /d "%~dp0"

:: 1. Ensure Python Virtual Environment
if not exist ".venv\Scripts\python.exe" (
    echo [*] Creating Python virtual environment (.venv)...
    python -m venv .venv
    echo [*] Installing requirements...
    call .venv\Scripts\activate.bat
    pip install -r requirements.txt
)

:: 2. Ensure Frontend Dependencies
if not exist "frontend\node_modules" (
    echo [*] Installing frontend dependencies (npm install)...
    cd frontend
    call npm install
    cd ..
)

:: 3. Free busy ports 8000 and 3000 if left open by previous sessions
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000" ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":3000" ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)

echo [1/2] Starting FastAPI Backend on http://127.0.0.1:8000 ...
start "WSN-Backend" cmd /k ".venv\Scripts\activate.bat && python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000"

timeout /t 3 /nobreak >nul

echo [2/2] Starting React Frontend on http://localhost:3000 ...
start "WSN-Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ============================================================
echo   System launched successfully!
echo   - Web Dashboard: http://localhost:3000
echo   - Backend Docs:  http://127.0.0.1:8000/docs
echo ============================================================
echo Opening browser...
start http://localhost:3000
