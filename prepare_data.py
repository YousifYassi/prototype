"""
Data preparation script for BDD100K dataset
Converts annotations to the format expected by the training pipeline
"""
import os
import json
import argparse
from pathlib import Path
from collections import defaultdict
import random


def create_sample_annotations(root_dir, output_file):
    """
    Create sample annotations file for BDD100K dataset
    This is a template - you'll need to adapt it to your actual annotation format
    
    Args:
        root_dir: Root directory of BDD100K dataset
        output_file: Path to save annotations JSON
    """
    root_dir = Path(root_dir)
    video_dir = root_dir / 'videos'
    
    # Define unsafe action classes
    unsafe_actions = [
        "aggressive_driving",
        "tailgating",
        "unsafe_lane_change",
        "running_red_light",
        "distracted_driver",
        "speeding",
        "wrong_way_driving",
        "pedestrian_collision_risk",
        "near_miss"
    ]
    
    annotations = {
        'train': [],
        'val': [],
        'test': []
    }
    
    # Check if video directory exists
    if not video_dir.exists():
        print(f"Video directory not found: {video_dir}")
        print("Creating sample annotation structure...")
        
        # Create sample structure
        for split in ['train', 'val', 'test']:
            split_dir = video_dir / split
            split_dir.mkdir(parents=True, exist_ok=True)
            
            # Create sample annotations (you'll replace this with actual data)
            num_samples = 100 if split == 'train' else 20
            for i in range(num_samples):
                video_name = f"{split}_video_{i:04d}.mp4"
                # Random label (0 = safe, 1-9 = unsafe actions)
                label = random.randint(0, len(unsafe_actions))
                
                annotations[split].append({
                    'video_name': video_name,
                    'label': label,
                    'action_name': unsafe_actions[label-1] if label > 0 else 'safe'
                })
    else:
        # Parse existing videos
        for split in ['train', 'val', 'test']:
            split_dir = video_dir / split
            if split_dir.exists():
                video_files = list(split_dir.glob('*.mp4')) + list(split_dir.glob('*.avi'))
                
                for video_file in video_files:
                    # You'll need to load actual labels from your annotation files
                    # This is just a placeholder
                    annotations[split].append({
                        'video_name': video_file.name,
                        'label': 0,  # Default to safe
                        'action_name': 'safe'
                    })
    
    # Save annotations
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(annotations, f, indent=2)
    
    print(f"Annotations saved to: {output_file}")
    print(f"Train samples: {len(annotations['train'])}")
    print(f"Val samples: {len(annotations['val'])}")
    print(f"Test samples: {len(annotations['test'])}")


def convert_bdd100k_labels(bdd_labels_file, output_file, video_dir):
    """
    Convert BDD100K detection labels to action detection format
    You'll need to define rules for what constitutes unsafe actions
    
    Args:
        bdd_labels_file: Path to BDD100K labels JSON
        output_file: Path to save converted annotations
        video_dir: Directory containing videos
    """
    print("Converting BDD100K labels...")
    
    # Load BDD100K labels
    with open(bdd_labels_file, 'r') as f:
        bdd_labels = json.load(f)
    
    # Define unsafe action detection rules based on object detections
    # This is an example - customize based on your needs
    def detect_unsafe_action(frame_labels):
        """
        Detect unsafe actions based on object detections and attributes
        Returns: (action_label, action_name)
        """
        # Example rules:
        # - Check for close proximity of vehicles (tailgating)
        # - Check for pedestrians near vehicle path (collision risk)
        # - Check for traffic light state (running red light)
        # etc.
        
        # Placeholder: default to safe
        return 0, 'safe'
    
    annotations = defaultdict(list)
    
    for item in bdd_labels:
        video_name = item.get('name', item.get('video_name', ''))
        
        # Detect unsafe action
        action_label, action_name = detect_unsafe_action(item)
        
        # Determine split (you may have this info in your dataset)
        split = 'train'  # Default
        
        annotations[split].append({
            'video_name': video_name,
            'label': action_label,
            'action_name': action_name
        })
    
    # Save
    with open(output_file, 'w') as f:
        json.dump(dict(annotations), f, indent=2)
    
    print(f"Converted annotations saved to: {output_file}")


def split_dataset(annotations_file, train_ratio=0.8, val_ratio=0.1, test_ratio=0.1):
    """
    Split dataset into train/val/test sets
    
    Args:
        annotations_file: Path to annotations file
        train_ratio: Ratio of training data
        val_ratio: Ratio of validation data
        test_ratio: Ratio of test data
    """
    with open(annotations_file, 'r') as f:
        annotations = json.load(f)
    
    # If already split, return
    if isinstance(annotations, dict) and 'train' in annotations:
        print("Dataset already split")
        return
    
    # Combine all annotations
    all_annotations = []
    if isinstance(annotations, list):
        all_annotations = annotations
    else:
        for split in annotations.values():
            all_annotations.extend(split)
    
    # Shuffle
    random.shuffle(all_annotations)
    
    # Split
    n = len(all_annotations)
    train_end = int(n * train_ratio)
    val_end = train_end + int(n * val_ratio)
    
    split_annotations = {
        'train': all_annotations[:train_end],
        'val': all_annotations[train_end:val_end],
        'test': all_annotations[val_end:]
    }
    
    # Save
    with open(annotations_file, 'w') as f:
        json.dump(split_annotations, f, indent=2)
    
    print(f"Dataset split complete:")
    print(f"  Train: {len(split_annotations['train'])}")
    print(f"  Val: {len(split_annotations['val'])}")
    print(f"  Test: {len(split_annotations['test'])}")


def main():
    parser = argparse.ArgumentParser(description='Prepare data for training')
    parser.add_argument('--root_dir', type=str, default='datasets/bdd100k',
                       help='Root directory of BDD100K dataset')
    parser.add_argument('--output', type=str, default='datasets/bdd100k/annotations.json',
                       help='Output path for annotations file')
    parser.add_argument('--bdd_labels', type=str, default=None,
                       help='Path to BDD100K labels file (if converting)')
    parser.add_argument('--split', action='store_true',
                       help='Split dataset into train/val/test')
    
    args = parser.parse_args()
    
    if args.bdd_labels and os.path.exists(args.bdd_labels):
        # Convert existing BDD100K labels
        convert_bdd100k_labels(args.bdd_labels, args.output, args.root_dir)
    else:
        # Create sample annotations
        create_sample_annotations(args.root_dir, args.output)
    
    if args.split:
        split_dataset(args.output)


if __name__ == '__main__':
    main()

