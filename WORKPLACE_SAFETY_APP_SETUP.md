# Workplace Safety Monitoring Application - Setup Guide

Complete setup guide for the AI-powered workplace safety monitoring application with video analysis, email/SMS alerts, and React frontend.

## 🎯 Overview

This application detects unsafe actions in workplace videos using AI and sends real-time alerts via email and SMS. It includes:

- **Backend API** (FastAPI) - Video processing, authentication, alerts
- **Frontend** (React) - User interface with Google/Facebook OAuth
- **AI Model** - Pre-trained action detection model
- **Notifications** - Email (SMTP/SendGrid) and SMS (Twilio)

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+ and npm
- GPU (recommended) with CUDA support for faster processing
- Google OAuth credentials (for login)
- Email service (Gmail or SendGrid) for email alerts
- Twilio account (optional, for SMS alerts)

## 🚀 Part 1: Backend Setup

### Step 1: Install Python Dependencies

```bash
# Install main project dependencies
pip install -r requirements.txt

# Install backend-specific dependencies
pip install -r backend/requirements.txt
```

### Step 2: Initialize Database

```bash
# Create database tables
python -c "from backend.database import init_db; init_db()"
```

### Step 3: Configure Backend Environment

Create `backend/.env` file:

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env` and configure:

```env
# JWT Secret (generate a strong random key)
JWT_SECRET_KEY=your-very-long-random-secret-key-here

# Database
DATABASE_URL=sqlite:///./backend/workplace_safety.db

# === Email Configuration (choose one) ===

# Option 1: Gmail SMTP
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password  # See Gmail setup below
SMTP_FROM_EMAIL=your-email@gmail.com
SMTP_FROM_NAME=Workplace Safety Monitor

# Option 2: SendGrid (recommended for production)
SENDGRID_API_KEY=your-sendgrid-api-key

# === SMS Configuration (Twilio) ===
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_FROM_NUMBER=+1234567890
```

#### Gmail Setup for Email Alerts

1. Go to your Google Account settings
2. Enable 2-factor authentication
3. Generate an "App Password" for email:
   - Go to: https://myaccount.google.com/apppasswords
   - Select "Mail" and "Other (Custom name)"
   - Copy the 16-character password
   - Use this as `SMTP_PASSWORD`

#### SendGrid Setup (Alternative)

1. Sign up at https://sendgrid.com/
2. Create an API key with "Mail Send" permissions
3. Use the API key as `SENDGRID_API_KEY`

#### Twilio Setup for SMS

1. Sign up at https://www.twilio.com/
2. Get your Account SID and Auth Token from dashboard
3. Purchase a phone number
4. Add credentials to `.env`

### Step 4: Verify Model

Ensure the trained model exists:

```bash
# Check if model exists
ls checkpoints/best_model.pth

# If model doesn't exist, train it first:
python train.py
```

### Step 5: Start Backend Server

```bash
cd backend
python app.py

# Or use uvicorn directly:
uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
```

Backend will be available at: http://localhost:8000

Test it: http://localhost:8000 (should return `{"status": "online"}`)

## 🎨 Part 2: Frontend Setup

### Step 1: Install Node Dependencies

```bash
cd frontend
npm install
```

### Step 2: Configure Google OAuth

#### Create Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable "Google+ API"
4. Go to "Credentials" → "Create Credentials" → "OAuth client ID"
5. Choose "Web application"
6. Add authorized JavaScript origins:
   - `http://localhost:3000`
   - `http://localhost:5173`
7. Add authorized redirect URIs:
   - `http://localhost:3000`
8. Copy the "Client ID"

### Step 3: Configure Frontend Environment

Create `frontend/.env` file:

```bash
cp frontend/.env.example frontend/.env
```

Edit `frontend/.env`:

```env
# Backend API URL
VITE_API_URL=http://localhost:8000

# Google OAuth Client ID (from step above)
VITE_GOOGLE_CLIENT_ID=your-google-client-id-here.apps.googleusercontent.com

# Facebook OAuth (optional)
VITE_FACEBOOK_APP_ID=your-facebook-app-id
```

### Step 4: Start Frontend Development Server

```bash
cd frontend
npm run dev
```

Frontend will be available at: http://localhost:3000

## 🧪 Testing the Application

### 1. Test Backend API

```bash
# Health check
curl http://localhost:8000/

# Test notifications (optional)
python backend/notifications.py
```

### 2. Test Frontend Login

1. Open http://localhost:3000
2. Click "Continue with Google"
3. Sign in with your Google account
4. You should be redirected to the dashboard

### 3. Test Video Upload and Detection

