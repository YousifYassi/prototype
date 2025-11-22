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

## Finding Camera Credentials (Username & Password)

Each camera brand has default credentials and different methods for accessing them. Here's how to find and configure credentials for each camera model listed above:

### Quick Reference Table

| Camera Brand | Default Username | Default Password | Configuration Tool |
|--------------|------------------|------------------|-------------------|
| Wyze Cam v3 | admin or blank | Your Wyze password | Wyze app |
| Reolink | admin | blank (set on first use) | Reolink app or web |
| TP-Link Tapo | admin | Set in Tapo app | Tapo app |
| Hikvision | admin | Set on activation | SADP Tool + web |
| Dahua | admin | admin or blank | ConfigTool + web |
| Axis | root | Set on first setup | AXIS Device Manager |
| Bosch | service/user | On camera label | Config Manager |
| Avigilon | admin | admin (change required) | ACC Software |

**⚠️ Security Warning**: Always change default passwords immediately after setup!

### Budget-Friendly Cameras

#### Wyze Cam v3
- **Default Username**: Usually not required for RTSP (leave blank or use "admin")
- **Default Password**: Your Wyze account password or custom RTSP password
- **⚠️ IMPORTANT**: Wyze has removed official RTSP firmware from their website. You'll need to install legacy firmware.
- **Setup Process** (Requires microSD card):
  1. **Download Legacy RTSP Firmware**: 
     - Download from: https://download.wyzecam.com/firmware/rtsp/demo_v3_RTSP_4.61.0.1.zip
     - Extract `demo_wcv3.bin` file
  2. **Prepare microSD Card**:
     - Format a microSD card (8GB or larger) as FAT32
     - Rename the extracted file to: `demo_wcv3.bin`
     - Place the file in the root directory of the microSD card
  3. **Flash the Camera**:
     - Power OFF the camera
     - Insert the microSD card into the camera
     - Hold the SETUP button on the bottom of the camera
     - While holding SETUP, plug in power
     - Keep holding for 3-4 seconds until LED flashes purple
     - Release button - camera will flash blue/purple during update (3-5 minutes)
     - LED will turn solid blue when complete
     - Power cycle the camera
  4. **Configure RTSP**:
     - Install Wyze app and add camera (may need to update in app first)
     - Go to Camera Settings → Advanced Settings → RTSP
     - Enable RTSP and set a password (remember this!)
     - Note the RTSP URL displayed (format: `rtsp://camera-ip/live`)
  5. **Find Camera IP**:
     - In Wyze app: Settings → Device Info → IP Address
     - Or check your router's DHCP client list
- **RTSP URL Format**: `rtsp://camera-ip/live` (no username needed, password from step 4)
- **Where to Configure**: 
  - Wyze app → Camera Settings → Advanced Settings → RTSP
