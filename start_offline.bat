@echo off
title WSN Energy Routing - Offline Launcher
echo ============================================================
echo   Starting WSN Energy Routing System (Offline Mode)
echo ============================================================
echo.

cd /d %~dp0

echo [1/2] Starting FastAPI Backend on http://127.0.0.1:8000 ...
start "WSN-Backend" cmd /k ".venv\Scripts\python.exe -m uvicorn backend.main:app --port 8000"

timeout /t 3 /nobreak >nul

echo [2/2] Starting React Frontend on http://localhost:3000 ...
start "WSN-Frontend" cmd /k "cd frontend & npm run dev"

echo.
echo ============================================================
echo   System launched successfully!
echo   - Web Dashboard: http://localhost:3000
echo   - Backend Docs:  http://localhost:8000/docs
echo ============================================================
echo Opening browser...
start http://localhost:3000
