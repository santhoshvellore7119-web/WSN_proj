# WSN Energy Routing - PowerShell Offline Launcher
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Starting WSN Energy Routing System (Offline Mode)" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

$Root = $PSScriptRoot
Set-Location $Root

# 1. Ensure Python Virtual Environment
if (-not (Test-Path "$Root\.venv\Scripts\python.exe")) {
    Write-Host "[*] Creating Python virtual environment (.venv)..." -ForegroundColor Yellow
    python -m venv .venv
    Write-Host "[*] Installing requirements..." -ForegroundColor Yellow
    & "$Root\.venv\Scripts\pip.exe" install -r requirements.txt
}

# 2. Ensure Frontend Dependencies
if (-not (Test-Path "$Root\frontend\node_modules")) {
    Write-Host "[*] Installing frontend dependencies (npm install)..." -ForegroundColor Yellow
    Push-Location "$Root\frontend"
    npm install
    Pop-Location
}

# 3. Free busy ports 8000 and 3000 if occupied
Get-NetTCPConnection -LocalPort 8000, 3000 -ErrorAction SilentlyContinue | ForEach-Object {
    Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue
}

Write-Host "`n[1/2] Starting FastAPI Backend on http://127.0.0.1:8000..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$Root'; .\.venv\Scripts\activate; python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000"

Start-Sleep -Seconds 2

Write-Host "[2/2] Starting React Frontend on http://localhost:3000..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$Root\frontend'; npm run dev"

Write-Host "`n============================================================" -ForegroundColor Green
Write-Host "  System launched successfully!" -ForegroundColor Green
Write-Host "  - Web Dashboard: http://localhost:3000" -ForegroundColor Green
Write-Host "  - Backend Docs:  http://127.0.0.1:8000/docs" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green

Start-Process "http://localhost:3000"
