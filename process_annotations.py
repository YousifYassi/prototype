#!/usr/bin/env python3
"""
Process Label Studio annotations and prepare them for model training
"""

import json
import argparse
from pathlib import Path
from collections import Counter
import csv


def load_annotations(export_file):
    """Load Label Studio export file"""
    with open(export_file, 'r') as f:
        return json.load(f)


def process_annotations(annotations):
    """Process annotations into training format"""
    training_data = []
    
    for item in annotations:
        # Skip unannotated items
        if 'annotations' not in item or not item['annotations']:
            continue
        
        video_path = item['data']['video'].replace('file:///', '').replace('file://', '')
        
        # Extract labels and metadata
        labels = []
        severity = 0
        notes = ""
        bounding_boxes = []
        
        for result in item['annotations'][0]['result']:
            if result['from_name'] == 'action' and result['type'] == 'choices':
                labels = result['value']['choices']
            elif result['from_name'] == 'severity' and result['type'] == 'rating':
                severity = result['value']['rating']
            elif result['from_name'] == 'notes' and result['type'] == 'textarea':
                notes = result['value'].get('text', [''])[0] if isinstance(result['value'].get('text'), list) else result['value'].get('text', '')
            elif result['from_name'] == 'box' and result['type'] == 'videorectangle':
                bounding_boxes.append(result['value'])
        
        training_data.append({
            'video_path': video_path,
            'filename': Path(video_path).name,
            'labels': labels,
            'severity': severity,
            'notes': notes,
            'has_bounding_boxes': len(bounding_boxes) > 0,
            'num_bounding_boxes': len(bounding_boxes),
            'bounding_boxes': bounding_boxes
        })
    
    return training_data


def generate_statistics(training_data):
    """Generate annotation statistics"""
    stats = {
        'total_annotated': len(training_data),
        'label_distribution': Counter(),
        'severity_distribution': Counter(),
        'avg_severity': 0,
        'videos_with_boxes': 0
    }
    
    all_labels = []
    all_severities = []
    
    for item in training_data:
        # Count labels
        for label in item['labels']:
            stats['label_distribution'][label] += 1
            all_labels.append(label)
        
        # Count severity
        if item['severity'] > 0:
            stats['severity_distribution'][item['severity']] += 1
            all_severities.append(item['severity'])
        
        # Count bounding boxes
        if item['has_bounding_boxes']:
            stats['videos_with_boxes'] += 1
    
    if all_severities:
        stats['avg_severity'] = sum(all_severities) / len(all_severities)
    
    return stats


def save_training_data(training_data, output_file):
    """Save processed training data"""
    with open(output_file, 'w') as f:
        json.dump(training_data, f, indent=2)
    print(f"✓ Saved {len(training_data)} annotations to {output_file}")


def save_csv(training_data, output_file):
    """Save data as CSV for easy viewing"""
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['filename', 'labels', 'severity', 'notes', 'num_bounding_boxes']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        writer.writeheader()
        for item in training_data:
            writer.writerow({
                'filename': item['filename'],
                'labels': '; '.join(item['labels']),
                'severity': item['severity'],
                'notes': item['notes'],
                'num_bounding_boxes': item['num_bounding_boxes']
            })
    print(f"✓ Saved CSV summary to {output_file}")


def print_statistics(stats):
    """Print annotation statistics"""
    print("\n" + "=" * 60)
    print("ANNOTATION STATISTICS")
    print("=" * 60)
    
    print(f"\n📊 Total Annotated Videos: {stats['total_annotated']}")
    print(f"📦 Videos with Bounding Boxes: {stats['videos_with_boxes']}")
    
    if stats['avg_severity'] > 0:
        print(f"⭐ Average Severity: {stats['avg_severity']:.2f}/5")
    
    print("\n🏷️  Label Distribution:")
    print("-" * 60)
    for label, count in stats['label_distribution'].most_common():
        percentage = (count / stats['total_annotated']) * 100
        print(f"  {label:40s} {count:5d} ({percentage:5.1f}%)")
    
    if stats['severity_distribution']:
        print("\n⭐ Severity Distribution:")
        print("-" * 60)
        for severity in sorted(stats['severity_distribution'].keys()):
            count = stats['severity_distribution'][severity]
            percentage = (count / len(stats['severity_distribution'])) * 100
            stars = "★" * severity + "☆" * (5 - severity)
            print(f"  {stars:15s} {count:5d} ({percentage:5.1f}%)")
    
    print("=" * 60)


def create_class_mapping(training_data):
    """Create a class mapping file for training"""
    all_labels = set()
    for item in training_data:
        all_labels.update(item['labels'])
    
    class_mapping = {label: idx for idx, label in enumerate(sorted(all_labels))}
    
    with open('class_mapping.json', 'w') as f:
        json.dump(class_mapping, f, indent=2)
    
    print(f"\n✓ Created class mapping with {len(class_mapping)} classes")
    return class_mapping


def main():
    parser = argparse.ArgumentParser(
        description='Process Label Studio annotations for model training'
    )
    parser.add_argument(
        'export_file',
        help='Label Studio export file (JSON format)'
    )
    parser.add_argument(
        '--output', '-o',
        default='training_annotations.json',
        help='Output file for processed annotations (default: training_annotations.json)'
    )
    parser.add_argument(
        '--csv',
        help='Also save as CSV for easy viewing'
    )
    parser.add_argument(
        '--stats-only',
        action='store_true',
        help='Only show statistics, don\'t save files'
    )
    
    args = parser.parse_args()
    
    # Check if export file exists
    if not Path(args.export_file).exists():
        print(f"❌ Error: File '{args.export_file}' not found")
        print("\nTo export from Label Studio:")
        print("  1. Go to your project")
        print("  2. Click 'Export'")
        print("  3. Select 'JSON' format")
        print("  4. Download the file")
        return
    
    print(f"📂 Loading annotations from {args.export_file}...")
    annotations = load_annotations(args.export_file)
    print(f"✓ Loaded {len(annotations)} items")
    
    print("\n🔄 Processing annotations...")
    training_data = process_annotations(annotations)
    
    if not training_data:
        print("❌ No annotated videos found in export file")
        print("Make sure you have submitted annotations in Label Studio")
        return
    
    print(f"✓ Processed {len(training_data)} annotated videos")
    
    # Generate and display statistics
    stats = generate_statistics(training_data)
    print_statistics(stats)
    
    if not args.stats_only:
        # Save training data
        save_training_data(training_data, args.output)
        
        # Save CSV if requested
        if args.csv:
            save_csv(training_data, args.csv)
        
        # Create class mapping
        create_class_mapping(training_data)
        
        print("\n✅ Processing complete!")
        print(f"\nNext steps:")
        print(f"  1. Review {args.output} to verify annotations")
        print(f"  2. Use this data to train your model")
        print(f"  3. Check class_mapping.json for label indices")


if __name__ == '__main__':
    main()

