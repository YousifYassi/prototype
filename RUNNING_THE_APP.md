# Running the Application - Quick Reference

Multiple options to run the Workplace Safety Monitoring application with a single command!

## 🚀 Quick Start Options

### Option 1: Windows Batch File (Recommended for Windows)

**First time setup:**
```cmd
setup.bat
```

**Run the application:**
```cmd
run.bat
```

### Option 2: PowerShell Script

**First time setup:**
```powershell
.\setup.ps1
```

**Run the application:**
```powershell
.\run.ps1
```

### Option 3: Makefile (For Git Bash, WSL, or MinGW users)

**First time setup:**
```bash
make full-setup
```

**Run the application:**
```bash
make run
```

**Other useful make commands:**
```bash
make help           # Show all available commands
make install        # Install dependencies only
make check          # Verify setup
make run-backend    # Run backend only
make run-frontend   # Run frontend only
make stop           # Stop all services
make clean          # Clean generated files
```

## 📋 What Each Setup Script Does

All setup scripts perform the same steps:

1. ✅ Install Python dependencies (FastAPI, SQLAlchemy, etc.)
2. ✅ Install Frontend dependencies (React, TypeScript, etc.)
3. ✅ Create environment configuration files
4. ✅ Initialize the database

## 🎯 After Setup

Before running the application, you must configure:

### 1. Google OAuth Client ID (Required for Login)

1. Go to: https://console.cloud.google.com/apis/credentials
2. Create OAuth 2.0 Client ID
3. Add authorized origin: `http://localhost:3000`
4. Copy the Client ID
5. Edit `frontend/.env` and replace `YOUR_GOOGLE_CLIENT_ID_HERE`

### 2. Email Alerts (Optional)

Edit `backend/.env` and add your Gmail credentials:
```env
SMTP_USERNAME=your.email@gmail.com
SMTP_PASSWORD=your-16-char-app-password
SMTP_FROM_EMAIL=your.email@gmail.com
```

Get Gmail App Password: https://myaccount.google.com/apppasswords

## 🌐 Access Points

Once running:
- **Frontend (Main App):** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs

## 🛑 Stopping the Application

### Windows Batch/PowerShell:
- Close the two windows that opened (Backend and Frontend)

### Makefile:
```bash
make stop
```

Or press `Ctrl+C` in the terminals

## 🔧 Troubleshooting

**"ERROR: backend/.env not found"**
- Run the setup script first: `setup.bat` or `.\setup.ps1` or `make full-setup`

**"Port already in use"**
- Kill existing processes:
  ```powershell
  # Kill backend
  Get-Process | Where-Object {$_.Path -like "*python*"} | Stop-Process
  
  # Kill frontend
  Get-Process | Where-Object {$_.ProcessName -like "*node*"} | Stop-Process
  ```

**"Login doesn't work"**
- Make sure you've added your Google Client ID to `frontend/.env`
- Check that authorized origins include `http://localhost:3000`

**"Email alerts not working"**
- Verify SMTP credentials in `backend/.env`
- Use Gmail App Password (not regular password)
- Check spam folder

## 📖 Full Documentation

For detailed setup and usage:
- **Quick Start:** `QUICK_START.md`
- **Complete Setup:** `WORKPLACE_SAFETY_APP_SETUP.md`
- **User Guide:** `APPLICATION_README.md`

## 💡 Tips

- Run `make check` or `python check_setup.py` to verify your setup
- Both backend and frontend will auto-reload when you make code changes
- Check the console windows for error messages if something doesn't work

