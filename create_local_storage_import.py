#!/usr/bin/env python3
"""
Create Label Studio import file using local storage paths
This avoids CSP issues by using Label Studio's built-in local file serving
"""

import json
import argparse
from pathlib import Path

def create_local_storage_import(video_dir='datasets', output_file='labelstudio_import_local.json', storage_prefix='/local-files/'):
    """
    Create import file with local storage paths for Label Studio
    
    Args:
        video_dir: Directory containing videos (relative to project root)
        output_file: Output JSON file name
        storage_prefix: Prefix for local storage (default: /local-files/)
    """
    project_root = Path(__file__).parent.absolute()
    video_path = project_root / video_dir
    
    # Find all video files
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
    video_files = []
    
    for ext in video_extensions:
        video_files.extend(video_path.rglob(f'*{ext}'))
    
    print(f"Found {len(video_files)} video files")
    
    # Create tasks with local storage paths
    tasks = []
    for video_file in video_files:
        # Get relative path from video_dir (not project root)
        try:
            # Get path relative to the video_dir
            relative_path = video_file.relative_to(video_path)
            # Convert Windows path separators to forward slashes
            storage_path = str(relative_path).replace('\\', '/')
            
            # Create local storage URL
            local_storage_url = f"{storage_prefix}{storage_path}"
            
            task = {
                "data": {
                    "video": local_storage_url
                },
                "meta": {
                    "source_path": str(video_file),
                    "filename": video_file.name,
                    "relative_path": storage_path,
                    "storage_type": "local"
                }
            }
            tasks.append(task)
        except ValueError:
            # Skip files outside video_dir
            continue
    
    # Write to JSON file
    with open(output_file, 'w') as f:
        json.dump(tasks, f, indent=2)
    
    print(f"Created {output_file} with {len(tasks)} videos")
    print(f"\nNext steps:")
    print(f"   1. In Label Studio: Settings -> Cloud Storage -> Add Source")
    print(f"   2. Select 'Local Files'")
    print(f"   3. Set absolute path to: {video_path.absolute()}")
    print(f"   4. Set prefix to: {storage_prefix}")
    print(f"   5. Click 'Sync Storage'")
    print(f"   6. Import {output_file} into Label Studio")
    
    return output_file

def main():
    parser = argparse.ArgumentParser(
        description='Create Label Studio import file with local storage paths'
    )
    parser.add_argument(
        '--output', '-o',
        default='labelstudio_import_local.json',
        help='Output file name (default: labelstudio_import_local.json)'
    )
    parser.add_argument(
        '--dir', '-d',
        default='datasets',
        help='Directory to scan for videos (default: datasets)'
    )
    parser.add_argument(
        '--prefix', '-p',
        default='/local-files/',
        help='Storage prefix (default: /local-files/)'
    )
    
    args = parser.parse_args()
    
    create_local_storage_import(
        video_dir=args.dir,
        output_file=args.output,
        storage_prefix=args.prefix
    )

if __name__ == '__main__':
    main()


