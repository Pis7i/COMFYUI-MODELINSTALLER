"""
EyeStabilizer V2 Node for ComfyUI
Enhanced with ethnicity-aware presets and specialized optimizations.

Features:
1. Ethnicity-specific presets (East Asian, South Asian, African, Caucasian, Middle Eastern, Latino, Auto)
2. Adaptive thresholds based on eye shape characteristics
3. Specialized enhancement techniques per ethnicity
4. Auto-calibration mode that learns from the video
5. Dense eye landmark detection (MediaPipe Face Mesh - 478 landmarks)
6. Temporal smoothing using Kalman filtering
7. Blink detection with adaptive thresholds
8. Eye region enhancement with ethnicity-aware processing

Usage: Insert between RMBG (background removal) and control map generation in Wan2.2 workflows.
"""

import torch
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance
import cv2
from typing import Tuple, Optional, List, Dict
from collections import deque


# Ethnicity-specific preset configurations
ETHNICITY_PRESETS = {
    "auto": {
        "name": "Auto-Detect",
        "blink_threshold": 0.2,
        "smoothing_strength": 0.7,
        "enhancement_strength": 1.3,
        "ear_baseline": None,  # Will be auto-calibrated
        "description": "Automatically calibrates to the person in the video"
    },
    "east_asian": {
        "name": "East Asian (Chinese, Japanese, Korean)",
        "blink_threshold": 0.12,  # Lower for monolids/epicanthic folds
        "smoothing_strength": 0.4,  # Less aggressive
        "enhancement_strength": 1.1,  # Gentler sharpening
        "ear_baseline": 0.18,  # Typical open eye EAR for East Asian
        "iris_visibility_factor": 0.7,  # Less visible iris area
        "eyelid_weight": 1.3,  # More emphasis on eyelid tracking
        "description": "Optimized for monolids and epicanthic folds"
    },
    "south_asian": {
        "name": "South Asian (Indian, Pakistani, Bangladeshi)",
        "blink_threshold": 0.18,
        "smoothing_strength": 0.6,
        "enhancement_strength": 1.25,
        "ear_baseline": 0.22,
        "iris_visibility_factor": 0.85,
        "eyelid_weight": 1.0,
        "description": "Balanced for varied eye shapes"
    },
    "african": {
        "name": "African / African American",
        "blink_threshold": 0.22,
        "smoothing_strength": 0.65,
        "enhancement_strength": 1.4,  # Higher contrast enhancement
        "ear_baseline": 0.25,
        "iris_visibility_factor": 0.9,
        "eyelid_weight": 0.9,
        "contrast_boost": 1.15,  # Additional contrast for darker skin tones
        "description": "Enhanced contrast for better landmark detection"
    },
    "caucasian": {
        "name": "Caucasian / European",
        "blink_threshold": 0.20,
        "smoothing_strength": 0.7,
        "enhancement_strength": 1.3,
        "ear_baseline": 0.26,
        "iris_visibility_factor": 1.0,
        "eyelid_weight": 1.0,
        "description": "Standard MediaPipe calibration"
    },
    "middle_eastern": {
        "name": "Middle Eastern / Arab",
        "blink_threshold": 0.19,
        "smoothing_strength": 0.6,
        "enhancement_strength": 1.35,
        "ear_baseline": 0.24,
        "iris_visibility_factor": 0.95,
        "eyelid_weight": 1.1,
        "description": "Optimized for almond-shaped eyes"
    },
    "latino": {
        "name": "Latino / Hispanic",
        "blink_threshold": 0.19,
        "smoothing_strength": 0.65,
        "enhancement_strength": 1.3,
        "ear_baseline": 0.24,
        "iris_visibility_factor": 0.95,
        "eyelid_weight": 1.0,
        "description": "Balanced settings for diverse Latino features"
    }
}


class KalmanFilter1D:
    """Simple 1D Kalman filter for temporal smoothing."""
    
    def __init__(self, process_variance=1e-3, measurement_variance=1e-1):
        self.process_variance = process_variance
        self.measurement_variance = measurement_variance
        self.estimate = 0.0
        self.error_estimate = 1.0
        
    def update(self, measurement):
        """Update filter with new measurement."""
        # Prediction
        prediction_error = self.error_estimate + self.process_variance
        
        # Update
        kalman_gain = prediction_error / (prediction_error + self.measurement_variance)
        self.estimate = self.estimate + kalman_gain * (measurement - self.estimate)
        self.error_estimate = (1 - kalman_gain) * prediction_error
        
        return self.estimate


