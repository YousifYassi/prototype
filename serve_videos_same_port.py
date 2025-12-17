#!/usr/bin/env python3
"""
HTTP server to serve video files on the same port as Label Studio
This avoids CSP violations by serving from the same origin
"""

import http.server
import socketserver
import os
import sys
from pathlib import Path
from urllib.parse import urlparse

class VideoHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler that serves videos with proper headers"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS, HEAD')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        
        # Add proper content type for videos
        if self.path.endswith('.mp4'):
            self.send_header('Content-Type', 'video/mp4')
        elif self.path.endswith('.avi'):
            self.send_header('Content-Type', 'video/x-msvideo')
        elif self.path.endswith('.mov'):
            self.send_header('Content-Type', 'video/quicktime')
        elif self.path.endswith('.webm'):
            self.send_header('Content-Type', 'video/webm')
        elif self.path.endswith('.mkv'):
            self.send_header('Content-Type', 'video/x-matroska')
        
        # Add range request support for video streaming
        self.send_header('Accept-Ranges', 'bytes')
        
        super().end_headers()
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.end_headers()
    
    def do_HEAD(self):
        """Handle HEAD requests for video files"""
        self.do_GET()
    
    def log_message(self, format, *args):
        """Only log video requests"""
        if any(ext in self.path for ext in ['.mp4', '.avi', '.mov', '.mkv', '.webm']):
            print(f"Serving video: {self.path}")

def main():
    # Get the project root directory
    project_root = Path(__file__).parent.absolute()
    
    # Change to project root so we can serve files relative to it
    os.chdir(project_root)
    
    # Use port 8081 (same as Label Studio) or find available port
    # Actually, we can't use 8081 if Label Studio is there, so use 8000
    # But we'll configure Label Studio to proxy requests
    port = 8000
    
    # Check if port is available
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(('', port))
        sock.close()
    except OSError:
        print(f"Port {port} is already in use. Trying port 8001...")
        port = 8001
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('', port))
            sock.close()
        except OSError:
            print(f"Error: Ports 8000 and 8001 are both in use")
            sys.exit(1)
    
    print("=" * 60)
    print("Video File Server for Label Studio")
    print("=" * 60)
    print(f"\nServing files from: {project_root}")
    print(f"Server running at: http://localhost:{port}")
    print(f"\nIMPORTANT: Configure Label Studio to allow this origin!")
    print(f"   Add to Label Studio environment:")
    print(f"   LABEL_STUDIO_HOST=0.0.0.0")
    print(f"   Or use the proxy solution below")
    print("\nVideos will be accessible at:")
    print(f"   http://localhost:{port}/datasets/...")
    print(f"   http://localhost:{port}/backend/uploads/...")
    print("\nKeep this server running while using Label Studio!")
    print("   Press Ctrl+C to stop the server")
    print("=" * 60)
    print()
    
    try:
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


