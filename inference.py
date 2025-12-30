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
    
    def __init__(self, config, model_path, project_context=None):
        self.config = config
        self.device = torch.device(config['training']['device'] 
                                   if torch.cuda.is_available() else 'cpu')
        
        # Logger (initialize first)
        self.logger = setup_logger(config['logging']['save_dir'])
        self.logger.info(f"Detector initialized on device: {self.device}")
        
        # Project context for jurisdiction/industry-specific rules
        self.project_context = project_context or {}
        
        # Action classes (default from config, may be overridden by checkpoint)
        self.action_classes = ['safe'] + config['unsafe_actions']
        
        # Load jurisdiction-specific actions if available
        if project_context and 'jurisdiction_code' in project_context and 'industry_code' in project_context:
            jurisdiction_industry_key = f"{project_context['jurisdiction_code']}_{project_context['industry_code']}"
            if 'jurisdiction_industry_actions' in config:
                specific_actions = config['jurisdiction_industry_actions'].get(jurisdiction_industry_key, [])
                if specific_actions:
                    self.action_classes = ['safe'] + specific_actions
                    self.logger.info(f"Using {len(specific_actions)} actions for {jurisdiction_industry_key}")
        
        # Load model (may override action_classes from checkpoint's label_mapping)
        self.model = self.load_model(model_path)
        self.model.eval()
        
        # Inference settings
        self.confidence_threshold = config['inference']['confidence_threshold']
        self.temporal_smoothing = config['inference']['temporal_smoothing']
        self.smoothing_window = config['inference']['smoothing_window']
        
        # Alert settings
        self.alert_cooldown = config['inference']['alert_cooldown']
        self.last_alert_times = {}
        
        # Severity filtering
        self.min_severity_alert = project_context.get('min_severity_alert', 1) if project_context else 1
        
        # Action severity mapping (loaded from database if available)
        self.action_severity_map = {}
        self.regulation_mapping = {}
        
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
    
    def load_model(self, model_path):
        """Load trained model from checkpoint"""
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model checkpoint not found: {model_path}")
        
        # Load checkpoint first to get the config it was trained with
        checkpoint = torch.load(model_path, map_location=self.device, weights_only=False)
        
        # Use checkpoint config if available (for architecture compatibility)
        checkpoint_config = checkpoint.get('config', None)
        if checkpoint_config and 'model' in checkpoint_config:
            # Use the model architecture from the checkpoint
            model_config = checkpoint_config
            self.logger.info(f"Using model config from checkpoint: backbone={model_config['model'].get('backbone')}, num_classes={model_config['model'].get('num_classes')}")
        else:
            # Fall back to provided config
            model_config = self.config
            self.logger.info("Using config.yaml for model architecture")
        
        # Create model with the correct architecture
        model = create_model(model_config)
        
        # Load the weights
        model.load_state_dict(checkpoint['model_state_dict'])
        model.to(self.device)
        
        # Update action classes from checkpoint's label mapping if available
        label_mapping = checkpoint.get('label_mapping', None)
        if label_mapping:
            # Build action classes list from label mapping
            sorted_labels = sorted(label_mapping.items(), key=lambda x: x[1])
            self.action_classes = [label for label, _ in sorted_labels]
            self.logger.info(f"Loaded {len(self.action_classes)} action classes from checkpoint")
        
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
    
    def send_alert(self, action_class, confidence, frame=None, video_clip_path=None, 
                   severity_level=None, regulation_violation=None):
        """
        Send alert through configured notification methods
        
        Args:
            action_class: Detected unsafe action class
            confidence: Confidence score
            frame: Current frame (for display/saving)
            video_clip_path: Path to saved video clip
            severity_level: Severity level (1-5) (optional)
            regulation_violation: Regulation violation details (optional)
        """
        if not self.alert_config['enabled']:
            return
        
        action_name = self.action_classes[action_class]
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        severity_label = self._get_severity_label(severity_level) if severity_level else "Unknown"
        
        alert_message = {
            'timestamp': timestamp,
            'action': action_name,
            'confidence': float(confidence),
            'severity_level': severity_level,
            'severity_label': severity_label,
            'regulation_violation': regulation_violation,
            'video_clip': video_clip_path
        }
        
        # Console alert
        if 'console' in self.alert_config['methods']:
            console_msg = (
                f"⚠️  UNSAFE ACTION DETECTED [{severity_label}]: {action_name} "
                f"(Confidence: {confidence:.2%}) at {timestamp}"
            )
            if regulation_violation:
                console_msg += f"\n   Regulation: {regulation_violation}"
            self.logger.warning(console_msg)
        
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
    
    def set_severity_and_regulation_data(self, severity_map, regulation_map):
        """
        Set severity and regulation mappings from database
        
        Args:
            severity_map: Dict mapping action names to severity levels
            regulation_map: Dict mapping action names to regulation violations
        """
        self.action_severity_map = severity_map
        self.regulation_mapping = regulation_map
        self.logger.info(f"Loaded severity data for {len(severity_map)} actions")
    
    def get_action_severity(self, action_name):
        """Get severity level for an action (1-5)"""
        return self.action_severity_map.get(action_name, 3)  # Default to Medium (3)
    
    def should_alert_by_severity(self, action_name):
        """Check if action severity meets minimum threshold for alerting"""
        action_severity = self.get_action_severity(action_name)
        return action_severity >= self.min_severity_alert
    
    def get_regulation_violation(self, action_name):
        """Get regulation violation details for an action"""
        return self.regulation_mapping.get(action_name, None)
    
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
                'alert': False,
                'severity': 0
            }
        
        # Make prediction
        action_class, confidence = self.predict(video_clip)
        
        # Apply temporal smoothing
        action_class, confidence = self.smooth_predictions(action_class, confidence)
        
        action_name = self.action_classes[action_class]
        
        # Check if unsafe action detected
        is_unsafe = action_class > 0 and confidence >= self.confidence_threshold
        
        # Get severity level
        severity_level = self.get_action_severity(action_name) if is_unsafe else 0
        
        # Check if severity meets alerting threshold
        meets_severity_threshold = self.should_alert_by_severity(action_name) if is_unsafe else False
        
        # Final alert decision
        should_alert = (
            is_unsafe and 
            meets_severity_threshold and 
            self.should_trigger_alert(action_class)
        )
        
        # Get regulation violation details
        regulation_violation = self.get_regulation_violation(action_name) if is_unsafe else None
        
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
            
            # Send alert with severity and regulation info
            self.send_alert(action_class, confidence, frame, video_clip_path, 
                          severity_level, regulation_violation)
        
        # Prepare result
        result = {
            'action': action_name,
            'confidence': confidence,
            'alert': should_alert,
            'is_unsafe': is_unsafe,
            'severity': severity_level,
            'severity_label': self._get_severity_label(severity_level),
            'regulation_violation': regulation_violation
        }
        
        return result
    
    def _get_severity_label(self, severity_level):
        """Convert severity level to label"""
        labels = {
            0: "Safe",
            1: "Low",
            2: "Medium",
            3: "High",
            4: "Critical",
            5: "Emergency"
        }
        return labels.get(severity_level, "Unknown")
    
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