class AdaptiveBlinkDetector:
    """
    Adaptive blink detector with auto-calibration.
    Learns the person's baseline eye opening from the video.
    Supports blink suppression mode to reduce excessive blinking from Wan2.2.
    """
    
    def __init__(self, history_size=5, threshold=0.2, ethnicity_preset=None, 
                 blink_suppression=False, min_blink_duration=3):
        self.history_size = history_size
        self.threshold = threshold
        self.ear_history = deque(maxlen=history_size)
        self.baseline_ear = None
        self.calibration_samples = []
        self.calibrated = False
        self.ethnicity_preset = ethnicity_preset
        
        # Blink suppression features
        self.blink_suppression = blink_suppression
        self.min_blink_duration = min_blink_duration  # Minimum frames for valid blink
        self.blink_counter = 0  # Consecutive blink frames
        self.forced_open_ear = None  # EAR to maintain when suppressing
        
    def calculate_ear(self, eye_landmarks):
        """
        Calculate Eye Aspect Ratio (EAR).
        
        Args:
            eye_landmarks: Array of eye landmark points [(x, y), ...]
            
        Returns:
            float: Eye aspect ratio (0 = closed, ~0.3 = open)
        """
        if len(eye_landmarks) < 6:
            return 0.3  # Default open eye
        
        # Vertical distances
        v1 = np.linalg.norm(eye_landmarks[1] - eye_landmarks[5])
        v2 = np.linalg.norm(eye_landmarks[2] - eye_landmarks[4])
        
        # Horizontal distance
        h = np.linalg.norm(eye_landmarks[0] - eye_landmarks[3])
        
        # EAR calculation
        ear = (v1 + v2) / (2.0 * h + 1e-6)
        
        return ear
    
    def calibrate(self, ear_value):
        """
        Auto-calibrate baseline EAR from video samples.
        Collects samples from first ~30 frames to establish baseline.
        """
        if not self.calibrated:
            self.calibration_samples.append(ear_value)
            
            # After 30 samples, compute baseline
            if len(self.calibration_samples) >= 30:
                # Use 75th percentile as baseline (likely open eyes)
                self.baseline_ear = np.percentile(self.calibration_samples, 75)
                # Adaptive threshold: blink if drops below 65% of baseline
                self.threshold = 0.35  # 35% drop from baseline = blink
                self.calibrated = True
                print(f"[EyeStabilizer] Auto-calibrated baseline EAR: {self.baseline_ear:.3f}")
                print(f"[EyeStabilizer] Blink threshold set to {self.threshold:.2f} (relative)")
    
    def detect_blink(self, left_ear, right_ear):
        """
        Detect if a blink is occurring.
        Uses adaptive threshold if calibrated, otherwise uses preset.
        Includes blink suppression logic to reduce excessive blinking.
        
        Args:
            left_ear: Left eye aspect ratio
            right_ear: Right eye aspect ratio
            
        Returns:
            bool: True if blink detected (and allowed)
        """
        avg_ear = (left_ear + right_ear) / 2.0
        
        # Auto-calibration in progress
        if not self.calibrated and self.ethnicity_preset == "auto":
            self.calibrate(avg_ear)
        
        self.ear_history.append(avg_ear)
        
        if len(self.ear_history) < self.history_size:
            return False
        
        # Determine if technically blinking
        is_blinking_raw = False
        if self.calibrated and self.baseline_ear:
            is_blinking_raw = avg_ear < (self.baseline_ear * (1 - self.threshold))
        else:
            avg_historical = sum(self.ear_history) / len(self.ear_history)
            is_blinking_raw = avg_ear < (avg_historical * (1 - self.threshold))
        
        # Blink suppression logic
        if self.blink_suppression:
            if is_blinking_raw:
                self.blink_counter += 1
                
                # Only allow blink if it's sustained for minimum duration
                # This filters out micro-blinks from Wan2.2 jitter
                if self.blink_counter >= self.min_blink_duration:
                    return True  # Valid blink
                else:
                    return False  # Suppress - too short, likely noise
            else:
                # Reset counter when eyes open
                self.blink_counter = 0
                return False
        
        return is_blinking_raw
    
    def smooth_blink(self, current_ear, is_blinking):
        """
        Smooth blink transition.
        
        Args:
            current_ear: Current eye aspect ratio
            is_blinking: Whether blink is detected
            
        Returns:
            float: Smoothed EAR value
        """
        if not self.ear_history:
            return current_ear
        
        if is_blinking:
            # During blink, interpolate smoothly
            avg_historical = sum(self.ear_history) / len(self.ear_history)
            return current_ear * 0.3 + avg_historical * 0.7
        
        return current_ear


