# Fix: CSP Violation Blocking Videos

## The Problem

Label Studio's Content Security Policy (CSP) is blocking videos from `localhost:8000` because Label Studio only allows resources from `'self'` (localhost:8081).

## Solution Options

### Option 1: Use Label Studio's Local Storage (Recommended)

Label Studio has built-in support for local file storage that bypasses CSP issues:

1. **In Label Studio UI:**
   - Go to **Settings** → **Cloud Storage**
   - Click **"Add Source"**
   - Select **"Local Files"**
   - Set **"Absolute local path"** to: `C:\Users\yousi\prototype\datasets`
   - Set **"Prefix"** to: `/local-files/`
   - Click **"Sync Storage"**

2. **Update Import File:**
   Use paths like: `/local-files/bdd100k/videos/test/test_video_0000.mp4`

### Option 2: Start Label Studio with CSP Disabled

Start Label Studio with environment variable to disable strict CSP:

```bash
# Windows PowerShell
$env:LABEL_STUDIO_DISABLE_CSP="true"
label-studio start --host 0.0.0.0 --port 8081

# Or create a batch file
```

### Option 3: Use Same-Origin Proxy (Best for Development)

Serve videos from Label Studio's port using a reverse proxy or by configuring Label Studio to serve static files.

### Option 4: Browser Extension (Quick Fix)

Install a browser extension to disable CSP for localhost:
- Chrome: "Disable Content-Security-Policy" extension
- Firefox: "CSP Bypass" extension

**⚠️ Only use this for development, not production!**

---

## Quick Fix: Update Import File for Local Storage

Let me create a script to generate an import file that uses Label Studio's local storage:


