# ControlNet Face Preservation Node - Implementation Plan

## Concept Overview

Create a ComfyUI node that recreates an input image using ControlNet while preserving the original face. This combines multiple ControlNet types for maximum accuracy with face detection and preservation.

## Technical Approach

### 1. **Multi-ControlNet Strategy**
Use multiple ControlNet models in combination for best image recreation:
- **Canny Edge** - Captures sharp edges and outlines
- **Depth** - Preserves spatial relationships and 3D structure  
- **OpenPose** - Maintains body/pose structure
- **Lineart** - Captures fine details and textures
- **Color** - Preserves color palette and distribution

Each ControlNet will guide the generation to match the reference image structure.

### 2. **Face Detection & Preservation**
- Use **InsightFace** or **MediaPipe** to detect face regions
- Extract face bounding box and landmarks
- Create a mask for the face area
- Preserve original face using **Inpainting** (inverse mask - keep face, regenerate everything else)

### 3. **Workflow Logic**

```
Input Image
    ↓
┌───────────────────────────────┐
│  Face Detection               │
│  - Detect face region         │
│  - Create face mask           │
│  - Extract face crop          │
└───────────────────────────────┘
    ↓
┌───────────────────────────────┐
│  ControlNet Preprocessing     │
│  - Canny edge detection       │
│  - Depth map estimation       │
│  - Pose estimation            │
│  - Lineart extraction         │
│  - Color extraction           │
└───────────────────────────────┘
    ↓
┌───────────────────────────────┐
│  Multi-ControlNet Generation  │
│  - Apply all ControlNets      │
│  - Strength: 0.8-1.0          │
│  - Guided by preprocessors    │
└───────────────────────────────┘
    ↓
┌───────────────────────────────┐
│  Face Composite               │
│  - Blend original face        │
│  - Feather edges (10-20px)    │
│  - Color match if needed      │
└───────────────────────────────┘
    ↓
Output Image (Same structure, original face)
```

## Node Architecture

### Input Ports
1. **image** - Reference image to recreate
2. **model** - Stable Diffusion checkpoint
3. **positive_prompt** - Text prompt (optional, extracted from CLIP interrogation)
4. **negative_prompt** - Negative prompt
5. **controlnet_strength** - Float (0.0-1.0, default 0.85)
6. **face_blend_strength** - Float (0.0-1.0, default 1.0)
7. **feather_radius** - Int (pixels, default 15)
8. **seed** - Random seed

### Output Ports
1. **image** - Final composited image
2. **face_mask** - Generated face mask (for debugging)
3. **controlnet_images** - Preprocessed ControlNet images (optional)

### Processing Steps

```python
class ControlNetFacePreservation:
    def __init__(self):
        self.face_detector = load_insightface()
        self.controlnet_processors = {
            'canny': CannyDetector(),
            'depth': DepthEstimator(),
            'openpose': OpenposeDetector(),
            'lineart': LineartDetector(),
        }
    
    def process(self, image, model, positive, negative, cn_strength, face_strength, feather, seed):
        # Step 1: Face Detection
        faces = self.face_detector.detect(image)
        face_mask = create_mask_from_faces(faces, feather_radius=feather)
        
        # Step 2: ControlNet Preprocessing
        canny_img = self.controlnet_processors['canny'](image)
        depth_img = self.controlnet_processors['depth'](image)
        pose_img = self.controlnet_processors['openpose'](image)
        lineart_img = self.controlnet_processors['lineart'](image)
        
        # Step 3: Multi-ControlNet Generation
        latent = encode_to_latent(image)
        
        # Apply all ControlNets during diffusion
        generated_latent = diffusion_process(
            model=model,
            latent=latent,
            positive=positive,
            negative=negative,
            controlnets=[
                (canny_controlnet, canny_img, cn_strength),
                (depth_controlnet, depth_img, cn_strength),
                (pose_controlnet, pose_img, cn_strength * 0.9),
                (lineart_controlnet, lineart_img, cn_strength * 0.7),
            ],
            seed=seed
        )
        
        generated_image = decode_from_latent(generated_latent)
        
        # Step 4: Face Preservation
        # Composite original face onto generated image
        final_image = composite_images(
            background=generated_image,
            foreground=image,
            mask=face_mask,
            blend_strength=face_strength
        )
        
        return (final_image, face_mask, [canny_img, depth_img, pose_img, lineart_img])
```

## Required Dependencies

### Python Packages
```
insightface>=0.7.3
onnxruntime>=1.16.0
opencv-python>=4.8.0
controlnet-aux>=0.0.6
```

