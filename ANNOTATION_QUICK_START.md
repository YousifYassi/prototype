# 🚀 Quick Start: Video Annotation with Label Studio

## ✅ Setup Complete!

Label Studio is now running on your machine!

### 📍 Access Label Studio

**URL**: http://localhost:8080

Open this in your browser to get started.

### 📊 Your Dataset

- **Total Videos Found**: 8,247 videos
- **Import File Ready**: `labelstudio_import.json`

### 🎯 Step-by-Step Guide

#### 1. Create Your Account (First Time Only)
- Open http://localhost:8080
- Sign up with any email/password (stored locally)
- This is just for your local machine

#### 2. Create a New Project
- Click **"Create Project"**
- Name it: **"Workplace Safety Video Annotations"**
- Click **"Save"**

#### 3. Import Your Videos
- In your project, click **"Import"** button
- Click **"Upload Files"** and select `labelstudio_import.json`
- Wait for import to complete (may take a few minutes for 8,247 videos)

#### 4. Configure Annotation Interface
- Go to **Settings** → **Labeling Interface**
- Click **"Code"** button
- Delete any existing code
- Copy the entire contents of `labelstudio_config.xml`
- Paste it into the editor
- Click **"Save"**

#### 5. Start Annotating! 🎥
- Go back to your project dashboard
- Click on any video to start annotating
- Select violations, rate severity, add notes
- Click **"Submit"** when done

## 📋 Annotation Categories Available

### PPE Violations
- Missing Helmet
- Missing Vest
- Missing Gloves
- Missing Safety Glasses

### Safety Violations
- Unsafe Working at Height
- Improper Lifting Technique
- Unauthorized Area Access
- Equipment Misuse
- Slip/Trip/Fall Hazard
- Fire Safety Violation
- Electrical Safety Violation
- Chemical Handling Violation

### Other
- Safe Behavior
- Other Violation

## 💡 Pro Tips

1. **Keyboard Shortcuts**: Learn them in Label Studio to speed up annotation
2. **Filters**: Use filters to focus on specific video types
3. **Save Often**: Click Submit after each video
4. **Team Work**: Multiple people can annotate simultaneously
5. **Regular Exports**: Export your work regularly (JSON or CSV format)

## 📤 Exporting Your Annotations

When you're ready to export:

1. Go to your project
2. Click **"Export"** button
3. Choose format:
   - **JSON**: Best for training (recommended)
   - **CSV**: Good for analysis
   - **COCO**: For object detection models

## 🔄 Using Annotations for Training

After exporting, you can use this script to prepare training data:

```python
import json

# Load your exported annotations
with open('label-studio-export.json', 'r') as f:
    annotations = json.load(f)

# Process for training
training_data = []
for item in annotations:
    if 'annotations' in item and item['annotations']:
        video_path = item['data']['video'].replace('file:///', '')
        
        # Extract all labels
        labels = []
        severity = 0
        
        for result in item['annotations'][0]['result']:
            if result['from_name'] == 'action':
                labels = result['value']['choices']
            elif result['from_name'] == 'severity':
                severity = result['value']['rating']
        
        training_data.append({
            'video': video_path,
            'labels': labels,
            'severity': severity
        })

# Save for training
with open('training_annotations.json', 'w') as f:
    json.dump(training_data, f, indent=2)

print(f"Processed {len(training_data)} annotated videos")
```

## 🛠️ Troubleshooting

### Videos Not Loading?
- Check browser console for errors
- Ensure video codec is supported (H.264 works best)
- Try a different browser (Chrome/Firefox recommended)

### Label Studio Won't Start?
```bash
# Stop any existing instances
taskkill /F /IM label-studio.exe

# Start on different port
label-studio start --port 8081
```

### Import Failed?
- Check `labelstudio_import.json` exists
- Verify video paths are correct
- Try importing in smaller batches

## 📚 Resources

- **Full Guide**: See `LABELSTUDIO_GUIDE.md`
- **Label Studio Docs**: https://labelstud.io/guide/
- **Video Annotation Tutorial**: https://labelstud.io/guide/video.html

## 🎬 What's Next?

1. **Annotate Sample Videos**: Start with 50-100 videos to test your workflow
2. **Review Quality**: Check inter-annotator agreement if using multiple annotators
3. **Export & Train**: Use annotations to improve your model
4. **Iterate**: Retrain, evaluate, annotate more as needed

---

**Happy Annotating! 🎉**

For questions or issues, check the full guide in `LABELSTUDIO_GUIDE.md`

