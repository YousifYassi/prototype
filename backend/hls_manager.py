"""
HLS Streaming Manager for converting RTSP/RTMP streams to HLS format
Uses FFmpeg to transcode streams to HTTP Live Streaming
"""
import os
import subprocess
import logging
import threading
import time
from pathlib import Path
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)

class HLSStreamManager:
    """Manages HLS transcoding processes for multiple streams"""
    
    def __init__(self, output_dir: str = "backend/hls_output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.processes: Dict[str, subprocess.Popen] = {}
        self.stream_dirs: Dict[str, Path] = {}
        
    def start_hls_stream(self, stream_id: str, source_url: str, source_type: str) -> Tuple[bool, str]:
        """
        Start FFmpeg process to transcode stream to HLS
        
        Args:
            stream_id: Unique identifier for the stream
            source_url: RTSP/RTMP source URL
            source_type: Type of source (rtsp, rtmp, http, webcam)
        
        Returns:
            Tuple of (success: bool, error_message: str)
            error_message is empty string on success, detailed error on failure
        """
        if stream_id in self.processes:
            logger.warning(f"HLS stream {stream_id} already running")
            return (True, "")
        
        try:
            # Create output directory for this stream
            stream_dir = self.output_dir / stream_id
            stream_dir.mkdir(parents=True, exist_ok=True)
            self.stream_dirs[stream_id] = stream_dir
            
            # HLS output path
            playlist_path = stream_dir / "stream.m3u8"
            
            # FFmpeg command for HLS streaming
            cmd = [
                'ffmpeg',
                '-loglevel', 'warning',
                '-rtsp_transport', 'tcp',  # Use TCP for RTSP (more reliable)
                '-i', source_url,  # Input source
                
                # Video encoding
                '-c:v', 'libx264',  # H.264 codec
                '-preset', 'veryfast',  # Fast encoding
                '-tune', 'zerolatency',  # Low latency
                '-b:v', '2M',  # Video bitrate
                '-maxrate', '2M',
                '-bufsize', '4M',
                '-g', '30',  # GOP size (keyframe every 30 frames)
                '-sc_threshold', '0',
                
                # Audio (copy or remove if not needed)
                '-an',  # No audio for now (simpler)
                
                # HLS output options
                '-f', 'hls',
                '-hls_time', '2',  # 2 second segments
                '-hls_list_size', '5',  # Keep last 5 segments in playlist
                '-hls_flags', 'delete_segments+append_list',  # Delete old segments
                '-hls_segment_filename', str(stream_dir / 'segment_%03d.ts'),
                str(playlist_path)
            ]
            
            logger.info(f"Starting HLS transcode for stream {stream_id}")
            logger.debug(f"FFmpeg command: {' '.join(cmd)}")
            
            # Start FFmpeg process
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=10**8
            )
            
            self.processes[stream_id] = process
            
            # Monitor FFmpeg in background
            monitor_thread = threading.Thread(
                target=self._monitor_process,
                args=(stream_id, process),
                daemon=True
            )
            monitor_thread.start()
            
            # Wait a moment to see if FFmpeg starts successfully
            time.sleep(2)
            
            if process.poll() is not None:
                # Process died immediately - capture full error output
                stderr = process.stderr.read().decode('utf-8', errors='ignore')
                logger.error(f"FFmpeg failed to start for stream {stream_id}: {stderr}")
                self._cleanup_stream(stream_id)
                
                # Extract the most relevant error message
                error_msg = "FFmpeg failed to start"
                if "Connection refused" in stderr:
                    error_msg = "Connection refused. Check if the stream source is accessible."
                elif "Invalid data" in stderr or "Invalid argument" in stderr:
                    error_msg = "Invalid stream format or URL."
                elif "401 Unauthorized" in stderr or "403 Forbidden" in stderr:
                    error_msg = "Authentication failed. Check username and password in URL."
                elif "Connection timed out" in stderr or "timeout" in stderr.lower():
                    error_msg = "Connection timed out. Check network connectivity and stream URL."
                elif "No route to host" in stderr:
                    error_msg = "Cannot reach host. Check IP address and network."
                elif stderr.strip():
                    # Include a snippet of the actual error
                    error_lines = stderr.strip().split('\n')
                    # Get last few meaningful lines
                    meaningful_lines = [line for line in error_lines if line.strip() and not line.startswith('[')][-3:]
                    if meaningful_lines:
                        error_msg = f"FFmpeg error: {' | '.join(meaningful_lines)}"
                
                return (False, error_msg)
            
            logger.info(f"Successfully started HLS stream {stream_id}")
            return (True, "")
            
        except Exception as e:
            logger.error(f"Error starting HLS stream {stream_id}: {e}")
            self._cleanup_stream(stream_id)
            error_msg = f"Failed to start HLS transcoding: {str(e)}"
            return (False, error_msg)
    
    def stop_hls_stream(self, stream_id: str):
        """Stop HLS transcoding process"""
        if stream_id not in self.processes:
            logger.warning(f"HLS stream {stream_id} not running")
            return
        
        try:
            process = self.processes[stream_id]
            logger.info(f"Stopping HLS stream {stream_id}")
            
            # Terminate FFmpeg gracefully
            process.terminate()
            
            # Wait for termination
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                logger.warning(f"FFmpeg didn't stop gracefully, killing process")
                process.kill()
                process.wait()
            
            self._cleanup_stream(stream_id)
            logger.info(f"Stopped HLS stream {stream_id}")
            
        except Exception as e:
            logger.error(f"Error stopping HLS stream {stream_id}: {e}")
    
    def get_playlist_path(self, stream_id: str) -> Optional[Path]:
        """Get path to HLS playlist file"""
        if stream_id not in self.stream_dirs:
            return None
        
        playlist_path = self.stream_dirs[stream_id] / "stream.m3u8"
        if playlist_path.exists():
            return playlist_path
        return None
    
    def get_segment_path(self, stream_id: str, segment_name: str) -> Optional[Path]:
        """Get path to HLS segment file"""
        if stream_id not in self.stream_dirs:
            return None
        
        segment_path = self.stream_dirs[stream_id] / segment_name
        if segment_path.exists():
            return segment_path
        return None
    
    def is_stream_active(self, stream_id: str) -> bool:
        """Check if HLS stream is active"""
        if stream_id not in self.processes:
            return False
        
        process = self.processes[stream_id]
        return process.poll() is None
    
    def _monitor_process(self, stream_id: str, process: subprocess.Popen):
        """Monitor FFmpeg process and log errors"""
        try:
            # Read stderr in real-time
            while True:
                if process.poll() is not None:
                    break
                
                # Read any error output
                if process.stderr:
                    line = process.stderr.readline()
                    if line:
                        logger.debug(f"FFmpeg {stream_id}: {line.decode('utf-8', errors='ignore').strip()}")
                
                time.sleep(0.1)
            
            # Process ended
            if process.returncode != 0:
                stderr = process.stderr.read().decode('utf-8', errors='ignore')
                logger.error(f"FFmpeg process {stream_id} ended with error: {stderr}")
            
        except Exception as e:
            logger.error(f"Error monitoring FFmpeg process {stream_id}: {e}")
    
    def _cleanup_stream(self, stream_id: str):
        """Clean up stream resources"""
        if stream_id in self.processes:
            del self.processes[stream_id]
        
        # Note: We keep the stream directory for now
        # It will be cleaned up on next start or manually
    
    def cleanup_all(self):
        """Stop all streams and cleanup"""
        for stream_id in list(self.processes.keys()):
            self.stop_hls_stream(stream_id)

# Global HLS manager instance
_hls_manager = None

def get_hls_manager() -> HLSStreamManager:
    """Get or create global HLS manager instance"""
    global _hls_manager
    if _hls_manager is None:
        _hls_manager = HLSStreamManager()
    return _hls_manager


