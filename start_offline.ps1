# WSN Energy Routing - PowerShell Offline Launcher
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Starting WSN Energy Routing System (Offline Mode)" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

$Root = $PSScriptRoot
Set-Location $Root

Write-Host "`n[1/2] Starting FastAPI Backend on http://127.0.0.1:8000..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$Root'; .\.venv\Scripts\activate; python -m uvicorn backend.main:app --port 8000"

Start-Sleep -Seconds 2

Write-Host "[2/2] Starting React Frontend on http://localhost:3000..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$Root\frontend'; npm run dev"

Write-Host "`n============================================================" -ForegroundColor Green
Write-Host "  System launched successfully!" -ForegroundColor Green
Write-Host "  - Web Dashboard: http://localhost:3000" -ForegroundColor Green
Write-Host "  - Backend Docs:  http://localhost:8000/docs" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green

Start-Process "http://localhost:3000"
