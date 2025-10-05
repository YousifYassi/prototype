# Unsafe Action Detection System

A real-time video analysis system that detects unsafe actions and behaviors in video streams, providing instant alerts when intervention is needed.

## 🎯 Overview

This system uses deep learning to analyze video streams (from cameras, video files, or RTSP streams) and detect unsafe actions in real-time. It's designed for applications like:

- **Traffic Safety**: Detecting dangerous driving behaviors (aggressive driving, tailgating, running red lights)
- **Workplace Safety**: Identifying unsafe practices in industrial environments
- **Security Monitoring**: Detecting suspicious or dangerous activities
- **Autonomous Vehicles**: Real-time hazard detection

## ✨ Features

- **Real-time Detection**: Process live video streams with low latency
- **Multiple Alert Methods**: Console, file logging, and webhook notifications
- **Temporal Analysis**: Uses multiple frames to understand actions over time
- **Video Recording**: Automatically saves clips of detected unsafe actions
- **Configurable Thresholds**: Adjust sensitivity and alert cooldown periods
- **Multiple Model Architectures**: Choose from CNN+LSTM, 3D CNN, or hybrid approaches
- **GPU Acceleration**: Optimized for CUDA-enabled GPUs

## 🏗️ Architecture

The system consists of three main components:

1. **Data Pipeline** (`data/dataset.py`): Loads and processes video data
2. **Model** (`models/action_detector.py`): Neural networks for temporal action recognition
3. **Inference Engine** (`inference.py`): Real-time detection with alert system

### Model Architectures

- **VideoActionDetector**: 2D CNN backbone + temporal convolutions (recommended)
- **LSTMActionDetector**: CNN feature extractor + bidirectional LSTM
- **SimpleC3D**: Full 3D convolutional network

## 📋 Requirements

- Python 3.8+
- PyTorch 2.0+
- CUDA-capable GPU (recommended)
- OpenCV
- See `requirements.txt` for full list

## 🚀 Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd prototype
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Verify GPU setup** (optional but recommended)
```bash
python verify.py
```

## 📊 Data Preparation

### Using BDD100K Dataset

