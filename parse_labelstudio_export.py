"""
Parse Label Studio JSON export and prepare training data for unsafe behavior detection.

This script:
1. Reads the Label Studio export JSON
2. Extracts video paths and timeline annotations
3. Creates a structured dataset for training
4. Generates frame-level labels for each video segment
"""
import json
import os
import urllib.parse
from pathlib import Path
from collections import defaultdict
import shutil


def decode_labelstudio_path(ls_path: str) -> str:
    """
    Decode Label Studio local file path to actual file system path.
    
    Label Studio encodes paths like:
    /data/local-files/?d=Users%5Cyousi%5Cprototype%5C...
    
    This decodes to: C:/Users/yousi/prototype/...
    """
    # Extract the 'd' parameter
    if '/data/local-files/?d=' in ls_path:
        encoded_path = ls_path.split('/data/local-files/?d=')[1]
        # URL decode the path
        decoded_path = urllib.parse.unquote(encoded_path)
        # Convert to proper Windows path with drive letter
        # The path starts without drive letter, so we add C:
        full_path = f"C:/{decoded_path}"
        # Normalize path separators
        full_path = full_path.replace('\\', '/')
        return full_path
    elif ls_path.startswith('http'):
        # HTTP URL - extract filename and look for it locally
        return ls_path
    else:
        return ls_path


def parse_labelstudio_export(json_path: str) -> dict:
    """
    Parse Label Studio JSON export and extract annotations.
    
    Args:
        json_path: Path to the exported JSON file
        
    Returns:
        Dictionary with parsed annotations and statistics
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Define label mapping
    label_mapping = {
        'Safe': 0,
        'No PPE - Missing Gloves': 1,
        'No PPE - Missing Helmet': 2,
        'No PPE - Missing Safety Glasses': 3,
        'No PPE - Missing High Visibility Vest': 4,
        'Other Violation': 5,
        'Unsafe Behavior': 6,
        'Near Miss': 7,
    }
    
    annotations = []
    label_counts = defaultdict(int)
    videos_found = 0
    videos_missing = 0
    
    print(f"Processing {len(data)} tasks from Label Studio export...")
    
    for task in data:
        task_id = task.get('id')
        video_data = task.get('data', {})
        video_ls_path = video_data.get('video', '')
        
        # Decode the Label Studio path
        video_path = decode_labelstudio_path(video_ls_path)
        
        # Check if video exists
        video_exists = os.path.exists(video_path)
        if video_exists:
            videos_found += 1
        else:
            videos_missing += 1
            print(f"  Warning: Video not found: {video_path}")
        
        # Get annotations
        task_annotations = task.get('annotations', [])
        
        for ann in task_annotations:
            results = ann.get('result', [])
            
            for result in results:
                result_type = result.get('type')
                
                if result_type == 'timelinelabels':
                    # Timeline labels with frame ranges
                    value = result.get('value', {})
                    labels = value.get('timelinelabels', [])
                    ranges = value.get('ranges', [])
                    
                    for label in labels:
                        # Map label to numeric ID
                        label_id = label_mapping.get(label, label_mapping.get('Other Violation', 5))
                        label_counts[label] += 1
                        
                        for frame_range in ranges:
                            start_frame = frame_range.get('start', 0)
                            end_frame = frame_range.get('end', 0)
                            
                            annotations.append({
                                'task_id': task_id,
                                'video_path': video_path,
                                'video_exists': video_exists,
                                'label': label,
                                'label_id': label_id,
                                'start_frame': start_frame,
                                'end_frame': end_frame,
                                'frame_count': end_frame - start_frame
                            })
    
    # Create summary
    result = {
        'annotations': annotations,
        'label_mapping': label_mapping,
        'label_counts': dict(label_counts),
        'videos_found': videos_found,
        'videos_missing': videos_missing,
        'total_videos': len(data),
        'total_annotations': len(annotations)
    }
    
    return result


def create_training_json(parsed_data: dict, output_path: str):
    """
    Create a training-ready JSON file with video segments and labels.
    
    Args:
        parsed_data: Output from parse_labelstudio_export
        output_path: Path to save the training JSON
    """
    training_data = {
        'label_mapping': parsed_data['label_mapping'],
        'samples': []
    }
    
    for ann in parsed_data['annotations']:
        if ann['video_exists']:
            sample = {
                'video_path': ann['video_path'],
                'label': ann['label'],
                'label_id': ann['label_id'],
                'start_frame': ann['start_frame'],
                'end_frame': ann['end_frame']
            }
            training_data['samples'].append(sample)
    
    # Save to file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(training_data, f, indent=2)
    
    print(f"Saved training data to: {output_path}")
    return training_data


def print_summary(parsed_data: dict):
    """Print summary of parsed annotations."""
    print("\n" + "=" * 60)
    print("LABEL STUDIO EXPORT SUMMARY")
    print("=" * 60)
    print(f"\nTotal videos: {parsed_data['total_videos']}")
    print(f"Videos found: {parsed_data['videos_found']}")
    print(f"Videos missing: {parsed_data['videos_missing']}")
    print(f"Total annotation segments: {parsed_data['total_annotations']}")
    
    print("\nLabel distribution:")
    print("-" * 40)
    for label, count in sorted(parsed_data['label_counts'].items()):
        print(f"  {label}: {count}")
    
    print("\nLabel ID mapping:")
    print("-" * 40)
    for label, label_id in parsed_data['label_mapping'].items():
        print(f"  {label_id}: {label}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Parse Label Studio export for training')
    parser.add_argument('--input', '-i', type=str, 
                        default=r'C:\Users\yousi\Downloads\project-1-at-2025-12-17-13-45-ec1123a5.json',
                        help='Path to Label Studio JSON export')
    parser.add_argument('--output', '-o', type=str,
                        default='training_data.json',
                        help='Output path for training JSON')
    
    args = parser.parse_args()
    
    print(f"Parsing Label Studio export: {args.input}")
    
    # Parse the export
    parsed_data = parse_labelstudio_export(args.input)
    
    # Print summary
    print_summary(parsed_data)
    
    # Create training JSON
    training_data = create_training_json(parsed_data, args.output)
    
    print(f"\n[OK] Created training data with {len(training_data['samples'])} samples")
    
    # Check for missing videos
    if parsed_data['videos_missing'] > 0:
        print("\n[WARNING] Some videos are missing!")
        print("   Please ensure the video files exist at the expected paths.")
        print("   You may need to download or move the CharadesEgo dataset.")
        
        # List missing videos
        missing_videos = set()
        for ann in parsed_data['annotations']:
            if not ann['video_exists']:
                missing_videos.add(ann['video_path'])
        
        print("\n   Missing videos:")
        for v in sorted(missing_videos):
            print(f"   - {v}")
    
    return parsed_data


if __name__ == '__main__':
    main()
