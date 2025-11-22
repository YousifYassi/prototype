# Label Studio Setup for Workplace Safety Video Annotation

This guide will help you set up Label Studio to annotate videos for improving the workplace safety model.

## Quick Start

### 1. Install and Setup Label Studio

```bash
python setup_labelstudio.py
```

This will:
- Install Label Studio and dependencies
- Scan your dataset folders for all video files
- Create an import file (`labelstudio_import.json`) with all videos

### 2. Start Label Studio

```bash
python start_labelstudio.py
```

Or manually:
```bash
label-studio start --data-dir label-studio-data
```

Label Studio will open in your browser at: http://localhost:8080

### 3. Create Your First Project

1. **Sign up/Login**: Create an account (stored locally)
2. **Create New Project**: Click "Create Project"
3. **Project Name**: e.g., "Workplace Safety Video Annotations"
4. **Import Data**:
   - Click on the "Import" button
   - Upload the `labelstudio_import.json` file
   - Or manually add video URLs/paths

### 4. Configure Labeling Interface

1. Go to **Settings** → **Labeling Interface**
2. Click **Code** to edit the XML configuration
3. Copy the entire contents of `labelstudio_config.xml` and paste it
4. Click **Save**

### 5. Start Annotating!

Click on any task to begin annotating videos.

## Annotation Categories

The configuration includes the following workplace safety categories:

### PPE Violations
- No PPE - Missing Helmet
- No PPE - Missing Vest
- No PPE - Missing Gloves
- No PPE - Missing Safety Glasses

### Safety Violations
- Unsafe Working at Height
- Improper Lifting Technique
- Unauthorized Area Access
- Equipment Misuse
- Slip/Trip/Fall Hazard
- Fire Safety Violation
- Electrical Safety Violation
- Chemical Handling Violation

### Positive Behaviors
- Safe Behavior

### Other
- Other Violation

## Features

### 1. Multi-label Classification
Select multiple violations per video if needed.

### 2. Severity Rating
Rate the severity of violations from 1-5 stars.

### 3. Time-based Annotations
Use the VideoRectangle tool to:
- Mark specific frames where violations occur
- Draw bounding boxes around safety issues
- Track objects through video frames

### 4. Additional Notes
Add detailed observations and context in the text area.

## Exporting Annotations

Once you've annotated videos, you can export the data:

1. Go to your project
2. Click **Export**
3. Choose format:
   - **JSON**: For custom processing
   - **CSV**: For spreadsheet analysis
   - **COCO**: For object detection training
   - **YOLO**: For YOLO format training

## Data Structure

Your annotated data will be in this format:

```json
{
  "id": 1,
  "data": {
    "video": "file:///path/to/video.mp4"
  },
  "annotations": [{
    "result": [
      {
        "value": {
          "choices": ["No PPE - Missing Helmet"]
        },
        "from_name": "action",
        "to_name": "video",
        "type": "choices"
      },
      {
        "value": {
          "rating": 4
        },
        "from_name": "severity",
        "to_name": "video",
        "type": "rating"
      }
    ]
  }]
}
```

## Integration with Training

After annotating, you can use the exported data to:

1. **Fine-tune your model**: Use the annotations as ground truth labels
2. **Evaluate performance**: Compare model predictions with human annotations
3. **Create training datasets**: Build balanced datasets for specific violation types

### Example: Converting Label Studio exports to training data

```python
import json

# Load Label Studio export
with open('label-studio-export.json', 'r') as f:
    annotations = json.load(f)

# Process annotations
training_data = []
for item in annotations:
    video_path = item['data']['video'].replace('file://', '')
    
    # Extract labels
    labels = []
    severity = 0
    
    for annotation in item['annotations'][0]['result']:
        if annotation['from_name'] == 'action':
            labels = annotation['value']['choices']
        elif annotation['from_name'] == 'severity':
            severity = annotation['value']['rating']
    
    training_data.append({
        'video': video_path,
        'labels': labels,
        'severity': severity
    })

# Save processed data
with open('processed_annotations.json', 'w') as f:
    json.dump(training_data, f, indent=2)
```

## Tips for Efficient Annotation

1. **Batch Processing**: Annotate similar videos together
2. **Use Shortcuts**: Learn keyboard shortcuts in Label Studio
3. **Multiple Annotators**: Have multiple people annotate for inter-annotator agreement
4. **Regular Exports**: Export your work regularly to avoid data loss
5. **Clear Guidelines**: Create annotation guidelines for consistency

## Troubleshooting

### Videos not loading
- Make sure video paths are absolute paths
- Check file permissions
- Verify video codecs are supported by your browser

### Label Studio won't start
```bash
# Reinstall Label Studio
pip install --upgrade label-studio

# Or use a different port
label-studio start --port 8081
```

### Import file not working
- Ensure `labelstudio_import.json` exists
- Check JSON formatting
- Verify video file paths are correct

## Available Video Datasets

The setup script will automatically find videos in:
- `datasets/bdd100k/videos/` (100 training + 20 test videos)
- `datasets/CharadesEgo_v1/videos/`
- `datasets/missing_files_v1-2_test/videos/`
- `backend/uploads/` (10 uploaded videos)

## Advanced Configuration

### Custom Labels
Edit `labelstudio_config.xml` to add or modify labels:

```xml
<Choices name="action" toName="video" choice="multiple">
  <Choice value="Your Custom Label"/>
</Choices>
```

### Adding More Annotation Types
You can add:
- **Text transcription**: `<TextArea>`
- **Audio segments**: `<Audio>` with `<Labels>`
- **Key points**: `<KeyPoint>`
- **Polygons**: `<PolygonLabels>`

### Team Collaboration
Label Studio supports multiple users. Each annotator can:
- Have their own account
- Work on assigned tasks
- Review others' annotations

## Resources

- [Label Studio Documentation](https://labelstud.io/guide/)
- [Video Annotation Guide](https://labelstud.io/guide/video.html)
- [ML Backend Integration](https://labelstud.io/guide/ml.html)

## Next Steps

After annotation:
1. Export your annotations
2. Update your training pipeline to use the new labels
3. Retrain the model with annotated data
4. Evaluate improvements in model accuracy

