# Quick Start Guide

Get up and running with the Unsafe Action Detection System in 5 minutes!

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Verify Setup

Check that everything is installed correctly:

```bash
python demo.py --check
```

This will verify:
- ✓ All required packages are installed
- ✓ GPU availability (if applicable)
- ✓ Configuration file exists

## Step 3: Prepare Your Data

### Option A: Test with Demo Video

Create a demo video for testing:

```bash
python demo.py --create-video
```

### Option B: Use Your Own Data

1. Place your videos in: `datasets/bdd100k/videos/train/`, `val/`, `test/`

2. Create annotations file:

```bash
python prepare_data.py --root_dir datasets/bdd100k
```

3. Your `annotations.json` should look like:
```json
{
  "train": [
    {"video_name": "video_001.mp4", "label": 0, "action_name": "safe"},
    {"video_name": "video_002.mp4", "label": 1, "action_name": "aggressive_driving"}
  ],
  "val": [...],
  "test": [...]
}
```

## Step 4: Configure System

Edit `config.yaml` to customize:

```yaml
# Basic configuration
model:
  architecture: "video_action_detector"
  backbone: "resnet50"
  num_frames: 16

training:
  batch_size: 8  # Reduce if GPU memory is limited
  num_epochs: 50
  learning_rate: 0.001

inference:
  confidence_threshold: 0.7
  alert_cooldown: 3.0
```

## Step 5: Train Your Model

Start training:

```bash
python train.py
```

Monitor with TensorBoard:

```bash
tensorboard --logdir runs
```

Expected output:
```
Starting training...
Epoch 1/50 - Train Loss: 1.2345, Train Acc: 0.6543, Val Loss: 1.1234, Val Acc: 0.7123
Epoch 2/50 - Train Loss: 1.0987, Train Acc: 0.7234, Val Loss: 1.0456, Val Acc: 0.7456
...
```

Training typically takes 2-4 hours on a GPU (depends on dataset size).

## Step 6: Run Real-time Detection

### Test on a Video File

```bash
python inference.py --model checkpoints/best_model.pth --source demo_video.mp4
```

### Test with Webcam

```bash
python inference.py --model checkpoints/best_model.pth --source 0
```

### Test on RTSP Stream

```bash
python inference.py --model checkpoints/best_model.pth --source rtsp://your-stream-url
```

## Expected Output

When running inference, you'll see:

1. **Console Output**:
```
INFO - Detector initialized on device: cuda
INFO - Loaded model from: checkpoints/best_model.pth
INFO - Processing video: demo_video.mp4
WARNING - ⚠️ UNSAFE ACTION DETECTED: tailgating (Confidence: 87.45%) at 2025-10-05 14:30:45
```

2. **Visual Display**:
   - Live video with annotations
   - Action name and confidence score
   - Warning indicators for unsafe actions

3. **Saved Files**:
   - Alert logs: `logs/alerts.log`
   - Video clips: `output/alert_clips/`

## Customization

### Change Detection Sensitivity

More sensitive (more alerts):
```yaml
inference:
  confidence_threshold: 0.5  # Lower threshold
```

Less sensitive (fewer false positives):
```yaml
inference:
  confidence_threshold: 0.9  # Higher threshold
```

### Add Custom Actions

Edit `config.yaml`:
```yaml
unsafe_actions:
  - "your_custom_action_1"
  - "your_custom_action_2"
  # ... add more
```

Update model:
```yaml
model:
  num_classes: 11  # 1 (safe) + 10 (your custom actions)
```

### Change Model Architecture

For faster inference (lower accuracy):
```yaml
model:
  architecture: "video_action_detector"
  backbone: "resnet18"  # Lighter than resnet50
  num_frames: 8  # Fewer frames
```

For better accuracy (slower):
```yaml
model:
  architecture: "lstm"
  backbone: "resnet50"
  num_frames: 32  # More temporal context
```

## Troubleshooting

### Problem: GPU Out of Memory

**Solution 1**: Reduce batch size
```yaml
training:
  batch_size: 4  # or even 2
```

**Solution 2**: Use smaller model
```yaml
model:
  backbone: "resnet18"
  num_frames: 8
```

### Problem: Training Too Slow

**Check**: Is GPU being used?
```bash
python verify.py
```

If GPU not available, you can still train on CPU (will be slower):
```yaml
training:
  device: "cpu"
  batch_size: 2  # Use smaller batch size
```

### Problem: Poor Detection Accuracy

**Solutions**:
1. Train for more epochs: `num_epochs: 100`
2. Collect more training data
3. Balance your dataset (equal safe/unsafe samples)
4. Try different model architecture: `architecture: "lstm"`

### Problem: Too Many False Alarms

**Solutions**:
1. Increase threshold: `confidence_threshold: 0.8`
2. Enable smoothing: `temporal_smoothing: true`
3. Increase cooldown: `alert_cooldown: 5.0`

## Next Steps

1. **Evaluate Model**:
```bash
python evaluate.py --model checkpoints/best_model.pth --split test
```

2. **Fine-tune on Your Data**: 
   - Collect domain-specific videos
   - Annotate with your specific unsafe actions
   - Retrain the model

3. **Deploy**:
   - Set up webhook notifications
   - Integrate with your existing systems
   - Run as a service

4. **Optimize**:
   - Use model quantization for faster inference
   - Batch process multiple streams
   - Deploy on edge devices

## Support

- 📖 Full documentation: See `README.md`
- 🐛 Found a bug? Open an issue on GitHub
- 💡 Have questions? Check troubleshooting section

## Useful Commands Cheat Sheet

```bash
# System check
python demo.py --check

# Create demo video
python demo.py --create-video

# Prepare data
python prepare_data.py --root_dir datasets/bdd100k

# Train model
python train.py

# Evaluate model
python evaluate.py --model checkpoints/best_model.pth

# Real-time detection (webcam)
python inference.py --model checkpoints/best_model.pth --source 0

# Process video file
python inference.py --model checkpoints/best_model.pth --source video.mp4 --output result.mp4

# Monitor training
tensorboard --logdir runs
```

---

**You're all set!** 🎉 If you have any issues, refer to the troubleshooting section or the full README.