- **Troubleshooting**:
  - If flash fails, try a different microSD card (some cards aren't compatible)
  - Ensure microSD card is FAT32 formatted
  - Camera must be Wyze Cam v3 specifically (not v2 or Pan)
  - After flashing, you may lose cloud recording features

#### Reolink E1 Pro
- **Default Username**: `admin`
- **Default Password**: Blank (empty) - you'll be forced to create one on first setup
- **Setup Process**:
  1. **Physical Setup**:
     - Power on camera using included USB cable
     - Connect to WiFi via Reolink app during initial setup
     - Or use Ethernet cable for wired connection (more reliable)
  2. **Initial Configuration**:
     - Download Reolink app (iOS/Android)
     - Tap "+" to add device
     - Scan QR code on camera or enter UID manually
     - Follow wizard to connect to WiFi
     - Create admin password (8-32 characters)
  3. **Enable RTSP**:
     - RTSP is enabled by default on Reolink cameras
     - No additional configuration needed
  4. **Find Camera IP**:
     - In Reolink app: Device Settings → Device Info → IP Address
     - Or use Reolink Client software (Windows/Mac) to scan network
     - Or check router's DHCP client list
  5. **Set Static IP** (Recommended):
     - Web interface: Network → IP Settings → Static IP
     - Or reserve IP in your router's DHCP settings
  6. **Get RTSP URL**:
     - Main stream: `rtsp://admin:password@camera-ip:554/h264Preview_01_main`
     - Sub stream (lower quality): `rtsp://admin:password@camera-ip:554/h264Preview_01_sub`
- **Where to Configure**:
  - Web interface: `http://camera-ip` → Settings → User Management
  - Reolink app → Device Settings → User Management
- **RTSP Access**: Same username/password used for web interface
- **Tips**:
  - Use main stream for best quality
  - Sub stream useful for bandwidth-constrained networks
  - Camera supports pan/tilt control via app

#### TP-Link Tapo C200
- **Default Username**: `admin`
- **Default Password**: The password you created in the Tapo app
- **Setup Process**:
  1. **Physical Setup**:
     - Power on camera using included power adapter
     - Camera LED will blink red/green
  2. **Initial Configuration**:
     - Download Tapo app (iOS/Android)
     - Create TP-Link account if you don't have one
     - Tap "+" → "Camera" → Select Tapo C200
     - Connect phone to camera's temporary WiFi (Tapo_Cam_XXXX)
     - Select your home WiFi network and enter password
     - Camera will connect and reboot
  3. **Set Camera Password** (Critical):
     - During setup, app will ask you to create a "Camera Account"
     - Username: `admin`
     - Set a strong password (this is for RTSP/local access)
     - **This is different from your TP-Link cloud account password**
     - Write it down - you'll need it for RTSP
  4. **Enable RTSP/ONVIF**:
     - Open camera in Tapo app
     - Tap Settings (gear icon) → Advanced Settings
     - Scroll to "Camera Account"
     - Enable "Camera Account" toggle
     - Confirm the username is `admin` and password is set
  5. **Find Camera IP**:
     - Tapo app → Camera Settings → Device Info → IP Address
     - Or check your router's DHCP client list
  6. **Verify RTSP Works**:
     - Use VLC: Media → Open Network Stream
     - Enter: `rtsp://admin:your_password@camera-ip:554/stream1`
     - If video plays, you're ready!
- **RTSP URL Formats**:
  - Stream 1 (high quality): `rtsp://admin:password@camera-ip:554/stream1`
  - Stream 2 (low quality): `rtsp://admin:password@camera-ip:554/stream2`
- **Where to Configure**:
  - Tapo app → Camera Settings → Advanced Settings → Camera Account
  - Web interface: `http://camera-ip` (use camera account credentials)
- **Troubleshooting**:
  - If RTSP doesn't work, ensure "Camera Account" is enabled in app
  - Try rebooting camera after enabling RTSP
  - Verify you're using camera password, not TP-Link account password
  - Some older firmware versions may not support RTSP - update firmware

### Professional Cameras

#### Hikvision DS-2CD2043G2-I
- **Default Username**: `admin`
- **Default Password**: No default - you create it on first activation
- **Setup Process**:
  1. **Physical Setup**:
     - Connect camera to PoE switch or use 12V DC power adapter
     - Connect Ethernet cable to network
     - Camera will power on automatically (LED indicators will light)
     - Wait 2-3 minutes for camera to boot
  2. **Download SADP Tool**:
     - Go to: https://www.hikvision.com/en/support/tools/
     - Download "SADP" (Search Active Devices Protocol)
     - Install and run SADP on your computer
  3. **Discover Camera**:
     - Open SADP tool - it will automatically scan network
     - Find your camera in the list (look for "INACTIVE" status)
     - Note the IP address and MAC address
  4. **Activate Camera** (First Time Only):
     - Select inactive camera in SADP
     - Click "Activate" or right-click → Activate
     - Create admin password:
       - 8-16 characters
       - Must include: uppercase, lowercase, numbers
       - Optionally: special characters
       - Example: `Admin123!`
     - Confirm password
     - Optional: Enter email for password recovery
     - Click "OK" - camera will activate (may reboot)
  5. **Access Web Interface**:
     - Open browser and go to `http://camera-ip`
     - Login with username: `admin` and your new password
     - May prompt to install browser plugin (required for some browsers)
     - Chrome/Edge: Use "Webcomponents" mode (no plugin needed)
  6. **Configure Network** (Recommended):
     - Configuration → Network → Basic Settings → TCP/IP
     - Set static IP or reserve DHCP address
     - Note the HTTP Port (usually 80) and RTSP Port (usually 554)
  7. **Enable RTSP**:
     - RTSP is enabled by default
     - Configuration → Network → Advanced Settings → RTSP
     - Verify RTSP port is 554 (default)
  8. **Get RTSP URL**:
     - Main stream (high quality): `rtsp://admin:password@camera-ip:554/Streaming/Channels/101`
     - Sub stream (low quality): `rtsp://admin:password@camera-ip:554/Streaming/Channels/102`
     - Third stream (if available): `rtsp://admin:password@camera-ip:554/Streaming/Channels/103`
- **Where to Configure**:
  - Web interface: `http://camera-ip` → Configuration → User Management
  - SADP Tool: For network configuration and activation
- **Additional Users**: Can create users with different permissions:
  - Configuration → User Management → Add
  - Operator: View only
  - User: View + playback
  - Admin: Full control
- **Password Reset**: 
  - Requires physical access to camera
  - Export XML file from SADP with camera info
  - Contact Hikvision support for reset code
  - Or use reset button (may not work on newer models)
- **Tips**:
  - Use main stream (101) for monitoring
  - Sub stream (102) useful for remote viewing or bandwidth saving
  - Update firmware: Configuration → System → Maintenance → Upgrade
  - Enable NTP for accurate timestamps: Configuration → System → Time Settings

#### Dahua IPC-HFW2431S-S
- **Default Username**: `admin`
- **Default Password**: `admin` (older models) or blank (newer models require password creation)
- **Setup Process**:
  1. **Physical Setup**:
     - Connect camera to PoE switch or use 12V DC power
     - Connect Ethernet cable
     - Camera boots in 1-2 minutes
  2. **Download ConfigTool**:
     - Go to: https://www.dahuasecurity.com/support/tools
     - Download "ConfigTool" or "ToolBox"
     - Install and run on your computer
  3. **Discover Camera**:
     - Open ConfigTool
     - Click "Search" or "Scan"
     - Camera will appear in list with IP address
  4. **Initial Login**:
     - Open browser to `http://camera-ip`
     - Try username: `admin`, password: `admin`
     - If that doesn't work, password may be blank - you'll be prompted to create one
     - Create strong password (8-32 characters)
  5. **Initialize Camera** (If Required):
     - Some models require initialization
     - Create admin password: uppercase, lowercase, numbers
     - Set security questions for password recovery
  6. **Configure Video Settings**:
     - Setup → Camera → Encode → Main Stream
     - Set resolution: 2560x1440 or desired resolution
     - Frame rate: 30 FPS
     - Bitrate: CBR, 4096-8192 Kbps for high quality
  7. **Enable RTSP**:
     - RTSP is enabled by default on port 554
     - Setup → Network → Port
     - Verify RTSP port is 554
  8. **Get RTSP URL**:
     - Main stream: `rtsp://admin:password@camera-ip:554/cam/realmonitor?channel=1&subtype=0`
     - Sub stream: `rtsp://admin:password@camera-ip:554/cam/realmonitor?channel=1&subtype=1`
- **Where to Configure**:
  - Web interface: `http://camera-ip` → Setup → System → Account
  - ConfigTool: For bulk configuration and discovery
- **Password Change**:
  - Setup → System → Account → Username (admin) → Modify
- **Tips**:
  - Change default password immediately
  - Enable NTP: Setup → System → Date & Time
  - Update firmware: Setup → System → Upgrade
  - For multiple cameras, use ConfigTool for batch configuration

#### Axis M3045-V
- **Default Username**: `root`
- **Default Password**: No default - set during initial setup
- **Setup Process**:
  1. **Physical Setup**:
     - Connect camera to PoE switch (Axis cameras are all PoE)
     - Camera will boot in 1-2 minutes
     - LED indicator will show status
  2. **Download AXIS Tools**:
     - Go to: https://www.axis.com/support/tools
     - Download "AXIS IP Utility" (Windows) or "AXIS Device Manager" (Mac/Windows)
     - Or use AXIS Companion app for mobile
  3. **Discover Camera**:
     - Open AXIS IP Utility
     - Camera will appear automatically
     - Note the IP address and serial number
  4. **Initial Setup**:
     - Click camera in utility and click "Home page" button
     - Or browse to `http://camera-ip`
     - Setup wizard will start automatically
     - Accept license agreement
  5. **Create Root Account**:
     - Set root password (8+ characters strongly recommended)
     - Must include: uppercase, lowercase, numbers
     - Example: `AxisRoot123!`
     - Confirm password
  6. **Network Configuration**:
     - Set static IP or use DHCP (can configure later)
     - Configure date/time (enable NTP recommended)
  7. **Configure Video**:
     - Setup → Video → Stream profiles
     - Default profiles usually work well
     - H.264 or H.265 encoding
     - Resolution: 1920x1080 or higher
  8. **Create RTSP User** (Best Practice):
     - Setup → System Options → Users
     - Click "Add user"
     - Username: `operator` or `rtsp_user`
     - Password: Strong password
     - Privileges: Select "Operator" (view + PTZ)
     - This is more secure than using root for streaming
  9. **Get RTSP URL**:
     - Basic: `rtsp://username:password@camera-ip/axis-media/media.amp`
     - Specific profile: `rtsp://username:password@camera-ip/axis-media/media.amp?videocodec=h264&resolution=1920x1080`
     - Stream 1: `rtsp://username:password@camera-ip/axis-media/media.amp?streamprofile=profile_1_h264`
- **Where to Configure**:
  - Web interface: `http://camera-ip` → Setup → System Options → Users
  - AXIS Companion app for mobile configuration
  - AXIS Device Manager for bulk management
- **Additional Users**: Can create users with different access levels:
  - Viewer: View only
  - Operator: View + PTZ control  
  - Administrator: Full access
- **Best Practices**:
  - Create separate user for RTSP streaming (not root)
  - Enable HTTPS: Setup → System Options → Security → HTTPS
  - Update firmware regularly: Setup → Maintenance
  - Use strong passwords and change defaults
- **Advanced Features**:
  - Axis cameras support ONVIF, VAPIX API
  - Can configure motion detection, analytics
  - Support for edge storage (SD card recording)

### Industrial/Enterprise Cameras

#### Bosch FLEXIDOME IP 5000i
- **Default Username**: `service` or `user`
- **Default Password**: Blank or device-specific (printed on camera label)
- **Setup Process**:
  1. **Physical Setup**:
     - Connect camera to PoE+ switch (requires PoE+ for full power)
     - Or use 24V AC power if available
     - Camera boots in 2-3 minutes
  2. **Find Default Password**:
     - Check the label on the camera body or cable
     - Look for "Installer Password" or "Service Password"
     - It's usually a 4-16 character alphanumeric code
     - If no password on label, try leaving it blank
  3. **Download Bosch Tools**:
     - Go to: https://www.boschsecurity.com/xc/en/support/downloads/
     - Download "Configuration Manager"
     - Or use ONVIF Device Manager (generic tool)
  4. **Discover Camera**:
     - Run Configuration Manager
     - It will scan and find Bosch devices
     - Note IP address and model
  5. **Access Web Interface**:
     - Open browser to `https://camera-ip` (HTTPS by default)
     - Accept security certificate warning (self-signed)
     - Login with username: `service` and password from camera label
     - Or try username: `user` with blank password
  6. **Initial Configuration**:
     - First login may require accepting EULA
     - Change default password immediately: Device → User Management
     - Create strong password for service account
  7. **Configure Network**:
     - Device → Network → Network Access
     - Set static IP or configure DHCP
     - Enable NTP for time sync
  8. **Configure Video**:
     - Device → Encoder → Encoder Profiles
     - Set H.264 or H.265 encoding
     - Resolution: 2560x1920 (5MP) or desired setting
     - Frame rate: 30 FPS
     - Bitrate: 4-8 Mbps for high quality
  9. **Enable RTSP**:
     - RTSP is enabled by default
     - Device → Network → Network Access → RTSP Port (usually 554)
  10. **Get RTSP URL**:
      - Profile 1: `rtsp://user:password@camera-ip/rtsp_tunnel?inst=1`
      - Profile 2: `rtsp://user:password@camera-ip/rtsp_tunnel?inst=2`
      - H.265: `rtsp://user:password@camera-ip/rtsp_tunnel?h265&inst=1`
- **Where to Configure**:
  - Web interface: Device → User Management
  - Configuration Manager: For discovery and bulk config
- **Password Location**: Printed on camera label or documentation
- **Tips**:
  - Bosch cameras have advanced analytics built-in
  - Configure intelligent video analytics: Alarm → IVA (Intelligent Video Analysis)
  - Cameras support vandal-resistant mounting
  - Firmware updates: Device → Maintenance → Firmware

#### Avigilon H4 Multisensor
- **Default Username**: `admin`
- **Default Password**: `admin` (must be changed on first login)
- **Setup Process**:
  1. **Physical Setup**:
     - Connect camera to PoE++ switch (requires high power)
     - Or use 24V AC power adapter
     - Multisensor cameras need significant power for 4 sensors
     - Camera boots in 3-5 minutes
  2. **Download Avigilon Control Center (ACC)** (Recommended):
     - Go to: https://www.avigilon.com/support/downloads
     - Download ACC Client software
     - Install on your computer
     - ACC is the primary management interface for Avigilon cameras
  3. **Alternative: Direct Web Access**:
     - If not using ACC, browse to `http://camera-ip`
     - Login with username: `admin`, password: `admin`
     - Will be forced to change password immediately
  4. **Setup via ACC** (Preferred Method):
     - Open ACC Client
     - File → Add Site (if first time)
     - Right-click site → Add Devices
     - ACC will scan network for Avigilon cameras
     - Select camera from list
     - Default credentials: admin/admin
     - You'll be prompted to change password
  5. **Create Strong Password**:
     - Minimum 8 characters
     - Must include: uppercase, lowercase, numbers
     - Special characters recommended
     - Example: `Avigilon2024!`
  6. **Configure Camera**:
     - In ACC: Right-click camera → Setup → Video
     - H.264 or H.265 encoding
     - Each sensor can be configured independently
     - Set resolution per sensor (typically 3MP per sensor)
     - Frame rate: 30 FPS per sensor
  7. **Network Configuration**:
     - Setup → Network
     - Set static IP (recommended for enterprise cameras)
     - Configure NTP for time synchronization
  8. **RTSP Access** (If Not Using ACC):
     - Sensor 1: `rtsp://admin:password@camera-ip/defaultPrimary?streamType=u`
     - Sensor 2: `rtsp://admin:password@camera-ip/defaultPrimary2?streamType=u`
     - Sensor 3: `rtsp://admin:password@camera-ip/defaultPrimary3?streamType=u`
     - Sensor 4: `rtsp://admin:password@camera-ip/defaultPrimary4?streamType=u`
     - Secondary stream (lower quality): Replace `defaultPrimary` with `defaultSecondary`
  9. **Configure Analytics** (ACC Only):
     - Avigilon cameras have built-in AI analytics
     - Setup → Analytics
     - Configure appearance search, unusual motion detection
     - Requires ACC Professional or Enterprise license
- **Where to Configure**:
  - ACC Software → Camera Settings → Users (Recommended)
  - Web interface: Setup → Users (Alternative)
- **Important Notes**:
  - Avigilon cameras are designed to work with ACC
  - Full features only available through ACC software
  - RTSP access is limited compared to ACC integration
  - Licensing may be required for advanced features
  - Each sensor provides independent video stream
- **Tips**:
  - Use ACC for best experience and features
  - Configure recording schedules in ACC
  - Enable self-learning video analytics for intelligent detection
  - Multisensor provides 360° coverage - plan mounting carefully

### Generic IP Camera Credentials

If you have a generic or unlisted camera brand, try these common defaults:

| Username | Password | Notes |
|----------|----------|-------|
| admin | admin | Most common default |
| admin | (blank) | Common on newer cameras |
| admin | 12345 | Some budget cameras |
| admin | password | Older cameras |
| root | root | Linux-based cameras |
| admin | 888888 | Some Chinese brands |
| user | user | Limited access account |

**Finding Your Specific Camera's Defaults**:
1. Check the camera manual or quick start guide
2. Look for a label/sticker on the camera itself
3. Search online: "YourCameraModel default password"
4. Visit the manufacturer's support website
5. Check the camera's retail box

### How to Access Camera Web Interface

For most cameras, finding credentials requires accessing the web interface first:

1. **Find Camera IP Address**:
   - Use manufacturer's discovery tool
   - Check your router's DHCP client list
   - Use IP scanner: Advanced IP Scanner (Windows) or Angry IP Scanner (cross-platform)
   - Check camera's display screen if it has one

2. **Access Web Interface**:
   - Open browser and go to `http://camera-ip`
   - Or `https://camera-ip` for cameras with SSL
   - Some cameras use custom ports: `http://camera-ip:8080`

3. **Login with Default Credentials**:
   - Try common defaults listed above
   - Check camera manual for specific defaults
   - First-time setup may require creating password

4. **Find RTSP Settings**:
   - Look in: Network → Streaming, Video → Streaming, or Settings → RTSP
   - Enable RTSP if disabled
   - Note the RTSP port (usually 554)
   - Note the stream path (e.g., `/stream1`)

### Creating Secure Credentials

When setting up your camera for the first time:

1. **Strong Password Requirements**:
   - Minimum 12-16 characters
   - Mix of uppercase, lowercase, numbers, symbols
   - Avoid common words or patterns
   - Don't reuse passwords from other accounts

2. **Password Managers**: Use a password manager to generate and store credentials
   - LastPass, 1Password, Bitwarden, etc.
   - Store with camera name and IP for easy reference

3. **Documentation**: Keep secure record of:
   - Camera model and serial number
   - IP address (especially if static)
   - Username and password
   - RTSP URL format
   - Camera location/name

4. **Backup Account**: Create a secondary admin account in case you forget the primary password

### Password Reset Procedures

If you've forgotten the camera password:

#### Hikvision
1. Use SADP tool → Select camera → Click "Export" to get security code file
2. Send file to Hikvision support for reset code
3. Or use physical reset button (30 seconds) - loses all settings

#### Dahua
1. Use ConfigTool → Click "Reset Password"
2. Provide camera serial number to support for reset code
3. Or hold reset button 10-15 seconds while powered on

#### Reolink
1. Physical reset: Hold reset button 10 seconds
2. Or use Reolink app → Device Info → Reset

#### Axis
1. Press and hold control button during power-on for 15-25 seconds
2. Resets to factory defaults

#### Generic Cameras
1. Look for small reset button (usually recessed)
2. Hold for 10-30 seconds while camera is powered
3. Wait for camera to reboot (may take 2-3 minutes)
4. **Warning**: Factory reset erases all settings including network configuration

### Verifying Credentials Work

After finding your credentials, test them:

1. **Web Interface Test**:
   - Login to `http://camera-ip` with your credentials
   - Should access camera settings

2. **RTSP Test** (using VLC Media Player):
   - Open VLC → Media → Open Network Stream
   - Enter: `rtsp://username:password@camera-ip:554/stream-path`
   - If video plays, credentials are correct

3. **Command Line Test** (ffmpeg):
   ```bash
   ffmpeg -rtsp_transport tcp -i "rtsp://username:password@camera-ip:554/stream-path" -frames:v 1 test.jpg
   ```
   - If image is created, RTSP connection works

## Camera Setup Instructions

### 1. For RTSP Cameras (Most Common)

#### Step 1: Connect Camera to Network
1. Connect camera to your router via Ethernet cable
2. Power on the camera (or use PoE)
3. Download the camera's mobile app or use the manufacturer's discovery tool
4. Note the camera's IP address

#### Step 2: Configure Camera Settings
1. Access camera web interface (usually `http://camera-ip`)
2. Login with credentials (see [Finding Camera Credentials](#finding-camera-credentials-username--password) section above)
3. **Change default password immediately** (if using defaults)
4. Enable RTSP streaming (usually under Network or Video settings)
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
1. Verify username and password (see [Finding Camera Credentials](#finding-camera-credentials-username--password) section)
2. Check for special characters in password (URL encode them - see below)
3. Ensure credentials work in camera's web interface first
4. Verify RTSP is enabled in camera settings
5. Try default credentials if you haven't changed them yet
6. Reset camera to factory defaults if needed (see Password Reset Procedures above)
7. Ensure user has streaming permissions in camera settings

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

