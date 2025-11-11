# Camera Setup Guide for Real-Time Safety Monitoring

This guide will help you choose and configure the right camera for your workplace safety monitoring system.

## Table of Contents
- [Camera Requirements](#camera-requirements)
- [Recommended Cameras](#recommended-cameras)
- [Camera Setup Instructions](#camera-setup-instructions)
- [Network Configuration](#network-configuration)
- [Troubleshooting](#troubleshooting)

## Camera Requirements

### Minimum Specifications
- **Resolution**: 1920x1080 (1080p) or higher
- **Frame Rate**: 15-30 FPS minimum
- **Protocols**: RTSP, RTMP, or HTTP streaming support
- **Network**: Ethernet (preferred) or WiFi with stable connection
- **Field of View**: 90-120 degrees (depending on monitoring area)
- **Low Light Performance**: Good performance in typical workplace lighting

### Recommended Specifications
- **Resolution**: 2560x1440 (2K) or 3840x2160 (4K)
- **Frame Rate**: 30 FPS
- **Protocols**: RTSP with H.264/H.265 encoding
- **Network**: PoE (Power over Ethernet) for single-cable setup
- **Field of View**: 110-130 degrees
- **Features**: WDR (Wide Dynamic Range), motion detection, night vision

## Recommended Cameras

### Budget-Friendly Options ($30-$100)

#### 1. Wyze Cam v3
- **Price**: ~$35
- **Resolution**: 1080p @ 20 FPS
- **Protocol**: RTSP (requires firmware)
- **Pros**: Affordable, good image quality, easy setup
- **Cons**: Requires custom firmware for RTSP
- **Setup URL**: `rtsp://username:password@camera-ip/live`
- **Best for**: Small businesses, testing, single location

#### 2. Reolink E1 Pro
- **Price**: ~$60
- **Resolution**: 2560x1440 @ 25 FPS
- **Protocol**: RTSP native support
- **Pros**: Good value, pan/tilt, native RTSP
- **Cons**: WiFi only
- **Setup URL**: `rtsp://admin:password@camera-ip:554/h264Preview_01_main`
- **Best for**: Indoor monitoring, flexible positioning

#### 3. TP-Link Tapo C200
- **Price**: ~$40
- **Resolution**: 1080p @ 15 FPS
- **Protocol**: RTSP (via ONVIF)
- **Pros**: Pan/tilt, motion tracking, affordable
- **Cons**: Lower frame rate
- **Setup URL**: `rtsp://username:password@camera-ip:554/stream1`
- **Best for**: General purpose indoor monitoring

### Professional Options ($150-$400)

#### 4. Hikvision DS-2CD2043G2-I
- **Price**: ~$200
- **Resolution**: 4MP @ 30 FPS
- **Protocol**: RTSP, ONVIF
- **Pros**: Excellent image quality, PoE, weatherproof
- **Cons**: Higher cost
- **Setup URL**: `rtsp://admin:password@camera-ip:554/Streaming/Channels/101`
- **Best for**: Professional installations, outdoor use

#### 5. Dahua IPC-HFW2431S-S
- **Price**: ~$150
- **Resolution**: 4MP @ 30 FPS
- **Protocol**: RTSP, ONVIF
- **Pros**: Good value, PoE, night vision
- **Cons**: Complex interface
- **Setup URL**: `rtsp://admin:password@camera-ip:554/cam/realmonitor?channel=1&subtype=0`
- **Best for**: 24/7 monitoring, multiple locations

#### 6. Axis M3045-V
- **Price**: ~$350
- **Resolution**: 1080p @ 30 FPS
- **Protocol**: RTSP, ONVIF
- **Pros**: Enterprise quality, excellent low light, wide dynamic range
- **Cons**: Expensive
- **Setup URL**: `rtsp://root:password@camera-ip/axis-media/media.amp`
- **Best for**: Enterprise deployments, critical applications

### Industrial/Enterprise Options ($400+)

#### 7. Bosch FLEXIDOME IP 5000i
- **Price**: ~$600
- **Resolution**: 5MP @ 30 FPS
- **Protocol**: RTSP, ONVIF
- **Pros**: Industrial grade, intelligent video analytics, vandal-resistant
- **Cons**: Very expensive
- **Setup URL**: `rtsp://user:password@camera-ip/rtsp_tunnel`
- **Best for**: High-risk environments, critical infrastructure

#### 8. Avigilon H4 Multisensor
- **Price**: ~$1,500
- **Resolution**: 4x 3MP sensors
- **Protocol**: RTSP, proprietary
- **Pros**: 360° coverage, AI analytics, exceptional quality
- **Cons**: Extremely expensive, complex setup
- **Best for**: Large facilities, comprehensive coverage

## Camera Setup Instructions

### 1. For RTSP Cameras (Most Common)

#### Step 1: Connect Camera to Network
1. Connect camera to your router via Ethernet cable
2. Power on the camera (or use PoE)
3. Download the camera's mobile app or use the manufacturer's discovery tool
4. Note the camera's IP address

#### Step 2: Configure Camera Settings
1. Access camera web interface (usually `http://camera-ip`)
2. Login with default credentials (check manual)
3. **Change default password immediately**
4. Enable RTSP streaming
5. Set resolution to 1080p or higher
6. Set frame rate to 30 FPS
7. Enable H.264 or H.265 encoding

#### Step 3: Find RTSP URL
Common formats:
- Generic: `rtsp://username:password@camera-ip:554/stream`
- Hikvision: `rtsp://admin:password@camera-ip:554/Streaming/Channels/101`
- Dahua: `rtsp://admin:password@camera-ip:554/cam/realmonitor?channel=1&subtype=0`
- Reolink: `rtsp://admin:password@camera-ip:554/h264Preview_01_main`
- Axis: `rtsp://root:password@camera-ip/axis-media/media.amp`

#### Step 4: Add to Safety Monitoring System
1. Login to your workplace safety monitoring dashboard
2. Navigate to "Live Streams"
3. Click "Add Stream"
4. Enter:
   - **Name**: Descriptive name (e.g., "Warehouse Camera 1")
   - **Source Type**: RTSP
   - **Source URL**: Your RTSP URL from Step 3
   - **FPS**: 30 (or your camera's frame rate)
5. Click "Add Stream"

### 2. For USB Webcams

#### Step 1: Connect Webcam
1. Plug USB webcam into the computer running the backend server
2. Verify it's detected by your operating system

#### Step 2: Find Camera Index
**Windows:**
```powershell
# List video devices
Get-PnpDevice -Class Camera
```

**Linux:**
```bash
# List video devices
ls -l /dev/video*
```

**macOS:**
```bash
# List video devices
system_profiler SPCameraDataType
```

Usually, the first webcam is index `0`, second is `1`, etc.

#### Step 3: Add to Safety Monitoring System
1. Navigate to "Live Streams" → "Add Stream"
2. Enter:
   - **Name**: "Local Webcam"
   - **Source Type**: Webcam
   - **Source URL**: 0 (or appropriate index)
   - **FPS**: 30
3. Click "Add Stream"

### 3. For RTMP Streams

If you have an RTMP stream (e.g., from OBS Studio or another encoder):

1. **RTMP URL Format**: `rtmp://server-address/live/stream-key`
2. Add to system using Source Type: RTMP

### 4. For HTTP Streams (MJPEG)

Some cameras provide MJPEG streams over HTTP:

1. **URL Format**: `http://camera-ip/video.mjpeg`
2. Add to system using Source Type: HTTP

## Network Configuration

### Static IP Address (Recommended)
Assign a static IP to your camera to ensure the URL doesn't change:

1. Access your router's admin panel
2. Find DHCP settings
3. Reserve an IP address for your camera's MAC address
4. Or configure static IP directly in camera settings

### Port Forwarding (For Remote Access)
If accessing cameras from outside your network:

1. **Do NOT expose cameras directly to the internet**
2. Use a VPN to access your local network
3. Or set up secure port forwarding with strong authentication
4. Change default ports (554 for RTSP)
5. Use strong, unique passwords

### Network Requirements
- **Bandwidth per camera**: 2-8 Mbps (depending on resolution/compression)
- **Recommended**: Gigabit Ethernet switch
- **WiFi**: 5GHz preferred, strong signal required
- **Latency**: <100ms recommended

## Troubleshooting

### Camera Not Connecting

**Issue**: Stream fails to start
**Solutions**:
1. Verify camera IP address (ping the IP)
2. Check RTSP URL format for your camera model
3. Verify username/password
4. Check firewall settings
5. Ensure camera's RTSP is enabled

### Poor Video Quality

**Issue**: Blurry or pixelated video
**Solutions**:
1. Increase camera resolution in camera settings
2. Adjust bitrate (increase for better quality)
3. Check network bandwidth
4. Clean camera lens
5. Improve lighting conditions

### High Latency/Lag

**Issue**: Delayed video feed
**Solutions**:
1. Reduce FPS in stream settings
2. Use wired connection instead of WiFi
3. Reduce number of simultaneous streams
4. Enable H.265 encoding (if supported)
5. Increase buffer size in camera settings

### Connection Drops

**Issue**: Stream disconnects frequently
**Solutions**:
1. Check network stability
2. Reduce video quality/bitrate
3. Update camera firmware
4. Check camera power supply
5. Reduce wireless interference (if using WiFi)

### Authentication Errors

**Issue**: "Invalid credentials" or "Authentication failed"
**Solutions**:
1. Verify username and password
2. Check for special characters in password (URL encode them)
3. Reset camera to factory defaults if needed
4. Ensure user has streaming permissions

## URL Encoding for Special Characters

If your password contains special characters, URL encode them:

- `@` → `%40`
- `:` → `%3A`
- `/` → `%2F`
- `?` → `%3F`
- `#` → `%23`
- `&` → `%26`
- `=` → `%3D`
- `+` → `%2B`
- `$` → `%24`

**Example**: 
- Password: `Pass@123!`
- Encoded: `Pass%40123!`
- URL: `rtsp://admin:Pass%40123!@192.168.1.100:554/stream`

## Camera Placement Best Practices

### Positioning
1. **Height**: 8-12 feet for optimal coverage
2. **Angle**: 15-30 degrees downward
3. **Coverage**: Overlap fields of view by 10-20%
4. **Lighting**: Avoid pointing directly at bright lights or windows

### Coverage Areas
- **Warehouses**: One camera per 1,000-2,000 sq ft
- **Manufacturing**: Cover hazardous equipment and walkways
- **Construction**: Focus on high-traffic and high-risk zones
- **General**: Ensure no blind spots in critical areas

### Environmental Considerations
- **Outdoor**: Use IP66+ rated weatherproof cameras
- **Indoor**: IP20+ suitable for most environments
- **Temperature**: Check operating range for your environment
- **Vibration**: Use vibration-resistant mounts near machinery

## Security Best Practices

1. **Change default passwords immediately**
2. **Use strong, unique passwords** (16+ characters)
3. **Enable HTTPS** for camera web interface
4. **Update firmware regularly**
5. **Disable UPnP** on cameras
6. **Use VLANs** to isolate cameras from main network
7. **Enable authentication** for RTSP streams
8. **Regular security audits**
9. **Disable unused features** (FTP, SMTP, etc.)
10. **Monitor access logs**

## Performance Optimization

### For Multiple Cameras
- Use a dedicated server/computer for the monitoring system
- **Recommended specs**:
  - CPU: 4+ cores
  - RAM: 8GB+ (add 1-2GB per camera)
  - GPU: NVIDIA GPU with CUDA support (highly recommended)
  - Network: Gigabit Ethernet
  - Storage: SSD for alert clips

### Frame Rate Guidelines
- **Low activity areas**: 15 FPS
- **Normal monitoring**: 20-25 FPS
- **High activity/critical areas**: 30 FPS

### Compression Settings
- **H.265 (HEVC)**: Best compression, requires more processing
- **H.264 (AVC)**: Good balance, widely supported
- **MJPEG**: Highest quality, largest bandwidth

## Getting Help

If you need additional assistance:

1. **Check camera documentation**: Manufacturer's manual
2. **Online resources**: 
   - [IPVM Camera Calculator](https://calculator.ipvm.com/) - For coverage planning
   - Camera manufacturer support forums
3. **Professional installation**: Consider for complex setups
4. **System logs**: Check backend logs for detailed error messages

## Quick Reference: Common RTSP URLs

```
# Hikvision
rtsp://admin:password@192.168.1.64:554/Streaming/Channels/101

# Dahua
rtsp://admin:password@192.168.1.108:554/cam/realmonitor?channel=1&subtype=0

# Reolink
rtsp://admin:password@192.168.1.100:554/h264Preview_01_main

# Axis
rtsp://root:password@192.168.1.90/axis-media/media.amp

# Amcrest
rtsp://admin:password@192.168.1.50:554/cam/realmonitor?channel=1&subtype=1

# Foscam
rtsp://admin:password@192.168.1.80:554/videoMain

# TP-Link
rtsp://admin:password@192.168.1.70:554/stream1

# Generic ONVIF
rtsp://admin:password@192.168.1.X:554/onvif1
```

---

**Need more help?** Check the main README.md or open an issue on GitHub.

