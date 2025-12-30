#!/usr/bin/env python3
"""
Setup script for Label Studio with workplace safety video annotation
"""

import os
import json
import subprocess
import sys
from pathlib import Path

def find_video_files(dataset_dir):
    """Find all video files in the dataset directory"""
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
    video_files = []
    
    dataset_path = Path(dataset_dir)
    if not dataset_path.exists():
        print(f"Warning: {dataset_dir} does not exist")
        return []
    
    for video_file in dataset_path.rglob('*'):
        if video_file.is_file() and video_file.suffix.lower() in video_extensions:
            video_files.append(video_file)
    
    return video_files

def create_labelstudio_import_json(output_file='labelstudio_import.json'):
    """Create a JSON file for importing videos into Label Studio"""
    
    # Find videos in all dataset directories
    dataset_dirs = [
        'datasets/bdd100k/videos',
        'datasets/CharadesEgo_v1/videos',
        'datasets/missing_files_v1-2_test/videos',
        'backend/uploads'  # Include uploaded videos too
    ]
    
    all_videos = []
    for dataset_dir in dataset_dirs:
        videos = find_video_files(dataset_dir)
        all_videos.extend(videos)
    
    print(f"Found {len(all_videos)} video files")
    
    # Create Label Studio import format
    # Label Studio expects tasks with a video URL or path
    tasks = []
    for video_path in all_videos:
        # Convert to absolute path for Label Studio
        abs_path = video_path.absolute().as_posix()
        
        task = {
            "data": {
                "video": f"file://{abs_path}"
            },
            "meta": {
                "source_path": str(video_path),
                "filename": video_path.name,
                "dataset": video_path.parts[-3] if len(video_path.parts) > 3 else "unknown"
            }
        }
        tasks.append(task)
    
    # Write to JSON file
    with open(output_file, 'w') as f:
        json.dump(tasks, f, indent=2)
    
    print(f"Created {output_file} with {len(tasks)} tasks")
    return output_file

def check_labelstudio_installed():
    """Check if Label Studio is installed"""
    try:
        result = subprocess.run(['label-studio', '--version'], 
                              capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

def install_labelstudio():
    """Install Label Studio with Windows-specific error handling"""
    print("Installing Label Studio...")
    
    # Detect Windows
    is_windows = sys.platform.startswith('win')
    
    # Try multiple installation strategies for Windows compatibility
    strategies = []
    
    if is_windows:
        # On Windows, try --user first to avoid permission issues
        strategies.append(
            [sys.executable, '-m', 'pip', 'install', '--user', '-r', 'labelstudio_requirements.txt']
        )
    
    # Add other strategies
    strategies.extend([
        # Standard install with upgrade
        [sys.executable, '-m', 'pip', 'install', '--upgrade', '-r', 'labelstudio_requirements.txt'],
        # Install with --no-cache-dir to avoid file locking issues
        [sys.executable, '-m', 'pip', 'install', '--no-cache-dir', '-r', 'labelstudio_requirements.txt'],
    ])
    
    for i, cmd in enumerate(strategies, 1):
        try:
            print(f"\nTrying installation strategy {i}...")
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print("Label Studio installed successfully!")
            return True
        except subprocess.CalledProcessError as e:
            error_output = e.stderr if e.stderr else e.stdout
            if i < len(strategies):
                print(f"Strategy {i} failed, trying next approach...")
                print(f"Error: {error_output[:200]}...")  # Show first 200 chars
            else:
                print(f"\nAll installation strategies failed.")
                print(f"Last error: {error_output}")
                print("\n" + "=" * 60)
                print("TROUBLESHOOTING:")
                print("=" * 60)
                print("\nThis is a common Windows issue where pip can't rename files.")
                print("Try these solutions:\n")
                print("1. Close any Python processes or IDEs that might be using the files")
                print("2. Run PowerShell/CMD as Administrator and try again")
                print("3. Manually uninstall problematic packages first:")
                print("   python -m pip uninstall genson -y")
                print("   python -m pip install -r labelstudio_requirements.txt")
                print("\n4. Or install with --user flag (installs to user directory):")
                print("   python -m pip install --user -r labelstudio_requirements.txt")
                print("\n5. Or use a virtual environment (recommended):")
                print("   python -m venv venv")
                print("   venv\\Scripts\\activate")
                print("   pip install -r labelstudio_requirements.txt")
                return False
    
    return False

def main():
    print("=" * 60)
    print("Label Studio Setup for Workplace Safety Video Annotation")
    print("=" * 60)
    
    # Check if Label Studio is installed
    if not check_labelstudio_installed():
        print("\nLabel Studio is not installed.")
        install = input("Would you like to install it now? (y/n): ").lower().strip()
        if install == 'y':
            if not install_labelstudio():
                print("Failed to install Label Studio. Exiting.")
                return
        else:
            print("Please install Label Studio manually:")
            print(f"  {sys.executable} -m pip install -r labelstudio_requirements.txt")
            return
    else:
        print("\n[OK] Label Studio is already installed")
    
    # Create import file
    print("\nCreating Label Studio import file...")
    import_file = create_labelstudio_import_json()
    
    print("\n" + "=" * 60)
    print("Setup Complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Start Label Studio:")
    print("   label-studio")
    print("\n2. Create a new project in the Label Studio UI")
    print("\n3. In the project settings:")
    print("   - Go to 'Labeling Interface'")
    print("   - Copy the contents of 'labelstudio_config.xml'")
    print("   - Paste it into the code editor")
    print("\n4. Import the videos:")
    print(f"   - Go to 'Import' and upload '{import_file}'")
    print("\n5. Start annotating!")
    print("\nOr use the quick start script:")
    print("   python start_labelstudio.py")
    print()

if __name__ == '__main__':
    main()

