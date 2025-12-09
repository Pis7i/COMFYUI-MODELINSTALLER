# ControlNet Character Face Swap Node - Implementation Plan

## Concept Overview

Create a ComfyUI node that takes a **reference image** (for pose, clothing, background, scene) and applies a **character's face** from your AI model collection. This lets you place your consistent AI characters into any pose/scene while maintaining their identity.

## Use Case Example

**Input 1:** Reference image of a person sitting at a café (pose + scene)  
**Input 2:** Your AI character model/LoRA or reference face image  
**Output:** Your character sitting at the café in the same pose

## Technical Approach

### 1. **Multi-ControlNet for Structure Transfer**
Extract structure from reference image:
- **OpenPose** - Body pose and skeleton (PRIMARY - most important)
- **Depth** - Spatial depth and 3D structure
- **Canny Edge** - Sharp outlines and composition
- **Normal Map** - Surface details and lighting direction
- **Softedge** - Softer structural guidance

### 2. **Character Face Application Methods**

#### Option A: LoRA-Based (Best for consistent characters)
- Use character-specific LoRA trained on your AI character
- ControlNets guide pose/scene
- LoRA ensures consistent face/identity
- **Strength:** LoRA weight 0.7-1.0

#### Option B: IP-Adapter FaceID (Best for flexibility)
- Use IP-Adapter with FaceID model
- Input: Reference image structure + Character face reference
- Maintains face identity across different scenes
- **Strength:** IP-Adapter weight 0.8-1.0

#### Option C: Reactor/ReActor Face Swap
- Generate image with ControlNets
- Use face swap to replace generated face with character face
- Most accurate face transfer
- Works with any character reference

### 3. **Recommended Hybrid Approach**
Combine multiple methods for best results:

```
Reference Image (pose/scene)
    ↓
┌─────────────────────────────────┐
│  ControlNet Preprocessing       │
│  - OpenPose skeleton            │
│  - Depth map                    │
│  - Canny edges                  │
│  - Normal map                   │
└─────────────────────────────────┘
    ↓
┌─────────────────────────────────┐
│  Initial Generation             │
│  - Base model + Character LoRA  │
│  - Guided by ControlNets        │
│  - Prompt: character description│
└─────────────────────────────────┘
    ↓
┌─────────────────────────────────┐
│  Face Identity Reinforcement    │
│  Option 1: IP-Adapter FaceID    │
│  Option 2: ReActor Face Swap    │
│  - Apply character face         │
│  - Blend seamlessly             │
└─────────────────────────────────┘
    ↓
Output: Character in reference pose/scene
```

## Node Architecture

### Input Ports

#### Required
1. **reference_image** - Source image for pose/background/scene
2. **model** - Base Stable Diffusion checkpoint
3. **character_face_image** - Your character's face reference

#### Character Method (Choose One)
4. **character_lora** - LoRA file for your character (optional)
5. **lora_strength** - Float (0.0-1.5, default 0.8)

#### ControlNet Settings
6. **pose_strength** - Float (0.0-1.5, default 1.0) - Most important
7. **depth_strength** - Float (0.0-1.5, default 0.7)
8. **canny_strength** - Float (0.0-1.5, default 0.5)

#### Generation Settings
9. **positive_prompt** - Character description + scene details
10. **negative_prompt** - Quality negatives
11. **face_method** - Choice ["IP-Adapter FaceID", "ReActor", "Both"]
12. **face_strength** - Float (0.0-1.0, default 0.85)
13. **seed** - Random seed

#### Optional
14. **preserve_clothes** - Boolean (try to keep reference clothing)
15. **preserve_background** - Boolean (keep original background)
16. **style_prompt** - Override style (anime, realistic, etc.)

### Output Ports
1. **image** - Final generated image
2. **pose_preview** - OpenPose skeleton preview
3. **depth_preview** - Depth map preview
4. **face_mask** - Face region mask (debugging)

## Processing Pipeline

