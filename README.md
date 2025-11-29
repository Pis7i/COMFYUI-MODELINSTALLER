# ComfyUI Model Installer + PMA Utils

A comprehensive ComfyUI extension pack featuring model management, video processing utilities, and custom nodes.

## Features

### Model Management
- One-click model installation from the ComfyUI interface
- Real-time download progress in a dedicated window
- Automatically organizes models into their correct folders
- Resumes interrupted downloads
- Skips already downloaded models

### Video Processing Nodes
- **Eye Stabilizer**: Fixes eye glitching in video motion transfer workflows (Wan2.2, etc.)
- **Character Swap**: ControlNet-based character face swapping
- Temporal smoothing and enhancement tools

### System Utilities
- Automatic shutdown monitoring with queue detection
- Activity tracking to prevent premature shutdowns
- ComfyUI session management tools

## Installation

1. Navigate to your ComfyUI custom_nodes directory:
```bash
cd ComfyUI/custom_nodes
```

2. Clone or copy this extension:
```bash
git clone https://github.com/yourusername/ComfyUI-ModelInstaller.git
```

Or manually copy the `ComfyUI-ModelInstaller` folder to your `custom_nodes` directory.

3. Restart ComfyUI

## Usage

1. Launch ComfyUI
2. Click on **Model Manager** → **Install Models** in the top menu bar
3. A dialog window will open
4. Click **Start Download** to begin downloading all models
5. Monitor the progress in real-time
6. Close the window when complete

## Requirements

### Core Requirements
- wget must be installed on your system
  - **Linux/Mac**: Usually pre-installed
  - **Windows**: Install via [chocolatey](https://chocolatey.org/): `choco install wget`

### For Eye Stabilizer Node
- MediaPipe (for face detection):
  ```bash
  pip install mediapipe==0.10.21
  ```
  - If not installed, node falls back to basic mode without face tracking

## Models Included

The extension downloads the following models:

1. **ControlNet Union SDXL** - Advanced control model
2. **GFPGAN Face Restore** - Face restoration model
3. **CLIP Vision SDXL** - CLIP vision encoder
4. **GonzalomoXL Checkpoint** - Main checkpoint model
5. **IP-Adapter FaceID Plus v2** - Face identity preservation
6. **SwinIR 4x Upscaler** - Image upscaling model
7. **EpiC Negative Embedding** - Negative prompt embedding
8. **Deep Negative Embedding** - Additional negative embedding

## Adding More Models

To add more models to the download list, edit `model_downloader.py`:

```python
MODELS = [
    {
        "url": "https://example.com/model.safetensors",
        "path": "folder/filename.safetensors",
        "name": "Display Name"
    },
    # Add more models here
]
```

## Troubleshooting

**wget not found error:**
- Install wget on your system
- Linux: `sudo apt-get install wget` or `sudo yum install wget`
- Mac: `brew install wget`
- Windows: `choco install wget`

**Downloads fail:**
- Check your internet connection
- Verify the URLs are still valid
- Ensure you have sufficient disk space

## Custom Nodes Documentation

### Eye Stabilizer
Fixes eye glitching, jittering, and unnatural blinking in video motion transfer workflows.

**Full Documentation**: [EYE_STABILIZER_README.md](EYE_STABILIZER_README.md)  
**Setup Guide**: [SETUP_EYE_STABILIZER.md](SETUP_EYE_STABILIZER.md)  
**Technical Details**: [EYE_STABILIZER_IMPLEMENTATION.md](EYE_STABILIZER_IMPLEMENTATION.md)

**Features**:
- Dense eye landmark detection (478 facial points via MediaPipe)
- Temporal smoothing using Kalman filtering
- Blink detection and synthesis
- Eye region enhancement
- Debug visualization

**Quick Start**:
```
Video → RMBG → [Eye Stabilizer] → DWPose/Depth → WanVaceToVideo
```

**Test Installation**:
```bash
python test_eye_stabilizer.py
```

### Character Swap
ControlNet-based character face swapping for pose/scene transfer.

**Status**: Basic implementation (preprocessors only)  
**Planned**: Full IP-Adapter FaceID integration

## Project Structure

```
ComfyUI-ModelInstaller/
├── __init__.py                          # Main entry point
├── model_downloader.py                  # Model download system
├── shutdown_monitor.py                  # Auto-shutdown utilities
├── character_swap_node.py              # Character swap node
├── eye_stabilizer_node.py              # Eye stabilizer node (NEW)
├── test_eye_stabilizer.py              # Test suite (NEW)
├── README.md                            # This file
├── EYE_STABILIZER_README.md            # Eye stabilizer docs
├── SETUP_EYE_STABILIZER.md             # Setup guide
├── EYE_STABILIZER_IMPLEMENTATION.md    # Technical docs
└── js/
    └── model_installer.js               # Frontend UI
```

## License

MIT
