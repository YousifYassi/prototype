"""
Dataset classes for loading video data for unsafe action detection
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


class VideoActionDataset(Dataset):
    """
    Dataset for loading video clips with action labels
    Supports both video files and image sequences
    """
    
    def __init__(self, video_paths, labels, num_frames=16, frame_interval=2, 
                 input_size=(224, 224), augment=False):
        """
        Args:
            video_paths: List of paths to video files or directories with frames
            labels: List of corresponding action labels
            num_frames: Number of frames to sample from each video
            frame_interval: Interval between sampled frames
            input_size: Target size for frames (H, W)
            augment: Whether to apply data augmentation
        """
        self.video_paths = video_paths
        self.labels = labels
        self.num_frames = num_frames
        self.frame_interval = frame_interval
        self.input_size = input_size
        self.augment = augment
        
        # Define transforms
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
            ])
    
    def __len__(self):
        return len(self.video_paths)
    
    def load_video(self, video_path):
        """Load video and extract frames"""
        frames = []
        
        if os.path.isfile(video_path):
            # Load from video file
            cap = cv2.VideoCapture(video_path)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Calculate indices to sample
            indices = self._get_frame_indices(total_frames)
            
            for idx in indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
                ret, frame = cap.read()
                if ret:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frames.append(frame)
            
            cap.release()
        else:
            # Load from image sequence directory
            frame_files = sorted([f for f in os.listdir(video_path) 
                                if f.endswith(('.jpg', '.png'))])
            indices = self._get_frame_indices(len(frame_files))
            
            for idx in indices:
                frame_path = os.path.join(video_path, frame_files[idx])
                frame = cv2.imread(frame_path)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frames.append(frame)
        
        # Pad if not enough frames
        while len(frames) < self.num_frames:
            frames.append(frames[-1] if frames else np.zeros((224, 224, 3), dtype=np.uint8))
        
        return frames[:self.num_frames]
    
    def _get_frame_indices(self, total_frames):
        """Calculate which frames to sample from video"""
        required_length = self.num_frames * self.frame_interval
        
        if total_frames <= required_length:
            # Not enough frames, sample with repetition
            indices = np.linspace(0, max(0, total_frames - 1), self.num_frames).astype(int)
        else:
            # Randomly select a starting point
            max_start = total_frames - required_length
            start_idx = np.random.randint(0, max_start + 1) if self.augment else max_start // 2
            indices = np.arange(start_idx, start_idx + required_length, self.frame_interval)
        
        return indices[:self.num_frames]
    
    def __getitem__(self, idx):
        video_path = self.video_paths[idx]
        label = self.labels[idx]
        
        # Load frames
        frames = self.load_video(video_path)
        
        # Apply augmentation to each frame
        processed_frames = []
        for frame in frames:
            if self.augment and hasattr(self, 'aug_transform'):
                augmented = self.aug_transform(image=frame)
                frame = augmented['image']
            
            # Apply normalization
            frame_tensor = self.transform(frame)
            processed_frames.append(frame_tensor)
        
        # Stack frames: (T, C, H, W)
        video_tensor = torch.stack(processed_frames)
        
        return video_tensor, torch.tensor(label, dtype=torch.long)


class BDD100KActionDataset(VideoActionDataset):
    """
    BDD100K specific dataset for unsafe driving action detection
    """
    
    def __init__(self, root_dir, annotations_file, split='train', **kwargs):
        """
        Args:
            root_dir: Root directory of BDD100K dataset
            annotations_file: Path to annotations JSON file
            split: 'train', 'val', or 'test'
        """
        self.root_dir = Path(root_dir)
        self.split = split
        
        # Load annotations
        if os.path.exists(annotations_file):
            with open(annotations_file, 'r') as f:
                self.annotations = json.load(f)
        else:
            print(f"Warning: Annotations file {annotations_file} not found.")
            self.annotations = {}
        
        # Parse video paths and labels
        video_paths, labels = self._parse_annotations()
        
        super().__init__(video_paths, labels, **kwargs)
    
    def _parse_annotations(self):
        """Parse BDD100K annotations for unsafe actions"""
        video_paths = []
        labels = []
        
        # If annotations exist, parse them
        if self.annotations:
            for item in self.annotations.get(self.split, []):
                video_path = self.root_dir / 'videos' / item.get('video_name', '')
                if video_path.exists():
                    video_paths.append(str(video_path))
                    labels.append(item.get('label', 0))
        else:
            # Fallback: scan for video files
            video_dir = self.root_dir / 'videos' / self.split
            if video_dir.exists():
                for video_file in video_dir.glob('*.mp4'):
                    video_paths.append(str(video_file))
                    labels.append(0)  # Default safe class
        
        return video_paths, labels


class StreamVideoBuffer:
    """
    Buffer for processing real-time video streams
    Maintains a sliding window of frames for temporal analysis
    """
    
    def __init__(self, buffer_size=32, num_frames=16, frame_interval=2):
        self.buffer_size = buffer_size
        self.num_frames = num_frames
        self.frame_interval = frame_interval
        self.buffer = []
        
        self.transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ])
    
    def add_frame(self, frame):
        """Add a new frame to the buffer"""
        self.buffer.append(frame)
        if len(self.buffer) > self.buffer_size:
            self.buffer.pop(0)
    
    def get_clip(self):
        """Get a clip of frames for model inference"""
        if len(self.buffer) < self.num_frames:
            return None
        
        # Sample frames from buffer
        indices = np.linspace(0, len(self.buffer) - 1, self.num_frames).astype(int)
        frames = [self.buffer[i] for i in indices]
        
        # Process frames
        processed_frames = []
        for frame in frames:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_tensor = self.transform(frame_rgb)
            processed_frames.append(frame_tensor)
        
        # Stack: (T, C, H, W)
        clip_tensor = torch.stack(processed_frames)
        return clip_tensor.unsqueeze(0)  # Add batch dimension: (1, T, C, H, W)
    
    def clear(self):
        """Clear the buffer"""
        self.buffer = []


def create_dataloaders(config):
    """
    Create train, validation, and test dataloaders
    """
    dataset_config = config['dataset']
    model_config = config['model']
    training_config = config['training']
    
    # Create datasets
    train_dataset = BDD100KActionDataset(
        root_dir=dataset_config['root_dir'],
        annotations_file=dataset_config['annotations_file'],
        split='train',
        num_frames=model_config['num_frames'],
        frame_interval=model_config['frame_interval'],
        input_size=tuple(model_config['input_size']),
        augment=True
    )
    
    val_dataset = BDD100KActionDataset(
        root_dir=dataset_config['root_dir'],
        annotations_file=dataset_config['annotations_file'],
        split='val',
        num_frames=model_config['num_frames'],
        frame_interval=model_config['frame_interval'],
        input_size=tuple(model_config['input_size']),
        augment=False
    )
    
    # Create dataloaders
    train_loader = DataLoader(
        train_dataset,
        batch_size=training_config['batch_size'],
        shuffle=True,
        num_workers=training_config['num_workers'],
        pin_memory=True
    )
    
    val_loader = DataLoader(
        val_dataset,
        batch_size=training_config['batch_size'],
        shuffle=False,
        num_workers=training_config['num_workers'],
        pin_memory=True
    )
    
    return train_loader, val_loader

