# Live Streaming Feature - Quick Start Guide

## Overview

The real-time video streaming feature allows you to connect IP cameras, RTSP streams, RTMP feeds, or webcams to your workplace safety monitoring system. The AI will continuously analyze the video feed and alert you when unsafe actions are detected.

## Features

✅ **Multiple Stream Support**: Monitor multiple cameras simultaneously  
✅ **Real-Time Detection**: Instant unsafe action detection with alerts  
✅ **Multiple Protocols**: Support for RTSP, RTMP, HTTP streams, and USB webcams  
✅ **Live Dashboard**: View all active streams in a modern web interface  
✅ **Auto-Reconnect**: Automatic reconnection if stream drops  
✅ **Performance Stats**: Monitor FPS, frame count, and detection statistics  
✅ **Low Latency**: Optimized for minimal delay (~100-500ms)  

## Quick Start

### 1. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Or specifically for streaming:
pip install fastapi uvicorn python-multipart opencv-python
```

### 2. Start the Backend Server

```bash
# From the project root directory
cd backend
python app.py
```

The API will start on `http://localhost:8000`

### 3. Start the Frontend

```bash
cd frontend
npm install
npm run dev
```

The web interface will open at `http://localhost:5173`

### 4. Add Your First Camera

1. Login to the web interface
2. Navigate to **"Live Streams"** in the navigation menu
3. Click **"+ Add Stream"**
4. Fill in the form:
   - **Stream Name**: Give it a descriptive name (e.g., "Warehouse Camera 1")
   - **Source Type**: Choose your camera type (RTSP, Webcam, etc.)
   - **Source URL**: Enter the stream URL or webcam index
   - **FPS**: Set frame rate (30 recommended)
5. Click **"Add Stream"**

The stream will start immediately and begin detecting unsafe actions!

## Camera Types & Setup

### Option 1: RTSP IP Camera (Recommended)

**What you need:**
- IP camera with RTSP support
- Camera connected to same network as your server

**Example URL:**
```
rtsp://admin:password@192.168.1.100:554/stream
```

**Setup steps:**
1. Find your camera's IP address (check router or camera app)
2. Enable RTSP in camera settings
3. Note the RTSP URL format (check camera manual or [CAMERA_SETUP_GUIDE.md](CAMERA_SETUP_GUIDE.md))
4. Add to system using the web interface

### Option 2: USB Webcam (Easiest for Testing)

**What you need:**
- USB webcam connected to the server computer

**Source URL:**
```
0  (for first webcam, 1 for second, etc.)
```

**Setup steps:**
1. Plug webcam into server computer
2. Verify it's detected (check Device Manager on Windows)
3. Add to system using Source Type: "Webcam" and Source URL: "0"

### Option 3: RTMP Stream

**What you need:**
- RTMP stream source (OBS Studio, hardware encoder, etc.)

**Example URL:**
```
rtmp://server-address:1935/live/stream-key
```

### Option 4: HTTP/MJPEG Stream

**What you need:**
- Camera or server providing MJPEG stream

**Example URL:**
```
http://192.168.1.100:8080/video.mjpeg
```

## Camera Recommendations

### Budget Options ($30-$100)
| Camera | Price | Resolution | Best For |
|--------|-------|------------|----------|
| **Wyze Cam v3** | ~$35 | 1080p | Testing, home office |
| **Reolink E1 Pro** | ~$60 | 2K | Indoor monitoring |
| **TP-Link Tapo C200** | ~$40 | 1080p | General purpose |

### Professional Options ($150-$400)
| Camera | Price | Resolution | Best For |
|--------|-------|------------|----------|
| **Hikvision DS-2CD2043G2** | ~$200 | 4MP | Professional installs |
| **Dahua IPC-HFW2431S** | ~$150 | 4MP | 24/7 monitoring |
| **Axis M3045-V** | ~$350 | 1080p | Enterprise deployments |

For detailed recommendations and setup instructions, see [CAMERA_SETUP_GUIDE.md](CAMERA_SETUP_GUIDE.md).

## Testing with a Webcam

The fastest way to test the live streaming feature:

1. **Start the backend:**
   ```bash
   cd backend
   python app.py
   ```

2. **Start the frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Add webcam:**
   - Go to Live Streams page
   - Click "+ Add Stream"
   - Name: "Test Webcam"
   - Source Type: Webcam
   - Source URL: 0
   - FPS: 30
   - Click "Add Stream"

4. **You should see:**
   - Live video feed from your webcam
   - Real-time detection results
   - Detection confidence scores
   - FPS and performance stats

## API Endpoints

The streaming feature adds these new API endpoints:

### Create Stream
```http
POST /streams
Content-Type: application/json
Authorization: Bearer <token>

{
  "name": "Warehouse Camera 1",
  "source_url": "rtsp://admin:password@192.168.1.100:554/stream",
  "source_type": "rtsp",
  "fps": 30
}
```

### List Streams
```http
GET /streams
Authorization: Bearer <token>
```

### Get Stream Status
```http
GET /streams/{stream_id}
Authorization: Bearer <token>
```

### Get Current Frame
```http
GET /streams/{stream_id}/frame
Authorization: Bearer <token>
```