### ComfyUI Custom Nodes
- **ComfyUI-ControlNet-Aux** (for preprocessors)
- **ComfyUI-Impact-Pack** (for face detection, optional alternative)
- **ComfyUI-Reactor** (for face detection, optional alternative)

### Models Required
1. **ControlNet Models:**
   - control_sd15_canny.pth
   - control_sd15_depth.pth
   - control_sd15_openpose.pth
   - control_sd15_lineart.pth

2. **Face Detection Model:**
   - InsightFace models (buffalo_l or antelopev2)

3. **Base Checkpoint:**
   - Any SD 1.5 or SDXL checkpoint

## Implementation Phases

### Phase 1: Basic Structure ✓
- [x] Create node class
- [x] Define input/output types
- [x] Set up basic image processing

### Phase 2: Face Detection
- [ ] Integrate InsightFace or MediaPipe
- [ ] Implement face mask generation
- [ ] Add feathering/blending functions

### Phase 3: ControlNet Integration
- [ ] Load multiple ControlNet models
- [ ] Run preprocessors (canny, depth, pose, lineart)
- [ ] Apply ControlNets to generation

### Phase 4: Composition
- [ ] Implement face blending algorithm
- [ ] Add color matching between face and body
- [ ] Handle edge cases (no face detected, multiple faces)

### Phase 5: Optimization
- [ ] Cache ControlNet models
- [ ] Optimize preprocessing speed
- [ ] Add batch processing support

### Phase 6: UI/UX
- [ ] Add preview outputs for each ControlNet
- [ ] Create preset configurations
- [ ] Add advanced settings toggle

## Advanced Features (Optional)

### 1. **Smart Prompt Generation**
- Use CLIP Interrogator to extract prompt from reference image
- Enhance prompt with detected attributes (pose, style, clothing)

### 2. **Multi-Face Handling**
- Detect and preserve multiple faces
- Individual face strength controls

### 3. **Skin Tone Matching**
- Analyze face skin tone
- Apply color correction to generated body to match face

### 4. **Detail Transfer**
- Transfer specific details (jewelry, tattoos) from reference
- Use additional IP-Adapter for fine details

### 5. **Style Control**
- Separate style strength from structure strength
- Allow artistic interpretation while keeping structure

## Example Use Cases

### Use Case 1: Portrait Recreation
**Input:** Professional headshot photo  
**Goal:** Recreate in different art style while keeping face  
**Settings:** High ControlNet strength (0.9), Full face preservation (1.0)

### Use Case 2: Outfit Swap
**Input:** Person in casual clothes  
**Goal:** Generate in formal wear, same pose, same face  
**Settings:** Medium ControlNet strength (0.7), Full face preservation (1.0), Prompt focuses on outfit

### Use Case 3: Background Change
**Input:** Person in office  
**Goal:** Same person, same pose, outdoor background  
**Settings:** High pose ControlNet (0.9), Lower depth (0.6), Full face preservation (1.0)

## Potential Challenges & Solutions

| Challenge | Solution |
|-----------|----------|
| Face color mismatch with body | Implement color transfer/matching algorithm |
| Visible seams at face boundary | Increase feather radius, use gradient blending |
| ControlNets conflict | Weight different ControlNets, allow priority settings |
| No face detected | Fallback to full image generation or error handling |
| Multiple faces | Allow selection or preserve all faces |
| Performance issues | Cache models, use FP16, optimize preprocessors |

## Testing Strategy

1. **Unit Tests**
   - Face detection accuracy
   - Mask generation quality
   - ControlNet preprocessing

2. **Integration Tests**
   - Full pipeline execution
   - Multi-face scenarios
   - Edge cases (no face, partial face)

3. **Quality Tests**
   - Visual comparison with reference
   - Face preservation accuracy
   - Structural similarity metrics (SSIM)

## Success Metrics

- **Face Preservation:** 95%+ similarity to original face
- **Structure Recreation:** 85%+ structural match to reference
- **Processing Time:** < 30 seconds on RTX 3090
- **User Satisfaction:** Easy to use, reliable results

## Future Enhancements

1. **Video Support** - Process video frames with temporal consistency
2. **Real-time Preview** - Show ControlNet preprocessor outputs live
3. **Auto-tuning** - Automatically adjust strengths based on image analysis
4. **Style Library** - Pre-configured settings for different art styles
5. **API Endpoint** - REST API for external applications

## Conclusion

This node combines the power of multiple ControlNets for maximum structural accuracy while using face detection and masking to preserve the original identity. The multi-stage approach ensures both quality recreation and precise face preservation.

**Estimated Development Time:** 2-3 weeks  
**Complexity:** High  
**Dependencies:** Medium (requires external models and libraries)  
**Value Proposition:** Unique node that solves a common problem with high-quality results