1. Navigate to "Upload Video" page
2. Upload a test video file
3. Wait for processing (check Dashboard for status)
4. Check your email/SMS for alerts (if unsafe actions detected)

### 4. Test Alert Configuration

1. Go to "Settings" page
2. Configure email address
3. Optionally add phone number for SMS
4. Save configuration
5. Upload another video to test alerts

## 📁 Project Structure

```
prototype/
├── backend/                    # Backend API
│   ├── app.py                 # FastAPI application
│   ├── database.py            # Database models
│   ├── notifications.py       # Email/SMS services
│   ├── requirements.txt       # Backend dependencies
│   └── .env                   # Backend configuration
│
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── contexts/          # Auth context
│   │   ├── lib/               # API client
│   │   ├── pages/             # Page components
│   │   └── main.tsx           # Entry point
│   ├── package.json           # Frontend dependencies
│   └── .env                   # Frontend configuration
│
├── models/                     # AI models
│   └── action_detector.py     # Model architectures
│
├── checkpoints/               # Trained models
│   └── best_model.pth        # Best trained model
│
├── config.yaml               # Model configuration
└── inference.py              # Inference engine
```

## 🔧 Troubleshooting

### Backend Issues

**Port 8000 already in use:**
```bash
# Kill existing process
kill -9 $(lsof -ti:8000)

# Or use different port
uvicorn backend.app:app --port 8001
```

**Database errors:**
```bash
# Reset database
rm backend/workplace_safety.db
python -c "from backend.database import init_db; init_db()"
```

**Email not sending:**
- Check SMTP credentials in `.env`
- Verify Gmail App Password is correct
- Check spam folder
- Look at backend logs for error messages

**Model not found:**
```bash
# Train model first
python train.py

# Or download pre-trained model (if available)
```

### Frontend Issues

**Port 3000 already in use:**
```bash
# Edit vite.config.ts and change port
# Or kill existing process
lsof -ti:3000 | xargs kill -9
```

**Google OAuth not working:**
- Verify `VITE_GOOGLE_CLIENT_ID` is correct
- Check authorized origins in Google Console
- Clear browser cache and cookies
- Check browser console for errors

**API connection failed:**
- Ensure backend is running on port 8000
- Check `VITE_API_URL` in frontend `.env`
- Verify CORS is enabled in backend

### Video Processing Issues

**Processing takes too long:**
- Use GPU acceleration (check with `python verify.py`)
- Reduce `num_frames` in `config.yaml`
- Use smaller backbone (`resnet18` instead of `resnet50`)

**Out of memory:**
- Reduce batch size in `config.yaml`
- Use CPU instead of GPU for small videos
- Close other applications

## 🚀 Production Deployment

### Backend Deployment

1. **Use production database** (PostgreSQL):
```env
DATABASE_URL=postgresql://user:password@localhost/workplace_safety
```

2. **Use production-grade WSGI server**:
```bash
pip install gunicorn
gunicorn backend.app:app -w 4 -k uvicorn.workers.UvicornWorker
```

3. **Enable HTTPS** with nginx/Apache reverse proxy

4. **Set strong JWT secret**:
```bash
# Generate random secret
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Frontend Deployment

1. **Build for production**:
```bash
cd frontend
npm run build
```

2. **Serve static files** with nginx/Apache or CDN

3. **Update OAuth redirect URIs** in Google Console for production domain

### Security Checklist

- [ ] Change all default passwords and secrets
- [ ] Use HTTPS in production
- [ ] Enable CORS only for trusted domains
- [ ] Implement rate limiting
- [ ] Regular security updates
- [ ] Backup database regularly
- [ ] Monitor logs for suspicious activity

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Google OAuth Setup](https://developers.google.com/identity/protocols/oauth2)
- [SendGrid Documentation](https://docs.sendgrid.com/)
- [Twilio Documentation](https://www.twilio.com/docs)

## 💡 Next Steps

1. **Train on custom data**: Add your own workplace videos to improve accuracy
2. **Customize actions**: Edit `unsafe_actions` in `config.yaml` for your use case
3. **Add more features**: Implement video playback, detailed analytics, etc.
4. **Scale horizontally**: Use task queues (Celery) for processing multiple videos
5. **Add live streaming**: Integrate RTSP/WebRTC for real-time monitoring

## 🆘 Support

If you encounter issues:

1. Check the logs in `logs/` directory
2. Verify all environment variables are set correctly
3. Ensure all dependencies are installed
4. Check firewall/network settings
5. Review this guide carefully

For model training and data preparation, refer to the main `README.md` file.

---

**Note**: This application is designed for workplace safety monitoring. Ensure compliance with privacy laws and regulations when deploying in production environments.

