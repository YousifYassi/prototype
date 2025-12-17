# Fix: "Not allowed to load local resource" Error

## Problem
Browsers block `file://` URLs for security reasons, so Label Studio can't load videos directly from your local filesystem.

## Solution: Use a Local HTTP Server

I've created a simple HTTP server that serves your videos so Label Studio can access them through `http://localhost` URLs.

---

## Quick Fix (3 Steps)

### Step 1: Start the Video Server

**Option A: Double-click the batch file**
```
start_video_server.bat
```

**Option B: Run from command line**
```bash
python serve_videos.py
```

You should see:
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
```

**⚠️ Keep this window open while annotating!**

### Step 2: Import the New File into Label Studio

1. Go to your Label Studio project
2. Click **"Import"**
3. Upload **`labelstudio_import_http.json`** (NOT the old file!)
4. Wait for import to complete

### Step 3: Start Annotating!

Now when you click on a video, it should load properly through the HTTP server.

---

## What Changed?

### Old Import File (Doesn't Work)
```json
{
  "data": {
    "video": "file:///C:/Users/yousi/prototype/datasets/..."
  }
}
```
❌ Browser blocks this

### New Import File (Works!)
```json
{
  "data": {
    "video": "http://localhost:8000/datasets/..."
  }
}
```
✅ Browser allows this

---

## Troubleshooting

### Videos Still Won't Load?

1. **Check the server is running**
   - You should see "Server running at: http://localhost:8000"
   - If not, start it: `python serve_videos.py`

2. **Check the port**
   - Default port is 8000
   - If 8000 is busy, the server will use 8001, 8002, etc.
   - Check the server output for the actual port
   - If port changed, regenerate import file:
     ```bash
     python create_http_import.py --port 8001
     ```

3. **Test a video URL directly**
   - Open browser and go to: `http://localhost:8000/datasets/bdd100k/videos/train/train_video_0000.mp4`
   - If it plays, the server is working
   - If not, check the server is running

4. **Check file paths**
   - Make sure videos exist in the expected locations
   - The server serves from your project root directory

### Server Won't Start?

**Port already in use:**
```bash
# Find what's using port 8000
netstat -ano | findstr :8000

# Or use a different port
python serve_videos.py
# It will auto-find an available port
```

**Permission errors:**
- Run command prompt as Administrator
- Or use a different port (8001, 8002, etc.)

### Import File Too Large?

If importing 8,268 videos at once is too slow:

1. **Import in batches:**
   ```python
   # Create smaller batches
   python create_http_import.py --dir datasets/bdd100k/videos/train --output batch1.json
   python create_http_import.py --dir datasets/bdd100k/videos/test --output batch2.json
   ```

2. **Or manually edit the JSON** to include only specific folders

---

## Alternative: Use Label Studio's Built-in File Serving

Label Studio can also serve files directly if configured properly:

1. **Start Label Studio with local file serving:**
   ```bash
   label-studio start --host 0.0.0.0 --port 8080
   ```

2. **Configure in Label Studio settings:**
   - Go to Settings → Cloud Storage
   - Add Local Files storage
   - Point to your datasets folder

However, the HTTP server method is simpler and more reliable.

---

## Files Created

| File | Purpose |
|------|---------|
| `serve_videos.py` | HTTP server to serve videos |
| `create_http_import.py` | Generate import file with HTTP URLs |
| `labelstudio_import_http.json` | **Use this file** (8,268 videos) |
| `start_video_server.bat` | Quick launcher for Windows |

---

## Workflow Summary

```
1. Start video server (keep running)
   ↓
2. Import labelstudio_import_http.json into Label Studio
   ↓
3. Annotate videos (they'll load via HTTP)
   ↓
4. When done, stop server (Ctrl+C)
```

---

## Need Help?

- Check that the server is running and shows the correct port
- Verify videos exist at the paths in the import file
- Test a video URL directly in your browser
- Make sure you're using `labelstudio_import_http.json`, not the old file

---

**You're all set! Start the server and import the new file.** 🚀


