# Running the Workplace Safety Monitoring Application

## 🚀 Quick Run Instructions

### First Time Setup

1. **Install Dependencies:**
```bash
# Python dependencies
pip install -r requirements.txt
pip install -r backend/requirements.txt

# Frontend dependencies
cd frontend && npm install && cd ..
```

2. **Configure Environment:**
```bash
# Backend
cp backend/.env.example backend/.env
# Edit backend/.env with your credentials

# Frontend
cp frontend/.env.example frontend/.env
# Edit frontend/.env with your Google Client ID
```

3. **Initialize Database:**
```bash
python setup_database.py
```

4. **Verify Setup:**
```bash
python check_setup.py
```

### Running the Application

Open **TWO terminals**:

**Terminal 1 - Backend:**
```bash
python start_backend.py
```
Wait for: `Application startup complete.`

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```
Wait for: `Local: http://localhost:3000/`

### Access the Application

1. **Frontend:** http://localhost:3000
2. **Backend API:** http://localhost:8000
3. **API Docs:** http://localhost:8000/docs

---

## 📋 Minimal Configuration

### Backend (.env)
```env
JWT_SECRET_KEY=my-super-secret-key-change-this
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your.email@gmail.com
SMTP_PASSWORD=your-gmail-app-password
SMTP_FROM_EMAIL=your.email@gmail.com
```

### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000
VITE_GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
```

---

## 🔑 Getting Required Credentials

### Google OAuth Client ID

1. Go to: https://console.cloud.google.com/
2. Create project or select existing
3. Enable Google+ API
4. Credentials → Create Credentials → OAuth client ID
5. Web application
6. Authorized origins: `http://localhost:3000`
7. Copy Client ID

### Gmail App Password

1. Go to: https://myaccount.google.com/apppasswords
2. Select "Mail" and "Other"
3. Generate password
4. Copy 16-character password
5. Use in `SMTP_PASSWORD`

---

## ✅ Usage Flow

1. **Login** → Click "Continue with Google"
2. **Settings** → Add email address, save
3. **Upload** → Select video file, upload
4. **Dashboard** → Monitor processing status
5. **Email** → Receive alert if unsafe action detected

---

## 🐛 Quick Troubleshooting

**Backend won't start:**
```bash
# Check if port in use
lsof -i :8000

# Kill if needed
kill -9 <PID>
```

**Frontend won't start:**
```bash
# Check if port in use
lsof -i :3000

# Try different port
vite --port 3001
```

**Can't login:**
- Verify Google Client ID is correct
- Check authorized origins in Google Console
- Clear browser cookies

**No emails:**
- Verify Gmail App Password (not regular password)
- Check spam folder
- Look at backend terminal for errors

---

## 🛑 Stopping the Application

Press `Ctrl+C` in both terminals to stop.

---

## 📖 More Information

- Detailed Setup: `WORKPLACE_SAFETY_APP_SETUP.md`
- Quick Start: `QUICK_START.md`
- User Guide: `APPLICATION_README.md`
- Project Summary: `PROJECT_SUMMARY.md`

