#!/usr/bin/env python3
"""
Convenience script to start the backend API server
"""
import os
import sys

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    import uvicorn
    from backend.app import app
    
    print("=" * 60)
    print("🚀 Starting Workplace Safety Monitoring Backend API")
    print("=" * 60)
    print()
    print("📍 Server will be available at: http://localhost:8000")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("📖 Alternative docs: http://localhost:8000/redoc")
    print()
    print("Press CTRL+C to stop the server")
    print("=" * 60)
    print()
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

