"""
Dataset class for loading video data from Label Studio timeline annotations.
Handles video segment extraction based on frame ranges from Label Studio exports.
"""
import os
import json
import cv2
import torch
import numpy as np
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
import albumentations as A
from pathlib import Path
import urllib.parse
from typing import List, Dict, Tuple, Optional


def decode_labelstudio_path(ls_path: str) -> str:
    """
    Decode Label Studio local file path to actual file system path.
    """
    if '/data/local-files/?d=' in ls_path:
        encoded_path = ls_path.split('/data/local-files/?d=')[1]
        decoded_path = urllib.parse.unquote(encoded_path)
        full_path = f"C:/{decoded_path}"
        full_path = full_path.replace('\\', '/')
        return full_path
    return ls_path


class LabelStudioVideoDataset(Dataset):
    """
    Dataset for loading video segments from Label Studio timeline annotations.
    
    This dataset:
    1. Parses Label Studio JSON export directly
    2. Extracts video clips from annotated frame ranges
    3. Supports multiple labels per video
    4. Handles both annotated (unsafe) and unannotated (safe) segments
    """
    
    # Default label mapping for safety violations
    DEFAULT_LABEL_MAPPING = {
        'Safe': 0,
        'No PPE - Missing Gloves': 1,
        'No PPE - Missing Helmet': 2,
        'No PPE - Missing Safety Glasses': 3,
        'No PPE - Missing High Visibility Vest': 4,
        'Other Violation': 5,
        'Unsafe Behavior': 6,
        'Near Miss': 7,
    }
    
    def __init__(
        self,
        labelstudio_json_path: str,
        num_frames: int = 16,
        frame_interval: int = 2,
        input_size: Tuple[int, int] = (224, 224),
        augment: bool = False,
        include_safe_segments: bool = True,
        min_segment_frames: int = 16,
        label_mapping: Optional[Dict[str, int]] = None
    ):
        """
        Args:
            labelstudio_json_path: Path to Label Studio JSON export
            num_frames: Number of frames to sample from each segment
            frame_interval: Interval between sampled frames
            input_size: Target frame size (H, W)
            augment: Whether to apply data augmentation
            include_safe_segments: Whether to include unannotated segments as 'safe'
            min_segment_frames: Minimum frames required for a valid segment
            label_mapping: Custom label to ID mapping (uses default if None)
        """
        self.labelstudio_json_path = labelstudio_json_path
        self.num_frames = num_frames
        self.frame_interval = frame_interval
        self.input_size = input_size
        self.augment = augment
        self.include_safe_segments = include_safe_segments
        self.min_segment_frames = min_segment_frames
        self.label_mapping = label_mapping or self.DEFAULT_LABEL_MAPPING
        
        # Parse annotations
        self.samples = self._parse_labelstudio_export()
        
        # Setup transforms
        self.transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize(input_size),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ])
        
        # Augmentation pipeline
        if augment:
            self.aug_transform = A.Compose([
                A.HorizontalFlip(p=0.5),
                A.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1, p=0.5),
                A.Rotate(limit=10, p=0.3),
                A.GaussNoise(var_limit=(10, 50), p=0.2),
            ])
        
        print(f"Loaded {len(self.samples)} samples from Label Studio export")
    
    def _parse_labelstudio_export(self) -> List[Dict]:
        """Parse Label Studio JSON export and create sample list."""
        with open(self.labelstudio_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        samples = []
        skipped_videos = 0
        
        for task in data:
            video_ls_path = task.get('data', {}).get('video', '')
            video_path = decode_labelstudio_path(video_ls_path)
            
            # Check if video exists
            if not os.path.exists(video_path):
                skipped_videos += 1
                continue
            
            # Get video metadata
            video_info = self._get_video_info(video_path)
            if video_info is None:
                skipped_videos += 1
                continue
            
            total_frames = video_info['total_frames']
            fps = video_info['fps']
            
            # Track annotated frame ranges
            annotated_ranges = []
            
            # Process annotations
            for ann in task.get('annotations', []):
                for result in ann.get('result', []):
                    if result.get('type') == 'timelinelabels':
                        value = result.get('value', {})
                        labels = value.get('timelinelabels', [])
                        ranges = value.get('ranges', [])
                        
                        for label in labels:
                            label_id = self.label_mapping.get(
                                label, 
                                self.label_mapping.get('Other Violation', 5)
                            )
                            
                            for frame_range in ranges:
                                start = frame_range.get('start', 0)
                                end = frame_range.get('end', total_frames)
                                
                                # Ensure valid range
                                start = max(0, min(start, total_frames - 1))
                                end = max(start + 1, min(end, total_frames))
                                
                                if end - start >= self.min_segment_frames:
                                    samples.append({
                                        'video_path': video_path,
                                        'start_frame': start,
                                        'end_frame': end,
                                        'label': label,
                                        'label_id': label_id,
                                        'fps': fps
                                    })
                                    annotated_ranges.append((start, end))
            
            # Add safe segments (unannotated portions)
            if self.include_safe_segments:
                safe_segments = self._find_safe_segments(
                    annotated_ranges, total_frames
                )
                for start, end in safe_segments:
                    if end - start >= self.min_segment_frames:
                        samples.append({
                            'video_path': video_path,
                            'start_frame': start,
                            'end_frame': end,
                            'label': 'Safe',
                            'label_id': 0,
                            'fps': fps
                        })
        
        if skipped_videos > 0:
            print(f"Warning: Skipped {skipped_videos} videos (not found or invalid)")
        
        return samples
    
    def _get_video_info(self, video_path: str) -> Optional[Dict]:
        """Get video metadata."""
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return None
            
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            cap.release()
            
            if total_frames <= 0:
                return None
            
            return {
                'total_frames': total_frames,
                'fps': fps,
                'width': width,
                'height': height
            }
        except Exception as e:
            print(f"Error reading video {video_path}: {e}")
            return None
    
    def _find_safe_segments(
        self, 
        annotated_ranges: List[Tuple[int, int]], 
        total_frames: int
    ) -> List[Tuple[int, int]]:
        """Find unannotated (safe) segments in the video."""
        if not annotated_ranges:
            # Entire video is safe
            return [(0, total_frames)]
        
        # Sort and merge overlapping ranges
        sorted_ranges = sorted(annotated_ranges)
        merged = [sorted_ranges[0]]
        
        for start, end in sorted_ranges[1:]:
            if start <= merged[-1][1]:
                merged[-1] = (merged[-1][0], max(merged[-1][1], end))
            else:
                merged.append((start, end))
        
        # Find gaps (safe segments)
        safe_segments = []
        current_pos = 0
        
        for start, end in merged:
            if current_pos < start:
                safe_segments.append((current_pos, start))
            current_pos = max(current_pos, end)
        
        if current_pos < total_frames:
            safe_segments.append((current_pos, total_frames))
        
        return safe_segments
    
    def __len__(self):
        return len(self.samples)
    
    def _get_frame_indices(self, start_frame: int, end_frame: int) -> np.ndarray:
        """Calculate which frames to sample from the segment."""
        segment_length = end_frame - start_frame
        required_length = self.num_frames * self.frame_interval
        
        if segment_length <= required_length:
            # Not enough frames, sample with interpolation
            indices = np.linspace(start_frame, end_frame - 1, self.num_frames)
        else:
            # Randomly select starting point (or center if not augmenting)
            max_start = segment_length - required_length
            if self.augment:
                offset = np.random.randint(0, max_start + 1)
            else:
                offset = max_start // 2
            indices = np.arange(offset, offset + required_length, self.frame_interval)
            indices = indices + start_frame
        
        return indices.astype(int)[:self.num_frames]
    
    def _load_frames(self, video_path: str, indices: np.ndarray) -> List[np.ndarray]:
        """Load specific frames from video."""
        frames = []
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            return frames
        
        for idx in indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ret, frame = cap.read()
            if ret and frame is not None:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frames.append(frame)
        
        cap.release()
        
        # Pad if needed
        while len(frames) < self.num_frames:
            if frames:
                frames.append(frames[-1].copy())
            else:
                frames.append(np.zeros((*self.input_size, 3), dtype=np.uint8))
        
        return frames[:self.num_frames]
    
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        sample = self.samples[idx]
        
        # Get frame indices
        indices = self._get_frame_indices(
            sample['start_frame'], 
            sample['end_frame']
        )
        
        # Load frames
        frames = self._load_frames(sample['video_path'], indices)
        
        # Process frames
        processed_frames = []
        for frame in frames:
            # Apply augmentation
            if self.augment and hasattr(self, 'aug_transform'):
                try:
                    augmented = self.aug_transform(image=frame)
                    frame = augmented['image']
                except Exception:
                    pass
            
            # Apply transforms
            frame_tensor = self.transform(frame)
            processed_frames.append(frame_tensor)
        
        # Stack frames: (T, C, H, W)
        video_tensor = torch.stack(processed_frames)
        label_tensor = torch.tensor(sample['label_id'], dtype=torch.long)
        
        return video_tensor, label_tensor
    
    def get_label_distribution(self) -> Dict[str, int]:
        """Get distribution of labels in the dataset."""
        distribution = {}
        for sample in self.samples:
            label = sample['label']
            distribution[label] = distribution.get(label, 0) + 1
        return distribution
    
    def get_num_classes(self) -> int:
        """Get number of unique classes in the dataset."""
        label_ids = set(sample['label_id'] for sample in self.samples)
        return max(label_ids) + 1


def create_labelstudio_dataloaders(
    labelstudio_json_path: str,
    batch_size: int = 4,
    num_workers: int = 4,
    num_frames: int = 16,
    frame_interval: int = 2,
    input_size: Tuple[int, int] = (224, 224),
    train_split: float = 0.8,
    include_safe_segments: bool = True
) -> Tuple[DataLoader, DataLoader]:
    """
    Create train and validation dataloaders from Label Studio export.
    
    Args:
        labelstudio_json_path: Path to Label Studio JSON export
        batch_size: Batch size for training
        num_workers: Number of data loading workers
        num_frames: Frames per clip
        frame_interval: Interval between frames
        input_size: Frame size (H, W)
        train_split: Fraction for training (rest is validation)
        include_safe_segments: Include unannotated segments as 'safe'
    
    Returns:
        train_loader, val_loader
    """
    # Create full dataset (without augmentation first for splitting)
    full_dataset = LabelStudioVideoDataset(
        labelstudio_json_path=labelstudio_json_path,
        num_frames=num_frames,
        frame_interval=frame_interval,
        input_size=input_size,
        augment=False,
        include_safe_segments=include_safe_segments
    )
    
    # Print label distribution
    print("\nLabel distribution:")
    for label, count in full_dataset.get_label_distribution().items():
        print(f"  {label}: {count}")
    
    # Split indices
    total_samples = len(full_dataset)
    indices = np.random.RandomState(42).permutation(total_samples)
    train_size = int(total_samples * train_split)
    
    train_indices = indices[:train_size].tolist()
    val_indices = indices[train_size:].tolist()
    
    # Get samples for train and val
    train_samples = [full_dataset.samples[i] for i in train_indices]
    val_samples = [full_dataset.samples[i] for i in val_indices]
    
    # Create separate datasets with appropriate augmentation
    train_dataset = LabelStudioVideoDataset.__new__(LabelStudioVideoDataset)
    train_dataset.samples = train_samples
    train_dataset.num_frames = num_frames
    train_dataset.frame_interval = frame_interval
    train_dataset.input_size = input_size
    train_dataset.augment = True
    train_dataset.label_mapping = full_dataset.label_mapping
    train_dataset.transform = full_dataset.transform
    train_dataset.aug_transform = A.Compose([
        A.HorizontalFlip(p=0.5),
        A.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1, p=0.5),
        A.Rotate(limit=10, p=0.3),
    ])
    
    val_dataset = LabelStudioVideoDataset.__new__(LabelStudioVideoDataset)
    val_dataset.samples = val_samples
    val_dataset.num_frames = num_frames
    val_dataset.frame_interval = frame_interval
    val_dataset.input_size = input_size
    val_dataset.augment = False
    val_dataset.label_mapping = full_dataset.label_mapping
    val_dataset.transform = full_dataset.transform
    
    print(f"\nTraining samples: {len(train_dataset)}")
    print(f"Validation samples: {len(val_dataset)}")
    
    # Create dataloaders
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=True
    )
    
    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=True
    )
    
    return train_loader, val_loader


if __name__ == '__main__':
    # Test the dataset
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--json', type=str, 
                        default=r'C:\Users\yousi\Downloads\project-1-at-2025-12-17-13-45-ec1123a5.json')
    args = parser.parse_args()
    
    print(f"Testing LabelStudioVideoDataset with: {args.json}")
    
    dataset = LabelStudioVideoDataset(
        labelstudio_json_path=args.json,
        num_frames=16,
        augment=False,
        include_safe_segments=True
    )
    
    print(f"\nTotal samples: {len(dataset)}")
    print(f"Number of classes: {dataset.get_num_classes()}")
    print(f"\nLabel distribution:")
    for label, count in dataset.get_label_distribution().items():
        print(f"  {label}: {count}")
    
    if len(dataset) > 0:
        print("\nTesting data loading...")
        video, label = dataset[0]
        print(f"Video tensor shape: {video.shape}")
        print(f"Label: {label.item()}")
