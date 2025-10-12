"""
Demo script to test the system with sample video or webcam
"""
import cv2
import yaml
import argparse
import numpy as np
from pathlib import Path


def create_demo_video(output_path='demo_video.mp4', duration=10, fps=30):
    """
    Create a demo video with simple patterns for testing
    
    Args:
        output_path: Path to save video
        duration: Duration in seconds
        fps: Frames per second
    """
    width, height = 640, 480
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    total_frames = duration * fps
    
    print(f"Creating demo video: {output_path}")
    
    for i in range(total_frames):
        # Create a frame with moving objects
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Add background gradient
        for y in range(height):
            frame[y, :] = [y * 255 // height, 50, 100]
        
        # Add moving rectangle (simulating a vehicle)
        x_pos = int((i / total_frames) * width)
        y_pos = height // 2
        cv2.rectangle(frame, (x_pos - 30, y_pos - 20), (x_pos + 30, y_pos + 20), 
                     (0, 255, 0), -1)
        
        # Add text
        cv2.putText(frame, f"Demo Frame {i+1}/{total_frames}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Add timestamp
        cv2.putText(frame, f"Time: {i/fps:.2f}s", (10, height - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        out.write(frame)
    
    out.release()
    print(f"Demo video created successfully!")


def test_webcam():
    """
    Test webcam connection
    """
    print("Testing webcam connection...")
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("[FAIL] Cannot access webcam")
        return False
    
    print("[OK] Webcam accessible")
    
    # Capture a few frames
    for i in range(30):
        ret, frame = cap.read()
        if not ret:
            print(f"[FAIL] Failed to read frame {i+1}")
            cap.release()
            return False
    
    print("[OK] Webcam working properly")
    cap.release()
    return True


def check_system():
    """
    Check system requirements and configuration
    """
    print("\n" + "="*50)
    print("System Check")
    print("="*50)
    
    # Check Python packages
    packages = {
        'torch': 'PyTorch',
        'cv2': 'OpenCV',
        'yaml': 'PyYAML',
        'numpy': 'NumPy'
    }
    
    print("\nPackage Check:")
    for module, name in packages.items():
        try:
            __import__(module)
            print(f"  [OK] {name}")
        except ImportError:
            print(f"  [FAIL] {name} - Not installed")
    
    # Check GPU
    try:
        import torch
        print(f"\nGPU Check:")
        print(f"  CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"  Device: {torch.cuda.get_device_name(0)}")
            print(f"  Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
    except Exception as e:
        print(f"  Error checking GPU: {e}")
    
    # Check config file
    print(f"\nConfiguration:")
    if Path('config.yaml').exists():
        print(f"  [OK] config.yaml found")
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
            print(f"  Model: {config['model']['architecture']}")
            print(f"  Backbone: {config['model']['backbone']}")
    else:
        print(f"  [FAIL] config.yaml not found")
    
    # Check directories
    print(f"\nDirectories:")
    dirs = ['datasets/bdd100k', 'checkpoints', 'logs', 'output']
    for dir_path in dirs:
        exists = Path(dir_path).exists()
        status = "[OK]" if exists else "[MISS]"
        print(f"  {status} {dir_path}")
    
    print("\n" + "="*50)


def main():
    parser = argparse.ArgumentParser(description='Demo and system testing')
    parser.add_argument('--check', action='store_true',
                       help='Check system requirements')
    parser.add_argument('--test-webcam', action='store_true',
                       help='Test webcam connection')
    parser.add_argument('--create-video', action='store_true',
                       help='Create demo video for testing')
    parser.add_argument('--output', type=str, default='demo_video.mp4',
                       help='Output path for demo video')
    
    args = parser.parse_args()
    
    if args.check:
        check_system()
    
    if args.test_webcam:
        test_webcam()
    
    if args.create_video:
        create_demo_video(args.output)
    
    if not any([args.check, args.test_webcam, args.create_video]):
        print("Demo script - use --help for options")
        print("\nQuick commands:")
        print("  python demo.py --check          # Check system setup")
        print("  python demo.py --test-webcam    # Test webcam")
        print("  python demo.py --create-video   # Create demo video")


if __name__ == '__main__':
    main()