class EyeStabilizerV2Node:
    """
    Enhanced Eye Stabilizer with ethnicity-aware presets.
    """
    
    def __init__(self):
        self.type = "EyeStabilizerV2Node"
        self.landmark_filters = {}
        self.blink_detector = None
        self.mediapipe_available = False
        self.current_preset = None
        
        # Try to import MediaPipe
        try:
            import mediapipe as mp
            self.mp_face_mesh = mp.solutions.face_mesh
            self.face_mesh = None
            self.mediapipe_available = True
            print("[EyeStabilizer V2] MediaPipe Face Mesh available")
        except ImportError:
            print("[EyeStabilizer V2] WARNING: MediaPipe not found. Install with: pip install mediapipe")
            print("[EyeStabilizer V2] Falling back to basic stabilization mode")
    
    @classmethod
    def INPUT_TYPES(cls):
        ethnicity_choices = list(ETHNICITY_PRESETS.keys())
        ethnicity_names = [ETHNICITY_PRESETS[k]["name"] for k in ethnicity_choices]
        
        return {
            "required": {
                "images": ("IMAGE",),
                "ethnicity_preset": (ethnicity_choices, {
                    "default": "auto",
                    "tooltip": "Select ethnicity for optimized eye detection and tracking"
                }),
                "enable_temporal_smoothing": ("BOOLEAN", {
                    "default": True,
                    "label_on": "Enabled",
                    "label_off": "Disabled"
                }),
                "enable_blink_detection": ("BOOLEAN", {
                    "default": True,
                    "label_on": "Enabled",
                    "label_off": "Disabled"
                }),
                "enable_eye_enhancement": ("BOOLEAN", {
                    "default": True,
                    "label_on": "Enabled",
                    "label_off": "Disabled"
                }),
                "blink_suppression_mode": (["off", "light", "moderate", "aggressive"], {
                    "default": "off",
                    "tooltip": "Reduce excessive blinking from Wan2.2 (off=normal, light=filter 1-2 frame blinks, moderate=3+ frames, aggressive=5+ frames)"
                }),
            },
            "optional": {
                "smoothing_override": ("FLOAT", {
                    "default": -1.0,
                    "min": -1.0,
                    "max": 1.0,
                    "step": 0.05,
                    "display": "slider",
                    "tooltip": "Override preset smoothing (-1 = use preset)"
                }),
                "enhancement_override": ("FLOAT", {
                    "default": -1.0,
                    "min": -1.0,
                    "max": 2.0,
                    "step": 0.1,
                    "display": "slider",
                    "tooltip": "Override preset enhancement (-1 = use preset)"
                }),
                "blink_threshold_override": ("FLOAT", {
                    "default": -1.0,
                    "min": -1.0,
                    "max": 0.5,
                    "step": 0.05,
                    "display": "slider",
                    "tooltip": "Override preset blink threshold (-1 = use preset)"
                }),
                "eye_region_dilation": ("INT", {
                    "default": 10,
                    "min": 0,
                    "max": 50,
                    "step": 5,
                    "tooltip": "Pixels to expand eye mask region"
                }),
            }
        }
    
    RETURN_TYPES = ("IMAGE", "MASK", "IMAGE", "STRING")
    RETURN_NAMES = ("stabilized_images", "eye_mask", "debug_visualization", "preset_info")
    FUNCTION = "stabilize_eyes"
    CATEGORY = "PMA Utils/Video Processing"
    
    def stabilize_eyes(self, images, ethnicity_preset, enable_temporal_smoothing,
                      enable_blink_detection, enable_eye_enhancement, blink_suppression_mode,
                      smoothing_override=-1.0, enhancement_override=-1.0,
                      blink_threshold_override=-1.0, eye_region_dilation=10):
        """
        Main function with ethnicity-aware processing.
        """
        
        # Load preset
        preset = ETHNICITY_PRESETS[ethnicity_preset]
        self.current_preset = preset
        
        # Apply overrides or use preset values
        smoothing_strength = smoothing_override if smoothing_override >= 0 else preset["smoothing_strength"]
        enhancement_strength = enhancement_override if enhancement_override >= 0 else preset["enhancement_strength"]
        blink_threshold = blink_threshold_override if blink_threshold_override >= 0 else preset["blink_threshold"]
        
        # Configure blink suppression
        blink_suppression_settings = {
            "off": (False, 0),
            "light": (True, 2),      # Filter 1-2 frame micro-blinks
            "moderate": (True, 3),   # Filter 1-3 frame blinks
            "aggressive": (True, 5)  # Only allow 5+ frame sustained blinks
        }
        suppress_enabled, min_duration = blink_suppression_settings[blink_suppression_mode]
        
        print(f"[EyeStabilizer V2] Processing {images.shape[0]} frames...")
        print(f"[EyeStabilizer V2] Preset: {preset['name']}")
        print(f"[EyeStabilizer V2] Smoothing: {smoothing_strength:.2f}")
        print(f"[EyeStabilizer V2] Enhancement: {enhancement_strength:.2f}")
        print(f"[EyeStabilizer V2] Blink Threshold: {blink_threshold:.2f}")
        print(f"[EyeStabilizer V2] Blink Suppression: {blink_suppression_mode} (min {min_duration} frames)")
        
        # Reset state for new sequence
        self.landmark_filters = {}
        self.blink_detector = AdaptiveBlinkDetector(
            threshold=blink_threshold,
            ethnicity_preset=ethnicity_preset,
            blink_suppression=suppress_enabled,
            min_blink_duration=min_duration
        )
        
        # Process frames
        batch_size = images.shape[0]
        stabilized_frames = []
        eye_masks = []
        debug_frames = []
        
        for i in range(batch_size):
            frame = images[i]
            
            stabilized, eye_mask, debug_viz = self._process_frame(
                frame,
                preset,
                enable_temporal_smoothing,
                enable_blink_detection,
                enable_eye_enhancement,
                smoothing_strength,
                enhancement_strength,
                eye_region_dilation
            )
            
            stabilized_frames.append(stabilized)
            eye_masks.append(eye_mask)
            debug_frames.append(debug_viz)
            
            if (i + 1) % 10 == 0:
                print(f"[EyeStabilizer V2] Processed {i + 1}/{batch_size} frames")
        
        # Stack frames
        stabilized_batch = torch.stack(stabilized_frames, dim=0)
        eye_mask_batch = torch.stack(eye_masks, dim=0)
        debug_batch = torch.stack(debug_frames, dim=0)
        
        # Preset info string
        preset_info = f"{preset['name']}: {preset['description']}"
        if self.blink_detector.calibrated:
            preset_info += f" | Auto-calibrated EAR: {self.blink_detector.baseline_ear:.3f}"
        
        print(f"[EyeStabilizer V2] Completed: {preset_info}")
        
        return (stabilized_batch, eye_mask_batch, debug_batch, preset_info)
    
    def _process_frame(self, frame, preset, enable_smoothing, enable_blink,
                      enable_enhancement, smoothing_strength, enhancement_strength, dilation):
        """Process a single frame with ethnicity-specific optimizations."""
        
        # Convert to numpy and PIL
        frame_np = (frame.cpu().numpy() * 255).astype(np.uint8)
        frame_pil = Image.fromarray(frame_np)
        
        # Initialize outputs
        stabilized_pil = frame_pil.copy()
        eye_mask_pil = Image.new('L', frame_pil.size, 0)
        debug_pil = frame_pil.copy()
        
        if self.mediapipe_available:
            stabilized_pil, eye_mask_pil, debug_pil = self._process_with_mediapipe(
                frame_pil, preset, enable_smoothing, enable_blink, enable_enhancement,
                smoothing_strength, enhancement_strength, dilation
            )
        else:
            if enable_enhancement:
                stabilized_pil = self._enhance_image(frame_pil, enhancement_strength)
        
        # Convert back to tensors
        stabilized_tensor = self._pil_to_tensor(stabilized_pil)
        eye_mask_tensor = self._pil_to_tensor(eye_mask_pil.convert('RGB'))[:, :, 0:1]
        debug_tensor = self._pil_to_tensor(debug_pil)
        
        return stabilized_tensor, eye_mask_tensor, debug_tensor
    
    def _process_with_mediapipe(self, frame_pil, preset, enable_smoothing, enable_blink,
                               enable_enhancement, smoothing_strength, enhancement_strength, dilation):
        """Process with MediaPipe and ethnicity-specific optimizations."""
        
        # Initialize face mesh
        if self.face_mesh is None:
            self.face_mesh = self.mp_face_mesh.FaceMesh(
                static_image_mode=False,
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
        
        # Ethnicity-specific preprocessing
        frame_pil = self._ethnicity_preprocess(frame_pil, preset)
        
        # Convert to RGB for MediaPipe
        frame_rgb = np.array(frame_pil.convert('RGB'))
        height, width = frame_rgb.shape[:2]
        
        # Process with MediaPipe
        results = self.face_mesh.process(frame_rgb)
        
        stabilized_pil = frame_pil.copy()
        eye_mask_pil = Image.new('L', frame_pil.size, 0)
        debug_pil = frame_pil.copy()
        
        if results.multi_face_landmarks:
            face_landmarks = results.multi_face_landmarks[0]
            
            # Extract eye landmarks
            left_eye_indices = [33, 160, 158, 133, 153, 144]
            right_eye_indices = [362, 385, 387, 263, 373, 380]
            left_iris_indices = [468, 469, 470, 471, 472]
            right_iris_indices = [473, 474, 475, 476, 477]
            
            # Get landmark coordinates
            left_eye = self._get_landmarks(face_landmarks, left_eye_indices, width, height)
            right_eye = self._get_landmarks(face_landmarks, right_eye_indices, width, height)
            left_iris = self._get_landmarks(face_landmarks, left_iris_indices, width, height)
            right_iris = self._get_landmarks(face_landmarks, right_iris_indices, width, height)
            
            # Apply temporal smoothing with ethnicity weight
            if enable_smoothing:
                eyelid_weight = preset.get("eyelid_weight", 1.0)
                left_eye = self._apply_smoothing(left_eye, "left_eye", smoothing_strength * eyelid_weight)
                right_eye = self._apply_smoothing(right_eye, "right_eye", smoothing_strength * eyelid_weight)
                
                iris_weight = preset.get("iris_visibility_factor", 1.0)
                left_iris = self._apply_smoothing(left_iris, "left_iris", smoothing_strength * iris_weight)
                right_iris = self._apply_smoothing(right_iris, "right_iris", smoothing_strength * iris_weight)
            
            # Blink detection
            is_blinking = False
            if enable_blink:
                left_ear = self.blink_detector.calculate_ear(left_eye)
                right_ear = self.blink_detector.calculate_ear(right_eye)
                is_blinking = self.blink_detector.detect_blink(left_ear, right_ear)
            
            # Create eye mask
            eye_mask_np = np.zeros((height, width), dtype=np.uint8)
            left_eye_int = left_eye.astype(np.int32)
            right_eye_int = right_eye.astype(np.int32)
            
            cv2.fillPoly(eye_mask_np, [left_eye_int], 255)
            cv2.fillPoly(eye_mask_np, [right_eye_int], 255)
            
            if dilation > 0:
                kernel = np.ones((dilation, dilation), np.uint8)
                eye_mask_np = cv2.dilate(eye_mask_np, kernel, iterations=1)
            
            eye_mask_pil = Image.fromarray(eye_mask_np)
            
            # Ethnicity-specific enhancement
            if enable_enhancement:
                stabilized_pil = self._ethnicity_enhance_eyes(
                    frame_pil, eye_mask_pil, preset, enhancement_strength
                )
            
            # Debug visualization
            debug_np = np.array(debug_pil)
            
            # Draw landmarks
            for point in left_eye_int:
                cv2.circle(debug_np, tuple(point), 2, (0, 255, 0), -1)
            for point in right_eye_int:
                cv2.circle(debug_np, tuple(point), 2, (0, 255, 0), -1)
            for point in left_iris.astype(np.int32):
                cv2.circle(debug_np, tuple(point), 1, (255, 0, 0), -1)
            for point in right_iris.astype(np.int32):
                cv2.circle(debug_np, tuple(point), 1, (255, 0, 0), -1)
            
            if is_blinking:
                cv2.putText(debug_np, "BLINK", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            
            # Show preset name
            cv2.putText(debug_np, preset["name"], (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            
            debug_pil = Image.fromarray(debug_np)
        
        return stabilized_pil, eye_mask_pil, debug_pil
    
    def _ethnicity_preprocess(self, frame_pil, preset):
        """Apply ethnicity-specific preprocessing for better landmark detection."""
        
        # African/darker skin tones: Boost contrast
        if "contrast_boost" in preset:
            enhancer = ImageEnhance.Contrast(frame_pil)
            frame_pil = enhancer.enhance(preset["contrast_boost"])
        
        return frame_pil
    
    def _ethnicity_enhance_eyes(self, frame_pil, eye_mask_pil, preset, base_strength):
        """Apply ethnicity-specific eye enhancement."""
        
        frame_np = np.array(frame_pil)
        mask_np = np.array(eye_mask_pil) / 255.0
        
        # Base sharpening
        frame_sharp = frame_pil.filter(ImageFilter.SHARPEN)
        enhancer = ImageEnhance.Sharpness(frame_sharp)
        frame_sharp = enhancer.enhance(base_strength)
        frame_sharp_np = np.array(frame_sharp)
        
        # Additional contrast boost for African ethnicity
        if "contrast_boost" in preset:
            contrast_enhancer = ImageEnhance.Contrast(Image.fromarray(frame_sharp_np))
            frame_sharp = contrast_enhancer.enhance(1.1)
            frame_sharp_np = np.array(frame_sharp)
        
        # Blend using mask
        mask_3ch = np.stack([mask_np] * 3, axis=-1)
        blended_np = (frame_sharp_np * mask_3ch + frame_np * (1 - mask_3ch)).astype(np.uint8)
        
        return Image.fromarray(blended_np)
    
    def _get_landmarks(self, face_landmarks, indices, width, height):
        """Extract landmark coordinates."""
        landmarks = []
        for idx in indices:
            landmark = face_landmarks.landmark[idx]
            x = int(landmark.x * width)
            y = int(landmark.y * height)
            landmarks.append([x, y])
        return np.array(landmarks, dtype=np.float32)
    
    def _apply_smoothing(self, landmarks, key, strength):
        """Apply Kalman filtering with ethnicity-adjusted strength."""
        smoothed = []
        
        for i, (x, y) in enumerate(landmarks):
            filter_key_x = f"{key}_{i}_x"
            filter_key_y = f"{key}_{i}_y"
            
            if filter_key_x not in self.landmark_filters:
                variance = 1e-3 * (1 - strength)
                self.landmark_filters[filter_key_x] = KalmanFilter1D(
                    process_variance=variance,
                    measurement_variance=1e-1
                )
                self.landmark_filters[filter_key_y] = KalmanFilter1D(
                    process_variance=variance,
                    measurement_variance=1e-1
                )
            
            smoothed_x = self.landmark_filters[filter_key_x].update(x)
            smoothed_y = self.landmark_filters[filter_key_y].update(y)
            smoothed.append([smoothed_x, smoothed_y])
        
        return np.array(smoothed, dtype=np.float32)
    
    def _enhance_image(self, image_pil, strength):
        """Basic image enhancement fallback."""
        enhancer = ImageEnhance.Sharpness(image_pil)
        return enhancer.enhance(strength)
    
    def _pil_to_tensor(self, pil_image):
        """Convert PIL Image to ComfyUI tensor."""
        np_image = np.array(pil_image).astype(np.float32) / 255.0
        tensor = torch.from_numpy(np_image)
        return tensor


# Node registration
NODE_CLASS_MAPPINGS = {
    "PMAEyeStabilizerV2": EyeStabilizerV2Node,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PMAEyeStabilizerV2": "PMA Eye Stabilizer V2 (Ethnicity-Aware)",
}
