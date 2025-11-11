@echo off
REM Setup script for Workplace Safety Monitoring Application

echo ============================================================
echo    Workplace Safety Monitoring - Setup
echo ============================================================
echo.

echo [1/4] Installing Python dependencies...
pip install --user -q fastapi uvicorn[standard] sqlalchemy pyjwt aiosmtplib twilio sendgrid email-validator python-jose[cryptography] passlib[bcrypt] python-multipart httpx
if errorlevel 1 (
    echo ERROR: Failed to install Python dependencies
    pause
    exit /b 1
)
echo      Done!
echo.

echo [2/4] Installing Frontend dependencies...
cd frontend
call npm install --legacy-peer-deps --silent
if errorlevel 1 (
    echo ERROR: Failed to install frontend dependencies
    pause
    exit /b 1
)
cd ..
echo      Done!
echo.

echo [3/4] Creating environment files...

REM Create backend .env
if not exist "backend\.env" (
    (
        echo # Backend Environment Configuration
        echo JWT_SECRET_KEY=dev-secret-key-please-change-in-production
        echo DATABASE_URL=sqlite:///./backend/workplace_safety.db
        echo SMTP_HOST=smtp.gmail.com
        echo SMTP_PORT=587
        echo SMTP_USERNAME=
        echo SMTP_PASSWORD=
        echo SMTP_FROM_EMAIL=
        echo SMTP_FROM_NAME=Workplace Safety Monitor
        echo SENDGRID_API_KEY=
        echo TWILIO_ACCOUNT_SID=
        echo TWILIO_AUTH_TOKEN=
        echo TWILIO_FROM_NUMBER=
    ) > backend\.env
    echo      Created backend/.env
) else (
    echo      backend/.env already exists
)

REM Create frontend .env
if not exist "frontend\.env" (
    (
        echo # Frontend Environment Variables
        echo VITE_API_URL=http://localhost:8000
        echo VITE_GOOGLE_CLIENT_ID=YOUR_GOOGLE_CLIENT_ID_HERE
        echo VITE_FACEBOOK_APP_ID=
    ) > frontend\.env
    echo      Created frontend/.env
) else (
    echo      frontend/.env already exists
)
echo      Done!
echo.

echo [4/4] Initializing database...
python setup_database.py
if errorlevel 1 (
    echo ERROR: Failed to initialize database
    pause
    exit /b 1
)
echo      Done!
echo.

echo ============================================================
echo  Setup Complete!
echo ============================================================
echo.
echo IMPORTANT: Before running the application, configure:
echo.
echo 1. backend\.env
echo    - Add SMTP credentials for email alerts
echo    - Or leave empty to run without email alerts
echo.
echo 2. frontend\.env
echo    - Add your Google OAuth Client ID
echo    - Get it from: https://console.cloud.google.com/apis/credentials
echo.
echo After configuration, run: run.bat
echo ============================================================
echo.
pause

