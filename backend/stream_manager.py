"""
Real-time video stream management for multiple camera sources
Handles RTSP, RTMP, HTTP streams, and webcams
"""
import cv2
import asyncio
import threading
import time
import base64
import numpy as np
import os
from datetime import datetime
from typing import Dict, Optional, List
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class StreamConfig:
    """Configuration for a video stream"""
    stream_id: str
    name: str
    source_url: str
    source_type: str  # 'rtsp', 'rtmp', 'http', 'webcam'
    status: str  # 'active', 'inactive', 'error'
    fps: int = 30
    width: int = 1920
    height: int = 1080
    created_at: str = None
    last_frame_time: str = None
    error_message: str = None


class VideoStream:
    """
    Manages a single video stream with real-time processing
    """
    
    def __init__(self, config: StreamConfig, detector, alert_callback=None):
        self.config = config
        self.detector = detector
        self.alert_callback = alert_callback
        
        self.capture = None
        self.is_running = False
        self.thread = None
        self.current_frame = None
        self.current_result = None
        self.frame_lock = threading.Lock()
        
        self.frame_count = 0
        self.error_count = 0
        self.last_detection_time = None
        
    def start(self):
        """Start the video stream"""
        if self.is_running:
            logger.warning(f"Stream {self.config.stream_id} is already running")
            return False
        
        try:
            # Open video capture
            if self.config.source_type == 'webcam':
                source = int(self.config.source_url)
                self.capture = cv2.VideoCapture(source)
            else:
                source = self.config.source_url
                
                # For RTSP streams, use FFmpeg backend with special options
                if self.config.source_type == 'rtsp':
                    logger.info(f"Opening RTSP stream with FFmpeg backend: {source}")
                    
                    # Set FFmpeg options for RTSP via environment variable
                    # Use TCP transport (more reliable than UDP), set timeouts, and allow unauthorized connections
                    os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp|max_delay;5000000|timeout;10000000"
                    
                    # Use FFmpeg backend explicitly
                    self.capture = cv2.VideoCapture(source, cv2.CAP_FFMPEG)
                    
                    # Configure buffer settings
                    self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 3)
                    
                    # Try to open with retries (limited to avoid exhausting camera connection limit)
                    max_retries = 1
                    for attempt in range(max_retries):
                        if self.capture.isOpened():
                            logger.info(f"RTSP stream opened successfully on attempt {attempt + 1}")
                            break
                        if attempt < max_retries - 1:
                            logger.warning(f"RTSP connection attempt {attempt + 1}/{max_retries} failed, retrying...")
                            self.capture.release()
                            time.sleep(2)
                            self.capture = cv2.VideoCapture(source, cv2.CAP_FFMPEG)
                else:
                    self.capture = cv2.VideoCapture(source)
            
            if not self.capture.isOpened():
                # CRITICAL: Release the capture object to free camera connection
                if self.capture:
                    self.capture.release()
                    self.capture = None
                
                error_msg = f"Cannot open video source: {source}"
                
                # Check OpenCV build info
                build_info = cv2.getBuildInformation()
                if 'ffmpeg' not in build_info.lower() and 'gstreamer' not in build_info.lower():
                    error_msg += " | OpenCV is not built with FFmpeg or GStreamer support. Install opencv-python-headless or opencv-contrib-python."
                else:
                    error_msg += " | Camera connection limit may be reached. Try rebooting the camera, or check IP/credentials/network."
                
                raise Exception(error_msg)
            
            # Update config with actual stream properties
            self.config.width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.config.height = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self.config.fps = int(self.capture.get(cv2.CAP_PROP_FPS)) or 30
            
            self.is_running = True
            self.config.status = 'active'
            self.thread = threading.Thread(target=self._process_stream, daemon=True)
            self.thread.start()
            
            logger.info(f"Started stream {self.config.stream_id}: {self.config.source_url}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start stream {self.config.stream_id}: {e}")
            # CRITICAL: Release capture on error to free camera connection
            if self.capture:
                self.capture.release()
                self.capture = None
            self.config.status = 'error'
            self.config.error_message = str(e)
            return False
    
    def stop(self):
        """Stop the video stream and release all resources"""
        logger.info(f"Stopping stream {self.config.stream_id}")
        self.is_running = False
        
        # Wait for processing thread to finish
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5)
            if self.thread.is_alive():
                logger.warning(f"Stream thread {self.config.stream_id} did not stop gracefully")
        
        # Force release capture to free camera connection
        if self.capture:
            try:
                self.capture.release()
                logger.info(f"Released camera connection for stream {self.config.stream_id}")
            except Exception as e:
                logger.error(f"Error releasing capture: {e}")
            finally:
                self.capture = None
            self.capture = None
        
        self.config.status = 'inactive'
        logger.info(f"Stopped stream {self.config.stream_id}")
    
    def _process_stream(self):
        """Main processing loop for the stream"""
        consecutive_errors = 0
        max_consecutive_errors = 30  # Stop after 30 consecutive errors
        
        while self.is_running:
            try:
                ret, frame = self.capture.read()
                
                if not ret:
                    consecutive_errors += 1
                    logger.warning(f"Failed to read frame from stream {self.config.stream_id}")
                    
                    if consecutive_errors >= max_consecutive_errors:
                        logger.error(f"Too many errors, stopping stream {self.config.stream_id}")
                        self.config.status = 'error'
                        self.config.error_message = "Failed to read frames"
                        break
                    
                    time.sleep(0.1)
                    continue
                
                # Reset error counter on successful read
                consecutive_errors = 0
                self.frame_count += 1
                
                # Process frame with detector
                result = self.detector.process_frame(frame)
                
                # Draw results on frame
                annotated_frame = self.detector.draw_results(frame, result)
                
                # Update current frame and result
                with self.frame_lock:
                    self.current_frame = annotated_frame
                    self.current_result = result
                    self.config.last_frame_time = datetime.now().isoformat()
                
                # Send alert callback if unsafe action detected
                if result.get('alert') and self.alert_callback:
                    self.last_detection_time = datetime.now()
                    asyncio.run(self.alert_callback(
                        self.config.stream_id,
                        result['action'],
                        result['confidence']
                    ))
                
                # Control frame rate
                time.sleep(1.0 / self.config.fps)
                
            except Exception as e:
                self.error_count += 1
                logger.error(f"Error processing stream {self.config.stream_id}: {e}")
                time.sleep(1)
    
    def get_frame_jpeg(self) -> Optional[bytes]:
        """Get current frame as JPEG bytes"""
        with self.frame_lock:
            if self.current_frame is None:
                return None
            
            # Encode frame as JPEG
            ret, buffer = cv2.imencode('.jpg', self.current_frame, 
                                      [cv2.IMWRITE_JPEG_QUALITY, 85])
            if not ret:
                return None
            
            return buffer.tobytes()
    
    def get_frame_base64(self) -> Optional[str]:
        """Get current frame as base64 encoded string"""
        jpeg_bytes = self.get_frame_jpeg()
        if jpeg_bytes is None:
            return None
        
        return base64.b64encode(jpeg_bytes).decode('utf-8')
    
    def get_status(self) -> dict:
        """Get stream status and statistics"""
        return {
            'stream_id': self.config.stream_id,
            'name': self.config.name,
            'status': self.config.status,
            'source_type': self.config.source_type,
            'fps': self.config.fps,
            'width': self.config.width,
            'height': self.config.height,
            'frame_count': self.frame_count,
            'error_count': self.error_count,
            'last_frame_time': self.config.last_frame_time,
            'last_detection_time': self.last_detection_time.isoformat() if self.last_detection_time else None,
            'current_result': self.current_result,
            'error_message': self.config.error_message
        }