```python
class ControlNetCharacterSwap:
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "reference_image": ("IMAGE",),
                "character_face": ("IMAGE",),
                "model": ("MODEL",),
                "positive_prompt": ("STRING", {"multiline": True}),
                "pose_strength": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 2.0}),
                "face_strength": ("FLOAT", {"default": 0.85, "min": 0.0, "max": 1.0}),
            },
            "optional": {
                "character_lora": ("LORA",),
                "lora_strength": ("FLOAT", {"default": 0.8}),
                "depth_strength": ("FLOAT", {"default": 0.7}),
                "canny_strength": ("FLOAT", {"default": 0.5}),
                "face_method": (["IP-Adapter FaceID", "ReActor", "Both"],),
            }
        }
    
    RETURN_TYPES = ("IMAGE", "IMAGE", "IMAGE", "MASK")
    RETURN_NAMES = ("image", "pose_preview", "depth_preview", "face_mask")
    FUNCTION = "generate_character"
    CATEGORY = "PMA Utils/Character"
    
    def generate_character(self, reference_image, character_face, model, 
                          positive_prompt, pose_strength, face_strength,
                          character_lora=None, lora_strength=0.8,
                          depth_strength=0.7, canny_strength=0.5,
                          face_method="IP-Adapter FaceID"):
        
        # STEP 1: Extract ControlNet Maps
        pose_map = openpose_detector(reference_image)
        depth_map = depth_estimator(reference_image)
        canny_map = canny_detector(reference_image)
        
        # STEP 2: Prepare Model
        working_model = model
        if character_lora:
            working_model = apply_lora(model, character_lora, lora_strength)
        
        # STEP 3: Apply ControlNets
        # OpenPose is primary - controls body structure
        latent = apply_controlnet(
            model=working_model,
            controlnet=openpose_controlnet,
            image=pose_map,
            strength=pose_strength
        )
        
        # Depth adds spatial awareness
        latent = apply_controlnet(
            latent=latent,
            controlnet=depth_controlnet,
            image=depth_map,
            strength=depth_strength
        )
        
        # Canny for fine details (lower strength to allow character features)
        latent = apply_controlnet(
            latent=latent,
            controlnet=canny_controlnet,
            image=canny_map,
            strength=canny_strength
        )
        
        # STEP 4: Generate Base Image
        generated_image = generate(
            latent=latent,
            positive=positive_prompt,
            negative=negative_prompt,
            model=working_model
        )
        
        # STEP 5: Apply Character Face
        if face_method == "IP-Adapter FaceID":
            final_image = apply_ipadapter_faceid(
                image=generated_image,
                face_reference=character_face,
                strength=face_strength
            )
        
        elif face_method == "ReActor":
            final_image = reactor_face_swap(
                target_image=generated_image,
                source_face=character_face,
                strength=face_strength
            )
        
        elif face_method == "Both":
            # First IP-Adapter, then ReActor for maximum accuracy
            temp_image = apply_ipadapter_faceid(
                image=generated_image,
                face_reference=character_face,
                strength=face_strength * 0.7
            )
            final_image = reactor_face_swap(
                target_image=temp_image,
                source_face=character_face,
                strength=face_strength
            )
        
        # STEP 6: Generate Previews
        face_mask = detect_face_mask(final_image)
        
        return (final_image, pose_map, depth_map, face_mask)
```

## Workflow Example

### Basic Workflow
```
┌─────────────────┐
│ Reference Image │ (person at café)
└────────┬────────┘
         │
    ┌────▼─────────────────────┐
    │ ControlNet Preprocessors │
    │ - OpenPose               │
    │ - Depth                  │
    │ - Canny                  │
    └────┬─────────────────────┘
         │
    ┌────▼────────────┐      ┌──────────────────┐
    │ SD Generation   │◄─────┤ Character LoRA   │
    │ + ControlNets   │      └──────────────────┘
    └────┬────────────┘
         │
    ┌────▼────────────┐      ┌──────────────────┐
    │ IP-Adapter      │◄─────┤ Character Face   │
    │ FaceID          │      │ Reference        │
    └────┬────────────┘      └──────────────────┘
         │
    ┌────▼────────────┐
    │ Final Output    │ (Your character at café)
    └─────────────────┘
```

## Prompt Strategy

### Positive Prompt Template
```
[CHARACTER NAME/DESCRIPTION], [CHARACTER FEATURES], 
[REFERENCE SCENE DESCRIPTION], [POSE DESCRIPTION],
[STYLE KEYWORDS], high quality, detailed face, 8k
```

**Example:**
```
Emma, young woman with long brown hair, blue eyes, fair skin,
sitting at outdoor café table, holding coffee cup, relaxed pose,
photorealistic, natural lighting, bokeh background, professional photo
```

### Negative Prompt
```
bad face, deformed, ugly, blurry, low quality, bad anatomy, 
extra limbs, wrong proportions, watermark
```

## Required Models & Dependencies

### ControlNet Models (SD 1.5 or SDXL)
- **control_sd15_openpose.pth** - ESSENTIAL
- **control_sd15_depth.pth** - ESSENTIAL  
- **control_sd15_canny.pth** - Recommended
- **control_sd15_normal.pth** - Optional

### Face Models
- **IP-Adapter FaceID Plus v2** - For face identity transfer
  - Model: `ip-adapter-faceid-plusv2_sdxl.bin`
  - CLIP: `clip_vision_SDXL_vit-h.safetensors`

- **ReActor** - For face swapping
  - InsightFace models (buffalo_l)

### ComfyUI Custom Nodes
1. **ComfyUI-ControlNet-Aux** - Preprocessors
2. **ComfyUI-IPAdapter-Plus** - IP-Adapter support
3. **ReActor Node** - Face swapping
4. **ComfyUI-Impact-Pack** - Face detection utilities

