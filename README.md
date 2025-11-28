# ComfyUI Model Installer

A ComfyUI extension that adds a convenient "Install Models" button to the topbar menu for easy model downloads.

## Features

- One-click model installation from the ComfyUI interface
- Real-time download progress in a dedicated window
- Automatically organizes models into their correct folders
- Resumes interrupted downloads
- Skips already downloaded models

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

- wget must be installed on your system
  - **Linux/Mac**: Usually pre-installed
  - **Windows**: Install via [chocolatey](https://chocolatey.org/): `choco install wget`

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

## License

MIT
