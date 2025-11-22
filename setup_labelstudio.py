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
    """Install Label Studio"""
    print("Installing Label Studio...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'labelstudio_requirements.txt'], 
                      check=True)
        print("Label Studio installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing Label Studio: {e}")
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
        print("\n✓ Label Studio is already installed")
    
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

