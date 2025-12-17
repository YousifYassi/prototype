#!/usr/bin/env python3
"""
Simple HTTP server to serve video files for Label Studio
This allows browsers to access local video files
"""

import http.server
import socketserver
import os
import sys
from pathlib import Path

class VideoHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler that serves videos with proper CORS headers"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def end_headers(self):
        # Add CORS headers to allow Label Studio to access videos
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS, HEAD')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        # Add proper content type for videos
        if any(ext in self.path for ext in ['.mp4']):
            self.send_header('Content-Type', 'video/mp4')
        elif any(ext in self.path for ext in ['.avi']):
            self.send_header('Content-Type', 'video/x-msvideo')
        elif any(ext in self.path for ext in ['.mov']):
            self.send_header('Content-Type', 'video/quicktime')
        elif any(ext in self.path for ext in ['.webm']):
            self.send_header('Content-Type', 'video/webm')
        super().end_headers()
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.end_headers()
    
    def do_HEAD(self):
        """Handle HEAD requests for video files"""
        self.do_GET()
    
    def log_message(self, format, *args):
        """Suppress default logging, only log video requests"""
        if any(ext in self.path for ext in ['.mp4', '.avi', '.mov', '.mkv', '.webm']):
            print(f"Serving video: {self.path}")
        # Uncomment to see all requests:
        # super().log_message(format, *args)

def find_port(start_port=8000, max_port=8100):
    """Find an available port"""
    import socket
    for port in range(start_port, max_port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(('', port))
            sock.close()
            return port
        except OSError:
            sock.close()
            continue
    return None

def main():
    # Get the project root directory
    project_root = Path(__file__).parent.absolute()
    
    # Change to project root so we can serve files relative to it
    os.chdir(project_root)
    
    # Find available port
    port = find_port()
    if port is None:
        print("Error: Could not find an available port")
        sys.exit(1)
    
    print("=" * 60)
    print("Video File Server for Label Studio")
    print("=" * 60)
    print(f"\nServing files from: {project_root}")
    print(f"Server running at: http://localhost:{port}")
    print(f"\nVideos will be accessible at:")
    print(f"   http://localhost:{port}/datasets/...")
    print(f"   http://localhost:{port}/backend/uploads/...")
    print("\nIMPORTANT: Keep this server running while using Label Studio!")
    print("   Press Ctrl+C to stop the server")
    print("=" * 60)
    print()
    
    try:
        # Create server - SimpleHTTPRequestHandler serves from current directory
        httpd = socketserver.TCPServer(("", port), VideoHTTPRequestHandler)
        print(f"Server started successfully on port {port}")
        print("Ready to serve videos...\n")
        httpd.serve_forever()
    except OSError as e:
        print(f"Error starting server: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nServer stopped.")
        sys.exit(0)

if __name__ == '__main__':
    main()

