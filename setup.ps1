# Setup script for Workplace Safety Monitoring Application - PowerShell
# For Windows PowerShell users

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "   Workplace Safety Monitoring - Setup" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Install Python dependencies
Write-Host "[1/4] Installing Python dependencies..." -ForegroundColor Yellow
try {
    pip install --user fastapi uvicorn[standard] sqlalchemy pyjwt aiosmtplib twilio sendgrid email-validator python-jose[cryptography] passlib[bcrypt] python-multipart httpx 2>&1 | Out-Null
    Write-Host "     ✓ Done!" -ForegroundColor Green
} catch {
    Write-Host "     ✗ ERROR: Failed to install Python dependencies" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host ""

# Step 2: Install Frontend dependencies
Write-Host "[2/4] Installing Frontend dependencies..." -ForegroundColor Yellow
try {
    Push-Location frontend
    npm install --legacy-peer-deps --silent 2>&1 | Out-Null
    Pop-Location
    Write-Host "     ✓ Done!" -ForegroundColor Green
} catch {
    Write-Host "     ✗ ERROR: Failed to install frontend dependencies" -ForegroundColor Red
    Pop-Location
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host ""

# Step 3: Create environment files
Write-Host "[3/4] Creating environment files..." -ForegroundColor Yellow

# Create backend .env
if (-not (Test-Path "backend\.env")) {
    $backendEnv = @"
# Backend Environment Configuration
JWT_SECRET_KEY=dev-secret-key-please-change-in-production
DATABASE_URL=sqlite:///./backend/workplace_safety.db
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=
SMTP_FROM_EMAIL=
SMTP_FROM_NAME=Workplace Safety Monitor
SENDGRID_API_KEY=
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_FROM_NUMBER=
"@
    $backendEnv | Out-File -FilePath "backend\.env" -Encoding UTF8
    Write-Host "     ✓ Created backend/.env" -ForegroundColor Green
} else {
    Write-Host "     ✓ backend/.env already exists" -ForegroundColor Green
}

# Create frontend .env
if (-not (Test-Path "frontend\.env")) {
    $frontendEnv = @"
# Frontend Environment Variables
VITE_API_URL=http://localhost:8000
VITE_GOOGLE_CLIENT_ID=YOUR_GOOGLE_CLIENT_ID_HERE
VITE_FACEBOOK_APP_ID=
"@
    $frontendEnv | Out-File -FilePath "frontend\.env" -Encoding UTF8
    Write-Host "     ✓ Created frontend/.env" -ForegroundColor Green
} else {
    Write-Host "     ✓ frontend/.env already exists" -ForegroundColor Green
}
Write-Host ""

# Step 4: Initialize database
Write-Host "[4/4] Initializing database..." -ForegroundColor Yellow
try {
    python setup_database.py
    Write-Host "     ✓ Done!" -ForegroundColor Green
} catch {
    Write-Host "     ✗ ERROR: Failed to initialize database" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host ""

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " Setup Complete!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "IMPORTANT: Before running the application, configure:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. backend\.env" -ForegroundColor White
Write-Host "   - Add SMTP credentials for email alerts" -ForegroundColor Gray
Write-Host "   - Or leave empty to run without email alerts" -ForegroundColor Gray
Write-Host ""
Write-Host "2. frontend\.env" -ForegroundColor White
Write-Host "   - Add your Google OAuth Client ID" -ForegroundColor Gray
Write-Host "   - Get it from: https://console.cloud.google.com/apis/credentials" -ForegroundColor Gray
Write-Host ""
Write-Host "After configuration, run: .\run.ps1" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Read-Host "Press Enter to exit"

