# Workplace Safety Monitoring Application - PowerShell Launcher
# For Windows PowerShell users

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "   Workplace Safety Monitoring Application" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Check if backend .env exists
if (-not (Test-Path "backend\.env")) {
    Write-Host "ERROR: backend/.env not found!" -ForegroundColor Red
    Write-Host "Please run: .\setup.ps1" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if frontend .env exists
if (-not (Test-Path "frontend\.env")) {
    Write-Host "ERROR: frontend/.env not found!" -ForegroundColor Red
    Write-Host "Please run: .\setup.ps1" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Starting Backend API on http://localhost:8000" -ForegroundColor Green
Write-Host "Starting Frontend on http://localhost:3000" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop both services" -ForegroundColor Yellow
Write-Host ""

# Start backend in new window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python start_backend.py" -WindowStyle Normal

# Wait 3 seconds for backend to start
Start-Sleep -Seconds 3

# Start frontend in new window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev" -WindowStyle Normal

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " Backend:  http://localhost:8000" -ForegroundColor White
Write-Host " Frontend: http://localhost:3000" -ForegroundColor White
Write-Host " API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Both services are running in separate windows." -ForegroundColor Green
Write-Host "Close those windows to stop the services." -ForegroundColor Yellow
Write-Host ""
Read-Host "Press Enter to exit this launcher window"

