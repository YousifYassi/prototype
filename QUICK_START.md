# Quick Start Guide - Workplace Safety Monitoring

Get the application up and running in 15 minutes!

## ⚡ Prerequisites

- Python 3.8+
- Node.js 16+
- pip and npm installed
- Google account (for OAuth login)

## 🚀 Step-by-Step Setup

### 1. Install Dependencies (5 minutes)

```bash
# Install Python dependencies
pip install -r requirements.txt
pip install -r backend/requirements.txt

# Install frontend dependencies
cd frontend
npm install
cd ..
```

### 2. Setup Environment (3 minutes)

**Backend Configuration:**
```bash
# Copy example and edit
cp backend/.env.example backend/.env
nano backend/.env  # or use any text editor
```

Minimum required configuration in `backend/.env`:
```env
JWT_SECRET_KEY=your-long-random-secret-key-here

# For Gmail alerts (get App Password from Google Account settings)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-16-char-app-password
SMTP_FROM_EMAIL=your-email@gmail.com
```

**Frontend Configuration:**
```bash
cd frontend
cp .env.example .env
nano .env  # Add your Google Client ID
```

Get Google Client ID from: https://console.cloud.google.com/apis/credentials

Minimum required in `frontend/.env`:
```env
VITE_API_URL=http://localhost:8000
VITE_GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
```

### 3. Initialize Database (1 minute)

```bash
python setup_database.py
```

### 4. Verify Setup (1 minute)

```bash
python check_setup.py
```

Fix any issues reported before proceeding.

### 5. Start the Application (2 minutes)

**Terminal 1 - Backend:**
```bash
python start_backend.py
```

Wait for: `Uvicorn running on http://0.0.0.0:8000`

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Wait for: `Local: http://localhost:3000/`

### 6. Use the Application (3 minutes)

1. **Login:**
   - Open http://localhost:3000
   - Click "Continue with Google"
   - Sign in with your Google account

2. **Configure Alerts:**
   - Click "Settings" in navigation
   - Enter your email address
   - Enable email notifications
   - Click "Save Configuration"

3. **Upload Video:**
   - Click "Upload Video"
   - Select a video file (MP4, AVI, MOV)
   - Click "Upload & Analyze"
   - Go to Dashboard to see status

4. **Check Results:**
   - Dashboard shows processing status
   - If unsafe actions detected, you'll receive email alert
   - Check your inbox (including spam folder)

## 🎯 Test with Sample Video

If you don't have a test video, you can use any dashcam footage or workplace video. The system will analyze it for unsafe actions.

## ⚠️ Troubleshooting

**Backend won't start:**
- Check if port 8000 is already in use
- Verify all Python dependencies installed
- Check backend/.env file exists and is configured

**Frontend won't start:**
- Check if port 3000 is in use
- Run `npm install` in frontend directory
- Verify frontend/.env has Google Client ID

**Login doesn't work:**
- Verify Google Client ID is correct
- Check authorized origins in Google Console include http://localhost:3000
- Clear browser cookies and try again

**Email alerts not working:**
- Verify SMTP credentials in backend/.env
- Check Gmail App Password (not regular password)
- Look for errors in backend terminal

**Model not found:**
```bash
# Train the model first (this takes 1-2 hours)
python train.py

# Or download pre-trained model if available
```

## 📚 Next Steps

1. **Customize Detection:**
   - Edit `config.yaml` to adjust unsafe action types
   - Modify confidence threshold for alerts

2. **Add SMS Alerts:**
   - Sign up for Twilio
   - Add credentials to backend/.env
   - Enable SMS in Settings

3. **Deploy to Production:**
   - See `WORKPLACE_SAFETY_APP_SETUP.md` for production deployment guide

## 🆘 Need Help?

- **Setup Issues:** Check `WORKPLACE_SAFETY_APP_SETUP.md`
- **Application Details:** See `APPLICATION_README.md`
- **Model Training:** Refer to main `README.md`

---

**You're all set! Enjoy using the Workplace Safety Monitoring system! 🎉**

