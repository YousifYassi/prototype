#!/usr/bin/env python3
"""
Quick start script to launch Label Studio
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    # Create a label-studio directory for project data
    ls_dir = Path('label-studio-data')
    ls_dir.mkdir(exist_ok=True)
    
    print("=" * 60)
    print("Starting Label Studio for Video Annotation")
    print("=" * 60)
    print(f"\nProject data will be stored in: {ls_dir.absolute()}")
    print("\nLabel Studio will open in your browser at: http://localhost:8080")
    print("\nTo import videos:")
    print("  1. Create a new project")
    print("  2. Copy contents from 'labelstudio_config.xml' into Labeling Interface")
    print("  3. Import 'labelstudio_import.json' from the Import tab")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 60)
    print()
    
    try:
        # Start Label Studio with local file serving enabled
        subprocess.run([
            'label-studio',
            'start',
            '--data-dir', str(ls_dir),
            '--host', 'localhost',
            '--port', '8080'
        ])
    except KeyboardInterrupt:
        print("\n\nLabel Studio stopped.")
    except FileNotFoundError:
        print("\nError: Label Studio is not installed.")
        print("Please run: python setup_labelstudio.py")
        sys.exit(1)

if __name__ == '__main__':
    main()