class StreamManager:
    """
    Manages multiple video streams
    """
    
    def __init__(self, detector):
        self.detector = detector
        self.streams: Dict[str, VideoStream] = {}
        self.alert_handlers = []
    
    def add_alert_handler(self, handler):
        """Add callback for alerts"""
        self.alert_handlers.append(handler)
    
    async def _handle_alert(self, stream_id: str, action: str, confidence: float):
        """Handle alert from stream"""
        for handler in self.alert_handlers:
            try:
                await handler(stream_id, action, confidence)
            except Exception as e:
                logger.error(f"Error in alert handler: {e}")
    
    def add_stream(self, config: StreamConfig) -> bool:
        """Add and start a new stream"""
        if config.stream_id in self.streams:
            logger.warning(f"Stream {config.stream_id} already exists")
            return False
        
        # Create and start stream
        stream = VideoStream(config, self.detector, self._handle_alert)
        success = stream.start()
        
        # Add stream to manager even if it failed (so we can access error info)
        self.streams[config.stream_id] = stream
        
        if success:
            logger.info(f"Added and started stream {config.stream_id}")
        else:
            logger.error(f"Added stream {config.stream_id} but failed to start: {stream.config.error_message}")
        
        return success
    
    def remove_stream(self, stream_id: str) -> bool:
        """Remove and stop a stream"""
        if stream_id not in self.streams:
            logger.warning(f"Stream {stream_id} not found")
            return False
        
        stream = self.streams[stream_id]
        stream.stop()
        del self.streams[stream_id]
        logger.info(f"Removed stream {stream_id}")
        return True
    
    def get_stream(self, stream_id: str) -> Optional[VideoStream]:
        """Get stream by ID"""
        return self.streams.get(stream_id)
    
    def list_streams(self) -> List[dict]:
        """List all streams with their status"""
        return [stream.get_status() for stream in self.streams.values()]
    
    def get_stream_frame(self, stream_id: str, format: str = 'jpeg') -> Optional[bytes]:
        """Get current frame from stream"""
        stream = self.get_stream(stream_id)
        if not stream:
            return None
        
        if format == 'jpeg':
            return stream.get_frame_jpeg()
        elif format == 'base64':
            return stream.get_frame_base64()
        else:
            return None
    
    def stop_all_streams(self):
        """Stop all active streams"""
        for stream_id in list(self.streams.keys()):
            self.remove_stream(stream_id)
        logger.info("Stopped all streams")


def validate_stream_url(url: str, source_type: str) -> bool:
    """
    Validate stream URL/source
    
    Args:
        url: Stream URL or webcam index
        source_type: Type of source ('rtsp', 'rtmp', 'http', 'webcam')
    
    Returns:
        bool: Whether the URL is valid
    """
    if source_type == 'webcam':
        try:
            index = int(url)
            return 0 <= index <= 10
        except ValueError:
            return False
    
    elif source_type == 'rtsp':
        return url.startswith('rtsp://')
    
    elif source_type == 'rtmp':
        return url.startswith('rtmp://')
    
    elif source_type == 'http':
        return url.startswith('http://') or url.startswith('https://')
    
    return False

