"""
Real-time inference system for detecting unsafe actions in video streams
with alert notifications
"""
import os
import cv2
import torch
import yaml
import time
import json
import numpy as np
from datetime import datetime
from pathlib import Path
from collections import deque
import requests

from models.action_detector import create_model
from data.dataset import StreamVideoBuffer
from utils.logger import setup_logger


class UnsafeActionDetector:
    """
    Real-time unsafe action detector with alert system
    """
    
    def __init__(self, config, model_path):
        self.config = config
        self.device = torch.device(config['training']['device'] 
                                   if torch.cuda.is_available() else 'cpu')
        
        # Load model
        self.model = self.load_model(model_path)
        self.model.eval()
        
        # Action classes
        self.action_classes = ['safe'] + config['unsafe_actions']
        
        # Inference settings
        self.confidence_threshold = config['inference']['confidence_threshold']
        self.temporal_smoothing = config['inference']['temporal_smoothing']
        self.smoothing_window = config['inference']['smoothing_window']
        
        # Alert settings
        self.alert_cooldown = config['inference']['alert_cooldown']
        self.last_alert_times = {}
        
        # Video buffer for temporal analysis
        self.video_buffer = StreamVideoBuffer(
            buffer_size=config['inference']['video_buffer_size'],
            num_frames=config['model']['num_frames'],
            frame_interval=config['model']['frame_interval']
        )
        
        # Prediction smoothing buffer
        if self.temporal_smoothing:
            self.prediction_buffer = deque(maxlen=self.smoothing_window)
        
        # Alert system
        self.alert_config = config['alerts']
        self.setup_alerts()
        
        # Logger
        self.logger = setup_logger(config['logging']['save_dir'])
        self.logger.info(f"Detector initialized on device: {self.device}")
    
    def load_model(self, model_path):
        """Load trained model from checkpoint"""
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model checkpoint not found: {model_path}")
        
        # Create model
        model = create_model(self.config)
        
        # Load checkpoint
        checkpoint = torch.load(model_path, map_location=self.device)
        model.load_state_dict(checkpoint['model_state_dict'])
        model.to(self.device)
        
        self.logger.info(f"Loaded model from: {model_path}")
        return model
    
    def setup_alerts(self):
        """Setup alert notification system"""
        if self.alert_config['enabled']:
            # Create directories for saving alert clips
            if self.alert_config['save_clips']:
                Path(self.alert_config['clips_dir']).mkdir(parents=True, exist_ok=True)
            
            # Create log file
            if 'file' in self.alert_config['methods']:
                log_dir = Path(self.alert_config['log_file']).parent
                log_dir.mkdir(parents=True, exist_ok=True)
    
    def predict(self, video_clip):
        """
        Make prediction on a video clip
        
        Args:
            video_clip: Tensor of shape (1, T, C, H, W)
        
        Returns:
            action_class: Predicted action class
            confidence: Confidence score
        """
        with torch.no_grad():
            video_clip = video_clip.to(self.device)
            outputs = self.model(video_clip)
            probabilities = torch.softmax(outputs, dim=1)
            confidence, predicted = torch.max(probabilities, dim=1)
            
            action_class = predicted.item()
            confidence_score = confidence.item()
        
        return action_class, confidence_score
    
    def smooth_predictions(self, action_class, confidence):
        """
        Apply temporal smoothing to predictions
        
        Args:
            action_class: Current predicted class
            confidence: Confidence score
        
        Returns:
            smoothed_class: Smoothed action class
            avg_confidence: Average confidence
        """
        if not self.temporal_smoothing:
            return action_class, confidence
        
        # Add to buffer
        self.prediction_buffer.append((action_class, confidence))
        
        # Get most common prediction with average confidence
        classes = [pred[0] for pred in self.prediction_buffer]
        confidences = [pred[1] for pred in self.prediction_buffer]
        
        # Majority voting
        unique_classes, counts = np.unique(classes, return_counts=True)
        smoothed_class = unique_classes[np.argmax(counts)]
        
        # Average confidence for the smoothed class
        avg_confidence = np.mean([conf for cls, conf in self.prediction_buffer 
                                 if cls == smoothed_class])
        
        return smoothed_class, avg_confidence
    
    def should_trigger_alert(self, action_class):
        """
        Check if alert should be triggered based on cooldown
        
        Args:
            action_class: Detected action class
        
        Returns:
            should_alert: Boolean indicating if alert should be sent
        """
        if action_class == 0:  # Safe class
            return False
        
        current_time = time.time()
        action_name = self.action_classes[action_class]
        
        # Check cooldown
        if action_name in self.last_alert_times:
            time_since_last = current_time - self.last_alert_times[action_name]
            if time_since_last < self.alert_cooldown:
                return False
        
        # Update last alert time
        self.last_alert_times[action_name] = current_time
        return True
    
    def send_alert(self, action_class, confidence, frame=None, video_clip_path=None):
        """
        Send alert through configured notification methods
        
        Args:
            action_class: Detected unsafe action class
            confidence: Confidence score
            frame: Current frame (for display/saving)
            video_clip_path: Path to saved video clip
        """
        if not self.alert_config['enabled']:
            return
        
        action_name = self.action_classes[action_class]
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        alert_message = {
            'timestamp': timestamp,
            'action': action_name,
            'confidence': float(confidence),
            'video_clip': video_clip_path
        }
        
        # Console alert
        if 'console' in self.alert_config['methods']:
            self.logger.warning(
                f"⚠️  UNSAFE ACTION DETECTED: {action_name} "
                f"(Confidence: {confidence:.2%}) at {timestamp}"
            )
        
        # File logging
        if 'file' in self.alert_config['methods']:
            with open(self.alert_config['log_file'], 'a') as f:
                f.write(json.dumps(alert_message) + '\n')
        
        # Webhook notification
        if 'webhook' in self.alert_config['methods'] and self.alert_config['webhook_url']:
            try:
                response = requests.post(
                    self.alert_config['webhook_url'],
                    json=alert_message,
                    timeout=5
                )
                if response.status_code != 200:
                    self.logger.error(f"Webhook alert failed: {response.status_code}")
            except Exception as e:
                self.logger.error(f"Webhook error: {e}")
    
    def save_alert_clip(self, frames, action_class, confidence):
        """
        Save video clip of detected unsafe action
        
        Args:
            frames: List of frames
            action_class: Detected action class
            confidence: Confidence score
        
        Returns:
            clip_path: Path to saved clip
        """
        if not self.alert_config['save_clips']:
            return None
        
        action_name = self.action_classes[action_class]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        clip_filename = f"{action_name}_{timestamp}_{confidence:.2f}.mp4"
        clip_path = Path(self.alert_config['clips_dir']) / clip_filename
        
        # Save video
        if frames:
            height, width = frames[0].shape[:2]
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            fps = self.config['inference']['fps']
            out = cv2.VideoWriter(str(clip_path), fourcc, fps, (width, height))
            
            for frame in frames:
                out.write(frame)
            
            out.release()
            self.logger.info(f"Saved alert clip: {clip_path}")
        
        return str(clip_path)
    
    def process_frame(self, frame):
        """
        Process a single frame from video stream
        
        Args:
            frame: Video frame (BGR format)
        
        Returns:
            result: Dictionary with detection results
        """
        # Add frame to buffer
        self.video_buffer.add_frame(frame)
        
        # Get video clip for inference
        video_clip = self.video_buffer.get_clip()
        
        if video_clip is None:
            # Not enough frames yet
            return {
                'action': 'initializing',
                'confidence': 0.0,
                'alert': False
            }
        
        # Make prediction
        action_class, confidence = self.predict(video_clip)
        
        # Apply temporal smoothing
        action_class, confidence = self.smooth_predictions(action_class, confidence)
        
        # Check if unsafe action detected
        is_unsafe = action_class > 0 and confidence >= self.confidence_threshold
        should_alert = is_unsafe and self.should_trigger_alert(action_class)
        
        # Send alert if needed
        video_clip_path = None
        if should_alert:
            # Save video clip
            if self.alert_config['save_clips']:
                video_clip_path = self.save_alert_clip(
                    self.video_buffer.buffer, 
                    action_class, 
                    confidence
                )
            
            # Send alert
            self.send_alert(action_class, confidence, frame, video_clip_path)
        
        # Prepare result
        result = {
            'action': self.action_classes[action_class],
            'confidence': confidence,
            'alert': should_alert,
            'is_unsafe': is_unsafe
        }
        
        return result
    
    def run_on_video(self, video_path, display=True, save_output=None):
        """
        Run detection on a video file
        
        Args:
            video_path: Path to video file
            display: Whether to display results
            save_output: Path to save output video (optional)
        """
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")
        
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Setup video writer if saving
        out = None
        if save_output:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(save_output, fourcc, fps, (width, height))
        
        self.logger.info(f"Processing video: {video_path}")
        
        frame_count = 0
        start_time = time.time()
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame_count += 1
                
                # Process frame
                result = self.process_frame(frame)
                
                # Draw results on frame
                if display or save_output:
                    annotated_frame = self.draw_results(frame, result)
                    
                    if display:
                        cv2.imshow('Unsafe Action Detection', annotated_frame)
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            break
                    
                    if out:
                        out.write(annotated_frame)
        
        finally:
            cap.release()
            if out:
                out.release()
            if display:
                cv2.destroyAllWindows()
        
        # Print statistics
        elapsed_time = time.time() - start_time
        actual_fps = frame_count / elapsed_time
        self.logger.info(
            f"Processed {frame_count} frames in {elapsed_time:.2f}s "
            f"({actual_fps:.2f} FPS)"
        )
    
    def run_on_stream(self, source=0, display=True):
        """
        Run detection on live video stream (webcam or RTSP)
        
        Args:
            source: Video source (0 for webcam, or RTSP URL)
            display: Whether to display results
        """
        cap = cv2.VideoCapture(source)
        
        if not cap.isOpened():
            raise ValueError(f"Cannot open video source: {source}")
        
        self.logger.info(f"Starting live stream detection from source: {source}")
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    self.logger.warning("Failed to read frame")
                    continue
                
                # Process frame
                result = self.process_frame(frame)
                
                # Display
                if display:
                    annotated_frame = self.draw_results(frame, result)
                    cv2.imshow('Live Unsafe Action Detection', annotated_frame)
                    
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
        
        finally:
            cap.release()
            cv2.destroyAllWindows()
    
    def draw_results(self, frame, result):
        """
        Draw detection results on frame
        
        Args:
            frame: Input frame
            result: Detection result dictionary
        
        Returns:
            annotated_frame: Frame with annotations
        """
        annotated_frame = frame.copy()
        
        action = result['action']
        confidence = result['confidence']
        is_unsafe = result.get('is_unsafe', False)
        
        # Choose color based on safety
        color = (0, 0, 255) if is_unsafe else (0, 255, 0)  # Red for unsafe, green for safe
        
        # Draw text
        text = f"{action}: {confidence:.2%}"
        cv2.putText(annotated_frame, text, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        
        # Draw warning if unsafe
        if is_unsafe:
            cv2.putText(annotated_frame, "UNSAFE ACTION!", (10, 70),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        # Draw timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(annotated_frame, timestamp, (10, annotated_frame.shape[0] - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        return annotated_frame


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Real-time unsafe action detection')
    parser.add_argument('--config', type=str, default='config.yaml',
                       help='Path to configuration file')
    parser.add_argument('--model', type=str, default='checkpoints/best_model.pth',
                       help='Path to trained model checkpoint')
    parser.add_argument('--source', type=str, default='0',
                       help='Video source: file path, webcam (0), or RTSP URL')
    parser.add_argument('--output', type=str, default=None,
                       help='Path to save output video (optional)')
    parser.add_argument('--no-display', action='store_true',
                       help='Disable display')
    
    args = parser.parse_args()
    
    # Load config
    with open(args.config, 'r') as f:
        config = yaml.safe_load(f)
    
    # Create detector
    detector = UnsafeActionDetector(config, args.model)
    
    # Determine source type
    source = args.source
    if source.isdigit():
        source = int(source)
    
    # Run detection
    if isinstance(source, int) or source.startswith('rtsp://'):
        # Live stream
        detector.run_on_stream(source, display=not args.no_display)
    else:
        # Video file
        detector.run_on_video(source, display=not args.no_display, 
                            save_output=args.output)


if __name__ == '__main__':
    main()

