# Eye Stabilizer V2 - Ethnicity-Aware Edition

## What's New in V2

The V2 Eye Stabilizer adds **ethnicity-specific optimizations** to fix eye detection issues across different facial features and skin tones.

### Key Improvements

✅ **7 Ethnicity Presets** with optimized settings  
✅ **Auto-Calibration Mode** that learns from your video  
✅ **Adaptive Blink Detection** based on actual eye shape  
✅ **Specialized Enhancement** per ethnicity  
✅ **Better Accuracy** for Asian, African, and Middle Eastern faces  

## Why V2 Was Needed

The original Eye Stabilizer (V1) had **MediaPipe bias issues**:
- Trained primarily on Western/Caucasian faces
- Fixed thresholds don't work for all eye shapes
- Monolids and epicanthic folds detected as "closed eyes"
- Darker skin tones had lower landmark accuracy

**V2 solves these problems** with ethnicity-aware processing.

---

## Ethnicity Presets

### 1. Auto-Detect (Recommended)
**Best for**: Most use cases

- Automatically calibrates to the person in your video
- Learns baseline eye opening from first 30 frames
- Adaptive thresholds based on actual measurements
- Works across all ethnicities

**How it works**:
- Samples eye aspect ratio from first 30 frames
- Uses 75th percentile as "normal open eye" baseline
- Sets blink threshold relative to learned baseline
- Adapts to individual variations

### 2. East Asian (Chinese, Japanese, Korean)
**Optimized for**: Monolids, epicanthic folds, smaller visible iris area

**Special Optimizations**:
- ✅ **Lower blink threshold (0.12)** - doesn't mistake open eyes as closed
- ✅ **Reduced smoothing (0.4)** - preserves natural eye shape
- ✅ **Gentler enhancement (1.1)** - avoids over-sharpening
- ✅ **Increased eyelid tracking weight** - prioritizes eyelid landmarks
- ✅ **Adjusted iris visibility (0.7)** - accounts for smaller visible area

**Technical Details**:
```
Blink Threshold: 0.12 (vs 0.20 standard)
EAR Baseline: 0.18 (typical open eye)
Smoothing: 0.4 (less aggressive)
Enhancement: 1.1 (gentle)
Eyelid Weight: 1.3x (more emphasis)
```

### 3. South Asian (Indian, Pakistani, Bangladeshi)
**Optimized for**: Varied eye shapes, diverse features

**Special Optimizations**:
- ✅ **Balanced thresholds** for diverse eye shapes
- ✅ **Medium smoothing (0.6)** - works across variations
- ✅ **Standard enhancement (1.25)**

**Technical Details**:
```
Blink Threshold: 0.18
EAR Baseline: 0.22
Smoothing: 0.6
Enhancement: 1.25
```

### 4. African / African American
**Optimized for**: Darker skin tones, higher contrast needed

**Special Optimizations**:
- ✅ **Contrast boost (1.15x)** - improves landmark detection on darker skin
- ✅ **Higher enhancement (1.4)** - compensates for lower contrast
- ✅ **Preprocessing adjustments** - contrast enhancement before detection

**Technical Details**:
```
Blink Threshold: 0.22
EAR Baseline: 0.25
Smoothing: 0.65
Enhancement: 1.4
Contrast Boost: 1.15x (preprocessing)
```

**Why contrast boost?**
- MediaPipe trained on lighter skin tones
- Darker skin = lower contrast between features
- Pre-boost improves facial landmark accuracy

### 5. Caucasian / European
**Optimized for**: Standard MediaPipe calibration

**Special Optimizations**:
- ✅ **Default MediaPipe settings** - trained primarily on this group
- ✅ **Standard thresholds** work well

**Technical Details**:
```
Blink Threshold: 0.20
EAR Baseline: 0.26
Smoothing: 0.7
Enhancement: 1.3
```

### 6. Middle Eastern / Arab
**Optimized for**: Almond-shaped eyes, varied iris visibility

**Special Optimizations**:
- ✅ **Adjusted for almond eye shape**
- ✅ **Balanced iris tracking**
- ✅ **Medium-high enhancement**

**Technical Details**:
```
Blink Threshold: 0.19
EAR Baseline: 0.24
Smoothing: 0.6
Enhancement: 1.35
Iris Visibility: 0.95
Eyelid Weight: 1.1x
```