1. **Download BDD100K dataset** from [https://bdd-data.berkeley.edu/](https://bdd-data.berkeley.edu/)

2. **Organize your data**:
```
datasets/bdd100k/
├── videos/
│   ├── train/
│   ├── val/
│   └── test/
└── annotations.json
```

3. **Prepare annotations**:
```bash
python prepare_data.py --root_dir datasets/bdd100k --output datasets/bdd100k/annotations.json
```

### Custom Dataset

Create an `annotations.json` file with the following structure:
```json
{
  "train": [
    {
      "video_name": "video_001.mp4",
      "label": 0,
      "action_name": "safe"
    },
    {
      "video_name": "video_002.mp4",
      "label": 1,
      "action_name": "aggressive_driving"
    }
  ],
  "val": [...],
  "test": [...]
}
```

Labels:
- `0`: Safe (normal behavior)
- `1-9`: Unsafe action categories (customize in `config.yaml`)

## 🎓 Training

### 1. Configure Training

Edit `config.yaml` to customize:
- Model architecture and hyperparameters
- Dataset paths
- Unsafe action categories
- Training parameters

### 2. Start Training

```bash
python train.py
```

Monitor training with TensorBoard:
```bash
tensorboard --logdir runs
```

### 3. Training Output

- **Checkpoints**: Saved in `checkpoints/`
- **Logs**: Saved in `logs/`
- **TensorBoard**: Saved in `runs/`

## 🔍 Evaluation

Evaluate your trained model:

```bash
python evaluate.py --model checkpoints/best_model.pth --split test
```

This generates:
- Classification metrics (accuracy, precision, recall, F1)
- Confusion matrix visualization
- Per-class performance analysis

## 🎥 Inference

### Real-time Detection on Video File

```bash
python inference.py --model checkpoints/best_model.pth --source path/to/video.mp4
```

### Live Stream Detection (Webcam)

```bash
python inference.py --model checkpoints/best_model.pth --source 0
```

### RTSP Stream

```bash
python inference.py --model checkpoints/best_model.pth --source rtsp://your-stream-url
```

### Save Output Video

```bash
python inference.py --model checkpoints/best_model.pth --source video.mp4 --output output.mp4
```

### Run Without Display

```bash
python inference.py --model checkpoints/best_model.pth --source 0 --no-display
```

## ⚠️ Alert System

The system supports multiple notification methods:

### Console Alerts
Real-time warnings printed to console (default)

### File Logging
All alerts saved to `logs/alerts.log`:
```json
{
  "timestamp": "2025-10-05 14:30:45",
  "action": "tailgating",
  "confidence": 0.92,
  "video_clip": "output/alert_clips/tailgating_20251005_143045_0.92.mp4"
}
```

### Webhook Notifications
Configure webhook URL in `config.yaml`:
```yaml
alerts:
  webhook_url: "https://your-webhook-endpoint.com/alerts"
```

The system sends POST requests with alert data in JSON format.

### Video Clip Recording
Automatically saves video clips of detected unsafe actions to `output/alert_clips/`

## ⚙️ Configuration

Key configuration options in `config.yaml`:

### Unsafe Action Categories
```yaml
unsafe_actions:
  - "aggressive_driving"
  - "tailgating"
  - "unsafe_lane_change"
  - "running_red_light"
  - "distracted_driver"
  - "speeding"
  - "wrong_way_driving"
  - "pedestrian_collision_risk"
  - "near_miss"
```

### Detection Sensitivity
```yaml
inference:
  confidence_threshold: 0.7  # Higher = fewer false positives
  temporal_smoothing: true
  smoothing_window: 5  # Frames to average predictions
  alert_cooldown: 3.0  # Seconds between repeat alerts
```

### Model Selection
```yaml
model:
  architecture: "video_action_detector"  # or "lstm", "c3d"
  backbone: "resnet50"  # or "resnet18"
  num_frames: 16  # Frames per clip
  frame_interval: 2  # Sample every N frames
```

## 📁 Project Structure

```
prototype/
├── config.yaml              # Configuration file
├── requirements.txt         # Python dependencies
├── train.py                 # Training script
├── inference.py             # Real-time inference
├── evaluate.py              # Model evaluation
├── prepare_data.py          # Data preparation
├── verify.py                # GPU verification
│
├── data/                    # Data loading modules
│   └── dataset.py
│
├── models/                  # Model architectures
│   └── action_detector.py
│
├── utils/                   # Utility functions
│   ├── logger.py
│   ├── metrics.py
│   └── visualization.py
│
├── datasets/                # Dataset directory
│   └── bdd100k/
│
├── checkpoints/             # Saved models
├── logs/                    # Training logs
├── runs/                    # TensorBoard logs
└── output/                  # Evaluation results & alert clips
```

## 🔧 Troubleshooting

### Issue: Out of Memory (OOM)

**Solution**: Reduce batch size in `config.yaml`:
```yaml
training:
  batch_size: 4  # Reduce from 8
```

Or reduce number of frames:
```yaml
model:
  num_frames: 8  # Reduce from 16
```

### Issue: Low FPS During Inference

**Solutions**:
1. Use smaller backbone: `backbone: "resnet18"`
2. Reduce input size: `input_size: [112, 112]`
3. Reduce frames per clip: `num_frames: 8`
4. Use GPU acceleration (verify with `python verify.py`)

### Issue: Too Many False Positives

**Solutions**:
1. Increase confidence threshold: `confidence_threshold: 0.8`
2. Enable temporal smoothing: `temporal_smoothing: true`
3. Increase smoothing window: `smoothing_window: 10`

### Issue: Missing Unsafe Actions

**Solutions**:
1. Decrease confidence threshold: `confidence_threshold: 0.5`
2. Check class imbalance in training data
3. Use weighted loss function or data augmentation

## 🎯 Best Practices

1. **Data Quality**: Ensure diverse training data covering various scenarios
2. **Class Balance**: Balance safe vs unsafe action samples
3. **Temporal Context**: Use sufficient frames (16+) for action understanding
4. **Validation**: Always validate on separate test set
5. **Tuning**: Adjust thresholds based on your specific use case
6. **Hardware**: Use GPU for training and real-time inference

## 📈 Performance Tips

- **Training**: Use mixed precision training for faster training
- **Inference**: Batch process multiple frames when possible
- **Memory**: Use gradient checkpointing for large models
- **Speed**: Consider model quantization for deployment

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 Citation

If you use this system in your research, please cite:

```bibtex
@software{unsafe_action_detection,
  title={Real-time Unsafe Action Detection System},
  author={Your Name},
  year={2025},
  url={https://github.com/your-repo}
}
```

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- BDD100K dataset: [https://bdd-data.berkeley.edu/](https://bdd-data.berkeley.edu/)
- PyTorch framework: [https://pytorch.org/](https://pytorch.org/)

## 📞 Support

For questions or issues:
- Open an issue on GitHub
- Email: your-email@example.com

---

**Note**: This system is designed for research and development. For production deployment, additional testing, validation, and safety measures are recommended.

