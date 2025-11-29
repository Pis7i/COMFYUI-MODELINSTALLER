# Eye Stabilizer - Quick Setup Guide

## Installation Steps

### 1. Install MediaPipe Dependency

Choose one of the following methods:

#### Method A: Direct pip install (Recommended)
```bash
# Navigate to your ComfyUI directory
cd /path/to/ComfyUI

# Activate ComfyUI's Python environment if using venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install MediaPipe
pip install mediapipe==0.10.24
```

#### Method B: Using requirements.txt (Already added)
```bash
# The dependency is already in comfypips/requirements.txt
# Just run your sync script
cd /Users/pishtiwan/Documents/COMFYUI\ MODEL\ INSTALLER/comfypips
python venv_sync.py
```

### 2. Verify Installation

Restart ComfyUI and check the console for:
```
[PMA Utils] Eye stabilizer node loaded
```

### 3. Find the Node

In ComfyUI interface:
1. Right-click → **Add Node**
2. Navigate to: **PMA Utils** → **Video Processing**
3. Select: **PMA Eye Stabilizer**

## Quick Start: Integrating into Wan2.2 Workflow

### Current Workflow Structure
```
Node 61 (RMBG) 
    ↓
Node 60 (AIO_Preprocessor - DWPose)
    ↓
Node 69 (DepthAnythingV2)
```

### Modified Workflow Structure
```
Node 61 (RMBG) 
    ↓
PMA Eye Stabilizer ← [INSERT HERE]
    ↓
Node 60 (AIO_Preprocessor - DWPose)
    ↓
Node 69 (DepthAnythingV2)
```

### Step-by-Step Integration

1. **Open your Wan2.2 workflow JSON**
   - File: `Rapid-Wan2.2-All-In-One-Mega-NSFW (Motion Transfer) SeedVR 2.json`

2. **Locate Node 61 (RMBG)**
   - This node outputs to links: 196, 213
   - Link 213 goes to Node 69 (Depth)
   - Link 196 goes to Node 60 (Pose)

3. **Add Eye Stabilizer Node**
   - Right-click → Add Node → PMA Utils → Video Processing → PMA Eye Stabilizer
   - Position it between RMBG and the preprocessors

4. **Rewire Connections**

   **Original**:
   ```
   RMBG (61) output → DWPose (60) input
   RMBG (61) output → Depth (69) input
   ```

   **Modified**:
   ```
   RMBG (61) output → Eye Stabilizer input
   Eye Stabilizer output → DWPose (60) input
   Eye Stabilizer output → Depth (69) input
   ```

5. **Set Initial Parameters**
   - `enable_temporal_smoothing`: ✓ True
   - `enable_blink_detection`: ✓ True
   - `enable_eye_enhancement`: ✓ True
   - `smoothing_strength`: 0.7
   - `enhancement_strength`: 1.3
   - `blink_threshold`: 0.2
   - `eye_region_dilation`: 10

6. **Test Run**
   - Use a short test video (10-20 frames)
   - Check debug visualization output
   - Adjust parameters based on results

## Visual Connection Guide

### Before Eye Stabilizer
```
┌─────────────────┐
│  VHS_LoadVideo  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   ImageResize   │
└────────┬────────┘
         │
         ▼
    ┌────────┐
    │  RMBG  │──────┐
    └────────┘      │
         │          │
         │          │
    ┌────▼────┐  ┌──▼───────────┐
    │ DWPose  │  │ DepthAnything│
    └─────────┘  └──────────────┘
```

### After Eye Stabilizer
```
┌─────────────────┐
│  VHS_LoadVideo  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   ImageResize   │
└────────┬────────┘
         │
         ▼
    ┌────────┐
    │  RMBG  │
    └────┬───┘
         │
         ▼
┌─────────────────┐
│ Eye Stabilizer  │◄──── [NEW NODE]
└────────┬────────┘
         │
         │
    ┌────▼────┐  ┌──▼───────────┐
    │ DWPose  │  │ DepthAnything│
    └─────────┘  └──────────────┘
```

## Parameter Tuning Quick Reference

### If Eyes Are Still Glitching
→ **Increase** `smoothing_strength` to 0.8 or 0.9

### If Eyes Look Robotic/Frozen
→ **Decrease** `smoothing_strength` to 0.5 or 0.6

### If Blinks Not Smooth
→ **Lower** `blink_threshold` to 0.15

### If False Blink Detections
→ **Raise** `blink_threshold` to 0.25 or 0.3

### If Eyes Look Blurry
→ **Increase** `enhancement_strength` to 1.5

### If Eyes Look Over-Sharpened
→ **Decrease** `enhancement_strength` to 1.1 or 1.2

## Testing Checklist

After integration, test these scenarios:

- [ ] Normal eye movement (smooth tracking)
- [ ] Blinking (natural transitions)
- [ ] Fast head movement (no jitter)
- [ ] Close-up shots (detail preservation)
- [ ] Low-light scenes (stability)
- [ ] Multiple consecutive blinks (consistency)

## Debugging

### Enable Debug Output

1. Connect the **debug_visualization** output to a **Preview Image** node
2. Run workflow and check visualization:
   - **Green circles** = Eye outline detected ✓
   - **Blue circles** = Iris detected ✓
   - **Red "BLINK" text** = Blink detected ✓
   - **No circles** = Face not detected ✗

### Common Issues

**No landmarks visible in debug**:
- Face not detected
- Install MediaPipe: `pip install mediapipe`
- Check face is forward-facing

**Landmarks jumping around**:
- Increase `smoothing_strength`
- Check input video quality

**Processing very slow**:
- Normal: 1-2s per frame with MediaPipe
- Disable features you don't need
- Process in smaller batches

## Performance Tips

1. **Process in batches**: Don't exceed 100 frames per batch
2. **Use GPU**: Ensure CUDA is available for frame processing
3. **Disable unused features**: Turn off features you don't need
4. **Lower resolution**: Process at 512x512, upscale later

## Next Steps

After successful integration:

1. Run full workflow with your reference image and video
2. Compare output quality before/after Eye Stabilizer
3. Fine-tune parameters for your specific use case
4. Save workflow with new settings

## Example Workflow Modifications

### For Node 60 (AIO_Preprocessor) Input
```json
"inputs": [
  {
    "name": "image",
    "type": "IMAGE",
    "link": XXX  ← Change this link to Eye Stabilizer output
  }
]
```

### For Node 69 (DepthAnythingV2) Input
```json
"inputs": [
  {
    "name": "image",
    "type": "IMAGE",
    "link": YYY  ← Change this link to Eye Stabilizer output
  }
]
```

## Support Resources

- **Full Documentation**: `EYE_STABILIZER_README.md`
- **Technical Details**: See node code in `eye_stabilizer_node.py`
- **Workflow Analysis**: `IMPLEMENTATION_SUMMARY.md`

## Success Metrics

You'll know it's working when:
- ✓ Eyes maintain consistent position across frames
- ✓ Blinks appear smooth and natural (3-5 frames)
- ✓ Eye details remain sharp and clear
- ✓ No jittering or jumping
- ✓ Gaze direction stable
- ✓ Iris position tracked accurately

Good luck! 🎬👁️
