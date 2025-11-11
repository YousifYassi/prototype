@echo off
REM Workplace Safety Monitoring Application - Windows Batch Script
REM Quick launcher for Windows users

echo ============================================================
echo    Workplace Safety Monitoring Application
echo ============================================================
echo.

REM Check if backend .env exists
if not exist "backend\.env" (
    echo ERROR: backend/.env not found!
    echo Please run: setup.bat
    echo.
    pause
    exit /b 1
)

REM Check if frontend .env exists
if not exist "frontend\.env" (
    echo ERROR: frontend/.env not found!
    echo Please run: setup.bat
    echo.
    pause
    exit /b 1
)

echo Starting Backend API on http://localhost:8000
echo Starting Frontend on http://localhost:3000
echo.
echo Press Ctrl+C to stop both services
echo.

REM Start backend in new window
start "Workplace Safety - Backend" cmd /k "python start_backend.py"

REM Wait 3 seconds for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend in new window
start "Workplace Safety - Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ============================================================
echo  Backend: http://localhost:8000
echo  Frontend: http://localhost:3000
echo  API Docs: http://localhost:8000/docs
echo ============================================================
echo.
echo Both services are running in separate windows.
echo Close those windows to stop the services.
echo.
pause

