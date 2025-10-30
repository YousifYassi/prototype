# CoVLA Dataset Integration

This project now supports the **CoVLA Dataset** from Turing Motors via Hugging Face, providing access to 80+ hours of real-world driving videos with trajectory data and annotations.

## Dataset Overview

- **Source**: [turing-motors/CoVLA-Dataset](https://huggingface.co/datasets/turing-motors/CoVLA-Dataset)
- **Content**: 10,000 30-second video clips
- **Total Duration**: 80+ hours of real-world driving videos
- **Annotations**: Natural language descriptions and trajectory data
- **License**: Academic and non-commercial use only

## Setup Instructions

### 1. Install Required Dependencies

```bash
pip install datasets huggingface_hub
```

### 2. Accept License Terms

1. Visit the [CoVLA Dataset page](https://huggingface.co/datasets/turing-motors/CoVLA-Dataset)
2. Accept the license terms and conditions
3. (Optional) Create a Hugging Face account and login:
   ```bash
   huggingface-cli login
   ```

### 3. Configure Dataset

Edit `config.yaml` to use CoVLA dataset:

```yaml
dataset:
  name: "covla"  # Switch from "bdd100k" to "covla"
  hf_dataset_name: "turing-motors/CoVLA-Dataset"
  cache_dir: "data/covla_cache"
  use_mini: false  # Set to true for testing
```

### 4. Test Integration

Run the test script to verify everything works:

```bash
python test_covla_dataset.py
```

### 5. Start Training

```bash
python train.py
```

## Configuration Options

### Dataset Selection

```yaml
dataset:
  name: "covla"  # Options: "bdd100k", "covla"
```

### CoVLA-Specific Settings

```yaml
dataset:
  # Use mini dataset for testing (faster download)
  use_mini: true  # Uses CoVLA-Dataset-Mini
  
  # Custom cache directory
  cache_dir: "data/covla_cache"
  
  # Hugging Face dataset name
  hf_dataset_name: "turing-motors/CoVLA-Dataset"
```

## Dataset Features

### Automatic Label Extraction

The integration automatically extracts unsafe driving labels from CoVLA annotations by detecting keywords like:
- "aggressive", "dangerous", "unsafe", "reckless"
- "speeding", "tailgating", "cutting off"
- "running red", "wrong way", "near miss"
- "collision", "accident", "violation"

### Video Processing

- **Frame Sampling**: Configurable number of frames per clip
- **Resolution**: Resizable input frames (default: 224x224)
- **Augmentation**: Built-in data augmentation support
- **Caching**: Automatic local caching of downloaded videos

### Memory Management

- Videos are temporarily stored during training
- Automatic cleanup of temporary files
- Efficient streaming for large datasets

## Troubleshooting

### Common Issues

1. **License Error**: Make sure you've accepted the license terms on Hugging Face
2. **Download Error**: Check internet connection and try `huggingface-cli login`
3. **Memory Issues**: Reduce batch size or use `use_mini: true` for testing
4. **Slow Loading**: The first run downloads the dataset; subsequent runs use cached data

### Performance Tips

- Use `use_mini: true` for initial testing
- Reduce `num_frames` in model config for faster training
- Increase `num_workers` for faster data loading (if you have multiple CPU cores)
- Use GPU acceleration for training (see GPU_SETUP_GUIDE.md)

## Switching Between Datasets

To switch back to BDD100K:

```yaml
dataset:
  name: "bdd100k"  # Change back to BDD100K
  root_dir: "datasets/bdd100k"
  annotations_file: "datasets/bdd100k/annotations.json"
```

## Advanced Usage

### Custom Label Mapping

You can extend the `_extract_action_label` method in `CoVLADataset` to implement custom label extraction based on your specific needs.

### Trajectory Data

The CoVLA dataset includes trajectory data that can be accessed through the Hugging Face dataset structure. You can extend the dataset class to utilize this information for more sophisticated action detection.

### Multi-Modal Training

Combine video frames with trajectory data and text annotations for enhanced model performance.

