import torch
import numpy as np
from PIL import Image
import folder_paths
import comfy.model_management as mm


class CharacterSwapNode:
    """
    ComfyUI node that takes a reference image for pose/scene and applies a character's face.
    Uses ControlNet for structure transfer and face models for identity preservation.
    """
    
    def __init__(self):
        self.type = "CharacterSwapNode"
        
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "reference_image": ("IMAGE",),
                "character_face": ("IMAGE",),
                "positive_prompt": ("STRING", {
                    "multiline": True,
                    "default": "high quality, detailed face, professional photo, 8k"
                }),
                "negative_prompt": ("STRING", {
                    "multiline": True,
                    "default": "bad face, deformed, ugly, blurry, low quality, bad anatomy"
                }),
                "pose_strength": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 2.0,
                    "step": 0.05,
                    "display": "slider"
                }),
                "depth_strength": ("FLOAT", {
                    "default": 0.7,
                    "min": 0.0,
                    "max": 2.0,
                    "step": 0.05,
                    "display": "slider"
                }),
                "face_strength": ("FLOAT", {
                    "default": 0.85,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.05,
                    "display": "slider"
                }),
                "seed": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 0xffffffffffffffff
                }),
            },
            "optional": {
                "canny_strength": ("FLOAT", {
                    "default": 0.5,
                    "min": 0.0,
                    "max": 2.0,
                    "step": 0.05,
                    "display": "slider"
                }),
            }
        }
    
    RETURN_TYPES = ("IMAGE", "IMAGE", "IMAGE")
    RETURN_NAMES = ("output_image", "pose_preview", "depth_preview")
    FUNCTION = "swap_character"
    CATEGORY = "PMA Utils/Character"
    
    def swap_character(self, reference_image, character_face, positive_prompt, 
                      negative_prompt, pose_strength, depth_strength, face_strength, 
                      seed, canny_strength=0.5):
        """
        Main function to swap character face into reference pose/scene.
        
        Args:
            reference_image: Source image for pose/background/scene
            character_face: Character's face reference image
            positive_prompt: Text prompt for generation
            negative_prompt: Negative prompt
            pose_strength: OpenPose ControlNet strength
            depth_strength: Depth ControlNet strength
            face_strength: Face identity strength
            seed: Random seed
            canny_strength: Canny edge ControlNet strength
            
        Returns:
            Tuple of (output_image, pose_preview, depth_preview)
        """
        
        print("[CharacterSwap] Starting character swap process...")
        
        # Convert ComfyUI image format to PIL
        ref_pil = self.tensor_to_pil(reference_image)
        char_face_pil = self.tensor_to_pil(character_face)
        
        # STEP 1: Extract ControlNet maps
        print("[CharacterSwap] Extracting ControlNet preprocessors...")
        pose_map = self.extract_openpose(ref_pil)
        depth_map = self.extract_depth(ref_pil)
        
        # STEP 2: For now, return previews and placeholder
        # TODO: Integrate with ComfyUI's ControlNet pipeline
        # TODO: Add IP-Adapter FaceID integration
        # TODO: Add ReActor face swap integration
        
        print("[CharacterSwap] WARNING: This is a placeholder implementation.")
        print("[CharacterSwap] Full ControlNet integration requires:")
        print("[CharacterSwap]   - ComfyUI-ControlNet-Aux for preprocessors")
        print("[CharacterSwap]   - ControlNet models loaded")
        print("[CharacterSwap]   - IP-Adapter or ReActor nodes")
        
        # Convert back to ComfyUI tensor format
        pose_tensor = self.pil_to_tensor(pose_map)
        depth_tensor = self.pil_to_tensor(depth_map)
        output_tensor = reference_image  # Placeholder - return original for now
        
        return (output_tensor, pose_tensor, depth_tensor)
    
    def tensor_to_pil(self, tensor):
        """Convert ComfyUI image tensor to PIL Image."""
        # ComfyUI format: [B, H, W, C] in range [0, 1]
        if len(tensor.shape) == 4:
            tensor = tensor[0]  # Take first batch item
        
        # Convert to numpy and scale to [0, 255]
        np_image = (tensor.cpu().numpy() * 255).astype(np.uint8)
        
        # Convert to PIL
        pil_image = Image.fromarray(np_image)
        return pil_image
    
    def pil_to_tensor(self, pil_image):
        """Convert PIL Image to ComfyUI image tensor."""
        # Convert to numpy
        np_image = np.array(pil_image).astype(np.float32) / 255.0
        
        # Convert to torch tensor [H, W, C]
        tensor = torch.from_numpy(np_image)
        
        # Add batch dimension [1, H, W, C]
        tensor = tensor.unsqueeze(0)
        
        return tensor
    
    def extract_openpose(self, pil_image):
        """
        Extract OpenPose skeleton from image.
        
        NOTE: This requires ComfyUI-ControlNet-Aux to be installed.
        Install: cd custom_nodes && git clone https://github.com/Fannovel16/comfyui_controlnet_aux
        """
        try:
            from controlnet_aux import OpenposeDetector
            
            detector = OpenposeDetector.from_pretrained("lllyasviel/ControlNet")
            pose_image = detector(pil_image)
            
            print("[CharacterSwap] OpenPose extracted successfully")
            return pose_image
            
        except ImportError:
            print("[CharacterSwap] ERROR: controlnet_aux not found!")
            print("[CharacterSwap] Install: pip install controlnet-aux")
            print("[CharacterSwap] Or clone: https://github.com/Fannovel16/comfyui_controlnet_aux")
            
            # Return grayscale placeholder
            return pil_image.convert("L").convert("RGB")
        except Exception as e:
            print(f"[CharacterSwap] Error extracting OpenPose: {e}")
            return pil_image.convert("L").convert("RGB")
    
    def extract_depth(self, pil_image):
        """
        Extract depth map from image.
        
        NOTE: This requires ComfyUI-ControlNet-Aux to be installed.
        """
        try:
            from controlnet_aux import MidasDetector
            
            detector = MidasDetector.from_pretrained("lllyasviel/ControlNet")
            depth_image = detector(pil_image)
            
            print("[CharacterSwap] Depth map extracted successfully")
            return depth_image
            
        except ImportError:
            print("[CharacterSwap] ERROR: controlnet_aux not found!")
            print("[CharacterSwap] Install: pip install controlnet-aux")
            
            # Return grayscale placeholder
            return pil_image.convert("L").convert("RGB")
        except Exception as e:
            print(f"[CharacterSwap] Error extracting depth: {e}")
            return pil_image.convert("L").convert("RGB")
    
    def extract_canny(self, pil_image, low_threshold=100, high_threshold=200):
        """Extract Canny edges from image."""
        try:
            from controlnet_aux import CannyDetector
            
            detector = CannyDetector()
            canny_image = detector(pil_image, low_threshold, high_threshold)
            
            print("[CharacterSwap] Canny edges extracted successfully")
            return canny_image
            
        except ImportError:
            print("[CharacterSwap] ERROR: controlnet_aux not found!")
            return pil_image.convert("L").convert("RGB")
        except Exception as e:
            print(f"[CharacterSwap] Error extracting Canny: {e}")
            return pil_image.convert("L").convert("RGB")


