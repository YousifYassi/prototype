"""
Inference script for detecting unsafe behavior in videos.

Uses the trained safety model to analyze videos and detect:
- Missing PPE (gloves, helmet, safety glasses, etc.)
- Other safety violations
- Unsafe behaviors

Usage:
    python detect_unsafe_behavior.py --video path/to/video.mp4
    python detect_unsafe_behavior.py --video path/to/video.mp4 --output results.json
    python detect_unsafe_behavior.py --folder path/to/videos/
"""
import os
import sys
import json
import argparse
import cv2
import torch
import numpy as np
from pathlib import Path
from tqdm import tqdm
from torchvision import transforms
from datetime import datetime

from models.action_detector import create_model


# Default label mapping (same as training)
DEFAULT_LABEL_MAPPING = {
    0: 'Safe',
    1: 'No PPE - Missing Gloves',
    2: 'No PPE - Missing Helmet',
    3: 'No PPE - Missing Safety Glasses',
    4: 'No PPE - Missing High Visibility Vest',
    5: 'Other Violation',
    6: 'Unsafe Behavior',
    7: 'Near Miss',
}


class SafetyDetector:
    """
    Detector for unsafe behavior in videos using trained model.
    """
    
    def __init__(
        self,
        model_path: str = 'checkpoints/safety_model_best.pth',
        device: str = None,
        confidence_threshold: float = 0.5
    ):
        """
        Args:
            model_path: Path to trained model checkpoint
            device: Device to use ('cuda' or 'cpu'). Auto-detects if None.
            confidence_threshold: Minimum confidence for detection
        """
        self.confidence_threshold = confidence_threshold
        
        # Setup device
        if device is None:
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = torch.device(device)
        
        print(f"Using device: {self.device}")
        
        # Load model
        self.model, self.config, self.label_mapping = self._load_model(model_path)
        self.model.eval()
        
        # Get model parameters
        self.num_frames = self.config['model']['num_frames']
        self.frame_interval = self.config['model']['frame_interval']
        self.input_size = tuple(self.config['model']['input_size'])
        
        # Setup transforms
        self.transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize(self.input_size),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ])
        
        print(f"Model loaded successfully!")
        print(f"Classes: {list(self.label_mapping.values())}")
    
    def _load_model(self, model_path: str):
        """Load trained model from checkpoint."""
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found: {model_path}")
        
        print(f"Loading model from: {model_path}")
        checkpoint = torch.load(model_path, map_location=self.device, weights_only=False)
        
        # Get config and label mapping from checkpoint
        config = checkpoint['config']
        label_mapping = checkpoint.get('label_mapping', DEFAULT_LABEL_MAPPING)
        
        # Convert label mapping if needed (str keys to int keys for id->label)
        if label_mapping and isinstance(list(label_mapping.keys())[0], str):
            # It's label->id, convert to id->label
            label_mapping = {v: k for k, v in label_mapping.items()}
        
        # Create model
        model = create_model(config)
        model.load_state_dict(checkpoint['model_state_dict'])
        model = model.to(self.device)
        
        return model, config, label_mapping
    
    def _extract_frames(self, video_path: str, start_frame: int = 0, end_frame: int = None):
        """Extract frames from video."""
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise IOError(f"Cannot open video: {video_path}")
        
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        if end_frame is None:
            end_frame = total_frames
        
        # Calculate frame indices to sample
        segment_length = end_frame - start_frame
        required_length = self.num_frames * self.frame_interval
        
        if segment_length <= required_length:
            indices = np.linspace(start_frame, end_frame - 1, self.num_frames)
        else:
            offset = (segment_length - required_length) // 2
            indices = np.arange(offset, offset + required_length, self.frame_interval)
            indices = indices + start_frame
        
        indices = indices.astype(int)[:self.num_frames]
        
        # Extract frames
        frames = []
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
        
        return frames[:self.num_frames], fps, total_frames
    
    def _preprocess_frames(self, frames):
        """Preprocess frames for model input."""
        processed = []
        for frame in frames:
            frame_tensor = self.transform(frame)
            processed.append(frame_tensor)
        
        # Stack: (T, C, H, W)
        video_tensor = torch.stack(processed)
        # Add batch dimension: (1, T, C, H, W)
        return video_tensor.unsqueeze(0)
    
    @torch.no_grad()
    def predict(self, video_path: str, start_frame: int = 0, end_frame: int = None):
        """
        Predict unsafe behavior in a video or video segment.
        
        Args:
            video_path: Path to video file
            start_frame: Starting frame (for segment analysis)
            end_frame: Ending frame (for segment analysis)
        
        Returns:
            dict with prediction results
        """
        # Extract and preprocess frames
        frames, fps, total_frames = self._extract_frames(video_path, start_frame, end_frame)
        video_tensor = self._preprocess_frames(frames).to(self.device)
        
        # Run inference
        outputs = self.model(video_tensor)
        probabilities = torch.softmax(outputs, dim=1)
        
        # Get prediction
        confidence, predicted_class = torch.max(probabilities, dim=1)
        confidence = confidence.item()
        predicted_class = predicted_class.item()
        
        # Get label name
        label_name = self.label_mapping.get(predicted_class, f'Class_{predicted_class}')
        
        # Determine if this is a violation
        is_violation = predicted_class != 0 and confidence >= self.confidence_threshold
        
        # Get all class probabilities
        all_probs = {
            self.label_mapping.get(i, f'Class_{i}'): prob.item()
            for i, prob in enumerate(probabilities[0])
        }
        
        return {
            'video_path': video_path,
            'start_frame': start_frame,
            'end_frame': end_frame or total_frames,
            'total_frames': total_frames,
            'fps': fps,
            'prediction': label_name,
            'predicted_class': predicted_class,
            'confidence': confidence,
            'is_violation': is_violation,
            'all_probabilities': all_probs
        }
    
    def analyze_video(self, video_path: str, segment_duration: float = 5.0, overlap: float = 0.5):
        """
        Analyze entire video using sliding window approach.
        
        Args:
            video_path: Path to video file
            segment_duration: Duration of each segment in seconds
            overlap: Overlap ratio between segments (0-1)
        
        Returns:
            dict with analysis results
        """
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise IOError(f"Cannot open video: {video_path}")
        
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        duration = total_frames / fps if fps > 0 else 0
        cap.release()
        
        print(f"\nAnalyzing: {video_path}")
        print(f"Duration: {duration:.1f}s, FPS: {fps:.1f}, Frames: {total_frames}")
        
        # Calculate segment parameters
        segment_frames = int(segment_duration * fps)
        step_frames = int(segment_frames * (1 - overlap))
        
        # Ensure minimum segment size
        segment_frames = max(segment_frames, self.num_frames * self.frame_interval)
        step_frames = max(step_frames, self.num_frames)
        
        # Analyze segments
        segments = []
        violations = []
        
        num_segments = max(1, (total_frames - segment_frames) // step_frames + 1)
        
        for i in tqdm(range(num_segments), desc="Analyzing segments"):
            start_frame = i * step_frames
            end_frame = min(start_frame + segment_frames, total_frames)
            
            result = self.predict(video_path, start_frame, end_frame)
            result['segment_id'] = i
            result['start_time'] = start_frame / fps if fps > 0 else 0
            result['end_time'] = end_frame / fps if fps > 0 else 0
            
            segments.append(result)
            
            if result['is_violation']:
                violations.append(result)
        
        # Summary
        summary = {
            'video_path': video_path,
            'duration_seconds': duration,
            'fps': fps,
            'total_frames': total_frames,
            'segments_analyzed': len(segments),
            'violations_detected': len(violations),
            'violation_rate': len(violations) / len(segments) if segments else 0,
            'segments': segments,
            'violations': violations
        }
        
        return summary
    
    def print_results(self, results: dict):
        """Print analysis results in a readable format."""
        print("\n" + "=" * 60)
        print("SAFETY ANALYSIS RESULTS")
        print("=" * 60)
        
        print(f"\nVideo: {results['video_path']}")
        print(f"Duration: {results['duration_seconds']:.1f} seconds")
        print(f"Segments analyzed: {results['segments_analyzed']}")
        print(f"Violations detected: {results['violations_detected']}")
        print(f"Violation rate: {results['violation_rate']*100:.1f}%")
        
        if results['violations']:
            print("\n" + "-" * 40)
            print("DETECTED VIOLATIONS:")
            print("-" * 40)
            
            for v in results['violations']:
                print(f"\n  [{v['start_time']:.1f}s - {v['end_time']:.1f}s]")
                print(f"  Type: {v['prediction']}")
                print(f"  Confidence: {v['confidence']*100:.1f}%")
        else:
            print("\n[OK] No safety violations detected!")
        
        print("\n" + "=" * 60)


def main():
    parser = argparse.ArgumentParser(description='Detect unsafe behavior in videos')
    parser.add_argument(
        '--video', '-v', type=str,
        help='Path to video file to analyze'
    )
    parser.add_argument(
        '--folder', '-f', type=str,
        help='Path to folder containing videos to analyze'
    )
    parser.add_argument(
        '--model', '-m', type=str,
        default='checkpoints/safety_model_best.pth',
        help='Path to trained model'
    )
    parser.add_argument(
        '--output', '-o', type=str,
        help='Output JSON file for results'
    )
    parser.add_argument(
        '--threshold', '-t', type=float, default=0.5,
        help='Confidence threshold for detections'
    )
    parser.add_argument(
        '--segment-duration', '-s', type=float, default=5.0,
        help='Duration of each analysis segment in seconds'
    )
    
    args = parser.parse_args()
    
    if not args.video and not args.folder:
        print("Error: Please provide --video or --folder argument")
        parser.print_help()
        sys.exit(1)
    
    # Initialize detector
    detector = SafetyDetector(
        model_path=args.model,
        confidence_threshold=args.threshold
    )
    
    all_results = []
    
    # Process single video
    if args.video:
        if not os.path.exists(args.video):
            print(f"Error: Video not found: {args.video}")
            sys.exit(1)
        
        results = detector.analyze_video(args.video, segment_duration=args.segment_duration)
        detector.print_results(results)
        all_results.append(results)
    
    # Process folder of videos
    if args.folder:
        if not os.path.exists(args.folder):
            print(f"Error: Folder not found: {args.folder}")
            sys.exit(1)
        
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
        videos = []
        for ext in video_extensions:
            videos.extend(Path(args.folder).glob(f'*{ext}'))
        
        print(f"\nFound {len(videos)} videos in {args.folder}")
        
        for video_path in videos:
            try:
                results = detector.analyze_video(str(video_path), segment_duration=args.segment_duration)
                detector.print_results(results)
                all_results.append(results)
            except Exception as e:
                print(f"Error processing {video_path}: {e}")
    
    # Save results to JSON
    if args.output and all_results:
        output_data = {
            'analysis_timestamp': datetime.now().isoformat(),
            'model_path': args.model,
            'confidence_threshold': args.threshold,
            'results': all_results
        }
        
        with open(args.output, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        print(f"\nResults saved to: {args.output}")
    
    # Print summary
    if len(all_results) > 1:
        total_violations = sum(r['violations_detected'] for r in all_results)
        total_segments = sum(r['segments_analyzed'] for r in all_results)
        
        print("\n" + "=" * 60)
        print("OVERALL SUMMARY")
        print("=" * 60)
        print(f"Videos analyzed: {len(all_results)}")
        print(f"Total segments: {total_segments}")
        print(f"Total violations: {total_violations}")
        print(f"Overall violation rate: {total_violations/total_segments*100:.1f}%" if total_segments > 0 else "N/A")


if __name__ == '__main__':
    main()



