# ✅ Fix: CSP Violation - Use Label Studio Local Storage

## The Problem
Label Studio's Content Security Policy blocks videos from `localhost:8000` because it only allows resources from the same origin (`localhost:8081`).

## ✅ Solution: Use Label Studio's Built-in Local Storage

This is the **best solution** - it bypasses CSP completely and is the recommended way to serve local files.

### Step 1: Configure Local Storage in Label Studio

1. **Open Label Studio** at http://localhost:8081
2. Go to **Settings** → **Cloud Storage** (or **Storage**)
3. Click **"Add Source"** or **"Add Storage"**
4. Select **"Local Files"** as the storage type
5. Configure:
   - **Title**: `Local Videos`
   - **Absolute local path**: `C:\Users\yousi\prototype\datasets`
   - **Prefix**: `/local-files/`
   - **Description**: `Local video files for annotation`
6. Click **"Add Storage"** or **"Save"**
7. Click **"Sync Storage"** to sync the files

### Step 2: Import the New File

1. In your Label Studio project, go to **Import**
2. Upload **`labelstudio_import_local.json`** (NOT the HTTP version!)
3. The videos should now load without CSP violations

### Step 3: Verify It Works

- Click on a video task
- The video should load from `/local-files/...` path
- No CSP errors in the console!

---

## Alternative: Disable CSP (Development Only)

If local storage doesn't work, you can disable CSP for development:

### Option A: Environment Variable

Stop Label Studio, then start it with:

```bash
# Windows PowerShell
$env:LABEL_STUDIO_DISABLE_CSP="true"
label-studio start --host 0.0.0.0 --port 8081
```

### Option B: Browser Extension (Quick Fix)

Install a browser extension to disable CSP:
- **Chrome**: "Disable Content-Security-Policy"
- **Firefox**: "CSP Bypass"

⚠️ **Warning**: Only use this for development!

---

## Files Created

| File | Purpose |
|------|---------|
| `labelstudio_import_local.json` | **Use this!** - Uses local storage paths (8,268 videos) |
| `create_local_storage_import.py` | Script to regenerate if needed |
| `CSP_FIX_GUIDE.md` | This guide |

---

## Troubleshooting

### Local Storage Not Showing Up?

1. Make sure you set the **absolute path** correctly: `C:\Users\yousi\prototype\datasets`
2. Check that the path exists and contains videos
3. Try clicking **"Sync Storage"** again
4. Refresh the Label Studio page

### Videos Still Not Loading?

1. Check the import file uses `/local-files/` prefix
2. Verify the storage is synced in Label Studio settings
3. Check browser console for other errors
4. Make sure the video file paths in the import match the storage prefix

### Can't Find Cloud Storage Settings?

- In newer Label Studio versions, it might be under **Settings** → **Storage**
- Or **Settings** → **Data Management**
- Look for "Add Storage" or "Cloud Storage" option

---

## What Changed?

### Old Import (CSP Violation):
```json
{
  "data": {
    "video": "http://localhost:8000/datasets/..."
  }
}
```
❌ Blocked by CSP

### New Import (Works!):
```json
{
  "data": {
    "video": "/local-files/bdd100k/videos/test/test_video_0000.mp4"
  }
}
```
✅ No CSP issues!

---

**Try the local storage solution first - it's the cleanest approach!** 🚀