class CharacterSwapAdvanced(CharacterSwapNode):
    """
    Advanced version with full pipeline integration.
    This will require the following nodes to be properly connected in the workflow.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        base_inputs = super().INPUT_TYPES()
        
        # Add model and ControlNet inputs
        base_inputs["required"].update({
            "model": ("MODEL",),
            "vae": ("VAE",),
            "clip": ("CLIP",),
        })
        
        base_inputs["optional"].update({
            "openpose_controlnet": ("CONTROL_NET",),
            "depth_controlnet": ("CONTROL_NET",),
            "canny_controlnet": ("CONTROL_NET",),
            "ipadapter_model": ("IPADAPTER",),
        })
        
        return base_inputs
    
    RETURN_TYPES = ("IMAGE", "IMAGE", "IMAGE", "LATENT")
    RETURN_NAMES = ("output_image", "pose_preview", "depth_preview", "latent")
    FUNCTION = "swap_character_advanced"
    
    def swap_character_advanced(self, reference_image, character_face, positive_prompt,
                               negative_prompt, pose_strength, depth_strength, face_strength,
                               seed, model, vae, clip, canny_strength=0.5,
                               openpose_controlnet=None, depth_controlnet=None,
                               canny_controlnet=None, ipadapter_model=None):
        """
        Advanced character swap with full model integration.
        
        This version integrates with ComfyUI's native nodes for:
        - ControlNet application
        - IP-Adapter FaceID
        - VAE encoding/decoding
        - CLIP text encoding
        """
        
        print("[CharacterSwap Advanced] Starting full pipeline...")
        
        # Get preprocessor outputs
        ref_pil = self.tensor_to_pil(reference_image)
        pose_map = self.extract_openpose(ref_pil)
        depth_map = self.extract_depth(ref_pil)
        
        pose_tensor = self.pil_to_tensor(pose_map)
        depth_tensor = self.pil_to_tensor(depth_map)
        
        # TODO: Implement full pipeline
        # 1. Encode text prompts with CLIP
        # 2. Apply ControlNets (OpenPose, Depth, Canny)
        # 3. Generate latent with model
        # 4. Apply IP-Adapter FaceID
        # 5. Decode with VAE
        
        print("[CharacterSwap Advanced] Full pipeline not yet implemented")
        print("[CharacterSwap Advanced] Use standard ComfyUI workflow for now:")
        print("[CharacterSwap Advanced]   1. Use this node to get pose/depth maps")
        print("[CharacterSwap Advanced]   2. Connect to ControlNet Apply nodes")
        print("[CharacterSwap Advanced]   3. Connect to IPAdapter FaceID")
        print("[CharacterSwap Advanced]   4. Connect to KSampler")
        
        # Return previews and empty latent
        empty_latent = {"samples": torch.zeros((1, 4, 64, 64))}
        
        return (reference_image, pose_tensor, depth_tensor, empty_latent)


NODE_CLASS_MAPPINGS = {
    "PMACharacterSwap": CharacterSwapNode,
    "PMACharacterSwapAdvanced": CharacterSwapAdvanced,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PMACharacterSwap": "PMA Character Swap (Basic)",
    "PMACharacterSwapAdvanced": "PMA Character Swap (Advanced)",
}