Returns base64-encoded JPEG of current frame with detection overlay.

### Stop Stream
```http
DELETE /streams/{stream_id}
Authorization: Bearer <token>
```

### MJPEG Video Stream
```http
GET /streams/{stream_id}/video
Authorization: Bearer <token>
```

Returns continuous MJPEG stream for direct display in `<img>` tag.

## Architecture

```
┌─────────────┐
│   Camera    │
│ (RTSP/USB)  │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│  Stream Manager     │
│  - Capture frames   │
│  - Buffer mgmt      │
│  - Threading        │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Action Detector     │
│  - Frame analysis   │
│  - AI inference     │
│  - Temporal smooth  │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  FastAPI Backend    │
│  - REST endpoints   │
│  - MJPEG streaming  │
│  - Alert handling   │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  React Frontend     │
│  - Live video view  │
│  - Stream mgmt      │
│  - Alerts display   │
└─────────────────────┘
```

## Performance Optimization

### For Single Camera
- **CPU**: 4 cores minimum
- **RAM**: 4GB available
- **GPU**: Optional but recommended (10x faster)
- **Network**: 5 Mbps per camera

### For Multiple Cameras (4-8)
- **CPU**: 8+ cores (or GPU)
- **RAM**: 8GB+ (add ~1GB per camera)
- **GPU**: NVIDIA with CUDA (highly recommended)
- **Network**: Gigabit Ethernet

### Tips
1. **Use GPU acceleration**: Set `device: cuda` in `config.yaml`
2. **Adjust FPS**: Lower FPS (15-20) for less powerful systems
3. **Use H.265**: Better compression = less bandwidth
4. **Wired connection**: Always prefer Ethernet over WiFi
5. **Reduce resolution**: Use 1080p instead of 4K if needed

## Troubleshooting

### Stream Won't Start

**Problem:** "Failed to start stream" error

**Solutions:**
1. Check camera is powered on and connected to network
2. Verify RTSP URL is correct (check camera manual)
3. Test URL with VLC Media Player: Media → Open Network Stream
4. Check username/password are correct
5. Ensure camera's RTSP is enabled
6. Check firewall isn't blocking port 554 (RTSP)

### No Video Displayed

**Problem:** Stream status is "active" but no video shows

**Solutions:**
1. Check browser console for errors (F12)
2. Verify backend is running on port 8000
3. Check CORS settings in backend
4. Try refreshing the page
5. Check backend logs for errors

### Low FPS / Laggy Video

**Problem:** Video is stuttering or slow

**Solutions:**
1. Reduce FPS in stream settings
2. Lower camera resolution to 720p
3. Check network bandwidth
4. Use wired connection instead of WiFi
5. Close other streams if running multiple
6. Enable GPU acceleration

### High CPU Usage

**Problem:** CPU usage is very high

**Solutions:**
1. Enable GPU acceleration (set `device: cuda` in config.yaml)
2. Reduce number of concurrent streams
3. Lower FPS (20 instead of 30)
4. Reduce detection frequency
5. Use H.265 encoding if available

### Authentication Errors

**Problem:** "Invalid credentials" or 401 errors

**Solutions:**
1. Check username and password in RTSP URL
2. URL-encode special characters in password (see guide)
3. Verify user has streaming permissions in camera
4. Try accessing camera through web browser first

## Advanced Configuration

### Custom Detection Settings

Edit `config.yaml`:

```yaml
inference:
  confidence_threshold: 0.7  # Adjust sensitivity
  temporal_smoothing: true   # Smooth detections
  smoothing_window: 5        # Number of frames to smooth
  alert_cooldown: 30         # Seconds between alerts
  video_buffer_size: 100     # Frame buffer size
```

### Multiple Cameras Configuration

For optimal performance with multiple cameras:

```yaml
# config.yaml
training:
  device: cuda  # Use GPU

inference:
  fps: 20  # Lower FPS for multiple streams
  confidence_threshold: 0.75
  video_buffer_size: 60
```

### Network Settings

For remote cameras or low-bandwidth:

```yaml
inference:
  fps: 15  # Reduce bandwidth
  video_buffer_size: 30
```

## Security Considerations

⚠️ **Important Security Notes:**

1. **Change default camera passwords** immediately
2. **Use strong passwords** for RTSP authentication
3. **Don't expose cameras** directly to the internet
4. **Use VPN** for remote access
5. **Keep firmware updated** on all cameras
6. **Use HTTPS** in production
7. **Isolate cameras** on separate VLAN if possible

## Next Steps

1. ✅ Set up your first camera (see above)
2. 📹 Read the [Camera Setup Guide](CAMERA_SETUP_GUIDE.md) for detailed recommendations
3. ⚙️ Configure alert settings in Settings page
4. 📊 Monitor the Dashboard for detection statistics
5. 🔔 Set up email/SMS alerts for unsafe actions

## Support

- **Camera issues**: See [CAMERA_SETUP_GUIDE.md](CAMERA_SETUP_GUIDE.md)
- **General setup**: See [QUICK_START.md](QUICK_START.md)
- **API documentation**: Visit `http://localhost:8000/docs` when backend is running
- **Issues**: Open an issue on GitHub

---

**Happy monitoring! Stay safe! 🛡️**