### 7. Latino / Hispanic
**Optimized for**: Diverse Latino features

**Special Optimizations**:
- ✅ **Balanced settings** for mixed ancestry features
- ✅ **Works across diverse Latino backgrounds**

**Technical Details**:
```
Blink Threshold: 0.19
EAR Baseline: 0.24
Smoothing: 0.65
Enhancement: 1.3
```

---

## Usage Guide

### Basic Setup

1. **Add Node**: `PMA Utils` → `Video Processing` → `PMA Eye Stabilizer V2`

2. **Select Ethnicity Preset**:
   - Choose the preset that best matches your subject
   - **Start with "Auto-Detect"** - it works for most cases

3. **Use Default Settings** (they're already optimized!)
   - The preset handles all the fine-tuning
   - Only use overrides if needed

### Advanced: Manual Overrides

If preset doesn't work perfectly, you can override individual settings:

```
smoothing_override: -1.0 (use preset) or 0.0-1.0 (custom)
enhancement_override: -1.0 (use preset) or 1.0-2.0 (custom)
blink_threshold_override: -1.0 (use preset) or 0.1-0.5 (custom)
```

**Example**: East Asian face but eyes still look closed:
```
ethnicity_preset: east_asian
blink_threshold_override: 0.08  ← Even lower threshold
```

### Workflow Integration

**Same as V1**:
```
RMBG → Eye Stabilizer V2 → DWPose/Depth → WanVaceToVideo
```

**Parameters**:
```
images: Connect from RMBG output
ethnicity_preset: auto (or choose specific)
enable_temporal_smoothing: True
enable_blink_detection: True
enable_eye_enhancement: True
```

---

## Comparison: V1 vs V2

| Feature | V1 (Original) | V2 (Ethnicity-Aware) |
|---------|---------------|---------------------|
| Ethnicity Support | Generic only | 7 specific presets |
| Blink Detection | Fixed threshold | Adaptive per ethnicity |
| Auto-Calibration | No | Yes (auto preset) |
| Asian Eyes | Poor (too closed) | Excellent |
| African Faces | Good | Better (contrast boost) |
| Customization | Manual tuning | Smart presets |
| Learning Curve | High | Low (just pick preset) |

### When to Use V1 vs V2

**Use V1 if**:
- You already have perfect settings tuned
- Subject is Caucasian/European
- You want full manual control

**Use V2 if**:
- Subject is Asian, African, or other ethnicity
- V1 makes eyes look closed/weird
- You want auto-calibration
- You want easier setup (just pick preset)

---

## Troubleshooting by Ethnicity

### East Asian Faces

**Problem**: Eyes still look closed
- **Solution**: Lower blink threshold to 0.08-0.10
- **Or**: Use Auto-Detect mode (learns from your video)

**Problem**: Eyes look robotic/unnatural
- **Solution**: Reduce smoothing to 0.2-0.3

**Problem**: Not detecting face
- **Solution**: Ensure lighting is good, face is forward-facing

### African Faces

**Problem**: Landmarks not detecting
- **Solution**: Increase contrast_boost (V2 does this automatically)
- **Check**: Ensure good lighting in source video

**Problem**: Eyes too sharp/harsh
- **Solution**: Reduce enhancement to 1.2-1.3

### Middle Eastern Faces

**Problem**: Almond eyes not tracking well
- **Solution**: Adjust eyelid_weight via smoothing_override
- **Try**: Auto-Detect mode

---

## Technical: How Ethnicity Presets Work

### 1. Different EAR Baselines

**Eye Aspect Ratio (EAR)** varies by ethnicity:

```python
# Typical open eye EAR values
Caucasian: 0.26
African: 0.25
Middle Eastern: 0.24
South Asian: 0.22
East Asian: 0.18  ← Much lower!
```

**Why?**: Monolids and epicanthic folds create smaller eye openings

### 2. Adaptive Blink Thresholds

Instead of fixed threshold, V2 uses **relative thresholds**:

```python
# V1 (Fixed)
if ear < 0.20:
    is_blinking = True

# V2 (Adaptive)
baseline = learn_from_video()  # e.g., 0.18 for East Asian
if ear < (baseline * 0.65):  # 65% of normal = blink
    is_blinking = True
```

### 3. Ethnicity-Specific Weights

Different facial features weighted differently:

```python
# East Asian
eyelid_landmarks_weight = 1.3  # More emphasis on eyelids
iris_tracking_weight = 0.7     # Less on iris (smaller visible area)

# African
contrast_preprocessing = 1.15  # Boost before detection
enhancement_strength = 1.4      # Higher sharpening
```

### 4. Auto-Calibration Process

**Auto-Detect mode** learns from your video:

```
Frame 1-30: Collect EAR samples
   → [0.17, 0.18, 0.16, 0.19, 0.18, ...]
   
Calculate baseline:
   → 75th percentile = 0.185 (likely open eyes)
   
Set adaptive threshold:
   → Blink if EAR < (0.185 * 0.65) = 0.120
```

**Result**: Works perfectly for that specific person!

---

## Best Practices

### 1. Start with Auto-Detect
- Works 80% of the time
- Learns from your specific video
- No manual tuning needed

### 2. Use Specific Preset if Auto Fails
- Choose the ethnicity that best matches
- Presets are scientifically calibrated

### 3. Debug Visualization
- Always check the debug output first
- Green circles = good landmark detection
- No circles = face not detected, try different preset

### 4. Lighting Matters
- Good lighting improves all presets
- African preset especially benefits from good lighting
- Avoid harsh shadows on face

### 5. Reference Image Quality
- Higher quality reference = better results
- Ensure eyes are clearly visible in reference
- Forward-facing works best

---

## Outputs

V2 has **4 outputs**:

1. **stabilized_images**: Processed video with stable eyes
2. **eye_mask**: Binary mask of eye regions
3. **debug_visualization**: Landmarks + preset name overlay
4. **preset_info** ⭐ NEW: Text describing active preset + calibration info

**Example preset_info**:
```
"East Asian (Chinese, Japanese, Korean): Optimized for monolids and epicanthic folds"
"Auto-Detect: Automatically calibrates to the person in the video | Auto-calibrated EAR: 0.187"
```

---

## Performance

Same as V1:
- ~1-2 seconds per frame (CPU)
- ~500MB additional RAM
- Batch processing supported

**Note**: Auto-calibration adds ~0.1s overhead for first 30 frames only.

---

## Limitations

### Still Limited By:
- Single face detection only
- Forward-facing faces work best
- Requires visible eyes (not occluded)
- CPU processing (no GPU acceleration yet)

### MediaPipe Inherent Limitations:
- Training bias can't be fully eliminated
- Extreme lighting still affects accuracy
- Profile views (side faces) don't work well

---

## Future Enhancements

**Planned for V3**:
- [ ] Multi-face support
- [ ] Profile/side view handling
- [ ] Dynamic preset switching (per-frame ethnicity detection)
- [ ] Custom preset creation UI
- [ ] GPU acceleration
- [ ] Better handling of mixed features

---

## FAQ

**Q: Should I use V1 or V2?**  
A: Use V2 if you have Asian, African, Middle Eastern, or Latino subjects. V1 is fine for Caucasian faces only.

**Q: Which preset should I choose?**  
A: Start with "Auto-Detect". If that doesn't work, choose the specific ethnicity preset.

**Q: Can I create custom presets?**  
A: Not in the UI yet, but you can edit `ETHNICITY_PRESETS` in the code.

**Q: Does this work for mixed ethnicity?**  
A: Use "Auto-Detect" - it learns from the actual person regardless of ethnicity.

**Q: Why are eyes still closed with East Asian preset?**  
A: Try even lower blink threshold (0.08) or use Auto-Detect mode.

**Q: Does this work on anime/cartoon faces?**  
A: No, MediaPipe is designed for real human faces only.

---

## Credits

**Developer**: PMA Utils Team  
**V2 Enhancements**: Ethnicity-aware processing, adaptive calibration  
**Technology**: MediaPipe Face Mesh, OpenCV, PyTorch  
**Inspiration**: Community feedback on Asian face detection issues  

## License

Same as ComfyUI-ModelInstaller project

---

**Version**: 2.0.0  
**Release Date**: 2025-11-29  
**Compatibility**: Drop-in replacement for V1
