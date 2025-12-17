#!/usr/bin/env python3
"""Test if the video server is working"""

import urllib.request
import sys
from pathlib import Path

def test_server():
    test_url = "http://localhost:8000/datasets/bdd100k/videos/test/test_video_0000.mp4"
    test_file = Path("datasets/bdd100k/videos/test/test_video_0000.mp4")
    
    print("Testing video server...")
    print(f"File exists: {test_file.exists()}")
    print(f"File path: {test_file.absolute()}")
    print(f"Testing URL: {test_url}")
    print()
    
    try:
        # Test HEAD request
        req = urllib.request.Request(test_url)
        req.get_method = lambda: 'HEAD'
        
        with urllib.request.urlopen(req, timeout=5) as response:
            print(f"SUCCESS! Server is working!")
            print(f"Status Code: {response.getcode()}")
            print(f"Content-Type: {response.headers.get('Content-Type', 'N/A')}")
            print(f"Content-Length: {response.headers.get('Content-Length', 'N/A')} bytes")
            return True
    except urllib.error.URLError as e:
        print(f"ERROR: Could not connect to server")
        print(f"Error: {e}")
        print("\nMake sure the server is running:")
        print("  python serve_videos.py")
        return False
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")
        return False

if __name__ == '__main__':
    success = test_server()
    sys.exit(0 if success else 1)


