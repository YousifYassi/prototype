#!/usr/bin/env python3
"""
Initialize the database for the Workplace Safety Monitoring application
"""
import os
import sys

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    print("=" * 60)
    print("🗄️  Initializing Workplace Safety Monitoring Database")
    print("=" * 60)
    print()
    
    try:
        from backend.database import init_db, DATABASE_URL
        
        print(f"Database URL: {DATABASE_URL}")
        print()
        print("Creating tables...")
        
        init_db()
        
        print("✅ Database initialized successfully!")
        print()
        print("Tables created:")
        print("  - users")
        print("  - alert_configs")
        print("  - video_processing")
        print()
        print("You can now start the backend server.")
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