### Your Character Assets
- **Character LoRAs** - Trained on your AI characters
- **Character Face References** - Clean face shots of each character

## Character Library Management

### Suggested Structure
```
/models/loras/characters/
    emma_character.safetensors
    john_character.safetensors
    sarah_character.safetensors

/inputs/character_faces/
    emma_face.png
    john_face.png
    sarah_face.png
```

### Node Enhancement: Character Selector
Add dropdown to select from saved characters:

```python
"character_preset": (self.get_character_list(),)

def get_character_list(self):
    # Scan character directory
    return ["Emma", "John", "Sarah", "Custom..."]
```

## Advanced Features

### 1. **Outfit Preservation Mode**
- Extract clothing from reference with segmentation
- Apply clothing ControlNet or inpainting
- Keep character face + reference outfit

### 2. **Background Swapping**
- Segment background from reference
- Replace with custom background
- Keep character + pose

### 3. **Multi-Character Scenes**
- Detect multiple people in reference
- Apply different character faces to each
- Maintain relative positions

### 4. **Expression Transfer**
- Detect facial expression from reference
- Apply expression to character face
- Use expression ControlNet if available

### 5. **Batch Processing**
- Process multiple references with same character
- Generate character pose library
- Automatic prompt generation from reference

## Testing Scenarios

| Scenario | Reference | Character | Expected Result |
|----------|-----------|-----------|-----------------|
| Portrait | Professional headshot | Emma | Emma in professional setting |
| Action | Person jumping | John | John jumping, same pose |
| Group | 3 people at party | Sarah (1 person) | Sarah in same scene/pose |
| Historical | Vintage photo | Emma | Emma in vintage style/setting |
| Fashion | Model on runway | John | John as fashion model |

## Optimization Tips

### For Best Quality
1. **OpenPose Strength:** 0.9-1.2 (maintain pose)
2. **Character LoRA:** 0.7-1.0 (strong character features)
3. **Face Method:** "Both" (IP-Adapter + ReActor)
4. **Resolution:** Match reference or use 1024x1024 for SDXL

### For Speed
1. **Reduce ControlNets:** Use only OpenPose + Depth
2. **Lower Steps:** 20-25 steps sufficient
3. **Skip ReActor:** Use only IP-Adapter FaceID
4. **Batch Process:** Queue multiple generations

### For Consistency Across Images
1. **Use Same LoRA + Weight** for all generations
2. **Use Same Face Reference** image
3. **Lock Seed** for similar variations
4. **Save Workflow** as template

## Common Issues & Solutions

| Problem | Cause | Solution |
|---------|-------|----------|
| Wrong face | Weak face strength | Increase face_strength to 0.9-1.0 |
| Wrong pose | Weak pose ControlNet | Increase pose_strength to 1.2 |
| Blurry face | ControlNet conflict | Lower canny/depth, keep pose high |
| Wrong clothing | Strong clothing from ref | Lower depth_strength, use outfit prompt |
| Background wrong | ControlNets too strong | Lower all except pose, focus prompt on BG |
| Face doesn't match character | LoRA not strong enough | Increase lora_strength or use "Both" face method |

## Implementation Phases

### Phase 1: Core Functionality
- [x] Plan architecture
- [ ] Implement OpenPose ControlNet integration
- [ ] Implement Depth ControlNet integration
- [ ] Basic generation pipeline

### Phase 2: Face Integration
- [ ] IP-Adapter FaceID integration
- [ ] ReActor face swap integration
- [ ] Face blending quality improvements

### Phase 3: LoRA Support
- [ ] Character LoRA loading
- [ ] LoRA strength controls
- [ ] Character library management

### Phase 4: UI/UX
- [ ] Character preset selector
- [ ] Preview outputs for each stage
- [ ] Workflow templates

### Phase 5: Advanced Features
- [ ] Outfit preservation mode
- [ ] Expression transfer
- [ ] Batch processing

## Expected Results

**Quality Metrics:**
- **Face Similarity:** 90%+ match to character reference
- **Pose Accuracy:** 95%+ match to reference pose
- **Scene Coherence:** Natural integration of character into scene
- **Processing Time:** 15-30 seconds per image (RTX 3090)

## Conclusion

This node solves the problem of placing consistent AI characters into arbitrary poses and scenes. By combining ControlNet for structure transfer with face identity models (IP-Adapter/ReActor), you can maintain character consistency while achieving any pose or setting.

**Perfect for:**
- Building character portfolio/lookbooks
- Storytelling with consistent characters
- Virtual fashion/product modeling
- Character-based content creation
- AI influencer content

**Estimated Development Time:** 1-2 weeks  
**Complexity:** Medium-High  
**Value:** Extremely high for character-based workflows
