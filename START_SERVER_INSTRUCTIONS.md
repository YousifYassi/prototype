# 🚨 IMPORTANT: How to Start the Video Server

## The Problem
The server needs to be running in a **visible window** so you can see it's working and keep it running.

## Solution: Start Server Manually

### Option 1: Double-Click Batch File (Easiest)
1. **Double-click**: `start_video_server_foreground.bat`
2. A **new window** will open showing the server running
3. **Keep this window open** while using Label Studio
4. You should see: "Server running at: http://localhost:8000"

### Option 2: Command Line
1. Open **Command Prompt** or **PowerShell**
2. Navigate to your project folder:
   ```bash
   cd C:\Users\yousi\prototype
   ```
3. Run:
   ```bash
   python serve_videos.py
   ```
4. **Keep this window open** while using Label Studio

## What You Should See

When the server starts correctly, you'll see:
```
============================================================
Video File Server for Label Studio
============================================================

Serving files from: C:\Users\yousi\prototype
Server running at: http://localhost:8000

Videos will be accessible at:
   http://localhost:8000/datasets/...
   http://localhost:8000/backend/uploads/...

IMPORTANT: Keep this server running while using Label Studio!
   Press Ctrl+C to stop the server
============================================================

Server started successfully on port 8000
Ready to serve videos...
```

## Testing the Server

After starting the server, test it:

1. Open your browser
2. Go to: `http://localhost:8000/datasets/bdd100k/videos/test/test_video_0000.mp4`
3. The video should start playing or downloading

**OR** run the test script:
```bash
python test_video_server.py
```

## Using in Label Studio

1. ✅ **Start the server** (keep window open)
2. ✅ **Open Label Studio** at http://localhost:8080
3. ✅ **Import** `labelstudio_import_http.json`
4. ✅ **Start annotating** - videos should load now!

## Troubleshooting

### Server Won't Start?
- Make sure port 8000 isn't used by another program
- Try a different port: Edit `serve_videos.py` and change port 8000 to 8001

### Still Getting Connection Refused?
1. Check the server window is actually running
2. Look for any error messages in the server window
3. Try restarting the server
4. Check Windows Firewall isn't blocking it

### Videos Load Slowly?
- This is normal for large video files
- The server streams videos, so first load may take a moment
- Subsequent loads should be faster (browser caching)

## Quick Checklist

- [ ] Server window is open and showing "Server running at: http://localhost:8000"
- [ ] Test URL works in browser: `http://localhost:8000/datasets/bdd100k/videos/test/test_video_0000.mp4`
- [ ] Label Studio is open at http://localhost:8080
- [ ] Imported `labelstudio_import_http.json` (not the old file!)
- [ ] Videos are loading in Label Studio

---

**Remember: Keep the server window open while annotating!** 🚀


